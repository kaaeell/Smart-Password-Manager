# 🔐 Smart Password Manager v2
# simple CLI app to store and manage passwords
# built while learning python (and trying not to forget my own passwords 😅)

import json
import os
from getpass import getpass

DATA_FILE = "data.json"
MASTER_PASSWORD = "1234"  # TODO: replace this with something secure later


# ---------- basic file handling ----------

def load_data():
    """Load saved passwords from file (if it exists)."""
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("⚠️ Data file is corrupted. Starting fresh.")
        return []


def save_data(data):
    """Save passwords to file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------- authentication ----------

def login():
    """Simple login system using master password."""
    print("\n🔐 Login Required")
    password = getpass("Enter master password: ")

    if password == MASTER_PASSWORD:
        print("✅ Access granted\n")
        return True

    print("❌ Wrong password")
    return False


# ---------- core features ----------

def add_password(data):
    """Add a new password entry."""
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
    print("✅ Password saved successfully!")


def view_passwords(data):
    """Display all saved passwords."""
    print("\n📂 Saved Passwords")

    if not data:
        print("No passwords saved yet.")
        return

    for i, entry in enumerate(data, start=1):
        print(f"\n[{i}] {entry['site']}")
        print(f"   Username: {entry['username']}")
        print(f"   Password: {entry['password']}")


def search_password(data):
    """Search for a password by website name."""
    print("\n🔍 Search Passwords")

    keyword = input("Enter website name: ").lower().strip()

    results = [entry for entry in data if keyword in entry['site'].lower()]

    if not results:
        print("❌ No results found.")
        return

    print(f"\nFound {len(results)} result(s):")
    for entry in results:
        print(f"\nSite: {entry['site']}")
        print(f"Username: {entry['username']}")
        print(f"Password: {entry['password']}")


def delete_password(data):
    """Delete a password entry by index."""
    view_passwords(data)

    if not data:
        return

    try:
        choice = int(input("\nEnter number to delete: "))
        if choice < 1 or choice > len(data):
            print("⚠️ Invalid number.")
            return

        removed = data.pop(choice - 1)
        save_data(data)

        print(f"🗑️ Deleted: {removed['site']}")

    except ValueError:
        print("⚠️ Please enter a valid number.")


# ---------- main app loop ----------

def main():
    print("🧠 Smart Password Manager v2")

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

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_password(data)
        elif choice == "2":
            view_passwords(data)
        elif choice == "3":
            search_password(data)
        elif choice == "4":
            delete_password(data)
        elif choice == "5":
            print("👋 Exiting... stay safe.")
            break
        else:
            print("⚠️ Invalid option. Try again.")


if __name__ == "__main__":
    main()
