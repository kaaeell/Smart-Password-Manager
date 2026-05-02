import json
import os
import hashlib
import random
import string
import sys
from datetime import datetime
from getpass import getpass
from cryptography.fernet import Fernet

DATA_FILE = "data.json"
MASTER_FILE = "master.hash"
KEY_FILE = "secret.key"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def header(title):
    clear()
    print("=" * 50)
    print(f"🔐 PASSWORD MANAGER - {title}")
    print("=" * 50)
    print()

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    with open(KEY_FILE, "rb") as f:
        return f.read()

def encrypt(text, key):
    return Fernet(key).encrypt(text.encode()).decode()

def decrypt(encrypted, key):
    try:
        return Fernet(key).decrypt(encrypted.encode()).decode()
    except:
        return "[ERROR]"

def setup_master():
    header("FIRST TIME")
    print("This master password unlocks everything. Don't forget it.\n")
    
    while True:
        pw = getpass("Create master password: ")
        confirm = getpass("Confirm: ")
        
        if pw == confirm and len(pw) >= 4:
            with open(MASTER_FILE, "w") as f:
                f.write(hash_pw(pw))
            print("\n✅ Done!")
            input("\nPress Enter...")
            return True
        print("Try again.\n")

def login():
    if not os.path.exists(MASTER_FILE):
        return setup_master()
    
    header("LOGIN")
    with open(MASTER_FILE, "r") as f:
        stored = f.read()
    
    for attempt in range(3):
        pw = getpass("Master password: ")
        if hash_pw(pw) == stored:
            return True
        print(f"Wrong. {2 - attempt} tries left.\n")
    
    print("Too many attempts.")
    return False

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f) if f.read().strip() else []
    except:
        return []

def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except:
        return False

def gen_password(length=14):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    pw = [random.choice(string.ascii_lowercase),
          random.choice(string.ascii_uppercase),
          random.choice(string.digits),
          random.choice("!@#$%^&*")]
    
    for _ in range(length - 4):
        pw.append(random.choice(chars))
    
    random.shuffle(pw)
    return ''.join(pw)

def check_strength(pw):
    score = 0
    if len(pw) >= 10:
        score += 1
    if any(c.islower() for c in pw) and any(c.isupper() for c in pw):
        score += 1
    if any(c.isdigit() for c in pw):
        score += 1
    if any(c in "!@#$%^&*" for c in pw):
        score += 1
    
    if score == 4:
        return "Strong"
    elif score == 3:
        return "Medium"
    return "Weak"

def add(data, key):
    header("ADD")
    
    site = input("Website: ").strip()
    if not site:
        return
    
    username = input("Username: ").strip()
    if not username:
        return
    
    # Check for duplicate
    for entry in data:
        if entry['site'].lower() == site.lower() and entry['username'].lower() == username.lower():
            print("Already exists!")
            input("\nPress Enter...")
            return
    
    print("\n1. Generate password")
    print("2. Type my own")
    choice = input("\nChoose (1/2): ")
    
    if choice == "1":
        length = input("Length (default 14): ").strip()
        length = int(length) if length.isdigit() and int(length) >= 6 else 14
        password = gen_password(length)
        print(f"\nPassword: {password}")
        print(f"Strength: {check_strength(password)}")
        if input("\nSave? (y/n): ").lower() != 'y':
            return
    
    elif choice == "2":
        password = getpass("Enter password: ")
        if not password:
            return
        print(f"Strength: {check_strength(password)}")
        if input("Save? (y/n): ").lower() != 'y':
            return
    else:
        return
    
    notes = input("Notes (optional): ").strip()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    data.append({
        "site": site,
        "username": username,
        "password": encrypt(password, key),
        "notes": notes,
        "created": now,
        "updated": now
    })
    
    if save_data(data):
        print("\n✅ Saved!")
    input("\nPress Enter...")

def view(data, key):
    header("ALL PASSWORDS")
    
    if not data:
        print("Nothing saved yet.")
        input("\nPress Enter...")
        return
    
    show = input("Show passwords? (y/n): ").lower() == 'y'
    
    for i, entry in enumerate(data, 1):
        print(f"\n{i}. {entry['site']}")
        print(f"   Username: {entry['username']}")
        
        if show:
            pw = decrypt(entry['password'], key)
            print(f"   Password: {pw}")
            if "[ERROR]" not in pw:
                print(f"   Strength: {check_strength(pw)}")
        else:
            print(f"   Password: {'*'*10}")
        
        if entry.get('notes'):
            print(f"   Notes: {entry['notes'][:40]}")
    
    print(f"\nTotal: {len(data)}")
    input("\nPress Enter...")

def search(data, key):
    header("SEARCH")
    
    term = input("Search: ").lower().strip()
    if not term:
        return
    
    results = [e for e in data if term in e['site'].lower() or term in e['username'].lower()]
    
    if not results:
        print("Not found.")
        input("\nPress Enter...")
        return
    
    show = input("Show passwords? (y/n): ").lower() == 'y'
    
    for entry in results:
        print(f"\n{entry['site']} - {entry['username']}")
        if show:
            print(f"Password: {decrypt(entry['password'], key)}")
    
    input("\nPress Enter...")

def update(data, key):
    header("UPDATE")
    
    if not data:
        print("No entries.")
        input("\nPress Enter...")
        return
    
    for i, entry in enumerate(data, 1):
        print(f"{i}. {entry['site']} - {entry['username']}")
    
    try:
        choice = int(input("\nNumber to update: "))
        entry = data[choice-1]
        
        print(f"\nEditing: {entry['site']}")
        print("(Leave blank to keep current)\n")
        
        new_user = input(f"Username [{entry['username']}]: ").strip()
        if new_user:
            entry['username'] = new_user
        
        if input("Update password? (y/n): ").lower() == 'y':
            print("\n1. Generate new")
            print("2. Type new")
            if input("Choose (1/2): ") == "1":
                length = input("Length (14): ").strip()
                length = int(length) if length.isdigit() else 14
                new_pw = gen_password(length)
                print(f"New: {new_pw}")
                if input("Save? (y/n): ").lower() == 'y':
                    entry['password'] = encrypt(new_pw, key)
            else:
                new_pw = getpass("New password: ")
                if new_pw:
                    entry['password'] = encrypt(new_pw, key)
        
        new_notes = input(f"Notes [{entry.get('notes', '')}]: ").strip()
        if new_notes:
            entry['notes'] = new_notes
        
        entry['updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if save_data(data):
            print("\n✅ Updated!")
    except:
        print("Invalid choice.")
    
    input("\nPress Enter...")

def delete(data):
    header("DELETE")
    
    if not data:
        print("Nothing to delete.")
        input("\nPress Enter...")
        return
    
    for i, entry in enumerate(data, 1):
        print(f"{i}. {entry['site']} - {entry['username']}")
    
    try:
        choice = int(input("\nNumber to delete: "))
        entry = data[choice-1]
        
        confirm = input(f"Delete '{entry['site']}'? Type 'yes': ")
        if confirm.lower() == 'yes':
            data.pop(choice-1)
            if save_data(data):
                print("\n✅ Deleted!")
        else:
            print("Cancelled.")
    except:
        print("Invalid choice.")
    
    input("\nPress Enter...")

def export_data(data, key):
    header("EXPORT")
    
    if not data:
        print("Nothing to export.")
        input("\nPress Enter...")
        return
    
    print("1. TXT (readable)")
    print("2. CSV (Excel)")
    choice = input("\nChoose (1/2): ")
    
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if choice == "1":
        filename = f"backup_{ts}.txt"
        with open(filename, "w") as f:
            f.write(f"Password Export - {datetime.now()}\n\n")
            for entry in data:
                f.write(f"Site: {entry['site']}\n")
                f.write(f"Username: {entry['username']}\n")
                f.write(f"Password: {decrypt(entry['password'], key)}\n")
                if entry.get('notes'):
                    f.write(f"Notes: {entry['notes']}\n")
                f.write("-"*30 + "\n\n")
        print(f"\n✅ Saved to {filename}")
    
    elif choice == "2":
        filename = f"backup_{ts}.csv"
        import csv
        with open(filename, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Site", "Username", "Password", "Notes"])
            for entry in data:
                writer.writerow([
                    entry['site'],
                    entry['username'],
                    decrypt(entry['password'], key),
                    entry.get('notes', '')
                ])
        print(f"\n✅ Saved to {filename}")
    
    else:
        print("Invalid.")
    
    input("\nPress Enter...")

def stats(data, key):
    header("STATS")
    
    if not data:
        print("No data yet.")
        input("\nPress Enter...")
        return
    
    strong = medium = weak = 0
    
    for entry in data:
        pw = decrypt(entry['password'], key)
        if "[ERROR]" not in pw:
            s = check_strength(pw)
            if s == "Strong":
                strong += 1
            elif s == "Medium":
                medium += 1
            else:
                weak += 1
    
    print(f"Total passwords: {len(data)}")
    print(f"Unique sites: {len(set(e['site'].lower() for e in data))}")
    print(f"\nPassword strength:")
    print(f"  Strong: {strong}")
    print(f"  Medium: {medium}")
    print(f"  Weak: {weak}")
    
    input("\nPress Enter...")

def change_master():
    header("CHANGE MASTER")
    
    if not os.path.exists(MASTER_FILE):
        print("No master password set.")
        input("\nPress Enter...")
        return
    
    with open(MASTER_FILE, "r") as f:
        stored = f.read()
    
    old = getpass("Current master password: ")
    if hash_pw(old) != stored:
        print("Wrong password.")
        input("\nPress Enter...")
        return
    
    while True:
        new = getpass("New master password: ")
        confirm = getpass("Confirm: ")
        
        if new == confirm and len(new) >= 4:
            with open(MASTER_FILE, "w") as f:
                f.write(hash_pw(new))
            print("\n✅ Changed!")
            break
        print("Try again.\n")
    
    input("\nPress Enter...")

def main():
    if not login():
        sys.exit(1)
    
    key = load_key()
    data = load_data()
    
    while True:
        header("MENU")
        print("1. Add")
        print("2. View all")
        print("3. Search")
        print("4. Update")
        print("5. Delete")
        print("6. Export")
        print("7. Statistics")
        print("8. Change master password")
        print("9. Exit")
        print("=" * 50)
        
        choice = input("Choose (1-9): ")
        
        if choice == "1":
            add(data, key)
        elif choice == "2":
            view(data, key)
        elif choice == "3":
            search(data, key)
        elif choice == "4":
            update(data, key)
        elif choice == "5":
            delete(data)
        elif choice == "6":
            export_data(data, key)
        elif choice == "7":
            stats(data, key)
        elif choice == "8":
            change_master()
        elif choice == "9":
            header("BYE")
            print("Stay safe!")
            input("\nPress Enter...")
            clear()
            break
        else:
            print("Choose 1-9")
            input("\nPress Enter...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nLater!")
        sys.exit(0)
