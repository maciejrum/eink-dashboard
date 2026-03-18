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

## Manual run

```bash
cd /home/maciej/eink-dashboard
. .venv/bin/activate
python dashboard.py
```

## Systemd

1. Copy the service file:

```bash
sudo cp systemd/dashboard.service /etc/systemd/system/dashboard.service
```

2. Reload `systemd` and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now dashboard.service
```

3. Logs:

```bash
journalctl -u dashboard.service -f
```

## Notes

- `dashboard.py` currently keeps its configuration in constants at the top of the file.
- `lib/waveshare_epd` comes from the Waveshare repository and has been reduced to the minimum set of files needed for this project.
