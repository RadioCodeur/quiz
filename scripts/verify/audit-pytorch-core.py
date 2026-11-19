"""Exact CPU programs for the rebuilt PyTorch foundations. Offline only."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import platform
import time

ROOT=Path(__file__).resolve().parents[2]
DATA='''X = torch.tensor([[0.1, 1.5], [0.2, 4.5], [0.15, 2.5]], dtype=torch.float32)
cibles = torch.tensor([0, 1, 0], dtype=torch.long)'''
MODEL='''modele = torch.nn.Linear(2, 2)
with torch.no_grad():
    modele.weight.copy_(torch.tensor([[0., 1.], [0., -1.]]))
    modele.bias.zero_()'''
CODES={
'pytorch-en-une-page':'''import torch
mesures = torch.tensor([[0.1, 1.5], [0.2, 4.5], [0.15, 2.5]])
print(tuple(mesures.shape))''',
'tenseur-forme-type-device':'''import torch
'''+DATA+'''
premier = X[0]
valeur = X[0, 1]
finies = torch.isfinite(X)
toutes_finies = finies.all()
controle = toutes_finies.item()
print("tableau", X.tolist(), "forme", tuple(X.shape))
print("ligne", premier.tolist(), "forme", tuple(premier.shape))
print("case", valeur.item(), "forme", tuple(valeur.shape))
print("types", X.dtype, cibles.dtype, "long=int64", torch.long == torch.int64)
print("finies", finies.tolist(), "forme", tuple(finies.shape))
print("tout", toutes_finies.item(), "forme", tuple(toutes_finies.shape))
print("controle", controle, "Python", type(controle).__name__, "device", X.device)''',
'du-pipeline-au-modele':'''import torch
# Scores choisis à la main ; colonnes : voix 0, percussion 1.
scores = torch.tensor([[1.5, -1.5], [4.5, -4.5], [2.5, -2.5]])
cibles = torch.tensor([0, 1, 0], dtype=torch.long)
predictions = scores.argmax(dim=1)
accords = predictions == cibles
print("scores", scores.tolist(), "forme", tuple(scores.shape))
print("predictions", predictions.tolist(), "forme", tuple(predictions.shape))
print("accords", accords.tolist())
scores_modifies = scores.clone()
scores_modifies[1, 1] = 5.0
print("apres modification", scores_modifies.argmax(dim=1).tolist())
print("original", scores.tolist())''',
'construire-un-module':'''import torch
from torch import nn

class Classifieur(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(2, 2)

    def forward(self, entrees):
        return self.linear(entrees)

'''+DATA+'''
modele = Classifieur()
with torch.no_grad():
    modele.linear.weight.copy_(torch.tensor([[0., 1.], [0., -1.]]))
    modele.linear.bias.zero_()
scores = modele(X)
produits = X[0] * modele.linear.weight[0]
score_manuel = produits.sum() + modele.linear.bias[0]
print("poids", modele.linear.weight.tolist(), "forme", tuple(modele.linear.weight.shape))
print("produits voix A", produits.tolist(), "somme", score_manuel.item())
print("scores", scores.tolist(), "forme", tuple(scores.shape))
print("parametres", [(nom, tuple(p.shape)) for nom, p in modele.named_parameters()])''',
'construire-un-module/relu':'''import torch
x = torch.tensor([-2., 0., 3.])
y = torch.relu(x)
print("entree", x.tolist(), "sortie", y.tolist())''',
'choisir-la-perte':'''import torch
'''+DATA+'\n'+MODEL+'''
scores = modele(X)
critere = torch.nn.CrossEntropyLoss(reduction="none")
pertes = critere(scores, cibles)
perte = pertes.mean()
probabilites = scores.softmax(dim=1)
print("probabilites", [[round(v, 6) for v in ligne] for ligne in probabilites.tolist()])
print("pertes", [round(v, 6) for v in pertes.tolist()], "forme", tuple(pertes.shape))
print("moyenne", round(perte.item(), 6), "forme", tuple(perte.shape))
nouveaux_scores = torch.tensor(scores.tolist())
nouveaux_scores[1, 1] = 5.
print("perte B corrigee", round(critere(nouveaux_scores, cibles)[1].item(), 6))''',
'pertes-multi-etiquettes':'''import torch
scores = torch.tensor([[0., 0.]])
presences = torch.tensor([[1., 1.]], dtype=torch.float32)
critere = torch.nn.BCEWithLogitsLoss(reduction="none")
par_etiquette = critere(scores, presences)
print("presences", presences.tolist(), "type", presences.dtype)
print("probabilites", scores.sigmoid().tolist())
print("pertes", [[round(v, 6) for v in ligne] for ligne in par_etiquette.tolist()])
print("moyenne", round(par_etiquette.mean().item(), 6))''',
'autograd-et-derivees':'''import torch
w = torch.tensor(0., requires_grad=True)
perte = (w - 2.) ** 2
perte.backward()
print("poids", w.item(), "perte", perte.item(), "gradient", w.grad.item())
avant = (0. - 2.) ** 2
apres = (0.01 - 2.) ** 2
pente_approchee = (apres - avant) / 0.01
print("petite variation", round(apres, 4), "pente approchee", round(pente_approchee, 2))
u = torch.tensor(1., requires_grad=True)
(3 * u).backward()
print("premier gradient", u.grad.item())
(4 * u).backward()
print("gradient cumule", u.grad.item())''',
'retropropagation-a-la-main':'''import torch
x = torch.tensor(2.)
w1 = torch.tensor(3., requires_grad=True)
w2 = torch.tensor(-1., requires_grad=True)
h = w1 * x
h.retain_grad()
y = w2 * h
y.retain_grad()
perte = (y - 0) ** 2
perte.backward()
print("h, y, perte", h.item(), y.item(), perte.item())
print("gradients intermediaires", y.grad.item(), h.grad.item())
print("gradients poids", w1.grad.item(), w2.grad.item())''',
'une-iteration-entrainement':'''import torch
w = torch.tensor(0., requires_grad=True)
optimiseur = torch.optim.SGD([w], lr=0.1)
optimiseur.zero_grad()
perte = (w - 2.) ** 2
perte.backward()
gradient_avant = w.grad.item()
poids_avant = w.item()
optimiseur.step()
nouvelle_perte = (w - 2.) ** 2
print("avant", poids_avant, perte.item(), "gradient", gradient_avant)
print("apres", round(w.item(), 6), round(nouvelle_perte.item(), 6))
# Même pente initiale, mais un taux trop grand.
taux_trop_grand = 1.1
autre_poids = poids_avant - taux_trop_grand * gradient_avant
print("grand pas", round(autre_poids, 6), "perte", round((autre_poids - 2.) ** 2, 6))''',
'premiere-boucle-minimale':'''import torch
torch.set_num_threads(1)
torch.manual_seed(7)
'''+DATA+'\n'+MODEL+'''
critere = torch.nn.CrossEntropyLoss()
optimiseur = torch.optim.SGD(modele.parameters(), lr=0.1)
historique = []
for epoque in range(201):
    optimiseur.zero_grad()
    scores = modele(X)
    perte = critere(scores, cibles)
    perte.backward()
    optimiseur.step()
    historique.append(perte.item())
    if epoque in [0, 50, 200]:
        print("epoque", epoque, "perte avant pas", round(perte.item(), 6))
with torch.no_grad():
    scores_finaux = modele(X)
    predictions = scores_finaux.argmax(dim=1)
    perte_finale = critere(scores_finaux, cibles)
print("decisions finales", predictions.tolist())
print("cibles", cibles.tolist(), "perte finale", round(perte_finale.item(), 6))''',
'entrainer-ou-evaluer':'''import torch
from torch import nn
modele = nn.Sequential(nn.Dropout(p=0.5), nn.Linear(2, 1, bias=False))
with torch.no_grad():
    modele[1].weight.fill_(0.5)
x = torch.tensor([[2., 2.]])
for entrainement in [True, False]:
    for gradients in [True, False]:
        torch.manual_seed(7)
        modele.train(entrainement)
        with torch.set_grad_enabled(gradients):
            prediction = modele(x)
        print("train", entrainement, "grad_actifs", gradients,
              "prediction", prediction.tolist(), "suivi", prediction.requires_grad)
modele.eval()
with torch.no_grad():
    inference = modele(x)
print("inference", inference.tolist())''',
'organiser-les-axes':'''import torch
# Expérience indépendante : identifiants de cases, pas mesures audio.
X = torch.tensor([[1, 2, 3], [4, 5, 6]])
redecoupe = X.reshape(3, 2)
transpose = X.transpose(0, 1)
print("original", X.tolist(), "forme", tuple(X.shape))
print("reshape", redecoupe.tolist(), "forme", tuple(redecoupe.shape))
print("transpose", transpose.tolist(), "forme", tuple(transpose.shape))
mel = torch.arange(24).reshape(2, 3, 4)
mel_permute = mel.permute(0, 2, 1)
print("axes exemple", tuple(mel.shape), "vers", tuple(mel_permute.shape))
print("case conservee", mel[1, 2, 3].item(), mel_permute[1, 3, 2].item())''',
'ajouter-retirer-un-axe':'''import torch
signal = torch.tensor([[1., 2., 3.]])
avec_canal = signal.unsqueeze(1)
retour = avec_canal.squeeze(1)
tout_retire = avec_canal.squeeze()
print("signal", signal.tolist(), tuple(signal.shape))
print("canal", avec_canal.tolist(), tuple(avec_canal.shape))
print("squeeze(1)", retour.tolist(), tuple(retour.shape))
print("squeeze()", tout_retire.tolist(), tuple(tout_retire.shape))
print("None equivalent", torch.equal(signal[:, None, :], avec_canal))''',
'concatener-ou-empiler':'''import torch
a = torch.tensor([[1., 2., 3.]])
b = torch.tensor([[4., 5., 6.]])
nouveaux_extraits = torch.cat([a, b], dim=0)
nouveau_groupe = torch.stack([a, b], dim=0)
print("cat", nouveaux_extraits.tolist(), tuple(nouveaux_extraits.shape))
print("stack", nouveau_groupe.tolist(), tuple(nouveau_groupe.shape))
print("source", a.tolist(), b.tolist())''',
'selection-diffusion-reduction':'''import torch
# Indices de cases distincts : trois extraits, deux mesures.
X = torch.tensor([[1., 2.], [3., 4.], [5., 6.]])
par_mesure = X.mean(dim=0)
par_extrait = X.mean(dim=1)
reference = X.mean(dim=0, keepdim=True)
print("dim0", par_mesure.tolist(), tuple(par_mesure.shape))
print("dim1", par_extrait.tolist(), tuple(par_extrait.shape))
print("keepdim", reference.tolist(), tuple(reference.shape))
scores = torch.tensor([[1.5, -1.5], [4.5, -4.5], [2.5, -2.5]])
print("classe par extrait", scores.argmax(dim=1).tolist())
print("extrait par classe", scores.argmax(dim=0).tolist())''',
'broadcasting-pas-a-pas':'''import torch
X = torch.tensor([[1., 2.], [3., 4.], [5., 6.]])
reference = torch.tensor([[3., 4.]])
centres = X - reference
reference_explicitement = reference.expand_as(X)
print("reference", reference.tolist(), tuple(reference.shape))
print("alignee", reference_explicitement.tolist(), tuple(reference_explicitement.shape))
print("centres", centres.tolist(), tuple(centres.shape))
print("sources inchangees", X.tolist(), reference.tolist())''',
'filtrer-et-preserver-les-cibles':'''import torch
X = torch.tensor([[0.1, 1.5], [0.2, 4.5], [0.15, 2.5]])
cibles = torch.tensor([0, 1, 0], dtype=torch.long)
cretes = X[:, 1]
masque = cretes > 2.0
retenus = X[masque]
cibles_retenues = cibles[masque]
print("cretes", cretes.tolist(), tuple(cretes.shape))
print("masque", masque.tolist(), tuple(masque.shape))
print("retenus", retenus.tolist(), tuple(retenus.shape))
print("cibles correspondantes", cibles_retenues.tolist())''',
'modules-et-buffers':'''import torch
from torch import nn

class ProjectionCentree(nn.Module):
    def __init__(self):
        super().__init__()
        self.couches = nn.ModuleList([nn.Linear(2, 2, bias=False)])
        self.register_buffer("moyenne", torch.tensor([0.1, 1.5]))

    def forward(self, x):
        centre = x - self.moyenne
        for couche in self.couches:
            centre = couche(centre)
        return centre

modele = ProjectionCentree()
with torch.no_grad():
    modele.couches[0].weight.copy_(torch.eye(2))
x = torch.tensor([[0.2, 4.5]])
print("sortie", modele(x).tolist())
print("parametres", [nom for nom, _ in modele.named_parameters()])
print("buffers", [nom for nom, _ in modele.named_buffers()])
print("sauvegarde", list(modele.state_dict()))''',
}

def execute():
    import torch
    torch.set_num_threads(1)
    report={'python':platform.python_version(),'torch':torch.__version__,'device':'cpu','examples':[]}
    for name,code in CODES.items():
        torch.manual_seed(7)
        namespace={}
        output=io.StringIO()
        started=time.perf_counter()
        with contextlib.redirect_stdout(output):exec(compile(code,name,'exec'),namespace)
        values={}
        for key,value in namespace.items():
            if isinstance(value,torch.Tensor):values[key]={'values':value.detach().cpu().tolist(),'shape':list(value.shape),'dtype':str(value.dtype),'requires_grad':value.requires_grad}
        if name=='premiere-boucle-minimale':assert namespace['predictions'].tolist()==[0,1,0] and namespace['perte_finale'].item()<namespace['historique'][0]
        if name=='retropropagation-a-la-main':assert namespace['w1'].grad.item()==24 and namespace['w2'].grad.item()==-72
        report['examples'].append({'id':name,'sha256':hashlib.sha256(code.encode()).hexdigest(),'stdout':output.getvalue(),'seconds':round(time.perf_counter()-started,6),'values':values})
    path=ROOT/'scripts/verify/audit-pytorch-core-results.json'
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({entry['id']:entry['stdout'] for entry in report['examples']},ensure_ascii=False,indent=2))
if __name__=='__main__':execute()
