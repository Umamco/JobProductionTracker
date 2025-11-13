# ==============================================================
#  FILE: main_window.py
#  PROJECT: UMAMCO Job Production Tracker
#  DESCRIPTION:
#     Main application window that orchestrates all modular tabs:
#     Add Job, View Jobs, Shift Tracking, Staff Management,
#     Production Logs, and Dashboard Analytics.
# ==============================================================

import tkinter as tk
from tkinter import ttk, messagebox

# ==== Import modular UI tabs ====
from ui.tab_add_job import AddJobTab
from ui.tab_view_jobs import ViewJobsTab
from ui.tab_shift import ShiftTab
from ui.tab_staff import StaffTab
from ui.tab_logs import LogsTab
from ui.tab_dashboard import DashboardTab


class JobProductionApp:
    """Main application window that hosts all modular tabs."""

    def __init__(self, root):
        self.root = root
        self.root.title("UMAMCO Job Production Tracker")
        self.root.geometry("900x720")
        self.root.resizable(True, True)

        # ---- Global Styles ----
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Red.Horizontal.TProgressbar", troughcolor="white", background="red")
        style.configure("Yellow.Horizontal.TProgressbar", troughcolor="white", background="orange")
        style.configure("Green.Horizontal.TProgressbar", troughcolor="white", background="green")

        # ---- Notebook (Tabs Container) ----
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        # ---- Initialize Each Tab ----
        self.tab_add_job = AddJobTab(self.notebook)
        self.tab_view_jobs = ViewJobsTab(self.notebook)
        self.tab_shift = ShiftTab(self.notebook)
        self.tab_staff = StaffTab(self.notebook)
        self.tab_logs = LogsTab(self.notebook)
        self.tab_dashboard = DashboardTab(self.notebook)

        # ---- Add Tabs to Notebook ----
        self.notebook.add(self.tab_add_job.frame, text="➕ Add Job", sticky="nsew")
        self.notebook.add(self.tab_view_jobs.frame, text="📋 View Jobs")
        self.notebook.add(self.tab_shift.frame, text="🕒 Shift & Output")
        self.notebook.add(self.tab_staff.frame, text="👥 Staff Management")
        self.notebook.add(self.tab_logs.frame, text="📊 Production Logs")
        self.notebook.add(self.tab_dashboard.frame, text="📈 Dashboard")

        # ---- Bind Tab Change Event ----
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        messagebox.showinfo("Welcome", "UMAMCO Job Production Tracker is ready.")

    # ------------------- EVENT: TAB CHANGED -------------------
    def _on_tab_changed(self, event):
        """Handle automatic refresh of data when switching between tabs."""
        selected = event.widget.tab(event.widget.select(), "text")

        try:
            if "Shift" in selected:
                # Reload staff and job data dynamically
                self.tab_shift._load_active_staff_into_combobox()
                self.tab_shift._load_job_numbers_into_combobox()

            elif "Staff" in selected:
                # Refresh staff table
                self.tab_staff._load_staff_into_tree()

            elif "Logs" in selected:
                # Reload filters for job/staff selection
                self.tab_logs._refresh_filters()
                self.tab_logs._load_logs_to_tree()

            elif "Dashboard" in selected:
                # Refresh dashboard statistics
                self.tab_dashboard._load_dashboard_data()

        except Exception as e:
            messagebox.showerror("Error", f"Tab refresh failed:\n{e}")


# ------------------- RUN APPLICATION -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = JobProductionApp(root)
    root.mainloop()
