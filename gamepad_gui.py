import tkinter as tk
from tkinter import ttk, messagebox
import vgamepad as vg
from pynput import keyboard, mouse
import threading
import time
import math

class GamepadGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎮 Virtual Xbox Controller - GUI")
        self.root.geometry("800x600")
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
        
        # Create GUI
        self.create_widgets()
        self.setup_listeners()
        
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="🎮 Virtual Xbox Controller", 
                              font=('Arial', 20, 'bold'), fg='#00ff00', bg='#2b2b2b')
        title_label.pack(pady=(0, 20))
        
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
        
        # Settings tab
        self.create_settings_tab(notebook)
        
        # Status tab
        self.create_status_tab(notebook)
        
        # Control buttons
        self.create_control_buttons(main_frame)
        
    def create_controller_tab(self, notebook):
        controller_frame = tk.Frame(notebook, bg='#2b2b2b')
        notebook.add(controller_frame, text="🎮 Controller")
        
        # Left side - Joystick simulation
        left_frame = tk.Frame(controller_frame, bg='#2b2b2b')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Left joystick
        tk.Label(left_frame, text="Left Joystick (WASD)", font=('Arial', 12, 'bold'), 
                fg='white', bg='#2b2b2b').pack(pady=(0, 10))
        
        self.left_joystick_frame = tk.Frame(left_frame, bg='#404040', width=200, height=200)
        self.left_joystick_frame.pack(pady=10)
        self.left_joystick_frame.pack_propagate(False)
        
        self.left_joystick_canvas = tk.Canvas(self.left_joystick_frame, width=200, height=200, 
                                            bg='#404040', highlightthickness=0)
        self.left_joystick_canvas.pack()
        
        # Draw joystick base
        self.left_joystick_canvas.create_oval(20, 20, 180, 180, fill='#555555', outline='#777777', width=2)
        self.left_joystick_canvas.create_oval(90, 90, 110, 110, fill='#00ff00', outline='#00cc00', width=2, tags='left_knob')
        
        # Right side - Buttons
        right_frame = tk.Frame(controller_frame, bg='#2b2b2b')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # Buttons section
        tk.Label(right_frame, text="Controller Buttons", font=('Arial', 12, 'bold'), 
                fg='white', bg='#2b2b2b').pack(pady=(0, 10))
        
        # Action buttons (A, B, X, Y)
        action_frame = tk.Frame(right_frame, bg='#2b2b2b')
        action_frame.pack(pady=10)
        
        self.btn_a = self.create_button(action_frame, "A (T)", '#ff0000', 0, 0)
        self.btn_b = self.create_button(action_frame, "B (Y)", '#00ff00', 0, 1)
        self.btn_x = self.create_button(action_frame, "X (G)", '#0000ff', 1, 0)
        self.btn_y = self.create_button(action_frame, "Y (H)", '#ffff00', 1, 1)
        
        # System buttons
        system_frame = tk.Frame(right_frame, bg='#2b2b2b')
        system_frame.pack(pady=10)
        
        self.btn_back = self.create_button(system_frame, "Back (Z)", '#ff8800', 0, 0)
        self.btn_start = self.create_button(system_frame, "Start (X)", '#ff8800', 0, 1)
        self.btn_guide = self.create_button(system_frame, "Guide (C)", '#ff8800', 0, 2)
        
        # Triggers
        trigger_frame = tk.Frame(right_frame, bg='#2b2b2b')
        trigger_frame.pack(pady=10)
        
        self.btn_lt = self.create_button(trigger_frame, "LT (U)", '#8800ff', 0, 0)
        self.btn_rt = self.create_button(trigger_frame, "RT (O)", '#8800ff', 0, 1)
        
        # D-Pad
        dpad_frame = tk.Frame(right_frame, bg='#2b2b2b')
        dpad_frame.pack(pady=10)
        
        tk.Label(dpad_frame, text="D-Pad", font=('Arial', 10, 'bold'), 
                fg='white', bg='#2b2b2b').pack()
        
        dpad_buttons_frame = tk.Frame(dpad_frame, bg='#2b2b2b')
        dpad_buttons_frame.pack(pady=5)
        
        self.btn_dpad_up = self.create_button(dpad_buttons_frame, "↑ (1)", '#cccccc', 0, 1)
        self.btn_dpad_left = self.create_button(dpad_buttons_frame, "← (3)", '#cccccc', 1, 0)
        self.btn_dpad_down = self.create_button(dpad_buttons_frame, "↓ (2)", '#cccccc', 1, 2)
        self.btn_dpad_right = self.create_button(dpad_buttons_frame, "→ (4)", '#cccccc', 2, 1)
        
    def create_button(self, parent, text, color, row, col):
        btn = tk.Button(parent, text=text, width=8, height=2, 
                       bg=color, fg='white', font=('Arial', 8, 'bold'),
                       relief=tk.RAISED, bd=2)
        btn.grid(row=row, column=col, padx=2, pady=2)
        return btn
        
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
        center_x, center_y = 100, 100
        knob_x = center_x + (x * 60)  # Scale to joystick area
        knob_y = center_y - (y * 60)  # Invert Y for display
        
        # Keep knob within bounds
        knob_x = max(30, min(170, knob_x))
        knob_y = max(30, min(170, knob_y))
        
        self.left_joystick_canvas.coords('left_knob', knob_x-10, knob_y-10, knob_x+10, knob_y+10)
        
    def press_button_visual(self, button_name, button_obj):
        button_obj.config(relief=tk.SUNKEN, bg='#ffffff')
        self.root.after(100, lambda: button_obj.config(relief=tk.RAISED, bg=button_obj.cget('bg')))
        
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
                    
                # Action buttons
                elif char == 't':
                    self.press_button_visual("A", self.btn_a)
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
                    self.gamepad.update()
                    self.log_status("Button A pressed")
                    
                elif char == 'y':
                    self.press_button_visual("B", self.btn_b)
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
                    self.gamepad.update()
                    self.log_status("Button B pressed")
                    
                elif char == 'g':
                    self.press_button_visual("X", self.btn_x)
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
                    self.gamepad.update()
                    self.log_status("Button X pressed")
                    
                elif char == 'h':
                    self.press_button_visual("Y", self.btn_y)
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
                    self.gamepad.update()
                    self.log_status("Button Y pressed")
                    
                # System buttons
                elif char == 'z':
                    self.press_button_visual("Back", self.btn_back)
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK)
                    self.gamepad.update()
                    self.log_status("Back button pressed")
                    
                elif char == 'x':
                    self.press_button_visual("Start", self.btn_start)
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
                    self.gamepad.update()
                    self.log_status("Start button pressed")
                    
                elif char == 'c':
                    self.press_button_visual("Guide", self.btn_guide)
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE)
                    self.gamepad.update()
                    self.log_status("Guide button pressed")
                    
                # Triggers
                elif char == 'u':
                    self.press_button_visual("LT", self.btn_lt)
                    self.gamepad.left_trigger_float(1.0)
                    self.gamepad.update()
                    self.log_status("LT pressed")
                    
                elif char == 'o':
                    self.press_button_visual("RT", self.btn_rt)
                    self.gamepad.right_trigger_float(1.0)
                    self.gamepad.update()
                    self.log_status("RT pressed")
                    
                # D-Pad
                elif char == '1':
                    self.press_button_visual("D-Pad Up", self.btn_dpad_up)
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
                    self.gamepad.update()
                    self.log_status("D-Pad Up pressed")
                    
                elif char == '2':
                    self.press_button_visual("D-Pad Down", self.btn_dpad_down)
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
                    self.gamepad.update()
                    self.log_status("D-Pad Down pressed")
                    
                elif char == '3':
                    self.press_button_visual("D-Pad Left", self.btn_dpad_left)
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
                    self.gamepad.update()
                    self.log_status("D-Pad Left pressed")
                    
                elif char == '4':
                    self.press_button_visual("D-Pad Right", self.btn_dpad_right)
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
                    self.gamepad.update()
                    self.log_status("D-Pad Right pressed")
                    
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
                    
                # Action buttons
                elif char == 't':
                    self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
                    self.gamepad.update()
                    self.log_status("Button A released")
                    
                elif char == 'y':
                    self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
                    self.gamepad.update()
                    self.log_status("Button B released")
                    
                elif char == 'g':
                    self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
                    self.gamepad.update()
                    self.log_status("Button X released")
                    
                elif char == 'h':
                    self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
                    self.gamepad.update()
                    self.log_status("Button Y released")
                    
                # System buttons
                elif char == 'z':
                    self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK)
                    self.gamepad.update()
                    self.log_status("Back button released")
                    
                elif char == 'x':
                    self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
                    self.gamepad.update()
                    self.log_status("Start button released")
                    
                elif char == 'c':
                    self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE)
                    self.gamepad.update()
                    self.log_status("Guide button released")
                    
                # Triggers
                elif char == 'u':
                    self.gamepad.left_trigger_float(0)
                    self.gamepad.update()
                    self.log_status("LT released")
                    
                elif char == 'o':
                    self.gamepad.right_trigger_float(0)
                    self.gamepad.update()
                    self.log_status("RT released")
                    
                # D-Pad
                elif char == '1':
                    self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
                    self.gamepad.update()
                    self.log_status("D-Pad Up released")
                    
                elif char == '2':
                    self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
                    self.gamepad.update()
                    self.log_status("D-Pad Down released")
                    
                elif char == '3':
                    self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
                    self.gamepad.update()
                    self.log_status("D-Pad Left released")
                    
                elif char == '4':
                    self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
                    self.gamepad.update()
                    self.log_status("D-Pad Right released")
                    
        except Exception as e:
            self.log_status(f"Error in key release: {e}")
            
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
        self.log_status("🎮 Virtual Xbox Controller GUI Ready!")
        self.log_status("Press 'Start Controller' to begin")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        self.stop_controller()
        self.reset_controller()
        self.root.destroy()

if __name__ == "__main__":
    app = GamepadGUI()
    app.run()
