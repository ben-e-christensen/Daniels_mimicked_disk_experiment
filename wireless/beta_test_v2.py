import asyncio
from bleak import BleakClient, BleakScanner

DEVICE_NAME = "Seeed_BLE"
CHARACTERISTIC_UUID = "abcdefab-1234-5678-1234-abcdefabcdef"  # Must match server

async def run():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover(timeout=5)

    # Find the target device by name
    target = next((d for d in devices if d.name == DEVICE_NAME), None)
    if not target:
        print(f"Device named '{DEVICE_NAME}' not found.")
        return

    print(f"Connecting to {target.name} at {target.address}...")
    async with BleakClient(target.address) as client:
        print("Connected!")

        # Read from the characteristic
        value = await client.read_gatt_char(CHARACTERISTIC_UUID)
        print(f"Read value: {value.decode('utf-8')}")

        # (Optional) Write to the characteristic
        # message = "Hi ESP32!"
        # await client.write_gatt_char(CHARACTERISTIC_UUID, message.encode())
        # print(f"Wrote value: {message}")
    
asyncio.run(run())
