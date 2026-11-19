# Rapport de l’audit pédagogique — 19 novembre 2026

Cette révision applique l’audit transmis le 18 novembre au site de préparation à l’entretien IRCAM. Le point de départ est le commit `57fce919006dcf1edbf6aeadd4eb67f54d657453`, avec huit modules et 107 chapitres.

Le contenu compte désormais **120 chapitres**, **32 notebooks PyTorch** et les **200 questions de quiz d’origine**. Les 107 ancres de départ restent présentes. Douze chapitres PyTorch et un chapitre Apprentissage audio ont été ajoutés pour séparer des difficultés auparavant réunies.

## Changements transversaux

Les cours supposent la pratique du Python algorithmique. Les explications portent sur les conventions scientifiques nouvelles : provenance des nombres, axes, contrats, arguments, valeurs intermédiaires et mutations. Les rappels élémentaires restent disponibles sans ralentir le parcours principal.

Les exemples guidés suivent des opérations plus fines. Les détails locaux peuvent montrer un calcul, son explication et son état. Les lignes surlignées ont été rapprochées de l’action décrite. Les programmes autonomes et les extraits sont distingués ; les objets et fichiers requis sont annoncés avant le code.

Six laboratoires interactifs rendent visibles les axes d’argmax, reshape/transpose, le broadcasting, les produits de Linear, les gradients et la convolution. Ils calculent en JavaScript et l’annoncent. Le padding et les moyennes masquées restent expliqués par les tableaux et le code ; le laboratoire de padding disponible dans le composant n’est pas inséré dans les cours. Ces interactions ne constituent pas une exécution de PyTorch dans la page.

Les doublons exacts entre résultat et paragraphe, les traces de vérification dans le récit et les finales orales automatiques ont été retirés. Les questions de transfert peuvent demander une prédiction ou un diagnostic, avec une explication propre à l’option choisie. Les anciennes réponses sont invalidées lorsqu’une question change.

Les repères « lu », « à revoir », les étapes guidées et la reprise de lecture sont enregistrés séparément du quiz. Les anciennes données compatibles sont conservées. Les niveaux indiquent ce qu’il faut pratiquer, savoir discuter ou approfondir.

## Bilan par module

| Module | Chapitres | Révision principale |
| --- | ---: | --- |
| Python scientifique | 13 | Décomposer indexations, `None`, copies, `@`, réductions et diffusion ; expliquer formes et mutations avant les calculs. |
| Signal audio | 9 | Introduire fichiers, fenêtres, hop et FFT avant les calculs ; distinguer les échelles et conserver les médias réels commentés. |
| PyTorch | 32 | Construire rapidement une boucle minimale, puis séparer axes, données variables, masques, optimisation, buffers et convolutions. |
| Apprentissage audio | 11 | Clarifier les contrats de tâches et d’extraits ; séparer contraste et attention ; présenter le Transformer par étapes. |
| Génération et contrôle | 15 | Expliquer états et objectifs avant les transformations ; distinguer mécanisme miniature et modèle appris. |
| Évaluation et recherche | 10 | Construire une comparaison stable ; préciser unités, hypothèses et limites des données fabriquées. |
| Contexte IRCAM et recherche | 4 | Relier informations et lectures à des questions techniques argumentables. |
| Entretien | 26 | Proposer des pistes progressives avant les réponses modèles, puis des relances possibles. |

### Python scientifique

Les tableaux deviennent des objets dont on suit les cases, les axes et les changements. Une indexation avancée ou une réduction est précédée de son besoin et de son effet attendu. Les étapes locales explicitent notamment l’ajout d’un axe avec `None`, les produits et les moyennes. Les variations servent à observer une différence précise, sans imposer le même gabarit à chaque chapitre.

### Signal audio

Les fichiers nécessaires sont téléchargeables avant les programmes qui les lisent. Le nom de fichier, le dossier, le segment et le taux d’échantillonnage sont annoncés. Le signal source analysé peut différer du dérivé proposé à l’écoute ; leurs conventions sont distinguées.

Les ateliers d’écoute, images d’analyse et illustrations existants restent conservés. La fenêtre, le pas et la FFT sont introduits avant les transformations ; les normalisations spécialisées peuvent être abordées ensuite. Les niveaux relient amplitude, puissance, RMS et décibels aux mesures et à leur interprétation.

### PyTorch

Le socle garde un petit tableau de trois exemples fictifs. Les nombres sont choisis, les scores et cibles sont présentés avant leur utilisation, puis les calculs de Linear et de perte deviennent vérifiables à la main. La rétropropagation explique les gradients avant la première mise à jour.

Une première boucle arrive avant Dataset, padding et les dispositifs avancés. Les formes variables, l’axe ajouté, l’empilement, la concaténation et les masques ont leurs propres étapes. La suite distingue journalisation, gel, accumulation, reprise d’Adam, clipping, scheduler et CUDA/AMP.

Les convolutions commencent par un noyau calculable. La préparation mel est séparée de l’autoencodeur. Les signaux de 220 et 440 Hz sont nommés comme des ondes synthétiques, sans les présenter comme des fichiers de voix. L’exemple complet montre une chaîne cohérente sans prétendre entraîner un modèle audio représentatif.

### Apprentissage audio

Les tâches et représentations sont reliées à leurs contrats de forme. Les exemples de transfert, augmentation, mixup et attention disposent d’un contexte exécutable déclaré. Le nouveau chapitre `similarite-cosinus-et-contraste` isole les comparaisons de vecteurs. L’ancre historique `similarites-contraste-attention` reste disponible pour l’attention.

Le Transformer est présenté en étapes, plutôt que comme une liste de briques apparues simultanément. Les programmes n’utilisent pas une réussite fictive de modèle préentraîné comme preuve de qualité.

### Génération, évaluation, contexte et oral

Les mécanismes de quantification, RVQ, VAE, autorégression, diffusion et flow partent de conventions et de nombres explicités. Les prédictions fixées et les décodeurs identités sont annoncés comme dispositifs pédagogiques. Les transformations et variations ont été exécutées sur CPU.

Les exemples d’évaluation distinguent décisions fabriquées, protocole et conclusion possible. Un intervalle bootstrap sur ces données n’atteste pas une meilleure génération musicale. Le contexte garde les références primaires et les questions de lecture. Les 25 questions orales et le pitch proposent des pistes avant l’ouverture du modèle de réponse.

## Nouveaux chapitres

Les douze ajouts PyTorch sont :

- `premiere-boucle-minimale` ;
- `broadcasting-pas-a-pas` et `filtrer-et-preserver-les-cibles` ;
- `ajouter-retirer-un-axe` et `concatener-ou-empiler` ;
- `padding-et-collate` ;
- `convolution-a-la-main` et `preparer-mel-pour-conv` ;
- `pertes-multi-etiquettes` et `modules-et-buffers` ;
- `scheduler-et-arret-anticipe` et `cuda-amp-memoire`.

L’ajout Apprentissage audio est `similarite-cosinus-et-contraste`. Aucun ancien identifiant de chapitre n’est supprimé.

## Couverture du quiz et compatibilité

La banque conserve ses 200 questions, leurs identifiants et leur thème principal. Les sources d’origine restent présentes. Quinze questions rejoignent un chapitre plus ciblé :

| Questions | Ancien chapitre | Destination actuelle |
| --- | --- | --- |
| `pt-006`, `pt-007` | `organiser-les-axes` | `ajouter-retirer-un-axe` |
| `pt-020`, `pt-021` | `organiser-les-axes` | `concatener-ou-empiler` |
| `pt-019` | `selection-diffusion-reduction` | `filtrer-et-preserver-les-cibles` |
| `pt-023` | `selection-diffusion-reduction` | `broadcasting-pas-a-pas` |
| `pt-028`, `pt-038` | `dataset-et-batches` | `padding-et-collate` |
| `pt-027` | `construire-un-module` | `convolution-a-la-main` |
| `pt-034`, `pt-035` | `construire-un-module` | `modules-et-buffers` |
| `pt-026` | `choisir-la-perte` | `pertes-multi-etiquettes` |
| `pt-049` | `une-iteration-entrainement` | `optimiseurs-regularisation-pratique` |
| `aml-025`, `aml-029` | `similarites-contraste-attention` | `similarite-cosinus-et-contraste` |

Le registre machine est `scripts/verify/audit-question-moves.json`. Les liens provenant du quiz utilisent cette couverture actuelle ; les anciennes ancres restent des destinations valides.

## Notebooks et preuves

Les 32 chapitres PyTorch possèdent chacun leur notebook progressif. Les cellules conservent exactement les 38 programmes du cours, sans couper une instruction composée. Des cellules distinctes affichent les états utiles ; leurs observations sont limitées au programme courant.

Les 64 exercices sont de véritables cellules de code prêtes à éditer. À vide, ils indiquent « À compléter ». Ils n’annoncent pas un succès artificiel pour préserver « Tout exécuter ». Deux indices sont repliés avant les deux solutions en fin de document. Les solutions complètes sont exécutées par le vérificateur puis retirées des cellules de contrôle temporaires.

Les quatre scripts courants ont réussi **107 cas CPU**, comprenant 104 programmes et trois variantes explicites. Les 32 notebooks ont exécuté **654 cellules de code et 64 solutions**, avec sorties conservées. Les durées vont de 6,182 à 11,872 secondes par notebook ; le total final est 242,212 secondes. Les deux documents resynchronisés après les derniers paragraphes ont été réexécutés. Les 59 tests unitaires passent.

Les rapports de référence sont :

- `scripts/verify/audit-pytorch-core-results.json` : 19 cas ;
- `scripts/verify/audit-pytorch-advanced-results.json` : 19 cas ;
- `scripts/verify/audit-python-signal-ml-results.json` : 38 cas ;
- `scripts/verify/audit-generation-research-oral-results.json` : 31 cas ;
- `scripts/verify/notebooks-results.json` : 32 notebooks et leurs preuves ;
- `scripts/verify/all-results.json` : quatre commandes réussies, sans relance des notebooks lors de ce passage.

Les conditions et commandes sont détaillées dans `../VERIFICATION.md`. `scripts/verify/prose-audit.json` a été régénéré sur les 120 chapitres comme aide à la lecture, sans imposer les anciennes finales orales. Les archives du premier lot à 107 chapitres et 20 notebooks restent historiques ; elles ne remplacent pas ces preuves.

## Limites et livraison

La vérification est locale, sur Python 3.11.9 et PyTorch/TorchAudio 2.10.0 CPU. Les branches CUDA/AMP n’ont pas été exécutées sur GPU. Aucune session Colab authentifiée n’a exécuté ces notebooks. Aucun entraînement externe, benchmark perceptif ou gain de vitesse réel n’est revendiqué.

Les enregistrements du laboratoire sont réels ; les petits tableaux PyTorch, les données de classification et d’évaluation sont choisis. Les ondes de 220 et 440 Hz sont synthétiques. Leurs conclusions sont limitées au calcul illustré.

### Bilan navigateur final

État au 19 novembre 2026 : **59 tests unitaires, construction et 33 contrôles Edge réussis sur les fichiers finaux**.

Le responsable de livraison a contrôlé les 120 chapitres à 360 px sans débordement, le clavier, le feedback, la restauration des étapes et des réponses, et les positions après changement de taille du texte ou de mode lecture. Les pistes orales ont été vérifiées avant l’ouverture du modèle. L’audio réel, la construction sous un sous-chemin et les captures desktop/mobile ont été inspectés.

La vérification de reflow utilise 720 pixels CSS et une police racine à 200 %. Le zoom natif du navigateur n’est pas attesté. La relance finale a réussi après le dernier ajustement de libellé. Les journaux locaux sont `.tools/audit-unit.log`, `.tools/audit-build.log` et `.tools/audit-browser.log`, ignorés par Git. Les captures desktop et mobile inspectées restent dans `test-results/`.

### Publication vérifiée

État au 19 novembre 2026 : **publication et contrôle public réussis**.

- Commit applicatif `3bbeb56fe13e06efd74f37ec3c59634bfd2dc348`, poussé sur `main`.
- [Workflow Pages 44442432394 réussi](https://github.com/RadioCodeur/quiz/actions/runs/44442432394) pour ce commit.
- [Cours publiés](https://radiocodeur.github.io/quiz/cours.html) : huit modules, 120 chapitres et 32 notebooks comparés aux fichiers locaux ; glossaire de 160 termes également identique.
- Quiz, catalogue, axes interactifs, pistes orales et glossaire contrôlés dans Edge sur la version publique à 360 px ; aucune exception ni réponse HTTP en erreur.
- Les 32 notebooks publics répondent HTTP 200 avec le contenu attendu. Les liens Colab sont vérifiés localement ; aucune session Colab authentifiée n’a été exécutée.

Le contrôle `node scripts/verify-public.mjs` a été exécuté avec le SHA et l’URL ci-dessus après réussite du workflow. Son rapport `test-results/audit-public-verification.json` conserve les résultats et `errors: []` ; il est local et ignoré par Git. Les commandes complètes figurent dans `../VERIFICATION.md`.
