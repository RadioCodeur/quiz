# Les cours du professeur Squoinks

La page **Cours** est accessible dans le header. Le quiz reste la page principale. Pour essayer la version locale sous Windows, lancer `Lancer.cmd` puis ouvrir `http://127.0.0.1:5173/cours.html`.

## Contenu

Six cours, **57 chapitres**, environ **21 000 mots hors code**, **51 extraits commentés**, **53 exemples concrets** et **13 schémas**. L’ordre conseillé est Python → signal audio → PyTorch → apprentissage audio → génération et contrôle → évaluation et recherche. Chaque correction du quiz renvoie au chapitre qui explique sa notion.

Chaque chapitre présente une idée directrice, un développement explicatif, des exemples ou du code, puis trois idées à retenir. Le **mode lecture** masque le sommaire ; **Aa +** agrandit le texte. Le sommaire est replié au départ sur téléphone. Les schémas larges et le code défilent dans leur propre conteneur. Le portrait du professeur est local ; aucune image extérieure n’est chargée.

La case **J’ai lu ce chapitre** est un repère volontaire, pas un test de maîtrise. Le dernier chapitre et les préférences sont enregistrés dans `localStorage`, sous la clé distincte **`a-lecoute.courses.v1`**. La session du quiz reste intacte. Les données corrompues ou les identifiants retirés sont filtrés. Sans stockage disponible, la lecture fonctionne en mémoire.

## Sources et couverture

Les cours sont de vrais JSON dans `public/courses/`, avec un fichier par thème. Chaque chapitre déclare les `questionIds` dont il explique les connaissances et les `sourceIds` provenant des registres de références du quiz. Le validateur vérifie que les **200 questions** possèdent chacune un chapitre dans leur thème principal, sans oubli ni doublon. Cette vérification structurelle est complétée par une relecture pédagogique ; elle ne prouve pas automatiquement qu’un lecteur saura répondre juste.

Les extraits supposent les imports usuels (`np` pour NumPy, `torch` pour PyTorch) lorsqu’ils ne sont pas montrés. Aucun code Python n’est exécuté par le site. Les résultats des exemples sont expliqués pour permettre le raisonnement.

## Fichiers

- `cours.html` : deuxième point d’entrée de Vite, compatible avec un sous-chemin GitHub Pages.
- `src/courses.js` et `src/courses.css` : navigation et lecture.
- `src/course-model.js` : liens, progression et correspondances question/chapitre.
- `src/course-figures.js` : schémas SVG légendés.
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

Cette étape de travail reste locale : aucun envoi à GitHub ni déploiement du nouveau contenu n’est lancé.
