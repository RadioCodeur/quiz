# Vérification de la révision pédagogique

État documentaire au **19 novembre 2026**, après l’audit demandé le 18 novembre. La révision est publiée et vérifiée en ligne. Le quiz reste l’entrée principale ; le navigateur n’exécute pas Python.

## Contenu et compatibilité

- **120 chapitres dans huit modules**, dont 32 chapitres PyTorch. Les 107 identifiants du point de départ `57fce919006dcf1edbf6aeadd4eb67f54d657453` restent présents ; 13 identifiants sont ajoutés.
- **200 questions de quiz conservées** et couvertes dans leur thème principal. Les 15 changements de chapitre de référence sont consignés dans `scripts/verify/audit-question-moves.json`.
- Les anciennes ancres, les sources d’origine et les repères de lecture utiles restent compatibles. Les checkpoints peuvent être réécrits ; une ancienne tentative ne devient pas une réponse à une question modifiée.
- « Lu » et « À revoir » restent distincts du score du quiz. Les finales automatiques « À dire en entretien » ne sont plus une contrainte éditoriale.
- Les médias existants sont conservés : 18 WAV, 61 figures, cinq illustrations externes créditées, onze ateliers d’écoute et douze blocs d’images. Les tests contrôlent chemins, licences, empreintes et mesures PCM.

## Contrôles attestés pour cette révision

| Contrôle | État constaté | Preuve |
| --- | --- | --- |
| Tests unitaires Node | **59 réussis, 0 échec, 0 ignoré** sur les fichiers finaux. | Journal local `.tools/audit-unit.log`, ignoré par Git. |
| Quatre scripts scientifiques courants | **107 cas exécutés sur CPU**, variantes comprises ; quatre codes de sortie 0. | `scripts/verify/all-results.json` et les quatre rapports ci-dessous. |
| Notebooks PyTorch | **32 documents**, **654 cellules de code** et **64 solutions exécutées** ; aucun exercice vide annoncé comme réussi. | `scripts/verify/notebooks-results.json` et sorties conservées dans les notebooks. |
| Construction | **Réussie sur les fichiers finaux.** | Journal local `.tools/audit-build.log`, ignoré par Git. |
| Tests et relecture dans le navigateur | **33 contrôles réussis dans Edge sous Windows sur les fichiers finaux.** | Journal local `.tools/audit-browser.log`, ignoré par Git ; bilan ci-dessous. |
| Audit de prose | **120 chapitres parcourus** par l’outil d’aide à la lecture. | `scripts/verify/prose-audit.json` régénéré ; aucune finale orale obligatoire. |
| Push et publication GitHub Pages | **Réussis, puis vérifiés sur le site public.** | Commit `3bbeb56`, [workflow Pages réussi](https://github.com/RadioCodeur/quiz/actions/runs/44442432394), rapport local `test-results/audit-public-verification.json`. |

Les tests unitaires couvrent notamment la banque, les liens question/chapitre, les ancres, les états personnels, les notebooks, les empreintes CPU, les axes et les variations des laboratoires. Leur succès ne remplace pas une relecture pédagogique ni une vérification dans le navigateur.

## Calculs scientifiques réellement exécutés

Les rapports actuels lisent les programmes dans les JSON livrés. Ils enregistrent les empreintes du code, les sorties et, selon le cas, les valeurs intermédiaires et assertions. Les tests relient chaque programme Python affiché à sa preuve.

| Script courant | Cas | Ce qui est contrôlé |
| --- | ---: | --- |
| `scripts/verify/audit-pytorch-core.py` | 19 | Formes, types, scores, pertes, gradients, mise à jour, première boucle et opérations sur les axes. |
| `scripts/verify/audit-pytorch-advanced.py` | 19 | Dataset, padding, masques, gel, accumulation, reprise, optimisation, mel, convolution et boucle complète. |
| `scripts/verify/audit-python-signal-ml.py` | 38 | Python scientifique, fichiers audio déclarés, transformations, représentations et apprentissage audio ; une variante de similarité. |
| `scripts/verify/audit-generation-research-oral.py` | 31 | Mécanismes génératifs et calculs d’évaluation ; deux variantes de quantification et de VAE. |
| **Total** | **107** | **104 programmes affichés et trois variantes explicites.** |

Chaque script produit son fichier `*-results.json` de même nom. Les vérifications numériques complémentaires incluses dans ces rapports ne sont pas ajoutées au total des 107 cas.

Le dernier `all-results.json` contient les quatre commandes réussies et `notebooksReexecuted: false`. Il atteste leur regroupement, sans prétendre avoir relancé les notebooks lors de ce même passage. Les exécutions des 32 notebooks sont attestées séparément par `notebooks-results.json`.

Quelques résultats relus : les scores initiaux donnent `[0,0,0]`, puis la copie modifiée donne `[0,1,0]` sans modifier l’original. Le dernier lot du Dataset garde la forme `(1,2)` et sa cible. L’autoencodeur retrouve la forme `(2,1,64,96)` ; sa MSE passe de 0,875999 à 0,796794 après un pas sur sa miniature synthétique.

## Notebooks et exercices

Les 32 fichiers sont liés depuis leurs chapitres. Leurs métadonnées lient les **38 programmes PyTorch** aux cellules progressives par identifiant et SHA-256. La concaténation exacte des sources est vérifiée avant exécution. Les observations ajoutées restent distinctes du programme du cours et des exercices.

Deux cellules éditables par notebook utilisent `...` ou `None` avec une garde. Une cellule non complétée signale son état ; ses assertions ne prétendent pas valider une réponse absente. Les deux indices précèdent les solutions repliées en fin de document. Les solutions complètes sont ajoutées temporairement à la vérification, exécutées, puis retirées des cellules livrées.

Les documents finaux contiennent **654 cellules de code exécutées**. Les **64 solutions** sont exécutées en complément ; elles ne sont pas comptées comme exercices réussis par l’utilisateur. Les empreintes de document sont calculées sur le JSON canonique, avec les sorties conservées.

Le rapport final mesure **242,212 secondes cumulées**, avec **6,182 à 11,872 secondes par notebook**, démarrage du noyau compris. Les deux notebooks resynchronisés après les derniers paragraphes d’explication ont été réexécutés : 6,824 et 6,690 secondes. Le seuil de 120 secondes est respecté sur la machine de contrôle. Ces durées ne prédisent pas celles d’un autre ordinateur ou de Colab.

## Environnement et limites

Les calculs courants ont utilisé Python **3.11.9**, PyTorch et TorchAudio **2.10.0 CPU**, avec un thread pour les vérifications PyTorch. Les versions du noyau sont nbformat 5.11.1, nbclient 0.11.0 et ipykernel 7.1.0. Les dépendances sont déclarées dans `scripts/requirements-verify.txt` et `scripts/requirements-media.txt` : NumPy 2.3.5, SciPy 1.16.3, librosa 0.11.0, SoundFile 0.13.1 et Matplotlib 3.10.8.

Les branches CUDA/AMP sont expliquées, mais **n’ont pas été exécutées sur GPU**. Aucun benchmark GPU, test sur téléphone physique ou audit formel par lecteur d’écran n’est attesté par ces rapports.

Les extraits de voix et de percussion du laboratoire sont réels. Les programmes précisent le fichier, le segment, le taux d’échantillonnage et les conventions utilisés. Les lecteurs peuvent utiliser un dérivé différent du fichier source analysé ; le cours le signale.

Les tableaux PyTorch RMS/crête, les cibles, les décisions de classification et les données d’évaluation sont choisis pour raisonner. Les sinusoïdes de 220 et 440 Hz sont synthétiques. Les prédictions fixées et les décodeurs identités sont des dispositifs pédagogiques explicites. Les intervalles bootstrap ne démontrent pas une supériorité musicale réelle.

Aucun modèle neuronal audio préentraîné n’est téléchargé ou évalué par ces démonstrations. Le stockage logique des poids et l’erreur d’une projection miniature ne mesurent ni qualité perceptive, ni mémoire résidente, ni accélération réelle. Les interfaces multimodales montrent des contrats de représentation ; elles ne constituent pas une évaluation de CLAP ou de PostGenAI.

**Colab n’a pas été exécuté dans une session authentifiée pour cette révision.** La présence des liens est vérifiée dans le code et les tests. Les anciens contrôles HTTP de 20 notebooks ne prouvent pas la disponibilité ou l’exécution des 32 versions actuelles après publication.

## Reproduire les contrôles

Dans le dépôt, avec Node compatible et l’environnement scientifique isolé activé :

```powershell
npm run validate:courses
npm test
npm run build
npm run test:browser
python scripts/verify/all.py
python scripts/verify/notebooks.py
```

Pour régénérer les notebooks depuis `public/courses/pytorch.json`, puis réexécuter tous les calculs et noyaux :

```powershell
python scripts/make-progressive-notebooks.py
python scripts/verify/all.py --notebooks
```

La régénération remplace les documents : conserver ailleurs les réponses personnelles avant de la lancer. Les dépendances de vérification ne sont pas utilisées par le site :

```powershell
python -m pip install torch==2.10.0 torchaudio==2.10.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r scripts/requirements-verify.txt
```

Sous Windows, le runtime employé pour les preuves est `.tools/notebook-runtime/Scripts/python.exe`. Le vérificateur lance ses noyaux avec ce même interpréteur. Si npm n’est pas dans le PATH, `node scripts/run.mjs` accepte le nom du script npm.

## Bilan navigateur final

**État au 19 novembre 2026 : construction et 33 contrôles réussis sur les fichiers finaux.**

Le responsable de livraison a exécuté 33 contrôles dans Microsoft Edge sous Windows, tous réussis. Le parcours couvre les 120 chapitres à 360 px sans débordement, le retour d’une mauvaise réponse, le clavier, la restauration des étapes et des réponses, ainsi que la reprise après changement de taille du texte, mode lecture et rechargement. Trois pistes orales restent accessibles avant l’ouverture du modèle. Les interactions sur l’audio réel et la construction servie sous un sous-chemin ont été contrôlées. Les captures desktop et mobile ont été inspectées.

Le reflow correspondant à 200 % a été approché par une fenêtre de 720 pixels CSS et une taille de police racine à 200 %. **Le zoom natif de la barre d’outils du navigateur n’a pas été testé.** Ces contrôles ne constituent pas un test sur téléphone physique.

La relance finale de `npm test`, `npm run build` et `npm run test:browser` a réussi après le dernier ajustement de libellé. Les journaux locaux sont `.tools/audit-unit.log`, `.tools/audit-build.log` et `.tools/audit-browser.log`. Les captures restent dans `test-results/`, notamment `audit-scores-desktop.png`, `audit-linear-large-text.png` et `audit-linear-mobile.png`.

## Publication vérifiée

**État au 19 novembre 2026 : publication réussie et contrôle public réussi.**

- Commit applicatif publié : `3bbeb56fe13e06efd74f37ec3c59634bfd2dc348`, poussé sur `main` le 19 novembre 2026.
- [Workflow GitHub Pages 44442432394](https://github.com/RadioCodeur/quiz/actions/runs/44442432394) : `completed / success` pour ce commit.
- [Site publié](https://radiocodeur.github.io/quiz/cours.html) : les huit JSON de cours, les 32 notebooks et le glossaire public sont identiques aux fichiers locaux validés.
- Le contrôle Edge public à 360 px a parcouru le quiz, le catalogue des cours, les axes interactifs, les trois pistes orales et le glossaire de 160 termes : aucune exception ni réponse HTTP en erreur.
- Les 32 téléchargements ont répondu HTTP 200 et leur contenu a été comparé. Les liens Colab sont construits et vérifiés localement ; aucune exécution Colab authentifiée n’est revendiquée.

Commande réellement exécutée après déploiement :

```powershell
node scripts/verify-public.mjs 3bbeb56fe13e06efd74f37ec3c59634bfd2dc348 https://github.com/RadioCodeur/quiz/actions/runs/44442432394
```

Le rapport `test-results/audit-public-verification.json` conserve le SHA publié, le workflow, les effectifs et la liste des pages vérifiées, avec `errors: []`. Il reste local et ignoré par Git.

## Rapports historiques

`docs/revision-report.md`, `pytorch-existing-results.json`, `pytorch-additions-results.json`, les rapports `b-*`, `existing-corpus-results.json` et les anciens contrôles de liens décrivent des lots antérieurs. Leurs 107 chapitres, 20 notebooks, finales orales imposées et anciens nombres de tests ne valent pas pour le contenu actuel. Le rapport `prose-audit.json`, lui, a été régénéré sur les 120 chapitres ; il sert d’aide à la lecture et n’impose pas les anciennes finales orales.

`scripts/verify/audit-baseline.json` conserve le point de comparaison. Le rapport courant est `docs/audit-revision-report.md`. Les preuves actuelles sont les quatre rapports d’audit et le rapport des 32 notebooks cités plus haut.
