import json
import os
import hashlib
import random
import string
from getpass import getpass
from cryptography.fernet import Fernet

DATA_FILE = "data.json"
MASTER_FILE = "master.hash"
KEY_FILE = "secret.key"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

def load_key():
    if not os.path.exists(KEY_FILE):
        generate_key()
    with open(KEY_FILE, "rb") as f:
        return f.read()

def encrypt_password(password, key):
    return Fernet(key).encrypt(password.encode()).decode()

def decrypt_password(encrypted_password, key):
    try:
        return Fernet(key).decrypt(encrypted_password.encode()).decode()
    except:
        return "[DECRYPTION FAILED]"

def setup_master_password():
    print("No master password found. Let's create one.")
    while True:
        password = getpass("Create master password: ")
        confirm = getpass("Confirm password: ")
        
        if password == confirm:
            if not password:
                print("Password cannot be empty.")
                continue
            with open(MASTER_FILE, "w") as f:
                f.write(hash_password(password))
            print("Master password set!\n")
            break
        else:
            print("Passwords do not match.")

def verify_master_password():
    if not os.path.exists(MASTER_FILE):
        setup_master_password()
    
    with open(MASTER_FILE, "r") as f:
        stored_hash = f.read()
    
    attempts = 3
    for attempt in range(attempts):
        print("\nLogin Required")
        password = getpass("Enter master password: ")
        
        if hash_password(password) == stored_hash:
            print("Access granted\n")
            return True
        else:
            remaining = attempts - attempt - 1
            if remaining > 0:
                print(f"Wrong password. {remaining} attempts remaining.")
            else:
                print("Too many failed attempts.")
    
    return False

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    
    try:
        with open(DATA_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        print("Data file corrupted. Starting fresh.")
        return []

def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except IOError:
        print("Failed to save data.")
        return False

def generate_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choice(chars) for _ in range(length))

def add_password(data, key):
    print("\nAdd New Password")
    
    site = input("Website: ").strip()
    if not site:
        print("Website name required.")
        return
    
    username = input("Username: ").strip()
    if not username:
        print("Username required.")
        return
    
    random_pw = input("Generate random password? (y/n): ").lower()
    
    if random_pw == "y":
        password = generate_password()
        print(f"Generated password: {password}")
        confirm = input("Save this password? (y/n): ").lower()
        if confirm != "y":
            print("Cancelled.")
            return
    else:
        password = getpass("Password: ").strip()
        if not password:
            print("Password cannot be empty.")
            return
    
    encrypted = encrypt_password(password, key)
    
    for entry in data:
        if entry["site"].lower() == site.lower() and entry["username"].lower() == username.lower():
            print("Entry already exists for this site and username.")
            return
    
    data.append({
        "site": site,
        "username": username,
        "password": encrypted
    })
    
    if save_data(data):
        print("Saved!")

def view_passwords(data, key):
    print("\nSaved Passwords")
    
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
            print("   Password: ********")

def search_password(data, key):
    print("\nSearch")
    
    keyword = input("Enter site name: ").lower().strip()
    if not keyword:
        print("No search term provided.")
        return
    
    results = [e for e in data if keyword in e['site'].lower()]
    
    if not results:
        print("No results found.")
        return
    
    for entry in results:
        decrypted = decrypt_password(entry["password"], key)
        print(f"\n{entry['site']}")
        print(f"   Username: {entry['username']}")
        print(f"   Password: {decrypted}")

def update_password(data, key):
    print("\nUpdate Password")
    
    if not data:
        print("No entries available.")
        return
    
    for i, entry in enumerate(data, start=1):
        print(f"[{i}] {entry['site']} - {entry['username']}")
    
    try:
        choice = int(input("Select entry number: "))
        if 1 <= choice <= len(data):
            entry = data[choice - 1]
            
            new_username = input(f"New username (current: {entry['username']}, press Enter to keep): ").strip()
            if new_username:
                entry["username"] = new_username
            
            random_pw = input("Generate random password? (y/n): ").lower()
            
            if random_pw == "y":
                new_password = generate_password()
                print(f"Generated password: {new_password}")
                confirm = input("Save this password? (y/n): ").lower()
                if confirm == "y":
                    entry["password"] = encrypt_password(new_password, key)
                    print("Password updated")
                else:
                    print("Password unchanged.")
            else:
                new_password = getpass("New password (press Enter to keep): ").strip()
                if new_password:
                    entry["password"] = encrypt_password(new_password, key)
            
            if save_data(data):
                print("Updated successfully")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Please enter a valid number.")

def delete_password(data):
    print("\nDelete Password")
    
    if not data:
        print("No passwords to delete.")
        return
    
    for i, entry in enumerate(data, start=1):
        print(f"[{i}] {entry['site']} - {entry['username']}")
    
    try:
        choice = int(input("Enter number to delete: "))
        if 1 <= choice <= len(data):
            confirm = input(f"Delete {data[choice-1]['site']}? (y/n): ").lower()
            if confirm == "y":
                removed = data.pop(choice - 1)
                if save_data(data):
                    print(f"Deleted {removed['site']}")
            else:
                print("Cancelled.")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Please enter a valid number.")

def export_backup(data, key):
    print("\nExport Backup")
    
    if not data:
        print("No data to export.")
        return
    
    filename = input("Filename (default: backup.txt): ").strip()
    if not filename:
        filename = "backup.txt"
    
    if not filename.endswith('.txt'):
        filename += '.txt'
    
    try:
        with open(filename, "w") as f:
            f.write("SITE | USERNAME | PASSWORD\n")
            f.write("-" * 50 + "\n")
            for entry in data:
                password = decrypt_password(entry["password"], key)
                if "[DECRYPTION FAILED]" not in password:
                    f.write(f"{entry['site']} | {entry['username']} | {password}\n")
                else:
                    f.write(f"{entry['site']} | {entry['username']} | [DECRYPTION FAILED]\n")
        
        print(f"Backup saved to {filename}")
    except IOError:
        print("Failed to create backup.")

def main():
    print("Password Manager")
    
    if not verify_master_password():
        print("Access denied. Exiting.")
        return
    
    key = load_key()
    data = load_data()
    
    while True:
        print("\n" + "="*30)
        print("1. Add Password")
        print("2. View Passwords")
        print("3. Search")
        print("4. Update")
        print("5. Delete")
        print("6. Export Backup")
        print("7. Exit")
        print("="*30)
        
        choice = input("Choose (1-7): ").strip()
        
        if choice == "1":
            add_password(data, key)
        elif choice == "2":
            view_passwords(data, key)
        elif choice == "3":
            search_password(data, key)
        elif choice == "4":
            update_password(data, key)
        elif choice == "5":
            delete_password(data)
        elif choice == "6":
            export_backup(data, key)
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose 1-7.")

if __name__ == "__main__":
    main()
