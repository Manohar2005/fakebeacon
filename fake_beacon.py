import os
import time

def setup_interface(interface):
    # Set up the wireless interface in monitor mode
    os.system(f"sudo ip link set {interface} down")
    os.system(f"sudo iw dev {interface} set type monitor")
    os.system(f"sudo ip link set {interface} up")
    print(f"Interface {interface} is set to monitor mode.")

def start_fake_ssid_with_airbase(interface, ssid_list_file, channel=6):
    setup_interface(interface)  # Ensure interface is set up correctly

    with open(ssid_list_file, 'r') as file:
        ssid_names = [ssid.strip() for ssid in file.readlines()]

    for ssid_name in ssid_names:
        print(f"Starting fake SSID: {ssid_name}")
        # Start the fake AP directly in the terminal without opening a new window
        os.system(f"sudo airbase-ng -e '{ssid_name}' -c {channel} {interface}")
        time.sleep(2)  # Small delay to avoid conflicts

# Call the function with your interface and the text file containing SSIDs
start_fake_ssid_with_airbase('wlan0mon', 'fssid_list.txt')

