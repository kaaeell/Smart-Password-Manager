# 🔐 Smart Password Manager (CLI)

A simple command-line password manager built with Python.

I built this project while learning Python to practice file handling and create something actually useful (instead of just small exercises).

---

## 🚀 Features

* 🔐 Master password login
* ➕ Add new passwords
* 📂 View saved passwords
* 🔍 Search passwords by website
* 🗑️ Delete saved passwords

---

## 🧰 Technologies Used

* Python
* JSON (for storing data locally)
* `getpass` (to hide password input in the terminal)

---

## ▶️ How to Run

1. Make sure you have Python installed
2. Clone this repository or download the files
3. Run the program:

```bash
python main.py
```

---

## 📁 Project Structure

```
main.py       # main application file
data.json     # stores saved passwords (created automatically)
```

---

## 📦 Data Storage

All passwords are stored locally in a file called `data.json`.

> ⚠️ This is a simple implementation for learning purposes.

---

## ⚠️ Security Note

Passwords are currently stored **in plain text**.

This is okay for learning, but **not safe for real-world usage**.
Encryption will be added in future versions.

---

## 🔥 Future Improvements

* 🔒 Encrypt stored passwords
* 🎲 Password generator
* 👁️ Show/hide password option
* 📋 Copy password to clipboard
* 🧑‍💻 Better CLI interface

---

## 💭 Why I Built This

I wanted to move beyond basic Python exercises and build something practical.
This project helped me understand:

* File handling
* Working with JSON
* Structuring a CLI application
* Writing cleaner, more readable code

---

## 📌 Version

**v2 — improved structure, cleaner code, better user experience**
