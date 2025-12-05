#  EMEKA EXPENSE 3.0

import json
import os
from datetime import datetime
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from collections import defaultdict
import math

# Matplotlib for embedded charts
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DATA_FILE = "expenses_modern.json"


# ---------- Storage Layer ----------
class Storage:
    def __init__(self, filename=DATA_FILE):
        self.filename = filename
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.filename):
            self.save({"expenses": [], "budget": 0.0})

    def load(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"expenses": [], "budget": 0.0}

    def save(self, data):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# ---------- Theme Definitions ----------
class Theme:
    DARK = {
        "bg": "#0F1720",
        "panel": "#111827",
        "card": "#0B1220",
        "fg": "#E6EEF6",
        "muted": "#9AA6B2",
        "accent": "#60A5FA",
        "border": "#1F2937",
        "danger": "#F87171",
        "success": "#34D399",
        "table_bg": "#071021",
        "row_alt": "#0A1520",
        "entry_bg": "#0D1620",
    }

    LIGHT = {
        "bg": "#F7FAFC",
        "panel": "#FFFFFF",
        "card": "#FAFBFF",
        "fg": "#0B1220",
        "muted": "#54606E",
        "accent": "#2563EB",
        "border": "#E6EEF6",
        "danger": "#DC2626",
        "success": "#059669",
        "table_bg": "#FFFFFF",
        "row_alt": "#F3F6F9",
        "entry_bg": "#FFFFFF",
    }


# ---------- Main App ----------
class ExpenseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EMEKA — Smart Expense Tracker")
        self.geometry("1100x680")
        self.minsize(980, 600)

        # Data
        self.storage = Storage()
        self.data = self.storage.load()
        if "expenses" not in self.data:
            self.data = {"expenses": [], "budget": 0.0}

        # UI state
        self.theme = Theme.DARK
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # UI variables
        self.search_var = tk.StringVar()
        self.category_filter_var = tk.StringVar(value="All")
        self.budget_var = tk.StringVar(value=str(self.data.get("budget", 0.0)))

        # Preset categories
        self.default_categories = ["Food", "Transport", "Bills", "Shopping", "Health", "Entertainment", "Other"]

        # Build UI
        self._build_ui()
        self._apply_theme()
        self.show_frame("dashboard")
        self.refresh_all()

    # ---------------- UI BUILD ----------------
    def _build_ui(self):
        # Root layout: sidebar + content
        self.sidebar = tk.Frame(self, width=240)
        self.sidebar.pack(side="left", fill="y")
        self.content = tk.Frame(self)
        self.content.pack(side="right", fill="both", expand=True)

        self._build_sidebar()
        self.frames = {}
        self._build_pages()

    def _build_sidebar(self):
        t = self.theme
        padx = 14
        # Branding
        lbl_title = tk.Label(self.sidebar, text="🧭 EMEKA", font=("Segoe UI", 16, "bold"))
        lbl_sub = tk.Label(self.sidebar, text="Expense Tracker", font=("Segoe UI", 10))
        lbl_title.pack(padx=padx, pady=(18, 2), anchor="w")
        lbl_sub.pack(padx=padx, anchor="w")

        # Navigation
        nav_frame = tk.Frame(self.sidebar)
        nav_frame.pack(padx=padx, pady=16, fill="x")
        btns = [
            ("dashboard", "📊 Dashboard"),
            ("add", "➕ Add Expense"),
            ("reports", "📈 Reports"),
            ("settings", "⚙️ Settings"),
        ]
        self.navbuttons = {}
        for key, text in btns:
            b = tk.Button(nav_frame, text=text, anchor="w", relief="flat", padx=8,
                          command=lambda k=key: self.show_frame(k))
            b.pack(fill="x", pady=4)
            self.navbuttons[key] = b

        # Theme toggle
        ttk.Button(self.sidebar, text="Toggle Theme", command=self.toggle_theme).pack(fill="x", padx=padx, pady=(12, 6))

        # Quick stats
        self.total_lbl = tk.Label(self.sidebar, text="Total: ₦0.00", font=("Segoe UI", 10, "bold"))
        self.budget_lbl = tk.Label(self.sidebar, text="Budget: ₦0.00")
        self.total_lbl.pack(padx=padx, pady=(10, 0), anchor="w")
        self.budget_lbl.pack(padx=padx, pady=(2, 6), anchor="w")

        # Small search
        tk.Label(self.sidebar, text="Search", font=("Segoe UI", 9)).pack(padx=padx, anchor="w", pady=(8, 0))
        s = ttk.Entry(self.sidebar, textvariable=self.search_var)
        s.pack(fill="x", padx=padx, pady=6)
        self.search_var.trace_add("write", lambda *a: self.refresh_dashboard())

        # Category filter
        tk.Label(self.sidebar, text="Category", font=("Segoe UI", 9)).pack(padx=padx, anchor="w", pady=(8, 0))
        cats = ["All"] + self.default_categories
        self.cat_combo = ttk.Combobox(self.sidebar, values=cats, state="readonly", textvariable=self.category_filter_var)
        self.cat_combo.pack(fill="x", padx=padx, pady=6)
        self.cat_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_dashboard())

    def _build_pages(self):
        # Create frames
        for name in ("dashboard", "add", "reports", "settings"):
            frame = tk.Frame(self.content)
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.frames[name] = frame

        self._page_dashboard(self.frames["dashboard"])
        self._page_add(self.frames["add"])
        self._page_reports(self.frames["reports"])
        self._page_settings(self.frames["settings"])

    # ---------------- DASHBOARD ----------------
    def _page_dashboard(self, parent):
        t = self.theme
        pad = 18
        header = tk.Frame(parent)
        header.pack(fill="x", padx=pad, pady=(18, 8))
        tk.Label(header, text="Dashboard", font=("Segoe UI", 16, "bold")).pack(side="left")
        ttk.Button(header, text="Refresh", command=self.refresh_all).pack(side="right")

        # Cards
        cards = tk.Frame(parent)
        cards.pack(fill="x", padx=pad)
        self.card_total = self._make_card(cards, "Total Spent")
        self.card_budget = self._make_card(cards, "Budget")
        self.card_remaining = self._make_card(cards, "Remaining")

        # Table area
        table_box = tk.Frame(parent)
        table_box.pack(fill="both", expand=True, padx=pad, pady=(12, 18))

        tk.Label(table_box, text="Recent Expenses", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        cols = ("date", "category", "description", "amount")
        self.tree = ttk.Treeview(table_box, columns=cols, show="headings", selectmode="browse", height=12)
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
            if c == "description":
                self.tree.column(c, width=420, anchor="w")
            elif c == "amount":
                self.tree.column(c, width=120, anchor="e")
            else:
                self.tree.column(c, width=140)
        self.tree.pack(fill="both", expand=True, pady=(8, 0))

        # Actions for selected
        actions = tk.Frame(table_box)
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="Edit Selected", command=self.edit_selected).pack(side="left", padx=6)
        ttk.Button(actions, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=6)
        ttk.Button(actions, text="Export CSV", command=self.export_csv).pack(side="right", padx=6)

    def _make_card(self, parent, title):
        card = tk.Frame(parent, bd=0, relief="ridge", padx=12, pady=12)
        card.pack(side="left", expand=True, fill="x", padx=8)
        tk.Label(card, text=title, font=("Segoe UI", 10)).pack(anchor="w")
        val = tk.Label(card, text="₦0.00", font=("Segoe UI", 18, "bold"))
        val.pack(anchor="w", pady=(6, 0))
        return val

    def refresh_dashboard(self):
        # Filtered list based on search & category
        q = self.search_var.get().strip().lower()
        cat_filter = self.category_filter_var.get()
        expenses = self.data.get("expenses", [])
        filtered = []
        for e in reversed(expenses):
            matches_q = q == "" or q in e.get("description", "").lower() or q in e.get("category", "").lower()
            matches_cat = (cat_filter == "All") or (e.get("category", "") == cat_filter)
            if matches_q and matches_cat:
                filtered.append(e)

        total = sum(e["amount"] for e in expenses)
        budget = float(self.data.get("budget", 0.0))
        remaining = budget - total

        self.card_total.config(text=f"₦{total:,.2f}")
        self.card_budget.config(text=f"₦{budget:,.2f}")
        self.card_remaining.config(text=f"₦{remaining:,.2f}")

        self.total_lbl.config(text=f"Total: ₦{total:,.2f}")
        self.budget_lbl.config(text=f"Budget: ₦{budget:,.2f}")

        # Update tree
        for row in self.tree.get_children():
            self.tree.delete(row)
        for e in filtered[:200]:
            self.tree.insert("", "end", values=(e["date"], e["category"], e["description"], f"₦{e['amount']:,.2f}"))

    # ---------------- ADD / EDIT ----------------
    def _page_add(self, parent):
        self.add_frame = parent
        pad = 20
        header = tk.Frame(parent)
        header.pack(fill="x", padx=pad, pady=(18, 8))
        tk.Label(header, text="Add / Edit Expense", font=("Segoe UI", 16, "bold")).pack(side="left")
        self.add_form = tk.Frame(parent, bd=0)
        self.add_form.pack(fill="x", padx=pad, pady=12)

        # Form fields
        self.amount_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.edit_index = None  # None when adding, otherwise index in list

        form = tk.Frame(self.add_form)
        form.pack(fill="x")

        # Amount
        tk.Label(form, text="Amount (₦)").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.amount_var).grid(row=0, column=1, sticky="we", padx=6, pady=6)
        # Category (combo with presets)
        tk.Label(form, text="Category").grid(row=1, column=0, sticky="w")
        cats = self.default_categories + ["Custom..."]
        self.cat_combo_add = ttk.Combobox(form, values=cats, textvariable=self.category_var, state="readonly")
        self.cat_combo_add.grid(row=1, column=1, sticky="we", padx=6, pady=6)
        self.cat_combo_add.bind("<<ComboboxSelected>>", self._cat_preset_selected)
        # Description
        tk.Label(form, text="Description").grid(row=2, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.desc_var).grid(row=2, column=1, sticky="we", padx=6, pady=6)

        # Buttons
        buttons = tk.Frame(self.add_form)
        buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(buttons, text="Save Expense", command=self.save_expense).pack(side="left")
        ttk.Button(buttons, text="Clear", command=self.clear_add_form).pack(side="left", padx=(8, 0))

        # Make columns expand nicely
        form.columnconfigure(1, weight=1)

    def _cat_preset_selected(self, event):
        val = self.category_var.get()
        if val == "Custom...":
            # open a small dialog to type custom category
            custom = tk.simpledialog.askstring("Custom Category", "Enter category name:")
            if custom:
                custom = custom.strip().title()
                if custom:
                    self.category_var.set(custom)
                    if custom not in self.default_categories:
                        self.default_categories.append(custom)
                        # update filters
                        self.cat_combo.config(values=["All"] + self.default_categories)
                        self.cat_combo_add.config(values=self.default_categories + ["Custom..."])

    def save_expense(self):
        # Validate amount
        amt_str = self.amount_var.get().strip()
        try:
            # allow comma separators
            amt = float(amt_str.replace(",", ""))
        except Exception:
            messagebox.showerror("Invalid", "Amount must be a number (e.g., 1200.50)")
            return

        cat = self.category_var.get().strip() or "Other"
        desc = self.desc_var.get().strip() or "-"

        entry = {
            "amount": round(float(amt), 2),
            "category": cat.title(),
            "description": desc,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        if self.edit_index is None:
            # append
            self.data.setdefault("expenses", []).append(entry)
            messagebox.showinfo("Added", "Expense added successfully.")
        else:
            # editing: replace the item
            idx = self.edit_index
            try:
                self.data["expenses"][idx] = entry
                messagebox.showinfo("Updated", "Expense updated.")
            except Exception:
                messagebox.showerror("Error", "Could not update (index error).")
            self.edit_index = None

        self.storage.save(self.data)
        self.clear_add_form()
        self.refresh_all()
        # auto switch to dashboard for quick feedback
        self.show_frame("dashboard")

    def clear_add_form(self):
        self.amount_var.set("")
        self.category_var.set("")
        self.desc_var.set("")
        self.edit_index = None

    def edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select an expense to edit.")
            return
        vals = self.tree.item(sel[0])["values"]
        # Find the expense in dataset by matching date & amount & category & description (first match)
        target_date, target_cat, target_desc, target_amt = vals
        # strip currency symbol
        target_amt_val = float(str(target_amt).replace("₦", "").replace(",", ""))
        idx = None
        for i, e in enumerate(self.data.get("expenses", [])):
            try:
                if e["date"] == target_date and e["category"] == target_cat and e["description"] == target_desc and math.isclose(e["amount"], target_amt_val, rel_tol=1e-6):
                    idx = i
                    break
            except Exception:
                continue
        if idx is None:
            messagebox.showerror("Not found", "Could not locate the selected expense in storage.")
            return
        # populate add form
        e = self.data["expenses"][idx]
        self.amount_var.set(f"{e['amount']:.2f}")
        self.category_var.set(e["category"])
        self.desc_var.set(e["description"])
        self.edit_index = idx
        self.show_frame("add")

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select an expense to delete.")
            return
        if not messagebox.askyesno("Confirm", "Delete selected expense?"):
            return
        vals = self.tree.item(sel[0])["values"]
        target_date, target_cat, target_desc, target_amt = vals
        target_amt_val = float(str(target_amt).replace("₦", "").replace(",", ""))
        idx = None
        for i, e in enumerate(self.data.get("expenses", [])):
            try:
                if e["date"] == target_date and e["category"] == target_cat and e["description"] == target_desc and math.isclose(e["amount"], target_amt_val, rel_tol=1e-6):
                    idx = i
                    break
            except Exception:
                continue
        if idx is None:
            messagebox.showerror("Not found", "Could not locate the selected expense in storage.")
            return
        self.data["expenses"].pop(idx)
        self.storage.save(self.data)
        self.refresh_all()
        messagebox.showinfo("Deleted", "Expense removed.")

    # ---------------- REPORTS ----------------
    def _page_reports(self, parent):
        pad = 18
        header = tk.Frame(parent)
        header.pack(fill="x", padx=pad, pady=(18, 8))
        tk.Label(header, text="Reports", font=("Segoe UI", 16, "bold")).pack(side="left")
        ttk.Button(header, text="Refresh Chart", command=self.refresh_reports).pack(side="right")

        # Chart area
        chart_box = tk.Frame(parent)
        chart_box.pack(fill="both", expand=True, padx=pad, pady=(6, 18))

        self.fig = Figure(figsize=(6, 3.5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_box)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Report text area
        text_box = tk.Frame(parent)
        text_box.pack(fill="x", padx=pad, pady=(0, 12))
        ttk.Button(text_box, text="Export Report (.txt)", command=self.export_report_txt).pack(side="right")

    def refresh_reports(self):
        # Build monthly totals for the last 12 months
        now = datetime.now()
        monthly = defaultdict(float)
        for e in self.data.get("expenses", []):
            try:
                dt = datetime.strptime(e["date"], "%Y-%m-%d %H:%M:%S")
            except Exception:
                continue
            key = dt.strftime("%Y-%m")
            monthly[key] += e["amount"]

        # Get sorted last 12 months
        months = []
        vals = []
        for i in range(11, -1, -1):
            m = (now.month - i - 1) % 12 + 1
            y = now.year + ((now.month - i - 1) // 12)
            key = f"{y:04d}-{m:02d}"
            months.append(key)
            vals.append(monthly.get(key, 0.0))

        # Plot
        self.ax.clear()
        bars = self.ax.bar(months, vals)
        self.ax.set_title("Monthly Spending (last 12 months)")
        self.ax.set_ylabel("₦")
        self.ax.tick_params(axis='x', rotation=45)
        # neat labels for bars
        for rect, v in zip(bars, vals):
            height = rect.get_height()
            if height > 0:
                self.ax.annotate(f"₦{height:,.0f}", xy=(rect.get_x() + rect.get_width() / 2, height),
                                 xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8)
        self.fig.tight_layout()
        self.canvas.draw()

    def export_report_txt(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not path:
            return
        total = sum(e["amount"] for e in self.data.get("expenses", []))
        with open(path, "w", encoding="utf-8") as f:
            f.write("EMEKA Expense Report\n")
            f.write(f"Generated: {datetime.now()}\n\n")
            f.write(f"Total Spent: ₦{total:,.2f}\n\n")
            f.write("By Category:\n")
            by_cat = defaultdict(float)
            for e in self.data.get("expenses", []):
                by_cat[e["category"]] += e["amount"]
            for c, a in sorted(by_cat.items(), key=lambda x: x[1], reverse=True):
                f.write(f" - {c}: ₦{a:,.2f}\n")
            f.write("\nDetails:\n")
            for e in self.data.get("expenses", []):
                f.write(f"{e['date']} | {e['category']} | {e['description']} | ₦{e['amount']:,.2f}\n")
        messagebox.showinfo("Saved", "Report exported.")

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as csvf:
            writer = csv.writer(csvf)
            writer.writerow(["date", "category", "description", "amount"])
            for e in self.data.get("expenses", []):
                writer.writerow([e["date"], e["category"], e["description"], f"{e['amount']:.2f}"])
        messagebox.showinfo("Saved", "CSV exported.")

    # ---------------- SETTINGS ----------------
    def _page_settings(self, parent):
        pad = 20
        header = tk.Frame(parent)
        header.pack(fill="x", padx=pad, pady=(18, 8))
        tk.Label(header, text="Settings", font=("Segoe UI", 16, "bold")).pack(side="left")

        form = tk.Frame(parent)
        form.pack(fill="x", padx=pad, pady=8)
        tk.Label(form, text="Monthly Budget (₦)").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.budget_var).grid(row=0, column=1, padx=8, sticky="we")
        ttk.Button(form, text="Save Budget", command=self.save_budget).grid(row=0, column=2, padx=8)

        # Danger zone
        danger_box = tk.Frame(parent)
        danger_box.pack(fill="x", padx=pad, pady=(16, 8))
        tk.Label(danger_box, text="Danger Zone", font=("Segoe UI", 12, "bold"), fg=self.theme["danger"]).pack(anchor="w")
        ttk.Button(danger_box, text="Clear All Data", command=self.clear_all_data).pack(anchor="w", pady=8)

        form.columnconfigure(1, weight=1)

    def save_budget(self):
        try:
            b = float(self.budget_var.get().strip().replace(",", ""))
        except Exception:
            messagebox.showerror("Invalid", "Budget must be a number.")
            return
        self.data["budget"] = round(b, 2)
        self.storage.save(self.data)
        self.refresh_all()
        messagebox.showinfo("Saved", "Budget saved.")

    def clear_all_data(self):
        if not messagebox.askyesno("Confirm", "Clear ALL data? This cannot be undone."):
            return
        self.data = {"expenses": [], "budget": 0.0}
        self.storage.save(self.data)
        self.refresh_all()
        messagebox.showinfo("Done", "All data cleared.")

    # ---------------- Theme & Utilities ----------------
    def _apply_theme(self):
        t = self.theme
        # root / background
        self.configure(bg=t["bg"])
        self.sidebar.configure(bg=t["panel"])
        self.content.configure(bg=t["bg"])
        # sidebar children
        for c in self.sidebar.winfo_children():
            try:
                c.configure(bg=t["panel"], fg=t["fg"])
            except Exception:
                pass
        # nav buttons
        for b in self.navbuttons.values():
            b.configure(bg=t["panel"], fg=t["fg"], activebackground=t["card"], bd=0)

        # style ttk elements
        self.style.configure("TButton", padding=6)
        self.style.configure("TLabel", background=t["bg"], foreground=t["fg"])
        self.style.configure("TEntry", fieldbackground=t["entry_bg"], foreground=t["fg"])
        self.style.configure("Treeview", background=t["table_bg"], fieldbackground=t["table_bg"], foreground=t["fg"], rowheight=26)
        self.style.configure("Treeview.Heading", background=t["panel"], foreground=t["fg"])

        # apply to frames and widgets inside content
        for frame in self.frames.values():
            for w in frame.winfo_children():
                try:
                    if isinstance(w, tk.Frame):
                        w.configure(bg=t["bg"])
                    elif isinstance(w, tk.Label):
                        w.configure(bg=t["bg"], fg=t["fg"])
                    elif isinstance(w, tk.Text):
                        w.configure(bg=t["card"], fg=t["fg"])
                except Exception:
                    pass

    def toggle_theme(self):
        self.theme = Theme.LIGHT if self.theme == Theme.DARK else Theme.DARK
        self._apply_theme()
        self.refresh_all()

    def show_frame(self, name):
        for k, f in self.frames.items():
            f.place_forget()
            # change nav button relief
            self.navbuttons[k].config(relief="sunken" if k == name else "flat")
        self.frames[name].place(relx=0, rely=0, relwidth=1, relheight=1)
        # refresh logic
        if name == "dashboard":
            self.refresh_dashboard()
        elif name == "reports":
            self.refresh_reports()

    def refresh_all(self):
        # reload storage (in case external modification)
        self.data = self.storage.load()
        self.budget_var.set(str(self.data.get("budget", 0.0)))
        # ensure categories list includes current categories
        for e in self.data.get("expenses", []):
            c = e.get("category")
            if c and c not in self.default_categories:
                self.default_categories.append(c)
        self.cat_combo.config(values=["All"] + self.default_categories)
        self.cat_combo_add.config(values=self.default_categories + ["Custom..."])
        self.refresh_dashboard()
        self.refresh_reports()

# ---------------- Run ----------------
if __name__ == "__main__":
    app = ExpenseApp()
    app.mainloop()
