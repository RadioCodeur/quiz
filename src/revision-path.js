export const QUICK_CHAPTERS = [
  {themeId:'python-scientifique',chapterId:'fonctions-et-arguments',condition:'Si vous savez distinguer un argument positionnel et un argument nommé.'},
  {themeId:'python-scientifique',chapterId:'valeurs-par-defaut',condition:'Si vous savez expliquer le piège d’une liste utilisée comme valeur par défaut.'},
  {themeId:'python-scientifique',chapterId:'parcourir-et-filtrer',condition:'Si enumerate, zip et les compréhensions vous sont familiers.'},
  {themeId:'python-scientifique',chapterId:'lire-fonctions-objets',condition:'Si vous savez lire une fonction, une instance et ses attributs.'},
  {themeId:'python-scientifique',chapterId:'valeurs-noms-et-calculs',condition:'Si l’affectation et les calculs Python sont déjà acquis.'},
  {themeId:'python-scientifique',chapterId:'listes-et-indices',condition:'Si vous maîtrisez les indices, les tranches et les pas.'},
  {themeId:'audio-signal',chapterId:'echantillons-duree-canaux',condition:'Si vous savez retrouver durée, fréquence d’échantillonnage et axe des canaux.'},
  {themeId:'audio-signal',chapterId:'stft-fenetres-hop-trames',condition:'Si vous savez expliquer une fenêtre, le pas entre trames et les deux axes d’une STFT.'},
  {themeId:'audio-signal',chapterId:'mel-representation-compressee',condition:'Si vous savez distinguer spectre, puissance, filtres mel et affichage logarithmique.'},
];

export const REVISION_WEEKS = [
  {title:'Semaine 1 · Prendre PyTorch en main',goal:'Priorité à la chaîne données → modèle → perte → gradients → mise à jour.',links:[
    {text:'La carte de PyTorch',themeId:'pytorch',chapterId:'pytorch-en-une-page'},
    {text:'Former les lots',themeId:'pytorch',chapterId:'dataset-et-batches'},
    {text:'Remonter deux poids à la main',themeId:'pytorch',chapterId:'retropropagation-a-la-main'},
    {text:'Réunir la boucle complète',themeId:'pytorch',chapterId:'boucle-entrainement-complete'},
  ],deliverable:'Sans le modèle, réécrire une boucle CPU et expliquer chaque étape. Faire les exercices des notebooks quand une brique reste fragile.'},
  {title:'Semaine 2 · Relier les modèles aux sons',goal:'Passer d’une tâche claire aux représentations et au contexte temporel.',links:[
    {text:'Définir les cibles',themeId:'audio-ml',chapterId:'tache-cibles-pertes'},
    {text:'Traiter les durées variables',themeId:'audio-ml',chapterId:'durees-padding-masques'},
    {text:'Choisir une architecture',themeId:'audio-ml',chapterId:'architectures-axes-contexte'},
    {text:'Construire le Transformer',themeId:'audio-ml',chapterId:'transformer-complet'},
    {text:'Relier mel et autoencodeur',themeId:'pytorch',chapterId:'conv-mel-autoencodeur'},
  ],deliverable:'Dessiner les formes de tenseurs du son jusqu’à la sortie. Revenir au Signal si un axe, une échelle ou une transformation reste floue.'},
  {title:'Semaine 3 · Générer sous une intention',goal:'Choisir une représentation, un contrôle et une adaptation selon le besoin musical.',links:[
    {text:'Comprendre les codecs',themeId:'generation-controle',chapterId:'codecs-neuronaux-rvq'},
    {text:'Comparer DDPM et flow matching',themeId:'generation-controle',chapterId:'objectifs-diffusion-et-flow'},
    {text:'Assembler texte, audio et MIDI',themeId:'generation-controle',chapterId:'controle-multimodal-formes'},
    {text:'Raisonner sous un budget',themeId:'generation-controle',chapterId:'efficacite-petit-budget'},
    {text:'Choisir symbolique ou audio',themeId:'generation-controle',chapterId:'symbolique-midi-et-audio'},
  ],deliverable:'Proposer une méthode pour une modification musicale précise. Dire ce qu’elle contrôle, ce qu’elle risque de perdre et ce qui reste à mesurer.'},
  {title:'Semaine 4 · Évaluer, puis défendre à l’oral',goal:'Transformer la proposition en comparaison honnête, puis en discussion.',links:[
    {text:'Éviter les fuites',themeId:'evaluation-recherche',chapterId:'splits-et-fuites'},
    {text:'Préparer référence et ablations',themeId:'evaluation-recherche',chapterId:'baselines-et-ablations'},
    {text:'Organiser une écoute',themeId:'evaluation-recherche',chapterId:'ecoute-et-jugement-perceptif'},
    {text:'Relire l’offre',themeId:'contexte-recherche',chapterId:'lire-offre-et-se-preparer'},
    {text:'S’entraîner aux questions',themeId:'entretien',chapterId:'oral-boucle-pytorch'},
    {text:'Écrire son pitch',themeId:'entretien',chapterId:'pitch-recherche-deux-minutes'},
  ],deliverable:'Répondre avant de révéler le modèle. Essayer les relances et préparer un pitch fondé sur ses choix et son expérience réels.'},
];

export const quickChapter=(themeId,chapterId)=>QUICK_CHAPTERS.find(chapter=>chapter.themeId===themeId&&chapter.chapterId===chapterId);
