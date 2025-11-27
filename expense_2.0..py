#  EMEKA EXPENSE TRACKER VERSIOM 2.0
import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DATA_FILE = "expenses_premium.json"


# Save / Load
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"expenses": [], "budget": 0.0}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"expenses": [], "budget": 0.0}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# Themes
class Theme:
    DARK = {
        "bg": "#0D1117",
        "panel": "#161B22",
        "card": "#1E242C",
        "fg": "#E6EDF3",
        "muted": "#9BA4B3",
        "accent": "#58A6FF",
        "border": "#30363D",
        "danger": "#F85149",
        "success": "#2EA043",
        "table_bg": "#0D1117",
        "row_alt": "#111720",
    }

    LIGHT = {
        "bg": "#FFFFFF",
        "panel": "#F6F8FA",
        "card": "#F2F4F7",
        "fg": "#1F2328",
        "muted": "#6C7177",
        "accent": "#0969DA",
        "border": "#D0D7DE",
        "danger": "#CF222E",
        "success": "#1A7F37",
        "table_bg": "#FFFFFF",
        "row_alt": "#F6F8FA",
    }


# App
class ExpenseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EMEKA's Smart Expense Tracker")
        self.geometry("1000x620")
        self.minsize(900, 560)

        self.data = load_data()
        self.current_theme = Theme.DARK

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self._build_layout()
        self._apply_theme()

        self.show_frame("dashboard")
        self.refresh_dashboard()


    # Theme Apply
    def _apply_theme(self):
        t = self.current_theme
        self.configure(bg=t["bg"])

        # Sidebar
        self.sidebar.configure(bg=t["panel"])
        for child in self.sidebar.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg=t["panel"], fg=t["fg"])
            if isinstance(child, tk.Button):
                child.configure(bg=t["panel"], fg=t["fg"], activebackground=t["card"])

        # Content
        self.content.configure(bg=t["bg"])
        for frame in self.frames.values():
            frame.configure(bg=t["bg"])
            for w in frame.winfo_children():
                self._style_widget(w, t)

        # Buttons
        self.style.configure(
            "TButton",
            background=t["panel"],
            foreground=t["fg"],
            bordercolor=t["border"],
            padding=6,
            focusthickness=0,
        )
        self.style.map("TButton",
                       background=[("active", t["card"])],
                       foreground=[("active", t["fg"])])

        # Tables
        self.style.configure("Treeview",
                             background=t["table_bg"],
                             foreground=t["fg"],
                             fieldbackground=t["table_bg"],
                             rowheight=24)
        self.style.configure("Treeview.Heading",
                             foreground=t["fg"],
                             background=t["panel"],
                             font=(None, 10, "bold"))

    def _style_widget(self, w, t):
        if isinstance(w, tk.Label):
            w.configure(bg=w.cget("bg") if w.cget("bg") != "SystemButtonFace" else t["bg"],
                        fg=t["fg"])
        elif isinstance(w, tk.Frame):
            w.configure(bg=w.cget("bg") if w.cget("bg") != "SystemButtonFace" else t["bg"])
        elif isinstance(w, tk.Entry):
            w.configure(bg=t["card"], fg=t["fg"], insertbackground=t["fg"])


    # Layout
    def _build_layout(self):
        self.sidebar = tk.Frame(self, width=220)
        self.sidebar.pack(side="left", fill="y")

        self.content = tk.Frame(self)
        self.content.pack(side="right", fill="both", expand=True)

        self._build_sidebar()
        self._build_pages()

    def _build_sidebar(self):
        t = self.current_theme

        tk.Label(self.sidebar, text="🧭  EMEKA's", font=("Segoe UI", 16, "bold"),
                 bg=t["panel"], fg=t["fg"]).pack(padx=16, pady=(18, 0))

        tk.Label(self.sidebar, text="Expense Tracker", font=("Segoe UI", 10),
                 bg=t["panel"], fg=t["muted"]).pack(padx=16)

        nav_frame = tk.Frame(self.sidebar, bg=t["panel"])
        nav_frame.pack(fill="x", pady=20)

        buttons = [
            ("dashboard", "📊 Dashboard"),
            ("add", "➕ Add Expense"),
            ("reports", "📁 Reports"),
            ("settings", "⚙️ Settings"),
        ]

        self.nav_buttons = {}
        for key, text in buttons:
            btn = tk.Button(nav_frame, text=text, anchor="w", relief="flat",
                            bg=t["panel"], fg=t["fg"], bd=0,
                            activebackground=t["card"],
                            command=lambda k=key: self.show_frame(k))
            btn.pack(fill="x", padx=12, pady=4)
            self.nav_buttons[key] = btn

        ttk.Button(self.sidebar, text="Toggle Theme", command=self.toggle_theme)\
            .pack(fill="x", padx=16, pady=(16, 10))

        # Quick Stats
        self.total_label = tk.Label(self.sidebar, text="Total: ₦0.00",
                                    font=("Segoe UI", 10, "bold"),
                                    bg=t["panel"], fg=t["fg"])
        self.total_label.pack(anchor="w", padx=16)

        self.budget_label = tk.Label(self.sidebar, text="Budget: ₦0.00",
                                     bg=t["panel"], fg=t["muted"])
        self.budget_label.pack(anchor="w", padx=16, pady=(4, 0))

    
    # Pages
    def _build_pages(self):
        self.frames = {}

        self.frames["dashboard"] = tk.Frame(self.content)
        self.frames["add"] = tk.Frame(self.content)
        self.frames["reports"] = tk.Frame(self.content)
        self.frames["settings"] = tk.Frame(self.content)

        for f in self.frames.values():
            f.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._page_dashboard(self.frames["dashboard"])
        self._page_add(self.frames["add"])
        self._page_reports(self.frames["reports"])
        self._page_settings(self.frames["settings"])

    
    # Dashboard Page
    def _page_dashboard(self, parent):
        t = self.current_theme

        cards = tk.Frame(parent, bg=t["bg"])
        cards.pack(fill="x", padx=20, pady=20)

        self.card_total = self._make_card(cards, "Total Spent")
        self.card_budget = self._make_card(cards, "Budget")
        self.card_remaining = self._make_card(cards, "Remaining")

        table_box = tk.Frame(parent, bg=t["card"])
        table_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        tk.Label(table_box, text="Recent Expenses", font=("Segoe UI", 12, "bold"),
                 bg=t["card"], fg=t["fg"]).pack(anchor="w", padx=12, pady=8)

        cols = ("date", "category", "description", "amount")
        self.tree = ttk.Treeview(table_box, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=150)
        self.tree.pack(fill="both", expand=True, padx=12, pady=12)

    def _make_card(self, parent, title):
        t = self.current_theme
        card = tk.Frame(parent, bg=t["card"], padx=12, pady=12)
        card.pack(side="left", expand=True, fill="x", padx=8)

        tk.Label(card, text=title, font=("Segoe UI", 10),
                 fg=t["muted"], bg=t["card"]).pack(anchor="w")

        value = tk.Label(card, text="₦0.00", font=("Segoe UI", 18, "bold"),
                         fg=t["fg"], bg=t["card"])
        value.pack(anchor="w", pady=(6, 0))

        return value

    def refresh_dashboard(self):
        total = sum(e["amount"] for e in self.data["expenses"])
        budget = float(self.data.get("budget", 0))
        remaining = budget - total

        self.card_total.config(text=f"₦{total:.2f}")
        self.card_budget.config(text=f"₦{budget:.2f}")
        self.card_remaining.config(text=f"₦{remaining:.2f}")

        self.total_label.config(text=f"Total: ₦{total:.2f}")
        self.budget_label.config(text=f"Budget: ₦{budget:.2f}")

        # Update table
        for row in self.tree.get_children():
            self.tree.delete(row)

        for e in reversed(self.data["expenses"][-50:]):
            self.tree.insert("", "end",
                             values=(e["date"], e["category"], e["description"],
                                     f"₦{e['amount']:.2f}"))

    
    # Add Page
    
    def _page_add(self, parent):
        t = self.current_theme

        frame = tk.Frame(parent, bg=t["bg"], padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Add New Expense", font=("Segoe UI", 14, "bold"),
                 bg=t["bg"], fg=t["fg"]).pack(anchor="w")

        form = tk.Frame(frame, bg=t["card"], padx=16, pady=16)
        form.pack(fill="x", pady=12)

        self.amount_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.desc_var = tk.StringVar()

        def add_row(text, var):
            tk.Label(form, text=text, bg=t["card"], fg=t["fg"]).pack(anchor="w")
            tk.Entry(form, textvariable=var).pack(fill="x", pady=6)

        add_row("Amount (₦)", self.amount_var)
        add_row("Category", self.category_var)
        add_row("Description", self.desc_var)

        ttk.Button(form, text="Add Expense", command=self.add_expense)\
            .pack(pady=(10, 0))

    def add_expense(self):
        try:
            amount = float(self.amount_var.get())
        except:
            messagebox.showerror("Error", "Amount must be a number")
            return

        category = self.category_var.get().strip().title()
        desc = self.desc_var.get().strip()

        if not category or not desc:
            messagebox.showerror("Error", "Category and description required")
            return

        entry = {
            "amount": amount,
            "category": category,
            "description": desc,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        self.data["expenses"].append(entry)
        save_data(self.data)
        self.refresh_dashboard()

        self.amount_var.set("")
        self.category_var.set("")
        self.desc_var.set("")

        messagebox.showinfo("Success", "Expense added.")

    
    # Reports
    
    def _page_reports(self, parent):
        t = self.current_theme

        tk.Label(parent, text="Reports", font=("Segoe UI", 14, "bold"),
                 bg=t["bg"], fg=t["fg"]).pack(anchor="w", padx=20, pady=(20, 8))

        ttk.Button(parent, text="Export (.txt)", command=self.export_report)\
            .pack(anchor="w", padx=20, pady=(0, 16))

        box = tk.Frame(parent, bg=t["card"], padx=12, pady=12)
        box.pack(fill="both", expand=True, padx=20)

        self.report_text = tk.Text(box, wrap="word", bg=t["card"], fg=t["fg"],
                                   bd=0, insertbackground=t["fg"])
        self.report_text.pack(fill="both", expand=True)

        self.refresh_reports()

    def refresh_reports(self):
        total = sum(e["amount"] for e in self.data["expenses"])
        by_cat = {}

        for e in self.data["expenses"]:
            by_cat[e["category"]] = by_cat.get(e["category"], 0) + e["amount"]

        lines = [
            f"Report generated: {datetime.now()}",
            "",
            f"Total Spent: ₦{total:.2f}",
            "",
            "By Category:",
        ]

        for c, a in sorted(by_cat.items(), key=lambda x: x[1], reverse=True):
            lines.append(f" - {c}: ₦{a:.2f}")

        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, "\n".join(lines))

    
    # Settings Page
    
    def _page_settings(self, parent):
        t = self.current_theme

        tk.Label(parent, text="Settings", font=("Segoe UI", 14, "bold"),
                 bg=t["bg"], fg=t["fg"]).pack(anchor="w", padx=20, pady=(20, 8))

        form = tk.Frame(parent, bg=t["card"], padx=16, pady=16)
        form.pack(fill="x", padx=20)

        tk.Label(form, text="Set Monthly Budget (₦)", bg=t["card"], fg=t["fg"])\
            .grid(row=0, column=0, sticky="w")

        self.budget_var = tk.StringVar(value=str(self.data.get("budget", 0)))
        tk.Entry(form, textvariable=self.budget_var).grid(row=0, column=1, padx=8)

        ttk.Button(form, text="Save Budget", command=self.save_budget)\
            .grid(row=0, column=2, padx=8)

        # Danger zone
        danger = tk.Frame(parent, bg=t["bg"])
        danger.pack(fill="x", padx=20, pady=(20, 0))

        tk.Label(danger, text="Danger Zone", font=("Segoe UI", 12, "bold"),
                 bg=t["bg"], fg=t["danger"]).pack(anchor="w")

        tk.Button(danger, text="Clear All Data", bg=t["danger"], fg="white",
                  command=self.clear_all_data).pack(anchor="w", pady=8)

    def save_budget(self):
        try:
            budget = float(self.budget_var.get())
        except:
            messagebox.showerror("Error", "Budget must be a number")
            return

        self.data["budget"] = budget
        save_data(self.data)
        self.refresh_dashboard()
        messagebox.showinfo("Success", "Budget saved")

    
    # Misc
    
    def clear_all_data(self):
        if messagebox.askyesno("Confirm", "Clear ALL data?"):
            self.data = {"expenses": [], "budget": 0}
            save_data(self.data)
            self.refresh_dashboard()
            self.refresh_reports()
            messagebox.showinfo("Done", "All data cleared.")

    def toggle_theme(self):
        self.current_theme = Theme.LIGHT if self.current_theme == Theme.DARK else Theme.DARK
        self._apply_theme()

    def show_frame(self, name):
        for k, frame in self.frames.items():
            frame.place_forget()

        self.frames[name].place(relx=0, rely=0, relwidth=1, relheight=1)

        for k, btn in self.nav_buttons.items():
            btn.config(relief="sunken" if k == name else "flat")

        if name == "dashboard":
            self.refresh_dashboard()
        elif name == "reports":
            self.refresh_reports()

    def export_report(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not path:
            return

        total = sum(e["amount"] for e in self.data["expenses"])

        with open(path, "w", encoding="utf-8") as f:
            f.write("Expense Report\n")
            f.write(f"Generated: {datetime.now()}\n\n")
            f.write(f"Total Spent: ₦{total:.2f}\n\n")
            f.write("Details:\n")
            for e in self.data["expenses"]:
                f.write(f"{e['date']} | {e['category']} | {e['description']} | ₦{e['amount']:.2f}\n")

        messagebox.showinfo("Saved", "Report exported successfully.")



# Run
if __name__ == "__main__":
    ExpenseApp().mainloop()
