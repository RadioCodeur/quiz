# Révision narrative de PyTorch

État au **20 novembre 2026**, à partir de `9df9363`. Ce rapport décrit le travail demandé par `Audit_PyTorch_narration_2026-11-19.md`. L’assemblage, les noyaux CPU et les contrôles locaux sont terminés ; leur bilan figure dans `../VERIFICATION.md`.

## Organisation retenue

PyTorch comporte **14 chapitres principaux et huit références**, soit **22 entrées**. Les sept autres modules conservent leurs 88 chapitres : le site compte donc **110 entrées de cours**. L’index de dépannage, accessible depuis le menu PyTorch, contient six situations et n’ajoute pas un chapitre à terminer.

Le premier trajet s’arrête à une validation ordinaire. Il permet de pratiquer une petite boucle avant les lots, les masques et les compléments techniques.

| Partie | Chapitres principaux |
| --- | --- |
| Une première boucle et sa validation | 1. Préparons nos trois extraits ; 2. Que prédit notre classifieur ? ; 3. Calculons les scores avec une couche ; 4. Donnons un coût à l’erreur ; 5. Comment déplacer un poids ? ; 6. Faisons apprendre notre premier modèle ; 7. Essayons des exemples réservés. |
| Quand les données demandent plus de soin | 8. Dataset et DataLoader ; 9. Moyenne, broadcasting et sélection cohérente ; 10. Axes attendus ; 11. Padding et moyenne masquée ; 12. Expérience complète et sauvegarde simple. |
| Passer à une représentation audio | 13. Convolution locale ; 14. Préparation mel et reconstruction par autoencodeur. |

Les références A–H traitent la rétropropagation à deux poids, SGD/Adam/AdamW, copie/détachement/gel, les présences multiples, les états du modèle et d’Adam, les microlots, le réglage et la stabilisation, puis CPU/CUDA/AMP. Leur consultation est distincte de la progression principale sur 14 chapitres.

## Réécriture réalisée

Les pages ont été réécrites autour des difficultés rencontrées. Une percussion mal classée relie les scores, la couche, la perte et l’apprentissage. Les transitions nomment ce qui manque encore : produire un score pour une nouvelle mesure, donner un coût à l’erreur, utiliser le gradient, puis observer d’autres exemples.

La lecture présente de courts paragraphes et quelques nouvelles lignes. Chaque fragment Python précise ses objets nécessaires et correspond à une plage exacte d’un programme complet. Le programme autonome et son pas à pas restent repliés, comme outils complémentaires. Les résultats précis, diagnostics détaillés et variantes exhaustives sont placés à la demande.

Les questions demandent de prévoir une sélection, une mutation, un déplacement ou un diagnostic avant la correction correspondante. Elles conservent au moins quatre propositions et une seule réponse correcte. Les supports JavaScript sont intégrés au raisonnement : suivre un biais, comparer les axes, essayer un taux ou déplacer un noyau. Le navigateur n’exécute pas Python.

Principaux choix de progression :

- Création du tableau, types et sélection au premier plan ; contrôles de finitude dans un diagnostic facultatif.
- Couche `Linear` appelée directement avant l’organisation en `nn.Module`. Le biais est testé à poids constants.
- Deux réponses incorrectes pour la même percussion introduisent le besoin d’une perte ; les valeurs arrondies précèdent les décimales de contrôle.
- Un seul scalaire relie perte, dérivée et pas SGD. Les deux poids et `retain_grad` restent une référence.
- Première boucle sans réglage de threads ni graine dans son programme central.
- Validation sur quatre observations réservées, puis distinction entre `eval` et `no_grad`.
- Même expérience pour la synthèse et le rechargement ; aucune génération supplémentaire de nuages de points n’est nécessaire.
- Dataset de formes fixes avant les durées variables ; padding et moyenne masquée répondent à la même difficulté.
- Préparation mel expliquée dans le fil avant sa reconstruction, sans répéter toutes les lignes dans la première lecture.

## Données, résultats et portée

Les trois lignes de départ restent `[[0.1,1.5],[0.2,4.5],[0.15,2.5]]`, avec les annotations `[0,1,0]`. Les colonnes représentent une RMS et un facteur de crête choisis pour le calcul. Elles ne sont pas les mesures des fichiers du laboratoire audio.

Les poids initiaux `[[0,1],[0,-1]]` et les biais nuls donnent les décisions `[0,0,0]`. Après 201 pas SGD de taux 0,1, les décisions sont `[0,1,0]` et la perte moyenne recalculée vaut environ **0,225241**.

Les quatre observations réservées sont aussi choisies à la main. Le même modèle y donne `[0,1,0,1]`, soit quatre accords, et une perte moyenne d’environ **0,309575**. Ces résultats vérifient les mécanismes ; ils n’estiment pas une performance statistique sur une sonothèque réelle.

Le cas de padding indépendant utilise `[2,4]` et `[6]`, avec des unités arbitraires. La moyenne masquée retrouve 3 et 6 ; la moyenne naïve du rectangle donnerait 3 et 3. Les ondes de 220 et 440 Hz restent synthétiques. La reconstruction d’une carte mel ne constitue pas une reconstruction sonore certifiée.

## Compatibilité et périmètre

Les **200 questions du quiz** restent inchangées. Les **50 questions PyTorch** sont reliées aux passages qui traitent leur opération ou leur contrat ; les changements de destination sont consignés dans `scripts/verify/pytorch-narration-question-moves.json`.

Les 32 anciennes destinations PyTorch correspondent à **22 identifiants canoniques et dix alias**. Les anciennes ancres et les repères de progression sont repris vers le contenu regroupé. La lecture des références n’augmente pas le nombre de chapitres principaux terminés.

Les **22 notebooks canoniques** sont générés et exécutés, avec deux exercices par document. Dix anciens chemins de notebooks sont conservés comme documents d’orientation vers les versions regroupées. Les 474 cellules de code et les 44 solutions ont été exécutées sans erreur.

Les sept autres JSON de cours sont identiques octet pour octet à ceux du dépôt de départ. Leurs empreintes après normalisation des fins de ligne correspondent aussi au manifeste `scripts/verify/pytorch-narration-baseline.json`. Les adaptations partagées concernent la lecture continue, les renvois, le menu et la reprise de progression.

## Vérifications et état de livraison

Les trois fragments ont été exécutés séparément sur Python 3.11.9 / PyTorch 2.10.0 CPU : **25 programmes et 99 assertions**. Le vérificateur relie les petits fragments aux lignes exactes de leur programme. Le JSON final a également été exécuté : 25 programmes, 99 assertions et 63 extraits exacts. Les sept autres modules restent inchangés.

| Vérification finale | État de ce rapport |
| --- | --- |
| CPU sur le JSON assemblé | 25 programmes, 99 assertions et 63 extraits exacts ; rapport conservé. |
| 22 notebooks, exercices et solutions | 22 noyaux CPU, 474 cellules et 44 solutions réussis. |
| Tests unitaires et validation du contenu | 67 tests réussis ; banque et couverture des 200 questions valides. |
| Construction et contrôles navigateur | Construction et 36 contrôles Edge réussis. |
| Lisibilité étroite, clavier, progression et anciens liens | 110 entrées à 360 px, clavier, alias et repères contrôlés. |
| Publication et contrôle du site public | [Workflow Pages réussi](https://github.com/RadioCodeur/quiz/actions/runs/44635717608) ; fichiers publics identiques et aucune erreur navigateur. |

Les branches CUDA/AMP n’ont pas été exécutées sur GPU. Aucune session Colab authentifiée n’a été exécutée pour cette révision. Les chiffres d’exécution et de publication des anciens rapports décrivent leurs lots historiques.

Les captures de la lecture par défaut ont été inspectées. Le haut des pages a été allégé et les titres des compléments masqués ne donnent plus les résultats. La convolution possède désormais le contrôle du poids annoncé. Le reflow à 200 % est simulé ; le zoom natif du navigateur n’a pas été contrôlé.

## Publication

Le commit `86ff2b2441ecb978f02c54fd75662d13243b1fc5` est publié sur [le module PyTorch](https://radiocodeur.github.io/quiz/cours.html?theme=pytorch). Le [workflow Pages 44635717608](https://github.com/RadioCodeur/quiz/actions/runs/44635717608) a réussi. Le contrôle public du 20 novembre confirme les huit modules, les 22 notebooks canoniques, les dix orientations et le glossaire, avec des JSON identiques aux fichiers locaux et `errors: []`.

Le premier déploiement avait échoué sur l’empreinte des orientations, sensible aux fins de ligne Windows/Linux. Ces documents sont maintenant comparés par leur JSON canonique, sans changer les contenus exécutables. Les détails et la commande de vérification figurent dans `../VERIFICATION.md`.

## Références pédagogiques consultées

La progression s’inspire du besoin limité, des instructions proches de leur explication et des états à prévoir observés dans [France-IOI : suivre l’évolution des variables](https://www.france-ioi.org/algo/course.php?idChapter=644&idCourse=2364), [France-IOI : découverte « Réponds ! »](https://www.france-ioi.org/algo/task.php?idChapter=644&idTask=1863) et [OpenClassrooms : variables](https://openclassrooms.com/fr/courses/7168871-apprenez-les-bases-du-langage-python/7289466-enregistrez-vos-donnees-avec-des-variables). Ces pages publiques ont été ouvertes ; leurs textes et leurs histoires ne sont pas reproduits dans le cours.
