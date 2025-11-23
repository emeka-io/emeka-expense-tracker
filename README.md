# 💰 Emeka's Expense Tracker  
### A Modern Desktop Expense Manager with Dark/Light Mode, Analytics, Monthly Budgets & Reports  
Built with Python (Tkinter)

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success)
![UI](https://img.shields.io/badge/UI-Premium%20Desktop%20App-black)

---

## Overview  
**Emeka's Expense Tracker** is a **premium Python desktop application** designed to help users manage their monthly spending using a clean, modern UI.

It includes:
- Dark & Light mode  
- Sidebar navigation  
- Monthly budget management  
- Automatic warnings and alerts  
- Exportable financial reports  
- Persistent data storage (JSON)  
- Professional Tkinter interface design  

---

## Features  
### ✅ **Premium UI**
- Sidebar navigation  
- Modern dark theme (default)  
- Smooth light mode toggle  
- Rounded cards, clean typography  

### 💸 **Smart Expense Tools**
- Add, view, and manage expenses  
- Automatic total + monthly breakdown  
- Budget warnings (70% alert, 100% exceeded)  
- Recent expenses panel  

### 📊 **Reports**
- Export `.txt` reports  
- Summary breakdown (categories, total spent)  
- Clean formatting  

### 💾 **Data**
- Stored locally using JSON  
- Fast and lightweight  
- No database required (SQLite optional upgrade)

---

## 🗂️ Project Structure  

emeka-expense-tracker/
│
├── assets/ # icons, theme assets
│
├── data/
│ └── expenses.json # auto-generated on first run
│
├── src/
│ └── expense_tracker.py
│
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── CODE_OF_CONDUCT.md


---



## 🔧 Installation
### 1. Create Virtual Environment (optional)
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Mac/Linux

### 2. Install Requirements
This project uses only the Python Standard Library (Tkinter is built-in).
pip install -r requirements.txt

### 3. Run the App
python src/expense_tracker.py

## 🤝 Contributing
See CONTRIBUTING.md for guidelines.

## 📜 License
This project is licensed under the MIT License.
See LICENSE for details.

## ⭐ Support
If you like the project:

Star ⭐ the repo

Share it

Contribute improvements

Made with ❤️ by Emeka I.O

### **1. Clone the Repository**
```bash
git clone https://github.com/emeka-io/emekas-expense-tracker.git
cd emekas-expense-tracker
