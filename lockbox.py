import json
import os
import sys
from cryptography.fernet import Fernet

# File settings
KEY_FILE = "secret.key"
VAULT_FILE = "passwords.json"

def load_or_create_key():
    """Loads the master key or creates a new one if it doesn't exist."""
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        print("[!] NEW MASTER KEY GENERATED. Keep 'secret.key' safe!")
    return open(KEY_FILE, "rb").read()

# Initialize the encryption engine
try:
    cipher = Fernet(load_or_create_key())
except Exception as e:
    print(f"[!] Error loading encryption key: {e}")
    sys.exit(1)

def load_vault():
    """Reads the encrypted JSON file."""
    if not os.path.exists(VAULT_FILE):
        return {}
    with open(VAULT_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_vault(data):
    """Writes the dictionary to the JSON file."""
    with open(VAULT_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_password(service, password):
    vault = load_vault()
    encrypted = cipher.encrypt(password.encode()).decode()
    vault[service.lower()] = encrypted
    save_vault(vault)
    print(f"[+] Successfully locked password for: {service}")

def get_password(service):
    vault = load_vault()
    service = service.lower()
    if service in vault:
        encrypted = vault[service]
        decrypted = cipher.decrypt(encrypted.encode()).decode()
        print(f"[*] Password for {service}: {decrypted}")
    else:
        print(f"[!] No entry found for '{service}'.")

def list_services():
    vault = load_vault()
    if not vault:
        print("[!] The vault is currently empty.")
    else:
        print("[*] Stored Services:")
        for service in vault.keys():
            print(f" - {service}")

# Command line interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n--- LOCKBOX CLI ---")
        print("Usage:")
        print("  python3 lockbox.py add [service] [password]")
        print("  python3 lockbox.py get [service]")
        print("  python3 lockbox.py list")
    else:
        action = sys.argv[1].lower()
        if action == "add" and len(sys.argv) == 4:
            add_password(sys.argv[2], sys.argv[3])
        elif action == "get" and len(sys.argv) == 3:
            get_password(sys.argv[2])
        elif action == "list":
            list_services()
        else:
            print("[!] Invalid command or missing arguments.")
