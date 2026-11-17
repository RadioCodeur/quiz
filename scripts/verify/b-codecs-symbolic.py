"""Execute the exact standalone examples for Lot B: RVQ and symbolic music.

No downloads, trained weights, or audio-quality benchmark are involved.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import platform
import time
from pathlib import Path

import torch


CODES = {
    "codecs-neuronaux-rvq": '''import torch
torch.set_num_threads(1)

# Deux coordonnées latentes : ce ne sont pas des échantillons audio.
z = torch.tensor([[0.9], [-0.8]])
codebooks = [torch.tensor([[-1.0], [0.0], [1.0]]),
             torch.tensor([[-0.25], [0.0], [0.25]])]
residual = z.clone()
reconstruction = torch.zeros_like(z)
codes = []
for stage, book in enumerate(codebooks, start=1):
    # Chaque ligne compare un résidu à toutes les entrées du dictionnaire.
    distances = (residual[:, None, :] - book[None, :, :]).square().sum(-1)
    indices = distances.argmin(dim=1)
    quantized = book[indices]
    reconstruction += quantized
    residual -= quantized
    codes.append(indices)
    print(f"étage {stage} : indices {indices.tolist()}")
    print("  résidu :", [round(v, 2) for v in residual.flatten().tolist()])
mse = (z - reconstruction).square().mean()
print("reconstruction :", [round(v, 2) for v in reconstruction.flatten().tolist()])
print(f"erreur quadratique moyenne : {mse.item():.6f}")
''',
    "symbolique-midi-et-audio": '''import torch
torch.set_num_threads(1)

# Un vocabulaire miniature, inspiré des événements MIDI, pas un fichier MIDI.
vocabulary = [("NOTE_ON", 60), ("NOTE_ON", 64),
              ("NOTE_OFF", 60), ("NOTE_OFF", 64),
              ("SHIFT", 240), ("SHIFT", 480),
              ("VELOCITY", 80), ("VELOCITY", 100)]
events = [("VELOCITY", 80), ("NOTE_ON", 60), ("SHIFT", 240),
          ("NOTE_OFF", 60), ("VELOCITY", 100), ("NOTE_ON", 64),
          ("SHIFT", 480), ("NOTE_OFF", 64)]
tokens = torch.tensor([vocabulary.index(event) for event in events], dtype=torch.long)
tempo, ticks_per_beat, sample_rate = 120, 480, 16000
seconds_per_tick = 60 / tempo / ticks_per_beat
ticks, velocity = 0, 80
active, notes = {}, []
for token in tokens.tolist():
    kind, value = vocabulary[token]
    if kind == "SHIFT":
        ticks += value
    elif kind == "VELOCITY":
        velocity = value
    elif kind == "NOTE_ON":
        active[value] = (ticks, velocity)
    elif kind == "NOTE_OFF":
        start, note_velocity = active.pop(value)
        notes.append((value, start * seconds_per_tick,
                      (ticks - start) * seconds_per_tick, note_velocity))
assert not active
print("jetons :", tokens.tolist())
for pitch, start, duration, note_velocity in notes:
    print(f"note {pitch} : début {start:.2f} s ; durée {duration:.2f} s ; vélocité {note_velocity}")
duration_seconds = ticks * seconds_per_tick
sample_count = round(duration_seconds * sample_rate)
print(f"durée totale : {duration_seconds:.2f} s")
print(f"représentations : {tokens.numel()} jetons ; {sample_count} échantillons mono à {sample_rate} Hz")
''',
}


def execute_examples():
    torch.set_num_threads(1)
    report = {
        "python": platform.python_version(),
        "torch": torch.__version__,
        "device": "cpu",
        "threads": torch.get_num_threads(),
        "seed": "No randomness: fixed codebooks and fixed event sequence.",
        "limitations": [
            "The RVQ example isolates quantization: no learned encoder/decoder is trained.",
            "The symbolic vocabulary is deliberately tiny and is not a Standard MIDI File encoder.",
            "Representation counts are not a measurement of bytes, speed, compression ratio, or audio quality.",
        ],
        "examples": {},
    }
    for chapter_id, code in CODES.items():
        stream = io.StringIO()
        namespace = {}
        started = time.perf_counter()
        with contextlib.redirect_stdout(stream):
            exec(compile(code, chapter_id, "exec"), namespace)
        example = {
            "codeSha256": hashlib.sha256(code.encode("utf-8")).hexdigest(),
            "stdout": stream.getvalue(),
            "elapsedSeconds": time.perf_counter() - started,
        }
        if chapter_id == "codecs-neuronaux-rvq":
            assert [v.tolist() for v in namespace["codes"]] == [[2, 0], [1, 2]]
            assert torch.allclose(namespace["reconstruction"], torch.tensor([[1.0], [-0.75]]))
            assert abs(namespace["mse"].item() - 0.00625) < 1e-7
            example["measurements"] = {
                "codesByStage": [v.tolist() for v in namespace["codes"]],
                "reconstruction": namespace["reconstruction"].tolist(),
                "residual": namespace["residual"].tolist(),
                "meanSquaredError": namespace["mse"].item(),
            }
        else:
            assert namespace["tokens"].tolist() == [6, 0, 4, 2, 7, 1, 5, 3]
            assert namespace["notes"] == [(60, 0.0, 0.25, 80), (64, 0.25, 0.5, 100)]
            assert namespace["sample_count"] == 12000
            assert [namespace["vocabulary"][i] for i in namespace["tokens"].tolist()] == namespace["events"]
            example["measurements"] = {
                "tokens": namespace["tokens"].tolist(),
                "notesPitchOnsetSecondsDurationSecondsVelocity": namespace["notes"],
                "durationSeconds": namespace["duration_seconds"],
                "sampleRate": namespace["sample_rate"],
                "monoSampleCount": namespace["sample_count"],
            }
        report["examples"][chapter_id] = example
    fragment_path = Path(__file__).resolve().parents[2] / "work" / "b-codecs-symbolic.json"
    fragment = json.loads(fragment_path.read_text(encoding="utf-8"))
    checked = []
    for item in fragment["chapters"]:
        chapter = item["chapter"]
        walkthrough = next(block for block in chapter["blocks"] if block["type"] == "walkthrough")
        assert walkthrough["code"] == CODES[chapter["id"]]
        assert walkthrough["steps"][-1]["state"] == report["examples"][chapter["id"]]["stdout"]
        assert chapter["blocks"][-1]["text"].startswith("À dire en entretien :")
        assert sum(block["type"] == "callout" and block["tone"] == "pitfall" for block in chapter["blocks"]) == 1
        checked.append(chapter["id"])
    report["fragmentValidation"] = {"exactCodeAndOutputCopies": checked, "oralConclusionAndSinglePitfall": "passed"}
    return report


if __name__ == "__main__":
    result = execute_examples()
    output_path = Path(__file__).with_name("b-codecs-symbolic-results.json")
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
