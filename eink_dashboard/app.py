import logging
import time
from datetime import datetime

from eink_dashboard.config import DEFAULT_CONFIG
from eink_dashboard.display import create_epd
from eink_dashboard.providers.ble import get_ble_sensor
from eink_dashboard.providers.stocks import get_stock_quote
from eink_dashboard.providers.weather import get_weather
from eink_dashboard.rendering import render_dashboard
from eink_dashboard.scheduler import seconds_until_next_minute

logger = logging.getLogger(__name__)


def safe_get_weather(config):
    try:
        return get_weather(config)
    except Exception as exc:
        logger.warning("Weather fetch failed: %s", exc)
        return None


def safe_get_stock_quote(config):
    try:
        return get_stock_quote(config)
    except Exception as exc:
        logger.warning("Stock fetch failed: %s", exc)
        return None


def safe_get_local_sensor(config):
    local_sensor = get_ble_sensor(config)
    if local_sensor is None and (config.ble.target_addr or config.ble.target_name):
        logger.warning(
            "BLE sensor not available for this refresh "
            "(target_name=%r, target_addr=%r)",
            config.ble.target_name,
            config.ble.target_addr,
        )
    return local_sensor


def build_payload(config):
    weather = safe_get_weather(config) or {}
    weather["local"] = safe_get_local_sensor(config)
    return weather, safe_get_stock_quote(config)


def update_display(epd, config):
    weather, stock = build_payload(config)
    image = render_dashboard(epd, config, weather, stock).rotate(180)
    epd.display(epd.getbuffer(image))


def run_dashboard(config=DEFAULT_CONFIG):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    try:
        epd = create_epd()
        epd.init()
    except Exception as exc:
        logger.error("Failed to initialize the e-ink display: %s", exc)
        return

    try:
        while True:
            try:
                logger.info("Refreshing dashboard")
                update_display(epd, config)
            except Exception as exc:
                logger.error("Dashboard refresh failed: %s", exc)
            time.sleep(seconds_until_next_minute(datetime.now()))
    except KeyboardInterrupt:
        logger.info("Stopping dashboard")
    finally:
        try:
            epd.sleep()
        except Exception as exc:
            logger.warning("Failed to put the e-ink display to sleep: %s", exc)
