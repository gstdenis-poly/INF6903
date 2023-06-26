# Soumissionnaire intelligent de solutions logicielles pour application de processus d’affaires
### _Par Gabriel St-Denis sous la direction de Guillaume-Alexandre Bilodeau (Ph.D.)_

## Fonctionnalités
- Capture des données d'intérêts
- Détection des objets d'intérêts
- Interprétation des objets textuels
- Reconnaissance d'activités
- Reconnaissance de processus

## Technologies
- [Python3] - implémentation des côtés client et serveur
- [FFmpeg] - capture vidéo d'écran
- [pynput] - capture d'événements clavier et souris
- [UIED] - détection et classification d'éléments GUI
- [PaddleOCR] - détection de texte sur image
- [Keras] - classification par réseau de neurones
- [Scikit-learn] - apprentissage machine en Python

## Installation
L'application utilise des technologies multiplateforme mais n'a été testée que sur Unix. Les étapes d'installation de celle-ci pour un bon fonctionnement sur environnement Windows pourraient différer des étapes ci-dessous.

### Client
- Exécuter le script d'installation du client:
```sh
cd client
bash ./installer.sh
```
### Serveur
- Exécuter le script d'installation du serveur:
```sh
cd server
bash ./installer.sh
```
- (Optionnel: au besoin) Remplacer "from collections" par "from collections.abc" partout dans le site-packages attrdict de l'installation de Python3.
- (Optionnel: au besoin) Réinstaller libbz2-dev avec sudo apt-get install.
- Ajuster les chemins de dossiers définis dans server/configurator.py et s'assurer que tous les dossiers existent sur le serveur.
- Exécuter configurator.py avec python3.
- Ajuster les scripts d'exécution .sh pour qu'ils pointent sur l'emplacement exact de l'exécutable python3 et qu'ils utilisent un workload manager distinct de Slurm si nécessaire.

## Licence
Polytechnique Montréal
INF6903 - Projet de maîtrise en ingénierie III

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [Python3]: <https://www.python.org/>
   [FFmpeg]: <https://ffmpeg.org/>
   [pynput]: <https://pypi.org/project/pynput/>
   [UIED]: <https://github.com/MulongXie/UIED>
   [PaddleOCR]: <https://github.com/PaddlePaddle/PaddleOCR>
   [Keras]: <https://keras.io/>
   [Scikit-learn]: <https://scikit-learn.org/stable/index.html>

