# Vérification de la livraison

Contrôles locaux effectués le **5 novembre 2026**, avec Node.js 24.22.1 et Microsoft Edge piloté par Playwright.

- **Banque validée** : exactement 200 QCM, quotas principaux 20/50/30/30/40/30, 60/100/40 par difficulté, 99 questions avec code, 88 entrées de sources, IDs uniques, quatre options distinctes, bonne réponse existante, thèmes valides, explications présentes et références résolues.
- **17 tests de logique réussis** : union de thèmes sans doublons ; formats et valeurs par défaut ; tirages sans remise ; mélange sans mutation et réponses conservées par ID ; verrouillage et passage protégé ; scores globaux et multi-étiquettes ; mode erreurs sous 10 questions ; sérialisation ; stockage indisponible ; JSON corrompu ; session incohérente ; banque modifiée. Cinq tests dédiés vérifient aussi les cours : schéma, couverture question/chapitre, liens, prérequis, ancres et progression de lecture indépendante.
- **15 contrôles navigateur réussis** : configuration et filtrage ; bonnes et mauvaises réponses avec correction ; verrouillage des boutons ; reprise exacte après rafraîchissement ; fin de session avec score attendu 9/10 ; carnet d’erreurs ; reprise d’une seule erreur ; session parfaite ; nouvelle session ; abandon confirmé ou annulé ; sauvegardes invalides ; stockage bloqué sur un parcours entier ; clavier ; rendu à 360 px ; construction sous `/qr-entretien/` avec chargement des assets et des JSON. Les cours sont aussi parcourus : lien depuis une correction vers le bon chapitre, conservation de la session du quiz, lecture et préférences après rafraîchissement, navigation et historique, rendu des 57 chapitres à 360 px, stockage bloqué et ancien lien. Certains contrôles regroupent plusieurs assertions.
- **Cours validés** : six thèmes, 57 chapitres, 200 questions reliées une fois chacune, prérequis dans l’ordre du parcours, références existantes, trois points à retenir par chapitre et développement explicatif. Environ 21 000 mots hors code, 51 exemples de code, 53 exemples concrets et 13 schémas. Relecture pédagogique effectuée ; le contrôle automatique des correspondances ne suffit pas à prouver la compréhension des notions.
- **Construction Vite réussie**, puis application construite servie et testée à travers un serveur statique sous un chemin de dépôt. Aucun appel réseau de l’application vers une API extérieure.
- **Lanceur Windows corrigé et testé sans Node dans le PATH** : lancement réel de `Lancer.cmd` dans un environnement Windows réduit, recherche automatique du runtime local, réponse HTTP du serveur et accès aux 200 questions vérifiés. Test reproductible avec `node scripts/test-windows-launcher.mjs` ; le serveur de test est arrêté automatiquement.
- **Captures ordinateur et mobile inspectées visuellement**, notamment la configuration, une question avec code et la correction. Absence de débordement horizontal de page vérifiée à 360 px ; le code défile dans son propre conteneur.
- **Relecture pédagogique** des banques et consultation des références primaires pendant leur rédaction. Les vérifications structurelles ne sont pas une preuve automatique de justesse scientifique ; les extraits Python n’ont pas été exécutés. Ils sont destinés à être lus, comme demandé.

Captures reproductibles : `test-results/desktop-configuration.png`, `desktop-correction.png`, `desktop-bilan.png`, `mobile-configuration.png`, `mobile-question.png`, `mobile-correction.png`, `mobile-bilan.png`.

Captures des cours : `courses-desktop-overview.png`, `courses-desktop-chapter.png`, `courses-mobile-overview.png` et `courses-mobile-chapter.png`, dans le même dossier. Elles ont été inspectées visuellement. Le portrait de Squoinks a été généré avec ImageGen et inspecté ; son prompt est conservé dans `docs/illustration-squoinks.md`.

Limites : pas de publication réelle sur GitHub Pages ni d’exécution distante du workflow ; pas de test sur téléphone physique, Safari ou Firefox ; pas d’audit formel d’accessibilité par lecteur d’écran. L’émulation mobile vérifie la mise en page dans Edge. Aucune prétention à reproduire les véritables questions d’entretien de l’IRCAM.

Pour reproduire :

```powershell
npm ci
npm run validate
npm run validate:courses
npm test
npm run build
npm run test:browser
```

Si npm n’est pas dans le PATH, utiliser `node scripts/run.mjs` suivi du nom du script (`validate`, `test`, `build`, `test:browser`).
