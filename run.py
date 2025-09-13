#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف تشغيل مبسط لمحاكي الكونترولر الافتراضي
"""

import sys
import os

def check_requirements():
    """فحص المتطلبات"""
    try:
        import vgamepad
        import pynput
        print("✅ جميع المتطلبات مثبتة")
        return True
    except ImportError as e:
        print(f"❌ خطأ في المتطلبات: {e}")
        print("يرجى تثبيت المتطلبات باستخدام: pip install -r requirements.txt")
        return False

def main():
    print("🎮 محاكي كونترولر Xbox الافتراضي")
    print("=" * 40)
    
    if not check_requirements():
        sys.exit(1)
    
    print("🚀 جاري تشغيل المحاكي...")
    print("⚠️ تأكد من تشغيل البرنامج كـ Administrator")
    print("=" * 40)
    
    # تشغيل البرنامج الرئيسي
    try:
        import test_gamepad
    except KeyboardInterrupt:
        print("\n👋 تم إيقاف البرنامج بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()