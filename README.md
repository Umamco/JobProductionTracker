# 📦 UMAMCO Job Production Tracker  
A modular desktop application built with **Python** and **Tkinter** to help production teams track jobs, staff activity, hourly output, and performance analytics.  
This is the **public test build**, prepared with *empty data files* so each user can start fresh with their own entries.

---

## 🚀 Features

### **1. Job Management**
- Add new production jobs  
- Store customer details, product type, and stock requirements  
- Prevent duplicate job numbers  

### **2. Staff Management**
- Add, activate, or deactivate staff members  
- Staff list automatically refreshes across all tabs  

### **3. Shift & Output Tracking**
- Create production shifts  
- Auto-generate hourly targets  
- Enter actual hourly output and performance reasons  
- Visual performance indicators (Red, Yellow, Green, Blue)  
- Save full shift records to JSON  

### **4. Production Logs**
- Track job history and activities  
- Filter logs by job or staff  
- Auto-refreshing log view  

### **5. Analytics Dashboard**
- Displays output performance  
- Job counts & staff statistics  
- Graphs powered by Matplotlib  

---

## 📁 Project Structure
```
job_production_tracker/
│
├── main.py                     # Entry point of the application
├── main_window.py              # Main Tkinter window + tab controller
│
├── ui/                         # All user interface modules
│   ├── tab_add_job.py
│   ├── tab_view_jobs.py
│   ├── tab_shift.py
│   ├── tab_staff.py
│   ├── tab_logs.py
│   └── tab_dashboard.py
│
├── domain/                     # Dataclasses (application models)
│   └── models.py
│
├── storage/                    # Data access layer
│   └── json_store.py
│
├── data/                       # JSON data files (start empty)
│   ├── jobs.json
│   ├── staff.json
│   ├── shift_output.json
│   └── production.json
│
├── screenshots/                # App images used in README
│   ├── add_job.png
│   ├── view_jobs.png
│   ├── staff.png
│   ├── shift.png
│   ├── logs.png
│   └── dashboard.png
│
└── reset_data.py               # Wipes all JSON files (with confirmation)
```
---

## 📘 Note About `production.json`

The file **`production.json`** is included for future enhancements but is **not yet used in Version 1.0**.  
It will normally remain empty.

It is reserved for upcoming features in Version 1.1+, such as:

- Monthly or weekly production summaries  
- Full factory performance analytics  
- Aggregated job lifecycle data  
- High-level KPI tracking  
- Advanced reporting modules


---

## 📸 Screenshots

### **➕ Add Job**
![Add Job](screenshots/add_job.png)

### **📋 View Jobs**
![View Jobs](screenshots/view_jobs.png)

### **👥 Staff Management**
![Staff](screenshots/staff.png)

### **🕒 Shift & Output**
![Shift](screenshots/shift.png)

### **📊 Production Logs**
![Logs](screenshots/logs.png)

### **⚠️ Production Logs/Erase Button
![Logs](screenshots/erase.png)

### **📈 Dashboard**
![Dashboard](screenshots/dashboard.png)

### ** Dashboard Data Requirements **
![Requirements](screenshots/requirements.png)


### 🎬 Video Demonstration
[![Video Demo](screenshots/video_thumbnail.png)](https://1drv.ms/f/c/0bac7ab076f77651/IgBhtMIy_REJQ43lkuOqKo77ASmzxfG96bNaXD030FUKjeY?e=Acb6Wc)

---

## ⚙️ Installation & Running the App

### **1. Clone the Repository**
```bash
git clone https://github.com/Umamco/job_production_tracker.git
cd job_production_tracker
```

### **2. Create and Activate a Virtual Environment**
```bash
python -m venv venv
venv\Scripts\activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Run the Application**
```bash
python main.py
```
