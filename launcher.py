#!/usr/bin/env python3
"""
🎮 Virtual Xbox Controller Launcher
Choose between GUI and Console versions
"""

import sys
import os

def show_menu():
    print("🎮 Virtual Xbox Controller Launcher")
    print("=" * 50)
    print("Choose your preferred interface:")
    print()
    print("1. 🏆 Professional GUI Version (LATEST!)")
    print("   - Real Xbox controller image")
    print("   - Single-page design")
    print("   - Profiles in header")
    print("   - Mapping controls on same page")
    print("   - Interactive controller display")
    print()
    print("2. 🚀 Enhanced GUI Version")
    print("   - Real Xbox controller image")
    print("   - Customizable button mappings")
    print("   - Profile save/load system")
    print("   - Interactive controller display")
    print("   - Advanced settings management")
    print()
    print("3. 🖥️  Standard GUI Version")
    print("   - Modern graphical interface")
    print("   - Visual feedback for all controls")
    print("   - Easy settings adjustment")
    print("   - Real-time status logging")
    print()
    print("4. 💻 Console Version")
    print("   - Original command-line interface")
    print("   - Lightweight and fast")
    print("   - Full keyboard and mouse support")
    print()
    print("5. ❌ Exit")
    print()
    
def launch_professional_gui():
    try:
        print("🏆 Launching Professional GUI version...")
        import gamepad_gui_pro
        app = gamepad_gui_pro.GamepadGUIPro()
        app.run()
    except ImportError as e:
        print(f"❌ Error importing Professional GUI module: {e}")
        print("Make sure all required packages are installed:")
        print("pip install vgamepad pynput pillow")
    except Exception as e:
        print(f"❌ Error launching Professional GUI: {e}")

def launch_enhanced_gui():
    try:
        print("🚀 Launching Enhanced GUI version...")
        import gamepad_gui_enhanced
        app = gamepad_gui_enhanced.GamepadGUIEnhanced()
        app.run()
    except ImportError as e:
        print(f"❌ Error importing Enhanced GUI module: {e}")
        print("Make sure all required packages are installed:")
        print("pip install vgamepad pynput pillow")
    except Exception as e:
        print(f"❌ Error launching Enhanced GUI: {e}")

def launch_gui():
    try:
        print("🚀 Launching Standard GUI version...")
        import gamepad_gui
        app = gamepad_gui.GamepadGUI()
        app.run()
    except ImportError as e:
        print(f"❌ Error importing GUI module: {e}")
        print("Make sure all required packages are installed:")
        print("pip install vgamepad pynput")
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")

def launch_console():
    try:
        print("🚀 Launching console version...")
        import test_gamepad
    except ImportError as e:
        print(f"❌ Error importing console module: {e}")
        print("Make sure test_gamepad.py exists in the current directory")
    except Exception as e:
        print(f"❌ Error launching console version: {e}")

def main():
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == '1':
                launch_professional_gui()
                break
            elif choice == '2':
                launch_enhanced_gui()
                break
            elif choice == '3':
                launch_gui()
                break
            elif choice == '4':
                launch_console()
                break
            elif choice == '5':
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, 4, or 5.")
                print()
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print()

if __name__ == "__main__":
    main()
