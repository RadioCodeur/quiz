# Vérification de la livraison

Révision éditoriale du **13 novembre 2026**, adaptée à un lecteur connaissant déjà le Python algorithmique.

## Contenu et cohérence

- Six modules et 65 chapitres, dont deux rappels Python facultatifs en fin de sommaire. Les 65 identifiants et les associations aux 200 QCM sont comparés à la version publiée précédente et conservés. La banque du quiz reste inchangée.
- Les développements, projets et transitions ont été réécrits. Les signaux miniatures du Python servent successivement à calculer RMS, facteur de crête, caractéristiques et standardisation ; leurs sorties sont exécutées et vérifiées. Les changements de taille ou de scénario sont annoncés.
- Les 65 exemples guidés et les 65 représentations relationnelles sont présents. Les cas courts passent de 65 à 8 : les exemples de syntaxe élémentaire et les variantes répétitives ont été retirés. Les variantes conservées et les définitions se déplient à la demande.
- Les pages publiques de cours et de découverte France-IOI citées dans `docs/pedagogie.md` ont été lues, y compris des explications intégrées aux énoncés. OpenClassrooms a également été consulté. Aucun accès aux corrections privées ou aux niveaux verrouillés n’est revendiqué ; les scénarios et les textes audio sont originaux.
- Relecture de la couverture scientifique des QCM par thème. Les correspondances automatiques prouvent la présence d’un lien, pas la compréhension du lecteur ni une exhaustivité de toutes les questions d’entretien possibles.

## Vérifications techniques

- Banque validée : exactement 200 QCM, quotas principaux 20/50/30/30/40/30 et 60/100/40 par difficulté ; identifiants, propositions et références résolus.
- **34 tests de logique** : quiz, progression, liens historiques, schéma, couverture, références, géométrie des graphiques, échappement des sorties, exemples sans variante et navigation principale sans obligation de lire les rappels.
- **23 contrôles navigateur** : session du quiz, reprise, bilan, clavier et stockage indisponible ; navigation quiz/cours ; repères de lecture et préférences ; rendu des 65 chapitres à 360 px ; états et lignes des exemples guidés ; QCM de transfert ; tableaux des graphiques ; présentation des modules ; définitions repliables ; rappels par lien direct ; deux entrées Vite sous un chemin de dépôt. Certains contrôles regroupent plusieurs assertions.
- Construction Vite après validation des données, puis test du site construit sous `/qr-entretien/`. Aucun interpréteur Python ni nouvelle API extérieure n’est ajouté à l’application.
- Les extraits scientifiques modifiés sont vérifiés en Python avec NumPy, SciPy, librosa et PyTorch selon le thème. Les blocs partiels utilisent des données et objets de contexte explicites pendant la vérification. Aucun modèle audio complet n’a été entraîné pour cette révision.
- Un problème de l’ancien exemple Dropout est corrigé : `eval()` peut laisser Dropout retourner son entrée ; `no_grad()` ne retire pas rétroactivement `requires_grad` à cette entrée. L’exemple observe désormais une opération nouvelle dans ce contexte pour illustrer correctement la désactivation de l’enregistrement du graphe.

Les contrôles sont exécutés avec Node.js 24 et Microsoft Edge piloté par Playwright. Les captures du parcours dans `test-results/` sont des fichiers de vérification locaux, non publiés. Les vérifications du déploiement public sont effectuées séparément après la publication.

Le lanceur Windows a été corrigé et testé sans Node dans le PATH lors de la livraison précédente ; il est inchangé. Aucun test sur téléphone physique, Safari ou Firefox, ni audit formel par lecteur d’écran n’est revendiqué.

## Reproduire

```powershell
npm run validate
npm run validate:courses
npm test
npm run build
npm run test:browser
```

Si npm n’est pas dans le PATH, utiliser `node scripts/run.mjs` suivi du nom du script.


## Images et écoutes — 13 novembre 2026

Deux enregistrements réels sous CC BY 4.0, 18 WAV PCM16, 61 PNG calculés, cinq illustrations externes aux licences vérifiées ; attributions, modifications et fichiers sources conservés. Les schémas STFT à couleurs artificielles et mel qualitatif ont été retirés du cours Signal. Onze ateliers d’écoute et douze blocs d’images sont intégrés aux six modules.

Les tests médias recalculent crête, RMS, carré moyen, dBFS et facteur de crête depuis les octets PCM exportés ; ils vérifient aussi gain de 0,5, RMS commun, durée après rééchantillonnage et chemins GitHub Pages. Le contrôle navigateur couvre le décodage des images et WAV, l’absence de lecture automatique, le volume commun, l’arrêt de l’autre lecteur, le maintien de l’écoute lors d’un changement d’image et l’arrêt à la navigation. Les légendes distinguent références spectrales, dBFS et dB SPL. L’application ne lance aucun entraînement ou traitement scientifique en direct.

Les illustrations externes et les figures scientifiques représentatives sont inspectées ; des captures de l’interface finale sur ordinateur et à 360 px complètent ces contrôles. Les fichiers à régénérer et leurs dépendances sont décrits dans `docs/audio-lab.md`.


## Refonte entretien — lot A, 17 novembre 2026

Le module PyTorch contient vingt chapitres, dont six nouveaux ; le total passe à 71. Les 65 identifiants initiaux, leurs questions et leurs checkpoints sont protégés par `tests/revision-contracts.test.mjs`. Aucun QCM ajouté.

Les vingt programmes sont réellement exécutés sur PyTorch/TorchAudio 2.10.0+cpu, Python 3.11.9, avec un thread. Les versions publiées ont été vérifiées sur les pages de release officielles. Scripts : `scripts/verify/pytorch-existing.py` et `pytorch-additions.py`. Les JSON voisins conservent empreintes, sorties et assertions complémentaires. Le calcul demandé produit h=6, y=−6, L=36 et gradients 24/−72. Le programme complet effectue cinq époques puis un rechargement identique ; les pertes affichées sont celles enregistrées. Les cinq erreurs présentées sont réellement provoquées et corrigées. Le décalage de device est démontré avec meta/CPU, sans prétendre mesurer un GPU.

38 tests Node passent. L’audit de prose PyTorch ne trouve aucune phrase de plus de 30 mots, aucun dépassement de 1100 mots et aucune fin orale manquante. Les checkpoints historiques sont conservés et exclus de cette contrainte éditoriale. Commande : `node scripts/audit-prose.mjs --theme=pytorch --strict`.

L’audit CPU des autres modules est préparé dans `scripts/verify/existing-corpus.py`. Il a trouvé deux incohérences à corriger au lot F : tirage aléatoire VAE/diffusion décrit comme un bruit fixe. Le lot A ne les masque pas et n’est pas présenté comme la livraison finale du prompt complet.

Construction et 23 contrôles navigateur du lot A réussis, dont les 71 chapitres rendus à 360 px.


## Lot C — notebooks exécutables

Vingt notebooks Jupyter 4.5 exécutés de bout en bout, avec deux solutions supplémentaires vérifiées par document. Script : `scripts/verify/notebooks.py`. Résultats et empreintes du JSON écrit : `scripts/verify/notebooks-results.json`. Python 3.11.9, PyTorch/TorchAudio 2.10.0, CPU, un thread ; nbformat 5.11.1 et nbclient 0.11.0. Temps individuels mesurés : 5.391–8.222s, sous 120 s. Les notebooks livrés contiennent les sorties réellement obtenues. Les exercices ne cassent pas l’exécution complète : leurs trous sont dans des cellules Markdown.

Les notebooks sont vérifiés localement avec Jupyter. L’interface Colab connectée n’est pas exécutée par l’agent ; ses URL et les fichiers GitHub publics sont contrôlés après push. Cette limite ne remplace pas le contrôle CPU de toutes les cellules.

Lot C : 40 tests Node, construction Vite et 24 contrôles navigateur réussis.

Les vingt sources GitHub ont été retrouvées au commit `0ec5874`. Un GET du lien Colab PyTorch retourne HTTP 200 et une interface proposant la connexion. Le détail et la limite d’accès sont enregistrés dans `scripts/verify/notebook-links.json`.

## Lot B — génération et contrôle

Six chapitres ajoutés, 77 au total, sans modifier les 200 QCM. Scripts CPU exécutés : `scripts/verify/b-attention-control.py`, `b-codecs-symbolic.py`, `b-diffusion-efficiency.py`. Les rapports `*-results.json` relient les codes affichés à leurs empreintes et sorties. Python 3.11.9, torch 2.10.0+cpu, un thread.

Le test causal vérifie un écart nul dans le passé après modification du futur ; sans masque, l’écart est 0,204499. Les interfaces multimodales vérifient leurs formes, sans prétendre charger CLAP. La RVQ miniature reconstruit ses valeurs avec une erreur quadratique moyenne de 0,006250. La quantification compare des projections synthétiques ; ni qualité perceptive, ni mémoire résidente, ni accélération ne sont mesurées.

Validation des cours, 43 tests Node, construction et 25 contrôles navigateur réussis. Les 77 chapitres passent le contrôle de rendu à 360 px ; les liens techniques ouvrent les bonnes cibles. Les six nouveaux chapitres respectent les limites de prose et terminent par une formulation orale.

## Lot D — contexte et recherche

Quatre chapitres ajoutés, 81 au total. Les références du nouveau module correspondent à des pages réellement ouvertes du registre documentaire de 37 sources. Les huit lectures ont chacune trois idées et une question de recherche. Chaque chapitre relie des mécanismes techniques existants. Aucun résultat de projet ou usage personnel n’est inventé.

Validation, 45 tests Node et construction réussis. Les 25 contrôles navigateur passent, dont le rendu des 81 chapitres à 360 px et la construction sous le sous-répertoire de publication. Une valeur fixe de six cartes dans ce dernier contrôle a été remplacée par le nombre de modules enregistrés.
