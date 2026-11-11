# Vérification de la livraison

Révision éditoriale du **11 novembre 2026**, adaptée à un lecteur connaissant déjà le Python algorithmique.

## Contenu et cohérence

- Six modules et 65 chapitres, dont deux rappels Python facultatifs en fin de sommaire. Les 65 identifiants et les associations aux 200 QCM sont comparés à la version publiée précédente et conservés. La banque du quiz reste inchangée.
- Les développements, projets et transitions ont été réécrits. Les signaux miniatures du Python servent successivement à calculer RMS, facteur de crête, caractéristiques et standardisation ; leurs sorties sont exécutées et vérifiées. Les changements de taille ou de scénario sont annoncés.
- Les 65 exemples guidés et les 65 représentations relationnelles sont présents. Les cas courts passent de 65 à 8 : les exemples de syntaxe élémentaire et les variantes répétitives ont été retirés. Les variantes conservées et les définitions se déplient à la demande.
- Les pages publiques de cours et de découverte France-IOI citées dans `docs/pedagogie.md` ont été lues, y compris des explications intégrées aux énoncés. OpenClassrooms a également été consulté. Aucun accès aux corrections privées ou aux niveaux verrouillés n’est revendiqué ; les scénarios et les textes audio sont originaux.
- Relecture de la couverture scientifique des QCM par thème. Les correspondances automatiques prouvent la présence d’un lien, pas la compréhension du lecteur ni une exhaustivité de toutes les questions d’entretien possibles.

## Vérifications techniques

- Banque validée : exactement 200 QCM, quotas principaux 20/50/30/30/40/30 et 60/100/40 par difficulté ; identifiants, propositions et références résolus.
- **29 tests de logique** : quiz, progression, liens historiques, schéma, couverture, références, géométrie des graphiques, échappement des sorties, exemples sans variante et navigation principale sans obligation de lire les rappels.
- **20 contrôles navigateur** : session du quiz, reprise, bilan, clavier et stockage indisponible ; navigation quiz/cours ; repères de lecture et préférences ; rendu des 65 chapitres à 360 px ; états et lignes des exemples guidés ; QCM de transfert ; tableaux des graphiques ; présentation des modules ; définitions repliables ; rappels par lien direct ; deux entrées Vite sous un chemin de dépôt. Certains contrôles regroupent plusieurs assertions.
- Construction Vite après validation des données, puis test du site construit sous `/qr-entretien/`. Aucun interpréteur Python ni nouvelle API extérieure n’est ajouté à l’application.
- Les extraits scientifiques modifiés sont vérifiés en Python avec NumPy, SciPy, librosa et PyTorch selon le thème. Les blocs partiels utilisent des données et objets de contexte explicites pendant la vérification. Aucun modèle audio complet n’a été entraîné pour cette révision.
- Un problème de l’ancien exemple Dropout est corrigé : `eval()` peut laisser Dropout retourner son entrée ; `no_grad()` ne retire pas rétroactivement `requires_grad` à cette entrée. L’exemple observe désormais une opération nouvelle dans ce contexte pour illustrer correctement la désactivation de l’enregistrement du graphe.

Les contrôles sont exécutés avec Node.js 24 et Microsoft Edge piloté par Playwright. Les captures du parcours dans `test-results/` sont des fichiers de vérification locaux, non publiés. Les vérifications du déploiement public sont effectuées séparément après la publication.

Le lanceur Windows a été corrigé et testé sans Node dans le PATH lors de la livraison précédente ; il est inchangé. Aucun test sur téléphone physique, Safari ou Firefox, ni audit formel par lecteur d’écran n’est revendiqué.

## Reproduire

```powershell
npm run validate
npm run validate:courses
npm test
npm run build
npm run test:browser
```

Si npm n’est pas dans le PATH, utiliser `node scripts/run.mjs` suivi du nom du script.
