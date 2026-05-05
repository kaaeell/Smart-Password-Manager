import json
import os
import hashlib
import random
import string
import sys
import csv
from datetime import datetime
from getpass import getpass
from cryptography.fernet import Fernet, InvalidToken

DATA_FILE = "data.json"
MASTER_FILE = "master.hash"
KEY_FILE = "secret.key"

class PasswordManager:
    def __init__(self):
        self.data = []
        self.key = None
        self.failed_attempts = 0
        self.lockout_time = None
        
    def _clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _print_header(self, title):
        self._clear_screen()
        print("=" * 50)
        print(f"PASSWORD MANAGER - {title}")
        print("=" * 50)
        print()
    
    def _hash_password(self, password):
        salt = "fixed_salt_for_demo"  # In real app, use random salt per user
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def _load_key(self):
        if not os.path.exists(KEY_FILE):
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as f:
                f.write(key)
        with open(KEY_FILE, "rb") as f:
            return f.read()
    
    def _encrypt(self, text):
        return Fernet(self.key).encrypt(text.encode()).decode()
    
    def _decrypt(self, encrypted_text):
        try:
            return Fernet(self.key).decrypt(encrypted_text.encode()).decode()
        except (InvalidToken, Exception):
            return "[DECRYPTION_FAILED]"
    
    def _backup_data(self):
        if os.path.exists(DATA_FILE):
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(DATA_FILE, 'r') as original:
                    with open(backup_name, 'w') as backup:
                        backup.write(original.read())
                return True
            except:
                return False
        return False
    
    def _setup_master_password(self):
        self._print_header("FIRST TIME SETUP")
        print("This master password protects all your stored credentials.")
        print("WARNING: If you lose it, your data cannot be recovered.\n")
        
        while True:
            password = getpass("Create master password (min 8 characters): ")
            confirm = getpass("Confirm master password: ")
            
            if len(password) < 8:
                print("Password must be at least 8 characters long.\n")
            elif not any(c.isupper() for c in password):
                print("Password must contain at least one uppercase letter.\n")
            elif not any(c.islower() for c in password):
                print("Password must contain at least one lowercase letter.\n")
            elif not any(c.isdigit() for c in password):
                print("Password must contain at least one number.\n")
            elif password != confirm:
                print("Passwords do not match.\n")
            else:
                with open(MASTER_FILE, "w") as f:
                    f.write(self._hash_password(password))
                print("\nMaster password created successfully!")
                input("\nPress Enter to continue...")
                return True
    
    def _verify_master_password(self):
        if not os.path.exists(MASTER_FILE):
            return self._setup_master_password()
        
        self._print_header("LOGIN")
        
        with open(MASTER_FILE, "r") as f:
            stored_hash = f.read()
        
        for attempt in range(3):
            password = getpass("Enter master password: ")
            if self._hash_password(password) == stored_hash:
                self.failed_attempts = 0
                return True
            self.failed_attempts += 1
            print(f"Incorrect password. {2 - attempt} attempts remaining.\n")
        
        print("Too many failed attempts. Exiting.")
        return False
    
    def _load_data(self):
        if not os.path.exists(DATA_FILE):
            self.data = []
            return
        
        try:
            with open(DATA_FILE, "r") as f:
                content = f.read().strip()
                self.data = json.loads(content) if content else []
        except (json.JSONDecodeError, FileNotFoundError):
            self.data = []
            print("Warning: Data file was corrupted. Starting fresh.")
    
    def _save_data(self):
        try:
            self._backup_data()  # Create backup before saving
            with open(DATA_FILE, "w") as f:
                json.dump(self.data, f, indent=2)
            return True
        except IOError:
            print("Error saving data!")
            return False
    
    def _generate_password(self, length=14):
        if length < 8:
            length = 8
        if length > 32:
            length = 32
        
        lowercase = random.choice(string.ascii_lowercase)
        uppercase = random.choice(string.ascii_uppercase)
        digit = random.choice(string.digits)
        special = random.choice("!@#$%^&*")
        
        remaining_chars = ''.join(random.choices(
            string.ascii_letters + string.digits + "!@#$%^&*", 
            k=length - 4
        ))
        
        password_list = list(lowercase + uppercase + digit + special + remaining_chars)
        random.shuffle(password_list)
        
        return ''.join(password_list)
    
    def _check_password_strength(self, password):
        criteria = {
            'length': len(password) >= 12,
            'case': any(c.islower() for c in password) and any(c.isupper() for c in password),
            'digit': any(c.isdigit() for c in password),
            'special': any(c in "!@#$%^&*" for c in password)
        }
        
        score = sum(criteria.values())
        
        if score == 4:
            return "Strong"
        elif score == 3:
            return "Medium"
        else:
            return "Weak"
    
    def add_entry(self):
        self._print_header("ADD NEW ENTRY")
        
        site = input("Website/Service: ").strip()
        if not site:
            print("Website name is required.")
            input("\nPress Enter...")
            return
        
        username = input("Username/Email: ").strip()
        if not username:
            print("Username is required.")
            input("\nPress Enter...")
            return
        
        for entry in self.data:
            if (entry['site'].lower() == site.lower() and 
                entry['username'].lower() == username.lower()):
                print("Entry already exists!")
                input("\nPress Enter...")
                return
        
        print("\nPassword Options:")
        print("1. Generate strong password")
        print("2. Enter my own password")
        
        choice = input("\nChoose (1/2): ").strip()
        
        password = ""
        if choice == "1":
            length_input = input("Password length (default 14, min 8, max 32): ").strip()
            length = int(length_input) if length_input.isdigit() else 14
            length = max(8, min(length, 32))
            password = self._generate_password(length)
            print(f"\nGenerated Password: {password}")
            print(f"Strength: {self._check_password_strength(password)}")
            
            if input("\nSave this password? (y/n): ").lower() != 'y':
                return
        
        elif choice == "2":
            password = getpass("Enter your password: ")
            if not password:
                return
            if len(password) < 8:
                print("Warning: Short passwords are vulnerable!")
            print(f"Strength: {self._check_password_strength(password)}")
            
            if input("Save this password? (y/n): ").lower() != 'y':
                return
        else:
            print("Invalid choice.")
            input("\nPress Enter...")
            return
        
        notes = input("Notes (optional): ").strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        category = input("Category (Personal/Work/Finance/Social/Other): ").strip()
        if not category:
            category = "Other"
        
        self.data.append({
            "site": site,
            "username": username,
            "password": self._encrypt(password),
            "notes": notes,
            "category": category,
            "created": timestamp,
            "updated": timestamp
        })
        
        if self._save_data():
            print("\nEntry saved successfully!")
        input("\nPress Enter...")
    
    def view_entries(self):
        self._print_header("ALL ENTRIES")
        
        if not self.data:
            print("No entries found.")
            input("\nPress Enter...")
            return
        
        print("Filter options:")
        print("1. Show all")
        print("2. Filter by category")
        filter_choice = input("\nChoose (1/2): ").strip()
        
        filtered_data = self.data
        if filter_choice == "2":
            categories = list(set(entry.get('category', 'Other') for entry in self.data))
            print("\nAvailable categories:")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat}")
            cat_choice = input("\nSelect category: ").strip()
            if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
                selected_cat = categories[int(cat_choice)-1]
                filtered_data = [e for e in self.data if e.get('category', 'Other') == selected_cat]
        
        show_passwords = input("\nShow passwords? (y/n): ").lower() == 'y'
        
        for idx, entry in enumerate(filtered_data, 1):
            print(f"\n{idx}. [{entry.get('category', 'Other')}] {entry['site']}")
            print(f"   Username: {entry['username']}")
            
            if show_passwords:
                decrypted = self._decrypt(entry['password'])
                print(f"   Password: {decrypted}")
                if decrypted != "[DECRYPTION_FAILED]":
                    print(f"   Strength: {self._check_password_strength(decrypted)}")
            else:
                print(f"   Password: {'*' * 10}")
            
            if entry.get('notes'):
                notes_preview = entry['notes'][:50] + ('...' if len(entry['notes']) > 50 else '')
                print(f"   Notes: {notes_preview}")
        
        print(f"\nTotal: {len(filtered_data)} entries")
        input("\nPress Enter...")
    
    def search_entries(self):
        self._print_header("SEARCH")
        
        if not self.data:
            print("No entries to search.")
            input("\nPress Enter...")
            return
        
        search_term = input("Search query: ").strip().lower()
        if not search_term:
            return
        
        results = [
            entry for entry in self.data 
            if search_term in entry['site'].lower() or 
               search_term in entry['username'].lower() or
               search_term in entry.get('notes', '').lower()
        ]
        
        if not results:
            print(f"No results found for '{search_term}'.")
            input("\nPress Enter...")
            return
        
        show_passwords = input("Show passwords? (y/n): ").lower() == 'y'
        
        print(f"\nFound {len(results)} result(s):\n")
        for entry in results:
            print(f"[{entry.get('category', 'Other')}] {entry['site']}")
            print(f"   Username: {entry['username']}")
            if show_passwords:
                print(f"   Password: {self._decrypt(entry['password'])}")
            print()
        
        input("\nPress Enter...")
    
    def update_entry(self):
        self._print_header("UPDATE ENTRY")
        
        if not self.data:
            print("No entries to update.")
            input("\nPress Enter...")
            return
        
        for idx, entry in enumerate(self.data, 1):
            print(f"{idx}. [{entry.get('category', 'Other')}] {entry['site']} - {entry['username']}")
        
        try:
            choice = int(input("\nSelect entry number to update: "))
            if not 1 <= choice <= len(self.data):
                print("Invalid selection.")
                input("\nPress Enter...")
                return
            
            entry = self.data[choice - 1]
            print(f"\nEditing: {entry['site']}")
            print("(Press Enter to keep current value)\n")
            
            new_username = input(f"Username [{entry['username']}]: ").strip()
            if new_username:
                entry['username'] = new_username
            
            new_category = input(f"Category [{entry.get('category', 'Other')}]: ").strip()
            if new_category:
                entry['category'] = new_category
            
            if input("Update password? (y/n): ").lower() == 'y':
                print("\n1. Generate new password")
                print("2. Enter my own password")
                pw_choice = input("Choose (1/2): ").strip()
                
                if pw_choice == "1":
                    length_input = input("Password length (14): ").strip()
                    length = int(length_input) if length_input.isdigit() else 14
                    length = max(8, min(length, 32))
                    new_password = self._generate_password(length)
                    print(f"\nNew Password: {new_password}")
                    if input("Save this password? (y/n): ").lower() == 'y':
                        entry['password'] = self._encrypt(new_password)
                
                elif pw_choice == "2":
                    new_password = getpass("Enter new password: ")
                    if new_password:
                        if len(new_password) < 8:
                            print("Warning: Short password!")
                        entry['password'] = self._encrypt(new_password)
            
            new_notes = input(f"Notes [{entry.get('notes', '')}]: ").strip()
            if new_notes:
                entry['notes'] = new_notes
            
            entry['updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if self._save_data():
                print("\nEntry updated successfully!")
        
        except ValueError:
            print("Please enter a valid number.")
        
        input("\nPress Enter...")
    
    def delete_entry(self):
        self._print_header("DELETE ENTRY")
        
        if not self.data:
            print("No entries to delete.")
            input("\nPress Enter...")
            return
        
        for idx, entry in enumerate(self.data, 1):
            print(f"{idx}. {entry['site']} - {entry['username']}")
        
        try:
            choice = int(input("\nSelect entry number to delete: "))
            if not 1 <= choice <= len(self.data):
                print("Invalid selection.")
                input("\nPress Enter...")
                return
            
            entry = self.data[choice - 1]
            confirm = input(f"Delete '{entry['site']}'? Type 'yes' to confirm: ")
            
            if confirm.lower() == 'yes':
                self.data.pop(choice - 1)
                if self._save_data():
                    print("\nEntry deleted successfully!")
            else:
                print("Deletion cancelled.")
        
        except ValueError:
            print("Please enter a valid number.")
        
        input("\nPress Enter...")
    
    def export_data(self):
        self._print_header("EXPORT DATA")
        
        if not self.data:
            print("No data to export.")
            input("\nPress Enter...")
            return
        
        print("Export Format:")
        print("1. TXT (Human readable)")
        print("2. CSV (Compatible with Excel)")
        
        choice = input("\nChoose (1/2): ").strip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            if choice == "1":
                filename = f"password_export_{timestamp}.txt"
                with open(filename, "w", encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write(f"PASSWORD MANAGER EXPORT\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    
                    for entry in self.data:
                        f.write(f"Site: {entry['site']}\n")
                        f.write(f"Category: {entry.get('category', 'Other')}\n")
                        f.write(f"Username: {entry['username']}\n")
                        f.write(f"Password: {self._decrypt(entry['password'])}\n")
                        if entry.get('notes'):
                            f.write(f"Notes: {entry['notes']}\n")
                        f.write(f"Created: {entry['created']}\n")
                        f.write(f"Last Updated: {entry['updated']}\n")
                        f.write("-" * 40 + "\n\n")
                
                print(f"\nData exported to: {filename}")
            
            elif choice == "2":
                filename = f"password_export_{timestamp}.csv"
                with open(filename, "w", newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Category", "Site", "Username", "Password", "Notes", "Created", "Updated"])
                    
                    for entry in self.data:
                        writer.writerow([
                            entry.get('category', 'Other'),
                            entry['site'],
                            entry['username'],
                            self._decrypt(entry['password']),
                            entry.get('notes', ''),
                            entry['created'],
                            entry['updated']
                        ])
                
                print(f"\nData exported to: {filename}")
            
            else:
                print("Invalid choice.")
        
        except Exception as e:
            print(f"Export failed: {e}")
        
        input("\nPress Enter...")
    
    def show_statistics(self):
        self._print_header("STATISTICS")
        
        if not self.data:
            print("No data to analyze.")
            input("\nPress Enter...")
            return
        
        strong = medium = weak = 0
        category_count = {}
        
        for entry in self.data:
            cat = entry.get('category', 'Other')
            category_count[cat] = category_count.get(cat, 0) + 1
            
            decrypted = self._decrypt(entry['password'])
            if decrypted != "[DECRYPTION_FAILED]":
                criteria = {
                    'length': len(decrypted) >= 12,
                    'case': any(c.islower() for c in decrypted) and any(c.isupper() for c in decrypted),
                    'digit': any(c.isdigit() for c in decrypted),
                    'special': any(c in "!@#$%^&*" for c in decrypted)
                }
                score = sum(criteria.values())
                
                if score == 4:
                    strong += 1
                elif score == 3:
                    medium += 1
                else:
                    weak += 1
        
        unique_sites = len(set(entry['site'].lower() for entry in self.data))
        
        print(f"Total Passwords: {len(self.data)}")
        print(f"Unique Sites: {unique_sites}")
        print(f"Oldest Entry: {min(entry['created'] for entry in self.data)}")
        print(f"Latest Update: {max(entry['updated'] for entry in self.data)}")
        
        print("\nCategories:")
        for cat, count in sorted(category_count.items()):
            print(f"   {cat}: {count}")
        
        print(f"\nPassword Strength Distribution:")
        print(f"   Strong: {strong} ({strong*100//len(self.data) if self.data else 0}%)")
        print(f"   Medium: {medium} ({medium*100//len(self.data) if self.data else 0}%)")
        print(f"   Weak: {weak} ({weak*100//len(self.data) if self.data else 0}%)")
        
        if weak > 0:
            print(f"\nWARNING: {weak} weak password(s) detected!")
            print("   Consider updating them for better security.")
        
        input("\nPress Enter...")
    
    def change_master_password(self):
        self._print_header("CHANGE MASTER PASSWORD")
        
        if not os.path.exists(MASTER_FILE):
            print("No master password configured.")
            input("\nPress Enter...")
            return
        
        with open(MASTER_FILE, "r") as f:
            stored_hash = f.read()
        
        current = getpass("Enter current master password: ")
        if self._hash_password(current) != stored_hash:
            print("Incorrect current password.")
            input("\nPress Enter...")
            return
        
        print("\nWARNING: Changing master password will keep your data encrypted")
        print("   with the new password. You must remember this new password!\n")
        
        while True:
            new_password = getpass("New master password (min 8 chars): ")
            confirm = getpass("Confirm new master password: ")
            
            if len(new_password) < 8:
                print("Password must be at least 8 characters.\n")
            elif not any(c.isupper() for c in new_password):
                print("Password must contain at least one uppercase letter.\n")
            elif not any(c.islower() for c in new_password):
                print("Password must contain at least one lowercase letter.\n")
            elif not any(c.isdigit() for c in new_password):
                print("Password must contain at least one number.\n")
            elif new_password != confirm:
                print("Passwords do not match.\n")
            else:
                with open(MASTER_FILE, "w") as f:
                    f.write(self._hash_password(new_password))
                print("\nMaster password changed successfully!")
                break
        
        input("\nPress Enter...")
    
    def exit_program(self):
        self._print_header("GOODBYE")
        print("All changes saved.")
        print("Remember: Keep your master password safe!")
        input("\nPress Enter...")
        self._clear_screen()
        sys.exit(0)
    
    def run(self):
        if not self._verify_master_password():
            sys.exit(1)
        
        self.key = self._load_key()
        self._load_data()
        
        while True:
            self._print_header("MAIN MENU")
            print("1. Add New Entry")
            print("2. View All Entries")
            print("3. Search Entries")
            print("4. Update Entry")
            print("5. Delete Entry")
            print("6. Export Data")
            print("7. View Statistics")
            print("8. Change Master Password")
            print("9. Exit")
            print("=" * 50)
            
            choice = input("Select option (1-9): ").strip()
            
            if choice == '1':
                self.add_entry()
            elif choice == '2':
                self.view_entries()
            elif choice == '3':
                self.search_entries()
            elif choice == '4':
                self.update_entry()
            elif choice == '5':
                self.delete_entry()
            elif choice == '6':
                self.export_data()
            elif choice == '7':
                self.show_statistics()
            elif choice == '8':
                self.change_master_password()
            elif choice == '9':
                self.exit_program()
            else:
                print("Invalid option. Please choose 1-9.")
                input("\nPress Enter...")

def main():
    try:
        manager = PasswordManager()
        manager.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        print("Please check your data files and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
