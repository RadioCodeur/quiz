# Mise en œuvre de l’audit pédagogique — 18 novembre 2026

Point de départ : commit `57fce919006dcf1edbf6aeadd4eb67f54d657453`, huit modules et 107 chapitres. La demande du 18 novembre remplace les contraintes éditoriales précédentes : les finales « À dire en entretien » ne sont plus obligatoires et les checkpoints peuvent être améliorés. Les identifiants, liens, sources et progrès utiles restent compatibles ; les 200 questions du quiz restent inchangées.

## Constats vérifiés dans les sources

Les scores fictifs ne sont expliqués qu’après le code. Le premier Dataset mélange objets, dépaquetage, padding et masque. Le premier modèle emploie ModuleList et un buffer. La rétropropagation ne surligne pas retain_grad. Les notebooks recopient une démonstration dans une cellule et laissent les exercices en Markdown. Les réponses orales sont déjà repliées ; l’audit demande surtout des pistes avant le modèle et des relances présentées comme possibles.

## Réalisation

1. Refaire quatre exemples de référence : tenseurs/types, scores/axes, Linear et mise à jour. Conventions avant les lignes, calcul manuel, états intermédiaires, sens des arguments et effet d’une modification.
2. Réordonner PyTorch pour construire tôt une boucle minimale. Séparer données fixes et padding, premier module et buffers, optimisation courante et CUDA/AMP, préparation mel et convolution/autoencodeur. Garder les ancres existantes ; créer de nouveaux chapitres uniquement si la séparation aide.
3. Ajouter des supports de calcul : cases et axes, réduction, reshape/transpose, broadcasting, Linear, gradient, padding et convolution. Une interaction JavaScript est annoncée comme calcul pédagogique, jamais comme exécution PyTorch.
4. Renforcer les walkthroughs : plus d’étapes si nécessaire, lignes exactes, détail local repliable, valeurs/formes et mutation. Étiqueter les extraits et programmes autonomes avant le code. Déplacer l’accès aux notebooks après la première explication.
5. Revoir l’ensemble des autres modules selon leur difficulté : indexations Python, fichiers et paramètres Signal, contrats des extraits Audio ML, étapes des familles génératives, jeu d’évaluation stable, niveaux de préparation du contexte et pistes orales. Retirer les doublons, traces internes et finales automatiques après lecture de chaque chapitre.
6. Reconstruire les notebooks concernés en cellules progressives, états visibles, cellules d’exercice prêtes, indices et solutions distincts. Exécuter réellement les démonstrations et solutions sur CPU ; conserver les preuves.
7. Vérifier calculs, couverture des 200 QCM, ancres et progrès ; tester erreurs ciblées, étapes, détails, visuels, clavier, retour au chapitre, fenêtres étroites et zoom 200 %. Mettre à jour les tests de comportement et retirer ceux qui imposent les anciennes contraintes éditoriales.
8. Relire des trajets complets comme un apprenant. Documenter les changements et limites, lancer les commandes du dépôt, puis pousser et publier sur GitHub Pages.

## Contrat des enrichissements

Les blocs existants restent disponibles. Les walkthroughs peuvent contenir des étapes plus fines et `step.details: [{code, explanation, state}]` pour le rappel local. Un code porte `codeMode: "standalone"` ou `"excerpt"` ; un extrait annonce `requires: ["objet et contrat"]`. `checkpoint.optionFeedback` peut fournir une explication par identifiant d’option. Les chapitres peuvent porter `level: "practice" | "discuss" | "advanced"` et des liens de prérequis. Les calculs interactifs sont des blocs `tensor-lab`, rendus et vérifiés séparément.

## Suivi

- [x] Exemples représentatifs et socle PyTorch
- [x] Approfondissements PyTorch et progression
- [x] Python, Signal et Apprentissage audio
- [x] Génération, Évaluation, Contexte et Oral
- [x] Composants, navigation et exercices implémentés et vérifiés dans Edge
- [x] Notebooks et exécutions CPU : 32 notebooks liés et preuves conservées
- [x] Tests unitaires : 59 tests réussis ; anciennes contraintes de finales automatiques retirées
- [x] Vérifications navigateur et relecture : 33 contrôles réussis, 120 chapitres rendus à 360 px ; sources et prérequis relus par module
- [x] Vérification finale, push et publication GitHub Pages : commit applicatif `3bbeb56`, workflow `44442432394` réussi, huit modules et 32 notebooks publics comparés aux fichiers locaux le 19 novembre 2026

Le corpus fusionné contient 120 chapitres. `scripts/audit-prose.mjs` signale les phrases de plus de 30 mots et les chapitres de plus de 1 100 mots sans justification. Ces seuils orientent la relecture ; ils ne prouvent pas la qualité pédagogique. Aucune conclusion type ni présence d’un mot-clé n’est imposée.
