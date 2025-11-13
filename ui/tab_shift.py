# ==============================================================
#  FILE: tab_shift.py
#  PROJECT: UMAMCO Job Production Tracker
#  DESCRIPTION:
#     Handles the "Shift & Output" tab — creating hourly shift
#     records, calculating performance, and saving results.
# ==============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime, timedelta
from dataclasses import asdict
from domain.models import HourlyOutput, ShiftRecord
from storage.json_store import load_json, save_json


class ShiftTab:
    """Manages shift creation, hourly outputs, and saving."""

    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.shift_hours = []  # in-memory list of dicts
        self._build_shift_tab()

    # ------------------- SHIFT TAB UI -------------------
    def _build_shift_tab(self):
        """Builds the full Shift tab interface."""
        frame = self.frame

        # ---- Shift Header Section ----
        hdr = ttk.LabelFrame(frame, text="Shift Setup")
        hdr.pack(fill="x", padx=10, pady=10)

        ttk.Label(hdr, text="Job Number").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.cmb_job_number = ttk.Combobox(hdr, width=18, state="readonly")
        self.cmb_job_number.grid(row=0, column=1, padx=6, pady=4)
        self._load_job_numbers_into_combobox()

        ttk.Label(hdr, text="Staff Name").grid(row=0, column=2, sticky="w", padx=6, pady=4)
        self.cmb_staff_name = ttk.Combobox(hdr, width=20, state="readonly")
        self.cmb_staff_name.grid(row=0, column=3, padx=6, pady=4)
        self._load_active_staff_into_combobox()

        ttk.Label(hdr, text="Date").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.entry_shift_date = ttk.Entry(hdr, width=18)
        self.entry_shift_date.insert(0, date.today().isoformat())
        self.entry_shift_date.grid(row=1, column=1, padx=6, pady=4)

        ttk.Label(hdr, text="Start Time").grid(row=1, column=2, sticky="w", padx=6, pady=4)
        self.entry_start_time = ttk.Entry(hdr, width=10)
        self.entry_start_time.insert(0, "06:00")
        self.entry_start_time.grid(row=1, column=3, padx=6, pady=4)

        ttk.Label(hdr, text="End Time").grid(row=1, column=4, sticky="w", padx=6, pady=4)
        self.entry_end_time = ttk.Entry(hdr, width=10)
        self.entry_end_time.insert(0, "14:00")
        self.entry_end_time.grid(row=1, column=5, padx=6, pady=4)

        ttk.Label(hdr, text="Shift Type").grid(row=0, column=4, sticky="w", padx=6, pady=4)
        self.cmb_shift_type = ttk.Combobox(
            hdr, values=["Morning", "Afternoon", "Night", "Custom"], width=12, state="readonly"
        )
        self.cmb_shift_type.set("Morning")
        self.cmb_shift_type.grid(row=0, column=5, padx=6, pady=4)

        ttk.Button(hdr, text="Generate Hours", command=self._generate_hours).grid(row=2, column=5, padx=6, pady=(8, 4))

        # ---- Hourly Output Section ----
        self._build_hourly_output_section(frame)

    # ------------------- LOAD JOBS & STAFF -------------------
    def _load_job_numbers_into_combobox(self):
        """Load all job numbers into dropdown."""
        jobs = load_json("data/jobs.json", default=[])
        job_numbers = [j["job_number"] for j in jobs]
        self.cmb_job_number["values"] = job_numbers
        self.cmb_job_number.set(job_numbers[0] if job_numbers else "")

    def _load_active_staff_into_combobox(self):
        """Load only active staff into dropdown."""
        staff_list = load_json("data/staff.json", default=[])
        active_staff = [s["name"] for s in staff_list if s.get("status") == "Active"]
        self.cmb_staff_name["values"] = active_staff
        self.cmb_staff_name.set(active_staff[0] if active_staff else "")

    # ------------------- GENERATE HOURS -------------------
    def _generate_hours(self):
        """Auto-fill shift hours between start and end time."""
        self.shift_hours.clear()

        start_str = self.entry_start_time.get().strip()
        end_str = self.entry_end_time.get().strip()

        try:
            start = datetime.strptime(start_str, "%H:%M")
            end = datetime.strptime(end_str, "%H:%M")
        except ValueError:
            messagebox.showwarning("Time Format", "Use HH:MM (24-hr) format.")
            return

        base_target = 2500
        breaks = [("09:00", 20), ("12:00", 15)]

        current = start
        while current < end:
            nxt = current + timedelta(hours=1)
            label = f"{current.strftime('%H:%M')}-{nxt.strftime('%H:%M')}"
            tgt = base_target

            for b_time, b_min in breaks:
                b = datetime.strptime(b_time, "%H:%M")
                if current <= b < nxt:
                    tgt = round(base_target * (60 - b_min) / 60)
                    break

            self.shift_hours.append({
                "hour_label": label,
                "quantity": 0,
                "target": tgt,
                "comment": ""
            })
            current = nxt

        self._refresh_hour_tree()

    # ------------------- HOURLY OUTPUT SECTION -------------------
    def _build_hourly_output_section(self, frame):
        """Create table and buttons for hourly output."""
        sec = ttk.LabelFrame(frame, text="Hourly Output")
        sec.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("hour", "quantity", "target", "ach%", "expected", "cum%", "comment", "status")
        self.hour_tree = ttk.Treeview(sec, columns=columns, show="headings", height=10)
        for col, width in zip(columns, (90, 80, 100, 60, 90, 60, 150, 70)):
            self.hour_tree.heading(col, text=col.upper())
            self.hour_tree.column(col, width=width, anchor="center")
        self.hour_tree.pack(side="top", fill="x", padx=6, pady=6)

        self.hour_tree.tag_configure("NoData", foreground="black")
        self.hour_tree.tag_configure("Red", foreground="red")
        self.hour_tree.tag_configure("Yellow", foreground="orange")
        self.hour_tree.tag_configure("Green", foreground="green")
        self.hour_tree.tag_configure("Blue", foreground="blue")

        self.lbl_total_output = ttk.Label(sec, text="Total Output: 0 units", font=("Segoe UI", 10, "bold"))
        self.lbl_total_output.pack(pady=(4, 8))

        btns = ttk.Frame(sec)
        btns.pack(side="top", pady=6)
        ttk.Button(btns, text="➕ Add Output", command=self._open_add_output_dialog).grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="🗑️ Remove Selected", command=self._remove_selected_hour).grid(row=0, column=1, padx=5)

        footer = ttk.Frame(frame)
        footer.pack(fill="x", padx=10, pady=10)
        ttk.Button(footer, text="💾 Save & Finish Shift ✅", command=self._save_shift_record).pack(side="right")

    # ------------------- ADD OUTPUT DIALOG -------------------
    def _open_add_output_dialog(self):
        """Dialog to add output for the next available hour."""
        pending = [h for h in self.shift_hours if h["quantity"] == 0]
        if not pending:
            messagebox.showinfo("Done", "All hourly slots are already filled.")
            return

        hour = pending[0]["hour_label"]
        target = pending[0]["target"]

        dlg = tk.Toplevel(self.frame)
        dlg.title(f"Add Output ({hour})")
        dlg.geometry("360x280")
        dlg.transient(self.frame)
        dlg.grab_set()

        ttk.Label(dlg, text=f"Hour: {hour}").pack(pady=(12, 2))
        ttk.Label(dlg, text=f"Target: {target} (100%)").pack(pady=(0, 10))
        ttk.Label(dlg, text="Actual Output").pack()
        entry_qty = ttk.Entry(dlg, width=20)
        entry_qty.pack(pady=4)

        reasons = [
            "Machine cleaning", "Coder issue", "Stock finished", "Waiting on engineer",
            "Film changeover", "Power outage", "Maintenance", "Staff shortage",
            "Training", "Quality issue", "Inspection delay", "Setup time",
            "Breakdown", "Calibration", "Material jam", "Material defect",
            "Break time", "Shift end", "Other"
        ]

        ttk.Label(dlg, text="Comment / Reason").pack(pady=(8, 2))
        cmb_reason = ttk.Combobox(dlg, values=reasons, width=28, state="readonly")
        cmb_reason.pack()

        other_entry = ttk.Entry(dlg, width=28, state="disabled")
        other_entry.pack(pady=(4, 2))

        def on_reason_change(event):
            if cmb_reason.get() == "Other":
                other_entry.configure(state="normal")
            else:
                other_entry.delete(0, tk.END)
                other_entry.configure(state="disabled")

        cmb_reason.bind("<<ComboboxSelected>>", on_reason_change)

        def submit():
            val = entry_qty.get().strip()
            if not val:
                messagebox.showwarning("Missing", "Please enter actual output.", parent=dlg)
                return
            try:
                qty = int(val)
            except ValueError:
                messagebox.showwarning("Invalid", "Output must be a number.", parent=dlg)
                return

            comment_val = other_entry.get().strip() if cmb_reason.get() == "Other" else cmb_reason.get()

            for h in self.shift_hours:
                if h["hour_label"] == hour and h["quantity"] == 0:
                    h["quantity"] = qty
                    h["comment"] = comment_val
                    break

            self._refresh_hour_tree()
            dlg.destroy()

        ttk.Button(dlg, text="Add", command=submit).pack(pady=12)

    # ------------------- REFRESH TABLE -------------------
    def _refresh_hour_tree(self):
        """Recalculate percentages and update the hourly table."""
        for r in self.hour_tree.get_children():
            self.hour_tree.delete(r)

        total_qty, total_tgt = 0, 0

        for item in self.shift_hours:
            qty = item["quantity"]
            tgt = item["target"]

            total_qty += qty
            total_tgt += tgt

            ach_pct = round((qty / tgt) * 100, 1) if tgt else 0
            expected_cum = total_tgt
            cum_pct = round((total_qty / total_tgt) * 100, 1) if total_tgt else 0

            delta = qty - tgt
            status = "Under" if delta < 0 else ("Met" if delta == 0 else "Over")
            target_display = f"{tgt} (100%)"

            tag = (
                "NoData" if qty == 0 else
                "Red" if ach_pct < 80 else
                "Yellow" if ach_pct < 90 else
                "Green" if ach_pct <= 100 else
                "Blue"
            )

            self.hour_tree.insert(
                "", tk.END,
                values=(item["hour_label"], qty, target_display, ach_pct, expected_cum, cum_pct,
                        item.get("comment", ""), status),
                tags=(tag,)
            )

        if total_tgt > 0:
            if total_qty >= total_tgt:
                self.lbl_total_output.config(
                    text=f"Total Output: {total_qty} units ✅ On Target", foreground="green"
                )
            else:
                self.lbl_total_output.config(
                    text=f"Total Output: {total_qty} units ⚠️ Behind Target", foreground="red"
                )
        else:
            self.lbl_total_output.config(text="Total Output: 0 units", foreground="black")

    # ------------------- REMOVE HOURLY ROW -------------------
    def _remove_selected_hour(self):
        """Remove a selected hour entry."""
        sel = self.hour_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a row to remove.")
            return
        hour_to_remove = self.hour_tree.item(sel[0], "values")[0]
        self.shift_hours = [h for h in self.shift_hours if h["hour_label"] != hour_to_remove]
        self._refresh_hour_tree()

    # ------------------- RESET SHIFT FORM -------------------
    def _reset_shift_form(self):
        """Reset all shift entry fields to their default state."""
        self.shift_hours = []
        self._refresh_hour_tree()
        self._load_job_numbers_into_combobox()
        self._load_active_staff_into_combobox()

        self.entry_shift_date.delete(0, tk.END)
        self.entry_shift_date.insert(0, date.today().isoformat())

        self.entry_start_time.delete(0, tk.END)
        self.entry_start_time.insert(0, "06:00")

        self.entry_end_time.delete(0, tk.END)
        self.entry_end_time.insert(0, "14:00")

        self.cmb_shift_type.set("Morning")

    # ------------------- SAVE SHIFT RECORD -------------------
    def _save_shift_record(self):
        """Save all shift data to JSON."""
        try:
            job_number = self.cmb_job_number.get().strip()
            staff_name = self.cmb_staff_name.get().title().strip()
            shift_date = self.entry_shift_date.get().strip()
            start_time = self.entry_start_time.get().strip()
            end_time = self.entry_end_time.get().strip()
            shift_type = self.cmb_shift_type.get().strip()

            if not (job_number and staff_name and shift_date and start_time and end_time and shift_type):
                messagebox.showwarning("Missing Data", "All shift header fields are required.")
                return
            if not self.shift_hours:
                messagebox.showwarning("No Hourly Entries", "Please add at least one hourly output.")
                return

            hours_dc = [
                HourlyOutput(
                    hour_label=h["hour_label"],
                    quantity=h["quantity"],
                    target=h["target"],
                    comment=h.get("comment", "")
                ) for h in self.shift_hours
            ]

            total = sum(h.quantity for h in hours_dc)
            shift_id = f"{job_number}-{shift_date}-{start_time.replace(':', '')}"

            record = ShiftRecord(
                shift_id=shift_id,
                job_number=job_number,
                staff_name=staff_name,
                shift_date=shift_date,
                start_time=start_time,
                end_time=end_time,
                shift_type=shift_type,
                hourly_outputs=hours_dc,
                total_output=total
            )

            db = load_json("data/shift_output.json", default=[])
            db.append(asdict(record))
            save_json("data/shift_output.json", db)

            messagebox.showinfo("Saved", f"Shift saved.\nTotal Output: {total}")
            self._reset_shift_form()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save shift:\n{e}")
