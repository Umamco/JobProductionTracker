# ==============================================================
#  FILE: tab_logs.py
#  PROJECT: UMAMCO Job Production Tracker
#  DESCRIPTION:
#     Handles the "Production Logs & Reports" tab — providing
#     filtering, viewing, progress analytics, and exports.
# ==============================================================

import os
import csv
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from storage.json_store import load_json, save_json


class LogsTab:
    """Manages Production Logs, Filters, and Report Export."""

    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self._build_logs_tab()

    # ------------------- BUILD LOG TAB -------------------
    def _build_logs_tab(self):
        frame = self.frame
        ttk.Label(frame, text="Production Logs & Reports", font=("Segoe UI", 14, "bold")).pack(pady=10)

        # ==== Filter Section ====
        filter_frame = ttk.LabelFrame(frame, text="Filter Options")
        filter_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(filter_frame, text="Job Number").grid(row=0, column=0, padx=5, pady=4, sticky="w")
        self.cmb_log_job = ttk.Combobox(filter_frame, width=15, state="readonly")
        self.cmb_log_job.grid(row=0, column=1, padx=5, pady=4)

        ttk.Label(filter_frame, text="Staff Name").grid(row=0, column=2, padx=5, pady=4, sticky="w")
        self.cmb_log_staff = ttk.Combobox(filter_frame, width=20, state="readonly")
        self.cmb_log_staff.grid(row=0, column=3, padx=5, pady=4)

        ttk.Label(filter_frame, text="Date").grid(row=0, column=4, padx=5, pady=4, sticky="w")
        self.entry_log_date = ttk.Entry(filter_frame, width=15)
        self.entry_log_date.insert(0, date.today().isoformat())
        self.entry_log_date.grid(row=0, column=5, padx=5, pady=4)

        # Buttons for report actions
        btn_frame = ttk.Frame(filter_frame)
        btn_frame.grid(row=0, column=6, padx=5, pady=4)
        ttk.Button(btn_frame, text="🔍 Load Report", command=self._load_logs_to_tree).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="📄 Export CSV", command=self._export_logs_to_csv).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="🧾 Export PDF", command=self._export_logs_to_pdf).pack(side="left", padx=3)

        # ==== Report Table ====
        sec = ttk.LabelFrame(frame, text="Shift Reports")
        sec.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("date", "job", "staff", "shift", "output", "target", "progress", "status")
        self.logs_tree = ttk.Treeview(sec, columns=columns, show="headings", height=12)
        for col, width in zip(columns, (100, 100, 140, 80, 90, 90, 100, 80)):
            self.logs_tree.heading(col, text=col.upper())
            self.logs_tree.column(col, width=width, anchor="center")
        self.logs_tree.pack(fill="both", expand=True, padx=6, pady=6)

        self.logs_tree.tag_configure("low", foreground="red")
        self.logs_tree.tag_configure("mid", foreground="orange")
        self.logs_tree.tag_configure("ok", foreground="green")

        # ==== Summary ====
        self.lbl_summary = ttk.Label(
            frame, text="Total Shifts: 0 | Total Output: 0 units", font=("Segoe UI", 10, "bold")
        )
        self.lbl_summary.pack(pady=8)

        # ==== Job Progress Summary ====
        progress_frame = ttk.LabelFrame(frame, text="Job Completion Progress")
        progress_frame.pack(fill="x", padx=10, pady=10)

        self.lbl_job_target = ttk.Label(progress_frame, text="Total Target: 0 units")
        self.lbl_job_target.pack(pady=(4, 2))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, length=500)
        self.progress_bar.pack(pady=4)

        self.lbl_job_progress = ttk.Label(progress_frame, text="Progress: 0%")
        self.lbl_job_progress.pack(pady=(2, 4))

        # Load initial dropdown values
        self._refresh_filters()

    # ------------------- REFRESH FILTERS -------------------
    def _refresh_filters(self):
        """Reload available jobs and staff names for filters."""
        jobs = load_json("data/jobs.json", default=[])
        staff = load_json("data/staff.json", default=[])

        job_numbers = [j["job_number"] for j in jobs]
        staff_names = [s["name"] for s in staff if s.get("status") == "Active"]

        self.cmb_log_job["values"] = job_numbers
        self.cmb_log_staff["values"] = staff_names

        if job_numbers:
            self.cmb_log_job.set("")
        if staff_names:
            self.cmb_log_staff.set("")

    # ------------------- LOAD FILTERED LOGS -------------------
    def _load_logs_to_tree(self):
        """Load and filter shift records into the table."""
        for r in self.logs_tree.get_children():
            self.logs_tree.delete(r)

        all_shifts = load_json("data/shift_output.json", default=[])
        jobs = load_json("data/jobs.json", default=[])
        job_targets = {j["job_number"]: j["stocks"][0]["quantity"] for j in jobs if j.get("stocks")}

        filter_job = self.cmb_log_job.get().strip()
        filter_staff = self.cmb_log_staff.get().strip()
        filter_date = self.entry_log_date.get().strip()

        total_output = 0
        count = 0

        # --- Compute job completion ---
        if filter_job:
            job_entry = next((j for j in jobs if j["job_number"] == filter_job), None)
            if job_entry and job_entry.get("stocks"):
                job_target = job_entry["stocks"][0]["quantity"]
                self.lbl_job_target.config(text=f"Total Target: {job_target:,} units")

                job_shifts = [s for s in all_shifts if s["job_number"] == filter_job]
                total_job_output = sum(s["total_output"] for s in job_shifts)
                progress_pct = round((total_job_output / job_target) * 100, 2) if job_target else 0

                self.progress_var.set(progress_pct)
                self.lbl_job_progress.config(text=f"Progress: {progress_pct}% ({total_job_output:,} / {job_target:,})")

                style = ttk.Style()
                if progress_pct < 80:
                    style.configure("Red.Horizontal.TProgressbar", background="red")
                    self.progress_bar.config(style="Red.Horizontal.TProgressbar")
                elif progress_pct < 95:
                    style.configure("Yellow.Horizontal.TProgressbar", background="orange")
                    self.progress_bar.config(style="Yellow.Horizontal.TProgressbar")
                else:
                    style.configure("Green.Horizontal.TProgressbar", background="green")
                    self.progress_bar.config(style="Green.Horizontal.TProgressbar")
            else:
                self._reset_progress_labels()
        else:
            self._reset_progress_labels()

        # --- Load filtered logs ---
        for shift in all_shifts:
            if filter_job and shift["job_number"] != filter_job:
                continue
            if filter_staff and shift["staff_name"] != filter_staff:
                continue
            if filter_date and shift["shift_date"] != filter_date:
                continue

            job = shift["job_number"]
            total = shift["total_output"]
            target = job_targets.get(job, 0)
            progress = round((total / target) * 100, 1) if target else 0

            tag = "low" if progress < 90 else "mid" if progress < 100 else "ok"

            self.logs_tree.insert(
                "", tk.END,
                values=(
                    shift["shift_date"], job, shift["staff_name"],
                    shift["shift_type"], total, target,
                    f"{progress}%", "Completed" if progress >= 100 else "Ongoing"
                ),
                tags=(tag,)
            )

            total_output += total
            count += 1

        self.lbl_summary.config(text=f"Total Shifts: {count} | Total Output: {total_output} units")

    # ------------------- RESET PROGRESS -------------------
    def _reset_progress_labels(self):
        """Reset progress and target display."""
        self.lbl_job_target.config(text="Total Target: N/A")
        self.lbl_job_progress.config(text="Progress: 0%")
        self.progress_var.set(0)

    # ------------------- EXPORT TO CSV -------------------
    def _export_logs_to_csv(self):
        """Export current log data to CSV file."""
        if not self.logs_tree.get_children():
            messagebox.showwarning("No Data", "No logs available to export.")
            return

        try:
            os.makedirs("exports", exist_ok=True)
            filename = f"exports/Production_Report_{date.today()}.csv"

            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                headers = [col.upper() for col in self.logs_tree["columns"]]
                writer.writerow(headers)
                for row_id in self.logs_tree.get_children():
                    writer.writerow(self.logs_tree.item(row_id, "values"))

            messagebox.showinfo("Export Successful", f"Report exported to:\n{os.path.abspath(filename)}")
        except Exception as e:
            messagebox.showerror("Error", f"CSV export failed:\n{e}")

    # ------------------- EXPORT TO PDF -------------------
    def _export_logs_to_pdf(self):
        """Export the current log table to PDF."""
        if not self.logs_tree.get_children():
            messagebox.showwarning("No Data", "No logs available to export.")
            return

        try:
            os.makedirs("exports", exist_ok=True)
            filename = f"exports/Production_Report_{date.today()}.pdf"

            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            elements.append(Paragraph("📊 Production Logs Report", styles["Title"]))
            elements.append(Spacer(1, 12))

            info = Paragraph(
                f"Generated on: {date.today()}<br/>"
                f"Job Filter: {self.cmb_log_job.get() or 'All'} | "
                f"Staff: {self.cmb_log_staff.get() or 'All'} | "
                f"Date: {self.entry_log_date.get() or 'All'}",
                styles["Normal"]
            )
            elements.append(info)
            elements.append(Spacer(1, 12))

            headers = [col.upper() for col in self.logs_tree["columns"]]
            data = [headers] + [self.logs_tree.item(r, "values") for r in self.logs_tree.get_children()]

            table = Table(data)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(self.lbl_summary.cget("text"), styles["Italic"]))

            doc.build(elements)
            messagebox.showinfo("Export Successful", f"PDF report saved to:\n{os.path.abspath(filename)}")
        except Exception as e:
            messagebox.showerror("Error", f"PDF export failed:\n{e}")

