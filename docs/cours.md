# Les cours du professeur Squoinks

État de la révision pédagogique : **19 novembre 2026**. La page Cours est accessible dans le header ; le quiz reste la page principale. Sous Windows, lancer `Lancer.cmd`, puis ouvrir `http://127.0.0.1:5173/cours.html`.

## Parcours actuel

Les huit modules contiennent **120 chapitres**. Le parcours suppose une pratique du Python algorithmique et introduit les conventions scientifiques au moment de leur utilisation.

| Module | Chapitres | Besoin qui organise le cours |
| --- | ---: | --- |
| Python scientifique | 13 | Préparer des données et comprendre leurs formes, leurs copies et leurs transformations. |
| Signal audio | 9 | Comparer deux sons, puis choisir comment les représenter et les transformer. |
| PyTorch | 32 | Construire tôt une petite boucle d’apprentissage, puis traiter les besoins plus complexes. |
| Apprentissage audio | 11 | Relier tâches, représentations, objectifs et architectures. |
| Génération et contrôle | 15 | Comprendre les mécanismes génératifs et les commandes qu’ils permettent. |
| Évaluation et recherche | 10 | Construire une comparaison interprétable et connaître ses limites. |
| Contexte IRCAM et recherche | 4 | Relier les outils, les lectures et les choix de recherche. |
| Entretien | 26 | Préparer 25 réponses ouvertes et un pitch hypothétique. |

Les deux rappels Python de base restent facultatifs, accessibles par le sommaire et les liens. Les niveaux « Socle à pratiquer », « À discuter » et « Approfondissement » indiquent l’effort attendu ; ils ne certifient pas une compétence.

La progression PyTorch présente d’abord les données fixes, les scores, `Linear`, la perte, les gradients et une première boucle. Dataset, padding, masques, axes, buffers, convolutions et CUDA/AMP viennent ensuite selon leurs prérequis. Le contraste et l’attention ont désormais deux chapitres distincts dans Apprentissage audio.

## Lire, prévoir, puis vérifier

Chaque introduction situe le problème, les notions à venir et le résultat attendu. Les nombres choisis, les axes, les arguments importants et les mutations sont expliqués avant leur utilisation. Les analogies et les exemples restent liés au besoin traité.

Les exemples guidés surlignent les lignes concernées. Les boutons précédent/suivant permettent de suivre un calcul ; « toutes les étapes » donne une vue d’ensemble. Certains détails locaux se déplient pour examiner une opération, ses valeurs ou sa forme. Ce déroulé est rédigé et vérifié à l’avance : **le navigateur n’exécute pas Python**.

Six laboratoires de tenseurs calculent de petites variations en JavaScript : axes d’argmax, reshape/transpose, broadcasting, couche linéaire, gradient et convolution. Leur nature pédagogique est annoncée. Ils ne sont pas des exécutions PyTorch. Le padding et les moyennes masquées sont expliqués par les tableaux et le code ; le laboratoire de padding disponible dans le composant n’est pas inséré dans les cours. Les tableaux, figures et images possèdent des indications de lecture et des légendes.

Les programmes portent la mention « Programme autonome » ou « Extrait à lire ». Les objets nécessaires et leurs contrats sont annoncés avant un extrait. Les programmes audio indiquent les fichiers à télécharger et le dossier attendu. Les compléments peuvent être repliés pour préserver la première lecture.

Les questions de transfert invitent à prévoir une forme, une valeur, une mutation ou un diagnostic. Elles possèdent quatre options et peuvent expliquer l’erreur propre à chaque choix. Elles restent indépendantes du score des 200 questions du quiz.

## Repères personnels et liens

« J’ai lu ce chapitre » et « À revoir » sont deux repères distincts. Le dernier chapitre, les étapes guidées, la position de lecture, les préférences et les tentatives de transfert sont conservés dans `localStorage`, sous `a-lecoute.courses.v1`. Une question réécrite n’hérite pas d’une ancienne réponse devenue ambiguë. Les repères valides de l’ancien format sont conservés ; un stockage indisponible laisse la lecture fonctionner en mémoire.

La session du quiz reste séparée. Les notes du pitch utilisent `a-lecoute.pitch.v1`. Lire un chapitre ou réussir sa petite question ne constitue pas une mesure de maîtrise.

Les **107 identifiants de chapitre du point de départ sont conservés**. Treize chapitres ont été ajoutés. Les déplacements de couverture de 15 questions sont documentés dans `scripts/verify/audit-question-moves.json`. La banque garde ses **200 questions**, sans ajout, suppression ni renumérotation.

Les liens directs utilisent le thème et l’ancre, par exemple `cours.html?theme=pytorch#organiser-les-axes`. Un lien issu du quiz peut utiliser `cours.html?theme=pytorch&question=pt-020` ; il rejoint le chapitre qui couvre désormais cette question. Une ancre inconnue revient au premier chapitre, et un thème inconnu au catalogue.

## Voir et écouter les données

Les médias des révisions antérieures sont conservés : 18 WAV, 61 figures scientifiques, cinq illustrations externes créditées, onze ateliers d’écoute et douze blocs d’images commentées. La provenance, les licences et les conventions de calcul sont documentées dans `audio-lab.md` et `media-sources.md`.

Le laboratoire d’écoute utilise de véritables extraits de voix et de percussion. Les mesures dépendent des fichiers, du segment et des conventions annoncés. Le code peut travailler sur le fichier source mono à 16 kHz, tandis que le lecteur utilise un dérivé à 48 kHz : cette distinction est explicitée dans le cours.

Les petits tableaux RMS/crête de PyTorch sont des **valeurs choisies pour le calcul**, pas les mesures de ces fichiers. Les ondes de 220 et 440 Hz sont synthétiques. Une comparaison de nombres ou une baisse de perte ne prouve pas la qualité d’un modèle audio entraîné.

Les blocs `audio-lab`, `analysis-image` et `illustration` gardent leurs fichiers et crédits. `validate:media` contrôle les chemins, les empreintes et les mesures recalculées depuis le PCM.

## Notebooks PyTorch

Chacun des **32 chapitres PyTorch** possède un notebook téléchargeable et un lien Colab. L’accès est placé après la première explication du chapitre.

Les 38 programmes du cours sont répartis en cellules progressives. Chaque instruction composée reste entière. Leur concaténation reproduit exactement le code affiché ; les identifiants des cellules et les empreintes figurent dans `metadata.quiz.programs`. Des cellules distinctes observent les valeurs, les formes et les gradients.

Chaque notebook contient **deux cellules de code à compléter**, deux indices repliés et deux solutions repliées en fin de document. « Tout exécuter » sur les exercices vides affiche « À compléter » ; aucun succès n’est annoncé. Les contrôles s’activent lorsque la réponse est renseignée. Les solutions complètes sont aussi conservées dans les métadonnées pour être exécutées par le vérificateur.

Les **654 cellules de code livrées et les 64 solutions** ont été exécutées avec de vrais noyaux CPU. Les durées finales vont de **6,182 à 11,872 secondes** par notebook, démarrage compris, sous le seuil de 120 secondes sur cette machine. L’environnement mesuré utilise Python 3.11.9 et PyTorch/TorchAudio 2.10.0 CPU.

Le générateur courant est `scripts/make-progressive-notebooks.py`. `scripts/verify/notebooks.py` exécute les documents, conserve leurs sorties et écrit `scripts/verify/notebooks-results.json`. **Aucune exécution Colab authentifiée n’est attestée pour cette révision.**

## Organisation et vérification

Les textes se trouvent dans `public/courses/*.json`. Les `questionIds` relient les notions au quiz ; les `sourceIds` pointent vers les références du thème. Les introductions annoncent leurs concepts et les prérequis. Les blocs peuvent déclarer `codeMode`, `requires`, `resources`, des détails d’étapes et une correction par option.

Les principaux composants sont `src/courses.js`, `src/course-model.js`, `src/learning-blocks.js`, `src/tensor-labs.js` et `src/course-media.js`. Le site conserve trois entrées : quiz, cours et glossaire. Le glossaire propose 160 paires FR–EN, avec recherche et liens vers les chapitres.

```powershell
npm run validate:courses
npm test
npm run build
npm run test:browser
```

Si npm n’est pas dans le PATH, utiliser `node scripts/run.mjs` suivi du nom du script. Les commandes scientifiques et les preuves actuelles sont détaillées dans `../VERIFICATION.md`.

Au 19 novembre, les **59 tests unitaires**, la construction, les exécutions CPU et les **33 contrôles Edge sur les fichiers finaux** sont attestés. La révision `3bbeb56` est [publiée et vérifiée en ligne](https://radiocodeur.github.io/quiz/cours.html). Le workflow et les contrôles des huit modules et 32 téléchargements sont consignés dans `../VERIFICATION.md` et `audit-revision-report.md`.

## Historique

`revision-report.md` décrit le lot antérieur à 107 chapitres et 20 notebooks. Ses chiffres, ses finales orales obligatoires et ses exercices en Markdown ne décrivent plus l’état courant. Les anciens rapports CPU et de liens restent des archives. Les quatre rapports `audit-*-results.json` et le rapport des 32 notebooks font foi pour cette révision. `prose-audit.json` a été régénéré sur les 120 chapitres comme aide à la lecture, sans imposer de finale orale. Le détail des changements est dans `audit-revision-report.md`.
