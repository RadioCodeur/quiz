"""Exemples autonomes CPU : objectifs génératifs et budget de précision.

Les erreurs calculées ici sont pédagogiques. Ce ne sont ni des scores
perceptifs audio, ni des mesures de vitesse ou de mémoire résidente.
"""
import contextlib
import hashlib
import io
import json
import platform
import time
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
CODES = {
    "objectifs-diffusion-et-flow": '''import torch
torch.set_num_threads(1)
# Une coordonnée pédagogique, pas un enregistrement audio.
x0 = torch.tensor(2., dtype=torch.float64)
bruit = torch.tensor(-1., dtype=torch.float64)
alpha_bar = torch.tensor(0.64, dtype=torch.float64)
xt = alpha_bar.sqrt() * x0 + (1 - alpha_bar).sqrt() * bruit
bruit_predit = torch.tensor(-0.5, dtype=torch.float64)
perte_ddpm = (bruit_predit - bruit).square()
print(f"DDPM : xt={xt.item():.2f}, cible={bruit.item():.2f}, MSE={perte_ddpm.item():.2f}")
# Convention : s=0 sans condition ; s=1 avec condition.
sans_condition = torch.tensor(-0.2, dtype=torch.float64)
avec_condition = bruit_predit
s = 3.
guide = sans_condition + s * (avec_condition - sans_condition)
print(f"CFG : bruit guidé={guide.item():.2f}")
# Flow matching simplifié : t=0 au bruit, t=1 à la donnée.
z = bruit
t = 0.25
point = (1 - t) * z + t * x0
vitesse_cible = x0 - z
vitesse_predite = torch.tensor(2.5, dtype=torch.float64)
perte_flow = (vitesse_predite - vitesse_cible).square()
print(f"Flow : point={point.item():.2f}, vitesse={vitesse_cible.item():.2f}, MSE={perte_flow.item():.2f}")
# Un pas d'Euler avec la vitesse cible, connue seulement dans ce jouet.
pas = 0.25
point_suivant = z + pas * vitesse_cible
print(f"Euler depuis z : {point_suivant.item():.2f}")''',
    "efficacite-petit-budget": '''import torch
from torch import nn
torch.manual_seed(17)
torch.set_num_threads(1)
# Minuscule calcul manuel : 0.4 sur une grille de pas 1/3.
mini = torch.tensor(0.4, dtype=torch.float64)
mini_q = (mini * 3).round() / 3
print(f"À la main : {mini.item():.3f} -> {mini_q.item():.3f}")
# Comptes hors biais : une projection 64 -> 64 et un goulot 64 -> 8 -> 64.
d, rang = 64, 8
projection = nn.Linear(d, d, bias=False)
adapter = nn.Sequential(nn.Linear(d, rang, bias=False), nn.ReLU(),
                        nn.Linear(rang, d, bias=False))
total = sum(p.numel() for p in projection.parameters())
ajout = sum(p.numel() for p in adapter.parameters())
print(f"Paramètres : projection={total}, adapter={ajout}, fraction={ajout / total:.2f}")
# Test synthétique : 256 vecteurs de 64 caractéristiques, sans audio.
poids = torch.randn(d, d) * 0.1
entrees = torch.randn(256, d)
reference = entrees @ poids.T
mse_reference = (reference - reference).square().mean().item()
print(f"Float32 : MSE={mse_reference:.8f} ; poids={total * 4} octets")
mesures = []
for bits in (8, 3):
    maximum = 2 ** (bits - 1) - 1
    echelle = poids.abs().max() / maximum
    entiers = (poids / echelle).round().clamp(-maximum, maximum)
    reconstruits = entiers * echelle
    approximation = entrees @ reconstruits.T
    mse = (approximation - reference).square().mean().item()
    octets = (total * bits + 7) // 8
    mesures.append({"bits": bits, "logicalWeightBytes": octets, "mse": mse})
    print(f"{bits} bits : poids logiques={octets} octets, MSE={mse:.8f}")
# Une échéance analytique, pas une durée mesurée du réseau.
echeance_ms = 1000 * 256 / 48000
print(f"256 échantillons à 48 kHz : {echeance_ms:.3f} ms")''',
}


def main():
    report = {
        "python": platform.python_version(), "torch": torch.__version__,
        "device": "cpu", "threads": 1, "examples": {},
        "limits": [
            "Aucun modèle génératif externe entraîné ou évalué.",
            "MSE sur projections synthétiques, sans interprétation de qualité perceptive audio.",
            "Octets des poids calculés avec empaquetage idéal, hors échelles, activations, optimiseur et moteur.",
            "Quantification simulée en float32 ; aucun noyau entier ni gain de vitesse mesuré.",
            "Le calcul 256/48000 donne une échéance audio théorique, pas une latence système.",
        ],
    }
    for identifier, code in CODES.items():
        namespace = {"__name__": "__course_example__"}
        captured = io.StringIO()
        started = time.perf_counter()
        with contextlib.redirect_stdout(captured):
            exec(compile(code, identifier + ".py", "exec"), namespace)
        result = {
            "sourceSha256": hashlib.sha256(code.encode("utf-8")).hexdigest(),
            "codeSha256": hashlib.sha256(code.encode("utf-8")).hexdigest(),
            "stdout": captured.getvalue().strip(),
            "elapsedSeconds": round(time.perf_counter() - started, 6),
        }
        if identifier == "objectifs-diffusion-et-flow":
            assert torch.allclose(namespace["xt"], torch.tensor(1., dtype=torch.float64))
            assert namespace["perte_ddpm"].item() == 0.25
            assert abs(namespace["guide"].item() + 1.1) < 1e-12
            assert namespace["point"].item() == -0.25
            assert namespace["vitesse_cible"].item() == 3
            assert namespace["perte_flow"].item() == 0.25
            assert namespace["point_suivant"].item() == -0.25
            result["values"] = {key: namespace[key].item() for key in [
                "xt", "perte_ddpm", "guide", "point", "vitesse_cible", "perte_flow", "point_suivant"]}
        else:
            assert namespace["total"] == 4096
            assert namespace["ajout"] == 1024
            assert list(namespace["reference"].shape) == [256, 64]
            assert namespace["mesures"][0]["mse"] < namespace["mesures"][1]["mse"]
            assert namespace["echeance_ms"] == 1000 * 256 / 48000
            result["quantization"] = namespace["mesures"]
            result["values"] = {
                "projectionParameters": namespace["total"],
                "adapterParameters": namespace["ajout"],
                "adapterFraction": namespace["ajout"] / namespace["total"],
                "float32LogicalWeightBytes": namespace["total"] * 4,
                "audioDeadlineMilliseconds": namespace["echeance_ms"],
            }
        report["examples"][identifier] = result
        print(identifier, "OK", result["stdout"], sep="\n")
    target = ROOT / "scripts/verify/b-diffusion-efficiency-results.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
