import asyncio, bleak

NAME = "ESP32-Analog-100Hz"
CHAR = "c0de1000-0000-4a6f-9e00-000000000001"

async def main():
    print("Scanning...")
    devices = await bleak.BleakScanner.discover(timeout=5.0)
    d = next((dev for dev in devices if dev.name == NAME), None)
    if not d:
        print("Device not found")
        return

    print("Found:", d)

    def cb(_, data: bytearray):
        print("Notify:", len(data), list(data))

    async with bleak.BleakClient(d.address) as client:
        print("Connected, starting notify…")
        await client.start_notify(CHAR, cb)
        await asyncio.sleep(5)  # listen for 5 seconds
        await client.stop_notify(CHAR)

asyncio.run(main())
