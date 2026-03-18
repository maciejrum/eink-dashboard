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


DEFAULT_CONFIG = AppConfig()

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

