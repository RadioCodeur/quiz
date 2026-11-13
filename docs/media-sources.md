# Illustrations externes des cours

Sélection vérifiée le **12 novembre 2026**. Les cinq fichiers sont servis localement depuis `public/media/references/` ; aucune image n’est chargée à chaud chez un tiers pendant la lecture. Le registre d’affichage `public/media/illustrations.json` contient le titre, le texte alternatif, la légende, quatre indications de lecture, l’auteur, la page source, la licence choisie et les changements.

Les licences ci-dessous concernent les **fichiers illustrés**, et non la licence générale du texte de Wikimedia Commons. Quand plusieurs licences sont proposées, la licence Creative Commons indiquée a été choisie. Les images originales n’ont pas été recadrées, recolorées ni annotées dans leurs pixels ; les commentaires français sont affichés séparément. Les licences d’origine restent attachées à ces images, indépendamment du code du site.

| Identifiant | Auteur et source | Licence retenue | Usage et limite explicite |
| --- | --- | --- | --- |
| `speech-praat` | Ish ishwar — [Spectrogram -minato-.png](https://commons.wikimedia.org/wiki/File:Spectrogram_-minato-.png) | [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) | Vraie parole japonaise analysée avec Praat ; lecture du temps, des fréquences et des régions sombres. Préaccentuation source de 5 dB/octave ; absence de calibration SPL. Cette image n’est pas calculée depuis nos extraits de narration et de caisse claire. |
| `stft-windows` | Д.Ильин, vectorisation d’après Johnteslade~commonswiki — [STFT - windows-en.svg](https://commons.wikimedia.org/wiki/File:STFT_-_windows-en.svg) | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) | Grille qualitative du compromis temps/fréquence, sans mesures. Le [dessin source de Johnteslade](https://commons.wikimedia.org/wiki/File:STFT_-_windows.png) est lui aussi explicitement placé dans le domaine public. |
| `mel-hertz` | Krishna Vedala — [Mel-Hz plot.svg](https://commons.wikimedia.org/wiki/File:Mel-Hz_plot.svg) | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) | Courbe de conversion logarithmique hertz/mels. Ce n’est ni une matrice mel, ni une mesure d’audition individuelle ; la convention représentée doit être distinguée de celle du calcul pratique. |
| `cnn-convolution` | Daniel Voigt Godoy — [Convolutional neural network, convolution worked example.png](https://commons.wikimedia.org/wiki/File:Convolutional_neural_network,_convolution_worked_example.png), provenant de [dl-visuals](https://github.com/dvgodoy/dl-visuals/) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | Calcul détaillé d’une sortie de convolution et effet du padding. La matrice est un exemple numérique de l’auteur, pas un spectrogramme réel ni le résultat d’un réseau appris pour le cours. |
| `confusion-matrix` | Jackverr — [ConfusionMatrix.png](https://commons.wikimedia.org/wiki/File:ConfusionMatrix.png) | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) | Orientation des axes et localisation TP/FP/FN/TN. Le dessin ne contient aucun décompte ; les commentaires relient ces cases à un détecteur de voix sans inventer de performance. |

## Lecture visuelle et vérification

Les trois PNG ont été ouverts et inspectés avec le lecteur d’images. Les deux SVG ont été rendus dans Microsoft Edge puis inspectés sous forme de captures locales. L’orientation des axes et les détails décrits dans les commentaires ont été vérifiés sur les fichiers téléchargés, pas uniquement sur la description de leur page.

Pour la convolution, la case rouge est vérifiable : les contributions non nulles sont `5 - 8 + 4 + 6 = 7`. Pour la matrice de confusion, les lignes sont les prédictions et les colonnes la réalité ; certains outils utilisent l’orientation inverse. Les SVG ne contiennent pas de script et n’appellent pas de ressource extérieure.

La capture Praat du mot « Wikipedia », initialement envisagée, n’a pas été retenue : elle superpose plusieurs licences de composants d’interface et n’apporte pas un avantage clair sur l’image de parole à licence unique choisie. L’image `Mel RMel.png` n’a pas été retenue non plus : elle compare une variante R-Mel à gauche au banc Mel à droite, sans axes gradués. L’ajouter au cours de base introduirait une variante inutile et risquerait d’être prise pour une simple démonstration du banc Mel. Le banc réellement utilisé par l’atelier est représenté par un graphique calculé avec ses paramètres explicites.

## Fichiers d’origine et intégrité

`scripts/download-reference-images.py` retélécharge uniquement les cinq URL d’origine explicites, sans identifiants ni exploration d’autres sites. Les empreintes SHA-256 sont conservées dans le registre. Les originaux totalisent environ **455 Kio**.

| Fichier local | SHA-256 |
| --- | --- |
| `speech-praat.png` | `92a7bf663789e06f8fd067cd299621242f5c19a5414a63302d29d1a8b8db5425` |
| `stft-windows.svg` | `7dc0b80c482cd3e019d8d0f06edbd6c0b6acf71a2deb9fd27ac89a85cdfec46f` |
| `mel-hertz.svg` | `d2a7bdcff8bd035cd40b3af61d25c067d3515f3b01b6b393a710eecb6b2d6730` |
| `cnn-convolution.png` | `772620e38f5462452eff317ccdbe29b3a34377c52968229eeafa278defdb474d` |
| `confusion-matrix.png` | `7ba8cbed7b693c3052963e7e915ea77dc13e98d3600427754bae59aa32568bb7` |

Ces illustrations externes sont distinctes des formes d’onde, STFT, spectrogrammes mel et mesures calculés depuis les fichiers audio livrés. Les secondes servent aux comparaisons quantitatives et à la continuité entre transformations ; les premières donnent un autre exemple documenté ou rendent un mécanisme plus visible.
