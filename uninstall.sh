#!/usr/bin/env bash
set -Eeuo pipefail

INSTALL_DIR="/opt/minitel-keyboard"
SERVICE_NAME="minitel-keyboard.service"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}"
CLI_TARGET="/usr/local/bin/minitel"

[[ "${EUID}" -eq 0 ]] || { echo "Lancez ce script avec sudo : sudo ./uninstall.sh" >&2; exit 1; }

systemctl disable --now "${SERVICE_NAME}" 2>/dev/null || true
rm -f "${SERVICE_FILE}"
systemctl daemon-reload
systemctl reset-failed "${SERVICE_NAME}" 2>/dev/null || true
rm -f "${CLI_TARGET}" /etc/bash_completion.d/minitel

if [[ -t 0 ]]; then
    read -r -p "Supprimer aussi ${INSTALL_DIR} et le mapping calibré ? [y/N] " answer
else
    answer="n"
fi

case "${answer:-n}" in
    y|Y|yes|YES|o|O|oui|OUI) rm -rf -- "${INSTALL_DIR}" ;;
    *) echo "Les fichiers du projet et mapping.json sont conservés dans ${INSTALL_DIR}." ;;
esac

echo "Désinstallation du service terminée."
