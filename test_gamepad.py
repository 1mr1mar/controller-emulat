import vgamepad as vg
from pynput import keyboard, mouse
import sys
import time
import threading

# إعدادات الحساسية
SENSITIVITY = 1.0  # يمكن تغييرها من 0.1 إلى 2.0
ENABLE_LOGGING = True  # تفعيل/إلغاء تسجيل الحركات

# إنشاء الكونترولر
gamepad = vg.VX360Gamepad()
print("🎮 Virtual Xbox Controller جاهز للعمل!")
print(f"⚙️ حساسية الكونترولر: {SENSITIVITY}")
print(f"📝 تسجيل الحركات: {'مفعل' if ENABLE_LOGGING else 'معطل'}")
print("\n📋 تعليمات الاستخدام:")
print("WASD - تحريك الـ joystick الأيسر (يدعم الحركة القطرية!)")
print("  ↖️ W+A | ↗️ W+D | ↙️ S+A | ↘️ S+D")
print("🖱️ حركة الماوس - تحريك الـ joystick الأيمن") 
print("U/O - الضغط على LT/RT")
print("T/Y/G/H - أزرار A/B/X/Y")
print("Z/X/C - أزرار Back/Start/Guide")
print("1/2/3/4 - D-Pad (أعلى/أسفل/يسار/يمين)")
print("+/- - زيادة/تقليل حساسية الـ joystick")
print("Page Up/Down - زيادة/تقليل حساسية الماوس")
print("M - تفعيل/إلغاء تحكم الماوس")
print("ESC أو Q - الخروج من البرنامج")
print("\n🎯 اضغط على أي مفتاح للبدء...")

# متغيرات عالمية للحساسية والتسجيل
current_sensitivity = SENSITIVITY
logging_enabled = ENABLE_LOGGING

# متغيرات الماوس
mouse_sensitivity = 0.5  # حساسية الماوس (0.1 - 2.0)
mouse_center_x = 960     # مركز الشاشة X
mouse_center_y = 540     # مركز الشاشة Y
mouse_enabled = True     # تفعيل/إلغاء دعم الماوس

# تتبع حالة المفاتيح للحركة القطرية
pressed_keys = set()

# ==========================
# دوال مساعدة للكونترولر
# ==========================
def log_action(action):
    """تسجيل الحركات والأزرار المضغوطة"""
    if logging_enabled:
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {action}")

def press_button(btn):
    log_action(f"🔴 ضغط زر: {btn}")
    gamepad.press_button(btn)
    gamepad.update()

def release_button(btn):
    log_action(f"⚪ إطلاق زر: {btn}")
    gamepad.release_button(btn)
    gamepad.update()

def move_left_joystick(x=0.0, y=0.0):
    # تطبيق الحساسية
    adjusted_x = x * current_sensitivity
    adjusted_y = y * current_sensitivity
    log_action(f"🕹️ Joystick أيسر: X={adjusted_x:.2f}, Y={adjusted_y:.2f}")
    gamepad.left_joystick_float(adjusted_x, adjusted_y)
    gamepad.update()

def move_right_joystick(x=0.0, y=0.0):
    # تطبيق الحساسية
    adjusted_x = x * current_sensitivity
    adjusted_y = y * current_sensitivity
    log_action(f"🕹️ Joystick أيمن: X={adjusted_x:.2f}, Y={adjusted_y:.2f}")
    gamepad.right_joystick_float(adjusted_x, adjusted_y)
    gamepad.update()

def press_lt(value=1.0):
    log_action(f"🔴 LT: {value:.2f}")
    gamepad.left_trigger_float(value)
    gamepad.update()

def press_rt(value=1.0):
    log_action(f"🔴 RT: {value:.2f}")
    gamepad.right_trigger_float(value)
    gamepad.update()

def dpad_press(direction):
    log_action(f"🔴 D-Pad: {direction}")
    gamepad.press_button(direction)
    gamepad.update()

def dpad_release(direction):
    log_action(f"⚪ D-Pad: {direction}")
    gamepad.release_button(direction)
    gamepad.update()

def adjust_sensitivity(change):
    """تغيير حساسية الكونترولر"""
    global current_sensitivity
    new_sensitivity = current_sensitivity + change
    if 0.1 <= new_sensitivity <= 2.0:
        current_sensitivity = new_sensitivity
        print(f"⚙️ الحساسية الجديدة: {current_sensitivity:.1f}")
    else:
        print(f"⚠️ الحساسية يجب أن تكون بين 0.1 و 2.0")

def adjust_mouse_sensitivity(change):
    """تغيير حساسية الماوس"""
    global mouse_sensitivity
    new_sensitivity = mouse_sensitivity + change
    if 0.1 <= new_sensitivity <= 2.0:
        mouse_sensitivity = new_sensitivity
        print(f"🖱️ حساسية الماوس الجديدة: {mouse_sensitivity:.1f}")
    else:
        print(f"⚠️ حساسية الماوس يجب أن تكون بين 0.1 و 2.0")

def on_mouse_move(x, y):
    """معالجة حركة الماوس"""
    if not mouse_enabled:
        return
    
    # حساب المسافة من المركز
    dx = (x - mouse_center_x) / mouse_center_x
    dy = (y - mouse_center_y) / mouse_center_y
    
    # تطبيق الحساسية والحد من القيم
    dx = max(-1.0, min(1.0, dx * mouse_sensitivity))
    dy = max(-1.0, min(1.0, dy * mouse_sensitivity))
    
    # تحديث الـ joystick الأيمن
    move_right_joystick(dx, -dy)  # عكس Y للاتجاه الطبيعي

def toggle_mouse_control():
    """تفعيل/إلغاء تحكم الماوس"""
    global mouse_enabled
    mouse_enabled = not mouse_enabled
    status = "مفعل" if mouse_enabled else "معطل"
    print(f"🖱️ تحكم الماوس: {status}")
    if not mouse_enabled:
        move_right_joystick(0, 0)  # إعادة تعيين الـ joystick الأيمن

def calculate_movement():
    """حساب الحركة بناءً على المفاتيح المضغوطة"""
    x, y = 0.0, 0.0
    
    # تحقق من المفاتيح المضغوطة
    if 'w' in pressed_keys: y += 1.0   # أعلى
    if 's' in pressed_keys: y -= 1.0   # أسفل
    if 'a' in pressed_keys: x -= 1.0   # يسار
    if 'd' in pressed_keys: x += 1.0   # يمين
    
    # تطبيع الحركة القطرية (لتجنب الحركة السريعة جداً قطرياً)
    if x != 0 and y != 0:
        # تقسيم على √2 للحصول على سرعة طبيعية في الحركة القطرية
        x *= 0.707  # 1/√2 ≈ 0.707
        y *= 0.707
    
    return x, y

def update_left_joystick():
    """تحديث الـ joystick الأيسر بناءً على المفاتيح المضغوطة"""
    x, y = calculate_movement()
    move_left_joystick(x, y)

# ==========================
# ربط الكيبورد بالكونترولر
# ==========================
def on_press(key):
    try:
        # مفاتيح الخروج
        if key == keyboard.Key.esc or (hasattr(key, 'char') and key.char == 'q'):
            print("\n👋 جاري الخروج من البرنامج...")
            return False
        
        # مفاتيح التحكم في الحساسية
        if hasattr(key, 'char') and key.char:
            if key.char == '+':  # أو =
                adjust_sensitivity(0.1)
            elif key.char == '-':
                adjust_sensitivity(-0.1)
            elif key.char == 'm':
                toggle_mouse_control()
            elif key.char in ['w', 'a', 's', 'd']:
                # إضافة المفتاح للمفاتيح المضغوطة
                pressed_keys.add(key.char)
                update_left_joystick()
            elif key.char == 'u': press_lt(1.0)    # LT كامل
            elif key.char == 'o': press_rt(1.0)    # RT كامل
            elif key.char == 't': press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            elif key.char == 'y': press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
            elif key.char == 'g': press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
            elif key.char == 'h': press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
            elif key.char == 'z': press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK)
            elif key.char == 'x': press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
            elif key.char == 'c': press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE)
            elif key.char == '1': dpad_press(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
            elif key.char == '2': dpad_press(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
            elif key.char == '3': dpad_press(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            elif key.char == '4': dpad_press(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
        
        # مفاتيح خاصة للحساسية
        if key == keyboard.Key.page_up:
            adjust_mouse_sensitivity(0.1)
        elif key == keyboard.Key.page_down:
            adjust_mouse_sensitivity(-0.1)
    except Exception as e:
        print(f"⚠️ خطأ في معالجة المفتاح: {e}")
        pass

def on_release(key):
    try:
        if hasattr(key, 'char') and key.char:
            if key.char in ['w','s','a','d']:
                # إزالة المفتاح من المفاتيح المضغوطة
                pressed_keys.discard(key.char)
                update_left_joystick()
            elif key.char == 'u': press_lt(0)
            elif key.char == 'o': press_rt(0)
            elif key.char == 't': release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            elif key.char == 'y': release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
            elif key.char == 'g': release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
            elif key.char == 'h': release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
            elif key.char == 'z': release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK)
            elif key.char == 'x': release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
            elif key.char == 'c': release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE)
            elif key.char == '1': dpad_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
            elif key.char == '2': dpad_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
            elif key.char == '3': dpad_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            elif key.char == '4': dpad_release(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
    except Exception as e:
        print(f"⚠️ خطأ في إطلاق المفتاح: {e}")
        pass

# ==========================
# تشغيل مراقبي الكيبورد والماوس
# ==========================
def start_mouse_listener():
    """تشغيل مراقب الماوس في thread منفصل"""
    try:
        with mouse.Listener(on_move=on_mouse_move) as mouse_listener:
            mouse_listener.join()
    except Exception as e:
        print(f"⚠️ خطأ في مراقب الماوس: {e}")

# تشغيل مراقب الماوس في thread منفصل
mouse_thread = threading.Thread(target=start_mouse_listener, daemon=True)
mouse_thread.start()

try:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt:
    print("\n⚠️ تم إيقاف البرنامج بواسطة المستخدم")
except Exception as e:
    print(f"\n❌ خطأ غير متوقع: {e}")
finally:
    print("🔧 تنظيف الموارد...")
    # إعادة تعيين الكونترولر إلى الحالة الافتراضية
    try:
        move_left_joystick(0, 0)
        move_right_joystick(0, 0)
        press_lt(0)
        press_rt(0)
        gamepad.update()
        print("✅ تم تنظيف الكونترولر بنجاح")
    except:
        pass
    print("👋 وداعاً!")
