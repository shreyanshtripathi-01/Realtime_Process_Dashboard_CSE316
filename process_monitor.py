import psutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
from collections import deque
import subprocess
from datetime import datetime

themes = {
    "dark": {"bg": "#1a1a1a", "fg": "#ffffff", "accent": "#64b5f6"},
    "light": {"bg": "#f8f9fa", "fg": "#2d3436", "accent": "#1a237e"}
}

# Custom styling
def setup_styles():
    style = ttk.Style()
    style.theme_use('clam')  # Use 'clam' theme as base
    
    # Configure colors
    style.configure("Treeview",
                   background="#2b2b2b",
                   foreground="white",
                   fieldbackground="#2b2b2b",
                   rowheight=25)
    
    style.configure("Treeview.Heading",
                   background="#1e1e1e",
                   foreground="white",
                   relief="flat")
    
    style.map("Treeview",
              background=[('selected', '#404040')],
              foreground=[('selected', 'white')])
    
    style.configure("Custom.TButton",
                   background="#ff5252",
                   foreground="white",
                   padding=10,
                   font=('Helvetica', 10, 'bold'))

class ProcessMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Monitor Dashboard")
        self.root.geometry("1000x800")
        self.setup_ui()

    def setup_ui(self):
        self.root.configure(bg='#1e1e1e')
        # Additional frame setup for header, info, graphs, and table

# Data collection
def get_process_data():
    processes = {}
    try:
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_info']):
            processes[proc.info['pid']] = {
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'state': proc.info['status'],
                'cpu': proc.info['cpu_percent'],
                'memory': proc.info['memory_info'].rss / 1024 / 1024  # MB
            }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
    return processes

# GUI setup
root = tk.Tk()
root.title("Process Monitor Dashboard")
root.geometry("1000x800")
root.configure(bg='#1e1e1e')

# Setup custom styles
setup_styles()

# Create main frames
header_frame = ttk.Frame(root)
header_frame.pack(fill="x", padx=10, pady=5)

title_label = ttk.Label(header_frame, 
                       text="Process Monitor Dashboard",
                       font=('Helvetica', 16, 'bold'),
                       foreground="white",
                       background="#1e1e1e")
title_label.pack(side="left", pady=10)

# System info frame
info_frame = ttk.Frame(root)
info_frame.pack(fill="x", padx=10, pady=5)

cpu_label = ttk.Label(info_frame,
                     text="CPU Usage:",
                     font=('Helvetica', 10),
                     foreground="white",
                     background="#1e1e1e")
cpu_label.pack(side="left", padx=5)

memory_label = ttk.Label(info_frame,
                        text="Memory Usage:",
                        font=('Helvetica', 10),
                        foreground="white",
                        background="#1e1e1e")
memory_label.pack(side="left", padx=20)

# Graph frame
graph_frame = ttk.Frame(root)
graph_frame.pack(fill="both", expand=True, padx=10, pady=5)

# CPU graph with dark theme
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, 3))
fig.patch.set_facecolor('#1e1e1e')
ax.set_facecolor('#2b2b2b')
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().pack(fill="both", expand=True)
cpu_history = deque(maxlen=50)

# Table frame
table_frame = ttk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=10, pady=5)

# Scrollbar for treeview
scrollbar = ttk.Scrollbar(table_frame)
scrollbar.pack(side="right", fill="y")

# Table for process info
tree = ttk.Treeview(table_frame,
                    columns=("PID", "Name", "State", "CPU %", "Memory (MB)"),
                    show="headings",
                    yscrollcommand=scrollbar.set)

scrollbar.config(command=tree.yview)

# Configure column widths and alignments
tree.heading("PID", text="PID")
tree.heading("Name", text="Name")
tree.heading("State", text="State")
tree.heading("CPU %", text="CPU %")
tree.heading("Memory (MB)", text="Memory (MB)")

tree.column("PID", width=80, anchor="center")
tree.column("Name", width=200, anchor="w")
tree.column("State", width=100, anchor="center")
tree.column("CPU %", width=100, anchor="center")
tree.column("Memory (MB)", width=120, anchor="center")

tree.pack(fill="both", expand=True)

# Control frame
control_frame = ttk.Frame(root)
control_frame.pack(fill="x", padx=10, pady=10)

# Kill process button with custom styling
kill_btn = ttk.Button(control_frame,
                      text="Kill Selected Process",
                      style="Custom.TButton")
kill_btn.pack(side="left", padx=5)

# Store existing processes
existing_processes = {}

def update_tree(processes):
    current_items = {tree.item(item)["values"][0]: item for item in tree.get_children()}
    
    for pid, proc in processes.items():
        values = (proc['pid'], proc['name'], proc['state'], f"{proc['cpu']:.1f}", f"{proc['memory']:.1f}")
        if pid in current_items:
            tree.item(current_items[pid], values=values)
            current_items.pop(pid)
        else:
            tree.insert("", "end", values=values)
    
    for item in current_items.values():
        tree.delete(item)

def update_system_info():
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    cpu_label.config(text=f"CPU Usage: {cpu_percent:.1f}%")
    memory_label.config(text=f"Memory Usage: {memory.percent:.1f}%")

def update_graph():
    ax.clear()
    ax.plot(list(cpu_history), label="CPU Usage (%)", color='#00ff00', linewidth=2)
    ax.legend(loc='upper right')
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3)
    ax.set_facecolor('#2b2b2b')
    canvas.draw()

def update_dashboard():
    global existing_processes
    while True:
        try:
            processes = get_process_data()
            root.after(0, update_tree, processes)
            root.after(0, update_system_info)
            cpu_history.append(psutil.cpu_percent())
            root.after(0, update_graph)
            existing_processes = processes
            time.sleep(2)
        except Exception as e:
            print(f"Error in update: {e}")
            time.sleep(1)

def kill_process():
    selected = tree.selection()
    if selected:
        pid = int(tree.item(selected[0])["values"][0])
        try:
            proc = psutil.Process(pid)
            proc.terminate()
        except psutil.NoSuchProcess:
            print(f"Process {pid} not found.")

kill_btn.config(command=kill_process)

# Start update thread
thread = threading.Thread(target=update_dashboard, daemon=True)
thread.start()

root.mainloop()








