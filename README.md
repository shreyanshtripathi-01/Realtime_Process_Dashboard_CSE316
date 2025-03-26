# Realtime_Process_Dashboard_CSE316 
# ACADEMIC TASK II  - Group Project

**Group Members:**  
*1. Shraddha Gupta - 12304195 <br>*
*2. Khushi Gupta - 12303149 <br>*
*3. Shreyansh Tripathi - 12324670 <br>*

---

## Project Overview

The **Real-Time Process Monitoring Dashboard** is a Python-based application that provides a graphical interface to monitor system metrics in real-time. 
This tool enables users to track **CPU usage**, **memory usage**, and **active processes** while offering features such as **visual alerts** and **process management**. 
Built with Python libraries like `psutil`, `Tkinter`, and `Matplotlib`, the dashboard is a practical tool for system administrators and developers.

---

## Features
- **Real-Time Monitoring:** Displays live updates of CPU, memory, and process details.
- **Interactive Dashboard:** Includes charts, tables, and alerts for an engaging user experience.
- **Process Management:** Allows process filtering, sorting, and interaction (e.g., termination and priority adjustment).
- **Historical Visualization:** Shows CPU usage trends in a line chart.
- **Proactive Alerts:** Provides visual indicators for CPU usage exceeding thresholds.

---

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/Real-Time-Process-Monitoring-Dashboard.git
   
2. **Navigate to the Project Directory:**
   cd Real-Time-Process-Monitoring-Dashboard
   
4. **Install Dependencies**
   pip install -r requirements.txt

5. **Run the Application:**
   python dashboard.py

---

## Change Log

**Day 1:**  
- Created the repository and initialized the project structure.  
- Added the base README.md file.

**Day 2:**  
- Integrated the `psutil` library to fetch system metrics (CPU, memory, processes).

**Day 3:**  
- Built the data collection module for periodic polling and normalization of metrics.

**Day 4:**  
- Designed the basic Tkinter window layout with placeholders for CPU and memory usage.

**Day 5:**  
- Implemented the process table using `ttk.Treeview` in Tkinter for displaying live process data.

**Day 6:**  
- Added dynamic updating for CPU and memory usage labels.  
- Established periodic refresh logic.

**Day 7:**  
- Introduced the CPU usage history chart using Matplotlib and integrated it into Tkinter.

**Day 8:**  
- Optimized data polling to handle exceptions (e.g., inaccessible processes).

**Day 9:**  
- Implemented alert functionality for CPU usage exceeding 80%.

**Day 10:**  
- Enhanced the dashboard layout and added styles for better readability.

**Day 11:**  
- Enabled sorting and filtering for process table columns (CPU %, Memory %).

**Day 12:**  
- Added tooltips and hover functionality for better user interaction.

**Day 13:**  
- Improved logging to store key events and system alerts for analysis.

**Day 14:**  
- Conducted code refactoring and modularized functions for better maintainability.

**Day 15:**  
- Finalized the project.  
- Added installation instructions and screenshots to README.md.

---

