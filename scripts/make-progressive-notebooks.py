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

EXERCISES = {'tenseur-forme-type-device': [{'prompt': 'Choisissez le dtype des indices de classes [0,1,0] pour '
                                          'CrossEntropyLoss dans son mode à indices.',
                                'setup': 'exo_valeurs = [0,1,0]',
                                'var': 'exo_dtype',
                                'answer': 'torch.long',
                                'test': 'exo_cibles = torch.tensor(exo_valeurs,dtype=exo_dtype)\n'
                                        'assert exo_cibles.dtype == torch.int64',
                                'hint': 'long est un autre nom de int64. Les présences multi-étiquettes demandent '
                                        'un autre contrat.'},
                               {'prompt': 'Trois extraits ont deux descripteurs chacun. Quelle forme reste-t-il '
                                          'en sélectionnant seulement la première ligne ?',
                                'setup': 'exo_x = torch.tensor([[.1,1.5],[.2,4.5],[.15,2.5]])',
                                'var': 'exo_forme',
                                'answer': '(2,)',
                                'test': 'assert tuple(exo_forme) == tuple(exo_x[0].shape)',
                                'hint': 'Sélectionner une ligne retire l’axe des extraits ; il reste le vecteur '
                                        'de ses deux mesures.'}],
 'du-pipeline-au-modele': [{'prompt': 'Prévoyez les indices de classes renvoyés par argmax sur les colonnes.',
                            'setup': 'exo_scores = torch.tensor([[1.5,-1.5],[4.5,-4.5],[2.5,-2.5]])',
                            'var': 'exo_predictions',
                            'answer': 'torch.tensor([0,0,0])',
                            'test': 'torch.testing.assert_close(torch.as_tensor(exo_predictions),exo_scores.argmax(dim=1))',
                            'hint': 'Les trois lignes ont leur maximum en colonne 0. La taille du lot n’est pas '
                                    'le nombre de classes.'},
                           {'prompt': 'Reliez chaque décision à sa cible : quelles lignes sont correctement '
                                      'classées ?',
                            'setup': 'exo_predictions = torch.tensor([0,0,0])\nexo_cibles = torch.tensor([0,1,0])',
                            'var': 'exo_accords',
                            'answer': 'torch.tensor([True,False,True])',
                            'test': 'assert torch.equal(torch.as_tensor(exo_accords),exo_predictions == '
                                    'exo_cibles)',
                            'hint': 'Comparez les deux vecteurs position par position, en conservant l’ordre des '
                                    'extraits.'}],
 'construire-un-module': [{'prompt': 'Calculez le premier score d’une couche linéaire avec ces poids et ce biais.',
                           'setup': 'exo_x = torch.tensor([.1,1.5])\n'
                                    'exo_w = torch.tensor([0.,1.])\n'
                                    'exo_b = torch.tensor(0.)',
                           'var': 'exo_score',
                           'answer': '1.5',
                           'test': 'assert abs(float(exo_score) - float((exo_x*exo_w).sum()+exo_b)) < 1e-6',
                           'hint': 'Faites les deux produits, puis leur somme et enfin le biais.'},
                          {'prompt': 'Gardez les mêmes poids [0,1], mais fixez le biais à 0,5. Quel est le '
                                     'nouveau score pour [.1,1.5] ?',
                           'setup': 'exo_x=torch.tensor([.1,1.5])\n'
                                    'exo_w=torch.tensor([0.,1.])\n'
                                    'exo_b=torch.tensor(.5)',
                           'var': 'exo_score',
                           'answer': '2.',
                           'test': 'assert abs(float(exo_score)-((exo_x*exo_w).sum()+exo_b).item()) < 1e-6',
                           'hint': 'Le biais ajoute ici 0,5 au score déjà calculé. Il ne multiplie pas les '
                                   'mesures.'}],
 'choisir-la-perte': [{'prompt': 'Quelle ligne reçoit la plus grande perte individuelle : 0, 1 ou 2 ?',
                       'setup': 'exo_scores = torch.tensor([[1.5,-1.5],[4.5,-4.5],[2.5,-2.5]])\n'
                                'exo_cibles = torch.tensor([0,1,0])\n'
                                'exo_pertes = torch.nn.CrossEntropyLoss(reduction="none")(exo_scores,exo_cibles)',
                       'var': 'exo_indice',
                       'answer': '1',
                       'test': 'assert exo_indice == exo_pertes.argmax().item()',
                       'hint': 'La seconde ligne préfère fortement la classe voix alors que la cible demande '
                               'percussion.'},
                      {'prompt': 'Avec reduction="none", quelle est la forme de la sortie pour ces trois extraits '
                                 '?',
                       'setup': 'exo_scores = torch.zeros(3,2)\nexo_cibles = torch.tensor([0,1,0])',
                       'var': 'exo_forme',
                       'answer': '(3,)',
                       'test': 'assert tuple(exo_forme) == '
                               'tuple(torch.nn.CrossEntropyLoss(reduction="none")(exo_scores,exo_cibles).shape)',
                       'hint': 'Une perte par extrait reste disponible avant une éventuelle moyenne.'}],
 'autograd-et-derivees': [{'prompt': 'Prévoyez le gradient de (w−2)² au point w=0.',
                           'setup': 'exo_w = torch.tensor(0.,requires_grad=True)\n'
                                    'exo_perte = (exo_w-2.)**2\n'
                                    'exo_perte.backward()',
                           'var': 'exo_gradient',
                           'answer': '-4.',
                           'test': 'assert abs(float(exo_gradient)-exo_w.grad.item()) < 1e-6',
                           'hint': 'La dérivée vaut 2×(w−2), évaluée au poids actuel.'},
                          {'prompt': 'Deux backward successifs sur 3u puis 4u, sans remise à zéro : que contient '
                                     'u.grad ?',
                           'setup': 'exo_u = torch.tensor(1.,requires_grad=True)\n'
                                    '(3*exo_u).backward()\n'
                                    '(4*exo_u).backward()',
                           'var': 'exo_gradient',
                           'answer': '7.',
                           'test': 'assert abs(float(exo_gradient)-exo_u.grad.item()) < 1e-6',
                           'hint': 'Les contributions des deux graphes s’accumulent dans le même champ grad.'}],
 'premiere-boucle-minimale': [{'prompt': 'Diagnostiquez deux itérations sur w² sans zero_grad : quel poids final '
                                         'depuis w=1, avec lr=0,1 ?',
                               'setup': 'exo_w = torch.tensor(1.,requires_grad=True)\n'
                                        'exo_opt = torch.optim.SGD([exo_w],lr=.1)\n'
                                        'for _ in range(2):\n'
                                        '    (exo_w**2).backward()\n'
                                        '    exo_opt.step()',
                               'var': 'exo_poids',
                               'answer': '0.44',
                               'test': 'assert abs(float(exo_poids)-exo_w.item()) < 1e-6',
                               'hint': 'Le premier gradient vaut 2. Le second, 1,6, s’ajoute au précédent.'},
                              {'prompt': 'Nous remettons cette fois les gradients à zéro au début de chaque tour. '
                                         'Prévoyez le poids final.',
                               'setup': 'exo_w = torch.tensor(1.,requires_grad=True)\n'
                                        'exo_opt = torch.optim.SGD([exo_w],lr=.1)\n'
                                        'for _ in range(2):\n'
                                        '    exo_opt.zero_grad()\n'
                                        '    (exo_w**2).backward()\n'
                                        '    exo_opt.step()',
                               'var': 'exo_poids',
                               'answer': '0.64',
                               'test': 'assert abs(float(exo_poids)-exo_w.item()) < 1e-6',
                               'hint': 'Le premier poids devient 0,8. Le second pas utilise seulement le gradient '
                                       'courant, 1,6.'}],
 'entrainer-ou-evaluer': [{'prompt': 'Un modèle est en eval, mais sans no_grad. Sa nouvelle sortie possède-t-elle '
                                     'requires_grad=True ?',
                           'setup': 'exo_modele = torch.nn.Linear(1,1).eval()\n'
                                    'exo_sortie = exo_modele(torch.ones(1,1))',
                           'var': 'exo_gradient_actif',
                           'answer': 'True',
                           'test': 'assert exo_gradient_actif is exo_sortie.requires_grad',
                           'hint': 'eval change le comportement des modules concernés ; il ne désactive pas '
                                   'autograd.'},
                          {'prompt': 'Dans no_grad, cette nouvelle opération conserve-t-elle un graphe de '
                                     'dérivées ?',
                           'setup': 'exo_modele = torch.nn.Linear(1,1).eval()\n'
                                    'with torch.no_grad():\n'
                                    '    exo_sortie = exo_modele(torch.ones(1,1))',
                           'var': 'exo_gradient_actif',
                           'answer': 'False',
                           'test': 'assert exo_gradient_actif is exo_sortie.requires_grad',
                           'hint': 'Nous regardons la sortie d’une opération nouvelle, pas un tenseur créé avant '
                                   'le contexte.'}],
 'dataset-et-batches': [{'prompt': 'Ce jeu contient trois paires. Combien d’exemples contient-il ?',
                         'setup': 'exo_x = torch.tensor([[.1,1.5],[.2,4.5],[.15,2.5]])\n'
                                  'exo_y = torch.tensor([0,1,0])\n'
                                  'exo_dataset = torch.utils.data.TensorDataset(exo_x,exo_y)',
                         'var': 'exo_nombre',
                         'answer': '3',
                         'test': 'assert exo_nombre == len(exo_dataset)',
                         'hint': 'Chaque paire mesures/cible compte pour un exemple. La largeur des mesures ne '
                                 'compte pas les exemples.'},
                        {'prompt': 'Avec batch_size=2 et drop_last=False, quelle forme aura le dernier lot de '
                                   'mesures ?',
                         'setup': 'exo_x = torch.zeros(3,2)\n'
                                  'exo_y = torch.tensor([0,1,0])\n'
                                  'exo_loader = '
                                  'torch.utils.data.DataLoader(torch.utils.data.TensorDataset(exo_x,exo_y),batch_size=2,shuffle=False)',
                         'var': 'exo_forme',
                         'answer': '(1,2)',
                         'test': 'assert tuple(exo_forme) == tuple(list(exo_loader)[-1][0].shape)',
                         'hint': 'Après le premier lot de deux exemples, il reste un exemple avec ses deux '
                                 'caractéristiques.'}],
 'selection-diffusion-reduction': [{'prompt': 'Centrez chaque descripteur en retirant sa moyenne sur les trois '
                                              'extraits. Gardez un axe de taille un dans la référence.',
                                    'setup': 'exo_x = torch.tensor([[.1,1.5],[.2,4.5],[.15,2.5]])',
                                    'var': 'exo_reference',
                                    'answer': 'exo_x.mean(dim=0,keepdim=True)',
                                    'test': 'assert tuple(exo_reference.shape) == (1,2)\n'
                                            'exo_centre=exo_x-exo_reference\n'
                                            'torch.testing.assert_close(exo_centre.mean(dim=0),torch.zeros(2),atol=1e-6,rtol=0)',
                                    'hint': 'Réduire l’axe 0 rassemble les extraits séparément pour chaque '
                                            'colonne. La référence se rediffuse sur les lignes.'},
                                   {'prompt': 'Conservez les lignes dont la crête dépasse 2. Quelles cibles '
                                              'accompagnent les mesures dans le même ordre ?',
                                    'setup': 'exo_x = torch.tensor([[.1,1.5],[.2,4.5],[.15,2.5]])\n'
                                             'exo_cibles = torch.tensor([0,1,0])\n'
                                             'exo_masque = exo_x[:,1] > 2',
                                    'var': 'exo_cibles_gardees',
                                    'answer': 'exo_cibles[exo_masque]',
                                    'test': 'assert torch.equal(exo_cibles_gardees,torch.tensor([1,0]))\n'
                                            'assert len(exo_cibles_gardees) == len(exo_x[exo_masque])',
                                    'hint': 'Appliquez le même masque aux lignes et à leurs annotations.'}],
 'organiser-les-axes': [{'prompt': 'Avec la grille [[1,2,3],[4,5,6]], comparez la case [1,0] après reshape(3,2), '
                                   'puis après transpose(0,1). Donnez les deux valeurs dans cet ordre.',
                         'setup': 'exo_x = torch.arange(1,7).reshape(2,3)\n'
                                  'exo_r = exo_x.reshape(3,2)\n'
                                  'exo_t = exo_x.transpose(0,1)',
                         'var': 'exo_valeurs',
                         'answer': '(3,2)',
                         'test': 'assert tuple(exo_valeurs) == (exo_r[1,0].item(),exo_t[1,0].item())',
                         'hint': 'reshape conserve le parcours 1 à 6 ; transpose échange le rôle des axes. Une '
                                 'forme identique ne garantit pas le même contenu.'},
                        {'prompt': 'Ajoutez un axe canal en position 1 à cette grille 2×3, sans répéter ses '
                                   'valeurs.',
                         'setup': 'exo_x = torch.arange(1,7).reshape(2,3)',
                         'var': 'exo_avec_canal',
                         'answer': 'exo_x.unsqueeze(1)',
                         'test': 'assert tuple(exo_avec_canal.shape) == (2,1,3)\n'
                                 'assert torch.equal(exo_avec_canal.squeeze(1),exo_x)',
                         'hint': 'unsqueeze insère un axe de taille un ; squeeze(1) vérifie ensuite la '
                                 'conservation des valeurs.'}],
 'padding-et-collate': [{'prompt': 'A contient [2,4] et B [6], stockés après padding comme [[2,4],[6,0]]. Écrivez '
                                   'les deux moyennes qui ne comptent que les trames valides.',
                         'setup': 'exo_batch = torch.tensor([[[2.],[4.]],[[6.],[0.]]])\n'
                                  'exo_masque = torch.tensor([[True,True],[True,False]])\n'
                                  'exo_validite = exo_masque.unsqueeze(-1)',
                         'var': 'exo_moyennes',
                         'answer': '(exo_batch*exo_validite).sum(dim=1)/exo_validite.sum(dim=1)',
                         'test': 'torch.testing.assert_close(exo_moyennes,torch.tensor([[3.],[6.]]))',
                         'hint': 'La somme vaut six dans chaque extrait, mais les comptes sont deux et un. Gardez '
                                 'l’axe des mesures.'},
                        {'prompt': 'Chaque trame valide porte maintenant D=2 descripteurs. Quel dénominateur '
                                   'utiliser pour la MSE par valeur vers zéro ?',
                         'setup': 'exo_batch = torch.tensor([[[2.,20.],[4.,40.]],[[6.,60.],[0.,0.]]])\n'
                                  'exo_masque = torch.tensor([[True,True],[True,False]])',
                         'var': 'exo_denominateur',
                         'answer': 'exo_masque.sum()*exo_batch.shape[-1]',
                         'test': 'assert int(exo_denominateur) == 6\n'
                                 'exo_mse=(exo_batch.square()*exo_masque.unsqueeze(-1)).sum()/exo_denominateur\n'
                                 'torch.testing.assert_close(exo_mse,torch.tensor(5656/6))',
                         'hint': 'Trois trames sont réelles, chacune avec deux erreurs carrées. Comptez les '
                                 'valeurs, pas seulement les trames.'}],
 'boucle-entrainement-complete': [{'prompt': 'Les poids connus ont pour lignes [0,1] et [0,−1], avec biais nul. '
                                             'Prévoyez les trois décisions sur X, avant apprentissage.',
                                   'setup': 'exo_x=torch.tensor([[.1,1.5],[.2,4.5],[.15,2.5]])\n'
                                            'exo_modele=torch.nn.Linear(2,2)\n'
                                            'with torch.no_grad():\n'
                                            '    exo_modele.weight.copy_(torch.tensor([[0.,1.],[0.,-1.]]))\n'
                                            '    exo_modele.bias.zero_()',
                                   'var': 'exo_decisions',
                                   'answer': 'torch.tensor([0,0,0])',
                                   'test': 'assert torch.equal(exo_decisions,exo_modele(exo_x).argmax(dim=1))',
                                   'hint': 'Le premier score reste positif pour les trois lignes ; cela n’en fait '
                                           'pas les trois bonnes classes.'},
                                  {'prompt': 'Rechargez l’état du classifieur sauvegardé, puis calculez ses '
                                             'scores sur ces deux descripteurs.',
                                   'setup': 'exo_modele=torch.nn.Linear(2,2)\n'
                                            'with torch.no_grad():\n'
                                            '    exo_modele.weight.copy_(torch.tensor([[0.,1.],[0.,-1.]]))\n'
                                            '    exo_modele.bias.zero_()\n'
                                            'exo_x=torch.tensor([[.2,4.5]])\n'
                                            'torch.save(exo_modele.state_dict(),"exo-classifieur.pt")\n'
                                            'exo_copie=torch.nn.Linear(2,2)\n'
                                            'exo_etat=torch.load("exo-classifieur.pt",map_location="cpu",weights_only=True)\n'
                                            'exo_copie.load_state_dict(exo_etat)\n'
                                            'exo_copie.eval()',
                                   'var': 'exo_scores',
                                   'answer': 'exo_copie(exo_x)',
                                   'test': 'torch.testing.assert_close(exo_scores,torch.tensor([[4.5,-4.5]]))\n'
                                           'assert torch.equal(exo_scores,exo_modele(exo_x))',
                                   'hint': 'Même architecture, état chargé, puis nouvelle passe. Charger des '
                                           'poids ne lance ni entraînement ni prédiction.'}],
 'convolution-a-la-main': [{'prompt': 'Calculez le premier résultat d’un noyau [[1,0],[0,−1]] appliqué à la '
                                      'grille 1 à 9.',
                            'setup': 'exo_x = torch.arange(1.,10.).reshape(1,1,3,3)\n'
                                     'exo_noyau = torch.tensor([[[[1.,0.],[0.,-1.]]]])',
                            'var': 'exo_valeur',
                            'answer': '-4.',
                            'test': 'assert '
                                    'abs(float(exo_valeur)-torch.nn.functional.conv2d(exo_x,exo_noyau)[0,0,0,0].item()) '
                                    '< 1e-6',
                            'hint': 'La première fenêtre est [[1,2],[4,5]]. Faites les quatre produits, puis leur '
                                    'somme.'},
                           {'prompt': 'Avec le même noyau 2×2 et stride=2, quelle forme de sortie reste-t-il sur '
                                      'une entrée 3×3 ?',
                            'setup': 'exo_x = torch.arange(1.,10.).reshape(1,1,3,3)\n'
                                     'exo_noyau = torch.ones(1,1,2,2)',
                            'var': 'exo_forme',
                            'answer': '(1,1,1,1)',
                            'test': 'assert tuple(exo_forme) == '
                                    'tuple(torch.nn.functional.conv2d(exo_x,exo_noyau,stride=2).shape)',
                            'hint': 'Le premier placement couvre indices 0 et 1. Un nouveau départ à 2 '
                                    'dépasserait le bord sans padding.'}],
 'conv-mel-autoencodeur': [{'prompt': 'Conv2d(1,4,3,stride=2,padding=1) reçoit une carte préparée (2,1,64,96). '
                                      'Quelle forme produit-elle ?',
                            'setup': 'exo_x=torch.zeros(2,1,64,96)\n'
                                     'exo_conv=torch.nn.Conv2d(1,4,3,stride=2,padding=1)',
                            'var': 'exo_forme',
                            'answer': '(2,4,32,48)',
                            'test': 'assert tuple(exo_forme) == tuple(exo_conv(exo_x).shape)',
                            'hint': 'Le lot reste deux, les canaux deviennent quatre et les deux axes spatiaux '
                                    'sont divisés par deux ici.'},
                           {'prompt': 'Une cible logarithmique contient les valeurs choisies [−0,8 ; −0,2]. '
                                      'Quelle MSE minimale donne une sortie forcée à zéro par ReLU ?',
                            'setup': 'exo_cible=torch.tensor([-.8,-.2])\nexo_sortie=torch.nn.ReLU()(exo_cible)',
                            'var': 'exo_perte',
                            'answer': '0.34',
                            'test': 'torch.testing.assert_close(torch.as_tensor(exo_perte),torch.nn.functional.mse_loss(exo_sortie,exo_cible))',
                            'hint': 'Le meilleur nombre autorisé par ReLU pour chaque cible négative est zéro. '
                                    'Faites la moyenne de 0,8² et 0,2².'}],
 'retropropagation-a-la-main': [{'prompt': 'Complétez le gradient du premier poids dans le graphe x=2, w1=3, '
                                           'w2=−1.',
                                 'setup': 'exo_w1 = torch.tensor(3.,requires_grad=True)\n'
                                          'exo_w2 = torch.tensor(-1.,requires_grad=True)\n'
                                          'exo_h = exo_w1*2\n'
                                          'exo_y = exo_w2*exo_h\n'
                                          '(exo_y**2).backward()',
                                 'var': 'exo_gradient',
                                 'answer': '24.',
                                 'test': 'assert abs(float(exo_gradient)-exo_w1.grad.item()) < 1e-6',
                                 'hint': 'Remontez −12 vers h avec le facteur −1, puis vers w1 avec le facteur '
                                         '2.'},
                                {'prompt': 'Complétez cette fois le gradient du second poids, avec le même '
                                           'calcul.',
                                 'setup': 'exo_w1 = torch.tensor(3.,requires_grad=True)\n'
                                          'exo_w2 = torch.tensor(-1.,requires_grad=True)\n'
                                          'exo_h = exo_w1*2\n'
                                          'exo_y = exo_w2*exo_h\n'
                                          '(exo_y**2).backward()',
                                 'var': 'exo_gradient',
                                 'answer': '-72.',
                                 'test': 'assert abs(float(exo_gradient)-exo_w2.grad.item()) < 1e-6',
                                 'hint': 'La variation locale de y par rapport à w2 vaut h=6. Multipliez-la par '
                                         '−12.'}],
 'optimiseurs-regularisation-pratique': [{'prompt': 'AdamW reçoit un poids 1, un gradient nul, lr=0,1 et '
                                                    'weight_decay=0,1. Quel poids suit le pas ?',
                                          'setup': 'exo_p = torch.nn.Parameter(torch.tensor(1.))\n'
                                                   'exo_opt = torch.optim.AdamW([exo_p],lr=.1,weight_decay=.1)\n'
                                                   'exo_p.grad = torch.zeros_like(exo_p)\n'
                                                   'exo_opt.step()',
                                          'var': 'exo_poids',
                                          'answer': '0.99',
                                          'test': 'assert abs(float(exo_poids)-exo_p.item()) < 1e-6',
                                          'hint': 'Avec un gradient nul explicite, la décroissance découplée '
                                                  'applique ici le facteur 1−lr×weight_decay.'},
                                         {'prompt': 'SGD reçoit un poids 1, un gradient 2, lr=0,1 et '
                                                    'weight_decay=0,1. Quel poids suit le pas ?',
                                          'setup': 'exo_p = torch.nn.Parameter(torch.tensor(1.))\n'
                                                   'exo_opt = torch.optim.SGD([exo_p],lr=.1,weight_decay=.1)\n'
                                                   'exo_p.grad = torch.tensor(2.)\n'
                                                   'exo_opt.step()',
                                          'var': 'exo_poids',
                                          'answer': '0.79',
                                          'test': 'assert abs(float(exo_poids)-exo_p.item()) < 1e-6',
                                          'hint': 'La contribution de décroissance vaut 0,1×1. Soustrayez '
                                                  '0,1×(2+0,1).'}],
 'detacher-geler-journaliser': [{'prompt': 'Nous modifions la première case d’un tenseur détaché. Que vaut la '
                                           'première case de la source ?',
                                 'setup': 'exo_x = torch.tensor([1.,2.],requires_grad=True)\n'
                                          'exo_detache = exo_x.detach()\n'
                                          'exo_detache[0] = 9.',
                                 'var': 'exo_source',
                                 'answer': '9.',
                                 'test': 'assert abs(float(exo_source)-exo_x[0].item()) < 1e-6',
                                 'hint': 'detach retire le lien au graphe, mais partage encore le stockage.'},
                                {'prompt': 'Construisez cette fois une copie détachée indépendante avant de '
                                           'modifier sa première case.',
                                 'setup': 'exo_x = torch.tensor([1.,2.],requires_grad=True)',
                                 'var': 'exo_copie',
                                 'answer': 'exo_x.detach().clone()',
                                 'test': 'exo_copie[0]=9.\n'
                                         'assert exo_x[0].item() == 1.\n'
                                         'assert not exo_copie.requires_grad',
                                 'hint': 'Deux propriétés sont demandées : aucun lien au graphe et aucun stockage '
                                         'partagé.'}],
 'pertes-multi-etiquettes': [{'prompt': 'Un seul extrait contient voix ET percussion. Écrivez sa cible '
                                        'multi-étiquettes flottante dans cet ordre.',
                              'setup': 'exo_logits = torch.tensor([[.2,-.1]])',
                              'var': 'exo_cible',
                              'answer': 'torch.tensor([[1.,1.]])',
                              'test': 'assert torch.as_tensor(exo_cible).dtype.is_floating_point\n'
                                      'assert torch.equal(torch.as_tensor(exo_cible),torch.ones_like(exo_logits))',
                              'hint': 'Deux présences simultanées donnent deux 1, dans une ligne de forme (1,2).'},
                             {'prompt': 'Ces deux probabilités sigmoïdes doivent-elles nécessairement sommer à un '
                                        '? Répondez par True ou False.',
                              'setup': 'exo_probabilites = torch.sigmoid(torch.tensor([[2.,2.]]))',
                              'var': 'exo_somme_un',
                              'answer': 'False',
                              'test': 'assert exo_somme_un is '
                                      'bool(torch.isclose(exo_probabilites.sum(),torch.tensor(1.)).item())',
                              'hint': 'Chaque présence est traitée séparément. La softmax répond à une autre '
                                      'convention.'}],
 'modules-et-buffers': [{'prompt': 'Un buffer moyenne est enregistré. Prévoyez sa présence dans state_dict, puis '
                                   'dans named_parameters, avec deux booléens.',
                         'setup': 'exo_modele = torch.nn.Linear(2,2)\n'
                                  'exo_modele.register_buffer("moyenne",torch.zeros(2))',
                         'var': 'exo_presences',
                         'answer': '(True,False)',
                         'test': 'assert tuple(exo_presences) == ("moyenne" in exo_modele.state_dict(),"moyenne" '
                                 'in dict(exo_modele.named_parameters()))',
                         'hint': 'Le buffer persistant est sauvegardé et déplacé avec le modèle, mais reste hors '
                                 'des paramètres ajustables.'},
                        {'prompt': 'Après un pas Adam, fournissez l’état à recharger dans le nouvel optimiseur. '
                                   'Les poids du modèle sont déjà copiés.',
                         'setup': 'exo_modele = torch.nn.Linear(2,2)\n'
                                  'exo_opt = torch.optim.Adam(exo_modele.parameters(),lr=.01)\n'
                                  'exo_perte = exo_modele(torch.ones(1,2)).square().mean()\n'
                                  'exo_perte.backward()\n'
                                  'exo_opt.step()\n'
                                  'exo_copie = torch.nn.Linear(2,2)\n'
                                  'exo_copie.load_state_dict(exo_modele.state_dict())\n'
                                  'exo_opt_copie = torch.optim.Adam(exo_copie.parameters(),lr=.01)',
                         'var': 'exo_etat_optim',
                         'answer': 'exo_opt.state_dict()',
                         'test': 'exo_opt_copie.load_state_dict(exo_etat_optim)\n'
                                 'assert len(exo_opt_copie.state) == 2\n'
                                 'for exo_a,exo_b in zip(exo_opt.state.values(),exo_opt_copie.state.values()):\n'
                                 '    assert exo_b["step"].item() == 1\n'
                                 '    assert torch.equal(exo_a["exp_avg"],exo_b["exp_avg"])\n'
                                 '    assert torch.equal(exo_a["exp_avg_sq"],exo_b["exp_avg_sq"])',
                         'hint': 'Les moments et compteurs appartiennent à optimizer.state_dict(), pas au dernier '
                                 'nombre de perte.'}],
 'moyennes-et-microbatches': [{'prompt': 'Un lot de huit exemples a une perte moyenne de 1 ; le dernier de deux '
                                         'exemples, de 3. Quelle moyenne globale ?',
                               'setup': 'exo_tailles = [8,2]\nexo_pertes = [1.,3.]',
                               'var': 'exo_moyenne',
                               'answer': '1.4',
                               'test': 'assert abs(float(exo_moyenne)-sum(n*p for n,p in '
                                       'zip(exo_tailles,exo_pertes))/sum(exo_tailles)) < 1e-6',
                               'hint': 'Additionnez d’abord les contributions 8×1 et 2×3, puis divisez par dix '
                                       'exemples.'},
                              {'prompt': 'Le lot x=[1,2,3,4], cible=2x, est coupé en trois exemples puis un. '
                                         'Donnez les coefficients à appliquer aux deux MSE moyennes avant '
                                         'backward.',
                               'setup': 'exo_x = torch.tensor([1.,2.,3.,4.])\n'
                                        'exo_cibles = 2*exo_x\n'
                                        'exo_p = torch.tensor(1.,requires_grad=True)',
                               'var': 'exo_coefficients',
                               'answer': '(3/4,1/4)',
                               'test': 'for exo_coefficient,(exo_a,exo_b) in '
                                       'zip(exo_coefficients,[(0,3),(3,4)]):\n'
                                       '    '
                                       'exo_locale=((exo_p*exo_x[exo_a:exo_b]-exo_cibles[exo_a:exo_b])**2).mean()\n'
                                       '    (exo_coefficient*exo_locale).backward()\n'
                                       'assert abs(exo_p.grad.item()+15) < 1e-6',
                               'hint': 'Chaque fraction représente un effectif. Gardez les poids fixes et ne '
                                       'remettez pas les gradients à zéro entre les morceaux.'}],
 'scheduler-et-arret-anticipe': [{'prompt': 'StepLR multiplie le taux par 0,5 toutes les deux époques. Quel taux '
                                            'est prêt après les deux premières mises à jour, depuis 0,1 ?',
                                  'setup': 'exo_p = torch.nn.Parameter(torch.tensor(1.))\n'
                                           'exo_opt = torch.optim.SGD([exo_p],lr=.1)\n'
                                           'exo_scheduler = '
                                           'torch.optim.lr_scheduler.StepLR(exo_opt,step_size=2,gamma=.5)\n'
                                           'for _ in range(2):\n'
                                           '    exo_opt.zero_grad()\n'
                                           '    (exo_p**2).backward()\n'
                                           '    exo_opt.step()\n'
                                           '    exo_scheduler.step()',
                                  'var': 'exo_taux',
                                  'answer': '0.05',
                                  'test': 'assert abs(float(exo_taux)-exo_opt.param_groups[0]["lr"]) < 1e-6',
                                  'hint': 'Le scheduler est appelé après les mises à jour ; le nouveau taux '
                                          'servira à la troisième époque.'},
                                 {'prompt': 'Un gradient scalaire vaut 10. Limitez sa norme à 1 avant le pas SGD '
                                            'de taux 0,1. Complétez avec l’appel de clipping.',
                                  'setup': 'exo_p=torch.tensor(1.,requires_grad=True)\n'
                                           'exo_opt=torch.optim.SGD([exo_p],lr=.1)\n'
                                           '(10*exo_p).backward()',
                                  'var': 'exo_norme_avant',
                                  'answer': 'torch.nn.utils.clip_grad_norm_([exo_p],max_norm=1.)',
                                  'test': 'assert exo_norme_avant.item() == 10\n'
                                          'assert abs(exo_p.grad.item()-1) < 1e-6\n'
                                          'exo_opt.step()\n'
                                          'assert abs(exo_p.item()-.9) < 1e-6',
                                  'hint': 'Le clipping modifie les gradients déjà calculés et renvoie leur norme '
                                          'précédente. Il vient avant step.'}],
 'cuda-amp-memoire': [{'prompt': 'Placez les entrées sur le même device que le modèle. Conservez leur type '
                                 'flottant.',
                       'setup': 'exo_modele=torch.nn.Linear(2,2)\n'
                                'exo_device=next(exo_modele.parameters()).device\n'
                                'exo_entrees=torch.tensor([[.1,1.5],[.2,4.5]])',
                       'var': 'exo_placees',
                       'answer': 'exo_entrees.to(exo_device)',
                       'test': 'assert exo_placees.device == next(exo_modele.parameters()).device\n'
                               'assert exo_placees.dtype == torch.float32\n'
                               'torch.testing.assert_close(exo_placees,exo_entrees)',
                       'hint': 'Affectez le tenseur renvoyé par to(device). Sur ce noyau, tout reste sur CPU ; '
                               'aucune mesure CUDA n’est produite.'},
                      {'prompt': 'Combien d’octets logiques occupent les paramètres d’une Linear(2,2), avec '
                                 'biais, en float32 ?',
                       'setup': 'exo_modele=torch.nn.Linear(2,2,dtype=torch.float32)',
                       'var': 'exo_octets',
                       'answer': '24',
                       'test': 'assert exo_octets == sum(p.numel()*p.element_size() for p in '
                               'exo_modele.parameters())',
                       'hint': 'Quatre poids et deux biais font six valeurs de quatre octets. Les gradients et '
                               'activations ne sont pas comptés.'}]}

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


def make(chapter,checks):
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
    if any(b.get('readingCompanion') and 'torchaudio'in b.get('code','')for b in chapter['blocks']):
        cells.append(code_cell('try:\n    import torchaudio\nexcept (ImportError, OSError) as error:\n    raise RuntimeError("TorchAudio manque ou ne correspond pas à PyTorch. Installer torch==2.10.0 et torchaudio==2.10.0 ensemble, puis redémarrer.") from error\nprint("TorchAudio",torchaudio.__version__)','audio-environment',['setup']))
    cells.append(code_cell(OBSERVER,'observer-helper',['observation-helper'],{'jupyter':{'source_hidden':True}}))
    programs=[]
    relevant=[]
    for index,block in enumerate(chapter['blocks']):
        if block.get('readingCompanion') and block.get('code') and block.get('language','python')=='python':relevant.append((index,block))
    assert relevant,chapter['id']+': programme compagnon manquant'
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
        program_id=block['programId']
        assertions=checks.get(chapter['id']+'/'+program_id,[])
        assert len(assertions)>=2,chapter['id']+'/'+program_id+': contrôles numériques manquants'
        program={'blockIndex':block_index,'programId':program_id,'sourceSha256':hashlib.sha256(block['code'].encode()).hexdigest(),'cellIds':[],'assertions':assertions}
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
            cells.append(code_cell(part['source'],cell_id,['demonstration'],{'quizProgram':program_index,'programId':program_id,'sourceLines':[part['firstLine'],part['lastLine']]}))
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
        assertion_id=prefix+'-checks'
        assertion_source='\n'.join('assert bool('+expression+'), '+repr(chapter['id']+'/'+program_id+': '+expression) for expression in assertions)
        assertion_source+='\nprint("Contrôles numériques de la démonstration réussis.")'
        cells.append(code_cell(assertion_source,assertion_id,['demonstration-check'],{'programId':program_id,'jupyter':{'source_hidden':True}}))
        program['assertionCellId']=assertion_id
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

def alias_notebook(previous,canonical,chapter):
    """Keep the former download URL without duplicating runnable content."""
    assert previous.startswith('notebooks/') and canonical==chapter['notebook']
    text=f'''# Ce notebook a été regroupé

Le contenu de cette ancienne adresse est désormais intégré à **{chapter['title']}**.
Ce fichier de renvoi ne contient pas de code à exécuter.

- [Ouvrir le notebook complet dans Colab](https://colab.research.google.com/github/RadioCodeur/quiz/blob/main/public/{canonical})
- [Consulter le fichier canonique sur GitHub](https://github.com/RadioCodeur/quiz/blob/main/public/{canonical})
- [Revenir au chapitre](https://radiocodeur.github.io/quiz/cours.html?theme=pytorch#{chapter['id']})

Le notebook canonique contient la démonstration progressive, ses contrôles et les deux exercices.
'''
    return {'nbformat':4,'nbformat_minor':5,'metadata':{'quiz':{'themeId':'pytorch','notebookAlias':canonical,'canonicalChapterId':chapter['id']}},'cells':[md(text,'canonical-notebook')]}


def main():
    course=json.loads((ROOT/'public/courses/pytorch.json').read_text(encoding='utf-8'))
    checks=json.loads((ROOT/'scripts/verify/narration-pytorch-checks.json').read_text(encoding='utf-8'))
    destination=ROOT/'public/notebooks';destination.mkdir(exist_ok=True)
    expected=set()
    for chapter in course['chapters']:
        relative=chapter.get('notebook',f'notebooks/{chapter["id"]}.ipynb')
        assert relative==f'notebooks/{chapter["id"]}.ipynb'
        path=ROOT/'public'/relative
        expected.add(path.name)
        notebook=make(chapter,checks)
        path.write_text(json.dumps(notebook,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
        print(chapter['id'],len(notebook['cells']),'cellules',len(notebook['metadata']['quiz']['programs']),'programmes')
    canonical={chapter['notebook']:chapter for chapter in course['chapters']}
    aliases=course.get('notebookAliases',{})
    for previous,target in aliases.items():
        assert target in canonical and previous not in canonical
        old_path=Path(previous)
        assert old_path.parent==Path('notebooks') and old_path.suffix=='.ipynb' and '..'not in old_path.parts
        assert old_path.name not in expected
        path=ROOT/'public'/old_path
        path.write_text(json.dumps(alias_notebook(previous,target,canonical[target]),ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
        expected.add(path.name)
    stale=[path.name for path in destination.glob('*.ipynb')if path.name not in expected]
    if stale:raise RuntimeError('Anciens notebooks à traiter explicitement : '+', '.join(stale))
    print('Created',len(canonical),'progressive notebooks and',len(aliases),'Markdown redirects. Execute the canonical notebooks before delivery.')

if __name__=='__main__':main()
