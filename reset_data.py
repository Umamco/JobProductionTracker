
import json
import os

# List of JSON files data to clear when executed.
FILES_TO_CLEAR = [
    "data/jobs.json",
    "data/production.json",
    "data/staff.json",
    "data/shift_output.json"
]


# FUNCTION TO CLEAR DATA IN JSON FILES
def clear_json_files():
    for file_path in FILES_TO_CLEAR:
        # Ensure file exists; create if missing
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Overwrite file with empty JSON list
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
        
        print(f"Cleared: {file_path}")

if __name__ == "__main__":
    clear_json_files()
    print("\nAll data files cleared successfully.")

# SCRIPT TO RESET DATA IN SPECIFIED JSON FILES