# eink-dashboard

Minimalny projekt dashboardu dla Raspberry Pi Zero i wyświetlacza Waveshare e-ink 2.13" V4.

Repo zawiera tylko:
- własny kod aplikacji,
- minimalny sterownik Waveshare potrzebny dla `epd2in13_V4`,
- przykładową usługę `systemd`.

## Struktura

- `dashboard.py` - główny dashboard: pogoda, kurs akcji, lokalny czujnik BLE, render na e-inku
- `custom_text.py` - prosty test wyświetlania tekstu
- `lib/waveshare_epd/` - minimalny vendor driver dla `epd2in13_V4`
- `systemd/dashboard.service` - przykładowa usługa systemowa

## Wymagania

- Raspberry Pi z włączonym SPI
- Python 3
- pakiety systemowe potrzebne do kompilacji i obsługi GPIO/SPI

Przykładowo na Debian/Raspberry Pi OS:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip python3-dev libgpiod2
```

## Instalacja

```bash
cd /home/maciej/eink-dashboard
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Uruchomienie ręczne

```bash
cd /home/maciej/eink-dashboard
. .venv/bin/activate
python dashboard.py
```

## Systemd

1. Skopiuj usługę:

```bash
sudo cp systemd/dashboard.service /etc/systemd/system/dashboard.service
```

2. Przeładuj `systemd` i uruchom:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now dashboard.service
```

3. Logi:

```bash
journalctl -u dashboard.service -f
```

## Uwagi

- `dashboard.py` ma na razie konfigurację zaszytą w stałych na górze pliku.
- Sterownik `lib/waveshare_epd` pochodzi z repo Waveshare i został ograniczony do minimalnego zestawu plików potrzebnych dla tego projektu.

