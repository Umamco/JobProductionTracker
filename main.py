import sys, os
sys.path.append(os.path.dirname(__file__))

import tkinter as tk
from ui.main_window import JobProductionApp


def main():
    root = tk.Tk()
    app = JobProductionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
