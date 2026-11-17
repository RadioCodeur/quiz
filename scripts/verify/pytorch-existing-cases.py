"""Executable CPU examples for the fourteen original PyTorch chapters.

The cases are also reused when producing the companion notebooks.
Nothing is downloaded and temporary checkpoints are removed automatically.
"""
from __future__ import annotations

CASES = {
"du-pipeline-au-modele": '''import torch
scores = torch.tensor([[1.5, -1.5], [4.5, -4.5]])
cibles = torch.tensor([0, 1], dtype=torch.long)
predictions = scores.argmax(dim=1)
print("scores", scores.tolist())
print("predictions", predictions.tolist())
print("accords", (predictions == cibles).tolist())''',
"tenseur-forme-type-device": '''import torch
X = torch.tensor([[1., 2., 3.], [2., 0., 1.]], dtype=torch.float32)
cibles = torch.tensor([0, 1], dtype=torch.long)
device = torch.device("cpu")
X, cibles = X.to(device), cibles.to(device)
print("forme", tuple(X.shape), "ligne", tuple(X[1].shape))
print("types", X.dtype, cibles.dtype)
print("placement", X.device, cibles.device)
print("valeurs_finies", torch.isfinite(X).all().item())''',
"organiser-les-axes": '''import torch
X = torch.tensor([[1., 2., 3.], [2., 0., 1.]])
r = X.reshape(3, 2)
t = X.transpose(0, 1)
signal = torch.tensor([[1., 2., 3.]])
canal = signal.unsqueeze(1)
print("reshape", r.tolist())
print("transpose", t.tolist())
print("canal", tuple(canal.shape), "retour", tuple(canal.squeeze(1).shape))
print("cat", tuple(torch.cat([canal, canal], dim=0).shape))
print("stack", tuple(torch.stack([canal, canal], dim=0).shape))
print("plat_transpose", t.reshape(-1).tolist())''',
"selection-diffusion-reduction": '''import torch
X = torch.tensor([[1., 2., 3.], [2., 0., 1.]])
reference = X.mean(dim=0, keepdim=True)
centres = X - reference
scores = torch.tensor([[1.5, -1.5], [4.5, -4.5]])
par_extrait = scores.argmax(dim=1)
par_classe = scores.argmax(dim=0)
retenus = X[X[:, 1] > 1]
print("reference", reference.tolist())
print("centres", centres.tolist())
print("par_extrait", par_extrait.tolist(), "par_classe", par_classe.tolist())
print("retenus", retenus.tolist())''',
"dataset-et-batches": '''import torch
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence

class Extraits(Dataset):
    def __init__(self):
        self.signaux = [torch.tensor([[0., 1., 2.], [2., 3., 4.]]),
                        torch.tensor([[2., 0., 1.]])]
        self.cibles = [0, 1]
    def __len__(self):
        return len(self.signaux)
    def __getitem__(self, indice):
        return self.signaux[indice], self.cibles[indice]

def assembler(exemples):
    signaux, cibles = zip(*exemples)
    longueurs = torch.tensor([len(x) for x in signaux])
    valeurs = pad_sequence(signaux, batch_first=True)
    masque = torch.arange(valeurs.shape[1])[None, :] < longueurs[:, None]
    return valeurs, torch.tensor(cibles), longueurs, masque

loader = DataLoader(Extraits(), batch_size=2, collate_fn=assembler,
                    shuffle=False, num_workers=0)
batch, cibles, longueurs, masque = next(iter(loader))
print("forme", tuple(batch.shape))
print("cibles", cibles.tolist(), "longueurs", longueurs.tolist())
print("masque", masque.tolist())''',
"moyennes-masquees": '''import torch
batch = torch.tensor([[[0., 1., 2.], [2., 3., 4.]],
                      [[2., 0., 1.], [0., 0., 0.]]])
masque = torch.tensor([[True, True], [True, False]])
m = masque.unsqueeze(-1)
X = (batch * m).sum(dim=1) / m.sum(dim=1)
somme_carres = (batch.square() * m).sum()
compte = masque.sum() * batch.shape[-1]
mse = somme_carres / compte
print("X", X.tolist())
print("somme", somme_carres.item(), "compte", compte.item())
print("mse", round(mse.item(), 6))''',
"construire-un-module": '''import torch
from torch import nn

class Classifieur(nn.Module):
    def __init__(self):
        super().__init__()
        self.couches = nn.ModuleList([nn.Linear(3, 2, bias=False)])
        self.register_buffer("moyenne", torch.zeros(3))
    def forward(self, x):
        return self.couches[0](x - self.moyenne)

model = Classifieur()
with torch.no_grad():
    model.couches[0].weight.copy_(torch.tensor([[2., -1., .5], [-2., 1., -.5]]))
X = torch.tensor([[1., 2., 3.], [2., 0., 1.]])
scores = model(X)
print("scores", scores.tolist())
print("parametres", sum(p.numel() for p in model.parameters()))
print("buffer", model.moyenne.tolist())
''',
"choisir-la-perte": '''import torch
logits = torch.zeros(1, 2)
classe = torch.tensor([0], dtype=torch.long)
ce = torch.nn.CrossEntropyLoss(reduction="none")(logits, classe)
etiquettes = torch.tensor([[1., 1.]])
bce = torch.nn.BCEWithLogitsLoss()(logits, etiquettes)
favorables = torch.tensor([[1., 0.]])
ce_favorable = torch.nn.CrossEntropyLoss()(favorables, classe)
print("probabilites", logits.softmax(dim=1).tolist())
print("ce", round(ce.item(), 6), "forme", tuple(ce.shape))
print("bce", round(bce.item(), 6))
print("ce_favorable", round(ce_favorable.item(), 6))''',
"autograd-et-derivees": '''import torch
w = torch.tensor(0., requires_grad=True)
loss = (w - 2.) ** 2
loss.backward()
print("perte", loss.item())
print("gradient", w.grad.item())
print("poids", w.item())''',
"une-iteration-entrainement": '''import torch
w = torch.tensor(2., requires_grad=True)
optimizer = torch.optim.SGD([w], lr=0.1)
optimizer.zero_grad()
loss = 3 * w
loss.backward()
gradient = w.grad.item()
optimizer.step()
print("perte_avant", loss.item())
print("gradient", gradient)
print("poids_apres", round(w.item(), 6))''',
"entrainer-ou-evaluer": '''import torch
from torch import nn
model = nn.Sequential(nn.Dropout(p=0.5), nn.Linear(2, 1, bias=False))
with torch.no_grad():
    model[1].weight.fill_(0.5)
x = torch.tensor([[2., 2.]])
model.eval()
with torch.no_grad():
    prediction = model(x)
print("prediction", prediction.tolist())
print("suivi", prediction.requires_grad)
print("mode_train", model.training)''',
"detacher-geler-journaliser": '''import torch
w = torch.tensor(1., requires_grad=True)
loss = (w - 2.) ** 2
journal = loss.item()
scores_journal = torch.stack([loss, 2 * loss]).detach()
print("journal", journal, type(journal).__name__)
print("tableau", scores_journal.tolist())
print("suivi", scores_journal.requires_grad)
encodeur = torch.nn.Linear(3, 2)
for parametre in encodeur.parameters():
    parametre.requires_grad_(False)
encodeur.eval()
print("encodeur_gele", all(not p.requires_grad for p in encodeur.parameters()))''',
"moyennes-et-microbatches": '''valeurs = [(2.0, 8), (5.0, 2)]
somme = sum(moyenne * effectif for moyenne, effectif in valeurs)
effectif = sum(n for _, n in valeurs)
moyenne = somme / effectif
coefficients = [n / effectif for _, n in valeurs]
print("somme", somme, "effectif", effectif)
print("moyenne", moyenne)
print("coefficients", coefficients)''',
"sauvegarder-et-reprendre": '''import tempfile
from pathlib import Path
import torch
torch.manual_seed(17)
model = torch.nn.Linear(1, 1, bias=False)
with torch.no_grad():
    model.weight.fill_(1.)
optimizer = torch.optim.Adam(model.parameters(), lr=0.1)
optimizer.zero_grad()
model(torch.ones(1, 1)).square().mean().backward()
optimizer.step()
with tempfile.TemporaryDirectory() as dossier:
    fichier = Path(dossier) / "reprise.pt"
    torch.save({"model": model.state_dict(), "optimizer": optimizer.state_dict(),
                "epoch": 1}, fichier)
    etat = torch.load(fichier, map_location="cpu", weights_only=True)
    copie = torch.nn.Linear(1, 1, bias=False)
    nouvel_optim = torch.optim.Adam(copie.parameters(), lr=0.1)
    copie.load_state_dict(etat["model"])
    nouvel_optim.load_state_dict(etat["optimizer"])
print("poids", round(copie.weight.item(), 6))
print("identique", torch.equal(model.weight, copie.weight))
print("etats_adam", len(nouvel_optim.state), "epoch", etat["epoch"])''',
}

def extra_checks(torch):
    """Verify the numerical and storage details moved into later callouts."""
    result = {}
    u = torch.tensor(2., requires_grad=True)
    (3*u).backward(); (4*u).backward()
    result['accumulated_gradient'] = u.grad.item()
    assert result['accumulated_gradient'] == 7
    w = torch.tensor(2., requires_grad=True)
    opt = torch.optim.SGD([w], lr=.1)
    (3*w).backward()
    torch.nn.utils.clip_grad_norm_([w], 1.)
    opt.step()
    result['clipped_weight'] = w.item()
    assert abs(result['clipped_weight']-1.9)<1e-6
    x = torch.tensor([1.,2.],requires_grad=True)
    y = x.detach(); y[0] = 9
    z = x.detach().clone(); z[0] = 0
    result['detach_original'] = x.tolist(); result['independent_copy'] = z.tolist()
    assert x.tolist()==[9.,2.] and z.tolist()==[0.,2.]
    dropout = torch.nn.Dropout(.5).eval()
    with torch.no_grad():
        identity = dropout(x)
        new_output = dropout(x)*1.
    result['dropout_identity_requires_grad']=identity.requires_grad
    result['new_output_requires_grad']=new_output.requires_grad
    assert identity.requires_grad and not new_output.requires_grad
    data = torch.ones(4,1); targets = torch.tensor([[1.],[2.],[3.],[4.]])
    full = torch.nn.Linear(1,1,bias=False)
    small = torch.nn.Linear(1,1,bias=False)
    with torch.no_grad():full.weight.zero_();small.weight.zero_()
    torch.nn.functional.mse_loss(full(data),targets).backward()
    for xi,yi in zip(data.split(1),targets.split(1)):
        (torch.nn.functional.mse_loss(small(xi),yi)/4).backward()
    result['full_gradient']=full.weight.grad.item()
    result['accumulated_micro_gradient']=small.weight.grad.item()
    assert torch.allclose(full.weight.grad,small.weight.grad)
    result['relu_values']=torch.relu(torch.tensor([-2.,0.,3.])).tolist()
    conv=torch.nn.Conv1d(1,8,5)
    result['conv1d_shape']=list(conv(torch.zeros(4,1,100)).shape)
    assert result['relu_values']==[0.,0.,3.] and result['conv1d_shape']==[4,8,96]
    result['loss_curve']=[[i,(i-2)**2] for i in range(5)]
    return result
