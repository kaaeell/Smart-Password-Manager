# 🔐 Smart Password Manager v1

import json
import os
from getpass import getpass

DATA_FILE = "data.json"
MASTER_PASSWORD = "1234"  # change this later


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def login():
    print("\n🔐 Login")
    password = getpass("Enter master password: ")
    if password == MASTER_PASSWORD:
        print("Login successful!\n")
        return True
    else:
        print("Wrong password 😢")
        return False


def add_password(data):
    print("\n➕ Add New Password")
    site = input("Website: ")
    username = input("Username: ")
    password = getpass("Password: ")

    data.append({
        "site": site,
        "username": username,
        "password": password
    })

    save_data(data)
    print("Saved successfully! ✅")


def view_passwords(data):
    print("\n📂 Saved Passwords")
    if not data:
        print("No passwords saved yet.")
        return

    for i, entry in enumerate(data, start=1):
        print(f"\n[{i}]")
        print(f"Site: {entry['site']}")
        print(f"Username: {entry['username']}")
        print(f"Password: {entry['password']}")


def search_password(data):
    print("\n🔍 Search")
    keyword = input("Enter website name: ").lower()

    found = False
    for entry in data:
        if keyword in entry['site'].lower():
            print("\nFound:")
            print(f"Site: {entry['site']}")
            print(f"Username: {entry['username']}")
            print(f"Password: {entry['password']}")
            found = True

    if not found:
        print("No results 😢")


def delete_password(data):
    view_passwords(data)
    if not data:
        return

    try:
        choice = int(input("\nEnter number to delete: "))
        removed = data.pop(choice - 1)
        save_data(data)
        print(f"Deleted {removed['site']} ✅")
    except:
        print("Invalid choice")


def main():
    print("🧠 Smart Password Manager v1")

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

        choice = input("Choose: ")

        if choice == "1":
            add_password(data)
        elif choice == "2":
            view_passwords(data)
        elif choice == "3":
            search_password(data)
        elif choice == "4":
            delete_password(data)
        elif choice == "5":
            print("Goodbye 👋")
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()

