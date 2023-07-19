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
- Générer l'exécutable client avec la commande pyinstaller recorder.py --onefile -F --icon logo.ico.
- Téléverser l'exécutable sur le serveur pour permettre son téléchargement via l'application Web.
- Démarrer le tunnel SSH suivant: sshpass -p SSH_PASS ssh -L 8000:localhost:8000 SSH_ADDRESS.
### Serveur
- Exécuter le script d'installation du serveur:
```sh
cd server
bash ./installer.sh
```
- (Optionnel: au besoin) Remplacer "from collections" par "from collections.abc" partout dans le site-packages attrdict de l'installation de Python3.
- (Optionnel: au besoin) Réinstaller libbz2-dev avec sudo apt-get install.
- (Optionnel: au besoin) Remplacer "from sqlite3 import dbapi2 as Database" par "from pysqlite3 import dbapi2 as Database" dans le fichier base.py du répertoire site-packages/django/db/backends/sqlite3/ situé sous le dossier lib de l'installation de Python3.
- Clôner le répertoire [UIED_custom] à la racine du répertoire (INF6903).
- Créer un dossier models/ à la racine du répertoire (INF6903) puis y placer le fichier de modèle que le CNN de UIED doit utiliser.
- Ajuster les chemins de modèles définis dans config/CONFIG.py à la racine de UIED_custom afin de pointer sur les fichiers de modèles du dossier models/.
- Ajuster les chemins de dossiers définis dans server/workers/configurator.py et s'assurer que tous les dossiers existent sur le serveur.
- Exécuter configurator.py avec python3.
- Ajuster les scripts d'exécution .sh pour qu'ils pointent sur l'emplacement exact de l'exécutable python3 et qu'ils utilisent un workload manager distinct de Slurm si nécessaire.
- Ajuster les chemins de dossiers définis dans server/server/settings.py et s'assurer que tous les dossiers existent sur le serveur.
- Lancer le serveur Web avec la tâche runserver sur le fichier manage.py situé dans le dossier server/web/.
- Lancer les workers situés dans le dossier server/workers/.

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
   [UIED_custom]: <https://github.com/gstdenis-poly/UIED_custom>

