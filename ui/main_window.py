import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import asdict
from datetime import date, datetime, timedelta
from domain.models import Job, StockItem, HourlyOutput, ShiftRecord
from storage.json_store import load_json, save_json


class JobProductionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UMAMCO Job Production Tracker")
        self.root.geometry("840x680")
        self.root.resizable(False, False)

        # Notebook (Tabs)
        notebook = ttk.Notebook(root)
        notebook.pack(expand=True, fill="both")

        # Frames for tabs
        self.frame_add_job = ttk.Frame(notebook)
        self.frame_view_jobs = ttk.Frame(notebook)
        self.frame_shift = ttk.Frame(notebook)

        # add tabs once
        notebook.add(self.frame_add_job, text="➕ Add Job")        # TAB -> 1
        notebook.add(self.frame_view_jobs, text="📋 View Jobs")    # TAB -> 2
        notebook.add(self.frame_shift, text="🕒 Shift & Output")   # TAB -> 3

        # build all tabs
        self._build_add_job_tab()
        self._build_view_jobs_tab()
        self._build_shift_tab()

    # ------------------- ADD JOB TAB -------------------
    def _build_add_job_tab(self):
        frame = self.frame_add_job

        ttk.Label(frame, text="Add New Production Job", font=("Segoe UI", 14, "bold")).pack(pady=10)

        self.entry_job_number = self._add_entry(frame, "Job Number")
        self.entry_customer_name = self._add_entry(frame, "Customer Name")
        self.entry_product = self._add_entry(frame, "Product")
        self.entry_stock_name = self._add_entry(frame, "Stock Name")
        self.entry_stock_quantity = self._add_entry(frame, "Stock Quantity")

        ttk.Button(frame, text="Save Job", command=self.save_job).pack(pady=10)
        ttk.Button(frame, text="Clear Fields", command=self.clear_fields).pack(pady=5)

    def _add_entry(self, parent, label_text):
        ttk.Label(parent, text=label_text).pack(pady=(5, 0))
        entry = ttk.Entry(parent, width=40)
        entry.pack(pady=2)
        return entry

    def clear_fields(self):
        for e in [
            self.entry_job_number,
            self.entry_customer_name,
            self.entry_product,
            self.entry_stock_name,
            self.entry_stock_quantity,
        ]:
            e.delete(0, tk.END)

    def save_job(self):
        job_number = self.entry_job_number.get().strip()
        customer_name = self.entry_customer_name.get().strip()
        product = self.entry_product.get().strip()
        stock_name = self.entry_stock_name.get().strip()
        stock_quantity = self.entry_stock_quantity.get().strip()

        if not (job_number and customer_name and product and stock_name and stock_quantity):
            messagebox.showwarning("Missing Fields", "All fields must be filled!")
            return

        try:
            stock_quantity = int(stock_quantity)
        except ValueError:
            messagebox.showwarning("Invalid Quantity", "Stock quantity must be a number.")
            return

        new_job = Job(
            job_number=job_number,
            customer_name=customer_name,
            product=product,
            stocks=[StockItem(name=stock_name, quantity=stock_quantity)],
        )

        jobs = load_json("data/jobs.json", default=[])

        if any(j["job_number"] == job_number for j in jobs):
            messagebox.showwarning("Duplicate", f"Job {job_number} already exists!")
            return

        jobs.append(asdict(new_job))
        save_json("data/jobs.json", jobs)

        messagebox.showinfo("Success", f"Job {job_number} saved successfully!")
        self.clear_fields()
        self.load_jobs_to_treeview()  # Refresh list view automatically

    # ------------------- VIEW JOBS TAB -------------------
    def _build_view_jobs_tab(self):
        frame = self.frame_view_jobs

        ttk.Label(frame, text="All Jobs", font=("Segoe UI", 14, "bold")).pack(pady=10)

        columns = ("job_number", "customer_name", "product", "status")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=140)
        self.tree.pack(padx=10, pady=10, fill="x")

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="🔄 Refresh", command=self.load_jobs_to_treeview).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="❌ Delete", command=self.delete_selected_job).grid(row=0, column=1, padx=5)

        self.load_jobs_to_treeview()

    def load_jobs_to_treeview(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        jobs = load_json("data/jobs.json", default=[])
        for job in jobs:
            self.tree.insert("", tk.END, values=(
                job["job_number"],
                job["customer_name"],
                job["product"],
                job.get("status", "Pending"),
            ))

    def delete_selected_job(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a job to delete.")
            return

        job_number = self.tree.item(selected[0], "values")[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Delete job {job_number}?")
        if not confirm:
            return

        jobs = load_json("data/jobs.json", default=[])
        jobs = [j for j in jobs if j["job_number"] != job_number]
        save_json("data/jobs.json", jobs)
        self.load_jobs_to_treeview()
        messagebox.showinfo("Deleted", f"Job {job_number} has been removed.")

    # ------------- SHIFT TAB -------------
    def _build_shift_tab(self):
        frame = self.frame_shift

        # ---- Shift Header ----
        hdr = ttk.LabelFrame(frame, text="Shift Setup")
        hdr.pack(fill="x", padx=10, pady=10)

        ttk.Label(hdr, text="Job Number").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.cmb_job_number = ttk.Combobox(hdr, width=18, state="readonly")
        self.cmb_job_number.grid(row=0, column=1, padx=6, pady=4)
        self._load_job_numbers_into_combobox()

        ttk.Label(hdr, text="Staff Name").grid(row=0, column=2, sticky="w", padx=6, pady=4)
        self.entry_staff_name = ttk.Entry(hdr, width=20)
        self.entry_staff_name.grid(row=0, column=3, padx=6, pady=4)

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
            hdr, values=["Morning", "Afternoon", "Night", "Custom"],
            width=12, state="readonly"
        )
        self.cmb_shift_type.set("Morning")
        self.cmb_shift_type.grid(row=0, column=5, padx=6, pady=4)

        # NEW: auto-generate hours button
        ttk.Button(hdr, text="Generate Hours", command=self._generate_hours).grid(row=2, column=5, padx=6, pady=(8, 4))

        # ---- Hourly Output Section ----
        self.shift_hours = []  # in-memory list of dicts: {hour_label, quantity, target, comment}

        sec = ttk.LabelFrame(frame, text="Hourly Output")
        sec.pack(fill="both", expand=True, padx=10, pady=10)

        # changed MISS% -> EXPECTED
        columns = ("hour", "quantity", "target", "ach%", "expected", "cum%", "comment", "status")
        self.hour_tree = ttk.Treeview(sec, columns=columns, show="headings", height=10)
        for col, width in zip(columns, (90, 80, 100, 60, 90, 60, 150, 70)):
            self.hour_tree.heading(col, text=col.upper())
            self.hour_tree.column(col, width=width, anchor="center")
        self.hour_tree.pack(side="top", fill="x", padx=6, pady=6)

        
        # ---- Row color styles ----
        self.hour_tree.tag_configure("NoData", foreground="black")
        self.hour_tree.tag_configure("Red", foreground="red")
        self.hour_tree.tag_configure("Yellow", foreground="orange")
        self.hour_tree.tag_configure("Green", foreground="green")
        self.hour_tree.tag_configure("Blue", foreground="blue")


        # Live total output label
        self.lbl_total_output = ttk.Label(sec, text="Total Output: 0 units", font=("Segoe UI", 10, "bold"))
        self.lbl_total_output.pack(pady=(4, 8))

        btns = ttk.Frame(sec)
        btns.pack(side="top", pady=6)
        ttk.Button(btns, text="➕ Add Output", command=self._open_add_output_dialog).grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="🗑️ Remove Selected", command=self._remove_selected_hour).grid(row=0, column=1, padx=5)

        # ---- Footer: Save Shift ----
        footer = ttk.Frame(frame)
        footer.pack(fill="x", padx=10, pady=10)
        ttk.Button(footer, text="💾 Save & Finsh Shift ✅", command=self._save_shift_record).pack(side="right")

    # ---------- helper: load jobs ----------
    def _load_job_numbers_into_combobox(self):
        jobs = load_json("data/jobs.json", default=[])
        job_numbers = [j["job_number"] for j in jobs]
        self.cmb_job_number["values"] = job_numbers
        if job_numbers:
            self.cmb_job_number.set(job_numbers[0])

    # ---------- NEW: auto-generate hours ----------
    def _generate_hours(self):
        """Auto-fill shift_hours based on start/end time, with break-aware targets."""
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
        # break time (hh:mm, minutes)
        breaks = [("09:00", 20), ("12:00", 15)]

        current = start
        while current < end:
            nxt = current + timedelta(hours=1)
            label = f"{current.strftime('%H:%M')}-{nxt.strftime('%H:%M')}"
            tgt = base_target

            for b_time, b_min in breaks:
                b = datetime.strptime(b_time, "%H:%M")
                # break falls inside this hour
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

    # ---------- NEW: add output for next empty hour ----------
    def _open_add_output_dialog(self):
        """Open dialog for the next hour that has quantity == 0."""
        # find the next empty hour
        pending = [h for h in self.shift_hours if h["quantity"] == 0]
        if not pending:
            messagebox.showinfo("Done", "All hourly slots are already filled.")
            return

        hour = pending[0]["hour_label"]
        target = pending[0]["target"]

        dlg = tk.Toplevel(self.root)
        dlg.title(f"Add Output ({hour})")
        dlg.geometry("360x280")
        dlg.transient(self.root)
        dlg.grab_set()

        ttk.Label(dlg, text=f"Hour: {hour}").pack(pady=(12, 2))
        ttk.Label(dlg, text=f"Target: {target} (100%)").pack(pady=(0, 10))

        ttk.Label(dlg, text="Actual Output").pack()
        entry_qty = ttk.Entry(dlg, width=20)
        entry_qty.pack(pady=4)

        # predefined reasons
        reasons = [
            "Machine cleaning",
            "Coder issue",
            "Checkweigher issue",
            "Stock finished",
            "Waiting on engineer",
            "Other"
        ]
        ttk.Label(dlg, text="Comment / Reason").pack(pady=(8, 2))
        cmb_reason = ttk.Combobox(dlg, values=reasons, width=28, state="readonly")
        cmb_reason.pack()

        other_entry = ttk.Entry(dlg, width=28)
        other_entry.pack(pady=(4, 2))
        other_entry.configure(state="disabled")

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

            # final comment
            if cmb_reason.get() == "Other":
                comment_val = other_entry.get().strip()
            else:
                comment_val = cmb_reason.get()

            # update the first empty hour
            for h in self.shift_hours:
                if h["hour_label"] == hour and h["quantity"] == 0:
                    h["quantity"] = qty
                    h["comment"] = comment_val
                    break

            self._refresh_hour_tree()
            dlg.destroy()

        ttk.Button(dlg, text="Add", command=submit).pack(pady=12)

    # ---------- refresh tree with per-row and CUM% ----------
    def _refresh_hour_tree(self):
        for r in self.hour_tree.get_children():
            self.hour_tree.delete(r)

        total_qty = 0
        total_tgt = 0

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

            # ----- Color logic based on % achieved -----
            if qty == 0:
                tag = "NoData"  # black
            elif ach_pct < 80:
                tag = "Red"
            elif ach_pct < 90:
                tag = "Yellow"
            elif ach_pct <= 100:
                tag = "Green"
            else:
                tag = "Blue"

            self.hour_tree.insert(
                "",
                tk.END,
                values=(
                    item["hour_label"],      # Hour range
                    qty,                     # Actual Qty
                    target_display,          # Hourly Target
                    ach_pct,                 # % Achieved this hour
                    expected_cum,            # Expected cumulative output
                    cum_pct,                 # Cumulative %
                    item.get("comment", ""), # Comment
                    status                   # Status
                ),
                tags=(tag,)
            )

        # ---- Update live total output label ----
        if total_tgt > 0:
            if total_qty >= total_tgt:
                self.lbl_total_output.config(
                    text=f"Total Output: {total_qty} units ✅ On Target",
                    foreground="green"
                )
            else:
                self.lbl_total_output.config(
                    text=f"Total Output: {total_qty} units ⚠️ Behind Target",
                    foreground="red"
                )
        else:
            self.lbl_total_output.config(text="Total Output: 0 units", foreground="black")


    def _remove_selected_hour(self):
        sel = self.hour_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a row to remove.")
            return
        values = self.hour_tree.item(sel[0], "values")
        hour_to_remove = values[0]
        for idx, item in enumerate(self.shift_hours):
            if item["hour_label"] == hour_to_remove:
                del self.shift_hours[idx]
                break
        self._refresh_hour_tree()

    def _save_shift_record(self):
        job_number = self.cmb_job_number.get().strip()
        staff_name = self.entry_staff_name.get().strip()
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

        # Build dataclasses — NOTE: shift_hours must NOT contain extra keys
        hours_dc = [HourlyOutput(
            hour_label=h["hour_label"],
            quantity=h["quantity"],
            target=h["target"],
            comment=h.get("comment", "")
        ) for h in self.shift_hours]

        total = sum(h.quantity for h in hours_dc)

        shift_id = f"{job_number}-{shift_date}-{start_time.replace(':','')}"
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
        rec_dict = asdict(record)
        db.append(rec_dict)
        save_json("data/shift_output.json", db)

        messagebox.showinfo("Saved", f"Shift saved.\nTotal Output: {total}")
        self.shift_hours = []
        self._refresh_hour_tree()
