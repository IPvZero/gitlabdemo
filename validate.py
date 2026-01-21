from netmiko import ConnectHandler
import sys
import yaml


def load_inventory(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if "device" not in data or not isinstance(data["device"], dict):
        raise ValueError("Inventory must contain a top-level 'device:' mapping")
    return data["device"]


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate.py <inventory.yml>")
        sys.exit(2)

    inventory_path = sys.argv[1]

    try:
        device = load_inventory(inventory_path)

        print("Connecting to device...")
        connection = ConnectHandler(**device)

        # Get interface information (TextFSM will auto-parse if template exists)
        output = connection.send_command("show ip interface brief", use_textfsm=True)

        connection.disconnect()

        # Check if output was parsed (list of dicts) or raw text (string)
        if isinstance(output, list):
            # TextFSM parsing successful
            print("Parsed interface data:")
            for interface in output:
                if "Loopback100" in interface.get("interface", ""):
                    print("\n✓ Found Loopback100!")
                    print(f"  IP Address: {interface.get('ip_address', 'N/A')}")
                    print(f"  Status: {interface.get('status', 'N/A')}")
                    print(f"  Protocol: {interface.get('proto', 'N/A')}")
                    print("\nValidation PASSED!")
                    sys.exit(0)

            print("\n✗ Loopback100 NOT found!")
            print("Validation FAILED!")
            sys.exit(1)

        else:
            # Fallback to string parsing if TextFSM didn't work
            print("Raw output:")
            print(output)
            if "Loopback100" in output and "10.100.100.1" in output:
                print("\n✓ Validation PASSED!")
                sys.exit(0)
            else:
                print("\n✗ Validation FAILED!")
                sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
