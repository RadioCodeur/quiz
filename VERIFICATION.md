# Vérification de la révision narrative PyTorch

État au **20 novembre 2026**, après l’audit du 19 novembre, base `9df9363`. Le commit applicatif `86ff2b2441ecb978f02c54fd75662d13243b1fc5` est poussé sur `main`. La publication et le contrôle public ont réussi.

## Contenu et compatibilité

Le site contient **110 entrées** : 88 chapitres des sept modules inchangés, puis **14 chapitres principaux et huit références PyTorch**. Six diagnostics sont disponibles dans le menu, sans entrer dans la progression principale.

Les 200 questions sont conservées. Les destinations des 50 questions PyTorch ont été relues ; 23 liens de couverture changent de chapitre. Le registre est `scripts/verify/pytorch-narration-question-moves.json`. Les anciennes destinations restent accessibles via 22 identifiants et dix alias. Les repères « lu », « à revoir » et la dernière lecture sont repris sans compter les références dans la barre des 14 principaux.

Les sept autres JSON sont identiques octet pour octet à la base. Le test `tests/pytorch-narration.test.mjs` contrôle aussi leurs empreintes normalisées. Les anciens chemins de notebooks restent disponibles : **22 notebooks exécutables et dix documents Markdown d’orientation**.

## Résultats sur les fichiers finaux

| Contrôle | Résultat | Preuve |
| --- | --- | --- |
| PyTorch assemblé | **25 programmes exécutés, 99 assertions réussies, 63 extraits reliés exactement** | `scripts/verify/narration-pytorch-results.json` |
| Notebooks | **22 noyaux CPU, 474 cellules de code et 44 solutions exécutées**, sans erreur | `scripts/verify/notebooks-results.json` et sorties livrées |
| Validation du contenu | **110 entrées et 200 questions couvertes** ; médias et banque valides | `npm run build` |
| Tests unitaires | **67 réussis, zéro échec** | `.tools/narration-unit.log`, journal local |
| Construction Vite | **Réussie** | `.tools/narration-build.log`, journal local |
| Navigateur | **36 contrôles Edge réussis** | `.tools/narration-browser.log`, journal local |
| Publication | **Réussie et vérifiée en ligne** | [Workflow Pages réussi](https://github.com/RadioCodeur/quiz/actions/runs/44635717608) |

Le lanceur `python scripts/verify/all.py` a aussi réussi ses trois commandes : PyTorch narratif, Python/Signal/Apprentissage audio, puis Génération/Évaluation/Oral. Le contrôle des liens accepte une ancienne ancre seulement si sa destination canonique existe. Les programmes des sept modules inchangés ont leurs preuves dans les deux rapports `audit-python-signal-ml-results.json` et `audit-generation-research-oral-results.json`.

`all-results.json` indique `notebooksReexecuted: false` pour ce passage : il ne prétend pas avoir lancé les noyaux au même moment. Les 22 exécutions Jupyter sont attestées séparément.

## Ce qui a été exécuté

Le vérificateur PyTorch exécute les programmes `readingCompanion` dans un dossier temporaire, puis vérifie leurs résultats et leurs empreintes. Les 63 extraits du fil sont des plages exactes de ces programmes. Ils restent présentés comme des extraits avec leurs objets nécessaires, pas comme des programmes autonomes.

La petite boucle effectue 201 pas SGD de taux 0,1. Elle donne `[0,1,0]` et une perte recalculée d’environ 0,225241 sur les trois lignes apprises. Les quatre observations réservées donnent `[0,1,0,1]` et une perte d’environ 0,309575 ; la validation ne modifie ni poids ni biais. Ces données choisies ne constituent pas une estimation de performance sur des fichiers réels.

Les notebooks conservent les 25 programmes par concaténation exacte des cellules de démonstration. Ils exécutent aussi leurs 99 assertions. Chaque notebook contient deux exercices éditables, deux indices et deux solutions repliées. À vide, les exercices indiquent « À compléter » ; ils ne prétendent pas avoir été réussis. Les 44 solutions sont exécutées en complément, puis les cellules de vérification temporaires sont retirées.

Les durées du rapport final vont de **4,862 à 6,822 secondes**, avec **132,255 secondes cumulées**, démarrage des noyaux compris. Le seuil de 120 secondes par notebook est respecté. Les dix documents d’orientation ne contiennent pas de code et ne sont pas comptés comme des exécutions.

## Lecture et interface

Le navigateur a parcouru les sept premières étapes jusqu’à la validation avec les programmes complets repliés. Les 110 entrées se rendent à 360 px sans débordement de page. Les contrôles couvrent aussi les dix alias, le compteur indépendant des références, la reprise des anciens repères, les réponses incorrectes, le clavier, les détails associés aux lignes, les préférences et la position de lecture.

La convolution permet effectivement de changer le premier poids du noyau ; passer de 1 à 2 donne `[[-3,-2],[0,1]]`. La préparation des scénarios de migration recharge les données avant la navigation afin de tester un vrai retour sur le site.

Les captures `test-results/narration-first-desktop.png`, `narration-loss-desktop.png`, `narration-linear-fragment.png` et `narration-dataset-mobile.png` ont été inspectées. L’introduction a été resserrée et les titres des résultats repliés ne révèlent plus leur correction.

Le reflow à 200 % a été approché avec 720 pixels CSS et une police racine à 200 %. Le zoom natif de la barre d’outils, le téléphone physique et l’audit formel par lecteur d’écran ne sont pas attestés.

## Publication

Le commit `86ff2b2441ecb978f02c54fd75662d13243b1fc5` est publié : [workflow Pages 44635717608 réussi](https://github.com/RadioCodeur/quiz/actions/runs/44635717608), contrôlé le **20 novembre 2026**.

Le script public a comparé les huit modules (110 entrées), les 22 notebooks, les dix renvois Markdown et les 160 termes du glossaire avec les fichiers locaux. Toutes les réponses étaient HTTP 200 et les JSON identiques. Edge a contrôlé le quiz, les cours, le sommaire 14+8, les programmes repliés, les axes, les pistes orales et le glossaire : `errors: []`.

Le contrôle des renvois utilise désormais une empreinte du JSON canonique, indépendante des fins de ligne de Git sous Windows ou Linux. Cette correction a résolu l’échec du premier workflow ; les contenus exécutables sont inchangés.

Commande réellement exécutée :

```powershell
node scripts/verify-public.mjs 86ff2b2441ecb978f02c54fd75662d13243b1fc5 https://github.com/RadioCodeur/quiz/actions/runs/44635717608
```

La commande `node scripts/verify-public.mjs SHA40 URL_DU_WORKFLOW` compare les huit modules, les 22 notebooks, les dix documents d’orientation et le glossaire. Elle vérifie aussi les trois pages et les interactions publiques. Son rapport `test-results/audit-public-verification.json` reste local et ignoré par Git.

## Environnement et limites

Python 3.11.9, PyTorch/TorchAudio 2.10.0 CPU, nbformat 5.11.1 et nbclient 0.11.0. Les vérifications configurent un thread hors du programme central de première boucle. Le runtime Windows est `.tools/notebook-runtime/Scripts/python.exe`.

Les branches CUDA/AMP n’ont pas été exécutées sur GPU. Aucune session Colab authentifiée n’a exécuté ces notebooks. Les descripteurs, cibles et exemples réservés sont choisis ; les ondes de 220 et 440 Hz sont synthétiques. Une baisse de MSE sur leurs cartes mel ne prouve ni qualité sonore ni généralisation.

## Reproduire

```powershell
npm run validate:courses
npm test
npm run build
npm run test:browser
python scripts/verify/all.py
python scripts/verify/notebooks.py
```

Pour reconstruire les notebooks : `python scripts/make-progressive-notebooks.py`, puis réexécuter leur vérificateur. Conserver ailleurs les réponses personnelles avant cette opération. Si npm manque dans le PATH, utiliser `node scripts/run.mjs` suivi du nom du script. Les dépendances scientifiques sont déclarées dans `scripts/requirements-verify.txt` et `scripts/requirements-media.txt`.

## Historique

`docs/audit-revision-report.md` décrit la précédente révision à 120 chapitres et 32 notebooks exécutables. Ses 59 tests, 33 contrôles navigateur, 654 cellules et 64 solutions restent historiques. Les rapports PyTorch précédents ne sont pas les preuves du présent module.

Le rapport éditorial courant est `docs/pytorch-narration-report.md`. La base des alias, des sources et des modules conservés est `scripts/verify/pytorch-narration-baseline.json`.
