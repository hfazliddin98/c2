"""
Django Management Command - Start All Servers
python manage.py startservers
"""

from django.core.management.base import BaseCommand
import subprocess
import sys
import os
import time


class Command(BaseCommand):
    help = 'Barcha C2 serverlarni ishga tushirish'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--no-monitor',
            action='store_true',
            help='Monitoring qilmasdan ishga tushirish',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('🚀 C2 Platform - Barcha Serverlar Ishga Tushirilmoqda'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
        
        servers = [
            ('TCP Server', 'server/tcp_server.py', 9999, '🔵'),
            ('HTTP Server', 'server/http_server.py', 8080, '🌐'),
            ('HTTPS Server', 'server/https_server.py', 8443, '🔒'),
            ('WebSocket Server', 'server/websocket_server.py', 8765, '🔌'),
            ('UDP Server', 'server/udp_server.py', 5353, '📡'),
            ('DNS Server', 'server/dns_server.py', 5353, '🌍'),
            ('RTSP Server', 'server/rtsp_server.py', 8554, '📹'),
        ]
        
        processes = []
        
        for name, script, port, icon in servers:
            try:
                if not os.path.exists(script):
                    self.stdout.write(
                        self.style.WARNING(f'{icon} {name:20} ❌ Script topilmadi: {script}')
                    )
                    continue
                
                # Start server
                if os.name == 'nt':  # Windows
                    process = subprocess.Popen(
                        [sys.executable, script],
                        creationflags=subprocess.CREATE_NEW_CONSOLE
                    )
                else:  # Linux/Mac
                    process = subprocess.Popen(
                        [sys.executable, script],
                        start_new_session=True
                    )
                
                processes.append((name, process))
                
                self.stdout.write(
                    self.style.SUCCESS(f'{icon} {name:20} ✅ Ishga tushdi (PID: {process.pid}, Port: {port})')
                )
                
                time.sleep(0.5)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'{icon} {name:20} ❌ Xato: {e}')
                )
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS(f'✅ {len(processes)} ta server ishga tushdi!'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
        
        if not options['no_monitor']:
            self.stdout.write(self.style.WARNING('\n💡 Monitoring: Ctrl+C - to\'xtatish\n'))
            
            try:
                while True:
                    time.sleep(5)
                    # Check processes
                    for name, process in processes:
                        if process.poll() is not None:
                            self.stdout.write(
                                self.style.WARNING(f'\n⚠️  {name} to\'xtadi!')
                            )
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('\n\n🛑 To\'xtatish...\n'))
                for name, process in processes:
                    try:
                        process.terminate()
                    except:
                        pass
