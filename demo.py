"""
C2 Platform Demo Script - Test qilish uchun
"""

import time
import threading
import subprocess
import os
import sys
from datetime import datetime


def print_banner():
    """Banner chiqarish"""
    print("=" * 60)
    print("🎯 C2 PLATFORM DEMO - TA'LIM MAQSADIDA")
    print("=" * 60)
    print("⚠️  Faqat o'z kompyuteringizda sinang!")
    print("⚠️  Noqonuniy ishlatish man etiladi!")
    print("=" * 60)
    print()


def check_python():
    """Python versiyasini tekshirish"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ talab qilinadi!")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def install_dependencies():
    """Dependencies o'rnatish"""
    print("📦 Dependencies o'rnatilmoqda...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Dependencies muvaffaqiyatli o'rnatildi")
            return True
        else:
            print(f"❌ Dependencies o'rnatishda xato: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Xato: {e}")
        return False


def start_server():
    """Server ishga tushirish"""
    print("🚀 Server ishga tushirilmoqda...")
    try:
        # Server papkasiga o'tish
        server_dir = os.path.join(os.getcwd(), "server")
        server_script = os.path.join(server_dir, "app.py")
        
        if not os.path.exists(server_script):
            print("❌ Server script topilmadi!")
            return None
        
        # Server ishga tushirish
        process = subprocess.Popen([
            sys.executable, server_script
        ], cwd=server_dir)
        
        print("✅ Server ishga tushdi")
        print("🌐 Dashboard: http://127.0.0.1:8080")
        return process
        
    except Exception as e:
        print(f"❌ Server ishga tushirishda xato: {e}")
        return None


def start_agent():
    """Agent ishga tushirish"""
    print("🤖 Agent ishga tushirilmoqda...")
    try:
        # Agent papkasiga o'tish
        agent_dir = os.path.join(os.getcwd(), "agent")
        agent_script = os.path.join(agent_dir, "client.py")
        
        if not os.path.exists(agent_script):
            print("❌ Agent script topilmadi!")
            return None
        
        # Agent ishga tushirish
        process = subprocess.Popen([
            sys.executable, agent_script
        ], cwd=agent_dir)
        
        print("✅ Agent ishga tushdi")
        return process
        
    except Exception as e:
        print(f"❌ Agent ishga tushirishda xato: {e}")
        return None


def show_menu():
    """Menu ko'rsatish"""
    print("\\n" + "=" * 40)
    print("📋 DEMO MENU")
    print("=" * 40)
    print("1. 🌐 Dashboard ochish (browser)")
    print("2. 💻 CLI ishga tushirish")
    print("3. 📊 Status ko'rsatish")
    print("4. 🛑 Demo to'xtatish")
    print("=" * 40)


def open_dashboard():
    """Dashboard ochish"""
    try:
        import webbrowser
        webbrowser.open("http://127.0.0.1:8080")
        print("✅ Dashboard brauzerda ochildi")
    except Exception as e:
        print(f"❌ Dashboard ochishda xato: {e}")
        print("🔗 Qo'lda oching: http://127.0.0.1:8080")


def start_cli():
    """CLI ishga tushirish"""
    try:
        cli_script = os.path.join("server", "cli.py")
        subprocess.run([sys.executable, cli_script])
    except Exception as e:
        print(f"❌ CLI xatosi: {e}")


def show_status(server_process, agent_process):
    """Status ko'rsatish"""
    print("\\n📊 DEMO STATUS:")
    print("-" * 30)
    
    if server_process and server_process.poll() is None:
        print("🟢 Server: Ishlamoqda")
    else:
        print("🔴 Server: To'xtagan")
    
    if agent_process and agent_process.poll() is None:
        print("🟢 Agent: Ishlamoqda")  
    else:
        print("🔴 Agent: To'xtagan")
    
    print(f"⏰ Vaqt: {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 30)


def cleanup(server_process, agent_process):
    """Tozalash"""
    print("\\n🧹 Jarayonlar to'xtatilmoqda...")
    
    if server_process:
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
            print("✅ Server to'xtatildi")
        except:
            server_process.kill()
            print("🔥 Server majburan to'xtatildi")
    
    if agent_process:
        try:
            agent_process.terminate()
            agent_process.wait(timeout=5)
            print("✅ Agent to'xtatildi")
        except:
            agent_process.kill()
            print("🔥 Agent majburan to'xtatildi")


def main():
    """Asosiy demo funksiya"""
    print_banner()
    
    # Python versiyasini tekshirish
    if not check_python():
        return
    
    # Dependencies o'rnatish
    if not install_dependencies():
        print("❌ Demo ishga tushmadi - dependencies xatosi")
        return
    
    # Jarayonlarni ishga tushirish
    server_process = start_server()
    if not server_process:
        print("❌ Demo ishga tushmadi - server xatosi")
        return
    
    # Serverga vaqt berish
    print("⏳ Server tayyor bo'lishi kutilmoqda...")
    time.sleep(3)
    
    agent_process = start_agent()
    if not agent_process:
        print("⚠️ Agent ishga tushmadi, lekin server ishlaydi")
    
    # Agentga vaqt berish
    time.sleep(2)
    
    print("\\n🎉 Demo tayyor!")
    print("🌐 Dashboard: http://127.0.0.1:8080")
    
    # Interaktiv menu
    try:
        while True:
            show_menu()
            choice = input("\\nTanlang (1-4): ").strip()
            
            if choice == '1':
                open_dashboard()
            elif choice == '2':
                start_cli()
            elif choice == '3':
                show_status(server_process, agent_process)
            elif choice == '4':
                break
            else:
                print("❌ Noto'g'ri tanlov!")
            
            input("\\nDavom etish uchun Enter bosing...")
    
    except KeyboardInterrupt:
        print("\\n🛑 Demo to'xtatildi")
    
    finally:
        cleanup(server_process, agent_process)
        print("\\n👋 Demo tugadi!")


if __name__ == "__main__":
    main()