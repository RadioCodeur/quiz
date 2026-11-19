# Les cours du professeur Squoinks

État documentaire : **20 novembre 2026**, révision narrative de PyTorch publiée et vérifiée en ligne. La page Cours est accessible dans le header ; le quiz reste la page principale. Sous Windows, lancer `Lancer.cmd`, puis ouvrir `http://127.0.0.1:5173/cours.html`.

## Parcours actuel

Les huit modules contiennent **110 entrées de cours**, dont les 14 chapitres principaux et les huit références de PyTorch. Le parcours suppose une pratique du Python algorithmique et introduit les conventions scientifiques au moment de leur utilisation.

| Module | Chapitres | Besoin qui organise le cours |
| --- | ---: | --- |
| Python scientifique | 13 | Préparer des données et comprendre leurs formes, leurs copies et leurs transformations. |
| Signal audio | 9 | Comparer deux sons, puis choisir comment les représenter et les transformer. |
| PyTorch | 22 : 14 principaux + 8 références | Corriger une percussion mal classée, construire une boucle et observer des exemples réservés. |
| Apprentissage audio | 11 | Relier tâches, représentations, objectifs et architectures. |
| Génération et contrôle | 15 | Comprendre les mécanismes génératifs et les commandes qu’ils permettent. |
| Évaluation et recherche | 10 | Construire une comparaison interprétable et connaître ses limites. |
| Contexte IRCAM et recherche | 4 | Relier les outils, les lectures et les choix de recherche. |
| Entretien | 26 | Préparer 25 réponses ouvertes et un pitch hypothétique. |

Les deux rappels Python de base restent facultatifs, accessibles par le sommaire et les liens. Les niveaux « Socle à pratiquer », « À discuter » et « Approfondissement » indiquent l’effort attendu ; ils ne certifient pas une compétence.

Le premier trajet PyTorch relie tenseurs → scores → couche → perte → gradient et pas SGD → boucle → validation, en sept chapitres. Les lots, les valeurs, les axes et les durées variables viennent ensuite selon le besoin, puis convolution et reconstruction mel. Huit références restent accessibles à la demande, avec une progression principale indépendante sur 14 chapitres. Un index du menu rassemble six diagnostics : forme, type, emplacement, valeurs non finies, graphe et stockage. Le contraste et l’attention gardent leurs deux chapitres distincts dans Apprentissage audio.

## Lire, prévoir, puis vérifier

Chaque introduction situe le problème, les notions à venir et le résultat attendu. Les nombres choisis, les axes, les arguments importants et les mutations sont expliqués avant leur utilisation. Les analogies et les exemples restent liés au besoin traité.

Les exemples guidés surlignent les lignes concernées. Les boutons précédent/suivant permettent de suivre un calcul ; « toutes les étapes » donne une vue d’ensemble. Certains détails locaux se déplient pour examiner une opération, ses valeurs ou sa forme. Ce déroulé est rédigé et vérifié à l’avance : **le navigateur n’exécute pas Python**.

Sept laboratoires de tenseurs calculent de petites variations en JavaScript : axes d’argmax, reshape/transpose, broadcasting, couche linéaire, gradient, padding et convolution. Leur nature pédagogique est annoncée. Ils ne sont pas des exécutions PyTorch. Le laboratoire de padding accompagne maintenant la question des durées variables et de leur moyenne. Les tableaux, figures et images possèdent des indications de lecture et des légendes.

Dans PyTorch, le texte continu présente seulement les nouvelles lignes utiles. Les fragments `reading-fragment` pointent par `programId` et `sourceLines` vers le programme autonome replié ; leurs dépendances sont annoncées. Les prédictions précèdent les résultats correspondants. Le programme complet et le pas à pas restent disponibles sans dominer la première lecture.

Les programmes portent la mention « Programme autonome » ou « Extrait à lire ». Les objets nécessaires et leurs contrats sont annoncés avant un extrait. Les programmes audio indiquent les fichiers à télécharger et le dossier attendu. Les compléments peuvent être repliés pour préserver la première lecture.

Les questions de transfert invitent à prévoir une forme, une valeur, une mutation ou un diagnostic. Elles possèdent quatre options et peuvent expliquer l’erreur propre à chaque choix. Elles restent indépendantes du score des 200 questions du quiz.

## Repères personnels et liens

« J’ai lu ce chapitre » et « À revoir » sont deux repères distincts. Le dernier chapitre, les étapes guidées, la position de lecture, les préférences et les tentatives de transfert sont conservés dans `localStorage`, sous `a-lecoute.courses.v1`. Une question réécrite n’hérite pas d’une ancienne réponse devenue ambiguë. Les repères valides de l’ancien format sont conservés ; un stockage indisponible laisse la lecture fonctionner en mémoire.

La session du quiz reste séparée. Les notes du pitch utilisent `a-lecoute.pitch.v1`. Lire un chapitre ou réussir sa petite question ne constitue pas une mesure de maîtrise.

Les anciennes destinations PyTorch restent accessibles par **22 identifiants canoniques et dix alias**. Les repères des pages regroupées sont repris vers leur destination ; consulter les références ne fait pas avancer le compteur des 14 principaux. La banque garde ses **200 questions**, sans ajout, suppression ni renumérotation. Les 50 questions PyTorch sont reliées aux passages pertinents ; leurs déplacements sont documentés dans `scripts/verify/pytorch-narration-question-moves.json`.

Les liens directs utilisent le thème et l’ancre, par exemple `cours.html?theme=pytorch#organiser-les-axes`. Un lien issu du quiz peut utiliser `cours.html?theme=pytorch&question=pt-020` ; il rejoint le chapitre qui couvre désormais cette question. Une ancre inconnue revient au premier chapitre, et un thème inconnu au catalogue.

## Voir et écouter les données

Les médias des révisions antérieures sont conservés : 18 WAV, 61 figures scientifiques, cinq illustrations externes créditées, onze ateliers d’écoute et douze blocs d’images commentées. La provenance, les licences et les conventions de calcul sont documentées dans `audio-lab.md` et `media-sources.md`.

Le laboratoire d’écoute utilise de véritables extraits de voix et de percussion. Les mesures dépendent des fichiers, du segment et des conventions annoncés. Le code peut travailler sur le fichier source mono à 16 kHz, tandis que le lecteur utilise un dérivé à 48 kHz : cette distinction est explicitée dans le cours.

Les petits tableaux RMS/crête de PyTorch sont des **valeurs choisies pour le calcul**, pas les mesures de ces fichiers. Les ondes de 220 et 440 Hz sont synthétiques. Une comparaison de nombres ou une baisse de perte ne prouve pas la qualité d’un modèle audio entraîné.

Les blocs `audio-lab`, `analysis-image` et `illustration` gardent leurs fichiers et crédits. `validate:media` contrôle les chemins, les empreintes et les mesures recalculées depuis le PCM.

## Notebooks PyTorch

Les **22 entrées canoniques PyTorch** possèdent un chemin de notebook et un lien Colab. Les dix anciens chemins des pages regroupées sont conservés comme documents d’orientation vers le notebook canonique.

La génération repart des **25 programmes autonomes** : les petits fragments de lecture ne sont pas recopiés comme de nouveaux programmes. Les cellules de démonstration conservent chaque instruction composée entière ; leur concaténation reproduit exactement le programme du cours. Les identifiants des cellules et les empreintes figurent dans `metadata.quiz.programs`.

Chaque notebook contient **deux cellules de code à compléter**, deux indices repliés et deux solutions repliées. Un exercice vide affiche « À compléter », sans annoncer de réussite. Les solutions sont exécutées séparément par le vérificateur.

**Les 22 notebooks, leurs 474 cellules de code et leurs 44 solutions ont été exécutés sur CPU.** Les dix anciens chemins sont des documents d’orientation sans code. Les preuves figurent dans `scripts/verify/notebooks-results.json` et `../VERIFICATION.md`.

Le générateur est `scripts/make-progressive-notebooks.py`. `scripts/verify/notebooks.py` exécute les documents et leurs solutions sur CPU. **Aucune exécution Colab authentifiée n’est attestée pour cette révision.**

## Organisation et vérification

Les textes se trouvent dans `public/courses/*.json`. Les `questionIds` relient les notions au quiz ; les `sourceIds` pointent vers les références du thème. Les introductions annoncent leurs concepts et les prérequis. Dans PyTorch, `readingGroups` organise le parcours, `readingRole` distingue les références et `chapterAliases` préserve les anciennes destinations. Les blocs peuvent déclarer `codeMode`, `requires`, `resources`, des détails d’étapes et une correction par option.

Les principaux composants sont `src/courses.js`, `src/course-model.js`, `src/learning-blocks.js`, `src/tensor-labs.js` et `src/course-media.js`. Le site conserve trois entrées : quiz, cours et glossaire. Le glossaire propose 160 paires FR–EN, avec recherche et liens vers les chapitres.

```powershell
npm run validate:courses
npm test
npm run build
npm run test:browser
```

Si npm n’est pas dans le PATH, utiliser `node scripts/run.mjs` suivi du nom du script. Les commandes scientifiques et les preuves actuelles sont détaillées dans `../VERIFICATION.md`.

La révision narrative part de `9df9363`. Les sept autres JSON de cours restent identiques octet pour octet. Le JSON assemblé est vérifié : 25 programmes, 99 assertions et 63 extraits. Les 67 tests unitaires, la construction et les 36 contrôles navigateur réussissent. La publication `86ff2b2` et le contrôle public ont réussi ; le workflow est consigné dans `../VERIFICATION.md`. Le détail éditorial figure dans `pytorch-narration-report.md`.

## Historique

`revision-report.md` décrit l’ancien lot à 107 chapitres et 20 notebooks. `audit-revision-report.md` décrit la révision antérieure à 120 chapitres et 32 notebooks. Leurs effectifs, durées, journaux et résultats de publication ne décrivent pas la présente refonte narrative.

La base de comparaison actuelle est `scripts/verify/pytorch-narration-baseline.json`, révision `9df9363`. Le rapport courant est `pytorch-narration-report.md` ; ses preuves CPU et notebooks sont indiquées dans `../VERIFICATION.md`. Les anciennes sources et les médias des sept modules inchangés restent documentés dans leurs rapports.
