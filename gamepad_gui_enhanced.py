import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import vgamepad as vg
from pynput import keyboard, mouse
import threading
import time
import json
import os
from PIL import Image, ImageTk, ImageDraw

class GamepadGUIEnhanced:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎮 Virtual Xbox Controller - Enhanced GUI")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2b2b2b')
        
        # Gamepad instance
        self.gamepad = vg.VX360Gamepad()
        
        # Settings
        self.sensitivity = 1.0
        self.mouse_sensitivity = 0.5
        self.mouse_enabled = True
        self.logging_enabled = True
        
        # Mouse center
        self.mouse_center_x = 960
        self.mouse_center_y = 540
        
        # Pressed keys tracking
        self.pressed_keys = set()
        
        # GUI state
        self.is_running = False
        self.keyboard_listener = None
        self.mouse_listener = None
        
        # Button mappings
        self.button_mappings = {
            'A': 't', 'B': 'y', 'X': 'g', 'Y': 'h',
            'Back': 'z', 'Start': 'x', 'Guide': 'c',
            'LT': 'u', 'RT': 'o',
            'DPad_Up': '1', 'DPad_Down': '2', 'DPad_Left': '3', 'DPad_Right': '4'
        }
        
        # Current profile
        self.current_profile = "Default"
        self.profiles = {}
        
        # Create GUI
        self.create_widgets()
        self.setup_listeners()
        self.load_default_profile()
        
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="🎮 Virtual Xbox Controller - Enhanced", 
                              font=('Arial', 20, 'bold'), fg='#00ff00', bg='#2b2b2b')
        title_label.pack(pady=(0, 10))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Style the notebook
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#2b2b2b')
        style.configure('TNotebook.Tab', background='#404040', foreground='white')
        
        # Controller tab
        self.create_controller_tab(notebook)
        
        # Button Mapping tab
        self.create_mapping_tab(notebook)
        
        # Settings tab
        self.create_settings_tab(notebook)
        
        # Status tab
        self.create_status_tab(notebook)
        
        # Control buttons
        self.create_control_buttons(main_frame)
        
    def create_controller_tab(self, notebook):
        controller_frame = tk.Frame(notebook, bg='#2b2b2b')
        notebook.add(controller_frame, text="🎮 Controller")
        
        # Create controller image
        self.create_controller_image(controller_frame)
        
    def create_controller_image(self, parent):
        # Create a canvas for the controller image
        canvas_frame = tk.Frame(parent, bg='#2b2b2b')
        canvas_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Create controller image (we'll draw a simple one)
        self.controller_canvas = tk.Canvas(canvas_frame, width=600, height=400, 
                                         bg='#1a1a1a', highlightthickness=0)
        self.controller_canvas.pack(expand=True)
        
        # Draw controller outline
        self.draw_controller()
        
        # Add interactive buttons
        self.create_interactive_buttons()
        
    def draw_controller(self):
        canvas = self.controller_canvas
        
        # Clear canvas
        canvas.delete("all")
        
        # Controller body
        canvas.create_rounded_rectangle(50, 150, 550, 250, radius=20, 
                                      fill='#333333', outline='#666666', width=2)
        
        # Left grip
        canvas.create_rounded_rectangle(30, 180, 80, 220, radius=15, 
                                      fill='#333333', outline='#666666', width=2)
        
        # Right grip
        canvas.create_rounded_rectangle(520, 180, 570, 220, radius=15, 
                                      fill='#333333', outline='#666666', width=2)
        
        # Left joystick area
        canvas.create_oval(120, 170, 180, 230, fill='#444444', outline='#777777', width=2)
        canvas.create_oval(145, 195, 155, 205, fill='#00ff00', outline='#00cc00', width=2, tags='left_joystick')
        
        # Right joystick area
        canvas.create_oval(420, 170, 480, 230, fill='#444444', outline='#777777', width=2)
        canvas.create_oval(445, 195, 455, 205, fill='#00ff00', outline='#00cc00', width=2, tags='right_joystick')
        
        # D-Pad
        canvas.create_polygon(200, 200, 210, 190, 220, 200, 210, 210, fill='#555555', outline='#888888', width=2)
        
        # Action buttons (A, B, X, Y)
        canvas.create_oval(380, 180, 400, 200, fill='#ff0000', outline='#cc0000', width=2, tags='btn_A')
        canvas.create_oval(400, 160, 420, 180, fill='#00ff00', outline='#00cc00', width=2, tags='btn_B')
        canvas.create_oval(360, 200, 380, 220, fill='#0000ff', outline='#0000cc', width=2, tags='btn_X')
        canvas.create_oval(400, 200, 420, 220, fill='#ffff00', outline='#cccc00', width=2, tags='btn_Y')
        
        # System buttons
        canvas.create_oval(250, 190, 270, 210, fill='#ff8800', outline='#cc6600', width=2, tags='btn_Back')
        canvas.create_oval(330, 190, 350, 210, fill='#ff8800', outline='#cc6600', width=2, tags='btn_Start')
        canvas.create_oval(290, 170, 310, 190, fill='#ff8800', outline='#cc6600', width=2, tags='btn_Guide')
        
        # Triggers
        canvas.create_rounded_rectangle(100, 140, 150, 160, radius=5, 
                                      fill='#8800ff', outline='#6600cc', width=2, tags='btn_LT')
        canvas.create_rounded_rectangle(450, 140, 500, 160, radius=5, 
                                      fill='#8800ff', outline='#6600cc', width=2, tags='btn_RT')
        
        # Labels
        canvas.create_text(390, 190, text="A", fill='white', font=('Arial', 8, 'bold'))
        canvas.create_text(410, 170, text="B", fill='white', font=('Arial', 8, 'bold'))
        canvas.create_text(370, 210, text="X", fill='white', font=('Arial', 8, 'bold'))
        canvas.create_text(410, 210, text="Y", fill='white', font=('Arial', 8, 'bold'))
        canvas.create_text(260, 200, text="Back", fill='white', font=('Arial', 6, 'bold'))
        canvas.create_text(340, 200, text="Start", fill='white', font=('Arial', 6, 'bold'))
        canvas.create_text(300, 180, text="Guide", fill='white', font=('Arial', 6, 'bold'))
        canvas.create_text(125, 150, text="LT", fill='white', font=('Arial', 8, 'bold'))
        canvas.create_text(475, 150, text="RT", fill='white', font=('Arial', 8, 'bold'))
        
    def create_interactive_buttons(self):
        # Make buttons clickable
        self.controller_canvas.tag_bind('btn_A', '<Button-1>', lambda e: self.simulate_button_press('A'))
        self.controller_canvas.tag_bind('btn_B', '<Button-1>', lambda e: self.simulate_button_press('B'))
        self.controller_canvas.tag_bind('btn_X', '<Button-1>', lambda e: self.simulate_button_press('X'))
        self.controller_canvas.tag_bind('btn_Y', '<Button-1>', lambda e: self.simulate_button_press('Y'))
        self.controller_canvas.tag_bind('btn_Back', '<Button-1>', lambda e: self.simulate_button_press('Back'))
        self.controller_canvas.tag_bind('btn_Start', '<Button-1>', lambda e: self.simulate_button_press('Start'))
        self.controller_canvas.tag_bind('btn_Guide', '<Button-1>', lambda e: self.simulate_button_press('Guide'))
        self.controller_canvas.tag_bind('btn_LT', '<Button-1>', lambda e: self.simulate_button_press('LT'))
        self.controller_canvas.tag_bind('btn_RT', '<Button-1>', lambda e: self.simulate_button_press('RT'))
        
    def simulate_button_press(self, button_name):
        if not self.is_running:
            messagebox.showwarning("Controller Not Running", "Please start the controller first!")
            return
            
        key = self.button_mappings.get(button_name)
        if key:
            # Simulate key press
            self.on_key_press(type('Key', (), {'char': key})())
            self.root.after(100, lambda: self.on_key_release(type('Key', (), {'char': key})()))
            
    def create_mapping_tab(self, notebook):
        mapping_frame = tk.Frame(notebook, bg='#2b2b2b')
        notebook.add(mapping_frame, text="🔧 Button Mapping")
        
        # Profile management
        profile_frame = tk.LabelFrame(mapping_frame, text="Profile Management", 
                                    font=('Arial', 12, 'bold'), fg='white', bg='#2b2b2b')
        profile_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Profile selection
        profile_select_frame = tk.Frame(profile_frame, bg='#2b2b2b')
        profile_select_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(profile_select_frame, text="Current Profile:", 
                font=('Arial', 10), fg='white', bg='#2b2b2b').pack(side=tk.LEFT)
        
        self.profile_var = tk.StringVar(value=self.current_profile)
        self.profile_combo = ttk.Combobox(profile_select_frame, textvariable=self.profile_var, 
                                        state='readonly', width=15)
        self.profile_combo.pack(side=tk.LEFT, padx=5)
        
        # Profile buttons
        profile_btn_frame = tk.Frame(profile_frame, bg='#2b2b2b')
        profile_btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(profile_btn_frame, text="Load Profile", command=self.load_profile,
                 bg='#0066cc', fg='white', font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)
        tk.Button(profile_btn_frame, text="Save Profile", command=self.save_profile,
                 bg='#00aa00', fg='white', font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)
        tk.Button(profile_btn_frame, text="New Profile", command=self.create_new_profile,
                 bg='#aa6600', fg='white', font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)
        tk.Button(profile_btn_frame, text="Delete Profile", command=self.delete_profile,
                 bg='#cc0000', fg='white', font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)
        
        # Button mapping section
        mapping_section = tk.LabelFrame(mapping_frame, text="Button Mappings", 
                                      font=('Arial', 12, 'bold'), fg='white', bg='#2b2b2b')
        mapping_section.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create scrollable frame for mappings
        canvas = tk.Canvas(mapping_section, bg='#2b2b2b', highlightthickness=0)
        scrollbar = ttk.Scrollbar(mapping_section, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2b2b2b')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Button mappings
        self.mapping_vars = {}
        row = 0
        
        for button, current_key in self.button_mappings.items():
            # Button name
            tk.Label(scrollable_frame, text=f"{button}:", 
                    font=('Arial', 10, 'bold'), fg='white', bg='#2b2b2b', width=12).grid(row=row, column=0, padx=5, pady=2, sticky='w')
            
            # Key entry
            var = tk.StringVar(value=current_key)
            self.mapping_vars[button] = var
            entry = tk.Entry(scrollable_frame, textvariable=var, width=5, 
                           font=('Arial', 10, 'bold'), justify='center')
            entry.grid(row=row, column=1, padx=5, pady=2)
            
            # Test button
            tk.Button(scrollable_frame, text="Test", 
                     command=lambda b=button: self.test_button_mapping(b),
                     bg='#666666', fg='white', font=('Arial', 8)).grid(row=row, column=2, padx=5, pady=2)
            
            row += 1
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Apply changes button
        apply_frame = tk.Frame(mapping_frame, bg='#2b2b2b')
        apply_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(apply_frame, text="Apply Changes", command=self.apply_mapping_changes,
                 bg='#00aa00', fg='white', font=('Arial', 12, 'bold')).pack()
        
    def create_settings_tab(self, notebook):
        settings_frame = tk.Frame(notebook, bg='#2b2b2b')
        notebook.add(settings_frame, text="⚙️ Settings")
        
        # Sensitivity settings
        sensitivity_frame = tk.LabelFrame(settings_frame, text="Sensitivity Settings", 
                                        font=('Arial', 12, 'bold'), fg='white', bg='#2b2b2b')
        sensitivity_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Joystick sensitivity
        tk.Label(sensitivity_frame, text="Joystick Sensitivity:", 
                font=('Arial', 10), fg='white', bg='#2b2b2b').pack(anchor=tk.W, padx=10, pady=5)
        
        self.sensitivity_var = tk.DoubleVar(value=self.sensitivity)
        self.sensitivity_scale = tk.Scale(sensitivity_frame, from_=0.1, to=2.0, resolution=0.1,
                                         orient=tk.HORIZONTAL, variable=self.sensitivity_var,
                                         command=self.update_sensitivity, bg='#404040', fg='white')
        self.sensitivity_scale.pack(fill=tk.X, padx=10, pady=5)
        
        self.sensitivity_label = tk.Label(sensitivity_frame, text=f"Current: {self.sensitivity:.1f}", 
                                         font=('Arial', 10), fg='#00ff00', bg='#2b2b2b')
        self.sensitivity_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Mouse sensitivity
        tk.Label(sensitivity_frame, text="Mouse Sensitivity:", 
                font=('Arial', 10), fg='white', bg='#2b2b2b').pack(anchor=tk.W, padx=10, pady=5)
        
        self.mouse_sensitivity_var = tk.DoubleVar(value=self.mouse_sensitivity)
        self.mouse_sensitivity_scale = tk.Scale(sensitivity_frame, from_=0.1, to=2.0, resolution=0.1,
                                               orient=tk.HORIZONTAL, variable=self.mouse_sensitivity_var,
                                               command=self.update_mouse_sensitivity, bg='#404040', fg='white')
        self.mouse_sensitivity_scale.pack(fill=tk.X, padx=10, pady=5)
        
        self.mouse_sensitivity_label = tk.Label(sensitivity_frame, text=f"Current: {self.mouse_sensitivity:.1f}", 
                                               font=('Arial', 10), fg='#00ff00', bg='#2b2b2b')
        self.mouse_sensitivity_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Control settings
        control_frame = tk.LabelFrame(settings_frame, text="Control Settings", 
                                    font=('Arial', 12, 'bold'), fg='white', bg='#2b2b2b')
        control_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Mouse control toggle
        self.mouse_enabled_var = tk.BooleanVar(value=self.mouse_enabled)
        mouse_check = tk.Checkbutton(control_frame, text="Enable Mouse Control", 
                                   variable=self.mouse_enabled_var, command=self.toggle_mouse_control,
                                   font=('Arial', 10), fg='white', bg='#2b2b2b', selectcolor='#404040')
        mouse_check.pack(anchor=tk.W, padx=10, pady=5)
        
        # Logging toggle
        self.logging_enabled_var = tk.BooleanVar(value=self.logging_enabled)
        logging_check = tk.Checkbutton(control_frame, text="Enable Logging", 
                                     variable=self.logging_enabled_var, command=self.toggle_logging,
                                     font=('Arial', 10), fg='white', bg='#2b2b2b', selectcolor='#404040')
        logging_check.pack(anchor=tk.W, padx=10, pady=5)
        
    def create_status_tab(self, notebook):
        status_frame = tk.Frame(notebook, bg='#2b2b2b')
        notebook.add(status_frame, text="📊 Status")
        
        # Status display
        tk.Label(status_frame, text="Controller Status", font=('Arial', 12, 'bold'), 
                fg='white', bg='#2b2b2b').pack(pady=10)
        
        self.status_text = tk.Text(status_frame, height=20, width=70, bg='#1a1a1a', 
                                 fg='#00ff00', font=('Consolas', 9))
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbar for status text
        scrollbar = tk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
        
        # Clear button
        clear_btn = tk.Button(status_frame, text="Clear Log", command=self.clear_status,
                            bg='#ff4444', fg='white', font=('Arial', 10, 'bold'))
        clear_btn.pack(pady=10)
        
    def create_control_buttons(self, parent):
        control_frame = tk.Frame(parent, bg='#2b2b2b')
        control_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = tk.Button(control_frame, text="▶️ Start Controller", 
                                 command=self.start_controller, bg='#00aa00', fg='white',
                                 font=('Arial', 12, 'bold'), width=15)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ Stop Controller", 
                                command=self.stop_controller, bg='#aa0000', fg='white',
                                font=('Arial', 12, 'bold'), width=15, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = tk.Button(control_frame, text="🔄 Reset Controller", 
                                 command=self.reset_controller, bg='#aa6600', fg='white',
                                 font=('Arial', 12, 'bold'), width=15)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
    # Profile management methods
    def load_default_profile(self):
        self.profiles = {
            "Default": {
                "button_mappings": self.button_mappings.copy(),
                "sensitivity": 1.0,
                "mouse_sensitivity": 0.5,
                "mouse_enabled": True,
                "logging_enabled": True
            }
        }
        self.update_profile_combo()
        
    def update_profile_combo(self):
        profiles = list(self.profiles.keys())
        self.profile_combo['values'] = profiles
        if self.current_profile not in profiles:
            self.current_profile = profiles[0] if profiles else "Default"
            self.profile_var.set(self.current_profile)
            
    def create_new_profile(self):
        name = tk.simpledialog.askstring("New Profile", "Enter profile name:")
        if name and name not in self.profiles:
            self.profiles[name] = {
                "button_mappings": self.button_mappings.copy(),
                "sensitivity": self.sensitivity,
                "mouse_sensitivity": self.mouse_sensitivity,
                "mouse_enabled": self.mouse_enabled,
                "logging_enabled": self.logging_enabled
            }
            self.current_profile = name
            self.profile_var.set(name)
            self.update_profile_combo()
            self.log_status(f"Created new profile: {name}")
            
    def save_profile(self):
        if self.current_profile in self.profiles:
            self.profiles[self.current_profile] = {
                "button_mappings": self.button_mappings.copy(),
                "sensitivity": self.sensitivity,
                "mouse_sensitivity": self.mouse_sensitivity,
                "mouse_enabled": self.mouse_enabled,
                "logging_enabled": self.logging_enabled
            }
            self.save_profiles_to_file()
            self.log_status(f"Saved profile: {self.current_profile}")
            
    def load_profile(self):
        profile_name = self.profile_var.get()
        if profile_name in self.profiles:
            profile = self.profiles[profile_name]
            self.button_mappings = profile["button_mappings"].copy()
            self.sensitivity = profile["sensitivity"]
            self.mouse_sensitivity = profile["mouse_sensitivity"]
            self.mouse_enabled = profile["mouse_enabled"]
            self.logging_enabled = profile["logging_enabled"]
            
            # Update GUI
            self.sensitivity_var.set(self.sensitivity)
            self.mouse_sensitivity_var.set(self.mouse_sensitivity)
            self.mouse_enabled_var.set(self.mouse_enabled)
            self.logging_enabled_var.set(self.logging_enabled)
            
            # Update mapping display
            for button, var in self.mapping_vars.items():
                var.set(self.button_mappings.get(button, ''))
                
            self.current_profile = profile_name
            self.log_status(f"Loaded profile: {profile_name}")
            
    def delete_profile(self):
        profile_name = self.profile_var.get()
        if profile_name != "Default" and profile_name in self.profiles:
            if messagebox.askyesno("Delete Profile", f"Are you sure you want to delete profile '{profile_name}'?"):
                del self.profiles[profile_name]
                self.update_profile_combo()
                self.log_status(f"Deleted profile: {profile_name}")
                
    def save_profiles_to_file(self):
        try:
            with open('gamepad_profiles.json', 'w') as f:
                json.dump(self.profiles, f, indent=2)
        except Exception as e:
            self.log_status(f"Error saving profiles: {e}")
            
    def load_profiles_from_file(self):
        try:
            if os.path.exists('gamepad_profiles.json'):
                with open('gamepad_profiles.json', 'r') as f:
                    self.profiles = json.load(f)
                self.update_profile_combo()
        except Exception as e:
            self.log_status(f"Error loading profiles: {e}")
            
    def test_button_mapping(self, button_name):
        key = self.mapping_vars[button_name].get()
        if key:
            self.log_status(f"Testing {button_name} -> {key}")
            # Simulate the button press
            self.simulate_button_press(button_name)
            
    def apply_mapping_changes(self):
        # Update button mappings from GUI
        for button, var in self.mapping_vars.items():
            new_key = var.get().lower()
            if new_key:
                self.button_mappings[button] = new_key
                
        self.log_status("Button mappings updated!")
        
    # Rest of the methods remain the same as the original GUI...
    def update_sensitivity(self, value):
        self.sensitivity = float(value)
        self.sensitivity_label.config(text=f"Current: {self.sensitivity:.1f}")
        
    def update_mouse_sensitivity(self, value):
        self.mouse_sensitivity = float(value)
        self.mouse_sensitivity_label.config(text=f"Current: {self.mouse_sensitivity:.1f}")
        
    def toggle_mouse_control(self):
        self.mouse_enabled = self.mouse_enabled_var.get()
        status = "Enabled" if self.mouse_enabled else "Disabled"
        self.log_status(f"Mouse control: {status}")
        
    def toggle_logging(self):
        self.logging_enabled = self.logging_enabled_var.get()
        status = "Enabled" if self.logging_enabled else "Disabled"
        self.log_status(f"Logging: {status}")
        
    def log_status(self, message):
        if self.logging_enabled:
            timestamp = time.strftime("%H:%M:%S")
            log_message = f"[{timestamp}] {message}\n"
            self.status_text.insert(tk.END, log_message)
            self.status_text.see(tk.END)
            
    def clear_status(self):
        self.status_text.delete(1.0, tk.END)
        
    def update_left_joystick_visual(self, x, y):
        # Update visual representation
        center_x, center_y = 150, 200
        knob_x = center_x + (x * 20)  # Scale to joystick area
        knob_y = center_y - (y * 20)  # Invert Y for display
        
        # Keep knob within bounds
        knob_x = max(130, min(170, knob_x))
        knob_y = max(180, min(220, knob_y))
        
        self.controller_canvas.coords('left_joystick', knob_x-5, knob_y-5, knob_x+5, knob_y+5)
        
    def start_controller(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.log_status("Controller started!")
            self.setup_listeners()
            
    def stop_controller(self):
        if self.is_running:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.log_status("Controller stopped!")
            self.cleanup_listeners()
            
    def reset_controller(self):
        # Reset all controller inputs
        self.gamepad.left_joystick_float(0, 0)
        self.gamepad.right_joystick_float(0, 0)
        self.gamepad.left_trigger_float(0)
        self.gamepad.right_trigger_float(0)
        self.gamepad.update()
        
        # Reset visual
        self.update_left_joystick_visual(0, 0)
        self.log_status("Controller reset!")
        
    def setup_listeners(self):
        if self.is_running:
            # Keyboard listener
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release
            )
            self.keyboard_listener.start()
            
            # Mouse listener
            self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move)
            self.mouse_listener.start()
            
    def cleanup_listeners(self):
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
            
    def on_key_press(self, key):
        try:
            if hasattr(key, 'char') and key.char:
                char = key.char.lower()
                
                # Movement keys
                if char in ['w', 'a', 's', 'd']:
                    self.pressed_keys.add(char)
                    self.update_movement()
                    
                # Check button mappings
                for button, mapped_key in self.button_mappings.items():
                    if char == mapped_key:
                        self.press_button_visual(button)
                        self.press_gamepad_button(button)
                        break
                        
        except Exception as e:
            self.log_status(f"Error in key press: {e}")
            
    def on_key_release(self, key):
        try:
            if hasattr(key, 'char') and key.char:
                char = key.char.lower()
                
                # Movement keys
                if char in ['w', 'a', 's', 'd']:
                    self.pressed_keys.discard(char)
                    self.update_movement()
                    
                # Check button mappings
                for button, mapped_key in self.button_mappings.items():
                    if char == mapped_key:
                        self.release_gamepad_button(button)
                        break
                        
        except Exception as e:
            self.log_status(f"Error in key release: {e}")
            
    def press_gamepad_button(self, button_name):
        button_map = {
            'A': vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
            'B': vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
            'X': vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
            'Y': vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
            'Back': vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
            'Start': vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
            'Guide': vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE,
            'DPad_Up': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
            'DPad_Down': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
            'DPad_Left': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
            'DPad_Right': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT
        }
        
        if button_name in button_map:
            self.gamepad.press_button(button_map[button_name])
            self.gamepad.update()
            self.log_status(f"Button {button_name} pressed")
        elif button_name == 'LT':
            self.gamepad.left_trigger_float(1.0)
            self.gamepad.update()
            self.log_status("LT pressed")
        elif button_name == 'RT':
            self.gamepad.right_trigger_float(1.0)
            self.gamepad.update()
            self.log_status("RT pressed")
            
    def release_gamepad_button(self, button_name):
        button_map = {
            'A': vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
            'B': vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
            'X': vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
            'Y': vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
            'Back': vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
            'Start': vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
            'Guide': vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE,
            'DPad_Up': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
            'DPad_Down': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
            'DPad_Left': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
            'DPad_Right': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT
        }
        
        if button_name in button_map:
            self.gamepad.release_button(button_map[button_name])
            self.gamepad.update()
            self.log_status(f"Button {button_name} released")
        elif button_name == 'LT':
            self.gamepad.left_trigger_float(0)
            self.gamepad.update()
            self.log_status("LT released")
        elif button_name == 'RT':
            self.gamepad.right_trigger_float(0)
            self.gamepad.update()
            self.log_status("RT released")
            
    def press_button_visual(self, button_name):
        # Visual feedback for button press
        tag_map = {
            'A': 'btn_A', 'B': 'btn_B', 'X': 'btn_X', 'Y': 'btn_Y',
            'Back': 'btn_Back', 'Start': 'btn_Start', 'Guide': 'btn_Guide',
            'LT': 'btn_LT', 'RT': 'btn_RT'
        }
        
        if button_name in tag_map:
            tag = tag_map[button_name]
            # Change color temporarily
            self.controller_canvas.itemconfig(tag, fill='#ffffff')
            self.root.after(100, lambda: self.reset_button_color(tag, button_name))
            
    def reset_button_color(self, tag, button_name):
        color_map = {
            'A': '#ff0000', 'B': '#00ff00', 'X': '#0000ff', 'Y': '#ffff00',
            'Back': '#ff8800', 'Start': '#ff8800', 'Guide': '#ff8800',
            'LT': '#8800ff', 'RT': '#8800ff'
        }
        self.controller_canvas.itemconfig(tag, fill=color_map.get(button_name, '#666666'))
        
    def update_movement(self):
        x, y = 0.0, 0.0
        
        if 'w' in self.pressed_keys: y += 1.0
        if 's' in self.pressed_keys: y -= 1.0
        if 'a' in self.pressed_keys: x -= 1.0
        if 'd' in self.pressed_keys: x += 1.0
        
        # Normalize diagonal movement
        if x != 0 and y != 0:
            x *= 0.707
            y *= 0.707
            
        # Apply sensitivity
        adjusted_x = x * self.sensitivity
        adjusted_y = y * self.sensitivity
        
        # Update controller
        self.gamepad.left_joystick_float(adjusted_x, adjusted_y)
        self.gamepad.update()
        
        # Update visual
        self.update_left_joystick_visual(x, y)
        
        if x != 0 or y != 0:
            self.log_status(f"Left joystick: X={adjusted_x:.2f}, Y={adjusted_y:.2f}")
            
    def on_mouse_move(self, x, y):
        if not self.mouse_enabled or not self.is_running:
            return
            
        # Calculate distance from center
        dx = (x - self.mouse_center_x) / self.mouse_center_x
        dy = (y - self.mouse_center_y) / self.mouse_center_y
        
        # Apply sensitivity and limit values
        dx = max(-1.0, min(1.0, dx * self.mouse_sensitivity))
        dy = max(-1.0, min(1.0, dy * self.mouse_sensitivity))
        
        # Update right joystick
        self.gamepad.right_joystick_float(dx, -dy)
        self.gamepad.update()
        
        if abs(dx) > 0.1 or abs(dy) > 0.1:
            self.log_status(f"Right joystick: X={dx:.2f}, Y={-dy:.2f}")
            
    def run(self):
        self.log_status("🎮 Virtual Xbox Controller Enhanced GUI Ready!")
        self.log_status("Press 'Start Controller' to begin")
        self.load_profiles_from_file()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        self.stop_controller()
        self.reset_controller()
        self.save_profiles_to_file()
        self.root.destroy()

# Add rounded rectangle method to Canvas
def create_rounded_rectangle(self, x1, y1, x2, y2, radius=10, **kwargs):
    points = []
    for x, y in [(x1, y1 + radius), (x1, y1), (x1 + radius, y1),
                 (x2 - radius, y1), (x2, y1), (x2, y1 + radius),
                 (x2, y2 - radius), (x2, y2), (x2 - radius, y2),
                 (x1 + radius, y2), (x1, y2), (x1, y2 - radius)]:
        points.extend([x, y])
    return self.create_polygon(points, smooth=True, **kwargs)

tk.Canvas.create_rounded_rectangle = create_rounded_rectangle

if __name__ == "__main__":
    import tkinter.simpledialog
    app = GamepadGUIEnhanced()
    app.run()
