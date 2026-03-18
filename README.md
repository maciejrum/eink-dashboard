# eink-dashboard

A minimal dashboard project for Raspberry Pi Zero and the Waveshare 2.13" V4 e-ink display.

This repository includes only:
- the application code,
- the minimal Waveshare driver required for `epd2in13_V4`,
- an example `systemd` service.

## Structure

- `dashboard.py` - main dashboard: weather, stock quote, local BLE sensor, and e-ink rendering
- `custom_text.py` - simple text rendering test
- `lib/waveshare_epd/` - minimal vendor driver for `epd2in13_V4`
- `systemd/dashboard.service` - example system service

## Requirements

- Raspberry Pi z włączonym SPI
- Python 3
- system packages needed for GPIO/SPI support and native Python builds

Example on Debian / Raspberry Pi OS:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip python3-dev libgpiod2
```

## Installation

```bash
cd /home/maciej/eink-dashboard
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## One-command install on Raspberry Pi / Debian

```bash
sudo ./install.sh
```

The installer will:
- install required system packages,
- create `.venv`,
- install Python dependencies,
- install `/etc/default/eink-dashboard` if it does not exist yet,
- install and start `eink-dashboard.service`.

## Manual run

```bash
cd /home/maciej/eink-dashboard
. .venv/bin/activate
python -m eink_dashboard.cli
```

## Configuration

Runtime configuration is read from environment variables. The installer copies:

- `config/eink-dashboard.env.example`

to:

- `/etc/default/eink-dashboard`

You can edit that file to change the city, coordinates, timezone, stock symbols, and BLE target.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Systemd

The service template lives in:

- `systemd/dashboard.service`

The installer fills in the user and install directory automatically.

If you want to install it manually:

1. Prepare the service file from the template:

```bash
sed \
  -e "s|__RUN_USER__|$USER|g" \
  -e "s|__INSTALL_DIR__|$PWD|g" \
  systemd/dashboard.service | sudo tee /etc/systemd/system/eink-dashboard.service >/dev/null
```

2. Reload `systemd` and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now eink-dashboard.service
```

3. Logs:

```bash
journalctl -u eink-dashboard.service -f
```

## Notes

- `dashboard.py` and `custom_text.py` are compatibility entrypoints. The actual application lives in the `eink_dashboard/` package.
- `lib/waveshare_epd` comes from the Waveshare repository and has been reduced to the minimum set of files needed for this project.
