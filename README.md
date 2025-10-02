# C2 Platform - Command and Control Framework

Bu Python'da yozilgan C2 (Command and Control) platformasidir. Bu loyiha faqat ta'lim maqsadida yaratilgan.

## ⚠️ Ogohlantirish

Bu dastur faqat **ta'lim va tadqiqot maqsadlarida** ishlatilishi kerak. Noqonuniy faoliyat uchun foydalanish man etiladi.

## Tarkibi

- `server/` - C2 server komponenti
- `agent/` - Target mashinada ishlaydigan agent
- `common/` - Umumiy funksiyalar va utilities
- `web/` - Web dashboard interface

## O'rnatish

```bash
pip install -r requirements.txt
```

## Ishlatish

### Server ishga tushirish:
```bash
cd server
python app.py
```

### Web dashboard:
```bash
cd web
python dashboard.py
```

## Xususiyatlar

- [x] Asosiy loyiha strukturasi
- [x] Flask server
- [x] Agent client  
- [x] HTTP/JSON aloqa protokoli
- [x] Web dashboard
- [x] CLI interface
- [x] Asosiy komandalar (exec, sysinfo, file operations)
- [x] Demo script

## Qo'shimcha Fayllar

- `demo.py` - To'liq demo ishga tushirish
- `start_cli.bat` - CLI ishga tushirish
- `STRUCTURE.md` - Loyiha strukturasi haqida

## Demo Ishga Tushirish

Eng oson yo'l:
```bash
python demo.py
```

Bu script avtomatik ravishda:
1. Dependencies o'rnatadi
2. Server ishga tushiradi
3. Agent ulaydi
4. Interaktiv menu ochadi

## Litsenziya

Bu loyiha faqat ta'lim maqsadida yaratilgan.