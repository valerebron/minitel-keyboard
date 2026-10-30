#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/minitel-keyboard"
SERVICE_NAME="minitel-keyboard.service"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}"
CLI_SOURCE="${PROJECT_DIR}/minitel"
CLI_TARGET="/usr/local/bin/minitel"

log() { printf '[minitel] %s\n' "$*"; }
die() { printf '[minitel] ERREUR : %s\n' "$*" >&2; exit 1; }

[[ "${EUID}" -eq 0 ]] || die "Lancez ce script avec sudo : sudo ./install.sh"
[[ -f "${PROJECT_DIR}/keyboard.py" ]] || die "keyboard.py est absent du dossier du projet."
[[ -f "${PROJECT_DIR}/mapping.json" ]] || die "mapping.json est absent du dossier du projet."
[[ -f "${PROJECT_DIR}/minitel-keyboard.service" ]] || die "minitel-keyboard.service est absent."

if ! grep -qiE 'Raspberry Pi OS|Raspbian' /etc/os-release 2>/dev/null; then
    log "Distribution non identifiée comme Raspberry Pi OS. Poursuite avec vérification manuelle."
fi

log "Installation des dépendances système..."
apt-get update
apt-get install -y python3 python3-rpi.gpio python3-evdev

log "Installation du projet dans ${INSTALL_DIR}..."
mkdir -p "${INSTALL_DIR}"

# Préserve le mapping déjà calibré lors d'une réinstallation.
if [[ -f "${INSTALL_DIR}/mapping.json" ]]; then
    cp -a "${INSTALL_DIR}/mapping.json" "${INSTALL_DIR}/mapping.json.install-backup"
fi

# Copie les fichiers du dépôt, sans recopier les métadonnées Git.
find "${PROJECT_DIR}" -mindepth 1 -maxdepth 1 \
    ! -name '.git' \
    ! -name 'mapping.json' \
    -exec cp -a -t "${INSTALL_DIR}" -- {} +

if [[ -f "${INSTALL_DIR}/mapping.json.install-backup" ]]; then
    mv -f "${INSTALL_DIR}/mapping.json.install-backup" "${INSTALL_DIR}/mapping.json"
else
    install -m 0644 "${PROJECT_DIR}/mapping.json" "${INSTALL_DIR}/mapping.json"
fi

chmod 0755 "${INSTALL_DIR}/keyboard.py"
for script in calibrate.py test_matrix.py; do
    [[ ! -f "${INSTALL_DIR}/${script}" ]] || chmod 0755 "${INSTALL_DIR}/${script}"
done

log "Installation du service systemd..."
install -m 0644 "${PROJECT_DIR}/minitel-keyboard.service" "${SERVICE_FILE}"

if [[ -f "${CLI_SOURCE}" ]]; then
    log "Installation de la commande minitel..."
    install -m 0755 "${CLI_SOURCE}" "${CLI_TARGET}"
    if [[ -f "${PROJECT_DIR}/minitel-completion.bash" ]]; then
        install -D -m 0644 "${PROJECT_DIR}/minitel-completion.bash" /etc/bash_completion.d/minitel
    fi
else
    log "Fichier minitel absent : la commande minitel ne sera pas installée."
fi

systemctl daemon-reload
systemctl enable minitel-keyboard.service

if [[ -t 0 ]]; then
    read -r -p "Démarrer le clavier maintenant ? [O/n] " answer
    case "${answer:-o}" in
        n|N|non|NON) log "Service installé et activé, démarrage différé." ;;
        *) systemctl restart minitel-keyboard.service
           systemctl --no-pager --full status minitel-keyboard.service || true ;;
    esac
else
    log "Installation terminée. Démarrez avec : sudo systemctl start minitel-keyboard"
fi

log "Installation terminée."
