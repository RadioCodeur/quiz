"""Exécute les six exemples du lot A, sur CPU, et conserve leurs preuves.

Les chaînes CODES sont les programmes copiés dans les nouveaux chapitres.
Commande : python scripts/verify/pytorch-additions.py
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
from pathlib import Path
import platform
import tempfile
import time

import torch

ROOT = Path(__file__).resolve().parents[2]

CODES = {
    "pytorch-en-une-page": '''import torch
w = torch.tensor(3., requires_grad=True)
y = w * 2
perte = (y - 0) ** 2
perte.backward()
print(y.item(), perte.item(), w.grad.item())''',
    "retropropagation-a-la-main": '''import torch
x = torch.tensor(2.)
w1 = torch.tensor(3., requires_grad=True)
w2 = torch.tensor(-1., requires_grad=True)
h = w1 * x
h.retain_grad()
y = w2 * h
y.retain_grad()
perte = (y - 0) ** 2
perte.backward()
print("h, y, L :", h.item(), y.item(), perte.item())
print("dL/dy, dL/dh :", y.grad.item(), h.grad.item())
print("w1.grad, w2.grad :", w1.grad.item(), w2.grad.item())''',
    "boucle-entrainement-complete": '''from pathlib import Path
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader

torch.manual_seed(17)
torch.set_num_threads(1)
device = torch.device("cpu")
perte_neutre = nn.functional.cross_entropy(torch.zeros(1, 2), torch.tensor([0]))
print(f"Perte de deux scores égaux : {perte_neutre.item():.6f}")

def fabriquer(n):
    cibles = torch.arange(n) % 2
    centres = (2 * cibles.float() - 1).unsqueeze(1)
    mesures = 0.4 * torch.randn(n, 3) + centres
    return mesures, cibles

class Nuages(Dataset):
    def __init__(self, mesures, cibles):
        self.mesures, self.cibles = mesures, cibles
    def __len__(self):
        return len(self.cibles)
    def __getitem__(self, indice):
        return self.mesures[indice], self.cibles[indice]

def assembler(exemples):
    mesures, cibles = zip(*exemples)
    return torch.stack(mesures), torch.stack(cibles).long()

train = Nuages(*fabriquer(128))
validation = Nuages(*fabriquer(64))
train_loader = DataLoader(train, batch_size=32, shuffle=True,
                          collate_fn=assembler, num_workers=0)
val_loader = DataLoader(validation, batch_size=32, shuffle=False,
                        collate_fn=assembler, num_workers=0)

def creer_modele():
    return nn.Sequential(nn.Linear(3, 8), nn.ReLU(), nn.Linear(8, 2))

modele = creer_modele().to(device)
critere = nn.CrossEntropyLoss()
optimiseur = torch.optim.Adam(modele.parameters(), lr=0.03)
historique = []
N = 5
for epoch in range(1, N + 1):
    modele.train()
    somme, effectif = 0.0, 0
    for mesures, cibles in train_loader:
        mesures, cibles = mesures.to(device), cibles.to(device)
        optimiseur.zero_grad(set_to_none=True)
        perte = critere(modele(mesures), cibles)
        perte.backward()
        optimiseur.step()
        somme += perte.item() * len(cibles)
        effectif += len(cibles)
    train_loss = somme / effectif

    modele.eval()
    somme, effectif = 0.0, 0
    with torch.no_grad():
        for mesures, cibles in val_loader:
            mesures, cibles = mesures.to(device), cibles.to(device)
            perte = critere(modele(mesures), cibles)
            somme += perte.item() * len(cibles)
            effectif += len(cibles)
    val_loss = somme / effectif
    historique.append([train_loss, val_loss])
    print(f"epoch {epoch}: train={train_loss:.6f}, val={val_loss:.6f}")

chemin = Path("modele-nuages.pt")
torch.save({"model": modele.state_dict(), "classes": ["nuage 0", "nuage 1"]}, chemin)
recharge = creer_modele().to(device)
etat = torch.load(chemin, map_location=device, weights_only=True)
recharge.load_state_dict(etat["model"])
recharge.eval()
with torch.no_grad():
    sonde = validation.mesures[:2].to(device)
    identique = torch.equal(modele(sonde), recharge(sonde))
print("Rechargement identique :", identique)''',
    "lire-erreurs-pytorch": '''import torch
from torch import nn

def montrer(nom, operation):
    try:
        operation()
    except (RuntimeError, AttributeError) as erreur:
        print(nom, "|", type(erreur).__name__, "|", str(erreur))

montrer("forme", lambda: nn.Linear(3, 2)(torch.ones(2, 4)))
montrer("type", lambda: nn.CrossEntropyLoss()(
    torch.tensor([[1., 2.]]), torch.tensor([1.])))
montrer("device", lambda: torch.ones(2) + torch.ones(2, device="meta"))
montrer("gradient", lambda: torch.tensor(2., requires_grad=True).grad.item())
montrer("vue", lambda: torch.arange(6).reshape(2, 3).t().view(6))

assert nn.Linear(3, 2)(torch.ones(2, 3)).shape == (2, 2)
assert torch.isfinite(nn.CrossEntropyLoss()(
    torch.tensor([[1., 2.]]), torch.tensor([1], dtype=torch.long)))
assert torch.equal(torch.ones(2) + torch.ones(2), torch.tensor([2., 2.]))
w = torch.tensor(2., requires_grad=True)
(w ** 2).backward()
assert w.grad.item() == 4
assert torch.arange(6).reshape(2, 3).t().reshape(6).shape == (6,)
print("Cinq corrections vérifiées.")''',
    "optimiseurs-regularisation-pratique": '''import copy
import torch
from torch import nn

torch.manual_seed(17)
torch.set_num_threads(1)
for classe in [torch.optim.SGD, torch.optim.Adam, torch.optim.AdamW]:
    w = nn.Parameter(torch.tensor(1.))
    opt = classe([w], lr=0.1, weight_decay=0.1)
    (w ** 2).backward()
    opt.step()
    print(classe.__name__, f"{w.item():.6f}")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
modele = nn.Linear(1, 1).to(device)
x = torch.tensor([[-1.], [0.], [1.]], device=device)
y = 2 * x
vx = torch.tensor([[-0.5], [0.5]], device=device)
vy = 2 * vx
opt = torch.optim.AdamW(modele.parameters(), lr=0.1, weight_decay=0.01)
scheduler = torch.optim.lr_scheduler.StepLR(opt, step_size=3, gamma=0.5)
amp_actif = device.type == "cuda"
scaler = torch.amp.GradScaler("cuda", enabled=amp_actif)
meilleure, attente, meilleur_etat = float("inf"), 0, None
for epoch in range(1, 9):
    modele.train()
    opt.zero_grad(set_to_none=True)
    with torch.amp.autocast(device_type=device.type, enabled=amp_actif):
        perte = nn.functional.mse_loss(modele(x), y)
    scaler.scale(perte).backward()
    scaler.step(opt)
    scaler.update()
    modele.eval()
    with torch.no_grad():
        val = nn.functional.mse_loss(modele(vx), vy).item()
    if val < meilleure - 1e-5:
        meilleure, attente = val, 0
        meilleur_etat = copy.deepcopy(modele.state_dict())
    else:
        attente += 1
    print(f"epoch {epoch}: val={val:.6f}, lr={opt.param_groups[0]['lr']:.5f}")
    scheduler.step()
    if attente >= 2:
        break
modele.load_state_dict(meilleur_etat)
print("Calcul :", device.type, "| AMP active :", amp_actif)
print("Octets des paramètres :", sum(p.numel() * p.element_size() for p in modele.parameters()))
if device.type == "cuda":
    print("Octets CUDA alloués :", torch.cuda.memory_allocated(device))''',
    "conv-mel-autoencodeur": '''import torch
import torchaudio
from torch import nn

torch.manual_seed(17)
torch.set_num_threads(1)
sr = 16000
t = torch.arange(sr) / sr
ondes = torch.stack([0.2 * torch.sin(2 * torch.pi * 220 * t),
                     0.2 * torch.sin(2 * torch.pi * 440 * t)])
fenetre = torch.hann_window(400)
D = torch.stft(ondes, n_fft=400, hop_length=160, window=fenetre,
               center=False, return_complex=True)
transformation = torchaudio.transforms.MelSpectrogram(
    sample_rate=sr, n_fft=400, win_length=400, hop_length=160,
    n_mels=64, f_min=0., f_max=8000., center=False,
    mel_scale="slaney", norm="slaney", power=2.)
mel = transformation(ondes) / fenetre.sum().square()
entree = (10 * mel.clamp_min(1e-10).log10() / 100)[:, None, :, :96]
encodeur = nn.Sequential(nn.Conv2d(1, 4, 3, stride=2, padding=1),
                        nn.ReLU(), nn.Conv2d(4, 8, 3, stride=2, padding=1), nn.ReLU())
decodeur = nn.Sequential(nn.ConvTranspose2d(8, 4, 4, stride=2, padding=1),
                        nn.ReLU(), nn.ConvTranspose2d(4, 1, 4, stride=2, padding=1))
modele = nn.Sequential(encodeur, decodeur)
print("STFT :", tuple(D.shape), "| mel :", tuple(mel.shape))
formes = []
z = entree
for nom, module in [("entrée", nn.Identity()),
                    ("conv1", encodeur[0]), ("relu1", encodeur[1]),
                    ("conv2", encodeur[2]), ("relu2", encodeur[3]),
                    ("transposée1", decodeur[0]), ("relu3", decodeur[1]),
                    ("transposée2", decodeur[2])]:
    z = module(z)
    formes.append([nom, list(z.shape)])
    print(nom, tuple(z.shape))
opt = torch.optim.Adam(modele.parameters(), lr=0.01)
opt.zero_grad(set_to_none=True)
reconstruction = modele(entree)
perte = nn.functional.mse_loss(reconstruction, entree)
avant = perte.item()
perte.backward()
opt.step()
with torch.no_grad():
    apres = nn.functional.mse_loss(modele(entree), entree).item()
print(f"MSE avant={avant:.6f}, après un pas={apres:.6f}")''',
}


def execute_code(identifier, code):
    torch.manual_seed(17)
    torch.set_num_threads(1)
    namespace = {"__name__": "__course_example__"}
    captured = io.StringIO()
    started = time.perf_counter()
    # Les sauvegardes des exemples ne restent pas dans le dépôt.
    with tempfile.TemporaryDirectory(prefix="squoinks-pytorch-") as directory:
        import os
        previous = os.getcwd()
        try:
            os.chdir(directory)
            with contextlib.redirect_stdout(captured):
                exec(compile(code, f"{identifier}.py", "exec"), namespace)
        finally:
            os.chdir(previous)
    result = {
        "codeSha256": hashlib.sha256(code.encode()).hexdigest(),
        "stdout": captured.getvalue().strip(),
        "elapsedSeconds": round(time.perf_counter() - started, 6),
    }
    if identifier == "pytorch-en-une-page":
        assert [namespace[k].item() for k in ["y", "perte"]] == [6, 36]
        assert namespace["w"].grad.item() == 24
    elif identifier == "retropropagation-a-la-main":
        assert namespace["w1"].grad.item() == 24
        assert namespace["w2"].grad.item() == -72
        assert namespace["y"].grad.item() == -12
        assert namespace["h"].grad.item() == 12
    elif identifier == "boucle-entrainement-complete":
        assert namespace["identique"] is True
        assert len(namespace["historique"]) == 5
        result["losses"] = namespace["historique"]
    elif identifier == "lire-erreurs-pytorch":
        assert len(result["stdout"].splitlines()) == 6
    elif identifier == "optimiseurs-regularisation-pratique":
        # Cette vérification documente un calcul CPU, jamais une mesure CUDA.
        assert namespace["device"].type == "cpu", "Exécuter ce vérificateur sans GPU pour la référence CPU."
        result["bestValidationLoss"] = namespace["meilleure"]
    elif identifier == "conv-mel-autoencodeur":
        assert list(namespace["D"].shape) == [2, 201, 98]
        assert list(namespace["mel"].shape) == [2, 64, 98]
        assert list(namespace["reconstruction"].shape) == [2, 1, 64, 96]
        assert torch.isfinite(namespace["perte"])
        result.update(shapes=namespace["formes"], mseBefore=namespace["avant"], mseAfter=namespace["apres"])
    return result


def main():
    results = {
        "python": platform.python_version(), "torch": torch.__version__,
        "device": "cpu", "threads": 1, "examples": {},
        "notes": "Sorties sur des données synthétiques. Aucune performance réelle d’un modèle audio ni accélération GPU n’est mesurée.",
    }
    import torchaudio
    results["torchaudio"] = torchaudio.__version__
    for identifier, code in CODES.items():
        result = execute_code(identifier, code)
        results["examples"][identifier] = result
        print(identifier, "OK", f"{result['elapsedSeconds']:.3f}s")
    target = ROOT / "scripts/verify/pytorch-additions-results.json"
    target.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
