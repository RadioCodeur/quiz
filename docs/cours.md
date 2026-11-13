# Les cours du professeur Squoinks

La page **Cours** est accessible dans le header. Le quiz reste la page principale. Pour essayer la version locale sous Windows, lancer `Lancer.cmd` puis ouvrir `http://127.0.0.1:5173/cours.html`.

## Contenu

Six cours, **65 chapitres** dont deux rappels Python facultatifs. L’ordre conseillé est Python → signal audio → PyTorch → apprentissage audio → génération et contrôle → évaluation et recherche. Les identifiants historiques sont conservés : les liens du quiz et les repères personnels restent valides, même si le parcours Python a été réordonné.

Le public connaît le Python algorithmique. Le parcours principal démarre donc sur le besoin numérique ; les rappels sur les valeurs et les indices restent en fin de sommaire et la navigation « suivant » ne les impose pas. Les six modules suivent un problème explicite : préparer une sonothèque, homogénéiser ses signaux, apprendre un classifieur, adapter la tâche aux mélanges, construire un instrument de percussion, puis vérifier une amélioration.

Chaque chapitre situe brièvement son entrée, son action et son résultat. Les définitions se déplient à la demande ; les notions scientifiques sont aussi expliquées dans le récit au moment de leur usage. Les premiers exemples et leurs variantes sont facultatifs : leur présence dépend du bénéfice pédagogique, pas d’un quota. Les répétitions et petits exemples sans lien ont été retirés. Le **mode lecture** masque le sommaire et **Aa +** agrandit le texte. Les schémas larges et le code défilent dans leur propre conteneur. Le portrait du professeur reste local.

Les exemples guidés possèdent des boutons précédent/suivant : ils surlignent les lignes de code concernées et expliquent les états avant/après. Il s’agit d’un déroulé rédigé et vérifié à l’avance, sans interpréteur Python. Une vue « toutes les étapes » reste disponible. Les tableaux et graphiques ont une légende interprétative ; les valeurs des graphiques sont consultables sous forme de tableau. Un QCM facultatif de transfert avec quatre choix et une correction immédiate suit chaque chapitre. Ces réponses ne sont pas ajoutées au score du quiz et ne sont pas conservées comme mesure de maîtrise.

La case **J’ai lu ce chapitre** est un repère volontaire, pas un test de maîtrise. Le dernier chapitre et les préférences sont enregistrés dans `localStorage`, sous la clé distincte **`a-lecoute.courses.v1`**. La session du quiz reste intacte. Les données corrompues ou les identifiants retirés sont filtrés. Sans stockage disponible, la lecture fonctionne en mémoire.

## Sources et couverture

Les cours sont de vrais JSON dans `public/courses/`, avec un fichier par thème. Chaque chapitre déclare les `questionIds` dont il explique les connaissances et les `sourceIds` provenant des registres de références du quiz. Le validateur vérifie que les **200 questions** possèdent chacune un chapitre dans leur thème principal, sans oubli ni doublon. Cette vérification structurelle est complétée par une relecture pédagogique ; elle ne prouve pas automatiquement qu’un lecteur saura répondre juste.

Les introductions de module utilisent `moduleIntroduction` (`startingPoint`, `goal`, `concepts` reliés par `chapterId`). Chaque chapitre porte `progression` (`input`, `action`, `output`) et `notions`. Le rôle `readingRole: "reference"` identifie un complément disponible par lien direct et sommaire, hors navigation principale. Le bloc facultatif `first-example` contient `title`, `introduction`, `code`, `language`, `output`, `explanation` ; son éventuelle `variant` contient `change`, `output`, `explanation` et se déplie à la demande. Aucun interpréteur n’est intégré au site.

Les extraits supposent les imports usuels (`np` pour NumPy, `torch` pour PyTorch) lorsqu’ils ne sont pas montrés. Aucun code Python n’est exécuté par le site. Les résultats des exemples sont expliqués pour permettre le raisonnement.

## Fichiers

- `cours.html` : deuxième point d’entrée de Vite, compatible avec un sous-chemin GitHub Pages.
- `src/courses.js` et `src/courses.css` : navigation et lecture.
- `src/course-model.js` : liens, progression et correspondances question/chapitre.
- `src/course-figures.js` : schémas SVG légendés, dont copies imbriquées et réductions NumPy.
- `src/learning-blocks.js` et `src/learning.css` : exemples guidés, graphiques, schémas et QCM de transfert.
- `public/courses/*.json` : textes, exemples et références des six cours.
- `public/images/professeur-squoinks.png` : portrait du personnage.
- `tests/courses.test.mjs` : tests du modèle et de la couverture.
- `scripts/validate-courses.mjs` : contrôle du contenu et des prérequis.

Les paramètres d’URL et les ancres permettent des liens directs, par exemple `cours.html?theme=pytorch&question=pt-020` ou `cours.html?theme=pytorch#organiser-les-axes`. Un identifiant de chapitre périmé revient au premier chapitre au lieu de bloquer l’affichage. Un thème inconnu revient au catalogue.

## Vérifier et construire

```powershell
npm run validate:courses
npm test
npm run build
npm run test:browser
```

Si npm n’est pas dans le PATH, utiliser `node scripts/run.mjs validate:courses`, puis les mêmes noms de scripts (`test`, `build`, `test:browser`). La construction valide la banque et les cours avant de produire `dist/index.html` et `dist/cours.html`. Le test navigateur parcourt les 65 chapitres à 360 px et vérifie les deux pages sous `/qr-entretien/`.

La publication utilise le workflow manuel GitHub Pages du dépôt, après validation et vérification dans le navigateur. Les principes pédagogiques et leur portée sont documentés dans `docs/pedagogie.md` et accessibles depuis le catalogue des cours.


## Voir et écouter les données réelles

La révision du 13 novembre 2026 ajoute deux extraits réels et leurs transformations : 18 WAV, 61 images calculées, cinq illustrations externes créditées, onze laboratoires d’écoute et douze blocs d’images commentées, répartis sur les six modules. La section niveaux explique amplitude, carré moyen, RMS, dBFS, dB SPL et LUFS avant le code, puis conclut sur les mesures des fichiers.

Les nouveaux blocs `audio-lab` utilisent une vue parmi `overview`, `level`, `resample`, `stft`, `mel`, `phase`, `augmentation`. Les `illustration` référencent `public/media/illustrations.json` et les `analysis-image` référencent les figures de `public/media/audio-lab.json`. L’interface, les légendes et les crédits se trouvent dans `src/course-media.js` et `src/course-media.css`. La provenance et les conventions de mesure sont documentées dans `docs/audio-lab.md` et `docs/media-sources.md`.

`validate:media` vérifie les chemins locaux, les licences déclarées, les fichiers, les empreintes et les mesures recalculées depuis le PCM. La construction lance ce contrôle. Les contenus et liens historiques des 200 QCM restent conservés.
