from netmiko import ConnectHandler
import sys
import yaml

config_commands = [
    "interface loopback 100",
    "ip address 10.100.100.1 255.255.255.0",
    "description Configured by Python Script",
]

def load_inventory(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if "device" not in data or not isinstance(data["device"], dict):
        raise ValueError("Inventory must contain a top-level 'device:' mapping")
    return data["device"]

def main():
    if len(sys.argv) < 2:
         print("Usage: python script.py <inventory.yml>")
         sys.exit(2)

    inventory_path = sys.argv[1]

    try:
        device = load_inventory(inventory_path)

        print("Connecting to device...")
        connection = ConnectHandler(**device)

        print("Sending configuration commands...")
        output = connection.send_config_set(config_commands)
        print(output)

        print("Saving configuration...")
        save_output = connection.save_config()
        print(save_output)

        connection.disconnect()
        print("\nConfiguration completed successfully!")
        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
