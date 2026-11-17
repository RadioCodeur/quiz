# Plan de révision — 17 novembre 2026

## Demande et contrat

Appliquer le prompt fourni dans `Texte collé.txt`, lots A, C, B, D, E, F dans cet ordre. La banque reste à 200 QCM : aucun ajout n’est nécessaire pour cette refonte. Les 65 identifiants initiaux, questionIds, sourceIds et checkpoints sont conservés. Les nouveaux chapitres reçoivent de nouveaux identifiants. Les sons, images et lecteurs existants restent disponibles. Le site n’exécute aucun Python.

Les fichiers imposés ont été lus avant ce plan : `src/courses.js`, `src/learning-blocks.js`, `src/course-model.js`, `scripts/validate-courses.mjs`, `docs/cours.md`. La branche de départ est main, commit bc35492, sans modification locale.

## A — PyTorch

- Réécrire les 14 chapitres existants avec le besoin, un calcul miniature, le code, sa lecture, un piège, une phrase orale.
- Ajouter six chapitres : `pytorch-en-une-page`, `retropropagation-a-la-main`, `boucle-entrainement-complete`, `lire-erreurs-pytorch`, `optimiseurs-regularisation-pratique`, `conv-mel-autoencodeur`.
- Placer le panorama avant `du-pipeline-au-modele`, puis la rétropropagation après `autograd-et-derivees`. La boucle complète réunit les briques après leur introduction.
- Exécuter les exemples en CPU. Capturer les cinq véritables messages d’erreur. Les exemples CUDA et précision mixte possèdent un chemin CPU : aucune mesure GPU ne sera inventée.
- Garder les subtilités dans des encadrés et les nombres réels dans `scripts/verify/`.
- Contrôles des cours, tests, construction, navigateur ; commit A.

## C — Notebooks

- Créer vingt notebooks dans `public/notebooks/`, un pour chaque chapitre PyTorch, ancien ou nouveau.
- Chaque notebook : versions, cellules complètes, deux exercices à trous, solutions repliées en fin de document.
- Liens de téléchargement et Colab depuis les chapitres. Vérifier les URL du dépôt public après push.
- Exécuter chaque notebook entièrement sur CPU et mesurer sa durée ; seuil de 120 secondes par notebook. Aucun téléchargement de modèle ou dataset externe requis.
- Contrôles et commit C.

## B — Audio ML et génération

- Ajouter `transformer-complet` dans Audio ML.
- Ajouter dans Génération : `codecs-neuronaux-rvq`, `objectifs-diffusion-et-flow`, `controle-multimodal-formes`, `efficacite-petit-budget`, `symbolique-midi-et-audio`.
- Définir position, normalisation, multi-têtes, causalité, RVQ, pertes, DDPM, guidance, flux, latent, CLAP, MIDI, FiLM et adaptations au point d’usage.
- Exemples de formes et de coûts réellement calculés. Les coûts analytiques sont distingués d’une mesure de temps ou de qualité.
- Sources primaires effectivement ouvertes : articles et dépôts officiels RAVE, EnCodec, DAC, Transformer, CLAP, LoRA, flow matching et Music Transformer.
- Contrôles et commit B.

## D — Contexte et recherche

- Ajouter le module `contexte-recherche` : offre et couverture ; outils IRCAM ; PostGenAI et interaction après génération ; huit lectures commentées.
- Chaque chapitre donne des liens vers les chapitres techniques utiles. Vérifier l’offre IRCAM et les pages officielles des projets avant rédaction.
- Étendre le registre de modules, sans transformer les deux nouveaux modules en thèmes de QCM.
- Contrôles et commit D.

## E — Oral et glossaire

- Ajouter le module `entretien` avec 25 questions ouvertes : chaque réponse modèle compte environ 150 à 225 mots, soit 60–90 secondes à débit indicatif.
- Pour chaque question : trois points, un piège, une relance. Un chapitre supplémentaire contient un pitch modèle et un gabarit de deux minutes, sans biographie inventée.
- Le format oral utilise les blocs autorisés ; il ne forcera pas un programme artificiel pour parler de motivation. Cette adaptation sera explicite dans les validateurs.
- Glossaire FR–EN d’au moins 120 entrées, page accessible depuis tous les headers.
- Contrôles et commit E.

## F — Parcours et audit final

- Indicateurs de parcours rapide, chapitres Python/Signal survolables et planning de quatre semaines PyTorch → Audio ML → Génération → Évaluation → Entretien.
- Tout walkthrough sans code est complété ou nommé et justifié comme tableau de calcul raisonné.
- Audit de longueur : environ 1100 mots hors code maximum, justification explicite des exceptions. Audit des phrases de plus de 30 mots, de l’oral final et des définitions FR–EN.
- Exécuter les blocs Python de tous les cours avec les contextes nécessaires ; conserver les scripts, résultats, versions et limites dans `scripts/verify/` et `VERIFICATION.md`.
- Vérifier conservation des identifiants, correspondances et checkpoints contre la version initiale.
- Exécuter validate:courses, npm test, build et test:browser. Inspecter ordinateur/mobile, notebooks, glossaire et nouveaux parcours. Commit F, push, déploiement Pages et contrôle public.

## Suivi des limites et des preuves

La dernière version de PyTorch ne sera pas déduite de mémoire. L’environnement possède torch et torchaudio 2.10.0 ; leur caractère publié sera vérifié avant de fixer les versions des notebooks. Les temps CPU seront mesurés ici, avec conditions indiquées. Ils ne garantissent pas la même durée sur tout matériel.

L’accès à l’interface Colab connectée n’est pas supposé. L’URL publique et le notebook source seront vérifiés ; l’exécution CPU locale couvre toutes les cellules. Toute impossibilité réelle sera notée ici, avec son impact, sans remplacer silencieusement le besoin.

## État des lots

- [x] A — PyTorch : vingt chapitres, preuves CPU, 38 tests et 23 contrôles navigateur réussis.
- [x] C — Notebooks : vingt documents et quarante solutions exécutés ; 40 tests et 24 contrôles navigateur réussis.
- [x] B — Six chapitres ajoutés, preuves CPU ; 43 tests et 25 contrôles navigateur réussis.
- [x] D — Quatre chapitres, huit lectures et liens techniques ; 45 tests et 25 contrôles navigateur réussis.
- [x] E — 25 réponses, pitch et glossaire de 160 termes ; 48 tests et 27 contrôles navigateur réussis.
- [x] F — Parcours rapide, neuf tableaux justifiés, audit des 107 chapitres et exécutions CPU complètes ; 51 tests et 28 contrôles navigateur réussis.

## Adaptations appliquées

Les sections de contexte emploient des tableaux de raisonnement. L’oral emploie des réponses modèles et un gabarit personnel, sans imposer de code artificiel. Le chapitre des niveaux conserve sa profondeur avec une justification de longueur affichée. Les checkpoints historiques restent inchangés conformément à V5.

Les vingt sources de notebooks sont publiques. Le lien Colab a répondu HTTP 200 ; aucune session Colab authentifiée n’a été disponible. Les vingt notebooks et leurs quarante solutions ont donc été vérifiés dans de vrais noyaux CPU locaux. Les rapports et temps individuels sont conservés.

Les deux bruits aléatoires incompatibles avec les calculs manuels VAE/diffusion ont été fixés puis réexécutés. La relecture finale a aussi rendu les conclusions orales prononçables et développé CLAP au premier usage.

La liste exhaustive des 42 créations et 65 chapitres historiques révisés est dans `docs/revision-report.md`. Les preuves, limites et commandes finales sont dans `VERIFICATION.md`. Le commit final est ensuite poussé et le workflow manuel Pages est contrôlé jusqu’à sa fin.
