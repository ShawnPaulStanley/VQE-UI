import tkinter as tk
from tkinter import ttk, Canvas, Frame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib.patches as patches
import sys
import os

class PixelFont:
    """Clean font helper"""
    @staticmethod
    def get_clean_font(size=12, weight="normal"):
        # Use clean, modern fonts
        return ("Segoe UI", size, weight)

class VQEDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("VQE Quantum Simulator")
        self.root.geometry("1400x900")
        self.root.configure(bg='#FFFFFF')
        
        # Set minimum size
        self.root.minsize(1200, 800)
        
        # Clean modern color scheme
        self.colors = {
            'bg': '#FFFFFF',
            'fg': '#2C3E50',
            'primary': '#3498DB',
            'secondary': '#ECF0F1',
            'accent': '#E74C3C',
            'text': '#34495E',
            'light_gray': '#F8F9FA',
            'border': '#BDC3C7'
        }
        
        # Configure matplotlib for clean white theme
        plt.style.use('default')
        
        # Data storage for real-time updates
        self.data_storage = {
            'normal_vqe': {'iterations': [], 'energy': []},
            'vqe_uccsd_hybrid': {'iterations': [], 'energy': []},
            'vqe_uccsd_hybrid_zne': {'iterations': [], 'energy': []}
        }
        
        # Current iteration counter
        self.current_iteration = 0
        
        # Simulation control
        self.simulation_stopped = False
        
        # Convergence tracking
        self.convergence_threshold = 0.001  # Energy difference threshold for convergence
        self.convergence_window = 5  # Number of points to check for convergence
        self.converged_methods = set()  # Track which methods have converged
        
        self.setup_ui()
        
        # Start real-time data generation
        self.start_data_generation()
        
    def setup_ui(self):
        """Setup the main UI layout"""
        # Top navbar with more padding
        self.create_navbar()
        
        # Main container with generous spacing
        main_frame = Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Sidebar and content with better spacing
        self.create_sidebar(main_frame)
        self.create_main_content(main_frame)
        
        # Status bar
        self.create_status_bar()
        
        # Footer with more space
        self.create_footer()
        
    def create_navbar(self):
        """Create the top navigation bar"""
        navbar = Frame(self.root, bg=self.colors['bg'], height=80)
        navbar.pack(fill=tk.X, padx=30, pady=(20, 10))
        navbar.pack_propagate(False)
        
        title_label = tk.Label(
            navbar,
            text="VQE Quantum Simulator",
            font=PixelFont.get_clean_font(24, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            anchor='center'
        )
        title_label.pack(expand=True, fill=tk.BOTH)
        
        # Add subtle bottom border
        border = Frame(navbar, bg=self.colors['border'], height=1)
        border.pack(fill=tk.X, side=tk.BOTTOM)
        
    def create_sidebar(self, parent):
        """Create the left sidebar with clean buttons"""
        sidebar = Frame(parent, bg=self.colors['light_gray'], width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 30))
        sidebar.pack_propagate(False)
        
        # Sidebar title with more space
        sidebar_title = tk.Label(
            sidebar,
            text="Controls",
            font=PixelFont.get_clean_font(16, "bold"),
            bg=self.colors['light_gray'],
            fg=self.colors['text'],
            pady=30
        )
        sidebar_title.pack(fill=tk.X)
        
        # Clean buttons with better spacing
        btn = self.create_clean_button(sidebar, "Run Simulation")
        btn.pack(fill=tk.X, padx=20, pady=10)
            
    def create_clean_button(self, parent, text):
        """Create a clean, modern button"""
        btn = tk.Button(
            parent,
            text=text,
            font=PixelFont.get_clean_font(11),
            bg=self.colors['primary'],
            fg='white',
            relief=tk.FLAT,
            borderwidth=0,
            pady=12,
            activebackground=self.colors['accent'],
            activeforeground='white',
            cursor='hand2',
            command=lambda: self.button_click(text)
        )
        
        # Bind hover effects
        btn.bind("<Enter>", lambda e: self.on_button_hover(btn, True))
        btn.bind("<Leave>", lambda e: self.on_button_hover(btn, False))
        
        return btn
        
    def on_button_hover(self, button, entering):
        """Handle button hover effects"""
        if entering:
            button.configure(bg=self.colors['accent'])
        else:
            button.configure(bg=self.colors['primary'])
            
    def button_click(self, button_text):
        """Handle button clicks with enhanced feedback"""
        print(f"Button clicked: {button_text}")
        
        # Add visual feedback for Run Simulation
        if button_text == "Run Simulation":
            self.update_status("🔬 Starting quantum simulation...")
            print("🔬 Starting quantum simulation...")
            # Reset data and restart
            self.current_iteration = 0
            self.converged_methods = set()  # Reset convergence tracking
            self.simulation_stopped = False  # Reset simulation stop flag
            for method in self.data_storage:
                self.data_storage[method]['iterations'] = []
                self.data_storage[method]['energy'] = []
            # Reset chart titles
            self.reset_chart_titles()
            
        # Reset status after 2 seconds
        self.root.after(2000, lambda: self.update_status("Ready - Real-time VQE Simulation"))
        
    def create_main_content(self, parent):
        """Create the main content area with 2x2 grid"""
        content_frame = Frame(parent, bg=self.colors['bg'])
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create 2x2 grid
        self.create_panel_grid(content_frame)
        
    def create_panel_grid(self, parent):
        """Create the 2x2 grid with 3 charts and 1 energy summary box"""
        # Configure grid weights
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        
        # Panel 1: Normal VQE
        self.panel1 = self.create_chart_panel(
            parent, "Normal VQE", 
            self.create_normal_vqe_chart,
            "Current Energy: Calculating..."
        )
        self.panel1.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        # Panel 2: VQE with UCCSD + Hybrid Optimizer  
        self.panel2 = self.create_chart_panel(
            parent, "VQE + UCCSD + Hybrid Optimizer",
            self.create_vqe_uccsd_hybrid_chart,
            "Current Energy: Calculating..."
        )
        self.panel2.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        # Panel 3: VQE with UCCSD + Hybrid Optimizer + ZNE
        self.panel3 = self.create_chart_panel(
            parent, "VQE + UCCSD + Hybrid Optimizer + ZNE",
            self.create_vqe_uccsd_hybrid_zne_chart,
            "Current Energy: Calculating..."
        )
        self.panel3.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        
        # Panel 4: Energy Summary Box
        self.panel4 = self.create_energy_summary_panel(parent)
        self.panel4.grid(row=1, column=1, padx=15, pady=15, sticky="nsew")
        
    def create_chart_panel(self, parent, title, chart_function, result_text):
        """Create a clean panel with title, chart, and result text"""
        panel = Frame(parent, bg='white', relief=tk.FLAT, borderwidth=1)
        panel.configure(highlightbackground=self.colors['border'], highlightthickness=1)
        
        # Panel title with better styling
        title_frame = Frame(panel, bg='white', height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text=title,
            font=PixelFont.get_clean_font(14, "bold"),
            bg='white',
            fg=self.colors['text'],
            pady=15
        )
        title_label.pack()
        
        # Chart area with padding
        chart_frame = Frame(panel, bg='white')
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Store chart frame and result label for updates
        panel.chart_frame = chart_frame
        
        # Create the specific chart
        chart_function(chart_frame)
        
        # Result text with better styling
        result_frame = Frame(panel, bg='white', height=40)
        result_frame.pack(fill=tk.X)
        result_frame.pack_propagate(False)
        
        result_label = tk.Label(
            result_frame,
            text=result_text,
            font=PixelFont.get_clean_font(10),
            bg='white',
            fg=self.colors['primary'],
            pady=10
        )
        result_label.pack()
        
        # Store result label for updates
        panel.result_label = result_label
        
        return panel
        
    def create_energy_summary_panel(self, parent):
        """Create an energy summary panel showing all method energies"""
        panel = Frame(parent, bg='white', relief=tk.FLAT, borderwidth=1)
        panel.configure(highlightbackground=self.colors['border'], highlightthickness=1)
        
        # Panel title
        title_frame = Frame(panel, bg='white', height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="Energy Values Summary",
            font=PixelFont.get_clean_font(14, "bold"),
            bg='white',
            fg=self.colors['text'],
            pady=15
        )
        title_label.pack()
        
        # Main content area
        content_frame = Frame(panel, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create energy display labels
        self.energy_labels = {}
        methods = [
            ('normal_vqe', 'Normal VQE'),
            ('vqe_uccsd_hybrid', 'VQE + UCCSD + Hybrid'),
            ('vqe_uccsd_hybrid_zne', 'VQE + UCCSD + Hybrid + ZNE')
        ]
        
        for i, (method_key, method_name) in enumerate(methods):
            # Method name label
            method_frame = Frame(content_frame, bg='white')
            method_frame.pack(fill=tk.X, pady=10)
            
            name_label = tk.Label(
                method_frame,
                text=f"{method_name}:",
                font=PixelFont.get_clean_font(11, "bold"),
                bg='white',
                fg=self.colors['text'],
                anchor='w'
            )
            name_label.pack(side=tk.LEFT)
            
            # Energy value label
            energy_label = tk.Label(
                method_frame,
                text="Calculating...",
                font=PixelFont.get_clean_font(11),
                bg='white',
                fg=self.colors['primary'],
                anchor='e'
            )
            energy_label.pack(side=tk.RIGHT)
            
            self.energy_labels[method_key] = energy_label
            
        # Add convergence status
        status_frame = Frame(content_frame, bg='white')
        status_frame.pack(fill=tk.X, pady=20)
        
        status_title = tk.Label(
            status_frame,
            text="Convergence Status:",
            font=PixelFont.get_clean_font(11, "bold"),
            bg='white',
            fg=self.colors['text']
        )
        status_title.pack()
        
        self.convergence_status_label = tk.Label(
            status_frame,
            text="Running simulations...",
            font=PixelFont.get_clean_font(10),
            bg='white',
            fg=self.colors['accent'],
            wraplength=200,
            justify='center'
        )
        self.convergence_status_label.pack(pady=5)
        
        return panel
        
    def create_normal_vqe_chart(self, parent):
        """Create normal VQE energy vs iterations chart"""
        try:
            fig, ax = plt.subplots(figsize=(5, 3.2), facecolor='white')
            ax.set_facecolor('white')
            
            # Initial empty plot
            line, = ax.plot([], [], color=self.colors['primary'], linewidth=2.5, alpha=0.8, label='Normal VQE')
            scatter = ax.scatter([], [], color=self.colors['accent'], s=30, alpha=0.7, zorder=5)
            
            ax.set_xlabel('Iterations', color=self.colors['text'], fontsize=10)
            ax.set_ylabel('Energy (Hartree)', color=self.colors['text'], fontsize=10)
            ax.grid(True, alpha=0.3, color='gray', linestyle='-', linewidth=0.5)
            ax.tick_params(colors=self.colors['text'], labelsize=9)
            ax.legend(fontsize=8, loc='upper right')
            
            # Clean styling
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(self.colors['border'])
            ax.spines['bottom'].set_color(self.colors['border'])
            
            # Set initial limits
            ax.set_xlim(0, 50)
            ax.set_ylim(-2.0, 0.0)  # Expanded initial range to accommodate lower values
            
            plt.tight_layout(pad=1.0)
            
            # Store figure and axes for updates
            parent.fig = fig
            parent.ax = ax
            parent.line = line
            parent.scatter = scatter
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            parent.canvas = canvas
            
        except Exception as e:
            self.create_error_placeholder(parent, f"Chart Error: {e}")
            
    def create_vqe_uccsd_hybrid_chart(self, parent):
        """Create VQE with UCCSD + Hybrid Optimizer chart"""
        try:
            fig, ax = plt.subplots(figsize=(5, 3.2), facecolor='white')
            ax.set_facecolor('white')
            
            line, = ax.plot([], [], color='darkorange', linewidth=2.5, alpha=0.8, label='VQE + UCCSD + Hybrid')
            scatter = ax.scatter([], [], color=self.colors['accent'], s=30, alpha=0.7, zorder=5)
            
            ax.set_xlabel('Iterations', color=self.colors['text'], fontsize=10)
            ax.set_ylabel('Energy (Hartree)', color=self.colors['text'], fontsize=10)
            ax.grid(True, alpha=0.3, color='gray', linestyle='-', linewidth=0.5)
            ax.tick_params(colors=self.colors['text'], labelsize=9)
            ax.legend(fontsize=8, loc='upper right')
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(self.colors['border'])
            ax.spines['bottom'].set_color(self.colors['border'])
            
            ax.set_xlim(0, 50)
            ax.set_ylim(-2.0, 0.0)  # Expanded initial range to accommodate lower values
            
            plt.tight_layout(pad=1.0)
            
            parent.fig = fig
            parent.ax = ax
            parent.line = line
            parent.scatter = scatter
            
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            parent.canvas = canvas
            
        except Exception as e:
            self.create_error_placeholder(parent, f"Chart Error: {e}")
            
    def create_vqe_uccsd_hybrid_zne_chart(self, parent):
        """Create VQE with UCCSD + Hybrid Optimizer + ZNE chart"""
        try:
            fig, ax = plt.subplots(figsize=(5, 3.2), facecolor='white')
            ax.set_facecolor('white')
            
            line, = ax.plot([], [], color='darkred', linewidth=2.5, alpha=0.8, label='VQE + UCCSD + Hybrid + ZNE')
            scatter = ax.scatter([], [], color=self.colors['accent'], s=30, alpha=0.7, zorder=5)
            
            ax.set_xlabel('Iterations', color=self.colors['text'], fontsize=10)
            ax.set_ylabel('Energy (Hartree)', color=self.colors['text'], fontsize=10)
            ax.grid(True, alpha=0.3, color='gray', linestyle='-', linewidth=0.5)
            ax.tick_params(colors=self.colors['text'], labelsize=9)
            ax.legend(fontsize=8, loc='upper right')
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(self.colors['border'])
            ax.spines['bottom'].set_color(self.colors['border'])
            
            ax.set_xlim(0, 50)
            ax.set_ylim(-2.0, 0.0)  # Expanded initial range to accommodate lower values
            
            # Tighter layout with padding
            plt.tight_layout(pad=1.0)
            
            parent.fig = fig
            parent.ax = ax
            parent.line = line
            parent.scatter = scatter
            
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            parent.canvas = canvas
            
        except Exception as e:
            self.create_error_placeholder(parent, f"Chart Error: {e}")
            
    def create_error_placeholder(self, parent, error_msg):
        """Create an error placeholder when charts fail to load"""
        error_frame = Frame(parent, bg='white')
        error_frame.pack(fill=tk.BOTH, expand=True)
        
        error_label = tk.Label(
            error_frame,
            text=f"⚠ {error_msg}",
            font=PixelFont.get_clean_font(10),
            bg='white',
            fg=self.colors['accent'],
            wraplength=200
        )
        error_label.pack(expand=True)
        
    def start_data_generation(self):
        """Start the real-time data generation with 2-second intervals"""
        # Check if simulation should stop
        if self.simulation_stopped or len(self.converged_methods) >= 3:
            if len(self.converged_methods) >= 3:
                self.update_status("✅ Simulation completed - All methods converged!")
                self.simulation_stopped = True
            return
            
        self.generate_new_data_point()
        # Schedule next update in 2 seconds (2000 milliseconds) only if not stopped
        if not self.simulation_stopped:
            self.root.after(2000, self.start_data_generation)
        
    def generate_new_data_point(self):
        """Generate new random data points for all VQE methods"""
        iteration = self.current_iteration
        
        # Generate random data for each method with different characteristics
        # Normal VQE - slower convergence, more noise
        if 'normal_vqe' not in self.converged_methods:
            normal_energy = -0.8 - 0.4 * (1 - np.exp(-iteration/20)) + 0.08 * np.random.random()
        else:
            # Keep at ground state with minimal fluctuation
            normal_energy = self.data_storage['normal_vqe']['energy'][-1] + 0.001 * (np.random.random() - 0.5)
        
        # VQE + UCCSD + Hybrid - fast convergence, medium noise
        if 'vqe_uccsd_hybrid' not in self.converged_methods:
            hybrid_energy = -1.0 - 0.4 * (1 - np.exp(-iteration/10)) + 0.03 * np.random.random()
        else:
            hybrid_energy = self.data_storage['vqe_uccsd_hybrid']['energy'][-1] + 0.001 * (np.random.random() - 0.5)
        
        # VQE + UCCSD + Hybrid + ZNE - best performance with all optimizations
        if 'vqe_uccsd_hybrid_zne' not in self.converged_methods:
            zne_energy = -1.1 - 0.5 * (1 - np.exp(-iteration/8)) + 0.02 * np.random.random()
        else:
            zne_energy = self.data_storage['vqe_uccsd_hybrid_zne']['energy'][-1] + 0.0005 * (np.random.random() - 0.5)
        
        # Store new data points
        self.data_storage['normal_vqe']['iterations'].append(iteration)
        self.data_storage['normal_vqe']['energy'].append(normal_energy)
        
        self.data_storage['vqe_uccsd_hybrid']['iterations'].append(iteration)
        self.data_storage['vqe_uccsd_hybrid']['energy'].append(hybrid_energy)
        
        self.data_storage['vqe_uccsd_hybrid_zne']['iterations'].append(iteration)
        self.data_storage['vqe_uccsd_hybrid_zne']['energy'].append(zne_energy)
        
        # Check for convergence
        self.check_convergence()
        
        # Update charts
        self.update_charts()
        
        # Update result labels and energy summary
        self.update_result_labels(normal_energy, hybrid_energy, zne_energy)
        self.update_energy_summary(normal_energy, hybrid_energy, zne_energy)
        
        # Update status
        converged_count = len(self.converged_methods)
        if converged_count == 3:
            self.update_status(f"✅ Iteration {iteration}: All methods converged - Simulation complete!")
            self.simulation_stopped = True
        elif converged_count > 0:
            self.update_status(f"Iteration {iteration}: {converged_count}/3 methods converged")
        else:
            self.update_status(f"Iteration {iteration}: Generating new quantum data...")
        
        # Increment iteration counter
        self.current_iteration += 1
        
        # Keep only last 50 points for performance
        if len(self.data_storage['normal_vqe']['iterations']) > 50:
            for method in self.data_storage:
                self.data_storage[method]['iterations'] = self.data_storage[method]['iterations'][-50:]
                self.data_storage[method]['energy'] = self.data_storage[method]['energy'][-50:]
    
    def check_convergence(self):
        """Check if any methods have converged based on energy difference threshold"""
        for method_name, data in self.data_storage.items():
            if method_name in self.converged_methods:
                continue  # Already converged
                
            energies = data['energy']
            if len(energies) >= self.convergence_window:
                # Check if the last few energy values are within threshold
                recent_energies = energies[-self.convergence_window:]
                energy_range = max(recent_energies) - min(recent_energies)
                
                if energy_range < self.convergence_threshold:
                    self.converged_methods.add(method_name)
                    print(f"{method_name} has converged to ground state at iteration {self.current_iteration}")
                    
                    # Update the chart title to show convergence
                    self.mark_convergence(method_name)
    
    def mark_convergence(self, method_name):
        """Mark a method as converged in the UI"""
        try:
            if method_name == 'normal_vqe' and hasattr(self.panel1.chart_frame, 'ax'):
                title = self.panel1.chart_frame.ax.get_title()
                self.panel1.chart_frame.ax.set_title("Normal VQE - CONVERGED ✓", 
                                                   color='green', fontweight='bold', fontsize=10)
                self.panel1.chart_frame.canvas.draw()
                
            elif method_name == 'vqe_uccsd' and hasattr(self.panel2.chart_frame, 'ax'):
                self.panel2.chart_frame.ax.set_title("VQE + UCCSD - CONVERGED ✓", 
                                                   color='green', fontweight='bold', fontsize=10)
                self.panel2.chart_frame.canvas.draw()
                
            elif method_name == 'vqe_uccsd_hybrid' and hasattr(self.panel3.chart_frame, 'ax'):
                self.panel3.chart_frame.ax.set_title("VQE + UCCSD + Hybrid - CONVERGED ✓", 
                                                   color='green', fontweight='bold', fontsize=10)
                self.panel3.chart_frame.canvas.draw()
                
            elif method_name == 'vqe_uccsd_hybrid_zne' and hasattr(self.panel4.chart_frame, 'ax'):
                self.panel4.chart_frame.ax.set_title("VQE + UCCSD + Hybrid + ZNE - CONVERGED ✓", 
                                                   color='green', fontweight='bold', fontsize=10)
                self.panel4.chart_frame.canvas.draw()
                
        except Exception as e:
            print(f"Error marking convergence for {method_name}: {e}")
            
    def reset_chart_titles(self):
        """Reset chart titles when simulation restarts"""
        try:
            if hasattr(self.panel1.chart_frame, 'ax'):
                self.panel1.chart_frame.ax.set_title("", fontsize=10)
                self.panel1.chart_frame.canvas.draw()
                
            if hasattr(self.panel2.chart_frame, 'ax'):
                self.panel2.chart_frame.ax.set_title("", fontsize=10)
                self.panel2.chart_frame.canvas.draw()
                
            if hasattr(self.panel3.chart_frame, 'ax'):
                self.panel3.chart_frame.ax.set_title("", fontsize=10)
                self.panel3.chart_frame.canvas.draw()
                
            if hasattr(self.panel4.chart_frame, 'ax'):
                self.panel4.chart_frame.ax.set_title("", fontsize=10)
                self.panel4.chart_frame.canvas.draw()
                
        except Exception as e:
            print(f"Error resetting chart titles: {e}")
    
    def update_charts(self):
        """Update all charts with new data"""
        try:
            # Update Normal VQE chart (Panel 1)
            if hasattr(self.panel1.chart_frame, 'line'):
                iterations = self.data_storage['normal_vqe']['iterations']
                energies = self.data_storage['normal_vqe']['energy']
                
                self.panel1.chart_frame.line.set_data(iterations, energies)
                if len(iterations) > 0:
                    # Update scatter plot with every 5th point
                    scatter_iterations = iterations[::5] if len(iterations) >= 5 else iterations
                    scatter_energies = energies[::5] if len(energies) >= 5 else energies
                    self.panel1.chart_frame.scatter.set_offsets(list(zip(scatter_iterations, scatter_energies)))
                
                # Auto-scale both x and y axes
                if iterations:
                    self.panel1.chart_frame.ax.set_xlim(0, max(max(iterations) + 5, 50))
                if energies:
                    min_energy = min(energies)
                    max_energy = max(energies)
                    energy_range = max_energy - min_energy
                    margin = max(0.1, energy_range * 0.1)  # 10% margin or minimum 0.1
                    self.panel1.chart_frame.ax.set_ylim(min_energy - margin, max_energy + margin)
                
                self.panel1.chart_frame.canvas.draw()
            
            # Update VQE + UCCSD + Hybrid chart (Panel 2)
            if hasattr(self.panel2.chart_frame, 'line'):
                iterations = self.data_storage['vqe_uccsd_hybrid']['iterations']
                energies = self.data_storage['vqe_uccsd_hybrid']['energy']
                
                self.panel2.chart_frame.line.set_data(iterations, energies)
                if len(iterations) > 0:
                    scatter_iterations = iterations[::5] if len(iterations) >= 5 else iterations
                    scatter_energies = energies[::5] if len(energies) >= 5 else energies
                    self.panel2.chart_frame.scatter.set_offsets(list(zip(scatter_iterations, scatter_energies)))
                
                # Auto-scale both x and y axes
                if iterations:
                    self.panel2.chart_frame.ax.set_xlim(0, max(max(iterations) + 5, 50))
                if energies:
                    min_energy = min(energies)
                    max_energy = max(energies)
                    energy_range = max_energy - min_energy
                    margin = max(0.1, energy_range * 0.1)  # 10% margin or minimum 0.1
                    self.panel2.chart_frame.ax.set_ylim(min_energy - margin, max_energy + margin)
                
                self.panel2.chart_frame.canvas.draw()
            
            # Update VQE + UCCSD + Hybrid + ZNE chart (Panel 3)
            if hasattr(self.panel3.chart_frame, 'line'):
                iterations = self.data_storage['vqe_uccsd_hybrid_zne']['iterations']
                energies = self.data_storage['vqe_uccsd_hybrid_zne']['energy']
                
                self.panel3.chart_frame.line.set_data(iterations, energies)
                if len(iterations) > 0:
                    scatter_iterations = iterations[::5] if len(iterations) >= 5 else iterations
                    scatter_energies = energies[::5] if len(energies) >= 5 else energies
                    self.panel3.chart_frame.scatter.set_offsets(list(zip(scatter_iterations, scatter_energies)))
                
                # Auto-scale both x and y axes
                if iterations:
                    self.panel3.chart_frame.ax.set_xlim(0, max(max(iterations) + 5, 50))
                if energies:
                    min_energy = min(energies)
                    max_energy = max(energies)
                    energy_range = max_energy - min_energy
                    margin = max(0.1, energy_range * 0.1)  # 10% margin or minimum 0.1
                    self.panel3.chart_frame.ax.set_ylim(min_energy - margin, max_energy + margin)
                
                self.panel3.chart_frame.canvas.draw()
                
        except Exception as e:
            print(f"Error updating charts: {e}")
    
    def update_result_labels(self, normal_energy, hybrid_energy, zne_energy):
        """Update the result labels with current energy values"""
        try:
            if hasattr(self.panel1, 'result_label'):
                self.panel1.result_label.config(text=f"Current Energy: {normal_energy:.4f} Hartree")
            
            if hasattr(self.panel2, 'result_label'):
                self.panel2.result_label.config(text=f"Current Energy: {hybrid_energy:.4f} Hartree")
            
            if hasattr(self.panel3, 'result_label'):
                self.panel3.result_label.config(text=f"Current Energy: {zne_energy:.4f} Hartree")
                
        except Exception as e:
            print(f"Error updating result labels: {e}")
    
    def update_energy_summary(self, normal_energy, hybrid_energy, zne_energy):
        """Update the energy summary panel with current values"""
        try:
            if hasattr(self, 'energy_labels'):
                self.energy_labels['normal_vqe'].config(text=f"{normal_energy:.4f} Hartree")
                self.energy_labels['vqe_uccsd_hybrid'].config(text=f"{hybrid_energy:.4f} Hartree")  
                self.energy_labels['vqe_uccsd_hybrid_zne'].config(text=f"{zne_energy:.4f} Hartree")
                
            # Update convergence status
            if hasattr(self, 'convergence_status_label'):
                converged_count = len(self.converged_methods)
                if converged_count == 3:
                    status_text = "All methods converged!"
                    color = self.colors['primary']
                elif converged_count > 0:
                    status_text = f"{converged_count}/3 methods converged"
                    color = self.colors['accent']
                else:
                    status_text = "Running simulations..."
                    color = self.colors['text']
                    
                self.convergence_status_label.config(text=status_text, fg=color)
                
        except Exception as e:
            print(f"Error updating energy summary: {e}")
        
    def create_footer(self):
        """Create the footer with prototype disclaimer"""
        footer = Frame(self.root, bg=self.colors['bg'], height=50)
        footer.pack(fill=tk.X, side=tk.BOTTOM, padx=30, pady=(10, 20))
        footer.pack_propagate(False)
        
        footer_text = tk.Label(
            footer,
            text="Real-time VQE Simulation - Data updates every 2 seconds",
            font=PixelFont.get_clean_font(10),
            bg=self.colors['bg'],
            fg=self.colors['text'],
            anchor='center'
        )
        footer_text.pack(expand=True, fill=tk.BOTH)
        
    def create_status_bar(self):
        """Create a status bar for user feedback"""
        status_frame = Frame(self.root, bg=self.colors['secondary'], height=35)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=30, pady=(10, 0))
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Real-time VQE Simulation Starting...")
        
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=PixelFont.get_clean_font(9),
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, padx=15, pady=8)
        
    def update_status(self, message):
        """Update the status bar message"""
        if hasattr(self, 'status_var'):
            self.status_var.set(message)
            self.root.update_idletasks()

def main():
    """Run the VQE Dashboard application"""
    try:
        root = tk.Tk()
        
        # Set window icon and additional properties
        root.resizable(True, True)
        root.minsize(800, 600)
        
        # Handle window closing gracefully
        def on_closing():
            try:
                plt.close('all')  # Close all matplotlib figures
                root.quit()
                root.destroy()
            except:
                pass
            
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Create the dashboard
        dashboard = VQEDashboard(root)
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting VQE Dashboard: {e}")
        print("Please check your Python environment and dependencies.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
