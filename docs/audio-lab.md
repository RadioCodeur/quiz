# Voir et entendre les mêmes enregistrements

Livraison du 13 novembre 2026. Les cours restent un site statique : les images et les sons sont calculés avant publication, et le navigateur ne charge aucun modèle ni interpréteur Python.

## Un corpus réel et des dérivés identifiés

Deux extraits de quatre secondes sont servis localement. La voix provient du corpus LibriSpeech ; la caisse claire est un montage accéléré de frappes enregistrées, publié dans les exemples Librosa. Ce montage n’est pas présenté comme une prise jouée en continu. Leurs sources étaient mono à 16 kHz et 22,05 kHz ; leur référence commune à 48 kHz est interpolée, sans gain initial. Cette interpolation n’invente pas de nouveaux aigus.

Les auteurs, pages sources, URL de téléchargement, licences CC BY 4.0, transformations et empreintes figurent dans `public/media/audio-lab.json`. Les fichiers d’origine et les mentions de licence accompagnent les WAV sous `public/media/audio/sources/`. Les cinq illustrations externes ont leurs licences propres, détaillées dans `docs/media-sources.md` ; elles ne sont pas confondues avec les images calculées sur nos extraits.

Chaque son possède neuf versions : référence, gain de 0,5, RMS commun de 0,08, rééchantillonnage à 16 kHz, passe-bas à 1 kHz, écrêtage, inversion de polarité, annulation de deux canaux construits et reconstruction à phase aléatoire. L’annulation est une expérience construite depuis une prise mono, pas une caractéristique stéréo de l’original. La reconstruction à phase aléatoire conserve le module de la STFT cible avant projection ; le module de la nouvelle STFT du WAV obtenu n’est pas garanti identique.

## Ce que les mesures permettent de conclure

Les mesures sont refaites après écriture puis relecture des WAV PCM16. La crête est `max(abs(x))`, le carré moyen `mean(x²)`, le RMS sa racine. Les niveaux numériques utilisent toujours la référence d’amplitude 1, y compris pour le RMS. Cette convention diffère des outils étalonnant une sinusoïde pleine échelle à 0 dBFS RMS. Les prises ne sont pas calibrées en pascals, watts ou dB SPL. Une RMS commune ne garantit pas la même sonie perceptive.

| Fichier de référence | Crête | RMS | Niveau RMS (réf. 1) | Facteur de crête |
| --- | --- | --- | --- | --- |
| Voix parlée | 0.8021 | 0.1207 | -18.36 dBFS | 16.45 dB |
| Caisse claire | 0.6526 | 0.0637 | -23.91 dBFS | 20.20 dB |

Après accord au RMS 0,08, les deux niveaux valent environ −21,94 dBFS RMS, mais les crêtes valent environ 0,5315 pour la voix et 0,8190 pour la percussion. La seconde a donc moins de marge pour ses pics. Ce résultat concerne ces extraits et leurs conditions d’enregistrement ; il ne classe pas la puissance acoustique naturelle de la voix et de la caisse claire.

## Lire les images

Les 54 cartes de variantes sont calculées depuis les WAV effectivement joués : forme d’onde, STFT, mel pour chacune des 18 versions. Les sept analyses complémentaires montrent une fenêtre réelle pondérée, le compromis 10/80 ms, le banc de filtres, les niveaux, la bande du rééchantillonnage, les axes du tenseur et un masque sur une entrée mel réelle.

La forme d’onde conserve les minima et maxima de tranches d’affichage. Les STFT utilisent Hann 25 ms et hop 10 ms. Le carré de magnitude est normalisé par la somme de la fenêtre avant projection mel. Les images utilisent une référence spectrale fixe de 1 et une échelle de couleur de −100 à 0 dB ; elles ne sont pas renormalisées individuellement. Cette référence spectrale n’est ni le dB SPL ni le RMS dBFS du fichier. Les 64 filtres mel Slaney sont normalisés en aire, entre 0 et 8 kHz ; leurs couleurs ne sont pas directement interchangeables avec celles des bins STFT. Les zones hachurées signalent une bande non représentable, pas une énergie mesurée nulle.

Les paramètres détaillés, légendes, lectures guidées et sources sont dans les deux manifestes locaux. Le cours distingue explicitement l’analyse d’une seconde sans centrage (98 trames à 16 kHz) des images de quatre secondes centrées (401 trames).

## Utilisation et vérification

Le lecteur démarre uniquement sur action du lecteur. Un curseur commun règle le volume des deux extraits à partir de 0,5 ; il ne change ni les fichiers ni les mesures. Le démarrage d’une écoute arrête l’autre, et la navigation arrête le son. Changer de représentation conserve l’audio en cours ; changer de transformation repart en pause. Les mesures et les paramètres sont dépliables, les images agrandissables. Les fichiers sont locaux, avec `preload="none"` pour les lecteurs et chargement différé des images.

Les nouveaux blocs sont `audio-lab`, `illustration` et `analysis-image`. Le laboratoire présente des transformations déterministes ; il ne prétend entraîner un modèle, exécuter un codec appris ni constituer un test perceptif aveugle.

Pour contrôler les médias existants :

```powershell
node scripts/run.mjs validate:media
python scripts/build-audio-media.py --verify
```

Pour régénérer les analyses : installer les dépendances de `scripts/requirements-media.txt`, puis exécuter `python scripts/build-audio-media.py`. `scripts/download-reference-images.py` retélécharge les cinq illustrations externes. Python est uniquement nécessaire à la fabrication des assets, pas à la lecture ni au déploiement du site.
