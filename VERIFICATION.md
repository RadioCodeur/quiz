# Vérification de la livraison

Contrôles locaux actualisés le **10 novembre 2026**, avec Node.js 24.22.1 et Microsoft Edge piloté par Playwright.

- **Banque validée** : exactement 200 QCM, quotas principaux 20/50/30/30/40/30, 60/100/40 par difficulté, 99 questions avec code, 88 entrées de sources, IDs uniques, quatre options distinctes, bonne réponse existante, thèmes valides, explications présentes et références résolues.
- **24 tests de logique réussis** : les 12 contrôles du quiz sont conservés. Les cours vérifient désormais schéma, couverture, prérequis, liens et progression, mais aussi conservation des 57 anciens identifiants, ordre des étapes, fusion des références, durée incluant les explications, géométrie des graphiques, échappement du texte, surlignage des lignes et QCM de transfert indépendants de l’ordre des propositions.
- **19 contrôles navigateur réussis** : parcours du quiz, reprise, bilan, erreurs, clavier et stockage dégradé ; navigation quiz/cours sans perte de session ; lecture et préférences ; affichage de tous les 65 chapitres à 360 px ; étapes de code avec états et numéros de ligne vérifiés ; QCM de transfert juste/faux et verrouillage ; graphique et tableau de valeurs ; projet et sources pédagogiques visibles ; anciens liens ; deux pages construites sous `/qr-entretien/`. Certains contrôles regroupent plusieurs assertions. Le lien d’évitement au clavier conserve le chapitre en cours.
- **Cours édition 2 validés** : six thèmes, 65 chapitres, 200 questions reliées une fois chacune, 65 exemples guidés, 65 nouveaux schémas relationnels, 15 graphiques numériques, 7 figures complémentaires et 65 QCM de transfert. Chaque chapitre présente rappel, problème, utilité et transition. Les 59 extraits de code sont à lire ; l’application ne les exécute pas. Environ 40 000 mots hors code. Relecture pédagogique effectuée ; le contrôle automatique des correspondances ne suffit pas à prouver la compréhension des notions.
- **Construction Vite réussie**, puis application construite servie et testée à travers un serveur statique sous un chemin de dépôt. Aucun appel réseau de l’application vers une API extérieure.
- **Lanceur Windows corrigé et testé sans Node dans le PATH** : lancement réel de `Lancer.cmd` dans un environnement Windows réduit, recherche automatique du runtime local, réponse HTTP du serveur et accès aux 200 questions vérifiés. Test reproductible avec `node scripts/test-windows-launcher.mjs` ; le serveur de test est arrêté automatiquement.
- **Captures ordinateur et mobile inspectées visuellement**, notamment la configuration, une question avec code et la correction. Absence de débordement horizontal de page vérifiée à 360 px ; le code défile dans son propre conteneur.
- **Relecture pédagogique** des banques et consultation des références primaires pendant leur rédaction. Les vérifications structurelles ne sont pas une preuve automatique de justesse scientifique ; les extraits Python n’ont pas été exécutés. Ils sont destinés à être lus, comme demandé.

Captures reproductibles : `test-results/desktop-configuration.png`, `desktop-correction.png`, `desktop-bilan.png`, `mobile-configuration.png`, `mobile-question.png`, `mobile-correction.png`, `mobile-bilan.png`.

Captures des cours : `courses-desktop-overview.png`, `courses-desktop-chapter.png`, `courses-mobile-overview.png` et `courses-mobile-chapter.png`, dans le même dossier. Elles ont été inspectées visuellement. Le portrait de Squoinks a été généré avec ImageGen et inspecté ; son prompt est conservé dans `docs/illustration-squoinks.md`.

Captures de la refonte : `courses-desktop-worked-example.png`, `courses-mobile-worked-example.png`, `courses-numeric-plot.png` et `courses-revised-python-introduction.png`. Les méthodes et leur portée sont documentées dans `docs/pedagogie.md`. Les cinq références pédagogiques du catalogue sont séparées des références techniques des chapitres.

Limites des contrôles locaux : pas de test sur téléphone physique, Safari ou Firefox ; pas d’audit formel d’accessibilité par lecteur d’écran. L’émulation mobile vérifie la mise en page dans Edge. Le déploiement et les vérifications sur le site public sont effectués séparément au moment de la publication. Aucune prétention à reproduire les véritables questions d’entretien de l’IRCAM, ni à garantir un effet individuel sur l’apprentissage.

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
