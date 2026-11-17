"""Create the fourteen historical PyTorch notebooks from the verified course.

No code is executed by the site. The parent verification runner executes the
notebook cells and metadata.quiz.exerciseSolutions separately on CPU.
"""
from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW_IDS = {
    "pytorch-en-une-page", "retropropagation-a-la-main",
    "boucle-entrainement-complete", "lire-erreurs-pytorch",
    "optimiseurs-regularisation-pratique", "conv-mel-autoencodeur",
}


def exercise(title: str, prompt: str, holes: str, solution: str):
    return dict(title=title, prompt=prompt, holes=holes, solution=solution)


EXERCISES = {
    "du-pipeline-au-modele": [
        exercise("Une classe pour chaque extrait",
                 "Nous avons deux extraits en lignes. Complétons l’axe de la décision, sans modifier les scores.",
                 '''scores = torch.tensor([[0., 2.], [3., 1.]])
classes = scores.argmax(dim=...)
print(classes.tolist())''',
                 '''import torch
scores = torch.tensor([[0., 2.], [3., 1.]])
classes = scores.argmax(dim=1)
assert classes.tolist() == [1, 0]
print(classes.tolist())'''),
        exercise("Comparer la décision à sa cible",
                 "Une décision ne devient une réussite qu’après comparaison avec sa cible. Complétons ce comptage.",
                 '''predictions = torch.tensor([0, 1, 1])
cibles = torch.tensor([0, 0, 1])
accords = ...
nombre_correct = accords....()
print(nombre_correct.item())''',
                 '''import torch
predictions = torch.tensor([0, 1, 1])
cibles = torch.tensor([0, 0, 1])
accords = predictions == cibles
nombre_correct = accords.sum()
assert nombre_correct.item() == 2
print(nombre_correct.item())'''),
    ],
    "tenseur-forme-type-device": [
        exercise("Nommer le type des mesures",
                 "Construisons quatre observations contenant chacune trois mesures continues. Complétons leur type numérique.",
                 '''X = torch.arange(12, dtype=...).reshape(4, 3)
print(tuple(X.shape), X.dtype)''',
                 '''import torch
X = torch.arange(12, dtype=torch.float32).reshape(4, 3)
assert tuple(X.shape) == (4, 3)
assert X.dtype == torch.float32
print(tuple(X.shape), X.dtype)'''),
        exercise("Préparer des indices de classes",
                 "Les indices reçus sont flottants. Convertissons-les pour une perte qui attend des indices entiers.",
                 '''cibles = torch.tensor([0., 1.])
cibles = cibles.to(dtype=..., device=...)
print(cibles.dtype, cibles.device)''',
                 '''import torch
cibles = torch.tensor([0., 1.])
cibles = cibles.to(dtype=torch.long, device="cpu")
assert cibles.dtype == torch.long
assert cibles.device.type == "cpu"
print(cibles.dtype, cibles.device)'''),
    ],
    "organiser-les-axes": [
        exercise("Ajouter le canal du modèle",
                 "Notre entrée est organisée en extraits, bandes, trames. Ajoutons un axe de canal entre les extraits et les bandes.",
                 '''mel = torch.zeros(2, 64, 5)
entree = mel.unsqueeze(...)
print(tuple(entree.shape))''',
                 '''import torch
mel = torch.zeros(2, 64, 5)
entree = mel.unsqueeze(1)
assert tuple(entree.shape) == (2, 1, 64, 5)
print(tuple(entree.shape))'''),
        exercise("Échanger les rôles des axes",
                 "Nous voulons que chaque colonne initiale devienne une ligne. Complétons la transposition, sans réarranger seulement les tailles.",
                 '''X = torch.arange(6).reshape(2, 3)
Y = X....(0, 1)
print(Y.tolist())''',
                 '''import torch
X = torch.arange(6).reshape(2, 3)
Y = X.transpose(0, 1)
assert Y.tolist() == [[0, 3], [1, 4], [2, 5]]
print(Y.tolist())'''),
    ],
    "selection-diffusion-reduction": [
        exercise("Une référence par descripteur",
                 "Chaque ligne est un extrait. Calculons une moyenne par colonne tout en conservant son axe réduit.",
                 '''X = torch.tensor([[1., 3.], [3., 7.]])
reference = X.mean(dim=..., keepdim=...)
centres = X - reference
print(reference.tolist(), centres.tolist())''',
                 '''import torch
X = torch.tensor([[1., 3.], [3., 7.]])
reference = X.mean(dim=0, keepdim=True)
centres = X - reference
assert tuple(reference.shape) == (1, 2)
assert torch.allclose(centres.mean(dim=0), torch.zeros(2))
print(reference.tolist(), centres.tolist())'''),
        exercise("Garder la cible de la ligne sélectionnée",
                 "Le filtre de durée doit sélectionner les observations et leurs cibles avec le même masque.",
                 '''X = torch.tensor([[.2, .8], [.9, .1], [.4, .6]])
cibles = torch.tensor([1, 0, 1])
durees = torch.tensor([2., .2, 1.5])
masque = durees >= 1.
X_gardes, cibles_gardees = ..., ...
print(X_gardes.tolist(), cibles_gardees.tolist())''',
                 '''import torch
X = torch.tensor([[.2, .8], [.9, .1], [.4, .6]])
cibles = torch.tensor([1, 0, 1])
durees = torch.tensor([2., .2, 1.5])
masque = durees >= 1.
X_gardes, cibles_gardees = X[masque], cibles[masque]
assert tuple(X_gardes.shape) == (2, 2)
assert cibles_gardees.tolist() == [1, 1]
print(X_gardes.tolist(), cibles_gardees.tolist())'''),
    ],
    "dataset-et-batches": [
        exercise("Décrire un jeu de données",
                 "Complétons les deux méthodes qui permettent au chargeur de retrouver un exemple et sa cible.",
                 '''from torch.utils.data import Dataset
class Mini(Dataset):
    def __init__(self):
        self.exemples = [torch.tensor([1., 2.]), torch.tensor([3., 4.])]
        self.cibles = [0, 1]
    def __len__(self):
        return ...
    def __getitem__(self, i):
        return ..., ...
jeu = Mini()
print(len(jeu), jeu[1])''',
                 '''import torch
from torch.utils.data import Dataset
class Mini(Dataset):
    def __init__(self):
        self.exemples = [torch.tensor([1., 2.]), torch.tensor([3., 4.])]
        self.cibles = [0, 1]
    def __len__(self):
        return len(self.exemples)
    def __getitem__(self, i):
        return self.exemples[i], self.cibles[i]
jeu = Mini()
assert len(jeu) == 2 and jeu[1][1] == 1
print(len(jeu), jeu[1])'''),
        exercise("Assembler des durées différentes",
                 "Complétons le remplissage et le masque. Une valeur ajoutée pour remplir ne devient pas une observation réelle.",
                 '''from torch.nn.utils.rnn import pad_sequence
def assembler(exemples):
    signaux, cibles = zip(*exemples)
    longueurs = torch.tensor([len(x) for x in signaux])
    valeurs = pad_sequence(signaux, batch_first=...)
    masque = torch.arange(valeurs.shape[1])[None, :] < ...
    return valeurs, torch.tensor(cibles), masque
lot = [(torch.tensor([[1.], [2.]]), 0), (torch.tensor([[3.]]), 1)]
valeurs, cibles, masque = assembler(lot)
print(tuple(valeurs.shape), masque.tolist())''',
                 '''import torch
from torch.nn.utils.rnn import pad_sequence
def assembler(exemples):
    signaux, cibles = zip(*exemples)
    longueurs = torch.tensor([len(x) for x in signaux])
    valeurs = pad_sequence(signaux, batch_first=True)
    masque = torch.arange(valeurs.shape[1])[None, :] < longueurs[:, None]
    return valeurs, torch.tensor(cibles), masque
lot = [(torch.tensor([[1.], [2.]]), 0), (torch.tensor([[3.]]), 1)]
valeurs, cibles, masque = assembler(lot)
assert tuple(valeurs.shape) == (2, 2, 1)
assert masque.tolist() == [[True, True], [True, False]]
assert cibles.tolist() == [0, 1]
print(tuple(valeurs.shape), masque.tolist())'''),
    ],
    "moyennes-masquees": [
        exercise("Ignorer le remplissage dans la moyenne",
                 "Les deux valeurs du premier extrait sont réelles. Seule la première du second extrait est réelle.",
                 '''batch = torch.tensor([[[1.], [3.]], [[6.], [0.]]])
masque = torch.tensor([[True, True], [True, False]])
m = masque.unsqueeze(-1)
moyennes = (batch * m).sum(dim=1) / ...
print(moyennes.tolist())''',
                 '''import torch
batch = torch.tensor([[[1.], [3.]], [[6.], [0.]]])
masque = torch.tensor([[True, True], [True, False]])
m = masque.unsqueeze(-1)
moyennes = (batch * m).sum(dim=1) / m.sum(dim=1)
assert moyennes.tolist() == [[2.], [6.]]
print(moyennes.tolist())'''),
        exercise("Choisir le bon dénominateur",
                 "Les nombres représentent déjà des erreurs au carré. Calculons leur moyenne sur les positions réelles uniquement.",
                 '''erreurs = torch.tensor([[1., 9.], [4., 0.]])
masque = torch.tensor([[True, True], [True, False]])
somme = (erreurs * masque).sum()
compte = ...
perte = somme / compte
print(somme.item(), compte.item(), perte.item())''',
                 '''import torch
erreurs = torch.tensor([[1., 9.], [4., 0.]])
masque = torch.tensor([[True, True], [True, False]])
somme = (erreurs * masque).sum()
compte = masque.sum()
perte = somme / compte
assert compte.item() == 3
assert torch.allclose(perte, torch.tensor(14. / 3.))
print(somme.item(), compte.item(), perte.item())'''),
    ],
    "construire-un-module": [
        exercise("Conserver un état sans l’entraîner",
                 "Le décalage appartient au modèle mais n’est pas un paramètre appris. Complétons son enregistrement.",
                 '''from torch import nn
class Centree(nn.Module):
    def __init__(self):
        super().__init__()
        self....("reference", torch.tensor([1.]))
        self.linear = nn.Linear(1, 1, bias=False)
    def forward(self, x):
        return self.linear(x - self.reference)
model = Centree()
print(list(model.state_dict()))''',
                 '''import torch
from torch import nn
class Centree(nn.Module):
    def __init__(self):
        super().__init__()
        self.register_buffer("reference", torch.tensor([1.]))
        self.linear = nn.Linear(1, 1, bias=False)
    def forward(self, x):
        return self.linear(x - self.reference)
model = Centree()
assert "reference" in model.state_dict()
assert "reference" not in dict(model.named_parameters())
print(list(model.state_dict()))'''),
        exercise("Enregistrer plusieurs couches",
                 "Une collection de couches doit être connue du module. Complétons la collection et le parcours du calcul.",
                 '''from torch import nn
class Petit(nn.Module):
    def __init__(self):
        super().__init__()
        self.couches = nn....([nn.Linear(2, 3), nn.Linear(3, 1)])
    def forward(self, x):
        for couche in self.couches:
            x = ...
        return x
model = Petit()
print(tuple(model(torch.ones(4, 2)).shape))''',
                 '''import torch
from torch import nn
torch.manual_seed(17)
class Petit(nn.Module):
    def __init__(self):
        super().__init__()
        self.couches = nn.ModuleList([nn.Linear(2, 3), nn.Linear(3, 1)])
    def forward(self, x):
        for couche in self.couches:
            x = couche(x)
        return x
model = Petit()
sortie = model(torch.ones(4, 2))
assert tuple(sortie.shape) == (4, 1)
assert len(list(model.parameters())) == 4
print(tuple(sortie.shape))'''),
    ],
    "choisir-la-perte": [
        exercise("Une seule classe attendue",
                 "Choisissons la perte pour une classe exclusive. Elle reçoit les logits directement.",
                 '''logits = torch.tensor([[1., 0.]])
cible = torch.tensor([0], dtype=...)
perte = torch.nn....()(logits, cible)
print(perte.item())''',
                 '''import torch
logits = torch.tensor([[1., 0.]])
cible = torch.tensor([0], dtype=torch.long)
perte = torch.nn.CrossEntropyLoss()(logits, cible)
assert torch.isfinite(perte)
assert perte.ndim == 0
print(perte.item())'''),
        exercise("Deux présences indépendantes",
                 "Un extrait peut contenir voix et percussion simultanément. Complétons la perte cohérente avec ces deux cibles flottantes.",
                 '''logits = torch.zeros(1, 2)
presences = torch.tensor([[1., 1.]])
perte = torch.nn....()(logits, presences)
print(perte.item())''',
                 '''import math
import torch
logits = torch.zeros(1, 2)
presences = torch.tensor([[1., 1.]])
perte = torch.nn.BCEWithLogitsLoss()(logits, presences)
assert torch.allclose(perte, torch.tensor(math.log(2.)))
print(perte.item())'''),
    ],
    "autograd-et-derivees": [
        exercise("Lire la pente d’un carré",
                 "Complétons la création du poids et la demande de dérivation. Le calcul ne doit pas déplacer le poids.",
                 '''w = torch.tensor(1., requires_grad=...)
perte = (w - 3.) ** 2
perte....()
print(w.item(), w.grad.item())''',
                 '''import torch
w = torch.tensor(1., requires_grad=True)
perte = (w - 3.) ** 2
perte.backward()
assert w.item() == 1.
assert w.grad.item() == -4.
print(w.item(), w.grad.item())'''),
        exercise("Changer la fonction, garder la méthode",
                 "La fonction est maintenant un cube. Complétons la même demande de gradient et expliquons sa valeur.",
                 '''x = torch.tensor(2., requires_grad=True)
y = x ** 3
...
print(x.grad.item())''',
                 '''import torch
x = torch.tensor(2., requires_grad=True)
y = x ** 3
y.backward()
assert x.grad.item() == 12.
print(x.grad.item())'''),
    ],
    "une-iteration-entrainement": [
        exercise("Un pas dans le bon sens",
                 "Complétons l’ordre du calcul. Nous devons calculer le gradient avant de demander le déplacement.",
                 '''w = torch.tensor(2., requires_grad=True)
optim = torch.optim.SGD([w], lr=0.1)
optim....()
perte = 3 * w
perte....()
optim....()
print(w.item())''',
                 '''import torch
w = torch.tensor(2., requires_grad=True)
optim = torch.optim.SGD([w], lr=0.1)
optim.zero_grad()
perte = 3 * w
perte.backward()
optim.step()
assert torch.allclose(w.detach(), torch.tensor(1.7))
print(w.item())'''),
        exercise("Recommencer avec le nouveau poids",
                 "Complétons deux pas vers la cible zéro. Chaque passage doit repartir de gradients remis à zéro.",
                 '''w = torch.tensor(2., requires_grad=True)
optim = torch.optim.SGD([w], lr=0.1)
for _ in range(2):
    ...
    perte = w.square()
    ...
    ...
print(w.item())''',
                 '''import torch
w = torch.tensor(2., requires_grad=True)
optim = torch.optim.SGD([w], lr=0.1)
for _ in range(2):
    optim.zero_grad()
    perte = w.square()
    perte.backward()
    optim.step()
assert torch.allclose(w.detach(), torch.tensor(1.28), atol=1e-6)
print(w.item())'''),
    ],
    "entrainer-ou-evaluer": [
        exercise("Les deux interrupteurs de validation",
                 "Complétons le mode du modèle et le contexte de calcul. La couche linéaire garantit une nouvelle sortie.",
                 '''from torch import nn
model = nn.Sequential(nn.Dropout(.5), nn.Linear(2, 1, bias=False))
with torch.no_grad():
    model[1].weight.fill_(1.)
model....()
with torch....():
    sortie = model(torch.ones(1, 2))
print(sortie.tolist(), sortie.requires_grad)''',
                 '''import torch
from torch import nn
model = nn.Sequential(nn.Dropout(.5), nn.Linear(2, 1, bias=False))
with torch.no_grad():
    model[1].weight.fill_(1.)
model.eval()
with torch.no_grad():
    sortie = model(torch.ones(1, 2))
assert sortie.tolist() == [[2.]]
assert not sortie.requires_grad
print(sortie.tolist(), sortie.requires_grad)'''),
        exercise("Revenir au mode d’entraînement",
                 "Après la validation, rétablissons le mode d’entraînement avant les lots suivants.",
                 '''model = torch.nn.Sequential(torch.nn.Dropout(.5), torch.nn.Linear(2, 1))
model.eval()
model....()
print(model.training, model[0].training)''',
                 '''import torch
model = torch.nn.Sequential(torch.nn.Dropout(.5), torch.nn.Linear(2, 1))
model.eval()
model.train()
assert model.training and model[0].training
print(model.training, model[0].training)'''),
    ],
    "detacher-geler-journaliser": [
        exercise("Conserver une mesure scalaire",
                 "Nous voulons un nombre Python dans le journal, sans conserver le graphe de ce calcul.",
                 '''w = torch.tensor(1., requires_grad=True)
perte = (w - 2.).square()
mesure = perte....()
print(mesure, type(mesure).__name__)''',
                 '''import torch
w = torch.tensor(1., requires_grad=True)
perte = (w - 2.).square()
mesure = perte.item()
assert isinstance(mesure, float)
print(mesure, type(mesure).__name__)'''),
        exercise("Apprendre seulement la tête",
                 "Gelons l’encodeur avant le calcul. Nous vérifierons que la tête reçoit encore des gradients.",
                 '''encodeur = torch.nn.Linear(2, 2)
tete = torch.nn.Linear(2, 1)
for p in encodeur.parameters():
    p.requires_grad_(...)
perte = tete(encodeur(torch.tensor([[1., 2.]]))).square().mean()
perte.backward()
print([p.grad is None for p in encodeur.parameters()])''',
                 '''import torch
torch.manual_seed(17)
encodeur = torch.nn.Linear(2, 2)
tete = torch.nn.Linear(2, 1)
for p in encodeur.parameters():
    p.requires_grad_(False)
perte = tete(encodeur(torch.tensor([[1., 2.]]))).square().mean()
perte.backward()
assert all(p.grad is None for p in encodeur.parameters())
assert all(p.grad is not None for p in tete.parameters())
print([p.grad is None for p in encodeur.parameters()])'''),
    ],
    "moyennes-et-microbatches": [
        exercise("Pondérer une moyenne de moyennes",
                 "Les deux lots n’ont pas le même effectif. Complétons une moyenne qui compte chaque exemple une fois.",
                 '''lots = [(1., 3), (5., 1)]
somme = sum(... for moyenne, nombre in lots)
effectif = sum(nombre for _, nombre in lots)
resultat = somme / ...
print(resultat)''',
                 '''lots = [(1., 3), (5., 1)]
somme = sum(moyenne * nombre for moyenne, nombre in lots)
effectif = sum(nombre for _, nombre in lots)
resultat = somme / effectif
assert resultat == 2.
print(resultat)'''),
        exercise("Rassembler des réductions partielles",
                 "Vérifions le résultat global en comparant deux lots de tailles différentes à une réduction directe.",
                 '''erreurs = torch.tensor([1., 4., 9., 16., 25.])
lots = [erreurs[:3], erreurs[3:]]
coefficients = [len(lot) / ... for lot in lots]
globale = sum(coef * lot.mean() for coef, lot in zip(coefficients, lots))
print(globale.item())''',
                 '''import torch
erreurs = torch.tensor([1., 4., 9., 16., 25.])
lots = [erreurs[:3], erreurs[3:]]
coefficients = [len(lot) / len(erreurs) for lot in lots]
globale = sum(coef * lot.mean() for coef, lot in zip(coefficients, lots))
assert torch.allclose(globale, erreurs.mean())
print(globale.item())'''),
    ],
    "sauvegarder-et-reprendre": [
        exercise("Retrouver les mêmes prédictions",
                 "Sauvegardons les poids, puis chargeons-les dans un modèle de même architecture.",
                 '''import tempfile
from pathlib import Path
model = torch.nn.Linear(1, 1)
with tempfile.TemporaryDirectory() as dossier:
    fichier = Path(dossier) / "poids.pt"
    torch.save(..., fichier)
    copie = torch.nn.Linear(1, 1)
    copie.load_state_dict(torch.load(fichier, map_location="cpu", weights_only=True))
print(torch.equal(model(torch.ones(1, 1)), copie(torch.ones(1, 1))))''',
                 '''import tempfile
from pathlib import Path
import torch
torch.manual_seed(17)
model = torch.nn.Linear(1, 1)
with tempfile.TemporaryDirectory() as dossier:
    fichier = Path(dossier) / "poids.pt"
    torch.save(model.state_dict(), fichier)
    copie = torch.nn.Linear(1, 1)
    copie.load_state_dict(torch.load(fichier, map_location="cpu", weights_only=True))
identique = torch.equal(model(torch.ones(1, 1)), copie(torch.ones(1, 1)))
assert identique
print(identique)'''),
        exercise("Retrouver aussi l’état de l’optimiseur",
                 "Après un premier pas Adam, sauvegardons son état avec celui du modèle et le numéro d’époque.",
                 '''model = torch.nn.Linear(1, 1)
optim = torch.optim.Adam(model.parameters(), lr=.1)
optim.zero_grad()
model(torch.ones(1, 1)).square().mean().backward()
optim.step()
etat = {"model": ..., "optimizer": ..., "epoch": 1}
copie = torch.nn.Linear(1, 1)
nouvel_optim = torch.optim.Adam(copie.parameters(), lr=.1)
copie.load_state_dict(etat["model"])
nouvel_optim.load_state_dict(...)
print(len(nouvel_optim.state), etat["epoch"])''',
                 '''import torch
torch.manual_seed(17)
model = torch.nn.Linear(1, 1)
optim = torch.optim.Adam(model.parameters(), lr=.1)
optim.zero_grad()
model(torch.ones(1, 1)).square().mean().backward()
optim.step()
etat = {"model": model.state_dict(), "optimizer": optim.state_dict(), "epoch": 1}
copie = torch.nn.Linear(1, 1)
nouvel_optim = torch.optim.Adam(copie.parameters(), lr=.1)
copie.load_state_dict(etat["model"])
nouvel_optim.load_state_dict(etat["optimizer"])
assert len(nouvel_optim.state) == len(list(copie.parameters()))
assert torch.equal(model(torch.ones(1, 1)), copie(torch.ones(1, 1)))
print(len(nouvel_optim.state), etat["epoch"])'''),
    ],
}


def md(id_: str, text: str, **metadata):
    return dict(cell_type="markdown", id=id_, metadata=metadata, source=text.splitlines(keepends=True))


def code(id_: str, text: str, **metadata):
    return dict(cell_type="code", id=id_, metadata=metadata,
                source=text.splitlines(keepends=True), execution_count=None, outputs=[])


def make(chapter):
    id_ = chapter["id"]
    examples = [b["code"] for b in chapter["blocks"]
                if b.get("code") and b.get("language", "python") == "python"]
    assert examples, id_
    exercises = EXERCISES[id_]
    introduction = (
        f"# {chapter['title']}\n\n"
        f"{chapter['summary']}\n\n"
        "Nous exécutons les cellules dans l’ordre, sur **CPU**. "
        "Aucun téléchargement de données ou de modèle n’est nécessaire.\n\n"
        "Version de référence : **Python 3.11, PyTorch 2.10.0+cpu**. "
        "La cellule suivante indique la version réellement utilisée. "
        "Les sorties peuvent varier avec une autre version.\n\n"
        f"[Relire le chapitre](https://radiocodeur.github.io/quiz/cours.html?theme=pytorch#{id_}). "
        "Les deux exercices sont des textes à compléter : ils n’interrompent pas l’exécution intégrale. "
        "Leurs solutions restent repliées à la fin."
    )
    cells = [md("introduction", introduction),
             code("environnement", '''import platform
import torch

torch.set_num_threads(1)
torch.manual_seed(17)
print("Python", platform.python_version())
print("PyTorch", torch.__version__)
print("Calcul", "CPU", "— threads", torch.get_num_threads())''', tags=["setup"])]
    notions = "\n".join(f"- **{n['name']}** : {n['explanation']}" for n in chapter["notions"])
    cells.append(md("reperes", "## Nos repères\n\n" + notions))
    for i, example in enumerate(examples):
        cells.append(md(f"consigne-exemple-{i}",
                        "## Le calcul du cours\n\n"
                        "Avant de lancer cette cellule, annonçons les entrées et la sortie attendue. "
                        "Après l’exécution, expliquons les nombres et les formes affichés. "
                        "Le programme est identique à celui du chapitre."))
        cells.append(code(f"exemple-{i}", example, tags=["course-example"]))
    interview = next((b["text"] for b in reversed(chapter["blocks"])
                      if b.get("type") == "paragraph" and b.get("text", "").startswith("À dire en entretien :")), "")
    cells.append(md("oral", "## Nous vérifions notre compréhension\n\n" + interview))
    for i, item in enumerate(exercises, 1):
        cells.append(md(f"exercice-{i}",
                        f"## Exercice {i} — {item['title']}\n\n"
                        f"{item['prompt']}\n\n"
                        "Remplaçons les points de suspension. Nous pouvons copier ce texte dans une nouvelle cellule de code.\n\n"
                        f"```python\n{item['holes']}\n```", tags=["exercise"]))
    cells.append(md("solutions", "# Solutions\n\n"
                    "Nous cherchons d’abord, puis ouvrons la solution utile. "
                    "Chaque programme ci-dessous est autonome. "
                    "Le vérificateur du dépôt exécute également ces solutions, séparément des exercices à trous."))
    for i, item in enumerate(exercises, 1):
        solution_html = html.escape(item["solution"])
        cells.append(md(f"solution-{i}",
                        f"<details>\n<summary>Afficher la solution de l’exercice {i} — {html.escape(item['title'])}</summary>\n\n"
                        f"<pre><code>{solution_html}</code></pre>\n</details>", tags=["solution"],
                        jupyter={"source_hidden": True}))
    return dict(nbformat=4, nbformat_minor=5, cells=cells,
                metadata=dict(kernelspec=dict(display_name="Python 3", language="python", name="python3"),
                              language_info=dict(name="python", version="3.11"),
                              colab=dict(name=f"{id_}.ipynb", provenance=[]),
                              quiz=dict(chapterId=id_, themeId="pytorch", device="cpu",
                                        referenceVersions={"python": "3.11", "torch": "2.10.0+cpu"},
                                        courseCodeHashes=[hashlib.sha256(c.encode()).hexdigest() for c in examples],
                                        exerciseSolutions=[e["solution"] for e in exercises],
                                        generatedBy="scripts/make-notebooks-existing.py")))


def main():
    course = json.loads((ROOT / "public/courses/pytorch.json").read_text("utf-8"))
    chapters = [ch for ch in course["chapters"] if ch["id"] not in NEW_IDS]
    assert {ch["id"] for ch in chapters} == set(EXERCISES)
    output = ROOT / "public/notebooks"
    output.mkdir(parents=True, exist_ok=True)
    for chapter in chapters:
        notebook = make(chapter)
        (output / f"{chapter['id']}.ipynb").write_text(
            json.dumps(notebook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(chapters)} notebooks historiques générés, avec deux exercices et solutions chacun.")


if __name__ == "__main__":
    main()
