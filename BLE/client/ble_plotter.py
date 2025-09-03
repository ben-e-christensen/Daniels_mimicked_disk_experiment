import asyncio
import threading
import time
import struct
import csv
import os
from datetime import datetime
from queue import Queue
from bleak import BleakClient, BleakError, BleakScanner
from gpiozero import InputDevice

# --- CONFIGURATION ---
DEFAULT_NAME = "ESP32-Analog-100Hz"
CHARACTERISTIC_UUID = "c0de1000-0000-4a6f-9e00-000000000001"
DEVICE_ADDRESS = None  # Set to "XX:XX:XX:XX:XX:XX" to skip discovery
PACK_FORMAT = "<10H"
PACK = struct.Struct(PACK_FORMAT)

# --- SHARED GLOBALS ---
data_queue_a0 = Queue()
data_queue_a1 = Queue()
stop_event = threading.Event()
csv_writer = None
csv_file = None
running = InputDevice(13)
# if running.is_active:

# --- ASYNCHRONOUS BLE LOGIC ---
async def find_device(name: str | None, address: str | None, timeout: float = 8.0):
    if address:
        return type('', (object,), {'address': address, 'name': '(address-specified)'})()
    
    print(f"[BLE] Scanning for device '{name}'...")
    device = await BleakScanner.find_device_by_name(name, timeout=timeout)
    
    if not device:
        print(f"[BLE] Device '{name}' not found. Please ensure it is advertising.")
    else:
        print(f"[BLE] Found device: {device.address} ({device.name})")
    
    return device

async def ble_receiver_task(csv_path: str | None):
    global csv_writer, csv_file

    if csv_path:
        os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
        csv_file = open(csv_path, "w", newline="", buffering=1)
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([
            "iso_time", "epoch_s",
            "a0_0", "a0_1", "a0_2", "a0_3", "a0_4",
            "a1_0", "a1_1", "a1_2", "a1_3", "a1_4"
        ])
        print(f"[BLE] Logging to {csv_path}")
    
    while not stop_event.is_set():
        device = await find_device(DEFAULT_NAME, DEVICE_ADDRESS)
        if not device:
            if not stop_event.is_set():
                print("[BLE] Retrying discovery in 5s...")
                await asyncio.sleep(5.0)
            continue
            
        try:
            print(f"[BLE] Attempting to connect to {device.address}...")
            async with BleakClient(device.address, timeout=10.0) as client:
                print("[BLE] Connected. Subscribing to notifications...")
                
                def notification_handler(_handle, data):
                    now = time.time()
                    try:
                        vals = PACK.unpack(data)
                        a0_vals = vals[:5]
                        a1_vals = vals[5:]
                        
                        for val in a0_vals:
                            data_queue_a0.put(val)
                        for val in a1_vals:
                            data_queue_a1.put(val)
                        if running.is_active:
                            if csv_writer:
                                csv_writer.writerow([
                                    datetime.utcfromtimestamp(now).isoformat(),
                                    f"{now:.6f}",
                                    *a0_vals, *a1_vals
                                ])
                    except struct.error:
                        print(f"[BLE] Bad packet length: {len(data)}")

                await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
                
                while client.is_connected and not stop_event.is_set():
                    await asyncio.sleep(0.1)

        except BleakError as e:
            print(f"[BLE] Connection error: {e}. Retrying in 2s...")
            if not stop_event.is_set():
                await asyncio.sleep(2.0)
        except Exception as e:
            print(f"[BLE] Unexpected error: {e}")
            break

    if csv_file:
        csv_file.close()
        print("[BLE] CSV closed.")
    print("[BLE] Receiver task stopped.")

def run_ble_in_thread(csv_path: str | None = None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(ble_receiver_task(csv_path))
    finally:
        loop.close()