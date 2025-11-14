# reset_data.py
import json
from tkinter import messagebox

FILES_TO_CLEAR = [
    "data/jobs.json",
    "data/staff.json",
    "data/shift_output.json",
    "data/production.json"
]

def reset_all_data():
    """Clear all JSON files after user confirms."""
    
    confirm = messagebox.askyesno(
        "Confirm Reset",
        "⚠️ WARNING: This will permanently erase ALL system data.\n\n"
        "The following files will be reset:\n"
        "- jobs.json\n"
        "- staff.json\n"
        "- shift_output.json\n"
        "- production.json\n\n"
        "This action cannot be undone.\n\n"
        "Do you want to proceed?"
    )

    if not confirm:
        return False   # User cancelled

    try:
        for file_path in FILES_TO_CLEAR:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

        messagebox.showinfo("Reset Complete", "All data files have been cleared successfully.")
        return True

    except Exception as e:
        messagebox.showerror("Error", f"Failed to reset data:\n{e}")
        return False
