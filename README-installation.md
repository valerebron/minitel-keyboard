## Installation

Depuis le dossier du dépôt, sur Raspberry Pi OS :

```bash
sudo ./install.sh
```

L'installateur installe les dépendances système (`python3`, `python3-rpi.gpio` et
`python3-evdev`), copie le projet dans `/opt/minitel-keyboard/`, installe le
service systemd et l'active au démarrage.

Une réinstallation conserve le fichier `/opt/minitel-keyboard/mapping.json`
existant afin de ne pas écraser une calibration. Si le dépôt contient le script
`minitel`, celui-ci est installé dans `/usr/local/bin/minitel`.

### Gestion du service

```bash
sudo systemctl start minitel-keyboard
sudo systemctl stop minitel-keyboard
sudo systemctl restart minitel-keyboard
sudo systemctl status minitel-keyboard
```

Pour consulter les journaux :

```bash
sudo journalctl -u minitel-keyboard -f
```

### Désinstallation

```bash
sudo ./uninstall.sh
```

Le service systemd et la commande `/usr/local/bin/minitel` sont supprimés.
Par défaut, les fichiers installés et le mapping calibré sont conservés.
Le script demande explicitement confirmation avant de supprimer également
`/opt/minitel-keyboard/`.

> **Note :** ces scripts ciblent Raspberry Pi OS avec les paquets Python fournis
> par APT. Ils doivent être testés sur le modèle et la version de Raspberry Pi OS
> utilisés avant toute installation en production. L'installateur ne configure
> pas le câblage GPIO et ne modifie pas la disposition clavier du système.


### Commande `minitel` et autocomplétion Bash

L'installation place la commande `minitel` dans `/usr/local/bin/` et
l'autocomplétion Bash dans `/etc/bash_completion.d/minitel`.

Commandes disponibles :

```bash
sudo minitel key start
sudo minitel key stop
sudo minitel key restart
minitel key status
sudo minitel key test
sudo minitel key calibrate
minitel key dump
```

L'autocomplétion propose `key`, puis `start`, `stop`, `restart`, `status`,
`test`, `calibrate` et `dump`. Elle est chargée automatiquement dans les
nouvelles sessions Bash si le paquet `bash-completion` est installé et activé.
Pour la charger dans le terminal courant :

```bash
source /etc/bash_completion
source /etc/bash_completion.d/minitel
```
