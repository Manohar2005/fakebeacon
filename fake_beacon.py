import os
import time
import subprocess
import signal

def setup_interface(interface):
    print("Disabling NetworkManager...")
    os.system("sudo systemctl stop NetworkManager.service")

    print(f"Setting {interface} to monitor mode...")
    os.system(f"sudo ip link set {interface} down")
    os.system(f"sudo iw dev {interface} set type monitor")
    os.system(f"sudo ip link set {interface} up")

def restore_interface(interface):
    print("Restoring Wi-Fi interface...")
    
    # Kill all hostapd processes
    os.system("sudo killall hostapd")
    time.sleep(1)  # Allow time for processes to terminate
    
    # Restore the interface to managed mode
    os.system(f"sudo ip link set {interface} down")
    os.system(f"sudo iw dev {interface} set type managed")
    os.system(f"sudo ip link set {interface} up")

    print("Re-enabling NetworkManager...")
    os.system("sudo systemctl start NetworkManager.service")

def start_fake_ssid_with_hostapd(interface, ssid_list_file, channel=6, duration=60):
    setup_interface(interface)

    with open(ssid_list_file, 'r') as file:
        ssid_names = [ssid.strip() for ssid in file.readlines()]

    # Create a hostapd configuration file
    config_file = "hostapd.conf"
    with open(config_file, 'w') as f:
        f.write(f"interface={interface}\n")
        f.write(f"driver=nl80211\n")
        f.write(f"channel={channel}\n")
        for i, ssid_name in enumerate(ssid_names):
            f.write(f"ssid={ssid_name}\n")
            f.write(f"bssid=00:11:22:33:44:{i:02X}\n")  # Unique BSSID for each SSID
            f.write(f"hw_mode=g\n")
            f.write(f"auth_algs=1\n")
            f.write(f"wpa=0\n")  # No encryption (open network)

    print("Starting hostapd to broadcast fake SSIDs...")
    proc = subprocess.Popen(
        f"sudo hostapd {config_file}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    print(f"Broadcasting fake SSIDs for {duration} seconds...")

    try:
        time.sleep(duration)
    except KeyboardInterrupt:
        print("Script interrupted manually.")
    finally:
        restore_interface(interface)

# Example usage: Broadcast for 60 seconds and then restore the network
start_fake_ssid_with_hostapd('wlan0', 'fssid_list.txt', duration=60)
