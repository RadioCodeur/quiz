# Refonte pédagogique — 10 novembre 2026

## Le problème traité

La première version couvrait les QCM mais n’expliquait pas suffisamment pourquoi une notion arrivait à un endroit donné. Le cours Python introduisait notamment fonctions, dictionnaires et classes dans le même premier chapitre. Les exemples montraient un résultat sans assez expliciter les opérations intermédiaires, et les schémas étaient trop rares.

La nouvelle édition distingue donc la couverture des connaissances et la construction de leur compréhension. Une correspondance question/chapitre est une vérification nécessaire ; ce n’est pas une mesure de qualité pédagogique ni une preuve d’apprentissage.

## Choix de conception et références

| Choix dans le site | Référence consultée | Portée de la référence |
| --- | --- | --- |
| Un projet concret, un départ, une destination et des objectifs explicites | [The Carpentries — Motivation and Demotivation](https://carpentries.github.io/instructor-training/08-motivation.html) | Guide de formation d’enseignants pour relier contenu et objectifs des apprenants. |
| Un fil conducteur scientifique avant les détails de syntaxe | [Software Carpentry — Programming with Python](https://swcarpentry.github.io/python-novice-inflammation/) | Exemple de cours existant organisé autour d’une tâche d’analyse de données ; il ne constitue pas à lui seul une étude d’efficacité. |
| Des exemples entièrement résolus et une situation de transfert à essayer | [IES / What Works Clearinghouse — Organizing Instruction and Study to Improve Student Learning](https://ies.ed.gov/ncee/wwc/PracticeGuide/1) | Guide issu de recherches sur l’apprentissage. Les recommandations disposent de niveaux de preuve différents. |
| Des représentations visuelles proches de leur explication et un passage concret → abstrait | [Le même guide IES](https://ies.ed.gov/ncee/wwc/PracticeGuide/1), [ressources NumPy sélectionnées par ses contributeurs](https://numpy.org/learn/) | Le guide éclaire la méthode ; NumPy sert de référence technique et d’exemple de présentation visuelle, sans lui attribuer une efficacité expérimentale non démontrée. |
| Des rappels, un QCM facultatif et la possibilité de revenir plus tard | [AERO — Spacing and retrieval practice guide](https://www.edresearch.edu.au/guides-resources/practice-guides/spacing-and-retrieval-practice-guide-full-publication) | Guide de pratiques appuyées sur la recherche. Ce site n’impose pas de répétition espacée et n’a pas fait l’objet d’une évaluation contrôlée. |

Ces sources ont été consultées le 10 novembre 2026. Le registre utilisé par l’interface est `public/courses/pedagogy.json`. Les nouvelles références techniques propres aux cours sont stockées dans leur tableau `references`, puis fusionnées avec celles de la banque pour afficher les sources de chaque chapitre. Les textes et les exemples sont originaux ; les sources servent à vérifier et à orienter le contenu.

## Ajustement des introductions avec France-IOI

À la demande du lecteur, cette passe prend aussi pour références deux pages de **cours**, sans utiliser les exercices : [Faire des calculs](https://www.france-ioi.org/algo/course.php?idChapter=686&idCourse=1908) et [Fonctions à plusieurs paramètres](https://www.france-ioi.org/algo/course.php?iOrder=4&idChapter=493). Ces pages publiques ont été accessibles et consultées. Cette référence est un choix de présentation adapté à l’expérience antérieure du lecteur, pas une nouvelle revendication d’efficacité expérimentale.

Nous en retenons une progression de présentation : partir d’un usage compréhensible, montrer un cas très court et son résultat, expliquer les mots ou la syntaxe utilisés, puis modifier un seul élément pour rendre visible ce qui change. Les exemples, les nombres et le texte du site restent originaux et sont adaptés à l’IA audio ; aucune leçon ni aucun exercice France-IOI n’a été recopié.

Les six modules annoncent désormais explicitement leurs notions et leurs étapes. Les 65 chapitres disposent de notions définies et d’un premier exemple avec sortie, explication et variation. Les introductions ont été clarifiées pour éviter l’usage d’un mot technique avant sa présentation. Les grands déroulés, schémas, QCM de transfert, identifiants et correspondances avec les 200 questions sont conservés.

## Ce que le lecteur retrouve à chaque étape

1. Le problème concret du chapitre et ce qui sera utile ensuite.
2. Le rappel des notions déjà rencontrées et leur place dans le projet.
3. Une explication suivie, avec définitions introduites avant les détails.
4. Un exemple dont on peut suivre les étapes, les valeurs et les lignes de code.
5. Un schéma, tableau ou graphique pour représenter les relations.
6. Trois idées à retenir, puis une question de transfert facultative et sa correction.
7. Une transition explicite vers le prochain chapitre.

La présentation réduit la quantité d’éléments à suivre simultanément : pas de défilement automatique, de minuterie ou d’animation obligatoire ; le lecteur contrôle le déroulé et peut afficher toutes les étapes. Ce sont des choix d’ergonomie, sans promesse médicale ni garantie individuelle d’efficacité.

## Progression et lien avec la préparation à l’entretien

L’[offre de doctorat IRCAM](https://www.ircam.fr/fr/offres-emplois/doctorante--composition-musicale-assiste-par-ia), relue pour cette refonte, demande Python/PyTorch, traitement du signal audio, GNU/Linux et une démarche de recherche. Le sujet porte sur le contrôle multimodal, l’adaptation de modèles aux matériaux des compositeurs et le calcul limité. Le tableau décrit notre interprétation des compétences à préparer ; il ne prétend pas décrire les questions réelles de l’entretien.

| Cours | Fil conducteur | Compétences que l’on veut pouvoir expliquer |
| --- | --- | --- |
| Python scientifique — 13 chapitres | D’un fichier annoté à un exemple préparé pour un modèle | Lire des valeurs, références et fonctions ; organiser les métadonnées ; parcourir les données ; comprendre les tableaux, axes, réductions et calculs numériques ; assembler une préparation cohérente. |
| Signal audio — 9 chapitres | Du microphone à une représentation exploitable | Relier échantillons, durée et cadence ; expliquer aliasing, niveaux et Fourier ; choisir une STFT ; interpréter mel, phase et reconstruction. |
| PyTorch — 14 chapitres | Des exemples organisés à un modèle appris et évalué | Comprendre formes, paramètres, pertes et dérivées ; construire les batches et les masques ; lire une mise à jour ; distinguer entraînement et évaluation ; reprendre une expérience. |
| Apprentissage audio — 9 chapitres | Construire un système de reconnaissance de sons | Définir la cible ; maintenir un prétraitement cohérent ; choisir une représentation et une architecture ; exploiter un modèle préentraîné ; vérifier les augmentations, les annotations et l’agrégation. |
| Génération et contrôle — 10 chapitres | Produire une variante musicale en conservant une intention | Séparer codec et générateur ; expliquer tokens, probabilités, autorégression, VAE et diffusion ; choisir un conditionnement ; raisonner sur les ressources et l’adaptation. |
| Évaluation et recherche — 10 chapitres | Tester une amélioration contre une base et défendre la conclusion | Poser une question vérifiable ; organiser l’environnement Linux et les expériences ; éviter les fuites ; comprendre métriques, ablations et écoutes ; traiter variabilité et limites. |

## Vérification et limites

Les 200 questions d’origine restent reliées une fois chacune à un chapitre de leur thème principal. Les 57 anciens identifiants de chapitre restent valides. Les huit nouveaux chapitres donnent des fondations ou des étapes de synthèse : ils n’ont pas besoin d’avoir une question d’origine associée pour être utiles.

Le validateur contrôle également l’ordre des étapes, les contextes, les références, les quatre propositions de chaque QCM, les numéros de lignes des exemples et les coordonnées numériques des graphiques. La relecture scientifique et pédagogique reste indispensable ; ces contrôles ne démontrent ni l’absence de toute ambiguïté ni un effet mesuré sur l’apprentissage. Le parcours n’est pas une liste exhaustive de toutes les questions possibles, ni un remplacement de la pratique d’écriture de code, de la lecture d’articles et de la présentation orale de ses propres projets.
