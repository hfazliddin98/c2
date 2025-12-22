"""
Auto IP Manager Example - Server IP ni avtomatik boshqarish
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common.auto_ip_manager import AutoIPManager, PublicIPDetector, GitHubGistUploader


def example_1_check_ip():
    """Example 1: Faqat IP tekshirish"""
    print("="*60)
    print("Example 1: Public IP Tekshirish")
    print("="*60)
    print()
    
    try:
        ip = PublicIPDetector.get_public_ip()
        print(f"✅ Sizning public IP: {ip}")
    except Exception as e:
        print(f"❌ Xato: {e}")
    
    print()


def example_2_github_upload():
    """Example 2: GitHub Gist ga upload"""
    print("="*60)
    print("Example 2: GitHub Gist Upload")
    print("="*60)
    print()
    
    # DIQQAT: O'z token va gist ID ni qo'shing!
    GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    GIST_ID = None  # Yangi gist uchun None
    
    if GITHUB_TOKEN.startswith("ghp_xxx"):
        print("⚠️ GitHub token ni kiriting!")
        print("   1. https://github.com/settings/tokens")
        print("   2. Generate new token (classic)")
        print("   3. 'gist' permission")
        print()
        return
    
    try:
        # IP aniqlash
        current_ip = PublicIPDetector.get_public_ip()
        print(f"📍 Current IP: {current_ip}")
        print()
        
        # Uploader yaratish
        uploader = GitHubGistUploader(GITHUB_TOKEN, GIST_ID)
        
        # Upload
        print("📤 GitHub Gist ga yuklanmoqda...")
        result = uploader.upload_config(
            server_ip=current_ip,
            backup_ips=['98.76.54.32', '11.22.33.44'],
            ports={'tcp': 9999, 'http': 8080, 'https': 8443}
        )
        
        if result['success']:
            print("✅ SUCCESS!")
            print(f"\nGist URL: {result['gist_url']}")
            print(f"Raw URL: {result['raw_url']}")
            print(f"\n📋 Agent'da ishlatish:")
            print(f"client.add_ip_update_source('github_gist',")
            print(f"    '{result['raw_url']}')")
        else:
            print(f"❌ Xato: {result['error']}")
            
    except Exception as e:
        print(f"❌ Xato: {e}")
    
    print()


def example_3_auto_manager():
    """Example 3: Full Auto Manager"""
    print("="*60)
    print("Example 3: Auto IP Manager")
    print("="*60)
    print()
    
    # Manager yaratish
    manager = AutoIPManager('example_config.json')
    
    # GitHub setup
    print("📝 GitHub Gist sozlash...")
    
    GITHUB_TOKEN = input("GitHub Token: ").strip()
    GIST_ID = input("Gist ID (yangi: Enter): ").strip() or None
    
    if GITHUB_TOKEN:
        manager.setup_github(GITHUB_TOKEN, GIST_ID)
        print()
        
        # Current IP
        try:
            current_ip = PublicIPDetector.get_public_ip()
            print(f"📍 Current IP: {current_ip}")
            print()
            
            # Update
            manager.update_ip(current_ip)
            
        except Exception as e:
            print(f"❌ Xato: {e}")
    
    print()


def example_4_monitoring():
    """Example 4: Monitoring (test mode)"""
    print("="*60)
    print("Example 4: Monitoring (Test)")
    print("="*60)
    print()
    
    manager = AutoIPManager('example_config.json')
    
    # Settings
    manager.check_interval = 30  # 30 sekund (test uchun)
    
    print(f"⚙️ Check interval: {manager.check_interval} sekund")
    print()
    
    # Initial IP
    try:
        current_ip = PublicIPDetector.get_public_ip()
        manager.current_ip = current_ip
        print(f"📍 Current IP: {current_ip}")
        print()
        
    except Exception as e:
        print(f"❌ Xato: {e}")
        return
    
    # 3 marta tekshirish (test)
    import time
    
    print("🔍 3 marta tekshiriladi (Ctrl+C - to'xtatish)...")
    print()
    
    for i in range(3):
        try:
            print(f"Tekshiruv #{i+1}:")
            changed, new_ip = manager.detect_ip_change()
            
            if changed:
                print(f"  ⚠️ IP o'zgardi: {manager.current_ip} → {new_ip}")
                # manager.update_ip(new_ip)  # Uncomment to upload
            else:
                print(f"  ✓ IP o'zgarmagan: {manager.current_ip}")
            
            if i < 2:
                print(f"  Keyingi tekshiruv: {manager.check_interval} sekunddan keyin...")
                print()
                time.sleep(manager.check_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 To'xtatildi")
            break
    
    print()


def main():
    """Main menu"""
    print("\n" + "="*60)
    print("🤖 AUTO IP MANAGER - EXAMPLES")
    print("="*60)
    print()
    print("Examples:")
    print("  1. Public IP tekshirish")
    print("  2. GitHub Gist upload")
    print("  3. Auto Manager setup")
    print("  4. Monitoring (test)")
    print("  0. Exit")
    print()
    
    choice = input("Tanlov [1-4]: ").strip()
    print()
    
    if choice == '1':
        example_1_check_ip()
    elif choice == '2':
        example_2_github_upload()
    elif choice == '3':
        example_3_auto_manager()
    elif choice == '4':
        example_4_monitoring()
    else:
        print("Exit")


if __name__ == '__main__':
    main()
