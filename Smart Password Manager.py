import json
import os
import hashlib
from getpass import getpass
from cryptography.fernet import Fernet

DATA_FILE = "data.json"
MASTER_FILE = "master.hash"
KEY_FILE = "secret.key"


# ---------- security utils ----------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)


def load_key():
    if not os.path.exists(KEY_FILE):
        generate_key()
    return open(KEY_FILE, "rb").read()


def encrypt_password(password, key):
    return Fernet(key).encrypt(password.encode()).decode()


def decrypt_password(encrypted_password, key):
    return Fernet(key).decrypt(encrypted_password.encode()).decode()


# ---------- master password ----------

def setup_master_password():
    print("🔐 No master password found. Let's create one.")
    while True:
        password = getpass("Create master password: ")
        confirm = getpass("Confirm password: ")

        if password == confirm:
            with open(MASTER_FILE, "w") as f:
                f.write(hash_password(password))
            print("✅ Master password set!\n")
            break
        else:
            print("❌ Passwords do not match.")


def verify_master_password():
    if not os.path.exists(MASTER_FILE):
        setup_master_password()

    with open(MASTER_FILE, "r") as f:
        stored_hash = f.read()

    print("\n🔐 Login Required")
    password = getpass("Enter master password: ")

    if hash_password(password) == stored_hash:
        print("✅ Access granted\n")
        return True

    print("❌ Wrong password")
    return False


# ---------- file handling ----------

def load_data():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        print("⚠️ Data corrupted. Resetting.")
        return []


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------- features ----------

def add_password(data, key):
    print("\n➕ Add New Password")

    site = input("Website: ").strip()
    username = input("Username: ").strip()
    password = getpass("Password: ").strip()

    if not site or not username or not password:
        print("⚠️ All fields required.")
        return

    encrypted = encrypt_password(password, key)

    data.append({
        "site": site,
        "username": username,
        "password": encrypted
    })

    save_data(data)
    print("✅ Saved securely!")


def view_passwords(data, key):
    print("\n📂 Saved Passwords")

    if not data:
        print("No passwords yet.")
        return

    show = input("Show passwords? (y/n): ").lower()

    for i, entry in enumerate(data, start=1):
        print(f"\n[{i}] {entry['site']}")
        print(f"   Username: {entry['username']}")

        if show == "y":
            decrypted = decrypt_password(entry["password"], key)
            print(f"   Password: {decrypted}")
        else:
            print("   Password: ******")


def search_password(data, key):
    print("\n🔍 Search")

    keyword = input("Enter site: ").lower().strip()
    results = [e for e in data if keyword in e['site'].lower()]

    if not results:
        print("❌ No results.")
        return

    for entry in results:
        decrypted = decrypt_password(entry["password"], key)
        print(f"\n🌐 {entry['site']}")
        print(f"👤 {entry['username']}")
        print(f"🔑 {decrypted}")


def delete_password(data):
    if not data:
        print("No passwords to delete.")
        return

    for i, entry in enumerate(data, start=1):
        print(f"[{i}] {entry['site']}")

    try:
        choice = int(input("Enter number to delete: "))
        if 1 <= choice <= len(data):
            removed = data.pop(choice - 1)
            save_data(data)
            print(f"🗑️ Deleted {removed['site']}")
        else:
            print("⚠️ Invalid choice.")
    except:
        print("⚠️ Enter a valid number.")


# ---------- main ----------

def main():
    print("🧠 Smart Password Manager v5")

    if not verify_master_password():
        return

    key = load_key()
    data = load_data()

    while True:
        print("""
1. Add Password
2. View Passwords
3. Search
4. Delete
5. Exit
""")

        choice = input("Choose: ").strip()

        if choice == "1":
            add_password(data, key)
        elif choice == "2":
            view_passwords(data, key)
        elif choice == "3":
            search_password(data, key)
        elif choice == "4":
            delete_password(data)
        elif choice == "5":
            print("👋 Bye, stay safe.")
            break
        else:
            print("⚠️ Invalid option.")


if __name__ == "__main__":
    main()
