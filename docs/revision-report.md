# Rapport de révision du 18 novembre 2026

107 chapitres dans huit modules : 42 nouveaux et 65 historiques retravaillés. Aucun QCM ajouté ; la banque conserve ses 200 questions.

## Chapitres créés

### pytorch

- **PyTorch en une page** — `pytorch-en-une-page`.
- **Rétropropagation à la main** — `retropropagation-a-la-main`.
- **Optimiseurs, taux d’apprentissage et régularisation en pratique** — `optimiseurs-regularisation-pratique`.
- **Une boucle d’entraînement complète** — `boucle-entrainement-complete`.
- **Conv2d sur un spectrogramme mel et autoencodeur** — `conv-mel-autoencodeur`.
- **Quand ça plante : lire une erreur PyTorch** — `lire-erreurs-pytorch`.

### audio-ml

- **Assembler l’attention en Transformer** — `transformer-complet`.

### generation-controle

- **Transporter un son par corrections successives : les codecs neuronaux** — `codecs-neuronaux-rvq`.
- **Écrire les gestes ou produire le son : symbolique, audio, ou les deux ?** — `symbolique-midi-et-audio`.
- **Choisir comment les commandes entrent dans le modèle** — `controle-multimodal-formes`.
- **Quelle cible apprendre pour retirer le bruit ?** — `objectifs-diffusion-et-flow`.
- **Choisir ce que notre budget doit réellement économiser** — `efficacite-petit-budget`.

### Contexte et recherche

- **Lire l’offre comme une question de recherche** — `lire-offre-et-se-preparer`.
- **Situer les outils entre modèle, son et composition** — `outils-ircam-et-pratiques-musicales`.
- **Après la génération : reprendre la main sur le résultat** — `postgenai-et-interaction`.
- **Huit lectures pour construire une discussion** — `huit-lectures-pour-discuter`.

### Entretien

- **Comment construiriez-vous une boucle PyTorch pour classer des extraits sonores ?** — `oral-boucle-pytorch`.
- **Comment expliqueriez-vous la rétropropagation sans vous limiter à appeler backward ?** — `oral-autograd`.
- **Comment traiteriez-vous ensemble des sons de durées différentes ?** — `oral-batches-masques`.
- **Pourquoi utiliser à la fois model.eval et no_grad pendant la validation ?** — `oral-evaluation-pytorch`.
- **Face à une erreur PyTorch, quelle serait votre méthode de diagnostic ?** — `oral-diagnostic-pytorch`.
- **Comment compareriez-vous les niveaux d'une voix et d'une percussion ?** — `oral-niveaux-audio`.
- **Pourquoi choisir une STFT ou un spectrogramme mel pour représenter un son ?** — `oral-stft-mel`.
- **Pourquoi un spectrogramme visuellement correct ne garantit-il pas un son bien reconstruit ?** — `oral-phase-reconstruction`.
- **Comment réuniriez-vous des fichiers audio possédant différentes fréquences d'échantillonnage ?** — `oral-reechantillonnage`.
- **Qu’ajoute un Transformer à une simple couche d’attention ?** — `oral-attention-transformer`.
- **Pourquoi générer des codes audio plutôt que directement une onde ?** — `oral-codecs-rvq`.
- **Comment entraîner puis utiliser un modèle autorégressif musical ?** — `oral-autoregression`.
- **Que gagne-t-on avec un VAE, et que faut-il surveiller dans son latent ?** — `oral-vae`.
- **Quelle différence feriez-vous entre un objectif DDPM et le flow matching ?** — `oral-diffusion-flow`.
- **Comment fonctionne la guidance sans classifieur, et pourquoi limiter sa force ?** — `oral-guidance`.
- **Comment combiner texte, référence audio et partition pour contrôler une génération ?** — `oral-controle-multimodal`.
- **Comment adapter un générateur au petit corpus d’un compositeur ?** — `oral-adaptation`.
- **Que vérifier avant d’annoncer qu’un modèle audio fonctionne avec peu de calcul, en temps réel ?** — `oral-budget-temps-reel`.
- **Comment transformeriez-vous une idée de modèle en expérience de recherche ?** — `oral-protocole-recherche`.
- **Comment vérifier qu’un modèle généralise à de nouveaux matériaux musicaux ?** — `oral-fuites-et-generalisation`.
- **Comment organiseriez-vous une évaluation perceptive d’un générateur audio contrôlable ?** — `oral-evaluation-perceptive`.
- **Pourquoi souhaiteriez-vous mener cette recherche à l’IRCAM ?** — `oral-motivation-ircam`.
- **Comment construiriez-vous un dialogue de travail avec une compositrice ou un compositeur ?** — `oral-dialogue-compositeur`.
- **Que feriez-vous si votre méthode ne dépassait pas une référence simple ?** — `oral-echec-et-incertitude`.
- **Quand choisiriez-vous une génération symbolique, audio ou hybride ?** — `oral-symbolique-ou-audio`.
- **Un pitch de recherche hypothétique : reprendre localement les matériaux d’un musicien** — `pitch-recherche-deux-minutes`.

## Chapitres historiques modifiés

Les identifiants, questions, sources d’origine et checkpoints sont conservés. Les modifications portent sur les explications, la progression et les conclusions.

### python-scientifique

- **Notre mission : préparer des sons pour les classer** — `du-son-aux-donnees`.
- **Un tableau pour calculer sur tous les échantillons** — `tableaux-et-indexation`.
- **Garder un original quand on modifie un signal** — `references-et-copies`.
- **Mesurer chaque extrait, sans mélanger les fichiers** — `reduire-les-bons-axes`.
- **Appliquer une correction, puis comparer des observations** — `broadcasting-et-algebre`.
- **Fixer une échelle pour les futurs fichiers** — `standardiser-et-preserver-precision`.
- **Une fonction dont on peut vérifier le contrat** — `fonctions-et-arguments`.
- **Quand deux appels partagent une liste sans le vouloir** — `valeurs-par-defaut`.
- **Filtrer un corpus sans décaler ses cibles** — `parcourir-et-filtrer`.
- **Conserver les métadonnées et les réglages** — `lire-fonctions-objets`.
- **Du fichier au modèle : vérifier toute la chaîne** — `assembler-pipeline-scientifique`.
- **Rappel facultatif : valeurs calculées et unités** — `valeurs-noms-et-calculs`.
- **Rappel facultatif : indices et plages** — `listes-et-indices`.

### audio-signal

- **Partir de deux vrais sons et retrouver leurs secondes** — `echantillons-duree-canaux`.
- **Mettre les fichiers à la même cadence sans changer les sons** — `nyquist-repliement-reechantillonnage`.
- **Comparer le niveau de la voix et de la percussion** — `amplitude-puissance-decibels`.
- **Découvrir les fréquences cachées dans la courbe** — `fourier-coefficients-frequences`.
- **Voir les syllabes et les attaques de caisse claire** — `stft-fenetres-hop-trames`.
- **Choisir une fenêtre pour la question posée** — `resolution-fuite-zero-padding`.
- **Alléger l’entrée avec des bandes mel** — `mel-representation-compressee`.
- **Vérifier ce que le passage en mono peut annuler** — `phase-canaux-annulations`.
- **Réécouter pour vérifier, puis envisager le direct** — `reconstruction-streaming-limites`.

### pytorch

- **Des mesures à une décision** — `du-pipeline-au-modele`.
- **Décrire un tenseur avant de calculer** — `tenseur-forme-type-device`.
- **Changer les axes sans mélanger les extraits** — `organiser-les-axes`.
- **Choisir l’axe qui répond à notre question** — `selection-diffusion-reduction`.
- **Assembler des séquences de durées différentes** — `dataset-et-batches`.
- **Ne moyenner que les valeurs observées** — `moyennes-masquees`.
- **Enregistrer la règle et son état** — `construire-un-module`.
- **Donner un coût à la mauvaise préférence** — `choisir-la-perte`.
- **Calculer une pente sans déplacer le poids** — `autograd-et-derivees`.
- **Transformer un gradient en un pas** — `une-iteration-entrainement`.
- **Évaluer avec deux interrupteurs indépendants** — `entrainer-ou-evaluer`.
- **Conserver une mesure sans garder son graphe** — `detacher-geler-journaliser`.
- **Donner le bon poids à chaque exemple** — `moyennes-et-microbatches`.
- **Sauvegarder ce qui permet de reprendre** — `sauvegarder-et-reprendre`.

### audio-ml

- **Choisir la réponse avant de choisir le réseau** — `tache-cibles-pertes`.
- **Garder le même sens des valeurs, du train au nouveau fichier** — `pretraitement-entrees-coherentes`.
- **Assembler des durées variables sans inventer du silence** — `durees-padding-masques`.
- **Construire une première référence avec un encodeur gelé** — `embeddings-transfert-domaines`.
- **Choisir ce que le modèle doit pouvoir observer** — `architectures-axes-contexte`.
- **Apprendre avec une présence de fichier sans inventer ses instants** — `annotations-faibles-agregation`.
- **Faire varier le son tout en gardant une cible honnête** — `augmentations-cibles-validation`.
- **Cacher une preuve partielle ou mélanger deux exemples** — `masquage-mixup-representations`.
- **Comparer deux sons, puis réunir leur contexte** — `similarites-contraste-attention`.

### generation-controle

- **Garder le caractère d’une frappe avant d’en inventer une autre** — `representation-et-reconstruction`.
- **Donner un vocabulaire à notre générateur** — `quantification-et-tokens`.
- **Continuer une percussion sans regarder la réponse** — `autoregression-et-causalite`.
- **Obtenir plusieurs variantes sans perdre le motif** — `echantillonnage-contexte-et-cout`.
- **Demander un accent à trois secondes** — `conditions-et-intention-musicale`.
- **Une autre piste : varier autour d’une représentation continue** — `vae-et-echantillonnage`.
- **Vérifier que le latent sert encore à varier la frappe** — `kl-et-latent-inutilise`.
- **Apprendre à retrouver une frappe à travers le bruit** — `diffusion-et-bruit`.
- **Renforcer une commande et garder le début joué** — `guidance-et-zones-connues`.
- **Retrouver le timbre du corpus sans tout réentraîner** — `adaptation-lora-et-petit-corpus`.

### evaluation-recherche

- **Écrire ce qui ferait adopter la nouvelle version** — `question-de-recherche-et-baseline`.
- **Pouvoir retrouver la version qui a produit un son** — `environnement-linux-et-traces`.
- **Réserver de vraies nouvelles prises** — `splits-et-fuites`.
- **Compter les bons événements, avec le bon dénominateur** — `metriques-et-seuils`.
- **Ne pas fausser le résultat en le rassemblant** — `boucle-evaluation-et-surapprentissage`.
- **Savoir quelle modification aide notre instrument** — `baselines-et-ablations`.
- **Faire entendre la différence sans suggérer la réponse** — `ecoute-et-jugement-perceptif`.
- **Ce que voit une distance audio, et ce qu’elle laisse passer** — `fad-et-limites-des-proxies`.
- **Le gain tient-il quand on recommence ?** — `variabilite-et-incertitude`.
- **Choisir une version, puis dire où la conclusion tient** — `generalisation-et-compte-rendu`.

## Livrables et vérifications

- Vingt notebooks, quarante exercices et solutions ; cellules et solutions réellement exécutées sur CPU.
- Module Contexte avec huit lectures, module Entretien avec 25 questions et un pitch, glossaire de 160 termes.
- Parcours rapide : neuf chapitres signalés et quatre semaines de priorités.
- Validation des cours, 51 tests Node, construction et 28 contrôles navigateur.
- Audit strict des 107 chapitres et preuve CPU correspondant à chacun des 74 blocs Python affichés.

## Adaptations explicites et limites

- Colab : URL publique et sources GitHub vérifiées ; aucune session Colab authentifiée disponible. Les vingt notebooks sont exécutés localement, avec sorties enregistrées.
- R1 : les sections de contexte utilisent des tableaux de raisonnement ; les questions d’entretien utilisent des réponses modèles. Les formats sont explicitement identifiés, sans code artificiel.
- V6 : le chapitre des niveaux conserve une longueur supérieure, justifiée et annoncée, afin de relier définitions, échelles et écoutes réelles.
- Les checkpoints historiques restent inchangés conformément à V5 ; leur texte est exclu de la réécriture des phrases.
- Aucun résultat de grand modèle audio ou gain matériel n’a été inventé. Le compromis coût/erreur est une expérience numérique pédagogique.

Aucun axe A–F n’est laissé sans livrable. Les limites ci-dessus précisent ce qui a effectivement été vérifié. Voir `VERIFICATION.md` pour les preuves et les commandes.
