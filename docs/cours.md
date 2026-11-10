# Les cours du professeur Squoinks

La page **Cours** est accessible dans le header. Le quiz reste la page principale. Pour essayer la version locale sous Windows, lancer `Lancer.cmd` puis ouvrir `http://127.0.0.1:5173/cours.html`.

## Contenu

Six cours, **65 chapitres**, environ **40 000 mots hors code**, **65 exemples guidés**, **65 schémas relationnels**, **15 graphiques numériques** et **7 figures complémentaires**. L’ordre conseillé est Python → signal audio → PyTorch → apprentissage audio → génération et contrôle → évaluation et recherche. Chaque correction du quiz renvoie au chapitre qui explique sa notion. Les anciens identifiants de chapitres sont conservés pour préserver les liens et les repères personnels.

Chaque cours annonce son projet, son point de départ, sa destination et les étapes qui relient ses chapitres. Chaque chapitre rappelle ce qui est déjà connu, pose un problème, explique son utilité dans le projet et prépare la suite. Le **mode lecture** masque le sommaire ; **Aa +** agrandit le texte. Le sommaire est replié au départ sur téléphone. Les schémas larges et le code défilent dans leur propre conteneur. Le portrait du professeur est local ; aucune image extérieure n’est chargée.

La présentation de chaque module annonce aussi cinq à huit notions, dans l’ordre où elles seront rencontrées, avec une explication et un lien vers le chapitre correspondant. Chaque chapitre nomme et définit deux à quatre notions avant ses exemples. Un **premier exemple très court** affiche la situation ou le code, son résultat, puis une variation qui change une seule chose. Ce passage précède le grand déroulé guidé : il sert à comprendre la règle avant de l’appliquer à un cas plus riche. La présentation s’inspire des pages de cours publiques de France-IOI consultées, avec des textes et exemples audio originaux.

Les exemples guidés possèdent des boutons précédent/suivant : ils surlignent les lignes de code concernées et expliquent les états avant/après. Il s’agit d’un déroulé rédigé et vérifié à l’avance, sans interpréteur Python. Une vue « toutes les étapes » reste disponible. Les tableaux et graphiques ont une légende interprétative ; les valeurs des graphiques sont consultables sous forme de tableau. Un QCM facultatif de transfert avec quatre choix et une correction immédiate suit chaque chapitre. Ces réponses ne sont pas ajoutées au score du quiz et ne sont pas conservées comme mesure de maîtrise.

La case **J’ai lu ce chapitre** est un repère volontaire, pas un test de maîtrise. Le dernier chapitre et les préférences sont enregistrés dans `localStorage`, sous la clé distincte **`a-lecoute.courses.v1`**. La session du quiz reste intacte. Les données corrompues ou les identifiants retirés sont filtrés. Sans stockage disponible, la lecture fonctionne en mémoire.

## Sources et couverture

Les cours sont de vrais JSON dans `public/courses/`, avec un fichier par thème. Chaque chapitre déclare les `questionIds` dont il explique les connaissances et les `sourceIds` provenant des registres de références du quiz. Le validateur vérifie que les **200 questions** possèdent chacune un chapitre dans leur thème principal, sans oubli ni doublon. Cette vérification structurelle est complétée par une relecture pédagogique ; elle ne prouve pas automatiquement qu’un lecteur saura répondre juste.

Les introductions de module utilisent `moduleIntroduction` (`startingPoint`, `goal`, `concepts` reliés par `chapterId`). Les nouvelles notions d’un chapitre sont dans `notions`. Le bloc `first-example` contient `title`, `introduction`, `code`, `language`, `output`, `explanation` et `variant` (`change`, `output`, `explanation`). Les sorties sont rédigées et vérifiées : aucun interpréteur n’est intégré au site. Le validateur impose un premier exemple de six lignes au plus, placé avant le grand exemple guidé.

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

Si npm n’est pas dans le PATH, utiliser `node scripts/run.mjs validate:courses`, puis les mêmes noms de scripts (`test`, `build`, `test:browser`). La construction valide la banque et les cours avant de produire `dist/index.html` et `dist/cours.html`. Le test navigateur parcourt les 57 chapitres à 360 px et vérifie les deux pages sous `/qr-entretien/`.

La publication utilise le workflow manuel GitHub Pages du dépôt, après validation et vérification dans le navigateur. Les principes pédagogiques et leur portée sont documentés dans `docs/pedagogie.md` et accessibles depuis le catalogue des cours.
