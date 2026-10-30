# Minitel Keyboard

**Transformer le clavier d'un Minitel 1B en clavier Linux avec un Raspberry Pi.**

- Version : `0.1`
- Système de référence : **Raspberry Pi OS**
- Matériel testé : Raspberry Pi 3B
- Langage : Python 3
- Interface Linux : `evdev` / `uinput`
- Dépôt : [github.com/valerebron/minitel-keyboard](https://github.com/valerebron/minitel-keyboard)

---

## Présentation

Ce projet permet de réutiliser le clavier d'un Minitel 1B comme un clavier standard sous Linux.

Le Raspberry Pi lit la matrice de touches du Minitel à travers ses broches GPIO. Un programme Python détecte les contacts, les associe à des codes clavier Linux (`KEY_*`), puis émule un clavier USB virtuel au niveau du système grâce à `evdev` et `uinput`.

Le Minitel devient ainsi un périphérique de saisie utilisable dans les applications Linux, sans modification matérielle du clavier lui-même.

### Fonctionnalités

- Lecture de la matrice du clavier par GPIO.
- Association des contacts à des keycodes Linux.
- Émulation d'un clavier Linux avec `uinput`.
- Configuration AZERTY/QWERTY gérée par la disposition système.
- Outil de test de la matrice.
- Outil de calibration des touches.
- Affichage du mapping logiciel.
- Démarrage automatique avec `systemd`.
- Commande centralisée `minitel` avec autocomplétion Bash.

## Matériel

### Équipement nécessaire

- Raspberry Pi 3B (ou modèle compatible).
- Carte microSD (16 Go minimum conseillé).
- Alimentation adaptée au Raspberry Pi.
- Minitel 1B avec clavier fonctionnel.
- Fils de connexion.
- Câblage adapté à la matrice du clavier.

### Attention aux niveaux électriques

Les GPIO du Raspberry Pi fonctionnent en **3,3 V** et ne sont pas tolérants au 5 V.

Avant tout branchement :

- Vérifier les niveaux électriques présents sur le connecteur du Minitel.
- Ne jamais appliquer directement une tension de 5 V sur une broche GPIO.
- Vérifier le brochage et la continuité des fils.
- Ne pas connecter le Minitel au Raspberry Pi tant que les niveaux électriques ne sont pas connus.

Les correspondances GPIO ci-dessous décrivent le câblage utilisé par le programme. Elles ne remplacent pas la vérification électrique du connecteur Minitel.

## Brochage du Raspberry Pi

Les numéros indiqués dans le projet sont les numéros **BCM**, et non les numéros physiques des broches du connecteur 40 points.

![Brochage GPIO du Raspberry Pi](mapping-rasberry.png)

*Brochage du connecteur GPIO du Raspberry Pi.*

### Lignes et colonnes utilisées

| Signal | GPIO BCM | Broche physique |
|---|---:|---:|
| Ligne 2 | GPIO 5 | 29 |
| Ligne 3 | GPIO 6 | 31 |
| Ligne 4 | GPIO 12 | 32 |
| Ligne 5 | GPIO 13 | 33 |
| Ligne C | GPIO 16 | 36 |
| Ligne D | GPIO 19 | 35 |
| Ligne E | GPIO 20 | 38 |
| Ligne F | GPIO 21 | 40 |
| Colonne 1 | GPIO 4 | 7 |
| Colonne 6 | GPIO 17 | 11 |
| Colonne 7 | GPIO 18 | 12 |
| Colonne 8 | GPIO 22 | 15 |
| Colonne 9 | GPIO 23 | 16 |
| Colonne A | GPIO 24 | 18 |
| Colonne B | GPIO 25 | 22 |
| Colonne G | GPIO 27 | 13 |

### Mapping utilisé dans les programmes

```python
ROWS = {
    "2": 5,
    "3": 6,
    "4": 12,
    "5": 13,
    "C": 16,
    "D": 19,
    "E": 20,
    "F": 21,
}

COLS = {
    "1": 4,
    "6": 17,
    "7": 18,
    "8": 22,
    "9": 23,
    "A": 24,
    "B": 25,
    "G": 27,
}
```

## Matrice du clavier Minitel 1B

Le clavier est organisé sous forme d'une matrice de lignes et de colonnes.

![Mapping de la matrice du clavier Minitel](mapping-minitel.jpg)

*Correspondance des lignes et colonnes du clavier Minitel 1B.*

Le programme balaie les lignes et les colonnes afin de détecter les contacts fermés.

| Type | Signal | GPIO BCM |
|---|---|---:|
| Ligne | 2 | 5 |
| Ligne | 3 | 6 |
| Ligne | 4 | 12 |
| Ligne | 5 | 13 |
| Ligne | C | 16 |
| Ligne | D | 19 |
| Ligne | E | 20 |
| Ligne | F | 21 |
| Colonne | 1 | 4 |
| Colonne | 6 | 17 |
| Colonne | 7 | 18 |
| Colonne | 8 | 22 |
| Colonne | 9 | 23 |
| Colonne | A | 24 |
| Colonne | B | 25 |
| Colonne | G | 27 |

Le câblage physique doit respecter les correspondances entre les contacts du connecteur clavier et les lignes/colonnes de cette matrice.

> **Note :** le brochage électrique détaillé du connecteur Minitel doit être documenté à partir du câblage réellement vérifié. Ne pas déduire les broches du connecteur à partir du seul tableau GPIO.

## Architecture logicielle

Le projet repose sur trois programmes Python :

| Fichier | Rôle |
|---|---|
| `keyboard.py` | Pilote principal : lecture de la matrice et émission des événements clavier |
| `test_matrix.py` | Diagnostic des contacts de la matrice |
| `calibrate.py` | Association des contacts détectés aux keycodes Linux |
| `mapping.json` | Correspondance entre les contacts et les touches Linux |

Le pilote utilise :

- `RPi.GPIO` pour accéder aux GPIO.
- `evdev` pour créer et piloter un clavier virtuel.
- `uinput` pour transmettre les événements clavier au noyau Linux.

### Arborescence cible

```text
minitel-keyboard/
├── README.md
├── LICENSE
├── mapping-minitel.jpg
├── mapping-rasberry.png
├── install.sh
├── uninstall.sh
├── src/
│   ├── keyboard.py
│   ├── calibrate.py
│   └── test_matrix.py
├── config/
│   └── mapping.json
├── systemd/
│   └── minitel-keyboard.service
├── cli/
│   └── minitel
└── completions/
    └── minitel
```

Les scripts d'installation et de désinstallation, ainsi que cette organisation du dépôt, constituent la structure cible du projet. Ils devront être présents et testés avant de considérer l'installation automatique comme disponible.

## Mapping logiciel et keycodes Linux

Le mapping logiciel associe chaque contact de la matrice à un code clavier Linux.

Le fichier `mapping.json` contient les correspondances utilisées par `keyboard.py`.

Les valeurs doivent être des noms de keycodes Linux, par exemple :

```json
{
    "2:1": "KEY_ESC",
    "2:6": "KEY_A",
    "2:7": "KEY_Z",
    "2:8": "KEY_E"
}
```

Cet extrait illustre le format : les associations exactes doivent être établies par calibration sur le clavier utilisé.

### Référence officielle des keycodes

La liste de référence est celle du noyau Linux :

[Linux input-event-codes.h — liste complète des codes clavier](https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h)

Quelques exemples :

| Keycode | Code numérique | Touche |
|---|---:|---|
| `KEY_ESC` | 1 | Échap |
| `KEY_1` | 2 | 1 |
| `KEY_2` | 3 | 2 |
| `KEY_ENTER` | 28 | Entrée |
| `KEY_A` | 30 | A |
| `KEY_S` | 31 | S |
| `KEY_D` | 32 | D |
| `KEY_F` | 33 | F |
| `KEY_SPACE` | 57 | Espace |

La liste complète évolue avec le noyau Linux. Il est préférable de se référer au fichier officiel plutôt que de maintenir une liste partielle dans le projet.

### Disposition du clavier

Les keycodes Linux représentent des touches physiques logiques. Le caractère affiché dépend ensuite de la disposition clavier configurée dans le système.

Pour ce projet, la disposition **QWERTY (`us`)** est utilisée afin que les touches physiques du Minitel correspondent directement aux keycodes configurés.

Sur Raspberry Pi OS, la configuration de la console peut être effectuée avec :

```bash
sudo nano /etc/default/keyboard
```

Vérifier notamment la présence de :

```ini
XKBLAYOUT="us"
```

Puis appliquer la configuration :

```bash
sudo setupcon --save
```

Redémarrer le Raspberry Pi et vérifier que la disposition est bien conservée.

Cette configuration concerne la disposition système utilisée pour le projet. Si un environnement graphique est utilisé, vérifier également sa propre configuration de disposition clavier.

## Installation

### Système de référence

Le développement et les premiers essais sont réalisés sur **Raspberry Pi OS**, avec un Raspberry Pi 3B.

Debian sera testé dans une étape ultérieure. La compatibilité avec d'autres modèles de Raspberry Pi n'est pas encore garantie.

### Récupération du projet

```bash
git clone https://github.com/valerebron/minitel-keyboard.git
cd minitel-keyboard
```

### Dépendances

Sur Raspberry Pi OS, installer les dépendances système :

```bash
sudo apt update
sudo apt install -y \
    python3 \
    python3-rpi.gpio \
    python3-evdev \
    evtest \
    kbd \
    console-setup \
    keyboard-configuration \
    bash-completion
```

Vérifier que le module `uinput` est disponible :

```bash
sudo modprobe uinput
```

Pour le charger automatiquement au démarrage :

```bash
echo uinput | sudo tee /etc/modules-load.d/uinput.conf
```

### Installation du pilote

Le répertoire d'installation cible est :

```text
/opt/minitel-keyboard/
```

Les fichiers Python doivent être installés dans ce répertoire, avec le fichier `mapping.json`.

Une fois les fichiers installés, le pilote peut être lancé manuellement pour les premiers essais :

```bash
sudo python3 /opt/minitel-keyboard/keyboard.py
```

L'installation automatisée en une commande sera documentée ici lorsqu'elle aura été implémentée et validée sur une installation Raspberry Pi OS vierge.

## Commande `minitel`

Le projet prévoit une commande unique pour administrer le clavier :

```bash
minitel key <commande>
```

### Commandes disponibles

| Commande | Fonction |
|---|---|
| `minitel key start` | Démarre le pilote |
| `minitel key stop` | Arrête le pilote |
| `minitel key restart` | Redémarre le pilote |
| `minitel key status` | Affiche l'état du service |
| `minitel key test` | Lance le test de la matrice |
| `minitel key calibrate` | Lance la calibration |
| `minitel key dump` | Affiche le mapping actuel |

### Exemples

Tester la matrice :

```bash
minitel key test
```

Calibrer les touches :

```bash
minitel key calibrate
```

Afficher le mapping :

```bash
minitel key dump
```

Redémarrer le pilote :

```bash
minitel key restart
```

### Autocomplétion Bash

L'autocomplétion doit permettre de compléter les commandes avec la touche `Tab`.

Exemple :

```text
minitel key [TAB]
calibrate  dump  restart  start  status  stop  test
```

## Service systemd

Le pilote est destiné à fonctionner en arrière-plan au démarrage du Raspberry Pi.

Nom du service :

```text
minitel-keyboard.service
```

Exemple d'unité systemd :

```ini
[Unit]
Description=Clavier Minitel 1B
After=multi-user.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/minitel-keyboard
ExecStart=/usr/bin/python3 /opt/minitel-keyboard/keyboard.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Installation et activation :

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now minitel-keyboard.service
```

Consulter son état :

```bash
sudo systemctl status minitel-keyboard.service
```

Consulter les journaux :

```bash
sudo journalctl -u minitel-keyboard.service -n 100 --no-pager
```

Les commandes `test` et `calibrate` doivent arrêter temporairement le service pour éviter que deux programmes n'accèdent simultanément à la matrice GPIO.

## Dépannage

### Le clavier ne répond pas

Vérifier successivement :

1. Le câblage des lignes et colonnes.
2. La correspondance BCM des GPIO.
3. Les droits et la disponibilité de `uinput`.
4. L'état du service :

```bash
sudo systemctl status minitel-keyboard.service
```

5. Les journaux :

```bash
sudo journalctl -u minitel-keyboard.service -n 100 --no-pager
```

### Une touche ne fonctionne pas

Lancer le test de matrice :

```bash
minitel key test
```

Puis vérifier le mapping :

```bash
minitel key dump
```

Si nécessaire, lancer une nouvelle calibration :

```bash
minitel key calibrate
```

### Les caractères ne correspondent pas aux touches

Vérifier la disposition clavier du système.

Pour le fonctionnement prévu dans ce projet, la disposition doit être QWERTY (`us`).

### Le service ne démarre pas

Vérifier la présence du module `uinput` :

```bash
lsmod | grep uinput
```

Le charger si nécessaire :

```bash
sudo modprobe uinput
```

Puis consulter les journaux systemd.

## Désinstallation

La désinstallation automatisée devra :

- arrêter et désactiver le service systemd ;
- supprimer l'unité systemd ;
- supprimer la commande `minitel` et son autocomplétion ;
- supprimer les fichiers installés dans `/opt/minitel-keyboard/` ;
- conserver une sauvegarde du fichier `mapping.json` si l'utilisateur le souhaite.

La disposition clavier du système ne doit pas être réinitialisée automatiquement sans demander confirmation : elle peut être utilisée par d'autres applications.

## Feuille de route

- [x] Lecture de la matrice avec les GPIO du Raspberry Pi 3B.
- [x] Émission d'événements clavier Linux avec `evdev` / `uinput`.
- [x] Configuration QWERTY validée sur le système de développement.
- [x] Service systemd défini.
- [x] Commandes de gestion du pilote définies.
- [ ] Finalisation de l'installation automatisée.
- [ ] Finalisation de la désinstallation.
- [ ] Validation de l'autocomplétion Bash.
- [ ] Documentation du brochage physique vérifié du connecteur Minitel.
- [ ] Tests sur une installation Raspberry Pi OS vierge.
- [ ] Tests de compatibilité Debian.
- [ ] Création d'une image SD préconfigurée.

## Licence

Ce projet est destiné à être distribué sous licence MIT. Le fichier `LICENSE` devra être présent à la racine du dépôt pour formaliser cette licence.

---

**Minitel Keyboard — v0.1**

Projet expérimental de réutilisation du clavier Minitel comme périphérique d'entrée Linux.

Dépôt : [github.com/valerebron/minitel-keyboard](https://github.com/valerebron/minitel-keyboard)
