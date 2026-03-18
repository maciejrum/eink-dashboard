#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${SCRIPT_DIR}"
SERVICE_NAME="eink-dashboard.service"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}"
ENV_PATH="/etc/default/eink-dashboard"
RUN_USER="${SUDO_USER:-${USER}}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
APT_PACKAGES=(
  python3
  python3-venv
  python3-pip
  python3-dev
  libgpiod2
  libbluetooth-dev
)

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run this installer with sudo."
  exit 1
fi

if ! command -v apt-get >/dev/null 2>&1; then
  echo "This installer currently supports Debian-based systems with apt-get."
  exit 1
fi

if ! command -v systemctl >/dev/null 2>&1; then
  echo "systemd is required to install and enable the dashboard service."
  exit 1
fi

echo "Installing system packages..."
apt-get update
apt-get install -y "${APT_PACKAGES[@]}"

echo "Creating Python virtual environment..."
sudo -u "${RUN_USER}" "${PYTHON_BIN}" -m venv "${INSTALL_DIR}/.venv"

echo "Installing Python dependencies..."
sudo -u "${RUN_USER}" "${INSTALL_DIR}/.venv/bin/pip" install --upgrade pip
sudo -u "${RUN_USER}" "${INSTALL_DIR}/.venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt"

if [[ ! -f "${ENV_PATH}" ]]; then
  echo "Installing default environment file..."
  install -m 0644 "${INSTALL_DIR}/config/eink-dashboard.env.example" "${ENV_PATH}"
fi

echo "Installing systemd service..."
sed \
  -e "s|__RUN_USER__|${RUN_USER}|g" \
  -e "s|__INSTALL_DIR__|${INSTALL_DIR}|g" \
  "${INSTALL_DIR}/systemd/dashboard.service" > "${SERVICE_PATH}"

chmod 0644 "${SERVICE_PATH}"
systemctl daemon-reload
systemctl enable --now "${SERVICE_NAME}"

echo
echo "Installation complete."
echo "Service status:"
systemctl --no-pager --full status "${SERVICE_NAME}" || true
echo
echo "Useful commands:"
echo "  sudo systemctl restart ${SERVICE_NAME}"
echo "  journalctl -u ${SERVICE_NAME} -f"
echo "  sudoedit ${ENV_PATH}"

