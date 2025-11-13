# ==============================================================
#  FILE: tab_view_jobs.py
#  PROJECT: UMAMCO Job Production Tracker
#  DESCRIPTION:
#     Handles the "View Jobs" tab — displays all saved jobs,
#     provides refresh and delete functionality.
# ==============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from storage.json_store import load_json, save_json


class ViewJobsTab:
    """Manages the View Jobs tab UI and behavior."""

    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self._build_view_jobs_tab()

    # ------------------- VIEW JOBS TAB -------------------
    def _build_view_jobs_tab(self):
        frame = self.frame

        ttk.Label(frame, text="All Jobs", font=("Segoe UI", 14, "bold")).pack(pady=10)

        columns = ("job_number", "customer_name", "product", "status")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=140, anchor="center")

        self.tree.pack(padx=10, pady=10, fill="x")

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="🔄 Refresh", command=self.load_jobs_to_treeview).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="❌ Delete", command=self.delete_selected_job).grid(row=0, column=1, padx=5)

        self.load_jobs_to_treeview()

    # ------------------- LOAD JOBS -------------------
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

    # ------------------- DELETE JOB -------------------
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
