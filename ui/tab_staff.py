
# ==============================================================
#  FILE: tab_staff.py
#  PROJECT: UMAMCO Job Production Tracker
#  DESCRIPTION:
#     Handles the "Staff Management" tab — registering, viewing,
#     activating/deactivating, and deleting staff records.
# ==============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import re
from storage.json_store import load_json, save_json


class StaffTab:
    """Manages the Staff Management tab UI and logic."""

    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self._build_staff_tab()

    # ------------------- BUILD STAFF TAB -------------------
    def _build_staff_tab(self):
        frame = self.frame
        ttk.Label(frame, text="Staff Management", font=("Segoe UI", 14, "bold")).pack(pady=10)

        # ==== Top Form ====
        form = ttk.LabelFrame(frame, text="Register New Staff")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Name").grid(row=0, column=0, padx=5, pady=4, sticky="w")
        self.entry_staff_name_new = ttk.Entry(form, width=25)
        self.entry_staff_name_new.grid(row=0, column=1, padx=5, pady=4)

        ttk.Label(form, text="Role").grid(row=0, column=2, padx=5, pady=4, sticky="w")
        self.cmb_role = ttk.Combobox(
            form, values=["Team Leader", "Operator", "Supervisor"],
            state="readonly", width=18
        )
        self.cmb_role.set("Team Leader")
        self.cmb_role.grid(row=0, column=3, padx=5, pady=4)

        ttk.Label(form, text="Shift Type").grid(row=1, column=0, padx=5, pady=4, sticky="w")
        self.cmb_shift_type_staff = ttk.Combobox(
            form, values=["Morning", "Afternoon", "Night"], state="readonly", width=18
        )
        self.cmb_shift_type_staff.set("Morning")
        self.cmb_shift_type_staff.grid(row=1, column=1, padx=5, pady=4)

        ttk.Label(form, text="Status").grid(row=1, column=2, padx=5, pady=4, sticky="w")
        self.cmb_status = ttk.Combobox(
            form, values=["Active", "Inactive"], state="readonly", width=18
        )
        self.cmb_status.set("Active")
        self.cmb_status.grid(row=1, column=3, padx=5, pady=4)

        ttk.Button(form, text="➕ Add Staff", command=self._add_staff).grid(row=2, column=3, padx=5, pady=(10, 6))

        # ==== Staff Directory Table ====
        sec = ttk.LabelFrame(frame, text="Staff Directory")
        sec.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "name", "role", "shift_type", "status", "date_joined")
        self.staff_tree = ttk.Treeview(sec, columns=columns, show="headings", height=10)
        for col, width in zip(columns, (80, 150, 120, 100, 90, 120)):
            self.staff_tree.heading(col, text=col.replace("_", " ").title())
            self.staff_tree.column(col, width=width, anchor="center")
        self.staff_tree.pack(fill="x", padx=6, pady=6)

        # ==== Buttons below table ====
        btns = ttk.Frame(sec)
        btns.pack(side="top", pady=6)
        ttk.Button(btns, text="🟢 Activate", command=self._activate_staff).grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="🔴 Deactivate", command=self._deactivate_staff).grid(row=0, column=1, padx=5)
        ttk.Button(btns, text="❌ Delete", command=self._delete_staff).grid(row=0, column=2, padx=5)
        ttk.Button(btns, text="🔄 Refresh", command=self._load_staff_into_tree).grid(row=0, column=3, padx=5)

        self._load_staff_into_tree()

    # ------------------- LOAD STAFF -------------------
    def _load_staff_into_tree(self):
        """Load all staff into the table."""
        for r in self.staff_tree.get_children():
            self.staff_tree.delete(r)

        db = load_json("data/staff.json", default=[])
        for s in db:
            self.staff_tree.insert("", tk.END, values=(
                s["staff_id"], s["name"], s["role"], s["shift_type"], s["status"], s["date_joined"]
            ))

    # ------------------- VALIDATION HELPERS -------------------
    def _generate_staff_id(self):
        """Generate next staff ID like STF001."""
        staff_list = load_json("data/staff.json", default=[])
        if not staff_list:
            return "STF001"
        last_id = max(int(s["staff_id"][3:]) for s in staff_list)
        return f"STF{last_id + 1:03d}"

    def _is_valid_name(self, name):
        """Ensure staff name contains only alphabets and spaces."""
        return bool(re.match(r"^[A-Za-z\s]+$", name))

    # ------------------- ADD STAFF -------------------
    def _add_staff(self):
        """Add a new staff record."""
        name = self.entry_staff_name_new.get().title().strip()
        role = self.cmb_role.get()
        shift_type = self.cmb_shift_type_staff.get()
        status = self.cmb_status.get()

        if not name:
            messagebox.showwarning("Missing Data", "Please enter the staff name.")
            return

        if not self._is_valid_name(name):
            messagebox.showwarning("Invalid Name", "Name must contain only letters and spaces.")
            return

        staff = {
            "staff_id": self._generate_staff_id(),
            "name": name,
            "role": role,
            "shift_type": shift_type,
            "status": status,
            "date_joined": date.today().isoformat()
        }

        db = load_json("data/staff.json", default=[])
        db.append(staff)
        save_json("data/staff.json", db)

        messagebox.showinfo("Success", f"Staff '{name}' added successfully.")
        self.entry_staff_name_new.delete(0, tk.END)
        self._load_staff_into_tree()

    # ------------------- STATUS ACTIONS -------------------
    def _get_selected_staff(self):
        """Return selected staff ID, or None."""
        sel = self.staff_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a staff record.")
            return None
        vals = self.staff_tree.item(sel[0], "values")
        return vals[0]  # staff_id

    def _activate_staff(self):
        self._change_staff_status("Active")

    def _deactivate_staff(self):
        self._change_staff_status("Inactive")

    def _change_staff_status(self, new_status):
        """Change status of selected staff."""
        staff_id = self._get_selected_staff()
        if not staff_id:
            return

        db = load_json("data/staff.json", default=[])
        for s in db:
            if s["staff_id"] == staff_id:
                s["status"] = new_status
                break

        save_json("data/staff.json", db)
        self._load_staff_into_tree()
        messagebox.showinfo("Status Updated", f"Staff {staff_id} set to {new_status}.")

    # ------------------- DELETE STAFF -------------------
    def _delete_staff(self):
        """Delete a staff record permanently."""
        staff_id = self._get_selected_staff()
        if not staff_id:
            return
        confirm = messagebox.askyesno("Confirm Delete", f"Delete staff {staff_id}?")
        if not confirm:
            return

        db = load_json("data/staff.json", default=[])
        db = [s for s in db if s["staff_id"] != staff_id]
        save_json("data/staff.json", db)
        self._load_staff_into_tree()
        messagebox.showinfo("Deleted", f"Staff {staff_id} removed.")
