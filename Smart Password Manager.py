import json
import os
import hashlib
import random
import string
import time
import sys
from datetime import datetime
from getpass import getpass
from cryptography.fernet import Fernet

# File paths - where we store everything
DATA_FILE = "data.json"           # Stores all your passwords (encrypted)
MASTER_FILE = "master.hash"       # Stores your master password hash
KEY_FILE = "secret.key"           # Stores encryption key (KEEP THIS SAFE!)

def clear_screen():
    """Clears terminal screen - works on Windows, Mac, and Linux"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Prints a nice formatted header for better UI"""
    clear_screen()
    print("=" * 50)
    print(f"🔐 PASSWORD MANAGER - {title}")
    print("=" * 50)
    print()

def hash_password(password):
    """Convert password to hash using SHA-256 (can't be reversed!)"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_key():
    """Creates a new encryption key for securing passwords"""
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    print("✅ Encryption key created!")

def load_key():
    """Loads existing encryption key or creates a new one"""
    if not os.path.exists(KEY_FILE):
        generate_key()
    with open(KEY_FILE, "rb") as f:
        return f.read()

def encrypt_password(password, key):
    """Encrypts a password so it's safe to store"""
    return Fernet(key).encrypt(password.encode()).decode()

def decrypt_password(encrypted_password, key):
    """Decrypts a password when you need to see it"""
    try:
        return Fernet(key).decrypt(encrypted_password.encode()).decode()
    except:
        return "[DECRYPTION FAILED]"

def setup_master_password():
    """First-time setup - create your master password"""
    print_header("FIRST TIME SETUP")
    print("Welcome to Password Manager!")
    print("This master password unlocks ALL your saved passwords.")
    print("Don't forget it - there's no 'reset' button!\n")
    
    while True:
        password = getpass("🔑 Create master password: ")
        confirm = getpass("🔑 Confirm master password: ")
        
        if password == confirm:
            if len(password) < 4:
                print("⚠️  Password must be at least 4 characters long.\n")
                continue
            if not password:
                print("⚠️  Password cannot be empty.\n")
                continue
            
            # Save the hashed version (never store real password!)
            with open(MASTER_FILE, "w") as f:
                f.write(hash_password(password))
            print("\n✅ Master password set successfully!")
            print("💡 Tip: Store it somewhere safe!")
            time.sleep(2)
            break
        else:
            print("❌ Passwords don't match. Try again.\n")

def verify_master_password():
    """Ask for master password and verify it (3 attempts only!)"""
    if not os.path.exists(MASTER_FILE):
        setup_master_password()
        return True
    
    print_header("LOGIN")
    
    with open(MASTER_FILE, "r") as f:
        stored_hash = f.read()
    
    attempts = 3
    for attempt in range(attempts):
        password = getpass("Enter master password: ")
        
        if hash_password(password) == stored_hash:
            print("\n✅ Access granted! Welcome back!")
            time.sleep(0.5)
            return True
        else:
            remaining = attempts - attempt - 1
            if remaining > 0:
                print(f"❌ Wrong password. {remaining} attempt(s) remaining.\n")
            else:
                print("\n🔒 Too many failed attempts. Exiting for security.")
                time.sleep(1)
                return False
    
    return False

def load_data():
    """Load all saved passwords from JSON file"""
    if not os.path.exists(DATA_FILE):
        return []
    
    try:
        with open(DATA_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        print("⚠️  Data file corrupted. Starting fresh.")
        return []

def save_data(data):
    """Save passwords to JSON file"""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except IOError:
        print("❌ Failed to save data.")
        return False

def generate_password(length=12, use_special=True):
    """Generate a strong random password - perfect for new accounts!"""
    chars = string.ascii_letters + string.digits
    if use_special:
        chars += "!@#$%^&*"
    
    # Make sure we have at least one of each type
    password = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
    ]
    
    if use_special:
        password.append(random.choice("!@#$%^&*"))
    
    # Fill the rest randomly
    for _ in range(length - len(password)):
        password.append(random.choice(chars))
    
    # Shuffle to avoid predictable patterns
    random.shuffle(password)
    return ''.join(password)

def check_password_strength(password):
    """Check how strong a password is and give tips to improve it"""
    strength = 0
    feedback = []
    
    # Check length
    if len(password) >= 12:
        strength += 1
    elif len(password) >= 8:
        feedback.append("⚠️  Make it at least 12 characters")
    else:
        feedback.append("❌ Too short (min 8 characters)")
    
    # Check for mixed case
    if any(c.islower() for c in password) and any(c.isupper() for c in password):
        strength += 1
    else:
        feedback.append("⚠️  Add both uppercase and lowercase letters")
    
    # Check for numbers
    if any(c.isdigit() for c in password):
        strength += 1
    else:
        feedback.append("⚠️  Add numbers")
    
    # Check for special characters
    if any(c in "!@#$%^&*" for c in password):
        strength += 1
    else:
        feedback.append("⚠️  Add special characters (!@#$%^&*)")
    
    if strength == 4:
        return "💪 Strong!", feedback
    elif strength == 3:
        return "👍 Medium", feedback
    else:
        return "⚠️  Weak", feedback

def add_password(data, key):
    """Add a new password to your vault"""
    print_header("ADD NEW PASSWORD")
    
    site = input("🌐 Website/Service (e.g., Google, GitHub): ").strip()
    if not site:
        print("❌ Website name required.")
        input("\nPress Enter to continue...")
        return
    
    username = input("👤 Username/Email: ").strip()
    if not username:
        print("❌ Username required.")
        input("\nPress Enter to continue...")
        return
    
    # Check for duplicates to avoid confusion
    for entry in data:
        if entry["site"].lower() == site.lower() and entry["username"].lower() == username.lower():
            print("⚠️  You already saved a password for this site and username!")
            input("\nPress Enter to continue...")
            return
    
    print("\n--- How do you want to create the password? ---")
    print("1. 🔄 Generate a random strong password (recommended)")
    print("2. ✏️  Type my own password")
    print("3. ❌ Cancel")
    
    choice = input("\nChoose (1-3): ").strip()
    
    if choice == "1":
        # Generate random password
        length = input("Password length (default 16, more = stronger): ").strip()
        length = int(length) if length.isdigit() and int(length) >= 8 else 16
        
        use_special = input("Include special characters? (y/n, default y): ").lower()
        use_special = use_special != 'n'
        
        password = generate_password(length, use_special)
        strength_text, _ = check_password_strength(password)
        
        print(f"\n🔑 Generated password: {password}")
        print(f"📊 Strength: {strength_text}")
        
        confirm = input("\nSave this password? (y/n): ").lower()
        if confirm != "y":
            print("❌ Cancelled.")
            input("\nPress Enter to continue...")
            return
        
    elif choice == "2":
        password = getpass("🔑 Enter your password: ").strip()
        if not password:
            print("❌ Password cannot be empty.")
            input("\nPress Enter to continue...")
            return
        
        strength_text, feedback = check_password_strength(password)
        print(f"\n📊 Strength: {strength_text}")
        
        if feedback:
            print("\n💡 Tips to make it stronger:")
            for tip in feedback:
                print(f"   {tip}")
        
        confirm = input("\nSave this password? (y/n): ").lower()
        if confirm != "y":
            print("❌ Cancelled.")
            input("\nPress Enter to continue...")
            return
    else:
        print("❌ Cancelled.")
        input("\nPress Enter to continue...")
        return
    
    # Optional notes field
    notes = input("\n📝 Notes (optional - e.g., 'used for school account'): ").strip()
    
    # Add timestamp for tracking
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Encrypt before storing
    encrypted = encrypt_password(password, key)
    
    data.append({
        "site": site,
        "username": username,
        "password": encrypted,
        "notes": notes,
        "created": timestamp,
        "updated": timestamp
    })
    
    if save_data(data):
        print("\n✅ Password saved successfully!")
    
    input("\nPress Enter to continue...")

def view_passwords(data, key):
    """Show all your saved passwords"""
    print_header("ALL PASSWORDS")
    
    if not data:
        print("📭 No passwords saved yet. Add some first!")
        input("\nPress Enter to continue...")
        return
    
    # Ask if user wants to see actual passwords (privacy)
    show_passwords = input("🔓 Show actual passwords? (y/n, default n): ").lower() == 'y'
    
    for i, entry in enumerate(data, start=1):
        print(f"\n{'─' * 40}")
        print(f"[{i}] {entry['site'].upper()}")
        print(f"   👤 Username: {entry['username']}")
        
        if show_passwords:
            decrypted = decrypt_password(entry["password"], key)
            print(f"   🔑 Password: {decrypted}")
            
            # Show strength if we can read it
            if "[DECRYPTION FAILED]" not in decrypted:
                strength, _ = check_password_strength(decrypted)
                print(f"   📊 Strength: {strength}")
        else:
            print(f"   🔑 Password: {'*' * 12} (hidden)")
        
        if entry.get("notes"):
            print(f"   📝 Notes: {entry['notes'][:50]}")
        
        print(f"   📅 Last updated: {entry.get('updated', 'Unknown')}")
    
    print(f"\n{'─' * 40}")
    print(f"📊 Total: {len(data)} password(s)")

def search_password(data, key):
    """Quickly find a specific password"""
    print_header("SEARCH")
    
    keyword = input("🔍 Enter website name or username: ").lower().strip()
    if not keyword:
        print("❌ No search term provided.")
        input("\nPress Enter to continue...")
        return
    
    # Search in both site name and username
    results = []
    for entry in data:
        if keyword in entry['site'].lower() or keyword in entry['username'].lower():
            results.append(entry)
    
    if not results:
        print(f"❌ No results found for '{keyword}'")
        input("\nPress Enter to continue...")
        return
    
    print(f"\n✅ Found {len(results)} result(s):\n")
    show_passwords = input("🔓 Show passwords? (y/n, default n): ").lower() == 'y'
    
    for entry in results:
        print(f"\n{'─' * 30}")
        print(f"🌐 {entry['site']}")
        print(f"👤 Username: {entry['username']}")
        
        if show_passwords:
            decrypted = decrypt_password(entry["password"], key)
            print(f"🔑 Password: {decrypted}")
        
        if entry.get("notes"):
            print(f"📝 Notes: {entry['notes'][:50]}")
    
    input("\nPress Enter to continue...")

def update_password(data, key):
    """Edit an existing password entry"""
    print_header("UPDATE PASSWORD")
    
    if not data:
        print("📭 No entries available.")
        input("\nPress Enter to continue...")
        return
    
    # Show all entries with numbers
    for i, entry in enumerate(data, start=1):
        print(f"[{i}] {entry['site']} - {entry['username']}")
    
    try:
        choice = int(input("\n📌 Select entry number to update: "))
        if 1 <= choice <= len(data):
            entry = data[choice - 1]
            
            print(f"\nUpdating: {entry['site']} ({entry['username']})")
            print("💡 Press Enter to keep current value\n")
            
            # Update username
            new_username = input(f"👤 New username [current: {entry['username']}]: ").strip()
            if new_username:
                entry["username"] = new_username
            
            # Update password
            update_pw = input("🔑 Update password? (y/n): ").lower()
            if update_pw == 'y':
                print("\n1. 🔄 Generate random password")
                print("2. ✏️  Enter manually")
                pw_choice = input("\nChoose (1/2): ").strip()
                
                if pw_choice == "1":
                    length = input("Length (default 16): ").strip()
                    length = int(length) if length.isdigit() and int(length) >= 8 else 16
                    new_password = generate_password(length)
                    print(f"\n🔑 New password: {new_password}")
                    confirm = input("Save this password? (y/n): ").lower()
                    if confirm == 'y':
                        entry["password"] = encrypt_password(new_password, key)
                        print("✅ Password updated")
                else:
                    new_password = getpass("🔑 New password: ").strip()
                    if new_password:
                        entry["password"] = encrypt_password(new_password, key)
                        print("✅ Password updated")
            
            # Update notes
            new_notes = input(f"📝 New notes [current: {entry.get('notes', 'None')}]: ").strip()
            if new_notes:
                entry["notes"] = new_notes
            
            # Update timestamp
            entry["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if save_data(data):
                print("\n✅ Entry updated successfully!")
        else:
            print("❌ Invalid choice.")
    except ValueError:
        print("❌ Please enter a valid number.")
    
    input("\nPress Enter to continue...")

def delete_password(data):
    """Remove a password from your vault"""
    print_header("DELETE PASSWORD")
    
    if not data:
        print("📭 No passwords to delete.")
        input("\nPress Enter to continue...")
        return
    
    for i, entry in enumerate(data, start=1):
        print(f"[{i}] {entry['site']} - {entry['username']}")
    
    try:
        choice = int(input("\n📌 Enter number to delete: "))
        if 1 <= choice <= len(data):
            entry = data[choice - 1]
            print(f"\n⚠️  WARNING: You're about to delete '{entry['site']}'")
            confirm = input(f"Type 'DELETE' to confirm: ").strip()
            
            if confirm == "DELETE":
                removed = data.pop(choice - 1)
                if save_data(data):
                    print(f"\n✅ Deleted '{removed['site']}'")
            else:
                print("\n❌ Cancelled - nothing was deleted")
        else:
            print("❌ Invalid choice.")
    except ValueError:
        print("❌ Please enter a valid number.")
    
    input("\nPress Enter to continue...")

def export_backup(data, key):
    """Create a backup of all your passwords"""
    print_header("EXPORT BACKUP")
    
    if not data:
        print("📭 No data to export.")
        input("\nPress Enter to continue...")
        return
    
    print("Choose export format:")
    print("1. 📄 TXT (easy to read)")
    print("2. 📊 CSV (for Excel/Google Sheets)")
    print("3. 🔧 JSON (raw format)")
    
    choice = input("\nChoose format (1-3): ").strip()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if choice == "1":
        filename = f"password_backup_{timestamp}.txt"
        try:
            with open(filename, "w") as f:
                f.write("PASSWORD MANAGER BACKUP\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*60 + "\n\n")
                
                for entry in data:
                    password = decrypt_password(entry["password"], key)
                    f.write(f"Site: {entry['site']}\n")
                    f.write(f"Username: {entry['username']}\n")
                    f.write(f"Password: {password if '[DECRYPTION FAILED]' not in password else '*****'}\n")
                    if entry.get("notes"):
                        f.write(f"Notes: {entry['notes']}\n")
                    f.write("-"*40 + "\n\n")
            
            print(f"\n✅ Backup saved to {filename}")
            print("💡 Move this file somewhere safe!")
        except IOError:
            print("❌ Failed to create backup.")
    
    elif choice == "2":
        filename = f"password_backup_{timestamp}.csv"
        try:
            import csv
            with open(filename, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Site", "Username", "Password", "Notes", "Created", "Updated"])
                for entry in data:
                    password = decrypt_password(entry["password"], key)
                    writer.writerow([
                        entry['site'],
                        entry['username'],
                        password if '[DECRYPTION FAILED]' not in password else '*****',
                        entry.get('notes', ''),
                        entry.get('created', ''),
                        entry.get('updated', '')
                    ])
            print(f"\n✅ Backup saved to {filename}")
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    elif choice == "3":
        filename = f"password_backup_{timestamp}.json"
        try:
            # Create a readable copy for backup
            backup_data = []
            for entry in data:
                entry_copy = entry.copy()
                entry_copy['password'] = decrypt_password(entry["password"], key)
                backup_data.append(entry_copy)
            
            with open(filename, "w") as f:
                json.dump(backup_data, f, indent=2)
            print(f"\n✅ Backup saved to {filename}")
            print("⚠️  WARNING: This backup has UNENCRYPTED passwords!")
            print("    Keep it in a secure place!")
        except IOError:
            print("❌ Failed to create backup.")
    else:
        print("❌ Invalid choice.")
    
    input("\nPress Enter to continue...")

def import_backup(data, key):
    """Import passwords from a backup file"""
    print_header("IMPORT BACKUP")
    
    print("Supported formats: .json or .csv")
    filename = input("📁 Enter backup filename: ").strip()
    
    if not filename:
        print("❌ No filename provided.")
        input("\nPress Enter to continue...")
        return
    
    if not os.path.exists(filename):
        print(f"❌ File '{filename}' not found.")
        input("\nPress Enter to continue...")
        return
    
    imported_count = 0
    
    try:
        if filename.endswith('.json'):
            with open(filename, "r") as f:
                imported_data = json.load(f)
            
            for item in imported_data:
                # Skip if already exists
                exists = any(
                    e['site'].lower() == item['site'].lower() and 
                    e['username'].lower() == item['username'].lower() 
                    for e in data
                )
                
                if not exists and item.get('password'):
                    encrypted = encrypt_password(item['password'], key)
                    data.append({
                        "site": item['site'],
                        "username": item['username'],
                        "password": encrypted,
                        "notes": item.get('notes', ''),
                        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    imported_count += 1
        
        elif filename.endswith('.csv'):
            import csv
            with open(filename, "r", encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    exists = any(
                        e['site'].lower() == row['Site'].lower() and 
                        e['username'].lower() == row['Username'].lower() 
                        for e in data
                    )
                    
                    if not exists and row.get('Password') and row['Password'] != '*****':
                        encrypted = encrypt_password(row['Password'], key)
                        data.append({
                            "site": row['Site'],
                            "username": row['Username'],
                            "password": encrypted,
                            "notes": row.get('Notes', ''),
                            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        imported_count += 1
        
        else:
            print("❌ Unsupported file format. Use .json or .csv")
            input("\nPress Enter to continue...")
            return
        
        if imported_count > 0 and save_data(data):
            print(f"\n✅ Successfully imported {imported_count} new entry(s)!")
        else:
            print("\n📭 No new entries were imported (duplicates or empty)")
    
    except Exception as e:
        print(f"❌ Import failed: {e}")
    
    input("\nPress Enter to continue...")

def view_stats(data, key):
    """Show statistics about your password collection"""
    print_header("STATISTICS")
    
    if not data:
        print("📭 No passwords stored yet.")
        input("\nPress Enter to continue...")
        return
    
    total = len(data)
    weak = medium = strong = 0
    
    # Analyze password strength
    for entry in data:
        decrypted = decrypt_password(entry["password"], key)
        if "[DECRYPTION FAILED]" not in decrypted:
            strength, _ = check_password_strength(decrypted)
            if strength == "💪 Strong!":
                strong += 1
            elif strength == "👍 Medium":
                medium += 1
            else:
                weak += 1
    
    # Count unique websites
    sites = set(entry['site'].lower() for entry in data)
    
    print(f"📊 Your Password Vault Statistics")
    print(f"{'─' * 35}")
    print(f"🔐 Total passwords: {total}")
    print(f"🌐 Unique websites: {len(sites)}")
    print(f"\n📈 Password Strength Breakdown:")
    print(f"   🟢 Strong:  {strong} ({strong/total*100:.1f}%)")
    print(f"   🟡 Medium: {medium} ({medium/total*100:.1f}%)")
    print(f"   🔴 Weak:   {weak} ({weak/total*100:.1f}%)")
    
    # Show recently added
    print(f"\n🕒 Recently added (last 5):")
    sorted_data = sorted(data, key=lambda x: x.get('created', ''), reverse=True)
    for entry in sorted_data[:5]:
        print(f"   • {entry['site']} - {entry['username']}")
    
    input("\nPress Enter to continue...")

def change_master_password():
    """Change your master password (you'll need to remember the new one!)"""
    print_header("CHANGE MASTER PASSWORD")
    
    if not os.path.exists(MASTER_FILE):
        print("❌ No master password set.")
        input("\nPress Enter to continue...")
        return False
    
    # Verify current password first
    with open(MASTER_FILE, "r") as f:
        stored_hash = f.read()
    
    current = getpass("🔑 Enter current master password: ")
    if hash_password(current) != stored_hash:
        print("❌ Incorrect password!")
        input("\nPress Enter to continue...")
        return False
    
    print("\nSet your new master password:")
    while True:
        new_pass = getpass("🔑 New master password: ")
        confirm = getpass("🔑 Confirm new password: ")
        
        if new_pass == confirm:
            if len(new_pass) < 4:
                print("❌ Password must be at least 4 characters.\n")
                continue
            if not new_pass:
                print("❌ Password cannot be empty.\n")
                continue
            
            with open(MASTER_FILE, "w") as f:
                f.write(hash_password(new_pass))
            print("\n✅ Master password changed successfully!")
            print("💡 Don't forget your new password!")
            input("\nPress Enter to continue...")
            return True
        else:
            print("❌ Passwords don't match.\n")

def main():
    """Main program - where everything starts"""
    # Verify user is authorized
    if not verify_master_password():
        sys.exit(1)
    
    # Load encryption key and existing data
    key = load_key()
    data = load_data()
    
    # Main menu loop
    while True:
        print_header("MAIN MENU")
        print("1. 🔐 Add New Password")
        print("2. 👁️  View All Passwords")
        print("3. 🔍 Search Passwords")
        print("4. ✏️  Update Password")
        print("5. 🗑️  Delete Password")
        print("6. 💾 Export Backup")
        print("7. 📂 Import Backup")
        print("8. 📊 View Statistics")
        print("9. 🔑 Change Master Password")
        print("10. 🚪 Exit")
        print("=" * 50)
        
        choice = input("👉 Choose an option (1-10): ").strip()
        
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
            import_backup(data, key)
        elif choice == "8":
            view_stats(data, key)
        elif choice == "9":
            change_master_password()
        elif choice == "10":
            print_header("GOODBYE")
            print("Thanks for using Password Manager!")
            print("Remember: Keep your master password safe! 🔒")
            print("GitHub: https://github.com/yourusername/password-manager")
            time.sleep(2)
            clear_screen()
            break
        else:
            print("❌ Invalid option. Please choose 1-10.")
            time.sleep(1)

# Run the program
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Stay safe online!")
        sys.exit(0)
