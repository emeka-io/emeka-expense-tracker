import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DATA_FILE = "expenses_premium.json"

# -------------------------
# Data storage helpers
# -------------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"expenses": [], "budget": 0.0}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# -------------------------
# Theme manager
# -------------------------
class Theme:
    """Simple theme manager for light/dark
    Colors are grouped to make consistent theming easy.
    """

    DARK = {
    "bg": "#0d0d0d",       # main background (deep charcoal)
    "panel": "#1a1a1a",    # sidebar (slightly lighter charcoal)
    "card": "#03C675",     # card backgrounds (for headers / top texts)
    "fg": "#e6e6e6",       # main readable text (soft white)
    "muted": "#9ca3af",    # muted grey
    "accent": "#4cc9f0",   # soft electric blue
    "danger": "#ef4444",   # red for errors
    "success": "#22c55e",  # green for success
    "table_bg": "#181818", # table background
    "row_alt": "#101010",  # alternate row background

}



    LIGHT = {
        "bg": "#ffffff",
        "panel": "#fefefe",
        "card": "#2D452D",
        "fg": "#00301f",
        "muted": "#475569",
        "accent": "#2563eb",
        "danger": "#dc2626",
        "success": "#16a34a",
        "table_bg": "#eaedea",
        "row_alt": "#f8fafc",
    }


# -------------------------
# Main App
# -------------------------
class ExpenseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EMEKA's Smart Expense Tracker")
        self.geometry("1000x620")
        self.minsize(880, 540)

        self.data = load_data()
        self.current_theme = Theme.DARK
        self.style = ttk.Style(self)

        # Build UI
        self._build_root_styles()
        self._build_layout()
        self._apply_theme()

        # Show dashboard by default
        self.show_frame("dashboard")
        self.check_budget_alert(startup=True)

    # -------------------------
    # Styling
    # -------------------------
    def _build_root_styles(self):
        # General ttk style tweaks
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=6, relief="flat")
        self.style.configure("TLabel", padding=4)
        self.style.configure("Card.TFrame", relief="flat")

    def _apply_theme(self):
        t = self.current_theme
        self.configure(bg=t["bg"])  # root background

        # Sidebar
        self.sidebar.configure(bg=t["panel"]) 
        for child in self.sidebar.winfo_children():
            try:
                child.configure(bg=t["panel"], fg=t["fg"], activebackground=t["card"], bd=0)
            except Exception:
                pass

        # Content area
        self.content.configure(bg=t["bg"]) 
        for frame in (self.dashboard_frame, self.add_frame, self.reports_frame, self.settings_frame):
            frame.configure(bg=t["bg"]) 
            for w in frame.winfo_children():
                self._style_widget(w, t)

        # Tree style for tables
        self.style.configure("Treeview",
                             background=t["table_bg"],
                             foreground=t["fg"],
                             fieldbackground=t["table_bg"],
                             rowheight=24)
        self.style.map('Treeview', background=[('selected', t['card'])])
        self.style.configure("Treeview.Heading", font=(None, 10, 'bold'), foreground=t["fg"], background=t["panel"]) 

    def _style_widget(self, w, t):
        # Apply simple bg/fg mapping to common widget types
        cls = w.__class__.__name__
        try:
            if cls in ("Label", "Frame", "Canvas"):
                w.configure(bg=t["bg"], fg=t.get("fg", ""))
        except Exception:
            pass

    # -------------------------
    # Layout
    # -------------------------
    def _build_layout(self):
        # Root frames
        self.sidebar = tk.Frame(self, width=220)
        self.sidebar.pack(side="left", fill="y")

        self.content = tk.Frame(self)
        self.content.pack(side="right", fill="both", expand=True)

        self._build_sidebar()
        self._build_content_frames()

    def _build_sidebar(self):
        t = self.current_theme
        self.sidebar.configure(bg=t["panel"]) 

        # App title / logo area
        logo = tk.Label(self.sidebar, text="🧭 EMEKA's", font=(None, 16, "bold"), anchor="w")
        logo.pack(fill="x", padx=16, pady=(18, 8))

        tagline = tk.Label(self.sidebar, text="Expense Tracker", font=(None, 9), anchor="w")
        tagline.pack(fill="x", padx=16)

        # Navigation buttons
        nav_frame = tk.Frame(self.sidebar, bg=t["panel"]) 
        nav_frame.pack(fill="x", padx=8, pady=18)

        btn_specs = [
            ("dashboard", "📊  Dashboard"),
            ("add", "➕  Add Expense"),
            ("reports", "📁  Reports"),
            ("settings", "⚙️  Settings"),
        ]

        self.nav_buttons = {}
        for key, label in btn_specs:
            b = tk.Button(nav_frame, text=label, anchor="w", relief="flat", padx=12,
                          command=lambda k=key: self.show_frame(k))
            b.pack(fill="x", pady=6, padx=6)
            self.nav_buttons[key] = b

        # Spacer
        tk.Frame(self.sidebar, height=10, bg=t["panel"]).pack(fill="x")

        # Theme toggle
        theme_label = tk.Label(self.sidebar, text="Theme", anchor="w", font=(None, 9))
        theme_label.pack(fill="x", padx=16, pady=(12, 4))

        self.theme_var = tk.StringVar(value="dark")
        self.theme_toggle = ttk.Button(self.sidebar, text="Toggle Dark / Light", command=self.toggle_theme)
        self.theme_toggle.pack(fill="x", padx=16, pady=(0, 12))

        # Quick stats at bottom
        bottom = tk.Frame(self.sidebar, bg=t["panel"])
        bottom.pack(side="bottom", fill="x", padx=12, pady=12)
        self.total_label = tk.Label(bottom, text="Total: ₦0.00", anchor="w", font=(None, 10, "bold"))
        self.total_label.pack(fill="x")
        self.budget_label = tk.Label(bottom, text="Budget: ₦0.00", anchor="w", font=(None, 9))
        self.budget_label.pack(fill="x", pady=(4, 0))

    def _build_content_frames(self):
        # Create dictionary of frames for pages
        self.frames = {}

        # Dashboard
        self.dashboard_frame = tk.Frame(self.content)
        self.frames["dashboard"] = self.dashboard_frame
        self._build_dashboard(self.dashboard_frame)

        # Add Expense
        self.add_frame = tk.Frame(self.content)
        self.frames["add"] = self.add_frame
        self._build_add(self.add_frame)

        # Reports
        self.reports_frame = tk.Frame(self.content)
        self.frames["reports"] = self.reports_frame
        self._build_reports(self.reports_frame)

        # Settings
        self.settings_frame = tk.Frame(self.content)
        self.frames["settings"] = self.settings_frame
        self._build_settings(self.settings_frame)

        # Pack a placeholder content area container
        for f in self.frames.values():
            f.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)

    # -------------------------
    # Page: Dashboard
    # -------------------------
    def _build_dashboard(self, parent):
        # Top cards
        cards = tk.Frame(parent, bg=self.current_theme["bg"]) 
        cards.pack(fill="x", padx=20, pady=18)

        self.card_total = self._make_card(cards, "Total Spent", "₦0.00")
        self.card_budget = self._make_card(cards, "Budget", f"₦{self.data.get('budget',0):.2f}")
        self.card_remaining = self._make_card(cards, "Remaining", "₦0.00")

        # Table area
        table_card = tk.Frame(parent, bg=self.current_theme["card"], bd=0)
        table_card.pack(fill="both", expand=True, padx=20, pady=(8, 20))

        lbl = tk.Label(table_card, text="Recent Expenses", font=(None, 12, "bold"), anchor="w")
        lbl.pack(fill="x", padx=12, pady=(12, 6))

        cols = ("date", "category", "description", "amount")
        self.tree = ttk.Treeview(table_card, columns=cols, show="headings", selectmode="browse")
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Footer quick actions
        footer = tk.Frame(parent, bg=self.current_theme["bg"]) 
        footer.pack(fill="x", padx=20, pady=(0, 12))
        ttk.Button(footer, text="Add Expense", command=lambda: self.show_frame("add")).pack(side="left")
        ttk.Button(footer, text="Export Report", command=self.export_report).pack(side="left", padx=8)

        self.refresh_dashboard()

    def _make_card(self, parent, title, value):
        f = tk.Frame(parent, bg=self.current_theme["card"], bd=0, padx=12, pady=12)
        f.pack(side="left", padx=8, pady=4, fill="y")
        tk.Label(f, text=title, font=(None, 9), anchor="w", bg=self.current_theme["card"]).pack(fill="x")
        lbl_val = tk.Label(f, text=value, font=(None, 14, "bold"), anchor="w", bg=self.current_theme["card"]) 
        lbl_val.pack(fill="x", pady=(6, 0))
        return lbl_val

    def refresh_dashboard(self):
        total = sum(e["amount"] for e in self.data.get("expenses", []))
        budget = float(self.data.get("budget", 0.0) or 0.0)
        remaining = budget - total if budget else 0.0

        self.card_total.config(text=f"₦{total:.2f}")
        self.card_budget.config(text=f"₦{budget:.2f}")
        if budget:
            self.card_remaining.config(text=f"₦{remaining:.2f}")
        else:
            self.card_remaining.config(text="—")

        # update sidebar quick stats
        self.total_label.config(text=f"Total: ₦{total:.2f}")
        self.budget_label.config(text=f"Budget: ₦{budget:.2f}")

        # populate recent expenses (most recent 50)
        for r in self.tree.get_children():
            self.tree.delete(r)
        expenses_sorted = sorted(self.data.get("expenses", []), key=lambda x: x["date"], reverse=True)[:50]
        for e in expenses_sorted:
            self.tree.insert("", "end", values=(e["date"], e["category"], e["description"], f"₦{e['amount']:.2f}"))

    # -------------------------
    # Page: Add Expense
    # -------------------------
    def _build_add(self, parent):
        pad = 18
        container = tk.Frame(parent, bg=self.current_theme["bg"]) 
        container.pack(fill="both", expand=True, padx=20, pady=20)

        form = tk.Frame(container, bg=self.current_theme["card"], padx=16, pady=16)
        form.pack(side="left", fill="y", padx=(0, 12))

        tk.Label(form, text="Add New Expense", font=(None, 12, "bold"), bg=self.current_theme["card"]).pack(fill="x", pady=(0, 8))

        tk.Label(form, text="Amount (₦)", bg=self.current_theme["card"]).pack(anchor="w")
        self.amount_var = tk.StringVar()
        tk.Entry(form, textvariable=self.amount_var).pack(fill="x", pady=6)

        tk.Label(form, text="Category", bg=self.current_theme["card"]).pack(anchor="w")
        self.category_var = tk.StringVar()
        tk.Entry(form, textvariable=self.category_var).pack(fill="x", pady=6)

        tk.Label(form, text="Description", bg=self.current_theme["card"]).pack(anchor="w")
        self.desc_var = tk.StringVar()
        tk.Entry(form, textvariable=self.desc_var).pack(fill="x", pady=6)

        tk.Button(form, text="Add Expense", command=self.add_expense, width=18).pack(pady=(12, 4))
        tk.Button(form, text="Back to Dashboard", command=lambda: self.show_frame("dashboard"), width=18).pack()

        # Right side: quick stats & categories
        right = tk.Frame(container, bg=self.current_theme["bg"]) 
        right.pack(side="right", fill="both", expand=True)

        stats_card = tk.Frame(right, bg=self.current_theme["card"], padx=12, pady=12)
        stats_card.pack(fill="both", expand=True)
        tk.Label(stats_card, text="Quick Stats", font=(None, 11, "bold"), bg=self.current_theme["card"]).pack(anchor="w")

        self.stats_text = tk.Label(stats_card, text="", justify="left", bg=self.current_theme["card"], anchor="nw")
        self.stats_text.pack(fill="both", expand=True, pady=(8,0))

        self.update_quick_stats()

    def add_expense(self):
        try:
            amount = float(self.amount_var.get())
        except Exception:
            messagebox.showerror("Invalid", "Amount must be a number.")
            return
        cat = self.category_var.get().strip().title()
        desc = self.desc_var.get().strip()
        if not cat or not desc:
            messagebox.showerror("Invalid", "Category and description are required.")
            return
        entry = {
            "amount": amount,
            "category": cat,
            "description": desc,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.data.setdefault("expenses", []).append(entry)
        save_data(self.data)
        messagebox.showinfo("Saved", "Expense added successfully.")
        self.amount_var.set("")
        self.category_var.set("")
        self.desc_var.set("")
        self.refresh_dashboard()
        self.update_quick_stats()
        self.check_budget_alert()

    def update_quick_stats(self):
        total = sum(e["amount"] for e in self.data.get("expenses", []))
        by_cat = {}
        for e in self.data.get("expenses", []):
            by_cat[e["category"]] = by_cat.get(e["category"], 0.0) + e["amount"]
        lines = [f"Total: ₦{total:.2f}", "", "Top Categories:"]
        top = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)[:5]
        for c, a in top:
            lines.append(f"{c}: ₦{a:.2f}")
        self.stats_text.config(text="\n".join(lines))

    # -------------------------
    # Page: Reports
    # -------------------------
    def _build_reports(self, parent):
        container = tk.Frame(parent, bg=self.current_theme["bg"]) 
        container.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(container, text="Reports", font=(None, 14, "bold"), bg=self.current_theme["bg"]).pack(anchor="w")
        tk.Button(container, text="Export full report (.txt)", command=self.export_report).pack(anchor="w", pady=8)

        # Summary area
        summary = tk.Frame(container, bg=self.current_theme["card"], padx=12, pady=12)
        summary.pack(fill="both", expand=True)
        self.report_text = tk.Text(summary, height=20, wrap="word", bd=0)
        self.report_text.pack(fill="both", expand=True)
        self.refresh_reports()

    def refresh_reports(self):
        total = sum(e["amount"] for e in self.data.get("expenses", []))
        by_cat = {}
        for e in self.data.get("expenses", []):
            by_cat[e["category"]] = by_cat.get(e["category"], 0.0) + e["amount"]
        lines = [f"Report generated: {datetime.now()}", "", f"Total Spent: ₦{total:.2f}", "", "By Category:"]
        for c, a in sorted(by_cat.items(), key=lambda x: x[1], reverse=True):
            lines.append(f" - {c}: ₦{a:.2f}")

        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, "\n".join(lines))

    # -------------------------
    # Page: Settings
    # -------------------------
    def _build_settings(self, parent):
        container = tk.Frame(parent, bg=self.current_theme["bg"]) 
        container.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(container, text="Settings", font=(None, 14, "bold"), bg=self.current_theme["bg"]).pack(anchor="w")

        form = tk.Frame(container, bg=self.current_theme["card"], padx=12, pady=12)
        form.pack(fill="x", pady=(12, 8))

        tk.Label(form, text="Set Monthly Budget (₦)", bg=self.current_theme["card"]).grid(row=0, column=0, sticky="w")
        self.budget_var = tk.StringVar(value=str(self.data.get("budget", "")))
        tk.Entry(form, textvariable=self.budget_var).grid(row=0, column=1, padx=8, pady=6)
        tk.Button(form, text="Save Budget", command=self.save_budget).grid(row=0, column=2, padx=8)

        # Danger zone
        danger = tk.Frame(container, bg=self.current_theme["bg"]) 
        danger.pack(fill="x", pady=(20,0))
        tk.Label(danger, text="Danger Zone", font=(None, 11, "bold"), bg=self.current_theme["bg"], fg=self.current_theme["danger"]).pack(anchor="w")
        tk.Button(danger, text="Clear All Data", command=self.clear_all_data, fg="white", bg=self.current_theme["danger"]).pack(anchor="w", pady=8)

    def save_budget(self):
        try:
            b = float(self.budget_var.get())
            self.data["budget"] = b
            save_data(self.data)
            messagebox.showinfo("Saved", "Budget saved.")
            self.refresh_dashboard()
        except Exception:
            messagebox.showerror("Invalid", "Budget must be a number.")

    def clear_all_data(self):
        if not messagebox.askyesno("Confirm", "This will delete all expenses and reset budget. Continue?"):
            return
        self.data = {"expenses": [], "budget": 0.0}
        save_data(self.data)
        self.refresh_dashboard()
        self.update_quick_stats()
        self.refresh_reports()
        messagebox.showinfo("Done", "All data cleared.")

    # -------------------------
    # Utility: page switching
    # -------------------------
    def show_frame(self, name):
        # hide all
        for k, f in self.frames.items():
            f.place_forget()
        # show target
        self.frames[name].place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
        # highlight nav
        for k, b in self.nav_buttons.items():
            if k == name:
                b.config(relief="sunken")
            else:
                b.config(relief="flat")
        # refresh page-specific content
        if name == "dashboard":
            self.refresh_dashboard()
        elif name == "reports":
            self.refresh_reports()
        elif name == "add":
            self.update_quick_stats()

    # -------------------------
    # Export report
    # -------------------------
    def export_report(self):
        report_lines = []
        report_lines.append("=== Expense Report ===")
        report_lines.append(f"Generated: {datetime.now()}")
        report_lines.append("")
        total = sum(e["amount"] for e in self.data.get("expenses", []))
        report_lines.append(f"Total Spent: ₦{total:.2f}")
        report_lines.append("")
        report_lines.append("Detail:")
        for e in sorted(self.data.get("expenses", []), key=lambda x: x["date"]):
            report_lines.append(f"{e['date']} | {e['category']} | {e['description']} | ₦{e['amount']:.2f}")

        # File dialog
        fpath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files","*.txt")], initialfile=f"expense_report_{datetime.now().strftime('%Y%m%d')}.txt")
        if fpath:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            messagebox.showinfo("Exported", f"Report saved to {fpath}")

    
    # Budget Alerts
    
    def check_budget_alert(self, startup=False):
        budget = float(self.data.get("budget", 0) or 0)
        if budget <= 0:
            return
        total = sum(e["amount"] for e in self.data.get("expenses", []))
        if total > budget:
            messagebox.showwarning("Budget Exceeded", f"You have exceeded your monthly budget!\nSpent: ₦{total:.2f}\nBudget: ₦{budget:.2f}")
        elif total >= 0.7 * budget and not startup:
            messagebox.showinfo("Budget Alert", f"You have used {total/budget:.0%} of your budget (>= 70%).\nSpent: ₦{total:.2f}\nBudget: ₦{budget:.2f}")

    
    # Theme toggle
    
    def toggle_theme(self):
        if self.current_theme is Theme.DARK:
            self.current_theme = Theme.LIGHT
        else:
            self.current_theme = Theme.DARK
        # update all theme-sensitive vars and re-apply
        self._apply_theme()
        # update widgets text/background that were not covered
        self._refresh_all_widget_colors()

    def _refresh_all_widget_colors(self):
        t = self.current_theme
        # sidebar
        self.sidebar.config(bg=t['panel'])
        for child in self.sidebar.winfo_children():
            try:
                child.config(bg=t['panel'], fg=t['fg'])
            except Exception:
                pass
        # content
        self.content.config(bg=t['bg'])
        for frame in self.frames.values():
            frame.config(bg=t['bg'])
            for w in frame.winfo_children():
                try:
                    if isinstance(w, tk.Frame) or isinstance(w, tk.LabelFrame):
                        w.config(bg=t['card'])
                    elif isinstance(w, tk.Label) or isinstance(w, tk.Button) or isinstance(w, tk.Entry) or isinstance(w, tk.Text):
                        w.config(bg=t['card'], fg=t['fg'])
                except Exception:
                    pass
        # cards
        try:
            self.card_total.master.config(bg=t['card'])
            self.card_budget.master.config(bg=t['card'])
            self.card_remaining.master.config(bg=t['card'])
        except Exception:
            pass


# Run
if __name__ == '__main__':
    app = ExpenseApp()
    
    app.mainloop()