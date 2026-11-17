"""Execute the existing non-PyTorch course examples, with explicit scaffolds.

No Python is executed by the web site. This is an offline authoring check.
The source for every executed block is read from the current course JSON.
--strict returns a failure if a printed course claim is inconsistent with it.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import hashlib
import importlib.metadata
import io
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import traceback

os.environ.setdefault("NUMBA_DISABLE_JIT", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
THEMES = ["python-scientifique", "audio-signal", "audio-ml",
          "generation-controle", "evaluation-recherche"]

# Each snippet's missing inputs are supplied here, not silently inferred.
# These miniatures test contracts; no pretrained model is represented as loaded.
SCAFFOLDS = {
    "embeddings-transfert-domaines": '''
encoder = torch.nn.Sequential(torch.nn.Linear(4, 512), torch.nn.Tanh())
x = torch.arange(8, dtype=torch.float32).reshape(2, 4) / 8
target = torch.tensor([[1., 0.], [0., 1.]])
''',
    "augmentations-cibles-validation": '''
sr = 16000
# Two distinct generated test signals, with the durations stated in the lesson.
y = np.sin(2 * np.pi * 220 * np.arange(sr * 10) / sr).astype(np.float64)
note = np.sin(2 * np.pi * 261.625565 * np.arange(sr) / sr).astype(np.float64)
''',
    "masquage-mixup-representations": '''
x_a = torch.tensor([[1., 2.], [3., 4.]])
x_b = torch.tensor([[5., 6.], [7., 8.]])
y_a = torch.tensor([1., 0.])
y_b = torch.tensor([0., 1.])
''',
    "similarites-contraste-attention/code": '''
D = 8
x = torch.arange(48, dtype=torch.float32).reshape(2, 3, D) / 10
valid = torch.tensor([[True, True, False], [True, True, True]])
''',
    "resolution-fuite-zero-padding": '''
import soundfile as sf
y, sr = sf.read("public/media/audio/voice-resampled.wav")
assert sr == 16000 and len(y) >= 2048
''',
    "reconstruction-streaming-limites": '''
import soundfile as sf
y, sr = sf.read("public/media/audio/voice-resampled.wav")
assert sr == 16000
''',
    "autoregression-et-causalite": '''
class MiniCausalModel(torch.nn.Module):
    """Small randomly initialized causal model, not a trained audio generator."""
    def __init__(self):
        super().__init__()
        self.embedding = torch.nn.Embedding(10, 4)
        self.layer = torch.nn.TransformerEncoderLayer(
            d_model=4, nhead=2, dim_feedforward=8, dropout=0., batch_first=True)
        self.head = torch.nn.Linear(4, 10)
    def forward(self, tokens):
        length = tokens.shape[1]
        causal = torch.ones(length, length, dtype=torch.bool).triu(diagonal=1)
        return self.head(self.layer(self.embedding(tokens), src_mask=causal))
model = MiniCausalModel()
''',
    "vae-et-echantillonnage": '''
mu = torch.tensor([[2.]])
logvar = torch.log(torch.tensor([[4.]]))
decoder = torch.nn.Identity()
''',
    "kl-et-latent-inutilise": '''
mu = torch.ones((2, 4))
logvar = torch.zeros((2, 4))
reconstruction_loss = torch.tensor(.25)
beta = .1
''',
    "diffusion-et-bruit": '''
x0 = torch.tensor([1.])
alpha_bar = torch.tensor(.64)
t = torch.tensor([1])
def model(xt, t):
    # A specified toy prediction, not a learned denoiser.
    return torch.full_like(xt, -.8)
''',
    "guidance-et-zones-connues": '''
eps_u = torch.tensor([2.])
eps_c = torch.tensor([5.])
s = 2.
known_mask = torch.tensor([True, True, False, False])
observed = torch.tensor([.1, .2, .3, .4])
generated = torch.tensor([9., 8., 7., 6.])
''',
    "adaptation-lora-et-petit-corpus": '''
d_in, d_out, r = 4, 3, 2
base = torch.nn.Linear(d_in, d_out, bias=False)
W0 = base.weight
x = torch.tensor([1., 2., 3., 4.])
''',
    "splits-et-fuites": '''
recording_ids = ["R1", "R2", "R3", "R4", "R5", "R6"]
def split_recording_ids(ids):
    assert len(set(ids)) == len(ids)
    return ids[:3], ids[3:5], ids[5:]
class Windows:
    def __init__(self, ids):
        self.recording_ids = [id for id in ids for _ in range(2)]
        self.features = np.array([[float(id[1:]), float(j)] for id in ids for j in range(2)])
def make_windows(ids):
    return Windows(ids)
class Scaler:
    def fit(self, features):
        self.mean_ = features.mean(axis=0)
        self.scale_ = np.maximum(features.std(axis=0), 1e-8)
        return self
    def transform(self, features):
        return (features - self.mean_) / self.scale_
scaler = Scaler()
''',
    "boucle-evaluation-et-surapprentissage": '''
model = torch.nn.Identity()
criterion = torch.nn.MSELoss(reduction="mean")
valid_loader = [
    (torch.zeros(8, 1, dtype=torch.float64), torch.ones(8, 1, dtype=torch.float64)),
    (torch.zeros(2, 1, dtype=torch.float64), torch.full((2, 1), math.sqrt(3), dtype=torch.float64)),
]
''',
    "variabilite-et-incertitude": '''
recording_ids = np.array([f"R{i:02}" for i in range(20)])
rng = np.random.default_rng(0)
base = {id: .7 + i * .005 for i, id in enumerate(recording_ids)}
adapted = {id: value + (.02 if i % 2 else -.005)
           for i, (id, value) in enumerate(base.items())}
def score_on_groups(scores, sampled):
    # Iterating the sampled list retains duplicate groups and paired sampling.
    return float(np.mean([scores[id] for id in sampled]))
''',
}

# Checks are independent statements, not observations copied into a claimed run.
CHECKS = {
    "tache-cibles-pertes": '''
assert tuple(logits.shape) == (1, 2)
assert torch.allclose(probabilities, torch.tensor([[.5, .75]]), atol=1e-6)
assert torch.isfinite(loss)
''',
    "pretraitement-entrees-coherentes": '''
assert mean.item() == 2 and std.item() == 1 and scaled.item() == 2
''',
    "durees-padding-masques": '''
assert naive.item() == 1.5 and pooled.item() == 3
''',
    "embeddings-transfert-domaines": '''
assert tuple(embeddings.shape) == (2, 512)
assert all(p.grad is None and not p.requires_grad for p in encoder.parameters())
assert all(p.grad is not None for p in head.parameters())
''',
    "architectures-axes-contexte": '''
assert tuple(h.shape) == (8, 16, 15996)
assert tuple(z.shape) == (8, 8, 62, 98)
''',
    "annotations-faibles-agregation": '''
assert abs(mean_score.item() - .3066666666667) < 1e-6
assert abs(max_score.item() - .9) < 1e-6
''',
    "augmentations-cibles-validation": '''
assert len(y) == 160000 and len(fast) == 128000
assert new_bpm == 125 and len(up) == len(note) and new_midi == 62
''',
    "masquage-mixup-representations": '''
assert torch.equal(y_mix, torch.tensor([.25, .75]))
assert torch.equal(x_mix, torch.tensor([[4., 5.], [6., 7.]]))
''',
    "similarites-contraste-attention/walkthrough": '''
assert torch.allclose(weights, torch.tensor([.75, .25]), atol=1e-6)
assert abs(summary.item() - 4) < 1e-6 and summary_valid.item() == 2
''',
    "similarites-contraste-attention/code": '''
assert tuple(y.shape) == (2, 3, 8)
assert torch.allclose(_[0, :, 2], torch.zeros(3))
''',
    "echantillons-duree-canaux": '''
assert tuple(y.shape) == (192000,) and sr == 48000
assert duree == 4 and len(premiere_demi_seconde) == 24000
''',
    "nyquist-repliement-reechantillonnage": '''
assert len(x) == 192000 and len(y) == 64000
assert len(x) / sr == len(y) / sr_y == 4
''',
    "amplitude-puissance-decibels": '''
assert abs(peak - .8021240234375) < 1e-12
assert abs(rms - .12074498188527522) < 1e-12
assert abs(rms_dbfs + 18.362618186240418) < 1e-9
assert abs(crest_db - 16.447448657415617) < 1e-9
''',
    "fourier-coefficients-frequences": '''
assert np.allclose(f, [0, 1000, 2000, 3000, 4000])
assert np.allclose(modules, [0, 0, 4, 0, 0])
''',
    "stft-fenetres-hop-trames": '''
assert sr == 16000 and len(y) == 16000 and D.shape == (201, 98)
''',
    "resolution-fuite-zero-padding": '''
assert len(short) == 512 and len(long) == 2048
assert spectrum_512.shape == (257,) and spectrum_padded.shape == spectrum_long.shape == (1025,)
assert len(short) / sr == .032 and len(long) / sr == .128
assert sr / 512 == 31.25
''',
    "mel-representation-compressee": '''
assert D.shape == power.shape == (201, 98)
assert weights.shape == (64, 201) and mel.shape == mel_db.shape == (64, 98)
assert mel_db.min() >= -100.000001
''',
    "phase-canaux-annulations": '''
assert stereo.shape == (2, 4) and np.array_equal(mono, np.zeros(4))
''',
    "reconstruction-streaming-limites": '''
assert len(y_hat) == len(y_estimated) == len(y)
round_trip_max_error = float(np.max(np.abs(y - y_hat)))
assert round_trip_max_error < 1e-10
assert np.isfinite(y_estimated).all() and future_context_seconds == .032
''',
    "autoregression-et-causalite": '''
assert tuple(tokens.shape) == (1, 4)
assert tuple(inputs.shape) == tuple(targets.shape) == (1, 3)
assert tuple(logits.shape) == (1, 3, 10)
assert targets.tolist() == [[4, 7, 9]]
''',
    "echantillonnage-contexte-et-cout": '''
assert torch.allclose(p1, torch.tensor([.119202922, .880797078]), atol=1e-6)
assert torch.allclose(p2, torch.tensor([.01798621, .98201379]), atol=1e-6)
''',
    "vae-et-echantillonnage": '''
assert std.item() == 2 and tuple(z.shape) == (1, 1)
assert torch.equal(x_hat, z)
''',
    "kl-et-latent-inutilise": '''
assert tuple(kl_dim.shape) == (2, 4)
assert torch.equal(kl_per_example, torch.tensor([2., 2.])) and kl.item() == 2
assert abs(loss.item() - .45) < 1e-6
discrete_kl = sum(q * math.log(q / p) for q, p in zip([.5, .5], [.9, .1]))
assert abs(discrete_kl - .5108256237659907) < 1e-12
''',
    "diffusion-et-bruit": '''
assert tuple(xt.shape) == (1,) and torch.isfinite(loss)
''',
    "guidance-et-zones-connues": '''
assert eps_guided.item() == 8
assert torch.equal(output, torch.tensor([.1, .2, 7., 6.]))
''',
    "adaptation-lora-et-petit-corpus": '''
assert tuple((B @ A).shape) == tuple(W0.shape) == (3, 4)
assert torch.allclose(h, W0 @ x)
h.sum().backward()
assert W0.grad is None and torch.all(A.grad == 0) and torch.any(B.grad != 0)
analytic_dense_count = 4096 * 4096
analytic_lora_count = 4096 * 8 + 8 * 4096
assert analytic_dense_count == 16777216 and analytic_lora_count == 65536
''',
    "splits-et-fuites": '''
assert set(train_ids).isdisjoint(valid_ids) and set(train_ids).isdisjoint(test_ids)
assert set(valid_ids).isdisjoint(test_ids)
assert set(train.recording_ids) == set(train_ids)
assert np.allclose(scaler.mean_, train.features.mean(axis=0))
assert valid_scaled.shape == valid.features.shape == (4, 2)
''',
    "metriques-et-seuils": '''
assert precision == .75 and recall == .6 and balanced_accuracy == .7
''',
    "boucle-evaluation-et-surapprentissage": '''
assert count == 10 and abs(loss_sum - 14) < 1e-12 and abs(mean_loss - 1.4) < 1e-12
''',
    "variabilite-et-incertitude": '''
assert len(recording_ids) == len(sampled) == 20
assert len(set(sampled)) < 20  # Duplicates really are retained.
assert difference == score_on_groups(adapted, sampled) - score_on_groups(base, sampled)
example_mean_base = float(np.mean([79, 81, 83]))
example_mean_adapted = float(np.mean([77, 82, 87]))
assert example_mean_base == 81 and example_mean_adapted == 82
''',
    "tableaux-et-indexation": '''
assert premier.shape == (4,) and une_ligne.shape == (1, 4)
assert np.array_equal(fin, [[-.5, .5], [0., 1.]]) and Y.shape == (4, 2)
''',
    "references-et-copies": '''
assert np.array_equal(signal, [-.5, .5, 0., .5])
assert np.array_equal(copie, [-.5, 0.]) and np.shares_memory(signal, vue)
assert not np.shares_memory(signal, copie)
''',
    "reduire-les-bons-axes": '''
assert np.array_equal(rms, [.5, .5]) and np.array_equal(pics, [.5, 1.])
assert np.array_equal(cretes, [1., 2.]) and np.array_equal(F, [[.5, 1.], [.5, 2.]])
''',
    "broadcasting-et-algebre/walkthrough": '''
assert np.array_equal(contributions, [[1., 1.], [1., 2.]])
assert np.array_equal(scores, [[2.], [3.]])
''',
    "broadcasting-et-algebre/code": '''
assert ecarts.shape == (2, 1, 2) and np.array_equal(dist2, [[0.], [1.]])
''',
    "standardiser-et-preserver-precision": '''
assert np.array_equal(mu, [[.5, 1.5]]) and np.array_equal(sigma, [[0., .5]])
assert np.array_equal(den, [[1e-8, .5]]) and np.array_equal(Z, [[0., -1.], [0., 1.]])
''',
    "fonctions-et-arguments": '''
assert np.array_equal(z, [[0., 1.]])
''',
    "valeurs-par-defaut": '''
assert a == ["voix_a.wav"] and b == ["perc_b.wav"] and a is not b
''',
    "parcourir-et-filtrer": '''
assert gardes == [("voix_a.wav", 0), ("voix_c.wav", 0)]
assert (numero, ligne) == (2, ("voix_c.wav", 0))
''',
    "lire-fonctions-objets": '''
assert a.gain == .5 and b.gain == 1
''',
    "assembler-pipeline-scientifique": '''
assert np.array_equal(F, [[.5, 1.], [.5, 2.]])
assert np.array_equal(X, [[0., -1.], [0., 1.]]) and np.array_equal(y, [0, 1])
''',
    "valeurs-noms-et-calculs": '''
assert duree == 2 and nouvelle_duree == 1 and nombre == 16000
''',
    "listes-et-indices": '''
assert premier == 10 and milieu == [20., 30., 40.] and un_sur_deux == [10., 30., 50.]
''',
}

VARIANTS = {
    "similarites-contraste-attention": ("b = np.array([0.6, 0.8])", "b = 2 * np.array([0.6, 0.8])"),
    "quantification-et-tokens": ("value = 2.6", "value = 3.6"),
    "vae-et-echantillonnage": ("variance = 4.0", "variance = 9.0"),
}

# Executable checks for numeric examples written as prose or calculation tables.
# They are reported separately from the verbatim Python blocks above.
ADDITIONAL_CHECKS = {
    "python/references-listes": '''
a = [1, 2]
b = a
b.append(3)
assert a == [1, 2, 3] and b is a
original = [[1.], [2.]]
travail = original.copy()
travail[0].append(3.)
assert original == [[1., 3.], [2.]]
travail[1] = [9.]
assert original[1] == [2.]
''',
    "python/tri-indices": '''
scores = np.array([.4, .9, .1])
ordre = np.argsort(scores)[::-1]
assert ordre.tolist() == [1, 0, 2]
''',
    "python/reduction-keepdims": '''
S = np.array([[-.5, .5, -.5, .5], [0., 0., 0., 1.]])
mu = S.mean(axis=1)
mu_garde = S.mean(axis=1, keepdims=True)
assert np.array_equal(mu, [0., .25]) and mu_garde.shape == (2, 1)
''',
    "python/precision-accumulation": '''
x = np.array([1e8, 1., -1e8], dtype=np.float32)
mean32 = np.mean(x)
mean64 = np.mean(x, dtype=np.float64)
post_conversion = np.float64(mean32)
assert mean32 == post_conversion == 0 and mean64 == 1 / 3
''',
    "python/parcours": '''
valeurs = [-2, 0, 3]
positifs = [x * x for x in valeurs if x > 0]
assert positifs == [9]
g = (i * 2 for i in range(3))
premier = list(g)
second = list(g)
assert premier == [0, 2, 4] and second == []
truncated = list(zip([1, 2, 3], ["a", "b"]))
assert truncated == [(1, "a"), (2, "b")]
strict_error = None
try:
    list(zip([1, 2, 3], ["a", "b"], strict=True))
except ValueError as error:
    strict_error = str(error)
assert strict_error is not None
''',
    "python/metadonnees": '''
meta = {"nom": "voix_a.wav"}
duree = meta.get("duree", 0)
assert duree == 0 and "duree" not in meta
''',
    "python/paires-generales": '''
X = np.zeros((7, 3))
Y = np.zeros((5, 3))
ecarts = X[:, None, :] - Y[None, :, :]
dist2 = (ecarts ** 2).sum(axis=-1)
assert ecarts.shape == (7, 5, 3) and dist2.shape == (7, 5)
''',
    "signal/repliement": '''
t = np.arange(24) / 8000
high = np.cos(2 * np.pi * 6000 * t)
low = np.cos(2 * np.pi * 2000 * t)
assert np.allclose(high, low, atol=1e-12)
''',
    "signal/gain-et-reference": '''
gain = .5
amplitude_delta_db = 20 * math.log10(gain)
power_delta_db = 10 * math.log10(gain ** 2)
full_scale_sine_rms_db = 20 * math.log10(1 / math.sqrt(2))
assert math.isclose(amplitude_delta_db, -6.020599913279624)
assert math.isclose(amplitude_delta_db, power_delta_db)
assert math.isclose(full_scale_sine_rms_db, -3.0102999566398125)
''',
    "generation/compter-les-codes": '''
duration, frames_per_second, codebooks = 10, 50, 4
frames = duration * frames_per_second
indices = frames * codebooks
assert frames == 500 and indices == 2000
''',
    "generation/aligner-condition": '''
frames_per_second = 50
accent_seconds = 3
crop_seconds = 1
accent_frame = accent_seconds * frames_per_second
cropped_frame = accent_frame - crop_seconds * frames_per_second
assert accent_frame == 150 and cropped_frame == 100
''',
    "evaluation/interaction-illustrative": '''
base, plus_a, plus_b, plus_ab = 70, 72, 71, 76
gain_a = plus_a - base
gain_b = plus_b - base
gain_ab = plus_ab - base
interaction = plus_ab - plus_a - plus_b + base
assert (gain_a, gain_b, gain_ab, interaction) == (2, 1, 6, 3)
''',
    "evaluation/frechet-une-dimension": '''
reference_mean, base_mean, adapted_mean = 2., 0., 1.
reference_variance = base_variance = adapted_variance = 1.
def gaussian_distance_1d(mu, variance):
    return (mu - reference_mean) ** 2 + variance + reference_variance - 2 * math.sqrt(variance * reference_variance)
base_distance = gaussian_distance_1d(base_mean, base_variance)
adapted_distance = gaussian_distance_1d(adapted_mean, adapted_variance)
assert base_distance == 4 and adapted_distance == 1
''',
}


def key_for(chapter_id, kind):
    return chapter_id + "/" + kind


def named_text(value, prefix=""):
    if isinstance(value, str):
        yield prefix, value
    elif isinstance(value, dict):
        for key, part in value.items():
            if key in {"code", "url", "sourceIds", "questionIds"}:
                continue
            yield from named_text(part, f"{prefix}.{key}" if prefix else key)
    elif isinstance(value, list):
        for index, part in enumerate(value):
            yield from named_text(part, f"{prefix}[{index}]")


def display_word_count(chapter):
    """Match the current chapterText construction, excluding code and state dumps."""
    fragments = list((chapter.get("progression") or chapter.get("context", {})).values())
    for notion in chapter.get("notions", []):
        fragments.extend([notion["name"], notion["explanation"]])
    for block in chapter["blocks"]:
        fragments.extend(block.get(k, "") for k in ["text", "title", "caption", "goal", "result", "introduction", "explanation", "conclusion"])
        variant = block.get("variant", {})
        fragments.extend([variant.get("change", ""), variant.get("explanation", "")])
        fragments.extend(block.get("items", []) + block.get("observations", []) + block.get("reading", []))
        for step in block.get("steps", []):
            fragments.extend([step["title"], step["text"]])
        for node in block.get("nodes", []):
            fragments.extend([node["title"], node["text"]])
        for panel in block.get("panels", []):
            fragments.extend([panel["title"], *panel["items"]])
    fragments.extend(chapter.get("checkpoint", {}).get(k, "") for k in ["prompt", "explanation"])
    return len(" ".join(str(x) for x in fragments if x).split())


def snapshot(value):
    import numpy as np
    import torch
    if isinstance(value, torch.Tensor):
        tensor = value.detach().cpu()
        result = {"shape": list(tensor.shape), "dtype": str(tensor.dtype),
                  "requires_grad": value.requires_grad}
        if tensor.numel() <= 24:
            result["values"] = tensor.tolist()
        elif tensor.dtype != torch.bool and not tensor.is_complex():
            result.update(min=float(tensor.min()), max=float(tensor.max()), mean=float(tensor.double().mean()))
        return result
    if isinstance(value, np.ndarray):
        result = {"shape": list(value.shape), "dtype": str(value.dtype)}
        if value.size <= 24:
            result["values"] = value.tolist() if not np.iscomplexobj(value) else [[float(x.real), float(x.imag)] for x in value.ravel()]
        elif np.issubdtype(value.dtype, np.number) and not np.iscomplexobj(value):
            result.update(min=float(value.min()), max=float(value.max()), mean=float(value.mean()))
        return result
    if isinstance(value, (float, int, str, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)) and len(value) <= 24:
        if all(isinstance(x, (float, int, str, bool, list, tuple)) for x in value):
            return value
    if hasattr(value, "gain"):
        return {"gain": value.gain}
    return None


def json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return "NaN" if math.isnan(value) else ("+Infinity" if value > 0 else "-Infinity")
    if isinstance(value, dict):
        return {key: json_safe(part) for key, part in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(part) for part in value]
    return value


def execute(theme, chapter, block, block_index, code, variant=False):
    import numpy as np
    import torch
    torch.manual_seed(0)
    np.random.seed(0)
    kind = block["type"]
    compound = key_for(chapter["id"], kind)
    scaffold = SCAFFOLDS.get(compound, SCAFFOLDS.get(chapter["id"], "")) if kind != "first-example" else ""
    checks = CHECKS.get(compound, CHECKS.get(chapter["id"], "")) if kind != "first-example" else ""
    env = {"np": np, "torch": torch, "math": math, "__name__": "__course_example__"}
    identity = f"{theme}/{chapter['id']}/{block_index}/{kind}" + ("/variant" if variant else "")
    output = io.StringIO()
    started = time.perf_counter()
    result = {"id": identity, "source_sha256": hashlib.sha256(code.encode()).hexdigest(),
              "scaffold": scaffold.strip(), "assertions": checks.strip()}
    with contextlib.redirect_stdout(output):
        if scaffold:
            exec(compile(scaffold, identity + "/scaffold", "exec"), env)
        exec(compile(code, identity, "exec"), env)
        if checks:
            exec(compile(checks, identity + "/assertions", "exec"), env)
    result.update(status="executed", seconds=round(time.perf_counter() - started, 6), stdout=output.getvalue())
    if kind == "first-example":
        expected = block["variant"]["output"] if variant else block["output"]
        assert output.getvalue().strip() == expected.strip(), (identity, output.getvalue(), expected)
        result["expected_stdout_verified"] = True
    names = set()
    for node in ast.walk(ast.parse(code + "\n" + checks)):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.add(node.id)
    result["values"] = {}
    for name in sorted(names):
        if name.startswith("_") or name not in env:
            continue
        captured = snapshot(env[name])
        if captured is not None:
            result["values"][name] = captured
    return result, env


def verify_protected(courses):
    target = OUT / "existing-corpus-baseline.json"
    current = {course["themeId"]: {chapter["id"]: {
        key: chapter[key] for key in ["questionIds", "sourceIds", "checkpoint"]
    } for chapter in course["chapters"]} for course in courses}
    if not target.exists():
        target.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    baseline = json.loads(target.read_text("utf-8"))
    for theme, chapters in baseline.items():
        for id, protected in chapters.items():
            assert id in current[theme], f"Ancien identifiant perdu : {theme}/{id}"
            assert current[theme][id]["questionIds"] == protected["questionIds"], f"Questions modifiées : {theme}/{id}"
            assert current[theme][id]["checkpoint"] == protected["checkpoint"], f"Checkpoint modifié : {theme}/{id}"
            assert set(protected["sourceIds"]).issubset(current[theme][id]["sourceIds"]), f"Source perdue : {theme}/{id}"
    return sum(len(chapters) for chapters in baseline.values())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    os.chdir(ROOT)
    import numpy as np
    import torch
    torch.set_num_threads(1)
    courses = [json.loads((ROOT / "public/courses" / (theme + ".json")).read_text("utf-8")) for theme in THEMES]
    report = {"python": sys.version.split()[0], "device": "cpu", "torch_threads": 1,
              "common_scaffold": "import numpy as np; import torch; import math; torch.manual_seed(0); np.random.seed(0)",
              "versions": {name: importlib.metadata.version(name) for name in ["torch", "numpy", "scipy", "librosa", "soundfile"]},
              "examples": [], "additional_checks": [], "non_python_blocks": [], "findings": [],
              "walkthroughs_without_code": [], "chapters_over_1100_words": [], "long_sentences": []}
    report["protected_chapters_verified"] = verify_protected(courses)
    started = time.perf_counter()
    for course in courses:
        theme = course["themeId"]
        for chapter in course["chapters"]:
            id = chapter["id"]
            count = display_word_count(chapter)
            if count > 1100:
                report["chapters_over_1100_words"].append({"theme": theme, "chapterId": id, "words": count})
            for field, text in named_text(chapter):
                if field.endswith(".state"):
                    continue
                for sentence in re.split(r"(?<=[.!?])\s+", text):
                    if len(sentence.split()) > 30:
                        report["long_sentences"].append({"theme": theme, "chapterId": id, "field": field, "words": len(sentence.split()), "text": sentence})
            for index, block in enumerate(chapter["blocks"]):
                if block["type"] == "walkthrough" and not block.get("code"):
                    report["walkthroughs_without_code"].append({"theme": theme, "chapterId": id, "blockIndex": index, "title": block["title"]})
                code = block.get("code")
                if not code:
                    continue
                language = block.get("language", "python")
                if language != "python":
                    report["non_python_blocks"].append({"theme": theme, "chapterId": id, "blockIndex": index, "language": language, "reason": "Tableau textuel ou commandes shell ; ne pas les interpréter comme du Python."})
                    continue
                try:
                    print(f"RUN {theme}/{id}/{block['type']}", flush=True)
                    result, env = execute(theme, chapter, block, index, code)
                    report["examples"].append(result)
                    if block["type"] == "walkthrough" and id == "vae-et-echantillonnage":
                        if not math.isclose(float(env["z"].item()), 1., abs_tol=1e-6):
                            report["findings"].append({"theme": theme, "chapterId": id, "blockIndex": index, "severity": "numeric-claim", "claim": "Le bruit illustratif vaut −0,5 et z vaut 1.", "measured": {"eps": float(env["eps"].item()), "z": float(env["z"].item())}, "reason": "randn_like tire un nouveau bruit ; il n’impose pas la valeur illustrée.", "suggested_replacement": "eps = torch.full_like(mu, -0.5)  # Bruit fixé pour cette miniature ; randn_like pour un tirage réel."})
                    if block["type"] == "walkthrough" and id == "diffusion-et-bruit":
                        if not math.isclose(float(env["xt"].item()), .2, abs_tol=1e-6):
                            report["findings"].append({"theme": theme, "chapterId": id, "blockIndex": index, "severity": "numeric-claim", "claim": "Bruit −1, xt=0,2 et erreur 0,04 pour une prédiction −0,8.", "measured": {key: float(env[key].item()) for key in ["eps", "xt", "pred_eps", "loss"]}, "reason": "Le tirage aléatoire du code ne reprend pas le bruit fixé dans le calcul expliqué.", "suggested_replacement": "eps = torch.full_like(x0, -1.)  # Bruit fixé pour le calcul à la main."})
                    if block["type"] == "first-example" and block.get("variant"):
                        before, after = VARIANTS[id]
                        assert before in code, f"Transformation de variante à actualiser : {id}"
                        changed = code.replace(before, after, 1)
                        variant_result, _ = execute(theme, chapter, block, index, changed, variant=True)
                        variant_result["change"] = block["variant"]["change"]
                        variant_result["explicit_replacement"] = {"before": before, "after": after}
                        report["examples"].append(variant_result)
                except Exception as error:
                    report["findings"].append({"theme": theme, "chapterId": id, "blockIndex": index, "severity": "execution-failure", "error": repr(error), "traceback": traceback.format_exc()})
                    print(f"FAIL {theme}/{id}: {error}", flush=True)
    for name, code in ADDITIONAL_CHECKS.items():
        env = {"np": np, "torch": torch, "math": math}
        exec(compile(code, name, "exec"), env)
        values = {}
        for node in ast.walk(ast.parse(code)):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store) and node.id in env:
                captured = snapshot(env[node.id])
                if captured is not None:
                    values[node.id] = captured
        report["additional_checks"].append({"id": name, "code": code.strip(), "status": "executed", "values": values})
    report["total_seconds"] = round(time.perf_counter() - started, 3)
    report["summary"] = {"executions": len(report["examples"]), "additional_checks": len(report["additional_checks"]), "findings": len(report["findings"]), "non_python_blocks": len(report["non_python_blocks"]), "code_free_walkthroughs": len(report["walkthroughs_without_code"]), "long_sentences": len(report["long_sentences"]), "long_chapters": len(report["chapters_over_1100_words"])}
    target = OUT / "existing-corpus-results.json"
    target.write_text(json.dumps(json_safe(report), ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    audit = {key: report[key] for key in ["summary", "findings", "walkthroughs_without_code", "chapters_over_1100_words", "long_sentences"]}
    (OUT / "existing-corpus-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False), flush=True)
    print(f"Results: {target}", flush=True)
    return 1 if args.strict and report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
