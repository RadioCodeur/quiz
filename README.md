# À l’écoute — Révisions IA audio

Application personnelle de révision en français : **200 QCM originaux**, quatre propositions et une seule bonne réponse. Sessions courtes, code à lire, corrections expliquées et reprise sur le même navigateur. Interface HTML/CSS/JavaScript en modules avec Vite, sans framework ni serveur applicatif.

## Essayer immédiatement

Dans ce dossier, avec Node.js 22.12+ (Node 24 recommandé) :

```powershell
npm ci
npm run dev
```

Ouvrir l’adresse affichée, généralement **http://127.0.0.1:5173**. Arrêter avec `Ctrl+C`.

Sur Windows, on peut aussi double-cliquer sur **Lancer.cmd**, ou utiliser :

```powershell
node scripts/run.mjs dev
```

Le double-clic sur `Lancer.cmd` ouvre automatiquement le quiz dans le navigateur. Garder la fenêtre du lanceur ouverte pendant la session ; `Ctrl+C` ou la fermeture de cette fenêtre arrête le serveur. Le lanceur recherche Node dans le PATH, dans les emplacements d’installation Windows usuels et dans le runtime local de Codex : il fonctionne donc aussi lorsque `node` n’est pas reconnu dans une console Windows ordinaire. Il affiche un message si aucun exécutable n’est trouvé.

Ce lanceur fonctionne aussi si Node est disponible mais que npm n’est pas dans le PATH : il prépare npm dans `.tools/`, puis installe les dépendances si elles sont absentes. Cette première préparation demande Internet et la commande `tar` (fournie sur les versions récentes de Windows). Les usages suivants réutilisent les outils locaux. Le quiz ne fait ensuite aucun appel à un service externe ; seules les références ouvertes volontairement conduisent vers leurs sites.

Ne pas ouvrir `index.html` directement en `file://` : les modules et JSON ont besoin d’un serveur HTTP local. L’application n’installe pas de service worker et ne promet pas une utilisation hors connexion après fermeture du serveur.

## Commandes

```powershell
npm run validate      # vérification du schéma, quotas, IDs et références
npm test              # tests de logique et de sauvegarde, sans navigateur
npm run build         # validation, puis construction dans dist/
npm run preview       # aperçu de dist/, généralement sur le port 4173
npm run test:browser  # parcours automatisé ordinateur/mobile + sous-chemin
```

Le test navigateur requiert une construction récente (`npm run build`). Il utilise Microsoft Edge installé ou, en repli, Chromium de Playwright. Pour installer ce dernier si nécessaire :

```powershell
npx playwright install chromium
```

Le test démarre et arrête ses propres serveurs, sur les ports **4188 et 4189**. Ses captures sont enregistrées dans `test-results/` (ignoré par Git). Pour une installation sans npm dans le PATH, les équivalents sont `node scripts/run.mjs validate`, `node scripts/run.mjs test`, `node scripts/run.mjs build`, `node scripts/run.mjs preview` et `node scripts/run.mjs test:browser`.

## Ce que fait le quiz

- Sélection de plusieurs thèmes par **union** : une question doit porter au moins une étiquette sélectionnée. Le compteur indique des questions uniques ; un même QCM peut apparaître dans les compteurs de plusieurs thèmes.
- Sessions de 10 à 200 questions, par dizaines, selon le stock filtré ; 50 par défaut si possible, sinon le plus grand multiple de 10 disponible. Un filtrage insuffisant désactive le départ.
- Tirage sans remise et mélange des réponses. La correction est liée à l’ID d’une option, indépendamment de sa position affichée.
- Une seule question à la fois ; le premier clic valide et verrouille les quatre choix. L’explication est toujours affichée. Aucune minuterie ou transition automatique.
- Bilan global, résultats par thème, repères indicatifs et carnet d’erreurs dépliable. Une question multi-étiquettes ne compte qu’une fois dans le score global, et une fois dans chacun de ses thèmes.
- « Refaire mes erreurs » reprend exactement les questions ratées, même une seule. Le bouton est désactivé sur une session parfaite.
- Confirmation avant abandon ou remplacement d’une session active. La reprise après rafraîchissement conserve question, choix mélangés et correction déjà affichée.

Les extraits supposent les imports usuels (`import numpy as np`, `import torch`) lorsque ceux-ci sont omis. Les dimensions, paramètres et hypothèses utiles sont donnés dans les énoncés ou extraits. **Aucun code Python n’est exécuté** par l’application.

## Contenu et références

| Thème principal | Questions |
| --- | ---: |
| Python scientifique | 20 |
| PyTorch | 50 |
| Signal audio | 30 |
| Apprentissage audio | 30 |
| Génération et contrôle | 40 |
| Évaluation et recherche | 30 |
| **Total** | **200** |

Répartition : **60 fondamentales, 100 intermédiaires, 40 avancées** ; **99 questions avec code**. Les étiquettes secondaires expriment des connaissances effectivement mobilisées, donc les compteurs de l’écran d’accueil peuvent dépasser ces quotas principaux.

Les **88 entrées de références** se trouvent dans les trois registres `public/data/sources-*.json`. Elles pointent vers les documentations officielles Python, NumPy, PyTorch, SciPy, librosa et scikit-learn, ainsi que vers des publications originales (VAE, DDPM, WaveNet, MusicGen, LoRA, SpecAugment, etc.). Les pages et publications ont été consultées lors de la rédaction le **5 novembre 2026**. Chaque QCM renvoie à ses références dans sa correction. Les textes sont des questions et explications originales, sans reprise des passages des sources.

L’[offre de doctorat IRCAM](https://www.ircam.fr/fr/offres-emplois/doctorante--composition-musicale-assiste-par-ia), également consultée, sert de contexte pour les compétences visées. Ces QCM ne proviennent pas de l’IRCAM et ne prétendent pas reproduire ses entretiens. Les résultats décrivent une session ; ils ne constituent pas une mesure définitive du niveau.

## Modifier ou ajouter des questions

Les vrais JSON sont dans `public/data/`, avec un fichier par thème principal. `themes.json` définit les identifiants, libellés et noms des fichiers à charger. `src/bank.js` charge puis fusionne ces fichiers au démarrage.

Pour modifier une question, éditer son objet JSON en gardant son ID stable. Pour une nouvelle question, ajouter principalement un objet de cette forme et, si nécessaire, une entrée dans le registre de sources pertinent :

```json
{
  "id": "py-021",
  "primaryTheme": "python-scientifique",
  "themes": ["python-scientifique"],
  "difficulty": "intermediaire",
  "prompt": "Énoncé précis et autonome",
  "code": "x = ...\nprint(x)",
  "options": [
    { "id": "a", "text": "Proposition A" },
    { "id": "b", "text": "Proposition B" },
    { "id": "c", "text": "Proposition C" },
    { "id": "d", "text": "Proposition D" }
  ],
  "correctOptionId": "b",
  "explanation": "Explication spécifique en deux à cinq phrases.",
  "sourceIds": ["python-functions"]
}
```

Ce schéma illustratif n’est pas une question incluse dans la banque. Les quotas exacts de cette livraison sont volontairement contrôlés : pour agrandir la banque au-delà de 200, ajuster aussi les contraintes de `scripts/validate-bank.mjs`, `src/bank.js` et la limite de session dans `src/storage.js`. Pour conserver 200 questions, remplacer un QCM en respectant son quota. Les textes, options et codes sont rendus comme du texte, avec échappement HTML.

## Organisation

```text
src/main.js                  interface et interactions
src/style.css                mise en page et accessibilité
src/quiz.js                  filtrage, tirage, réponses, mode erreurs
src/stats.js                 scores globaux et multi-étiquettes
src/storage.js               sauvegarde, validation, empreinte de banque
src/bank.js                  chargement des JSON
public/data/                 banque, thèmes et sources
tests/quiz.test.mjs          tests de logique
scripts/validate-bank.mjs    contrôle de la banque
scripts/browser-test.mjs     parcours navigateur et captures
.github/workflows/pages.yml  publication GitHub Pages manuelle
```

## Données enregistrées

`localStorage` contient seulement la dernière session et la configuration : clés **`a-lecoute.session.v1`** et **`a-lecoute.settings.v1`**. Il n’y a ni compte, ni analyse d’usage, ni base distante. « Nouvelle session » et l’abandon confirmé effacent la session ; les réglages restent disponibles.

La sauvegarde dépend du navigateur, du profil et de l’origine HTTP (hôte et port). Elle ne se transfère pas entre appareils ou entre le serveur local et GitHub Pages. Effacer les données du site l’efface aussi. Les données corrompues ou incompatibles avec la banque courante sont écartées avec un message. Une modification de contenu dans la banque invalide les anciennes sessions pour éviter un bilan incohérent. Si le stockage est bloqué, un message le précise et le quiz fonctionne en mémoire jusqu’au rafraîchissement ou à la fermeture.

## Publier ultérieurement sur GitHub Pages

La livraison ne crée aucun dépôt distant et ne publie rien. La construction utilise `base: './'` : scripts, styles, favicon et JSON ont des chemins relatifs. Il n’y a aucun routeur ni besoin de réécriture serveur ; le même `dist/` peut être servi à la racine ou sous un chemin de dépôt.

Quand vous souhaitez publier :

1. Créer vous-même un dépôt GitHub et y pousser ces sources avec `package-lock.json`, en excluant `node_modules`, `.tools`, `dist` et `test-results` (déjà ignorés).
2. Dans **Settings → Pages → Build and deployment → Source**, sélectionner **GitHub Actions**.
3. Dans **Actions**, sélectionner **Publier sur GitHub Pages (manuel)**, puis **Run workflow** sur la branche contenant le projet. Le workflow ne se déclenche que manuellement.
4. Le workflow installe, teste, construit et publie `dist/`. Son environnement `github-pages` affiche ensuite l’URL du site.

Voir les [instructions officielles de Vite](https://vite.dev/guide/static-deploy.html#github-pages) et les [workflows Pages de GitHub](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages), consultés pour préparer cette configuration. L’exécution distante du workflow reste à faire lorsque vous déciderez de publier.

## Vérifications réalisées

Voir [VERIFICATION.md](VERIFICATION.md) pour les contrôles exécutés et leurs limites.
