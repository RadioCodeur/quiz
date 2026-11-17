# Vérification de la livraison

Révision complète du 18 novembre 2026, pour la préparation de l’entretien IRCAM. Le quiz reste l’entrée principale ; aucun interpréteur Python n’est intégré au site.

## Résultat et conservation

- Huit modules, 107 chapitres : 65 identifiants historiques conservés, 42 nouveaux. Les `questionIds`, les références d’origine et les checkpoints historiques sont protégés par des contrats. Aucun QCM ajouté, supprimé ou renuméroté : les 200 restent couverts.
- Vingt chapitres PyTorch, vingt notebooks et quarante exercices avec solutions exécutées. Les six nouveaux chapitres techniques couvrent Transformer, codecs RVQ, objectifs génératifs, contrôle multimodal, budget et symbolique.
- Quatre chapitres de contexte, huit lectures commentées ; 25 questions ouvertes, un pitch hypothétique et son gabarit personnel ; glossaire de 160 termes et parcours rapide sur quatre semaines.
- Toutes les conclusions sont rédigées pour l’oral. L’audit des chapitres et des présentations de module ne trouve aucune phrase de prose au-dessus de 30 mots. Les checkpoints historiques sont conservés et exclus de cette réécriture.
- Le chapitre des niveaux audio dépasse 1100 mots avec une justification visible. Il conserve les définitions, les échelles et la comparaison des deux extraits réels demandées par le lecteur. Les autres chapitres respectent la limite.
- Les neuf walkthroughs historiques sans code sont annoncés comme tableaux de calcul raisonné. Les quatre exemples de contexte utilisent le même format. La boucle complète renvoie à son programme unique avec `codeBlockIndex`, sans recopier une seconde version.

## Contrôles d’acceptation

Les commandes `npm run validate:courses`, `npm test`, `npm run build` et `npm run test:browser` ont été lancées sur le dépôt Windows. Le bilan final comporte 51 tests Node et 28 contrôles navigateur.

Les contrôles navigateur utilisent Microsoft Edge et Playwright : 107 chapitres à 360 px, navigation et stockage du quiz, repères de lecture, exemples guidés, écoutes volontaires, sources, glossaire bilingue, pitch persistant et parcours rapide. La construction est aussi servie sous `/qr-entretien/` pour vérifier les chemins relatifs des trois pages. Les captures restent dans `test-results/`, sans publication.

Les tests couvrent les médias déjà livrés : 18 WAV, 61 figures scientifiques, cinq illustrations externes créditées, onze ateliers d’écoute et douze blocs d’images. Crête, RMS, dBFS, gains et durées sont recalculés depuis le PCM. Les fichiers source et licences sont inchangés.

## Exécutions scientifiques réelles

Commande complète : `python scripts/verify/all.py --notebooks`. Elle a réussi avec Python 3.11.9, PyTorch/TorchAudio 2.10.0+cpu et un thread. Les rapports conservent les empreintes du code, les sorties et les conditions ; les tests lient chaque bloc Python affiché à une preuve CPU.

- 74 blocs Python affichés sont couverts. L’audit hors PyTorch exécute 57 cas, dont trois variantes, et treize vérifications numériques complémentaires ; aucune incohérence restante.
- `pytorch-existing.py` et `pytorch-additions.py` : les vingt programmes PyTorch, le graphe à deux poids, les cinq erreurs et la boucle complète. Gradients mesurés : 24 et −72 ; sauvegarde puis rechargement identique.
- `b-attention-control.py`, `b-codecs-symbolic.py`, `b-diffusion-efficiency.py` : formes, causalité, RVQ, événements, objectifs et coûts. Le passé causal reste identique ; la RVQ miniature donne une MSE de 0,006250.
- `existing-corpus.py --strict` : sources lues dans les JSON courants, contextes des extraits partiels explicités, variantes et calculs hors code. Les deux bruits pédagogiques VAE/diffusion sont désormais fixés dans le programme comme dans le calcul manuel.
- `notebooks.py` : vingt noyaux Jupyter séparés, toutes cellules et quarante solutions. Durées finales, démarrage compris : 5.515–8.360 secondes par notebook, toutes sous 120 secondes. Les sorties sont enregistrées dans les documents livrés.
- `editorial-protection.json`, `baseline-course-contracts.json`, `existing-corpus-baseline.json` et `prose-audit.json` : conservation et audit éditorial. `all-results.json` donne les commandes et codes de sortie finaux.

Le noyau utilise nbformat 5.11.1, nbclient 0.11.0 et ipykernel 7.1.0. Les calculs audio utilisent NumPy 2.3.5, SciPy 1.16.3, librosa 0.11.0 et SoundFile 0.13.1. L’environnement est documenté dans `scripts/requirements-verify.txt`.

## Sources et portée

Les nouvelles références sont des pages primaires réellement ouvertes. Le registre `scripts/verify/research-sources.json` détaille 37 sources, les faits retenus et les accès remplacés. Les huit lectures ont chacune trois idées et une question de recherche. Les pages publiques de cours France-IOI et les références pédagogiques antérieures restent documentées dans `docs/pedagogie.md`.

Les vingt sources de notebooks existent sur GitHub. Le lien Colab public a répondu HTTP 200 ; son interface propose la connexion. Aucune session Colab authentifiée n’a été disponible : l’exécution attestée est locale sur CPU. Voir `scripts/verify/notebook-links.json`.

La comparaison du petit budget mesure une erreur numérique sur des projections synthétiques et calcule le stockage logique des poids. Elle ne démontre ni qualité perceptive audio, ni gain de vitesse, ni mémoire résidente. Les interfaces CLAP sont des exemples de formes, sans modèle préentraîné chargé. Les objectifs de PostGenAI ne sont pas présentés comme des résultats obtenus.

Aucun entraînement de grand modèle externe, benchmark GPU, test sur téléphone physique ou audit formel par lecteur d’écran n’est revendiqué. Les durées orales sont indicatives : 184–220 mots par réponse et 303 mots pour le pitch. Le format oral et les tableaux de contexte adaptent explicitement R1 à un raisonnement, sans programme artificiel.

## Reproduire

```powershell
npm run validate:courses
npm test
npm run build
npm run test:browser
python -m pip install torch==2.10.0 torchaudio==2.10.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r scripts/requirements-verify.txt
python scripts/verify/all.py --notebooks
```

Si npm n’est pas dans le PATH, utiliser `node scripts/run.mjs` suivi du nom du script. Les dépendances scientifiques concernent uniquement la vérification hors du navigateur.
