# ==============================================================
#  FILE: tab_dashboard.py
#  PROJECT: UMAMCO Job Production Tracker
#  DESCRIPTION:
#     Handles the "Dashboard" tab that summarizes key production
#     metrics and displays charts for jobs, staff, and weekly trends.
# ==============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from storage.json_store import load_json


class DashboardTab:
    """Displays analytical summaries and charts on production data."""

    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self._build_dashboard_tab()

    # ------------------- BUILD DASHBOARD TAB -------------------
    def _build_dashboard_tab(self):
        frame = self.frame
        ttk.Label(frame, text="Production Dashboard", font=("Segoe UI", 14, "bold")).pack(pady=10)


        # --- Summary Section ---
        summary = ttk.LabelFrame(frame, text="Summary Statistics")
        summary.pack(fill="x", padx=10, pady=10)

        self.lbl_total_jobs = ttk.Label(summary, text="Total Jobs: 0", font=("Segoe UI", 10, "bold"))
        self.lbl_total_output = ttk.Label(summary, text="Total Output: 0 units", font=("Segoe UI", 10, "bold"))
        self.lbl_avg_progress = ttk.Label(summary, text="Average Progress: 0%", font=("Segoe UI", 10, "bold"))
        self.lbl_top_performer = ttk.Label(summary, text="Top Performer: N/A", font=("Segoe UI", 10, "bold"))

        labels = [
            self.lbl_total_jobs,
            self.lbl_total_output,
            self.lbl_avg_progress,
            self.lbl_top_performer,
        ]
        for i, lbl in enumerate(labels):
            lbl.grid(row=0, column=i, padx=10, pady=4)

        ttk.Button(summary, text="🔄 Refresh Dashboard", command=self._load_dashboard_data).grid(row=0, column=4, padx=10, pady=4)

        # --- Chart Section ---
        chart_frame = ttk.Frame(frame)
        chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.chart_job_frame = ttk.LabelFrame(chart_frame, text="Output by Job")
        self.chart_staff_frame = ttk.LabelFrame(chart_frame, text="Output by Staff")
        self.chart_weekly_frame = ttk.LabelFrame(chart_frame, text="Weekly Output Trend")

        for c in (self.chart_job_frame, self.chart_staff_frame, self.chart_weekly_frame):
            c.pack(fill="both", expand=True, padx=10, pady=6)

    # ------------------- HELPER: CLEAR CHART FRAMES -------------------
    def _clear_frames(self):
        for frame in (self.chart_job_frame, self.chart_staff_frame, self.chart_weekly_frame):
            for widget in frame.winfo_children():
                widget.destroy()

    # ------------------- HELPER: DISPLAY MESSAGE -------------------
    def _show_message(self, frame, text):
        ttk.Label(frame, text=text, font=("Segoe UI", 10, "italic"), foreground="gray").pack(pady=20)

    # ------------------- LOAD DASHBOARD DATA -------------------
    def _load_dashboard_data(self):
        """Load production summary and update dashboard charts."""
        data = load_json("data/shift_output.json", default=[])
        self._clear_frames()

        if not data:
            self._show_message(self.chart_job_frame, "No job data available")
            self._show_message(self.chart_staff_frame, "No staff data available")
            self._show_message(self.chart_weekly_frame, "No trend data available")
            for lbl in [self.lbl_total_jobs, self.lbl_total_output, self.lbl_avg_progress, self.lbl_top_performer]:
                lbl.config(text=lbl.cget("text").split(":")[0] + ": 0")
            return

        job_totals, staff_totals, weekly_totals = {}, {}, {}

        for rec in data:
            try:
                job = rec["job_number"]
                staff = rec["staff_name"]
                total = int(rec["total_output"])
                shift_date = rec.get("shift_date")
                week_num = datetime.strptime(shift_date, "%Y-%m-%d").isocalendar()[1]
            except Exception:
                continue

            job_totals[job] = job_totals.get(job, 0) + total
            staff_totals[staff] = staff_totals.get(staff, 0) + total
            weekly_totals[week_num] = weekly_totals.get(week_num, 0) + total

        # --- Update summary stats ---
        total_jobs = len(job_totals)
        total_output = sum(job_totals.values())
        avg_target = max(total_jobs * 20000, 1)  # Estimated base
        avg_progress = round((total_output / avg_target) * 100, 1)

        self.lbl_total_jobs.config(text=f"Total Jobs: {total_jobs}")
        self.lbl_total_output.config(text=f"Total Output: {total_output:,} units")
        self.lbl_avg_progress.config(text=f"Average Progress: {avg_progress}%")

        if staff_totals:
            top_name, top_value = max(staff_totals.items(), key=lambda x: x[1])
            self.lbl_top_performer.config(text=f"Top Performer: {top_name} ({top_value:,} units)")
        else:
            self.lbl_top_performer.config(text="Top Performer: N/A")

        # --- Chart 1: Output by Job ---
        if job_totals:
            fig1, ax1 = plt.subplots(figsize=(5.5, 3.2))
            ax1.bar(job_totals.keys(), job_totals.values(), color="steelblue")
            ax1.set_title("Total Output by Job")
            ax1.set_xlabel("Job Number")
            ax1.set_ylabel("Output (units)")
            ax1.grid(True, linestyle="--", alpha=0.5)
            canvas1 = FigureCanvasTkAgg(fig1, master=self.chart_job_frame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig1)
        else:
            self._show_message(self.chart_job_frame, "No job data available")

        # --- Chart 2: Output by Staff ---
        if staff_totals:
            fig2, ax2 = plt.subplots(figsize=(5.5, 3.2))
            ax2.barh(list(staff_totals.keys()), list(staff_totals.values()), color="seagreen")
            ax2.set_title("Total Output by Staff")
            ax2.set_xlabel("Output (units)")
            ax2.grid(True, linestyle="--", alpha=0.5)
            canvas2 = FigureCanvasTkAgg(fig2, master=self.chart_staff_frame)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig2)
        else:
            self._show_message(self.chart_staff_frame, "No staff data available")

        # --- Chart 3: Weekly Trend ---
        if weekly_totals:
            sorted_weeks = sorted(weekly_totals.items())
            weeks, outputs = zip(*sorted_weeks)
            fig3, ax3 = plt.subplots(figsize=(6, 3.2))
            ax3.plot(weeks, outputs, marker="o", color="mediumpurple", linewidth=2)
            ax3.set_title("Weekly Output Trend")
            ax3.set_xlabel("Week Number")
            ax3.set_ylabel("Total Output (units)")
            ax3.grid(True, linestyle="--", alpha=0.5)
            canvas3 = FigureCanvasTkAgg(fig3, master=self.chart_weekly_frame)
            canvas3.draw()
            canvas3.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig3)
        else:
            self._show_message(self.chart_weekly_frame, "No trend data available")



# ------------------- END OF FILE -------------------