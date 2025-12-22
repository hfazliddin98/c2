"""
Test Mobile Payload Generator with ReportLab
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import tkinter as tk
from gui.modules.mobile_payload_module import MobilePayloadGenerator

def log_message(msg):
    print(f"[LOG] {msg}")

if __name__ == '__main__':
    print("="*60)
    print("Testing Mobile Payload Generator")
    print("ReportLab PDF generation")
    print("="*60)
    print()
    
    root = tk.Tk()
    root.title("🤖 Mobile Payload Generator - Test")
    root.geometry("900x700")
    
    generator = MobilePayloadGenerator(root, log_message)
    generator.show_generator()
    
    print("✅ GUI opened successfully!")
    print("📝 Try generating PDF payload from Tab 4")
    print()
    
    root.mainloop()
