import time
from datetime import datetime

from eink_dashboard.config import DEFAULT_CONFIG
from eink_dashboard.display import create_epd
from eink_dashboard.providers.ble import get_ble_sensor
from eink_dashboard.providers.stocks import get_stock_quote
from eink_dashboard.providers.weather import get_weather
from eink_dashboard.rendering import render_dashboard
from eink_dashboard.scheduler import seconds_until_next_half_hour


def run_dashboard():
    config = DEFAULT_CONFIG
    epd = create_epd()
    epd.init()

    try:
        while True:
            time.sleep(seconds_until_next_half_hour(datetime.now()))

            try:
                weather = get_weather(config)
            except Exception:
                weather = None

            try:
                stock = get_stock_quote(config)
            except Exception:
                stock = None

            local = None
            while local is None:
                local = get_ble_sensor(config)
                if local is None:
                    time.sleep(config.ble.retry_delay_s)

            if weather is None:
                weather = {}
            weather["local"] = local

            image = render_dashboard(epd, config, weather, stock).rotate(180)
            epd.display(epd.getbuffer(image))
    except KeyboardInterrupt:
        pass
    finally:
        epd.sleep()

