import time
from datetime import datetime

from eink_dashboard.config import DEFAULT_CONFIG
from eink_dashboard.display import create_epd
from eink_dashboard.providers.ble import get_ble_sensor
from eink_dashboard.providers.stocks import get_stock_quote
from eink_dashboard.providers.weather import get_weather
from eink_dashboard.rendering import render_dashboard
from eink_dashboard.scheduler import seconds_until_next_half_hour


def safe_get_weather(config):
    try:
        return get_weather(config)
    except Exception:
        return None


def safe_get_stock_quote(config):
    try:
        return get_stock_quote(config)
    except Exception:
        return None


def wait_for_local_sensor(config):
    local_sensor = None
    while local_sensor is None:
        local_sensor = get_ble_sensor(config)
        if local_sensor is None:
            time.sleep(config.ble.retry_delay_s)
    return local_sensor


def build_payload(config):
    weather = safe_get_weather(config) or {}
    weather["local"] = wait_for_local_sensor(config)
    return weather, safe_get_stock_quote(config)


def update_display(epd, config):
    weather, stock = build_payload(config)
    image = render_dashboard(epd, config, weather, stock).rotate(180)
    epd.display(epd.getbuffer(image))


def run_dashboard(config=DEFAULT_CONFIG):
    epd = create_epd()
    epd.init()

    try:
        while True:
            update_display(epd, config)
            time.sleep(seconds_until_next_half_hour(datetime.now()))
    except KeyboardInterrupt:
        pass
    finally:
        epd.sleep()
