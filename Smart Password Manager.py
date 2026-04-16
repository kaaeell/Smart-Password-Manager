# 🔐 Smart Password Manager v3
# safer, cleaner, and more "real-world ready"

import json
import os
import hashlib
from getpass import getpass

DATA_FILE = "data.json"
MASTER_HASH = hashlib.sha256("1234".encode()).hexdigest()  # change this!


# ---------- utils ----------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ---------- file handling ----------

def load_data():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("⚠️ Data corrupted. Starting fresh.")
        return []


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------- authentication ----------

def login():
    print("\n🔐 Login Required")
    password = getpass("Enter master password: ")

    if hash_password(password) == MASTER_HASH:
        print("✅ Access granted\n")
        return True

    print("❌ Wrong password")
    return False


# ---------- core features ----------

def add_password(data):
    print("\n➕ Add New Password")

    site = input("Website: ").strip()
    username = input("Username: ").strip()
    password = getpass("Password: ").strip()

    if not site or not username or not password:
        print("⚠️ All fields are required.")
        return

    data.append({
        "site": site,
        "username": username,
        "password": password
    })

    save_data(data)
    print("✅ Saved!")


def view_passwords(data):
    print("\n📂 Saved Passwords")

    if not data:
        print("No passwords yet.")
        return

    show = input("Show passwords? (y/n): ").lower()

    for i, entry in enumerate(data, start=1):
        print(f"\n[{i}] {entry['site']}")
        print(f"   Username: {entry['username']}")

        if show == "y":
            print(f"   Password: {entry['password']}")
        else:
            print("   Password: ******")


def search_password(data):
    print("\n🔍 Search")

    keyword = input("Enter site: ").lower().strip()

    results = [e for e in data if keyword in e['site'].lower()]

    if not results:
        print("❌ No results.")
        return

    for entry in results:
        print(f"\n🌐 {entry['site']}")
        print(f"👤 {entry['username']}")
        print(f"🔑 {entry['password']}")


def delete_password(data):
    view_passwords(data)

    if not data:
        return

    try:
        choice = int(input("\nEnter number to delete: "))
        if 1 <= choice <= len(data):
            removed = data.pop(choice - 1)
            save_data(data)
            print(f"🗑️ Deleted {removed['site']}")
        else:
            print("⚠️ Invalid choice.")
    except ValueError:
        print("⚠️ Enter a number.")


# ---------- main ----------

def main():
    print("🧠 Smart Password Manager v3")

    if not login():
        return

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
            add_password(data)
        elif choice == "2":
            view_passwords(data)
        elif choice == "3":
            search_password(data)
        elif choice == "4":
            delete_password(data)
        elif choice == "5":
            print("👋 Bye, stay safe.")
            break
        else:
            print("⚠️ Invalid option.")


if __name__ == "__main__":
    main()
