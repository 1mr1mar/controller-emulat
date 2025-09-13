import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import vgamepad as vg
from pynput import keyboard, mouse
import threading
import time
import json
import os
from PIL import Image, ImageTk, ImageDraw

class GamepadGUIPro:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎮 Virtual Xbox Controller - Professional")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        
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
        # Header with profiles
        self.create_header()
        
        # Main content area
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left side - Controller image and controls
        left_frame = tk.Frame(main_frame, bg='#1a1a1a')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Right side - Settings and status
        right_frame = tk.Frame(main_frame, bg='#1a1a1a', width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)
        
        # Create controller display
        self.create_controller_display(left_frame)
        
        # Create settings panel
        self.create_settings_panel(right_frame)
        
        # Create status panel
        self.create_status_panel(right_frame)
        
    def create_header(self):
        header_frame = tk.Frame(self.root, bg='#2b2b2b', height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame, text="🎮 Virtual Xbox Controller - Professional", 
                              font=('Arial', 18, 'bold'), fg='#00ff00', bg='#2b2b2b')
        title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Profile management in header
        profile_frame = tk.Frame(header_frame, bg='#2b2b2b')
        profile_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Profile selection
        tk.Label(profile_frame, text="Profile:", font=('Arial', 10, 'bold'), 
                fg='white', bg='#2b2b2b').pack(side=tk.LEFT, padx=(0, 5))
        
        self.profile_var = tk.StringVar(value=self.current_profile)
        self.profile_combo = ttk.Combobox(profile_frame, textvariable=self.profile_var, 
                                        state='readonly', width=15)
        self.profile_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Profile buttons
        profile_btn_frame = tk.Frame(profile_frame, bg='#2b2b2b')
        profile_btn_frame.pack(side=tk.LEFT)
        
        tk.Button(profile_btn_frame, text="Load", command=self.load_profile,
                 bg='#0066cc', fg='white', font=('Arial', 8, 'bold'), width=6).pack(side=tk.LEFT, padx=1)
        tk.Button(profile_btn_frame, text="Save", command=self.save_profile,
                 bg='#00aa00', fg='white', font=('Arial', 8, 'bold'), width=6).pack(side=tk.LEFT, padx=1)
        tk.Button(profile_btn_frame, text="New", command=self.create_new_profile,
                 bg='#aa6600', fg='white', font=('Arial', 8, 'bold'), width=6).pack(side=tk.LEFT, padx=1)
        tk.Button(profile_btn_frame, text="Delete", command=self.delete_profile,
                 bg='#cc0000', fg='white', font=('Arial', 8, 'bold'), width=6).pack(side=tk.LEFT, padx=1)
        
        # Control buttons in header
        control_frame = tk.Frame(header_frame, bg='#2b2b2b')
        control_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        self.start_btn = tk.Button(control_frame, text="▶️ Start", 
                                 command=self.start_controller, bg='#00aa00', fg='white',
                                 font=('Arial', 10, 'bold'), width=8)
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ Stop", 
                                command=self.stop_controller, bg='#aa0000', fg='white',
                                font=('Arial', 10, 'bold'), width=8, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        
        self.reset_btn = tk.Button(control_frame, text="🔄 Reset", 
                                 command=self.reset_controller, bg='#aa6600', fg='white',
                                 font=('Arial', 10, 'bold'), width=8)
        self.reset_btn.pack(side=tk.LEFT, padx=2)
        
    def create_controller_display(self, parent):
        # Controller image frame
        controller_frame = tk.LabelFrame(parent, text="🎮 Xbox Controller", 
                                       font=('Arial', 12, 'bold'), fg='white', bg='#1a1a1a')
        controller_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create controller canvas
        self.controller_canvas = tk.Canvas(controller_frame, width=600, height=400, 
                                         bg='#2a2a2a', highlightthickness=0)
        self.controller_canvas.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Draw controller
        self.draw_xbox_controller()
        
        # Button mapping controls below controller
        mapping_frame = tk.LabelFrame(parent, text="🔧 Button Mapping", 
                                    font=('Arial', 12, 'bold'), fg='white', bg='#1a1a1a')
        mapping_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create mapping grid
        self.create_mapping_grid(mapping_frame)
        
    def draw_xbox_controller(self):
        canvas = self.controller_canvas
        canvas.delete("all")
        
        # Get canvas dimensions
        width = canvas.winfo_reqwidth()
        height = canvas.winfo_reqheight()
        
        # Controller body (main shape)
        body_x1, body_y1 = width*0.1, height*0.3
        body_x2, body_y2 = width*0.9, height*0.7
        
        # Main controller body
        canvas.create_rounded_rectangle(body_x1, body_y1, body_x2, body_y2, radius=20, 
                                      fill='#333333', outline='#666666', width=3)
        
        # Left grip
        grip_left_x1, grip_left_y1 = width*0.05, height*0.4
        grip_left_x2, grip_left_y2 = width*0.15, height*0.6
        canvas.create_rounded_rectangle(grip_left_x1, grip_left_y1, grip_left_x2, grip_left_y2, radius=15, 
                                      fill='#333333', outline='#666666', width=2)
        
        # Right grip
        grip_right_x1, grip_right_y1 = width*0.85, height*0.4
        grip_right_x2, grip_right_y2 = width*0.95, height*0.6
        canvas.create_rounded_rectangle(grip_right_x1, grip_right_y1, grip_right_x2, grip_right_y2, radius=15, 
                                      fill='#333333', outline='#666666', width=2)
        
        # Left joystick
        left_joy_x, left_joy_y = width*0.25, height*0.5
        left_joy_radius = 25
        canvas.create_oval(left_joy_x-left_joy_radius, left_joy_y-left_joy_radius, 
                          left_joy_x+left_joy_radius, left_joy_y+left_joy_radius, 
                          fill='#444444', outline='#777777', width=2)
        canvas.create_oval(left_joy_x-8, left_joy_y-8, left_joy_x+8, left_joy_y+8, 
                          fill='#00ff00', outline='#00cc00', width=2, tags='left_joystick')
        
        # Right joystick
        right_joy_x, right_joy_y = width*0.75, height*0.5
        right_joy_radius = 25
        canvas.create_oval(right_joy_x-right_joy_radius, right_joy_y-right_joy_radius, 
                          right_joy_x+right_joy_radius, right_joy_y+right_joy_radius, 
                          fill='#444444', outline='#777777', width=2)
        canvas.create_oval(right_joy_x-8, right_joy_y-8, right_joy_x+8, right_joy_y+8, 
                          fill='#00ff00', outline='#00cc00', width=2, tags='right_joystick')
        
        # D-Pad
        dpad_x, dpad_y = width*0.4, height*0.5
        dpad_size = 20
        canvas.create_polygon(dpad_x, dpad_y-dpad_size, dpad_x+dpad_size, dpad_y, 
                            dpad_x, dpad_y+dpad_size, dpad_x-dpad_size, dpad_y, 
                            fill='#555555', outline='#888888', width=2, tags='dpad')
        
        # Action buttons (A, B, X, Y)
        btn_radius = 15
        # A button (right)
        a_x, a_y = width*0.65, height*0.45
        canvas.create_oval(a_x-btn_radius, a_y-btn_radius, a_x+btn_radius, a_y+btn_radius, 
                          fill='#ff0000', outline='#cc0000', width=2, tags='btn_A')
        canvas.create_text(a_x, a_y, text="A", fill='white', font=('Arial', 10, 'bold'))
        
        # B button (top)
        b_x, b_y = width*0.7, height*0.4
        canvas.create_oval(b_x-btn_radius, b_y-btn_radius, b_x+btn_radius, b_y+btn_radius, 
                          fill='#00ff00', outline='#00cc00', width=2, tags='btn_B')
        canvas.create_text(b_x, b_y, text="B", fill='white', font=('Arial', 10, 'bold'))
        
        # X button (left)
        x_x, x_y = width*0.6, height*0.45
        canvas.create_oval(x_x-btn_radius, x_y-btn_radius, x_x+btn_radius, x_y+btn_radius, 
                          fill='#0000ff', outline='#0000cc', width=2, tags='btn_X')
        canvas.create_text(x_x, x_y, text="X", fill='white', font=('Arial', 10, 'bold'))
        
        # Y button (bottom)
        y_x, y_y = width*0.65, height*0.5
        canvas.create_oval(y_x-btn_radius, y_y-btn_radius, y_x+btn_radius, y_y+btn_radius, 
                          fill='#ffff00', outline='#cccc00', width=2, tags='btn_Y')
        canvas.create_text(y_x, y_y, text="Y", fill='white', font=('Arial', 10, 'bold'))
        
        # System buttons
        sys_btn_radius = 12
        # Back button
        back_x, back_y = width*0.45, height*0.4
        canvas.create_oval(back_x-sys_btn_radius, back_y-sys_btn_radius, 
                          back_x+sys_btn_radius, back_y+sys_btn_radius, 
                          fill='#ff8800', outline='#cc6600', width=2, tags='btn_Back')
        canvas.create_text(back_x, back_y, text="Back", fill='white', font=('Arial', 7, 'bold'))
        
        # Start button
        start_x, start_y = width*0.55, height*0.4
        canvas.create_oval(start_x-sys_btn_radius, start_y-sys_btn_radius, 
                          start_x+sys_btn_radius, start_y+sys_btn_radius, 
                          fill='#ff8800', outline='#cc6600', width=2, tags='btn_Start')
        canvas.create_text(start_x, start_y, text="Start", fill='white', font=('Arial', 7, 'bold'))
        
        # Guide button (Xbox logo)
        guide_x, guide_y = width*0.5, height*0.35
        canvas.create_oval(guide_x-sys_btn_radius, guide_y-sys_btn_radius, 
                          guide_x+sys_btn_radius, guide_y+sys_btn_radius, 
                          fill='#ff8800', outline='#cc6600', width=2, tags='btn_Guide')
        canvas.create_text(guide_x, guide_y, text="Xbox", fill='white', font=('Arial', 6, 'bold'))
        
        # Triggers
        trigger_width = 40
        trigger_height = 15
        # LT
        lt_x, lt_y = width*0.2, height*0.25
        canvas.create_rounded_rectangle(lt_x-trigger_width//2, lt_y-trigger_height//2, 
                                      lt_x+trigger_width//2, lt_y+trigger_height//2, radius=5, 
                                      fill='#8800ff', outline='#6600cc', width=2, tags='btn_LT')
        canvas.create_text(lt_x, lt_y, text="LT", fill='white', font=('Arial', 8, 'bold'))
        
        # RT
        rt_x, rt_y = width*0.8, height*0.25
        canvas.create_rounded_rectangle(rt_x-trigger_width//2, rt_y-trigger_height//2, 
                                      rt_x+trigger_width//2, rt_y+trigger_height//2, radius=5, 
                                      fill='#8800ff', outline='#6600cc', width=2, tags='btn_RT')
        canvas.create_text(rt_x, rt_y, text="RT", fill='white', font=('Arial', 8, 'bold'))
        
        # Make buttons clickable
        self.make_buttons_clickable()
        
    def make_buttons_clickable(self):
        button_tags = ['btn_A', 'btn_B', 'btn_X', 'btn_Y', 'btn_Back', 'btn_Start', 'btn_Guide', 'btn_LT', 'btn_RT']
        for tag in button_tags:
            self.controller_canvas.tag_bind(tag, '<Button-1>', lambda e, t=tag: self.on_button_click(t))
            self.controller_canvas.tag_bind(tag, '<Enter>', lambda e, t=tag: self.on_button_hover(t, True))
            self.controller_canvas.tag_bind(tag, '<Leave>', lambda e, t=tag: self.on_button_hover(t, False))
            
    def on_button_click(self, tag):
        if not self.is_running:
            messagebox.showwarning("Controller Not Running", "Please start the controller first!")
            return
            
        button_name = tag.replace('btn_', '')
        key = self.button_mappings.get(button_name)
        if key:
            self.simulate_button_press(button_name)
            
    def on_button_hover(self, tag, entering):
        if entering:
            self.controller_canvas.itemconfig(tag, width=4)
        else:
            self.controller_canvas.itemconfig(tag, width=2)
            
    def create_mapping_grid(self, parent):
        # Create scrollable frame for mappings
        canvas = tk.Canvas(parent, bg='#1a1a1a', highlightthickness=0, height=150)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Button mappings in grid
        self.mapping_vars = {}
        row = 0
        col = 0
        
        for button, current_key in self.button_mappings.items():
            # Button name
            tk.Label(scrollable_frame, text=f"{button}:", 
                    font=('Arial', 9, 'bold'), fg='white', bg='#1a1a1a', width=8).grid(row=row, column=col*3, padx=2, pady=2, sticky='w')
            
            # Key entry
            var = tk.StringVar(value=current_key)
            self.mapping_vars[button] = var
            entry = tk.Entry(scrollable_frame, textvariable=var, width=3, 
                           font=('Arial', 9, 'bold'), justify='center')
            entry.grid(row=row, column=col*3+1, padx=2, pady=2)
            
            # Test button
            tk.Button(scrollable_frame, text="Test", 
                     command=lambda b=button: self.test_button_mapping(b),
                     bg='#666666', fg='white', font=('Arial', 7), width=4).grid(row=row, column=col*3+2, padx=2, pady=2)
            
            col += 1
            if col >= 3:  # 3 columns
                col = 0
                row += 1
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Apply changes button
        apply_frame = tk.Frame(parent, bg='#1a1a1a')
        apply_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(apply_frame, text="Apply Changes", command=self.apply_mapping_changes,
                 bg='#00aa00', fg='white', font=('Arial', 10, 'bold')).pack()
        
    def create_settings_panel(self, parent):
        # Settings frame
        settings_frame = tk.LabelFrame(parent, text="⚙️ Settings", 
                                     font=('Arial', 12, 'bold'), fg='white', bg='#1a1a1a')
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Joystick sensitivity
        tk.Label(settings_frame, text="Joystick Sensitivity:", 
                font=('Arial', 9), fg='white', bg='#1a1a1a').pack(anchor=tk.W, padx=5, pady=2)
        
        self.sensitivity_var = tk.DoubleVar(value=self.sensitivity)
        self.sensitivity_scale = tk.Scale(settings_frame, from_=0.1, to=2.0, resolution=0.1,
                                         orient=tk.HORIZONTAL, variable=self.sensitivity_var,
                                         command=self.update_sensitivity, bg='#404040', fg='white',
                                         length=200)
        self.sensitivity_scale.pack(fill=tk.X, padx=5, pady=2)
        
        self.sensitivity_label = tk.Label(settings_frame, text=f"Current: {self.sensitivity:.1f}", 
                                         font=('Arial', 8), fg='#00ff00', bg='#1a1a1a')
        self.sensitivity_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Mouse sensitivity
        tk.Label(settings_frame, text="Mouse Sensitivity:", 
                font=('Arial', 9), fg='white', bg='#1a1a1a').pack(anchor=tk.W, padx=5, pady=2)
        
        self.mouse_sensitivity_var = tk.DoubleVar(value=self.mouse_sensitivity)
        self.mouse_sensitivity_scale = tk.Scale(settings_frame, from_=0.1, to=2.0, resolution=0.1,
                                               orient=tk.HORIZONTAL, variable=self.mouse_sensitivity_var,
                                               command=self.update_mouse_sensitivity, bg='#404040', fg='white',
                                               length=200)
        self.mouse_sensitivity_scale.pack(fill=tk.X, padx=5, pady=2)
        
        self.mouse_sensitivity_label = tk.Label(settings_frame, text=f"Current: {self.mouse_sensitivity:.1f}", 
                                               font=('Arial', 8), fg='#00ff00', bg='#1a1a1a')
        self.mouse_sensitivity_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Control toggles
        self.mouse_enabled_var = tk.BooleanVar(value=self.mouse_enabled)
        mouse_check = tk.Checkbutton(settings_frame, text="Enable Mouse Control", 
                                   variable=self.mouse_enabled_var, command=self.toggle_mouse_control,
                                   font=('Arial', 9), fg='white', bg='#1a1a1a', selectcolor='#404040')
        mouse_check.pack(anchor=tk.W, padx=5, pady=2)
        
        self.logging_enabled_var = tk.BooleanVar(value=self.logging_enabled)
        logging_check = tk.Checkbutton(settings_frame, text="Enable Logging", 
                                     variable=self.logging_enabled_var, command=self.toggle_logging,
                                     font=('Arial', 9), fg='white', bg='#1a1a1a', selectcolor='#404040')
        logging_check.pack(anchor=tk.W, padx=5, pady=2)
        
    def create_status_panel(self, parent):
        # Status frame
        status_frame = tk.LabelFrame(parent, text="📊 Status Log", 
                                   font=('Arial', 12, 'bold'), fg='white', bg='#1a1a1a')
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status text
        self.status_text = tk.Text(status_frame, height=15, width=30, bg='#0a0a0a', 
                                 fg='#00ff00', font=('Consolas', 8))
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Clear button
        clear_btn = tk.Button(status_frame, text="Clear Log", command=self.clear_status,
                            bg='#ff4444', fg='white', font=('Arial', 9, 'bold'))
        clear_btn.pack(pady=5)
        
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
        name = simpledialog.askstring("New Profile", "Enter profile name:")
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
            self.simulate_button_press(button_name)
            
    def apply_mapping_changes(self):
        # Update button mappings from GUI
        for button, var in self.mapping_vars.items():
            new_key = var.get().lower()
            if new_key:
                self.button_mappings[button] = new_key
                
        self.log_status("Button mappings updated!")
        
    def simulate_button_press(self, button_name):
        key = self.button_mappings.get(button_name)
        if key:
            # Simulate key press
            self.on_key_press(type('Key', (), {'char': key})())
            self.root.after(100, lambda: self.on_key_release(type('Key', (), {'char': key})()))
            
    # Rest of the methods (same as before)
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
        width = self.controller_canvas.winfo_reqwidth()
        height = self.controller_canvas.winfo_reqheight()
        center_x, center_y = width*0.25, height*0.5
        
        knob_x = center_x + (x * 15)  # Scale to joystick area
        knob_y = center_y - (y * 15)  # Invert Y for display
        
        # Keep knob within bounds
        knob_x = max(center_x-15, min(center_x+15, knob_x))
        knob_y = max(center_y-15, min(center_y+15, knob_y))
        
        self.controller_canvas.coords('left_joystick', knob_x-8, knob_y-8, knob_x+8, knob_y+8)
        
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
        self.log_status("🎮 Virtual Xbox Controller Professional Ready!")
        self.log_status("Press 'Start' to begin")
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
    app = GamepadGUIPro()
    app.run()
