# Refonte pédagogique — actualisation du 11 novembre 2026

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

Cette première passe ajoutait systématiquement un cas court et une variation dans les 65 chapitres. Le retour du lecteur a montré la limite de ce gabarit : il savait déjà programmer, et le cumul de petits cas ne construisait pas un chemin assez fluide.

## Révision à partir du niveau réel du lecteur

Le lecteur indique un niveau 3–4 de France-IOI en Python algorithmique. La révision du 11 novembre suppose donc variables, listes, boucles et fonctions acquises. Deux rappels restent accessibles en complément, tandis que le parcours principal Python commence par un contrat de données puis les tableaux numériques. Les anciennes ancres et les repères de lecture restent valides.

Les pages publiques du parcours « Progresser » ont été consultées, notamment les explications intégrées aux découvertes [Préparation de l’onguent](https://www.france-ioi.org/algo/task.php?idChapter=651&idTask=2068), [Grand inventaire](https://www.france-ioi.org/algo/task.php?idChapter=651&idTask=2072), [Journée des cadeaux](https://www.france-ioi.org/algo/task.php?idChapter=651&idTask=2079) et [Punition](https://www.france-ioi.org/algo/task.php?idChapter=643&idTask=1876), ainsi que les cours [Structurer un programme](https://www.france-ioi.org/algo/course.php?idChapter=509&idCourse=1594) et [Précision des calculs](https://www.france-ioi.org/algo/course.php?idChapter=650&idCourse=1875). Il s’agit d’un échantillon lu des contenus publics des niveaux 1–2, pas d’une revendication d’accès aux corrections privées ou aux niveaux verrouillés.

Le principe retenu est le besoin avant l’outil : montrer ce qu’une solution déjà connue ne permet pas de faire, introduire le moyen adapté, puis expliquer le résultat sur le même problème. [OpenClassrooms — Transformez vos données en tableaux](https://openclassrooms.com/fr/courses/7771531-decouvrez-les-librairies-python-pour-la-data-science/7857032-transformez-vos-donnees-en-tableaux), également consulté, montre comment le sens métier des lignes et colonnes précède les opérations. Ces références éditoriales ne sont pas présentées comme une évaluation expérimentale de notre site. Le texte, les données et les scénarios audio restent originaux.

Les 65 chapitres ont été relus et réécrits autour de besoins suivis. Dans Python, deux signaux miniatures reviennent pour construire RMS, facteur de crête, tableau de caractéristiques et standardisation. Leur RMS identique motive réellement le deuxième descripteur. Le changement vers des formes ou données différentes est annoncé. Dans AudioML, le passage des classes exclusives aux mélanges est un changement de cahier des charges explicite. Dans Génération, VAE et diffusion sont des branches possibles, pas une succession d’améliorations garantie.

Les repères de début sont raccourcis à trois éléments (entrée, action, résultat). Les définitions restent dépliables. Les exemples courts, variantes et encadrés répétitifs sont retirés lorsqu’ils n’apportent rien ; un déroulé résolu et une représentation utile restent présents. Les termes scientifiques sont définis dans le corps avant leur emploi. Les exemples de code sont lus, pas exécutés par l’interface.

## Progression et lien avec la préparation à l’entretien

L’[offre de doctorat IRCAM](https://www.ircam.fr/fr/offres-emplois/doctorante--composition-musicale-assiste-par-ia), relue pour cette refonte, demande Python/PyTorch, traitement du signal audio, GNU/Linux et une démarche de recherche. Le sujet porte sur le contrôle multimodal, l’adaptation de modèles aux matériaux des compositeurs et le calcul limité. Le tableau décrit notre interprétation des compétences à préparer ; il ne prétend pas décrire les questions réelles de l’entretien.

| Cours | Fil conducteur | Compétences que l’on veut pouvoir expliquer |
| --- | --- | --- |
| Python scientifique — 13 chapitres | D’un fichier annoté à un exemple préparé pour un modèle | Lire les axes ; distinguer vues, copies et état partagé ; calculer RMS et facteur de crête ; standardiser sur le train ; conserver les cibles et assembler la préparation. |
| Signal audio — 9 chapitres | Du microphone à une représentation exploitable | Relier échantillons, durée et cadence ; expliquer aliasing, niveaux et Fourier ; choisir une STFT ; interpréter mel, phase et reconstruction. |
| PyTorch — 14 chapitres | Des exemples organisés à un modèle appris et évalué | Comprendre formes, paramètres, pertes et dérivées ; construire les batches et les masques ; lire une mise à jour ; distinguer entraînement et évaluation ; reprendre une expérience. |
| Apprentissage audio — 9 chapitres | Construire un système de reconnaissance de sons | Définir la cible ; maintenir un prétraitement cohérent ; choisir une représentation et une architecture ; exploiter un modèle préentraîné ; vérifier les augmentations, les annotations et l’agrégation. |
| Génération et contrôle — 10 chapitres | Produire une variante musicale en conservant une intention | Séparer codec et générateur ; expliquer tokens, probabilités, autorégression, VAE et diffusion ; choisir un conditionnement ; raisonner sur les ressources et l’adaptation. |
| Évaluation et recherche — 10 chapitres | Tester une amélioration contre une base et défendre la conclusion | Poser une question vérifiable ; organiser l’environnement Linux et les expériences ; éviter les fuites ; comprendre métriques, ablations et écoutes ; traiter variabilité et limites. |

## Vérification et limites

Les 200 questions d’origine restent reliées une fois chacune à un chapitre de leur thème principal. Les 57 anciens identifiants de chapitre restent valides. Les huit nouveaux chapitres donnent des fondations ou des étapes de synthèse : ils n’ont pas besoin d’avoir une question d’origine associée pour être utiles.

Le validateur contrôle également l’ordre des étapes, les contextes, les références, les quatre propositions de chaque QCM, les numéros de lignes des exemples et les coordonnées numériques des graphiques. La relecture scientifique et pédagogique reste indispensable ; ces contrôles ne démontrent ni l’absence de toute ambiguïté ni un effet mesuré sur l’apprentissage. Le parcours n’est pas une liste exhaustive de toutes les questions possibles, ni un remplacement de la pratique d’écriture de code, de la lecture d’articles et de la présentation orale de ses propres projets.
