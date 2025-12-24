"""
Shifrlash tezligini benchmark qilish
Test: AES-256 encryption performance impact
"""

import time
import json
import sys
from common.crypto import CryptoManager


def generate_test_data(size_kb):
    """Test ma'lumot yaratish"""
    data = {
        "agent_id": "test-agent-123",
        "hostname": "test-machine",
        "platform": "Windows 11",
        "command_result": "x" * (size_kb * 1024)  # KB hajmda ma'lumot
    }
    return json.dumps(data)


def benchmark_encryption(data_sizes):
    """Shifrlash tezligini o'lchash"""
    crypto = CryptoManager(password="test_password_12345")
    
    results = []
    
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║        AES-256 ENCRYPTION PERFORMANCE BENCHMARK           ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    for size_kb in data_sizes:
        # Test ma'lumot yaratish
        test_data = generate_test_data(size_kb)
        data_size_mb = len(test_data) / (1024 * 1024)
        
        print(f"📊 Test: {size_kb}KB ({data_size_mb:.2f}MB) ma'lumot")
        print("─" * 60)
        
        # 1. Shifrlanmagan yuborish (baseline)
        start = time.time()
        for _ in range(10):  # 10 marta takrorlash
            _ = test_data.encode('utf-8')
        baseline_time = (time.time() - start) / 10
        
        # 2. Shifrlangan yuborish
        start = time.time()
        for _ in range(10):
            encrypted = crypto.encrypt(test_data)
        encrypt_time = (time.time() - start) / 10
        
        # 3. Deshifrlash
        encrypted = crypto.encrypt(test_data)
        start = time.time()
        for _ in range(10):
            decrypted = crypto.decrypt(encrypted)
        decrypt_time = (time.time() - start) / 10
        
        # 4. To'liq sikl (encrypt + decrypt)
        start = time.time()
        for _ in range(10):
            encrypted = crypto.encrypt(test_data)
            decrypted = crypto.decrypt(encrypted)
        full_cycle_time = (time.time() - start) / 10
        
        # Overhead hisoblash
        overhead_ms = (full_cycle_time - baseline_time) * 1000
        overhead_percent = ((full_cycle_time - baseline_time) / baseline_time) * 100
        
        # Natijalarni saqlash
        result = {
            'size_kb': size_kb,
            'size_mb': data_size_mb,
            'baseline_ms': baseline_time * 1000,
            'encrypt_ms': encrypt_time * 1000,
            'decrypt_ms': decrypt_time * 1000,
            'full_cycle_ms': full_cycle_time * 1000,
            'overhead_ms': overhead_ms,
            'overhead_percent': overhead_percent
        }
        results.append(result)
        
        # Natijalarni chiqarish
        print(f"  ⏱️  Shifrlanmagan:     {baseline_time*1000:.2f}ms")
        print(f"  🔐 Shifrlash:         {encrypt_time*1000:.2f}ms")
        print(f"  🔓 Deshifrlash:       {decrypt_time*1000:.2f}ms")
        print(f"  🔄 To'liq sikl:       {full_cycle_time*1000:.2f}ms")
        print(f"  ⚡ Overhead:          {overhead_ms:.2f}ms ({overhead_percent:.1f}%)")
        
        # Tezlik (MB/s)
        throughput_encrypt = data_size_mb / encrypt_time
        throughput_decrypt = data_size_mb / decrypt_time
        print(f"  📈 Shifrlash tezligi: {throughput_encrypt:.2f} MB/s")
        print(f"  📉 Deshifrlash tezligi: {throughput_decrypt:.2f} MB/s")
        print()
    
    return results


def print_summary(results):
    """Umumiy natijalarni chiqarish"""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║                    NATIJALAR XULOSASI                      ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    print("📊 OVERHEAD (Qo'shimcha vaqt):\n")
    for r in results:
        print(f"  {r['size_kb']:>6}KB: +{r['overhead_ms']:>8.2f}ms ({r['overhead_percent']:>5.1f}%)")
    
    avg_overhead_ms = sum(r['overhead_ms'] for r in results) / len(results)
    avg_overhead_pct = sum(r['overhead_percent'] for r in results) / len(results)
    
    print(f"\n  O'rtacha: +{avg_overhead_ms:.2f}ms ({avg_overhead_pct:.1f}%)")
    
    print("\n\n🎯 XULOSALAR:\n")
    
    if avg_overhead_pct < 5:
        print("  ✅ JUDA YAXSHi: Shifrlash minimal ta'sir ko'rsatadi (<5%)")
    elif avg_overhead_pct < 10:
        print("  ✅ YAXSHi: Shifrlash qabul qilinadigan ta'sir (<10%)")
    elif avg_overhead_pct < 20:
        print("  ⚠️  O'RTACHA: Shifrlash sezilarli ta'sir (10-20%)")
    else:
        print("  ❌ PAST: Shifrlash katta ta'sir (>20%)")
    
    print(f"\n  Kichik ma'lumotlar (1-10KB):   {results[0]['overhead_ms']:.2f}ms qo'shimcha")
    print(f"  O'rta ma'lumotlar (100KB-1MB): {results[2]['overhead_ms']:.2f}ms qo'shimcha")
    print(f"  Katta ma'lumotlar (10MB+):     {results[-1]['overhead_ms']:.2f}ms qo'shimcha")
    
    print("\n\n💡 TAVSIYALAR:\n")
    print("  1. Kichik ma'lumotlar uchun shifrlash TAVSIYA ETILADI")
    print("     (minimal overhead, yuqori xavfsizlik)")
    print("\n  2. Heartbeat xabarlari uchun shifrlash OPTIONAL")
    print("     (juda kichik hajm, tez-tez yuboriladigan)")
    print("\n  3. Command natijalari uchun shifrlash MAJBURIY")
    print("     (muhim ma'lumotlar, xavfsizlik ustuvor)")
    print("\n  4. Fayl yuklash uchun chunk-based shifrlash")
    print("     (katta fayllarni bo'laklarga bo'lib shifrlash)")
    
    print("\n\n🔐 SHIFRLASH SOZLAMALARI:\n")
    print("  Algoritm:       AES-256 (Fernet)")
    print("  Mode:           CBC")
    print("  Key Derivation: PBKDF2-SHA256 (100,000 iterations)")
    print("  Encoding:       Base64")
    print("\n")


def test_real_scenario():
    """Real stsenariyli test"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║              REAL SSENARIY TESTI                          ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    crypto = CryptoManager(password="agent_password_123")
    
    # Ssenariy 1: Heartbeat xabari
    print("📡 Ssenariy 1: Heartbeat xabari")
    heartbeat = json.dumps({
        "type": "heartbeat_ack",
        "status": "alive",
        "timestamp": "2025-12-24T14:00:00"
    })
    
    start = time.time()
    encrypted = crypto.encrypt(heartbeat)
    decrypted = crypto.decrypt(encrypted)
    total_time = (time.time() - start) * 1000
    
    print(f"  Original size:  {len(heartbeat)} bytes")
    print(f"  Encrypted size: {len(encrypted)} bytes")
    print(f"  Vaqt:           {total_time:.3f}ms")
    print(f"  Overhead:       ~{total_time:.3f}ms\n")
    
    # Ssenariy 2: Command natijasi
    print("📋 Ssenariy 2: Command natijasi (sysinfo)")
    command_result = json.dumps({
        "command_id": "cmd-123",
        "status": "success",
        "result": {
            "hostname": "PC-NAME",
            "platform": "Windows 11",
            "cpu": "Intel Core i7-12700K",
            "ram": "32GB",
            "disk": "1TB SSD"
        }
    })
    
    start = time.time()
    encrypted = crypto.encrypt(command_result)
    decrypted = crypto.decrypt(encrypted)
    total_time = (time.time() - start) * 1000
    
    print(f"  Original size:  {len(command_result)} bytes")
    print(f"  Encrypted size: {len(encrypted)} bytes")
    print(f"  Vaqt:           {total_time:.3f}ms")
    print(f"  Overhead:       ~{total_time:.3f}ms\n")
    
    # Ssenariy 3: Screenshot (base64)
    print("📸 Ssenariy 3: Screenshot ma'lumoti (500KB)")
    screenshot_data = "x" * (500 * 1024)  # 500KB
    screenshot = json.dumps({
        "command_id": "cmd-456",
        "status": "success",
        "result": {"image": screenshot_data}
    })
    
    start = time.time()
    encrypted = crypto.encrypt(screenshot)
    decrypted = crypto.decrypt(encrypted)
    total_time = (time.time() - start) * 1000
    
    print(f"  Original size:  {len(screenshot)/1024:.1f}KB")
    print(f"  Encrypted size: {len(encrypted)/1024:.1f}KB")
    print(f"  Vaqt:           {total_time:.2f}ms")
    print(f"  Overhead:       ~{total_time:.2f}ms\n")


if __name__ == "__main__":
    # Test turli hajmdagi ma'lumotlar
    data_sizes = [1, 10, 100, 1000, 10000]  # KB
    
    print("\n🚀 Benchmark boshlandi...\n")
    
    # Benchmark
    results = benchmark_encryption(data_sizes)
    
    # Umumiy natijalar
    print_summary(results)
    
    # Real sssenariylar
    test_real_scenario()
    
    print("✅ Benchmark tugadi!\n")
