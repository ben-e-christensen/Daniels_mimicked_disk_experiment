import asyncio, threading, time, struct, csv, os, math
from datetime import datetime
from queue import Queue
from bleak import BleakClient, BleakError, BleakScanner
from gpiozero import InputDevice
from states import blob_state, location_state, motor_info_state

# --- CONFIGURATION ---
DEFAULT_NAME = "ESP32-Analog-100Hz"
CHARACTERISTIC_UUID = "c0de1000-0000-4a6f-9e00-000000000001"
DEVICE_ADDRESS = None  # Set to "XX:XX:XX:XX:XX:XX" to skip discovery
PACK_FORMAT = "<L8H"
PACK = struct.Struct(PACK_FORMAT)

# --- SHARED GLOBALS ---
csv_writer = None
csv_file = None
running = InputDevice(13)

running_time = 0

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

async def ble_receiver_task(csv_path: str | None, stop_event: threading.Event):
    global csv_writer, csv_file

    if csv_path:
        try:
            os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
            csv_file = open(csv_path, "w", newline="", buffering=1)
            csv_writer = csv.writer(csv_file)
            # --- MODIFICATION: Simplified CSV header ---
            csv_writer.writerow([
                "esp32_time_us",
                "a0_0", "a0_1", "a0_2", "a0_3",
                "a1_0", "a1_1", "a1_2", "a1_3",
                "angle_of_particles", "area_of_particles",
                "approximate_angle_of_a0", "approximate_angle_of_a1"
            ])
            # --- END MODIFICATION ---
            print(f"[BLE] Logging to {csv_path}")
        except Exception as e:
            print(f"[ERROR] CRITICAL: Failed to create or write to CSV file: {e}")
            return

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
                    pi_receipt_time = time.time() # Still needed for motor angle calculation
                    try:
                        vals = PACK.unpack(data)
                        esp32_time = vals[0]
                        adc_vals = vals[1:]
                        a0_vals = adc_vals[:4]
                        a1_vals = adc_vals[4:]

                        if running.is_active and location_state['flag']:
                            global running_time
                            if running_time == 0:
                                running_time = pi_receipt_time
                            if csv_writer:
                                elapsed = pi_receipt_time - running_time
                                
                                a0_angle = 0.0 # Default value
                                if elapsed > 0:
                                    steps = elapsed / (motor_info_state['delay'] * 2) 
                                    a0_angle = math.floor(steps) * motor_info_state['angles_per_step']
                                
                                # --- MODIFICATION: Write simplified data structure to CSV ---
                                csv_writer.writerow([
                                    esp32_time,
                                    *a0_vals, *a1_vals, 
                                    f"{blob_state.get('angle', 0.0):.4f}",
                                    f"{blob_state.get('area', 0.0):.4f}",
                                    f"{a0_angle:.4f}",
                                    f"{a0_angle + 180:.4f}"
                                ])
                                # --- END MODIFICATION ---

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

def run_ble_in_thread(csv_path: str | None, stop_event: threading.Event):
    """Entry point to run the BLE task in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(ble_receiver_task(csv_path, stop_event))
    finally:
        loop.close()

