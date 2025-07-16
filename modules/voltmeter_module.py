from daqhats import mcc118, OptionFlags, HatIDs
from daqhats_utils import select_hat_device, enum_mask_to_string, chan_list_to_mask
from gui_module import update_voltage
import time

READ_ALL_AVAILABLE = -1

def start_voltmeter_loop():
    channels = [0]
    channel_mask = chan_list_to_mask(channels)
    num_channels = len(channels)
    scan_rate = 1000.0
    samples_per_channel = 0
    options = OptionFlags.CONTINUOUS

    address = select_hat_device(HatIDs.MCC_118)
    hat = mcc118(address)

    hat.a_in_scan_start(channel_mask, samples_per_channel, scan_rate, options)
    timeout = 5.0

    while True:
        read_result = hat.a_in_scan_read(READ_ALL_AVAILABLE, timeout)

        if read_result.hardware_overrun or read_result.buffer_overrun:
            break

        samples_read_per_channel = int(len(read_result.data) / num_channels)
        if samples_read_per_channel > 0:
            index = samples_read_per_channel * num_channels - num_channels
            val = read_result.data[index]
            update_voltage(f"Voltage: {val:.3f} V")

        time.sleep(0.2)
