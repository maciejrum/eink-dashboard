import asyncio

from bleak import BleakScanner

from eink_dashboard.config import AppConfig


def decode_fixed_bthome(data: bytes) -> dict[str, object] | None:
    if len(data) != 11:
        return None
    if data[0] != 0x40 or data[1] != 0x00:
        return None
    if not (data[3] == 0x01 and data[5] == 0x02 and data[8] == 0x03):
        return None

    temp_raw = int.from_bytes(data[6:8], "little", signed=True)
    humidity_raw = int.from_bytes(data[9:11], "little", signed=False)

    return {
        "pid": data[2],
        "battery_pct": data[4],
        "temperature_c": temp_raw / 100.0,
        "humidity_pct": humidity_raw / 100.0,
    }


async def read_ble_once(config: AppConfig) -> dict[str, object]:
    ble = config.ble
    got = asyncio.Event()
    result: dict[str, object] = {}

    def callback(device, advertisement):
        if ble.target_addr and device.address != ble.target_addr:
            return
        if ble.target_name and device.name != ble.target_name:
            return

        data = (advertisement.service_data or {}).get(ble.service_uuid)
        if not data:
            return

        decoded = decode_fixed_bthome(data)
        if not decoded:
            return

        result.update(decoded)
        got.set()

    scanner = BleakScanner(callback)
    await scanner.start()
    try:
        await asyncio.wait_for(got.wait(), timeout=ble.timeout_s)
    finally:
        await scanner.stop()

    return result


def get_ble_sensor(config: AppConfig) -> dict[str, object] | None:
    try:
        return asyncio.run(read_ble_once(config))
    except Exception:
        return None

