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

# Modern Theme Configurations
themes = {
    "dark": {
        "bg": "#1a1a1a",
        "fg": "#ffffff",
        "accent": "#64b5f6",
        "accent_hover": "#42a5f5",
        "warning": "#ff6b6b",
        "success": "#2ecc71",
        "tree_bg": "#2d2d2d",
        "tree_fg": "#ffffff",
        "tree_field_bg": "#2d2d2d",
        "tree_head_bg": "#1a1a1a",
        "tree_sel_bg": "#3d3d3d",
        "btn_bg": "#64b5f6",
        "btn_fg": "#ffffff",
        "plt_style": "dark_background",
        "fig_bg": "#1a1a1a",
        "ax_bg": "#2d2d2d",
        "status_bg": "#2d2d2d",
        "system_bg": "#34495e",
        "section_bg": "#2d2d2d",
        "border": "#3d3d3d",
        "text_secondary": "#b3b3b3",
        "graph_colors": ["#64b5f6", "#ff6b6b", "#2ecc71", "#f1c40f", "#9b59b6", "#e67e22"]
    },
    "light": {
        "bg": "#f8f9fa",
        "fg": "#2d3436",
        "accent": "#1a237e",
        "accent_hover": "#283593",
        "warning": "#ff7675",
        "success": "#00b894",
        "tree_bg": "#ffffff",
        "tree_fg": "#2d3436",
        "tree_field_bg": "#ffffff",
        "tree_head_bg": "#f1f2f6",
        "tree_sel_bg": "#dfe6e9",
        "btn_bg": "#1a237e",
        "btn_fg": "#ffffff",
        "plt_style": "default",
        "fig_bg": "#ffffff",
        "ax_bg": "#f8f9fa",
        "status_bg": "#f1f2f6",
        "system_bg": "#74b9ff",
        "section_bg": "#f1f2f6",
        "border": "#dfe6e9",
        "text_secondary": "#636e72",
        "graph_colors": ["#1a237e", "#ff7675", "#00b894", "#fdcb6e", "#6c5ce7", "#e17055"]
    }
}

def setup_styles(theme="light"):
    style = ttk.Style()
    style.theme_use('clam')
    t = themes[theme]
    
    # Base styles
    style.configure(".", background=t["bg"], foreground=t["fg"])
    style.configure("TFrame", background=t["bg"])
    style.configure("TLabel", background=t["bg"], foreground=t["fg"])
    
    # Treeview styles
    style.configure("Treeview", 
                  background=t["tree_bg"],
                  foreground=t["tree_fg"],
                  fieldbackground=t["tree_field_bg"],
                  rowheight=35,
                  font=('Segoe UI', 11))
    style.configure("Treeview.Heading", 
                  background=t["tree_head_bg"],
                  foreground=t["fg"],
                  font=('Segoe UI', 11, 'bold'),
                  padding=10,
                  relief="flat")
    style.map("Treeview", 
             background=[('selected', t["tree_sel_bg"])],
             foreground=[('selected', t["fg"])])
    
    # Button styles
    style.configure("Accent.TButton", 
                  background=t["accent"],
                  foreground=t["btn_fg"],
                  font=('Segoe UI', 11, 'bold'),
                  padding=12,
                  borderwidth=0,
                  relief="flat")
    style.map("Accent.TButton",
             background=[('active', t["accent_hover"]), ('!disabled', t["accent"])])
    
    style.configure("Rounded.TButton",
                  background=t["accent"],
                  foreground=t["btn_fg"],
                  font=('Segoe UI', 11, 'bold'),
                  padding=12,
                  borderwidth=0,
                  relief="flat")
    style.map("Rounded.TButton",
             background=[('active', t["accent_hover"]), ('!disabled', t["accent"])])
    
    # Section headers
    style.configure("Section.TLabel",
                  background=t["section_bg"],
                  foreground=t["fg"],
                  font=('Segoe UI', 13, 'bold'),
                  padding=(15, 10, 15, 10),
                  relief="flat")
    
    # Status bar
    style.configure("Status.TLabel",
                  background=t["status_bg"],
                  foreground=t["text_secondary"],
                  font=('Segoe UI', 11),
                  padding=(15, 10),
                  relief="flat")
    
    # Info labels
    style.configure("Info.TLabel",
                  background=t["bg"],
                  foreground=t["text_secondary"],
                  font=('Segoe UI', 11),
                  padding=(5, 5))

class ProcessMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Process Monitor")
        self.root.geometry("1300x850")
        
        # Initialize variables
        self.current_theme = "light"
        self.existing_processes = {}
        self.cpu_history_overall = deque(maxlen=50)
        self.cpu_history_per_core = [deque(maxlen=50) for _ in range(psutil.cpu_count())]
        self.mem_history = deque(maxlen=50)
        self.sort_reverse = {"PID": False, "Name": False, "State": False, "CPU %": False, "Memory (MB)": False}
        
        # Variables for filters and controls
        self.cpu_filter_var = tk.StringVar(value="All")
        self.mem_filter_var = tk.StringVar(value="All")
        self.user_filter_var = tk.StringVar(value="All")
        self.graph_mode_var = tk.StringVar(value="overall")
        self.core_var = tk.StringVar(value="All")
        self.refresh_var = tk.DoubleVar(value=2.0)
        self.status_var = tk.StringVar()
        
        self.setup_ui()
        self.start_monitor_thread()
    
    def setup_ui(self):
        self.root.configure(bg=themes[self.current_theme]["bg"])
        setup_styles(self.current_theme)
        
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.setup_header()
        self.setup_filters()
        self.setup_system_info()
        self.setup_graphs()
        self.setup_process_table()
        self.setup_status_bar()
    
    def setup_header(self):
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 15))
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side='left')
        
        self.title_label = ttk.Label(
            title_frame, 
            text="⚡ PROCESS MONITOR DASHBOARD",
            font=('Segoe UI', 20, 'bold'),
            foreground=themes[self.current_theme]["accent"]
        )
        self.title_label.pack(side='left')
        
        self.theme_btn = tk.Button(
            header_frame,
            text="☀️" if self.current_theme == "dark" else "🌙",
            command=self.toggle_theme,
            bg=themes[self.current_theme]["accent"],
            fg=themes[self.current_theme]["btn_fg"],
            font=('Segoe UI', 11, 'bold'),
            relief="flat",
            width=3,
            cursor="hand2"
        )
        self.theme_btn.pack(side='right', padx=5)
        
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side='right', padx=10)
        
        tk.Button(controls_frame, text="📊 Overall",
                 bg=themes[self.current_theme]["accent"],
                 fg=themes[self.current_theme]["btn_fg"],
                 font=('Segoe UI', 11, 'bold'),
                 relief="flat",
                 cursor="hand2",
                 command=lambda: [self.graph_mode_var.set("overall"), self.update_graph()]).pack(side='left', padx=5)
        
        tk.Button(controls_frame, text="🔢 Per-Core",
                 bg=themes[self.current_theme]["accent"],
                 fg=themes[self.current_theme]["btn_fg"],
                 font=('Segoe UI', 11, 'bold'),
                 relief="flat",
                 cursor="hand2",
                 command=lambda: [self.graph_mode_var.set("per-core"), self.update_graph()]).pack(side='left', padx=5)
        
        core_options = ["All"] + [f"Core {i}" for i in range(psutil.cpu_count())]
        ttk.OptionMenu(controls_frame, self.core_var, "All", *core_options,
                      command=lambda _: self.update_graph()).pack(side='left', padx=5)
        
        refresh_options = ["1.0", "2.0", "3.0", "5.0"]
        ttk.OptionMenu(controls_frame, self.refresh_var, "2.0", *refresh_options,
                      command=lambda val: self.refresh_var.set(float(val))).pack(side='left', padx=5)
    
    def setup_system_info(self):
        info_frame = ttk.Frame(self.main_frame)
        info_frame.pack(fill='x', pady=(0, 15))
        
        cpu_frame = ttk.Frame(info_frame)
        cpu_frame.pack(side='left', padx=15)
        ttk.Label(cpu_frame, text="💻", font=('Segoe UI', 12)).pack(side='left', padx=(0, 5))
        self.cpu_label = ttk.Label(cpu_frame, text="CPU Usage: 0%", style="Info.TLabel")
        self.cpu_label.pack(side='left')
        
        mem_frame = ttk.Frame(info_frame)
        mem_frame.pack(side='left', padx=15)
        ttk.Label(mem_frame, text="💾", font=('Segoe UI', 12)).pack(side='left', padx=(0, 5))
        self.memory_label = ttk.Label(mem_frame, text="Memory Usage: 0%", style="Info.TLabel")
        self.memory_label.pack(side='left')
    
    def setup_filters(self):
        filter_section = ttk.Label(
            self.main_frame,
            text="PROCESS FILTERS",
            style="Section.TLabel"
        )
        filter_section.pack(fill='x', pady=(0, 5))
        
        filter_frame = ttk.Frame(self.main_frame)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        # Left side filters
        left_frame = ttk.Frame(filter_frame)
        left_frame.pack(side='left', padx=10)
        
        ttk.Label(left_frame, text="CPU ≥").pack(side="left", padx=(0, 5))
        ttk.OptionMenu(left_frame, self.cpu_filter_var, "All", "All", "10", "25", "50", "75",
                      command=lambda _: self.apply_filters()).pack(side="left")
        
        ttk.Label(left_frame, text="MB ≥").pack(side="left", padx=(10, 5))
        ttk.OptionMenu(left_frame, self.mem_filter_var, "All", "All", "50", "100", "250", "500",
                      command=lambda _: self.apply_filters()).pack(side="left")
        
        ttk.Label(left_frame, text="Type:").pack(side="left", padx=(10, 5))
        ttk.OptionMenu(left_frame, self.user_filter_var, "All", "All", "System", "User",
                      command=lambda _: self.apply_filters()).pack(side="left")
        
        tk.Button(left_frame, text="Clear Filters",
                 bg=themes[self.current_theme]["accent"],
                 fg="white",
                 font=('Segoe UI', 11, 'bold'),
                 relief="flat",
                 cursor="hand2",
                 command=self.clear_filters).pack(side='left', padx=10)
        
        # Right side action buttons
        right_frame = ttk.Frame(filter_frame)
        right_frame.pack(side='right', padx=10)
        
        tk.Button(right_frame, text="📥 Export Data",
                 bg=themes[self.current_theme]["accent"],
                 fg="white",
                 font=('Segoe UI', 11, 'bold'),
                 relief="flat",
                 cursor="hand2",
                 command=self.export_data).pack(side='right', padx=5)
        
        tk.Button(right_frame, text="▶️ Start Process",
                 bg="#4CAF50",
                 fg="white",
                 font=('Segoe UI', 11, 'bold'),
                 relief="flat",
                 cursor="hand2",
                 command=self.start_new_process).pack(side='right', padx=5)
        
        tk.Button(right_frame, text="❌ Kill Process",
                 bg="#ff4444",
                 fg="white",
                 font=('Segoe UI', 11, 'bold'),
                 relief="flat",
                 cursor="hand2",
                 command=self.kill_process).pack(side='right', padx=5)
    
    def setup_graphs(self):
        graph_section = ttk.Label(
            self.main_frame,
            text="SYSTEM USAGE",
            style="Section.TLabel"
        )
        graph_section.pack(fill='x', pady=(0, 5))
        
        graph_frame = ttk.Frame(self.main_frame)
        graph_frame.pack(fill='x', pady=(0, 10))
        
        plt.style.use(themes[self.current_theme]["plt_style"])
        self.fig, (self.ax_cpu, self.ax_mem) = plt.subplots(1, 2, figsize=(12, 3))
        self.fig.patch.set_facecolor(themes[self.current_theme]["fig_bg"])
        self.ax_cpu.set_facecolor(themes[self.current_theme]["ax_bg"])
        self.ax_mem.set_facecolor(themes[self.current_theme]["ax_bg"])
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill='x', expand=True)
    
    def setup_process_table(self):
        table_section = ttk.Label(
            self.main_frame,
            text="RUNNING PROCESSES",
            style="Section.TLabel"
        )
        table_section.pack(fill='x', pady=(0, 5))
        
        table_frame = ttk.Frame(self.main_frame)
        table_frame.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.tree = ttk.Treeview(table_frame,
                                columns=("PID", "Name", "State", "CPU %", "Memory (MB)"),
                                show="headings",
                                yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.tree.yview)
        
        self.tree.column("PID", width=120, anchor="center")
        self.tree.column("Name", width=300, anchor="w")
        self.tree.column("State", width=150, anchor="center")
        self.tree.column("CPU %", width=120, anchor="center")
        self.tree.column("Memory (MB)", width=150, anchor="center")
        
        for col in ("PID", "Name", "State", "CPU %", "Memory (MB)"):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c, self.sort_reverse[c]))
        
        self.tree.pack(fill='both', expand=True)
        
        self.tree.tag_configure("high_cpu", background="#ff6666" if self.current_theme == "dark" else "#ff9999")
        self.tree.tag_configure("high_mem", background="#ffcc66" if self.current_theme == "dark" else "#ffe066")
        self.tree.tag_configure("system_process", background=themes[self.current_theme]["system_bg"])
        
        self.tree.bind("<Double-1>", self.show_process_details)
    
    def setup_status_bar(self):
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill='x', pady=(5, 0))
        
        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            style="Status.TLabel"
        )
        self.status_label.pack(fill='x')
    
    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.root.configure(bg=themes[self.current_theme]["bg"])
        setup_styles(self.current_theme)
        
        self.theme_btn.configure(
            text="☀️" if self.current_theme == "dark" else "🌙",
            bg=themes[self.current_theme]["accent"],
            fg=themes[self.current_theme]["btn_fg"]
        )
        
        self.title_label.configure(foreground=themes[self.current_theme]["accent"])
        
        def update_button_colors(widget):
            if isinstance(widget, tk.Button):
                if widget.cget('bg') not in ["#ff4444", "#4CAF50"]:
                    widget.configure(
                        bg=themes[self.current_theme]["accent"],
                        fg=themes[self.current_theme]["btn_fg"]
                    )
            for child in widget.winfo_children():
                update_button_colors(child)
        
        update_button_colors(self.main_frame)
        
        self.tree.tag_configure("high_cpu", background="#ff6666" if self.current_theme == "dark" else "#ff9999")
        self.tree.tag_configure("high_mem", background="#ffcc66" if self.current_theme == "dark" else "#ffe066")
        self.tree.tag_configure("system_process", background=themes[self.current_theme]["system_bg"])
        
        plt.style.use(themes[self.current_theme]["plt_style"])
        self.fig.patch.set_facecolor(themes[self.current_theme]["fig_bg"])
        self.ax_cpu.set_facecolor(themes[self.current_theme]["ax_bg"])
        self.ax_mem.set_facecolor(themes[self.current_theme]["ax_bg"])
        
        self.update_graph()
    
    def get_process_data(self):
        processes = {}
        try:
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 
                                           'memory_info', 'username', 'create_time']):
                info = proc.info
                username = info['username'] or "Unknown"
                processes[info['pid']] = {
                    'pid': info['pid'],
                    'name': info['name'],
                    'state': info['status'],
                    'cpu': info['cpu_percent'],
                    'memory': info['memory_info'].rss / 1024 / 1024,
                    'username': username,
                    'create_time': time.ctime(info['create_time']),
                    'is_system': username in ['SYSTEM', 'root', 'NT AUTHORITY\\SYSTEM']
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        return processes
    
    def kill_process(self):
        selected = self.tree.selection()
        if selected:
            pid = int(self.tree.item(selected[0])["values"][0])
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                messagebox.showinfo("Success", f"Process {pid} terminated.")
            except psutil.NoSuchProcess:
                messagebox.showerror("Error", f"Process {pid} not found.")
    
    def start_new_process(self):
        cmd = tk.simpledialog.askstring("Start Process", "Enter command (e.g., notepad, python script.py):")
        if cmd:
            try:
                subprocess.Popen(cmd, shell=True)
                messagebox.showinfo("Success", f"Started process: {cmd}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start process: {e}")
    
    def set_process_priority(self):
        selected = self.tree.selection()
        if selected:
            pid = int(self.tree.item(selected[0])["values"][0])
            try:
                priority = tk.simpledialog.askinteger("Set Priority", 
                                                    "Enter nice value (-20 high to 19 low):",
                                                    minvalue=-20, maxvalue=19)
                if priority is not None:
                    proc = psutil.Process(pid)
                    proc.nice(priority)
                    messagebox.showinfo("Success", f"Priority set for process {pid}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to set priority: {e}")
    
    def export_data(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("PID,Name,State,CPU %,Memory (MB),Username,Type,Created\n")
                    for proc in self.existing_processes.values():
                        proc_type = "System" if proc['is_system'] else "User"
                        f.write(f"{proc['pid']},{proc['name']},{proc['state']},"
                               f"{proc['cpu']:.1f},{proc['memory']:.1f},"
                               f"{proc['username']},{proc_type},{proc['create_time']}\n")
                messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def apply_filters(self):
        cpu_threshold = self.cpu_filter_var.get()
        mem_threshold = self.mem_filter_var.get()
        user_type = self.user_filter_var.get()
        
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            proc = self.existing_processes.get(int(values[0]), {})
            
            cpu_ok = (cpu_threshold == "All") or (float(values[3]) >= float(cpu_threshold))
            mem_ok = (mem_threshold == "All") or (float(values[4]) >= float(mem_threshold))
            user_ok = (user_type == "All") or \
                     (user_type == "System" and proc.get('is_system', False)) or \
                     (user_type == "User" and not proc.get('is_system', True))
            
            if cpu_ok and mem_ok and user_ok:
                self.tree.item(item, tags=())
            else:
                self.tree.item(item, tags=('hidden',))
    
    def clear_filters(self):
        self.cpu_filter_var.set("All")
        self.mem_filter_var.set("All")
        self.user_filter_var.set("All")
        self.apply_filters()
    
    def show_process_details(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            pid = int(self.tree.item(item)["values"][0])
            proc = self.existing_processes.get(pid)
            if proc:
                details = (
                    f"PID: {pid}\n"
                    f"Name: {proc['name']}\n"
                    f"Status: {proc['state']}\n"
                    f"CPU %: {proc['cpu']:.1f}\n"
                    f"Memory: {proc['memory']:.1f} MB\n"
                    f"Username: {proc['username']}\n"
                    f"Type: {'System' if proc['is_system'] else 'User'}\n"
                    f"Created: {proc['create_time']}"
                )
                messagebox.showinfo("Process Details", details)
    
    def sort_treeview(self, col, reverse):
        data = [(self.tree.set(item, col), item) for item in self.tree.get_children()]
        
        self.sort_reverse[col] = not self.sort_reverse[col]
        
        if col in ["CPU %", "Memory (MB)"]:
            data.sort(key=lambda x: float(x[0]), reverse=self.sort_reverse[col])
        else:
            data.sort(key=lambda x: x[0].lower(), reverse=self.sort_reverse[col])
        
        for index, (val, item) in enumerate(data):
            self.tree.move(item, '', index)
        
        for column in self.tree["columns"]:
            if column == col:
                arrow = "↓" if self.sort_reverse[col] else "↑"
                self.tree.heading(column, text=f"{column} {arrow}")
            else:
                self.tree.heading(column, text=column)
    
    def update_tree(self, processes):
        current_items = {self.tree.item(item)["values"][0]: item for item in self.tree.get_children()}
        
        for pid, proc in processes.items():
            tags = []
            if proc['cpu'] > 50:
                tags.append("high_cpu")
            if proc['memory'] > 100:
                tags.append("high_mem")
            if proc['is_system']:
                tags.append("system_process")
                
            values = (proc['pid'], proc['name'], proc['state'], 
                     f"{proc['cpu']:.1f}", f"{proc['memory']:.1f}")
                    
            if pid in current_items:
                self.tree.item(current_items[pid], values=values, tags=tags)
                current_items.pop(pid)
            else:
                self.tree.insert("", "end", values=values, tags=tags)
        
        for item in current_items.values():
            self.tree.delete(item)
        
        self.apply_filters()
        self.tree.yview_moveto(1.0)
    
    def update_system_info(self):
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        self.cpu_label.config(text=f"CPU Usage: {cpu_percent:.1f}%")
        self.memory_label.config(text=f"Memory Usage: {memory.percent:.1f}%")
    
    def update_graph(self):
        self.ax_cpu.clear()
        self.ax_mem.clear()
        
        colors = {
            'low': '#2ecc71',
            'medium': '#f1c40f',
            'high': '#e74c3c'
        }
        
        fill_colors = {
            'low': '#a8e6cf',
            'medium': '#f8e58c',
            'high': '#f3a7a7'
        }
        
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        memory = psutil.virtual_memory()
        
        if self.graph_mode_var.get() == "overall":
            cpu_data = list(self.cpu_history_overall)
            if cpu_data:
                line_color = colors['low'] if cpu_data[-1] <= 45 else \
                            colors['medium'] if cpu_data[-1] <= 75 else \
                            colors['high']
                fill_color = fill_colors['low'] if cpu_data[-1] <= 45 else \
                            fill_colors['medium'] if cpu_data[-1] <= 75 else \
                            fill_colors['high']
                self.ax_cpu.plot(cpu_data, label=f"Overall CPU Usage\n{cpu_count} Cores @ {cpu_freq.current:.1f}MHz",
                               color=line_color, linewidth=2)
                self.ax_cpu.fill_between(range(len(cpu_data)), cpu_data, alpha=0.3, color=fill_color)
        elif self.graph_mode_var.get() == "per-core":
            if self.core_var.get() == "All":
                for i, history in enumerate(self.cpu_history_per_core):
                    core_data = list(history)
                    if core_data:
                        line_color = colors['low'] if core_data[-1] <= 45 else \
                                    colors['medium'] if core_data[-1] <= 75 else \
                                    colors['high']
                        fill_color = fill_colors['low'] if core_data[-1] <= 45 else \
                                    fill_colors['medium'] if core_data[-1] <= 75 else \
                                    fill_colors['high']
                        self.ax_cpu.plot(core_data, label=f"Core {i}", 
                                       color=line_color, linewidth=1.5)
                        self.ax_cpu.fill_between(range(len(core_data)), core_data, alpha=0.2, color=fill_color)
            else:
                core_idx = int(self.core_var.get().split()[1])
                core_data = list(self.cpu_history_per_core[core_idx])
                if core_data:
                    line_color = colors['low'] if core_data[-1] <= 45 else \
                                colors['medium'] if core_data[-1] <= 75 else \
                                colors['high']
                    fill_color = fill_colors['low'] if core_data[-1] <= 45 else \
                                fill_colors['medium'] if core_data[-1] <= 75 else \
                                fill_colors['high']
                    self.ax_cpu.plot(core_data, label=f"Core {core_idx}",
                                   color=line_color, linewidth=2)
                    self.ax_cpu.fill_between(range(len(core_data)), core_data, alpha=0.3, color=fill_color)
        
        mem_data = list(self.mem_history)
        if mem_data:
            mem_color = colors['low'] if mem_data[-1] <= 45 else \
                       colors['medium'] if mem_data[-1] <= 75 else \
                       colors['high']
            mem_fill_color = fill_colors['low'] if mem_data[-1] <= 45 else \
                           fill_colors['medium'] if mem_data[-1] <= 75 else \
                           fill_colors['high']
            self.ax_mem.plot(mem_data, label=f"Memory Usage\n{memory.used/1024/1024/1024:.1f}GB / {memory.total/1024/1024/1024:.1f}GB", 
                            color=mem_color, linewidth=2)
            self.ax_mem.fill_between(range(len(mem_data)), mem_data, alpha=0.3, color=mem_fill_color)
        
        self.ax_cpu.legend(loc='upper right', framealpha=0.8)
        self.ax_cpu.set_ylim(0, 100)
        self.ax_cpu.set_title("CPU Usage", color=themes[self.current_theme]["fg"], pad=15)
        self.ax_cpu.set_ylabel("Usage (%)", color=themes[self.current_theme]["fg"])
        self.ax_cpu.grid(True, alpha=0.2, linestyle='--')
        self.ax_cpu.set_facecolor(themes[self.current_theme]["ax_bg"])
        
        self.ax_mem.legend(loc='upper right', framealpha=0.8)
        self.ax_mem.set_ylim(0, 100)
        self.ax_mem.set_title("Memory Usage", color=themes[self.current_theme]["fg"], pad=15)
        self.ax_mem.set_ylabel("Usage (%)", color=themes[self.current_theme]["fg"])
        self.ax_mem.grid(True, alpha=0.2, linestyle='--')
        self.ax_mem.set_facecolor(themes[self.current_theme]["ax_bg"])
        
        self.canvas.draw()
    
    def update_dashboard(self):
        while True:
            try:
                start_time = time.time()
                processes = self.get_process_data()
                self.root.after(0, self.update_tree, processes)
                self.root.after(0, self.update_system_info)
                
                cpu_overall = psutil.cpu_percent()
                cpu_per_core = psutil.cpu_percent(percpu=True)
                self.cpu_history_overall.append(cpu_overall)
                for i, cpu in enumerate(cpu_per_core):
                    self.cpu_history_per_core[i].append(cpu)
                
                mem_percent = psutil.virtual_memory().percent
                self.mem_history.append(mem_percent)
                
                self.root.after(0, self.update_graph)
                self.existing_processes = processes
                
                update_time = datetime.now().strftime("%H:%M:%S")
                self.root.after(0, self.status_var.set, 
                              f"Last Updated: {update_time} | Processes: {len(processes)} | "
                              f"CPU: {cpu_overall:.1f}% | Memory: {mem_percent:.1f}%")
                
                elapsed = time.time() - start_time
                sleep_time = max(0, self.refresh_var.get() - elapsed)
                time.sleep(sleep_time)
                
            except Exception as e:
                error_time = datetime.now().strftime("%H:%M:%S")
                self.root.after(0, self.status_var.set, 
                              f"Error at {error_time}: {str(e)} - Retrying...")
                time.sleep(1)
    
    def start_monitor_thread(self):
        self.monitor_thread = threading.Thread(
            target=self.update_dashboard,
            daemon=True
        )
        self.monitor_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessMonitor(root)
    root.mainloop()
