"""Build progressive notebooks from the current PyTorch course source.

Each complete top-level Python statement stays intact. Demonstration source is
preserved byte for byte across the cells named in metadata.quiz.programs.
Exercise cells intentionally remain incomplete and say so when run unchanged.
"""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def exercise(prompt,setup,var,answer,test,hint):
    return dict(prompt=prompt,setup=setup,var=var,answer=answer,test=test,hint=hint)

EXERCISES={
'pytorch-en-une-page':[
 exercise('Trois extraits possèdent chacun deux descripteurs. Prévoyez la forme, avant de lancer cette cellule.','exo_mesures = torch.tensor([[.1,1.5],[.2,4.5],[.15,2.5]])','exo_forme','(3, 2)','assert tuple(exo_forme) == tuple(exo_mesures.shape)','La première taille compte les lignes, la seconde les valeurs de chaque ligne.'),
 exercise('Combien d’exemples ce tableau représente-t-il ? Le nombre de valeurs stockées est une autre question.','exo_mesures = torch.tensor([[.1,1.5],[.2,4.5],[.15,2.5]])','exo_nombre','3','assert exo_nombre == exo_mesures.shape[0]','Chaque extrait correspond à une ligne entière, pas à une case.')],
'tenseur-forme-type-device':[
 exercise('Choisissez le dtype des indices de classes [0,1,0] pour CrossEntropyLoss dans son mode à indices.','exo_valeurs = [0,1,0]','exo_dtype','torch.long','exo_cibles = torch.tensor(exo_valeurs,dtype=exo_dtype)\nassert exo_cibles.dtype == torch.int64','long est un autre nom de int64. Cela ne signifie pas que toutes les cibles de toutes les tâches sont entières.'),
 exercise('Le calcul complet isfinite(...).all().item() renverra-t-il True ici ?','exo_x = torch.tensor([1.,float("nan"),2.])','exo_fini','False','assert exo_fini is torch.isfinite(exo_x).all().item()','isfinite teste chaque case ; all demande que toutes soient valides ; item extrait le booléen scalaire.')],
'du-pipeline-au-modele':[
 exercise('Prévoyez les indices de classes renvoyés par argmax sur les colonnes.','exo_scores = torch.tensor([[1.5,-1.5],[4.5,-4.5],[2.5,-2.5]])','exo_predictions','torch.tensor([0,0,0])','torch.testing.assert_close(torch.as_tensor(exo_predictions),exo_scores.argmax(dim=1))','Les trois lignes ont leur maximum en colonne 0. La taille du lot n’est pas le nombre de classes.'),
 exercise('Reliez chaque décision à sa cible : quelles lignes sont correctement classées ?','exo_predictions = torch.tensor([0,0,0])\nexo_cibles = torch.tensor([0,1,0])','exo_accords','torch.tensor([True,False,True])','assert torch.equal(torch.as_tensor(exo_accords),exo_predictions == exo_cibles)','Comparez les deux vecteurs position par position, en conservant l’ordre des extraits.')],
'construire-un-module':[
 exercise('Calculez le premier score d’une couche linéaire avec ces poids et ce biais.','exo_x = torch.tensor([.1,1.5])\nexo_w = torch.tensor([0.,1.])\nexo_b = torch.tensor(0.)','exo_score','1.5','assert abs(float(exo_score) - float((exo_x*exo_w).sum()+exo_b)) < 1e-6','Faites les deux produits, puis leur somme et enfin le biais.'),
 exercise('Nous changeons seulement le poids du premier descripteur, de 0 à 2. Quel score obtient-on ?','exo_x = torch.tensor([.1,1.5])\nexo_w = torch.tensor([2.,1.])','exo_score','1.7','assert abs(float(exo_score)-float((exo_x*exo_w).sum())) < 1e-6','Le nouveau terme vaut 0,1×2. La seconde contribution reste 1,5.')],
'choisir-la-perte':[
 exercise('Quelle ligne reçoit la plus grande perte individuelle : 0, 1 ou 2 ?','exo_scores = torch.tensor([[1.5,-1.5],[4.5,-4.5],[2.5,-2.5]])\nexo_cibles = torch.tensor([0,1,0])\nexo_pertes = torch.nn.CrossEntropyLoss(reduction="none")(exo_scores,exo_cibles)','exo_indice','1','assert exo_indice == exo_pertes.argmax().item()','La seconde ligne préfère fortement la classe voix alors que la cible demande percussion.'),
 exercise('Avec reduction="none", quelle est la forme de la sortie pour ces trois extraits ?','exo_scores = torch.zeros(3,2)\nexo_cibles = torch.tensor([0,1,0])','exo_forme','(3,)','assert tuple(exo_forme) == tuple(torch.nn.CrossEntropyLoss(reduction="none")(exo_scores,exo_cibles).shape)','Une perte par extrait reste disponible avant une éventuelle moyenne.')],
'pertes-multi-etiquettes':[
 exercise('Un seul extrait contient voix ET percussion. Écrivez sa cible multi-étiquettes flottante dans cet ordre.','exo_logits = torch.tensor([[.2,-.1]])','exo_cible','torch.tensor([[1.,1.]])','assert torch.as_tensor(exo_cible).dtype.is_floating_point\nassert torch.equal(torch.as_tensor(exo_cible),torch.ones_like(exo_logits))','Deux présences simultanées donnent deux 1, dans une ligne de forme (1,2).'),
 exercise('Ces deux probabilités sigmoïdes doivent-elles nécessairement sommer à un ? Répondez par True ou False.','exo_probabilites = torch.sigmoid(torch.tensor([[2.,2.]]))','exo_somme_un','False','assert exo_somme_un is bool(torch.isclose(exo_probabilites.sum(),torch.tensor(1.)).item())','Chaque présence est traitée séparément. La softmax répond à une autre convention.')],
'autograd-et-derivees':[
 exercise('Prévoyez le gradient de (w−2)² au point w=0.','exo_w = torch.tensor(0.,requires_grad=True)\nexo_perte = (exo_w-2.)**2\nexo_perte.backward()','exo_gradient','-4.','assert abs(float(exo_gradient)-exo_w.grad.item()) < 1e-6','La dérivée vaut 2×(w−2), évaluée au poids actuel.'),
 exercise('Deux backward successifs sur 3u puis 4u, sans remise à zéro : que contient u.grad ?','exo_u = torch.tensor(1.,requires_grad=True)\n(3*exo_u).backward()\n(4*exo_u).backward()','exo_gradient','7.','assert abs(float(exo_gradient)-exo_u.grad.item()) < 1e-6','Les contributions des deux graphes s’accumulent dans le même champ grad.')],
'retropropagation-a-la-main':[
 exercise('Complétez le gradient du premier poids dans le graphe x=2, w1=3, w2=−1.','exo_w1 = torch.tensor(3.,requires_grad=True)\nexo_w2 = torch.tensor(-1.,requires_grad=True)\nexo_h = exo_w1*2\nexo_y = exo_w2*exo_h\n(exo_y**2).backward()','exo_gradient','24.','assert abs(float(exo_gradient)-exo_w1.grad.item()) < 1e-6','Remontez −12 vers h avec le facteur −1, puis vers w1 avec le facteur 2.'),
 exercise('Complétez cette fois le gradient du second poids, avec le même calcul.','exo_w1 = torch.tensor(3.,requires_grad=True)\nexo_w2 = torch.tensor(-1.,requires_grad=True)\nexo_h = exo_w1*2\nexo_y = exo_w2*exo_h\n(exo_y**2).backward()','exo_gradient','-72.','assert abs(float(exo_gradient)-exo_w2.grad.item()) < 1e-6','La variation locale de y par rapport à w2 vaut h=6. Multipliez-la par −12.')],
'une-iteration-entrainement':[
 exercise('Après un pas SGD de taux 0,25 sur (w−2)², depuis w=0, quelle valeur prend w ?','exo_w = torch.tensor(0.,requires_grad=True)\nexo_optimiseur = torch.optim.SGD([exo_w],lr=.25)\n((exo_w-2.)**2).backward()\nexo_optimiseur.step()','exo_apres','1.','assert abs(float(exo_apres)-exo_w.item()) < 1e-6','SGD soustrait taux×gradient : le gradient initial est −4.'),
 exercise('En changeant seulement le taux à 0,5, quelle perte obtient-on après le pas ?','exo_w = torch.tensor(0.,requires_grad=True)\nexo_optimiseur = torch.optim.SGD([exo_w],lr=.5)\n((exo_w-2.)**2).backward()\nexo_optimiseur.step()','exo_perte_apres','0.','assert abs(float(exo_perte_apres)-((exo_w-2.)**2).item()) < 1e-6','Le poids arrive à 2 dans cette fonction quadratique particulière. Cela ne se généralise pas à tout réseau.')],
'premiere-boucle-minimale':[
 exercise('Diagnostiquez deux itérations sur w² sans zero_grad : quel poids final depuis w=1, avec lr=0,1 ?','exo_w = torch.tensor(1.,requires_grad=True)\nexo_opt = torch.optim.SGD([exo_w],lr=.1)\nfor _ in range(2):\n    (exo_w**2).backward()\n    exo_opt.step()','exo_poids','0.44','assert abs(float(exo_poids)-exo_w.item()) < 1e-6','Le premier gradient vaut 2. Le second, 1,6, s’ajoute au précédent.'),
 exercise('Nous remettons cette fois les gradients à zéro au début de chaque tour. Prévoyez le poids final.','exo_w = torch.tensor(1.,requires_grad=True)\nexo_opt = torch.optim.SGD([exo_w],lr=.1)\nfor _ in range(2):\n    exo_opt.zero_grad()\n    (exo_w**2).backward()\n    exo_opt.step()','exo_poids','0.64','assert abs(float(exo_poids)-exo_w.item()) < 1e-6','Le premier poids devient 0,8. Le second pas utilise seulement le gradient courant, 1,6.')],
'entrainer-ou-evaluer':[
 exercise('Un modèle est en eval, mais sans no_grad. Sa nouvelle sortie possède-t-elle requires_grad=True ?','exo_modele = torch.nn.Linear(1,1).eval()\nexo_sortie = exo_modele(torch.ones(1,1))','exo_gradient_actif','True','assert exo_gradient_actif is exo_sortie.requires_grad','eval change le comportement des modules concernés ; il ne désactive pas autograd.'),
 exercise('Dans no_grad, cette nouvelle opération conserve-t-elle un graphe de dérivées ?','exo_modele = torch.nn.Linear(1,1).eval()\nwith torch.no_grad():\n    exo_sortie = exo_modele(torch.ones(1,1))','exo_gradient_actif','False','assert exo_gradient_actif is exo_sortie.requires_grad','Nous regardons la sortie d’une opération nouvelle, pas un tenseur créé avant le contexte.')],
'organiser-les-axes':[
 exercise('Une grille 2×3 est reshaped en 3×2. Quelle valeur trouve-t-on à la coordonnée [1,0] ?','exo_x = torch.arange(6).reshape(2,3)\nexo_r = exo_x.reshape(3,2)','exo_valeur','2','assert exo_valeur == exo_r[1,0].item()','reshape conserve ici le parcours des cases 0,1,2,3,4,5.'),
 exercise('Même grille initiale, mais avec transpose(0,1). Que vaut maintenant [1,0] ?','exo_x = torch.arange(6).reshape(2,3)\nexo_t = exo_x.transpose(0,1)','exo_valeur','1','assert exo_valeur == exo_t[1,0].item()','La nouvelle case [1,0] correspond à l’ancienne case [0,1].')],
'ajouter-retirer-un-axe':[
 exercise('Ajoutez l’axe canal en position 1 à une entrée (3,2). Prévoyez la forme.','exo_x = torch.zeros(3,2)\nexo_canal = exo_x.unsqueeze(1)','exo_forme','(3,1,2)','assert tuple(exo_forme) == tuple(exo_canal.shape)','Les valeurs ne sont ni répétées ni mélangées. Un axe de taille un est inséré.'),
 exercise('Retirez uniquement cet axe canal de taille un. Quelle forme reste-t-il ?','exo_x = torch.zeros(3,1,2)\nexo_sans_canal = exo_x.squeeze(1)','exo_forme','(3,2)','assert tuple(exo_forme) == tuple(exo_sans_canal.shape)','squeeze(1) vise un axe nommé ; il ne retire pas les autres axes.')],
'concatener-ou-empiler':[
 exercise('Deux lots (3,2) sont concaténés sur dim=0. Quelle forme obtient-on ?','exo_a = torch.zeros(3,2)\nexo_b = torch.ones(3,2)','exo_forme','(6,2)','assert tuple(exo_forme) == tuple(torch.cat([exo_a,exo_b],dim=0).shape)','cat allonge un axe existant : 3+3 lignes.'),
 exercise('Les mêmes lots sont empilés avec stack(...,dim=0). Quelle forme obtient-on ?','exo_a = torch.zeros(3,2)\nexo_b = torch.ones(3,2)','exo_forme','(2,3,2)','assert tuple(exo_forme) == tuple(torch.stack([exo_a,exo_b],dim=0).shape)','stack crée un nouvel axe qui compte les deux tableaux fournis.')],
'selection-diffusion-reduction':[
 exercise('Choisissez dim pour obtenir une moyenne par ligne, soit [1,5 ; 3,5 ; 5,5].','exo_x = torch.tensor([[1.,2.],[3.,4.],[5.,6.]])','exo_dim','1','torch.testing.assert_close(exo_x.mean(dim=exo_dim),torch.tensor([1.5,3.5,5.5]))','Nous rassemblons les deux colonnes de chaque ligne ; les trois lignes restent distinctes.'),
 exercise('Prévoyez argmax(dim=0) sur cette grille.','exo_x = torch.tensor([[1.,2.],[3.,4.],[5.,6.]])','exo_indices','torch.tensor([2,2])','assert torch.equal(torch.as_tensor(exo_indices),exo_x.argmax(dim=0))','Chaque colonne compare ses trois lignes. Les deux maxima sont en ligne 2.')],
'broadcasting-pas-a-pas':[
 exercise('Calculez X−référence, avec une correction par colonne.','exo_x = torch.tensor([[1.,2.],[3.,4.],[5.,6.]])\nexo_reference = torch.tensor([1.,2.])','exo_resultat','torch.tensor([[0.,0.],[2.,2.],[4.,4.]])','torch.testing.assert_close(torch.as_tensor(exo_resultat),exo_x-exo_reference)','La référence de taille 2 est réutilisée sur les trois lignes.'),
 exercise('Cette fois, soustrayez une référence par ligne : 1, 3, puis 5. Écrivez le tableau de références.','exo_x = torch.tensor([[1.,2.],[3.,4.],[5.,6.]])','exo_reference','torch.tensor([[1.],[3.],[5.]])','assert tuple(exo_reference.shape) == (3,1)\ntorch.testing.assert_close(exo_x-exo_reference,torch.tensor([[0.,1.],[0.,1.],[0.,1.]]))','Il faut garder l’axe des colonnes avec une taille un : (3,1), et non (3,).')],
'filtrer-et-preserver-les-cibles':[
 exercise('Prévoyez le masque qui conserve les lignes dont la seconde colonne dépasse 3.','exo_x = torch.tensor([[1.,2.],[3.,4.],[5.,6.]])','exo_masque','torch.tensor([False,True,True])','assert torch.equal(torch.as_tensor(exo_masque),exo_x[:,1]>3)','Le test utilise la seconde valeur de chaque ligne, pas les numéros de lignes.'),
 exercise('Appliquez le même masque aux cibles. Quel vecteur accompagne les deux lignes retenues ?','exo_cibles = torch.tensor([0,1,0])\nexo_masque = torch.tensor([False,True,True])','exo_cibles_gardees','torch.tensor([1,0])','assert torch.equal(torch.as_tensor(exo_cibles_gardees),exo_cibles[exo_masque])','Les positions 1 et 2 gardent leurs annotations dans cet ordre.')],
'modules-et-buffers':[
 exercise('Un buffer moyenne est enregistré. Doit-il apparaître dans state_dict ?','exo_modele = torch.nn.Linear(2,2)\nexo_modele.register_buffer("moyenne",torch.zeros(2))','exo_sauvegarde','True','assert exo_sauvegarde is ("moyenne" in exo_modele.state_dict())','Le buffer fait partie de l’état conservé, même s’il n’est pas appris comme un poids.'),
 exercise('Ce buffer doit-il apparaître dans named_parameters ?','exo_modele = torch.nn.Linear(2,2)\nexo_modele.register_buffer("moyenne",torch.zeros(2))','exo_parametre','False','assert exo_parametre is ("moyenne" in dict(exo_modele.named_parameters()))','Un buffer enregistré est distinct d’un paramètre enregistré.')],
'dataset-et-batches':[
 exercise('Ce jeu contient trois paires. Combien d’exemples contient-il ?','exo_x = torch.tensor([[.1,1.5],[.2,4.5],[.15,2.5]])\nexo_y = torch.tensor([0,1,0])\nexo_dataset = torch.utils.data.TensorDataset(exo_x,exo_y)','exo_nombre','3','assert exo_nombre == len(exo_dataset)','Chaque paire mesures/cible compte pour un exemple. La largeur des mesures ne compte pas les exemples.'),
 exercise('Avec batch_size=2 et drop_last=False, quelle forme aura le dernier lot de mesures ?','exo_x = torch.zeros(3,2)\nexo_y = torch.tensor([0,1,0])\nexo_loader = torch.utils.data.DataLoader(torch.utils.data.TensorDataset(exo_x,exo_y),batch_size=2,shuffle=False)','exo_forme','(1,2)','assert tuple(exo_forme) == tuple(list(exo_loader)[-1][0].shape)','Après le premier lot de deux exemples, il reste un exemple avec ses deux caractéristiques.')],
'padding-et-collate':[
 exercise('Deux séquences contiennent deux positions puis une seule. Complétez leur masque de validité après padding.','exo_longueurs = torch.tensor([2,1])\nexo_positions = torch.arange(2)[None,:]','exo_masque','torch.tensor([[True,True],[True,False]])','assert torch.equal(torch.as_tensor(exo_masque),exo_positions<exo_longueurs[:,None])','La deuxième case du second extrait a été ajoutée pour le stockage.'),
 exercise('Une séquence [5] est stockée comme [5,9]. Le second nombre est du padding. Quelle moyenne pertinente conserve-t-on ?','exo_x = torch.tensor([5.,9.])\nexo_valide = torch.tensor([True,False])','exo_moyenne','5.','assert abs(float(exo_moyenne)-exo_x[exo_valide].mean().item()) < 1e-6','Le masque dépend de la longueur d’origine, pas de la valeur zéro.')],
'moyennes-masquees':[
 exercise('Calculez la moyenne de [2,4,0,0] quand seules les deux premières positions sont réelles.','exo_x = torch.tensor([2.,4.,0.,0.])\nexo_valide = torch.tensor([True,True,False,False])','exo_moyenne','3.','assert abs(float(exo_moyenne)-exo_x[exo_valide].mean().item()) < 1e-6','Le numérateur vaut 6 et le nombre d’observations vaut 2.'),
 exercise('Changez seulement les deux valeurs de padding en 9 et 20. Quel résumé masqué obtient-on ?','exo_x = torch.tensor([2.,4.,9.,20.])\nexo_valide = torch.tensor([True,True,False,False])','exo_moyenne','3.','assert abs(float(exo_moyenne)-exo_x[exo_valide].mean().item()) < 1e-6','Les positions invalides ne deviennent pas des observations lorsque leur valeur change.')],
'detacher-geler-journaliser':[
 exercise('Nous modifions la première case d’un tenseur détaché. Que vaut la première case de la source ?','exo_x = torch.tensor([1.,2.],requires_grad=True)\nexo_detache = exo_x.detach()\nexo_detache[0] = 9.','exo_source','9.','assert abs(float(exo_source)-exo_x[0].item()) < 1e-6','detach retire le lien au graphe, mais partage encore le stockage.'),
 exercise('Construisez cette fois une copie détachée indépendante avant de modifier sa première case.','exo_x = torch.tensor([1.,2.],requires_grad=True)','exo_copie','exo_x.detach().clone()','exo_copie[0]=9.\nassert exo_x[0].item() == 1.\nassert not exo_copie.requires_grad','Deux propriétés sont demandées : aucun lien au graphe et aucun stockage partagé.')],
'moyennes-et-microbatches':[
 exercise('Un lot de huit exemples a une perte moyenne de 1 ; le dernier de deux exemples, de 3. Quelle moyenne globale ?','exo_tailles = [8,2]\nexo_pertes = [1.,3.]','exo_moyenne','1.4','assert abs(float(exo_moyenne)-sum(n*p for n,p in zip(exo_tailles,exo_pertes))/sum(exo_tailles)) < 1e-6','Additionnez d’abord les contributions 8×1 et 2×3, puis divisez par dix exemples.'),
 exercise('Quel résultat erroné donnerait une moyenne simple des deux moyennes de lots ?','exo_pertes = [1.,3.]','exo_moyenne_naive','2.','assert abs(float(exo_moyenne_naive)-sum(exo_pertes)/len(exo_pertes)) < 1e-6','Ce calcul donne le même poids au petit lot et au grand lot. Expliquer l’erreur fait partie de l’exercice.')],
'sauvegarder-et-reprendre':[
 exercise('Après sauvegarde et rechargement de ce Linear, quelle sortie obtient-on pour x=1 ?','exo_modele = torch.nn.Linear(1,1)\nwith torch.no_grad():\n    exo_modele.weight.fill_(2.)\n    exo_modele.bias.fill_(1.)\ntorch.save(exo_modele.state_dict(),"exo-modele.pt")\nexo_recharge = torch.nn.Linear(1,1)\nexo_recharge.load_state_dict(torch.load("exo-modele.pt",weights_only=True))','exo_sortie','3.','assert abs(float(exo_sortie)-exo_recharge(torch.ones(1,1)).item()) < 1e-6','La sauvegarde garde ici poids et biais : 2×1+1.'),
 exercise('Un nouveau Linear sans chargement est-il nécessairement identique au modèle précédent ?','exo_a = torch.nn.Linear(1,1)\nexo_b = torch.nn.Linear(1,1)\nwith torch.no_grad():\n    exo_a.weight.fill_(2.)\n    exo_b.weight.fill_(0.)','exo_identique','False','assert exo_identique is torch.equal(exo_a.weight,exo_b.weight)','Créer la même architecture ne recopie pas ses paramètres. Les valeurs ont été explicitement rendues différentes ici.')],
'optimiseurs-regularisation-pratique':[
 exercise('AdamW reçoit un poids 1, un gradient nul, lr=0,1 et weight_decay=0,1. Quel poids suit le pas ?','exo_p = torch.nn.Parameter(torch.tensor(1.))\nexo_opt = torch.optim.AdamW([exo_p],lr=.1,weight_decay=.1)\nexo_p.grad = torch.zeros_like(exo_p)\nexo_opt.step()','exo_poids','0.99','assert abs(float(exo_poids)-exo_p.item()) < 1e-6','Avec un gradient nul explicite, la décroissance découplée applique ici le facteur 1−lr×weight_decay.'),
 exercise('SGD reçoit un poids 1, un gradient 2, lr=0,1 et weight_decay=0,1. Quel poids suit le pas ?','exo_p = torch.nn.Parameter(torch.tensor(1.))\nexo_opt = torch.optim.SGD([exo_p],lr=.1,weight_decay=.1)\nexo_p.grad = torch.tensor(2.)\nexo_opt.step()','exo_poids','0.79','assert abs(float(exo_poids)-exo_p.item()) < 1e-6','La contribution de décroissance vaut 0,1×1. Soustrayez 0,1×(2+0,1).')],
'scheduler-et-arret-anticipe':[
 exercise('ReduceLROnPlateau utilise factor=0,5 et patience=0. Après deux mesures identiques, quel taux reste-t-il ?','exo_p = torch.nn.Parameter(torch.tensor(1.))\nexo_opt = torch.optim.SGD([exo_p],lr=1.)\nexo_scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(exo_opt,factor=.5,patience=0)\nexo_scheduler.step(1.)\nexo_scheduler.step(1.)','exo_taux','0.5','assert abs(float(exo_taux)-exo_opt.param_groups[0]["lr"]) < 1e-6','La première mesure fixe la référence. La suivante ne l’améliore pas ; le taux est multiplié par le facteur.'),
 exercise('Un arrêt anticipé autorise deux validations sans amélioration. Faut-il arrêter après les valeurs 0,5 puis 0,6, avec meilleur=0,4 ?','exo_meilleur = .4\nexo_attente = 0\nfor exo_mesure in [.5,.6]:\n    if exo_mesure < exo_meilleur:\n        exo_meilleur,exo_attente=exo_mesure,0\n    else:\n        exo_attente+=1','exo_arreter','True','assert exo_arreter is (exo_attente >= 2)','Les deux validations dépassent la meilleure perte. L’arrêt est une règle de sélection, pas une mise à jour des poids.')],
'cuda-amp-memoire':[
 exercise('Dans ce notebook vérifié sur CPU, quel placement doit produire le choix avec fallback ?','exo_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")','exo_type','"cpu"','assert exo_type == exo_device.type','CUDA_VISIBLE_DEVICES est vide dans l’environnement du notebook. Nous n’inventons pas une exécution GPU.'),
 exercise('Combien d’octets logiques occupent vingt poids float32 ?','exo_poids = torch.zeros(5,4,dtype=torch.float32)','exo_octets','80','assert exo_octets == exo_poids.numel()*exo_poids.element_size()','Comptez les valeurs puis les quatre octets par valeur. Ce n’est pas la mémoire totale d’un entraînement.')],
'preparer-mel-pour-conv':[
 exercise('Combien de bins donne la partie non redondante d’une FFT réelle de taille 400 ?','exo_n_fft = 400','exo_bins','201','assert exo_bins == torch.fft.rfft(torch.zeros(exo_n_fft)).numel()','Les fréquences zéro et de Nyquist sont présentes pour cette taille paire : N//2+1.'),
 exercise('Un mel a la forme (2 extraits,64 bandes,96 trames). Ajoutez le canal mono attendu par Conv2d. Quelle forme ?','exo_mel = torch.zeros(2,64,96)','exo_forme','(2,1,64,96)','assert tuple(exo_forme) == tuple(exo_mel.unsqueeze(1).shape)','Le canal s’insère après les extraits. Les bandes restent un axe spatial de la représentation.')],
'convolution-a-la-main':[
 exercise('Calculez le premier résultat d’un noyau [[1,0],[0,−1]] appliqué à la grille 1 à 9.','exo_x = torch.arange(1.,10.).reshape(1,1,3,3)\nexo_noyau = torch.tensor([[[[1.,0.],[0.,-1.]]]])','exo_valeur','-4.','assert abs(float(exo_valeur)-torch.nn.functional.conv2d(exo_x,exo_noyau)[0,0,0,0].item()) < 1e-6','La première fenêtre est [[1,2],[4,5]]. Faites les quatre produits, puis leur somme.'),
 exercise('Avec le même noyau 2×2 et stride=2, quelle forme de sortie reste-t-il sur une entrée 3×3 ?','exo_x = torch.arange(1.,10.).reshape(1,1,3,3)\nexo_noyau = torch.ones(1,1,2,2)','exo_forme','(1,1,1,1)','assert tuple(exo_forme) == tuple(torch.nn.functional.conv2d(exo_x,exo_noyau,stride=2).shape)','Le premier placement couvre indices 0 et 1. Un nouveau départ à 2 dépasserait le bord sans padding.')],
'conv-mel-autoencodeur':[
 exercise('Conv2d(1,8,3,stride=2,padding=1) reçoit (2,1,64,96). Quelle forme produit-elle ?','exo_x = torch.zeros(2,1,64,96)\nexo_conv = torch.nn.Conv2d(1,8,3,stride=2,padding=1)','exo_forme','(2,8,32,48)','assert tuple(exo_forme) == tuple(exo_conv(exo_x).shape)','Le lot reste 2, les canaux deviennent 8, et les deux tailles spatiales sont divisées par deux ici.'),
 exercise('Une reconstruction [1,2] est comparée à une cible [0,0] par MSE moyenne. Quelle perte ?','exo_reconstruction = torch.tensor([1.,2.])\nexo_cible = torch.zeros(2)','exo_perte','2.5','assert abs(float(exo_perte)-torch.nn.functional.mse_loss(exo_reconstruction,exo_cible).item()) < 1e-6','La moyenne des erreurs au carré vaut (1+4)/2. Ce n’est pas la moyenne des valeurs.')],
'lire-erreurs-pytorch':[
 exercise('Après une transposition, choisissez la méthode qui peut aplatir ce tableau sans exiger sa contiguïté.','exo_x = torch.arange(6).reshape(2,3).transpose(0,1)','exo_methode','"reshape"','exo_resultat=getattr(exo_x,exo_methode)(-1)\nassert exo_resultat.tolist() == [0,3,1,4,2,5]','reshape peut copier si nécessaire ; view impose une compatibilité de strides.'),
 exercise('Corrigez le type d’indices de classe stockés par erreur en float32.','exo_cibles = torch.tensor([0.,1.],dtype=torch.float32)','exo_correction','exo_cibles.to(torch.long)','assert exo_correction.dtype == torch.int64\nassert exo_correction.tolist() == [0,1]','La conversion porte sur des indices déjà entiers dans leur sens. Une cible multi-étiquettes demanderait un autre contrat.')],
'boucle-entrainement-complete':[
 exercise('Assemblez les mesures des deux paires en une matrice : une ligne par extrait, trois coordonnées par ligne.','exo_exemples=[(torch.tensor([1.,2.,3.]),0),(torch.tensor([4.,5.,6.]),1)]','exo_entrees','torch.stack([exemple[0] for exemple in exo_exemples])','assert tuple(exo_entrees.shape) == (2,3)\nassert exo_entrees.tolist() == [[1,2,3],[4,5,6]]','Chaque paire contient un vecteur puis sa cible. stack ajoute l’axe des exemples.'),
 exercise('Construisez les indices de classe dans le même ordre, au format demandé par CrossEntropyLoss.','exo_exemples=[(torch.tensor([1.,2.,3.]),0),(torch.tensor([4.,5.,6.]),1)]','exo_cibles','torch.tensor([exemple[1] for exemple in exo_exemples],dtype=torch.long)','assert exo_cibles.dtype == torch.int64\nassert exo_cibles.tolist() == [0,1]','Le second élément de chaque paire est l’annotation. Ne triez pas les cibles séparément des mesures.')],
}

ENVIRONMENT='''import os
import sys
import tempfile

# Choisir un noyau neuf pour garantir la vérification sur CPU.
os.environ["CUDA_VISIBLE_DEVICES"] = ""
try:
    import torch
except ImportError as error:
    raise RuntimeError("PyTorch manque. Installer torch==2.10.0 dans ce noyau, puis redémarrer et relancer.") from error
torch.set_num_threads(1)
torch.manual_seed(17)
print("Python", sys.version.split()[0], "— PyTorch", torch.__version__, "— CPU")
assert not torch.cuda.is_available(), "Redémarrer dans un noyau CPU neuf."
_quiz_initial_directory = os.getcwd()
_quiz_temporary_directory = tempfile.TemporaryDirectory(prefix="quiz-progressif-")
os.chdir(_quiz_temporary_directory.name)
'''

OBSERVER='''# Cet outil sert uniquement à afficher les états des démonstrations.
# Il ne modifie pas les tenseurs et ne fait pas partie du modèle étudié.
def observer(nom, valeur):
    if isinstance(valeur, torch.Tensor):
        contenu = valeur.detach().cpu()
        print(nom, "forme", tuple(contenu.shape), "type", contenu.dtype,
              "requires_grad", valeur.requires_grad)
        if contenu.numel() <= 16:
            print("  valeurs :", contenu.tolist())
    elif valeur is None or isinstance(valeur, (int, float, bool, str, tuple)):
        print(nom, "=", valeur)
    elif isinstance(valeur, list) and len(valeur) <= 8:
        if all(isinstance(item,(int,float,bool,str)) for item in valeur):
            print(nom, "=", valeur)
        else:
            print(nom, ":",len(valeur),"éléments ; formes des tenseurs :",
                  [tuple(item.shape) for item in valeur if isinstance(item,torch.Tensor)])
    elif isinstance(valeur,dict):
        print(nom, ": clés",list(valeur)[:12])

def observer_entrainement(espace, montrer_poids=False):
    # Une copie évite de parcourir un dictionnaire global en mutation.
    vus = set()
    for nom, objet in list(espace.items()):
        if nom.startswith('_'):
            continue
        if isinstance(objet, torch.Tensor) and objet.is_leaf and objet.requires_grad:
            parametres = [(nom, objet)]
        elif isinstance(objet, torch.nn.Module):
            parametres = [(nom + '.' + cle, parametre)
                          for cle, parametre in list(objet.named_parameters())[:4]]
        else:
            continue
        for cle, parametre in parametres:
            if id(parametre) in vus:
                continue
            vus.add(id(parametre))
            if montrer_poids:
                observer(cle, parametre)
            observer(cle + '.grad', parametre.grad)
'''

def md(text,id,tags=None):return {'cell_type':'markdown','id':id,'metadata':{'tags':tags or []},'source':text}
def code_cell(text,id,tags=None,metadata=None):return {'cell_type':'code','id':id,'metadata':{'tags':tags or [],**(metadata or {})},'source':text,'execution_count':None,'outputs':[]}

def kind(node):
    text=ast.unparse(node)
    if isinstance(node,(ast.Import,ast.ImportFrom)):return 'imports'
    if isinstance(node,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)):return 'definition'
    if isinstance(node,(ast.For,ast.While)):return 'boucle'
    if '.backward('in text:return 'gradient'
    if '.zero_grad('in text:return 'remise-zero'
    if '.step('in text:return 'mise-jour'
    if text.startswith('print('):return 'sortie'
    if 'optim.'in text:return 'optimiseur'
    if any(word in text for word in ['CrossEntropyLoss','BCEWithLogitsLoss','MSELoss']):return 'critere'
    if 'manual_seed'in text or 'set_num_threads'in text:return 'reglages'
    if isinstance(node,ast.With):return 'contexte'
    return 'operation'

def assigned_names(node):
    names=[]
    targets=[]
    if isinstance(node,(ast.Assign,ast.AnnAssign)):
        targets=node.targets if isinstance(node,ast.Assign)else[node.target]
    for target in targets:
        for sub in ast.walk(target):
            if isinstance(sub,ast.Name)and sub.id not in names:names.append(sub.id)
    return names

def chunks(source,steps=None):
    """Split at complete AST statement boundaries, preserving every source byte."""
    tree=ast.parse(source)
    lines=source.splitlines(keepends=True)
    nodes=tree.body
    if not nodes:return []
    anchors=set()
    for item in steps or []:
        active=item.get('lines',[])
        if not active:continue
        anchor=min(active)
        containing=[i for i,node in enumerate(nodes)if node.lineno<=anchor<=getattr(node,'end_lineno',node.lineno)]
        following=[i for i,node in enumerate(nodes)if node.lineno>=anchor]
        if containing:anchors.add(containing[0])
        elif following:anchors.add(following[0])
    groups=[]
    start=0
    current=[]
    current_kind=None
    for index,node in enumerate(nodes):
        label=kind(node)
        # The course's explained ideas define the main boundaries. Imports and
        # short output sections are grouped; backward, zero_grad and step stay
        # separate. Definitions and control blocks always remain syntactically
        # complete, even when the walkthrough discusses their inner lines.
        atomic={'definition','boucle','gradient','remise-zero','mise-jour','contexte'}
        span=getattr(node,'end_lineno',node.lineno)-start
        merge=bool(current)and index not in anchors and label not in atomic and current_kind not in atomic
        if label in {'imports','sortie'} or current_kind in {'imports','sortie'}:
            merge=merge and label==current_kind
        if len(current)>=4 or span>7:merge=False
        if current and not merge:
            boundary=min([node.lineno,*[d.lineno for d in getattr(node,'decorator_list',[])]])-1
            groups.append({'source':''.join(lines[start:boundary]),'nodes':current,'kind':current_kind,'firstLine':start+1,'lastLine':boundary})
            start=boundary;current=[]
        current.append(node);current_kind=label
    groups.append({'source':''.join(lines[start:]),'nodes':current,'kind':current_kind,'firstLine':start+1,'lastLine':len(lines)})
    assert ''.join(group['source']for group in groups)==source
    for group in groups:compile(group['source'],'notebook-cell','exec')
    return groups

LABELS={'imports':'Préparer les bibliothèques','definition':'Définir la règle avant de l’utiliser','boucle':'Répéter la même étape sur les données','gradient':'Calculer les gradients','remise-zero':'Remettre les gradients à zéro','mise-jour':'Appliquer une mise à jour','sortie':'Lire les sorties','optimiseur':'Choisir les paramètres et leur mise à jour','critere':'Construire la règle de perte','reglages':'Fixer les conditions du petit calcul','contexte':'Appliquer le contexte explicite','operation':'Calculer l’état suivant'}

def exercise_source(spec,completed=False):
    value=spec['answer']if completed else '...  # Remplacer les points par votre réponse.'
    setup=spec['setup']+'\n'if spec['setup']else''
    guarded='\n'.join('    '+line for line in spec['test'].splitlines())
    return f'''{setup}{spec['var']} = {value}
if {spec['var']} is Ellipsis or {spec['var']} is None:
    print("À compléter : cet exercice n’est pas encore réalisé.")
else:
{guarded}
    print("Contrôle réussi pour la réponse fournie. Expliquez maintenant pourquoi.")
'''


def context_markdown(blocks):
    """Carry the chapter's explanations of values and axes into the notebook."""
    paragraphs=[]
    for block in blocks:
        kind=block.get('type')
        if kind=='heading':paragraphs.append('### '+block.get('text',block.get('title','')))
        elif kind in {'paragraph','callout'}:
            if block.get('text'):paragraphs.append(block['text'])
        elif kind=='visual':
            if block.get('kind')=='table' and block.get('columns'):
                rows=[block['columns'],['---']*len(block['columns']),*block.get('rows',[])]
                paragraphs.append('\n'.join('| '+' | '.join(str(value)for value in row)+' |'for row in rows))
            if block.get('caption'):paragraphs.append(block['caption'])
        elif kind=='list' and block.get('items'):
            if block.get('title'):paragraphs.append('### '+block['title'])
            paragraphs.append('\n'.join('- '+str(item)for item in block['items']))
    return '\n\n'.join(paragraphs)


def make(chapter):
    if chapter['id']not in EXERCISES:raise ValueError('Deux exercices à écrire pour '+chapter['id'])
    cells=[]
    title=chapter['title']
    cells.append(md(f'''# {title}

{chapter['summary']}

Nous lisons et exécutons les étapes dans l’ordre. Les cellules « Observer » montrent les valeurs et les formes ; elles ne prouvent pas la réussite des exercices.

Environnement vérifié : Python 3.11.9, PyTorch 2.10.0 CPU et TorchAudio 2.10.0 lorsque le chapitre le demande. Aucun modèle ni jeu de données n’est téléchargé pendant l’exécution.

[Revenir au chapitre](https://radiocodeur.github.io/quiz/cours.html?theme=pytorch#{chapter['id']}).
''','presentation'))
    cells.append(md('## Préparer le noyau\n\nChoisissez un environnement CPU neuf. En cas de bibliothèque manquante, installez-la dans ce noyau, puis redémarrez-le. Les sorties affichent les versions réellement utilisées.','environment-help'))
    cells.append(code_cell(ENVIRONMENT,'environment',['setup']))
    if any('torchaudio'in b.get('code','')for b in chapter['blocks']):
        cells.append(code_cell('try:\n    import torchaudio\nexcept (ImportError, OSError) as error:\n    raise RuntimeError("TorchAudio manque ou ne correspond pas à PyTorch. Installer torch==2.10.0 et torchaudio==2.10.0 ensemble, puis redémarrer.") from error\nprint("TorchAudio",torchaudio.__version__)','audio-environment',['setup']))
    cells.append(code_cell(OBSERVER,'observer-helper',['observation-helper'],{'jupyter':{'source_hidden':True}}))
    programs=[]
    relevant=[]
    for index,block in enumerate(chapter['blocks']):
        if block.get('code')and block.get('language','python')=='python':relevant.append((index,block))
    previous_block_index=-1
    for program_index,(block_index,block)in enumerate(relevant,1):
        prefix=f'p{program_index:02}'
        context=context_markdown(chapter['blocks'][previous_block_index+1:block_index])
        if context:cells.append(md(context,prefix+'-context'))
        previous_block_index=block_index
        cells.append(md(f"## Démonstration {program_index} · {block.get('title','Le programme du chapitre')}\n\n{block.get('goal',block.get('caption','Nous conservons les conventions de données et d’axes annoncées dans le chapitre.'))}",prefix+'-intro'))
        if block.get('codeMode')=='excerpt':
            cells.append(md('Ce programme annonce les prérequis suivants :\n\n'+'\n'.join('- '+item for item in block.get('requires',[])),prefix+'-requirements'))
        parts=chunks(block['code'],block.get('steps'))
        program={'blockIndex':block_index,'sourceSha256':hashlib.sha256(block['code'].encode()).hexdigest(),'cellIds':[]}
        program_names=[]
        for part_index,part in enumerate(parts,1):
            cell_id=f'{prefix}-c{part_index:02}'
            # Reuse the explanations that correspond to these exact lines.
            explanations=[]
            for item in block.get('steps',[]):
                active=item.get('lines',[])
                if active and part['firstLine']<=min(active)<=part['lastLine']:
                    explanations.append(item['text'])
                    for detail in item.get('details',[]):explanations.append(detail['explanation'])
            text='\n\n'.join(dict.fromkeys(explanations))
            heading=LABELS[part['kind']]
            if not text:
                if part['kind']=='definition':text='Cette cellule définit un objet ou une fonction. Son corps ne sera utilisé que lors d’un appel. Nous gardons la définition entière pour ne pas casser la syntaxe.'
                elif part['kind']=='boucle':text='Le corps indenté reste dans une seule cellule. Les opérations se répètent dans l’ordre écrit ; les sorties permettront de suivre leurs effets.'
                elif part['kind']=='sortie':text='Ces impressions lisent les objets calculés. Elles n’entraînent pas le modèle et ne modifient pas les tenseurs.'
                else:text='Exécutez cette petite partie après la précédente. Si un objet est créé, la cellule d’observation suivante permet d’en examiner l’état.'
            cells.append(md('### '+heading+'\n\n'+text,cell_id+'-help'))
            cells.append(code_cell(part['source'],cell_id,['demonstration'],{'quizProgram':program_index,'sourceLines':[part['firstLine'],part['lastLine']]}))
            program['cellIds'].append(cell_id)
            names=[]
            for node in part['nodes']:
                for name in assigned_names(node):
                    if name not in names and not name.startswith('_'):names.append(name)
                    if name not in program_names and not name.startswith('_'):program_names.append(name)
            # Long models, optimiser instances and criteria are not printed as
            # giant reprs. The helper displays only scalar/list/tensor states.
            names=[name for name in names if name not in {'modele','model','encodeur','encoder','decodeur','decoder','optimiseur','optimizer','critere','criterion','dataset','loader'}]
            if names:
                code='\n'.join(f'observer({name!r}, {name})'for name in names[:6])
                cells.append(code_cell(code,cell_id+'-observe',['observation']))
            if part['kind']in {'gradient','remise-zero','mise-jour'}:
                scope='{'+', '.join(repr(name)+': '+name for name in program_names)+'}'
                cells.append(code_cell('observer_entrainement('+scope+', montrer_poids='+str(part['kind']=='mise-jour')+')',cell_id+'-training-state',['observation']))
        programs.append(program)
        if block.get('result'):cells.append(md(block['result'],prefix+'-interpretation'))
    cells.append(md('## À vous de modifier le calcul\n\nLes deux cellules suivantes sont prêtes à éditer. Si vous les exécutez sans les compléter, elles le signalent et ne prétendent pas que vous avez réussi. Une réponse fausse déclenche le contrôle correspondant.','practice-intro'))
    solutions=[]
    for i,spec in enumerate(EXERCISES[chapter['id']],1):
        cells.append(md(f"### Exercice {i}\n\n{spec['prompt']}",f'exercise-{i}-prompt'))
        cells.append(code_cell(exercise_source(spec),f'exercise-{i}',['exercise'],{'exerciseIndex':i}))
        cells.append(md(f"<details>\n<summary>Indice pour l’exercice {i}</summary>\n\n{spec['hint']}\n\n</details>",f'exercise-{i}-hint',['hint']))
        solutions.append(exercise_source(spec,True))
    cells.append(md('## Comparer avec les solutions\n\nOuvrez-les après avoir formulé votre réponse et votre explication. Les solutions sont également exécutées par le vérificateur du dépôt.','solutions-intro'))
    for i,solution in enumerate(solutions,1):
        cells.append(md(f'<details>\n<summary>Solution de l’exercice {i}</summary>\n\n```python\n{solution}```\n\n</details>',f'exercise-{i}-solution',['solution']))
    cells.append(code_cell('os.chdir(_quiz_initial_directory)\n_quiz_temporary_directory.cleanup()','cleanup',['cleanup']))
    return {'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11.9'},'quiz':{'chapterId':chapter['id'],'themeId':'pytorch','programs':programs,'exerciseSolutions':solutions,'exerciseCount':2,'exerciseCellsReady':True,'demonstrationAndPracticeAreSeparate':True,'verifiedVersions':{'python':'3.11.9','torch':'2.10.0','torchaudio':'2.10.0'}}},'cells':cells}

def main():
    course=json.loads((ROOT/'public/courses/pytorch.json').read_text(encoding='utf-8'))
    destination=ROOT/'public/notebooks';destination.mkdir(exist_ok=True)
    expected=set()
    for chapter in course['chapters']:
        relative=chapter.get('notebook',f'notebooks/{chapter["id"]}.ipynb')
        assert relative==f'notebooks/{chapter["id"]}.ipynb'
        path=ROOT/'public'/relative
        expected.add(path.name)
        notebook=make(chapter)
        path.write_text(json.dumps(notebook,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
        print(chapter['id'],len(notebook['cells']),'cellules',len(notebook['metadata']['quiz']['programs']),'programmes')
    stale=[path.name for path in destination.glob('*.ipynb')if path.name not in expected]
    if stale:raise RuntimeError('Anciens notebooks à traiter explicitement : '+', '.join(stale))
    print('Created',len(expected),'progressive notebooks. Execute them before delivery.')

if __name__=='__main__':main()
