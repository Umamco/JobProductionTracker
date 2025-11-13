# ==============================================================
#  FILE: tab_add_job.py
#  PROJECT: UMAMCO Job Production Tracker
#  DESCRIPTION:
#     Handles the "Add Job" tab — allows users to create and save
#     new production jobs with customer details and stock info.
# ==============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import asdict
from domain.models import Job, StockItem
from storage.json_store import load_json, save_json


class AddJobTab:
    """Handles creation of new production job records."""

    def __init__(self, parent, refresh_callback=None):
        """
        Initialize the tab.
        :param parent: parent notebook frame
        :param refresh_callback: optional callback to refresh job lists
        """
        
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True)

        self.refresh_callback = refresh_callback
        self._build_add_job_tab()

    # ------------------- BUILD TAB -------------------
    def _build_add_job_tab(self):
        """Create input fields and buttons for adding new jobs."""
        frame = self.frame

        ttk.Label(
            frame, text="Add New Production Job", font=("Segoe UI", 14, "bold")
        ).pack(pady=10)

        self.entry_job_number = self._add_entry(frame, "Job Number")
        self.entry_customer_name = self._add_entry(frame, "Customer Name")
        self.entry_product = self._add_entry(frame, "Product")
        self.entry_stock_name = self._add_entry(frame, "Stock Name")
        self.entry_stock_quantity = self._add_entry(frame, "Stock Quantity")

        ttk.Button(frame, text="💾 Save Job", command=self._save_job).pack(pady=10)
        ttk.Button(frame, text="🧹 Clear Fields", command=self._clear_fields).pack(pady=5)

        self.entry_job_number.focus_set()

    # ------------------- HELPER: ENTRY CREATION -------------------
    def _add_entry(self, parent, label_text):
        """Helper to create a label + entry pair."""
        ttk.Label(parent, text=label_text).pack(pady=(5, 0))
        entry = ttk.Entry(parent, width=40)
        entry.pack(pady=2)
        entry.bind("<FocusIn>", lambda e: entry.selection_clear())  # ✅ ensures typing works instantly
        return entry

    # ------------------- CLEAR FIELDS -------------------
    def _clear_fields(self):
        """Clear all input fields."""
        for e in [
            self.entry_job_number,
            self.entry_customer_name,
            self.entry_product,
            self.entry_stock_name,
            self.entry_stock_quantity,
        ]:
            e.delete(0, tk.END)

    # ------------------- SAVE JOB -------------------
    def _save_job(self):
        """Validate and save a new job record."""
        job_number = self.entry_job_number.get().upper().strip()
        customer_name = self.entry_customer_name.get().title().strip()
        product = self.entry_product.get().title().strip()
        stock_name = self.entry_stock_name.get().title().strip()
        stock_quantity = self.entry_stock_quantity.get().strip()

        # --- Validation ---
        if not (job_number and customer_name and product and stock_name and stock_quantity):
            messagebox.showwarning("Missing Fields", "All fields must be filled!")
            return

        try:
            stock_quantity = int(stock_quantity)
        except ValueError:
            messagebox.showwarning("Invalid Quantity", "Stock quantity must be a number.")
            return

        jobs = load_json("data/jobs.json", default=[])

        if any(j["job_number"] == job_number for j in jobs):
            messagebox.showwarning("Duplicate", f"Job {job_number} already exists!")
            return

        # --- Create job record ---
        new_job = Job(
            job_number=job_number,
            customer_name=customer_name,
            product=product,
            stocks=[StockItem(name=stock_name, quantity=stock_quantity)],
        )

        jobs.append(asdict(new_job))
        save_json("data/jobs.json", jobs)

        messagebox.showinfo("Success", f"✅ Job {job_number} saved successfully!")
        self._clear_fields()

        # Refresh job list if applicable
        if self.refresh_callback:
            self.refresh_callback()
