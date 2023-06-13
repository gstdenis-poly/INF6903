# Soumissionnaire intelligent de solutions logicielles pour application de processus d’affaires
### _Par Gabriel St-Denis sous la direction de Guillaume-Alexandre Bilodeau (Ph.D.)_

## Fonctionnalités
- Capture des données d'intérêts
- Détection des objets d'intérêts
- Interprétation des objets textuels

## Technologies
- [Node.js] - implémentation du côté client
- [FFmpeg] - capture vidéo d'écran
- [ioHook] - capture d'événements clavier et souris
- [Python3] - implémentation du côté serveur
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
- S'assurer que le fichier de clé .json généré à l'enregistrement du client sur le serveur se trouve à la racine du répertoire client/ (voir installation Serveur).
### Serveur
- Placer les répertoires server/, database/, keys/ et uploads/ sur une machine serveur. TMP: PLACER DANS UN RÉPERTOIRE SUR GOOGLE DRIVE.
- Exécuter le script d'installation du serveur:
```sh
# TMP: OUVRIR LES FICHIERS detector.ipynb et clusterizer.ipynb SUR GOOGLE DRIVE (ACTIVER L'EXTENSION GOOGLE COLAB AU BESOIN), MODIFIER LA DÉFINITION DE LA VARIABLE app_root AFIN QU'ELLE AU RÉPERTOIRE RACINE DE L'APPLICATION SUR GOOGLE DRIVE PUIS EXÉCUTER LE CODE DE LA SECTION "INSTALLER".
# cd server
# bash ./installer.sh
```
- Générer un fichier de clé au format requis par le serveur pour chaque client. TMP: ACTIVER L'API GOOGLE DRIVE SUR UN COMPTE GOOGLE, CRÉER UN COMPTE DE SERVICE PAR CLIENT, GÉNÉRER UN FICHIER DE CLÉ .JSON (VOIR https://cloud.google.com/iam/docs/service-accounts) PUIS PLACER LE FICHIER DANS LE RÉPERTOIRE keys/client_keys/.
- S'assurer que chaque client est associé à un répertoire auquel il a accès en écriture dans le répertoire tmp/. TMP: CRÉER UN RÉPERTOIRE PAR CLIENT DANS LE DOSSIER tmp/ SUR GOOGLE DRIVE puis un répertoire uploads/ à l'intérieur de chaque répertoire client, PARTAGER LE RÉPERTOIRE uploads/ (ACCÈS EN ÉCRITURE) AVEC LE COMPTE DE SERVICE ASSOCIÉ AU CLIENT DU RÉPERTOIRE PARENT, AJOUTER UNE PROPRIÉTÉ folder_id DE VALEUR CORRESPONDANTE À L'IDENTIFIANT GOOGLE DRIVE DU RÉPERTOIRE DANS LE FICHIER DE CLÉ .JSON ASSOCIÉ AU CLIENT PUIS PARTAGER LE FICHIER DE CLÉ .JSON AVEC LE CLIENT.

## Licence

Polytechnique Montréal
INF6909 - Projet d'études supérieures

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [Node.js]: <https://nodejs.org/en/>
   [FFmpeg]: <https://ffmpeg.org/>
   [ioHook]: <https://www.npmjs.com/package/iohook>
   [Python3]: <https://www.python.org/>
   [UIED]: <https://github.com/MulongXie/UIED>
   [PaddleOCR]: <https://github.com/PaddlePaddle/PaddleOCR>
   [Keras]: <https://keras.io/>
   [Scikit-learn]: <https://scikit-learn.org/stable/index.html>

