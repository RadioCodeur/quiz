"""Execute the exact autonomous B1/B4 teaching examples and retain their evidence.

Use --check-fragment after work/b-attention-control.json has been authored.
No pretrained encoder or audio generator is loaded by these interface examples.
"""
from contextlib import redirect_stdout
import argparse
import hashlib
import io
import json
from pathlib import Path
import platform
import time


CASES = {
    "transformer-complet": r'''import torch
from torch import nn
torch.manual_seed(4)
torch.set_num_threads(1)

# Un extrait, trois positions, quatre caractéristiques fictives.
tokens = torch.tensor([[[1., 0., 1., 0.]] * 3])
p = torch.arange(3, dtype=torch.float32)
position = torch.stack((p.sin(), p.cos(), (p / 100).sin(), (p / 100).cos()), dim=1)
x = tokens + position.unsqueeze(0)
mini = torch.tensor([1., 3.])
normalise = nn.LayerNorm(2)(mini)

class Bloc(nn.Module):
    def __init__(self):
        super().__init__()
        self.norm1, self.norm2 = nn.LayerNorm(4), nn.LayerNorm(4)
        self.attention = nn.MultiheadAttention(4, 2, dropout=0., batch_first=True)
        self.reseau = nn.Sequential(nn.Linear(4, 8), nn.ReLU(), nn.Linear(8, 4))

    def forward(self, h, masque):
        z = self.norm1(h)  # Normaliser seulement les caractéristiques.
        contexte, poids = self.attention(z, z, z, attn_mask=masque,
                                         average_attn_weights=False)
        h = h + contexte  # Connexion résiduelle : conserver un chemin direct.
        return h + self.reseau(self.norm2(h)), poids

blocs = nn.ModuleList([Bloc(), Bloc()]).eval()
# True interdit une relation : chaque ligne ne consulte pas son futur.
masque = torch.triu(torch.ones(3, 3, dtype=torch.bool), diagonal=1)

def calcul(entree, masque):
    h, formes = entree, []
    for bloc in blocs:
        h, poids = bloc(h, masque)
        formes.append(list(h.shape))
    return h, poids, formes

with torch.no_grad():
    sortie, poids, formes = calcul(x, masque)
    modifie = x.clone()
    modifie[:, 2] += torch.tensor([10., -8., 6., -4.])
    causal, _, _ = calcul(modifie, masque)
    libre, _, _ = calcul(x, None)
    libre_modifie, _, _ = calcul(modifie, None)
    ecart_causal = (sortie[:, :2] - causal[:, :2]).abs().max().item()
    ecart_libre = (libre[:, :2] - libre_modifie[:, :2]).abs().max().item()

print("position_zero", position[0].tolist())
print("entree_zero", x[0, 0].tolist())
print("moyenne_variance", mini.mean().item(), mini.var(unbiased=False).item())
print("normalisation", [round(v, 6) for v in normalise.tolist()])
print("dimension_tete", 4 // 2)
print("formes_couches", formes)
print("forme_poids", list(poids.shape))
print("masque", masque.int().tolist())
print("ecart_passe_causal", round(ecart_causal, 6))
print("ecart_passe_libre", round(ecart_libre, 6))
''',
    "controle-multimodal-formes": r'''import torch
from torch import nn
torch.manual_seed(7)
torch.set_num_threads(1)

# Les encodeurs sont remplacés par des caractéristiques fictives.
# Ces nombres ne représentent ni un texte compris, ni un son encodé.
audio = torch.tensor([[[1., 3., 0., 0.], [2., 4., 1., 0.],
                       [3., 5., 0., 1.], [4., 6., 1., 1.]]])
texte = torch.tensor([[[1., 0., 1., 0.], [0., 1., 0., 1.]]])
reference = torch.tensor([[[.2, .4, .1, .3], [.3, .1, .4, .2], [.1, .2, .3, .4]]])
# Événements : instant, hauteur normalisée, vélocité normalisée.
evenements = torch.tensor([[[0., 60 / 127, .8], [1.5, 64 / 127, .6]]])
midi = nn.Linear(3, 4)(evenements)
conditions = torch.cat((texte, reference, midi), dim=1)

attention = nn.MultiheadAttention(4, 2, dropout=0., batch_first=True).eval()
with torch.no_grad():
    croisee, poids = attention(audio, conditions, conditions,
                               average_attn_weights=False)
    # Concaténer des positions : conserver la largeur, allonger la suite.
    suite = torch.cat((audio, conditions), dim=1)
    suite_traitee, _ = attention(suite, suite, suite)
    audio_apres_concat = suite_traitee[:, :audio.shape[1]]

    # Grille choisie : deux trames par seconde, origine commune.
    indices = (evenements[0, :, 0] * 2).floor().long()
    grille = torch.zeros(1, 4, 2)  # Début de note et vélocité.
    grille[0, indices, 0] = 1.
    grille[0, indices, 1] = evenements[0, :, 2]
    caracteristiques = torch.cat((audio, grille), dim=-1)
    local = nn.Linear(6, 4)(caracteristiques)

    # FiLM produit une échelle et un décalage pour chaque caractéristique.
    globale = texte.mean(dim=1)
    gamma, beta = nn.Linear(4, 8)(globale).chunk(2, dim=-1)
    gamma, beta = gamma.unsqueeze(1), beta.unsqueeze(1)
    module = gamma * audio + beta
    manuel = torch.tensor([2., .5]) * torch.tensor([1., 3.]) + torch.tensor([-1., 1.])

print("entrees", {"audio": list(audio.shape), "texte": list(texte.shape),
                  "reference": list(reference.shape), "MIDI": list(midi.shape)})
print("conditions", list(conditions.shape))
print("croisee", list(croisee.shape), "poids", list(poids.shape))
print("concat_positions", list(suite.shape), "audio_retenu", list(audio_apres_concat.shape))
print("indices_evenements", indices.tolist())
print("concat_caracteristiques", list(caracteristiques.shape), "projection", list(local.shape))
print("FiLM", list(globale.shape), list(gamma.shape), list(beta.shape), list(module.shape))
print("FiLM_manuel", manuel.tolist())
''',
}


def verify_transformer(ns):
    import torch
    assert list(ns["x"].shape) == [1, 3, 4]
    assert ns["formes"] == [[1, 3, 4], [1, 3, 4]]
    assert list(ns["poids"].shape) == [1, 2, 3, 3]
    assert torch.allclose(ns["normalise"], torch.tensor([-1., 1.]), atol=1e-5)
    assert torch.equal(ns["x"][0, 0], torch.tensor([1., 1., 1., 1.]))
    assert torch.allclose(ns["poids"].sum(dim=-1), torch.ones(1, 2, 3))
    assert torch.equal(ns["poids"].masked_select(ns["masque"]), torch.zeros(6))
    assert ns["ecart_causal"] == 0.0
    assert ns["ecart_libre"] > 0.01
    assert ns["tokens"].device.type == "cpu"
    bloc = ns["blocs"][0]
    intermediate = bloc.reseau[0](ns["x"])
    assert list(intermediate.shape) == [1, 3, 8]
    assert list(bloc.reseau(ns["x"]).shape) == [1, 3, 4]
    assert ns["mini"].mean().item() == 2.0
    assert ns["mini"].var(unbiased=False).item() == 1.0
    assert bloc.attention.head_dim == 2
    return {"layers": ns["formes"], "attentionWeights": list(ns["poids"].shape),
            "feedForwardIntermediate": list(intermediate.shape),
            "headDimension": bloc.attention.head_dim,
            "causalPastDifference": ns["ecart_causal"],
            "unmaskedPastDifference": ns["ecart_libre"], "assertions": 15}


def verify_control(ns):
    import torch
    for key, shape in {"audio": [1, 4, 4], "texte": [1, 2, 4],
                       "reference": [1, 3, 4], "midi": [1, 2, 4],
                       "conditions": [1, 7, 4], "croisee": [1, 4, 4],
                       "poids": [1, 2, 4, 7], "suite": [1, 11, 4],
                       "audio_apres_concat": [1, 4, 4], "grille": [1, 4, 2],
                       "caracteristiques": [1, 4, 6], "local": [1, 4, 4],
                       "globale": [1, 4], "gamma": [1, 1, 4],
                       "beta": [1, 1, 4], "module": [1, 4, 4]}.items():
        assert list(ns[key].shape) == shape, key
    assert ns["indices"].tolist() == [0, 3]
    assert torch.equal(ns["grille"][0, :, 0], torch.tensor([1., 0., 0., 1.]))
    assert torch.allclose(ns["poids"].sum(-1), torch.ones(1, 2, 4))
    assert ns["manuel"].tolist() == [1.0, 2.5]
    assert ns["audio"].device.type == "cpu"
    return {"shapeAssertions": 16, "assertions": 21, "eventFrames": ns["indices"].tolist(),
            "manualFiLM": ns["manuel"].tolist(), "usesPretrainedEncoder": False,
            "claimsGenerationQuality": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-fragment", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    import torch
    torch.set_num_threads(1)
    results = {"python": platform.python_version(), "torch": torch.__version__,
               "device": "cpu", "threads": torch.get_num_threads(), "cases": []}
    fragment = None
    if args.check_fragment:
        fragment = json.loads((root / "work/b-attention-control.json").read_text(encoding="utf-8"))
    else:
        courses=[json.loads((root / "public/courses" / (theme+".json")).read_text(encoding="utf-8")) for theme in ["audio-ml","generation-controle"]]
        fragment={"chapters":[{"chapter":chapter} for course in courses for chapter in course["chapters"]]}
    for chapter_id, code in CASES.items():
        started = time.perf_counter()
        ns, stdout = {}, io.StringIO()
        with redirect_stdout(stdout):
            exec(compile(code, f"course/{chapter_id}.py", "exec"), ns)
        metrics = verify_transformer(ns) if chapter_id == "transformer-complet" else verify_control(ns)
        digest = hashlib.sha256(code.encode("utf-8")).hexdigest()
        if fragment:
            chapter = next(item["chapter"] for item in fragment["chapters"]
                           if item["chapter"]["id"] == chapter_id)
            blocks = [block for block in chapter["blocks"]
                      if block.get("language") == "python" and block.get("code")]
            assert len(blocks) == 1, "One autonomous Python example per chapter"
            assert blocks[0]["code"] == code, "Displayed and executed code must be byte-identical"
            assert 2 <= len(chapter["notions"]) <= 4
            assert len(chapter["takeaways"]) == 3
            assert len(chapter["checkpoint"]["options"]) == 4
            assert chapter["questionIds"] == []
            assert len([b for b in chapter["blocks"] if b.get("tone") == "pitfall"]) == 1
            assert chapter["blocks"][-1]["text"].startswith("À dire en entretien :")
            assert any(b["type"] in ("visual", "plot") for b in chapter["blocks"])
            for step in blocks[0]["steps"]:
                assert all(1 <= n <= len(code.splitlines()) for n in step.get("lines", []))
        results["cases"].append({"chapterId": chapter_id, "sha256": digest,
                                 "stdout": stdout.getvalue(), "metrics": metrics,
                                 "seconds": time.perf_counter() - started,
                                 "displayedCodeChecked": bool(fragment)})
    destination = root / "scripts/verify/b-attention-control-results.json"
    destination.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
