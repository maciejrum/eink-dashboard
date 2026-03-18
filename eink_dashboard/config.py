import os
from dataclasses import dataclass


@dataclass(frozen=True)
class BleConfig:
    service_uuid: str = "0000fcd2-0000-1000-8000-00805f9b34fb"
    target_addr: str = ""
    target_name: str = "ATC_032E2A"
    timeout_s: float = 8.0
    retry_delay_s: float = 10.0


@dataclass(frozen=True)
class MarketConfig:
    symbols: tuple[str, ...] = ("bmc", "bmc.pl")
    quote_url: str = "https://stooq.com/q/l/?s={sym}&f=sd2t2ohlcv&h&e=csv"


@dataclass(frozen=True)
class LocationConfig:
    city: str = "Kraków"
    lat: float = 50.0647
    lon: float = 19.9450
    timezone: str = "Europe/Warsaw"


@dataclass(frozen=True)
class LayoutConfig:
    padding: int = 4
    split_y: int = 62


@dataclass(frozen=True)
class AppConfig:
    location: LocationConfig = LocationConfig()
    market: MarketConfig = MarketConfig()
    ble: BleConfig = BleConfig()
    layout: LayoutConfig = LayoutConfig()
    user_agent: str = "pi-zero-eink/1.0"


def _get_env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    return float(value)


def _get_env_str(name: str, default: str) -> str:
    return os.getenv(name, default)


def load_config() -> AppConfig:
    return AppConfig(
        location=LocationConfig(
            city=_get_env_str("EINK_CITY", LocationConfig.city),
            lat=_get_env_float("EINK_LAT", LocationConfig.lat),
            lon=_get_env_float("EINK_LON", LocationConfig.lon),
            timezone=_get_env_str("EINK_TIMEZONE", LocationConfig.timezone),
        ),
        market=MarketConfig(
            symbols=tuple(
                item.strip()
                for item in _get_env_str("EINK_STOOQ_SYMBOLS", ",".join(MarketConfig.symbols)).split(",")
                if item.strip()
            )
            or MarketConfig.symbols,
            quote_url=_get_env_str("EINK_STOOQ_QUOTE_URL", MarketConfig.quote_url),
        ),
        ble=BleConfig(
            service_uuid=_get_env_str("EINK_BT_HOME_UUID", BleConfig.service_uuid),
            target_addr=_get_env_str("EINK_BT_TARGET_ADDR", BleConfig.target_addr),
            target_name=_get_env_str("EINK_BT_TARGET_NAME", BleConfig.target_name),
            timeout_s=_get_env_float("EINK_BT_TIMEOUT_S", BleConfig.timeout_s),
            retry_delay_s=_get_env_float("EINK_BT_RETRY_DELAY_S", BleConfig.retry_delay_s),
        ),
        layout=LayoutConfig(
            padding=int(_get_env_float("EINK_LAYOUT_PADDING", LayoutConfig.padding)),
            split_y=int(_get_env_float("EINK_LAYOUT_SPLIT_Y", LayoutConfig.split_y)),
        ),
        user_agent=_get_env_str("EINK_USER_AGENT", AppConfig.user_agent),
    )


DEFAULT_CONFIG = load_config()

WMO_DESCRIPTIONS = {
    0: "clear",
    1: "mostly clear",
    2: "partly cloudy",
    3: "cloudy",
    45: "fog",
    48: "fog",
    51: "drizzle",
    53: "drizzle",
    55: "drizzle",
    61: "rain",
    63: "rain",
    65: "rain",
    71: "snow",
    73: "snow",
    75: "snow",
    80: "showers",
    81: "showers",
    82: "heavy rain",
    95: "storm",
    96: "storm",
    99: "storm",
}
