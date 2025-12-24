"""
Scalable Session Manager - 1000+ Agent uchun optimizatsiya
Protocol switching, connection pooling, load balancing
"""

import threading
import time
from datetime import datetime
from collections import defaultdict
from queue import Queue, Empty
import json
import weakref


class ConnectionPool:
    """Har bir protokol uchun connection pool"""
    
    def __init__(self, protocol_name, max_connections=1000):
        self.protocol_name = protocol_name
        self.max_connections = max_connections
        
        # Active connections
        self.active_connections = {}  # {agent_id: connection_obj}
        self.connection_lock = threading.Lock()
        
        # Connection reuse queue
        self.idle_connections = Queue(maxsize=max_connections)
        
        # Statistics
        self.stats = {
            'total_created': 0,
            'total_reused': 0,
            'total_closed': 0,
            'current_active': 0,
            'peak_connections': 0
        }
    
    def get_connection(self, agent_id):
        """Agent uchun connection olish yoki qayta ishlatish"""
        with self.connection_lock:
            # Mavjud connection bormi?
            if agent_id in self.active_connections:
                self.stats['total_reused'] += 1
                return self.active_connections[agent_id]
            
            # Idle connection dan olish
            try:
                conn = self.idle_connections.get_nowait()
                self.active_connections[agent_id] = conn
                self.stats['current_active'] += 1
                
                if self.stats['current_active'] > self.stats['peak_connections']:
                    self.stats['peak_connections'] = self.stats['current_active']
                
                return conn
            except Empty:
                # Yangi connection yaratish
                if self.stats['current_active'] < self.max_connections:
                    conn = self._create_new_connection()
                    self.active_connections[agent_id] = conn
                    self.stats['total_created'] += 1
                    self.stats['current_active'] += 1
                    
                    if self.stats['current_active'] > self.stats['peak_connections']:
                        self.stats['peak_connections'] = self.stats['current_active']
                    
                    return conn
                else:
                    # Max limit reached - kutish yoki xato
                    return None
    
    def release_connection(self, agent_id):
        """Connection ni bo'shatish (reuse uchun)"""
        with self.connection_lock:
            if agent_id in self.active_connections:
                conn = self.active_connections.pop(agent_id)
                self.stats['current_active'] -= 1
                
                # Idle pool ga qo'shish
                try:
                    self.idle_connections.put_nowait(conn)
                except:
                    # Queue to'lgan - yopish
                    self._close_connection(conn)
    
    def close_connection(self, agent_id):
        """Connection ni butunlay yopish"""
        with self.connection_lock:
            if agent_id in self.active_connections:
                conn = self.active_connections.pop(agent_id)
                self._close_connection(conn)
                self.stats['current_active'] -= 1
                self.stats['total_closed'] += 1
    
    def _create_new_connection(self):
        """Yangi connection yaratish (protocol-specific)"""
        # Bu yerda har xil protokollar uchun connection yaratiladi
        return {'created_at': time.time(), 'protocol': self.protocol_name}
    
    def _close_connection(self, conn):
        """Connection ni yopish"""
        # Protocol-specific closing
        pass
    
    def get_stats(self):
        """Pool statistikasi"""
        return {
            'protocol': self.protocol_name,
            **self.stats
        }


class ProtocolSwitchHandler:
    """Protocol switching'ni boshqarish"""
    
    def __init__(self, session_manager):
        self.session_manager = session_manager
        
        # Protocol switch events
        self.switch_queue = Queue()
        self.switch_history = defaultdict(list)  # {agent_id: [switches]}
        
        # Processing thread
        self.processor = threading.Thread(target=self._process_switches, daemon=True)
        self.processor.start()
    
    def handle_protocol_switch(self, agent_id, old_protocol, new_protocol, reason=""):
        """Protocol almashishni boshqarish"""
        switch_event = {
            'agent_id': agent_id,
            'old_protocol': old_protocol,
            'new_protocol': new_protocol,
            'reason': reason,
            'timestamp': time.time()
        }
        
        # Queue ga qo'shish
        self.switch_queue.put(switch_event)
        
        # History'ga yozish
        self.switch_history[agent_id].append(switch_event)
    
    def _process_switches(self):
        """Protocol switch'larni qayta ishlash"""
        while True:
            try:
                event = self.switch_queue.get(timeout=1)
                
                agent_id = event['agent_id']
                old_proto = event['old_protocol']
                new_proto = event['new_protocol']
                
                # Eski connection ni yopish
                if old_proto:
                    self.session_manager.close_protocol_connection(agent_id, old_proto)
                
                # Yangi connection yaratish
                if new_proto:
                    self.session_manager.create_protocol_connection(agent_id, new_proto)
                
                # Log
                print(f"[SWITCH] Agent {agent_id[:8]}: {old_proto} → {new_proto}")
                
            except Empty:
                continue
            except Exception as e:
                print(f"❌ Protocol switch xatosi: {e}")
    
    def get_agent_switches(self, agent_id):
        """Agent'ning barcha protocol switch'lari"""
        return self.switch_history.get(agent_id, [])
    
    def get_total_switches(self):
        """Jami protocol switch'lar soni"""
        total = 0
        for switches in self.switch_history.values():
            total += len(switches)
        return total


class ScalableSessionManager:
    """1000+ agent uchun optimizatsiyalangan session manager"""
    
    def __init__(self):
        # Session storage
        self.sessions = {}  # {agent_id: session_info}
        self.sessions_lock = threading.RLock()
        
        # Protocol-specific connection pools
        self.connection_pools = {
            'tcp': ConnectionPool('tcp', max_connections=2000),
            'https': ConnectionPool('https', max_connections=2000),
            'http': ConnectionPool('http', max_connections=1000),
            'websocket': ConnectionPool('websocket', max_connections=1000),
            'dns': ConnectionPool('dns', max_connections=500),
            'icmp': ConnectionPool('icmp', max_connections=500)
        }
        
        # Protocol switching
        self.protocol_switcher = ProtocolSwitchHandler(self)
        
        # Session monitoring
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_sessions, daemon=True)
        self.monitor_thread.start()
        
        # Load balancing
        self.protocol_load = defaultdict(int)  # {protocol: active_count}
        
        # Statistics
        self.global_stats = {
            'total_sessions': 0,
            'active_sessions': 0,
            'total_protocol_switches': 0,
            'protocol_distribution': defaultdict(int),
            'avg_connections_per_protocol': {},
            'uptime_start': time.time()
        }
    
    def register_session(self, agent_id, agent_data, protocol='tcp'):
        """Yangi session ro'yxatdan o'tkazish"""
        with self.sessions_lock:
            session_info = {
                'agent_id': agent_id,
                'hostname': agent_data.get('hostname', 'unknown'),
                'platform': agent_data.get('platform', 'unknown'),
                'current_protocol': protocol,
                'protocol_history': [protocol],
                'first_seen': time.time(),
                'last_seen': time.time(),
                'status': 'active',
                'total_switches': 0,
                'data_sent': 0,
                'data_received': 0
            }
            
            self.sessions[agent_id] = session_info
            self.global_stats['total_sessions'] += 1
            self.global_stats['active_sessions'] += 1
            self.global_stats['protocol_distribution'][protocol] += 1
            self.protocol_load[protocol] += 1
            
            # Connection pool dan olish
            conn = self.connection_pools[protocol].get_connection(agent_id)
            
            print(f"✅ Session registered: {agent_id[:8]} ({protocol})")
            return True
    
    def switch_protocol(self, agent_id, new_protocol, reason=""):
        """Agent protokolini almashtirish"""
        with self.sessions_lock:
            if agent_id not in self.sessions:
                return False
            
            session = self.sessions[agent_id]
            old_protocol = session['current_protocol']
            
            if old_protocol == new_protocol:
                return True  # O'zgarish yo'q
            
            # Protocol switch handling
            self.protocol_switcher.handle_protocol_switch(
                agent_id, old_protocol, new_protocol, reason
            )
            
            # Session yangilash
            session['current_protocol'] = new_protocol
            session['protocol_history'].append(new_protocol)
            session['total_switches'] += 1
            session['last_seen'] = time.time()
            
            # Load balancing yangilash
            self.protocol_load[old_protocol] -= 1
            self.protocol_load[new_protocol] += 1
            
            # Global stats
            self.global_stats['total_protocol_switches'] += 1
            self.global_stats['protocol_distribution'][new_protocol] += 1
            
            return True
    
    def create_protocol_connection(self, agent_id, protocol):
        """Yangi protocol connection yaratish"""
        if protocol in self.connection_pools:
            conn = self.connection_pools[protocol].get_connection(agent_id)
            return conn is not None
        return False
    
    def close_protocol_connection(self, agent_id, protocol):
        """Protocol connection ni yopish"""
        if protocol in self.connection_pools:
            self.connection_pools[protocol].release_connection(agent_id)
            return True
        return False
    
    def update_session(self, agent_id):
        """Session'ni yangilash (heartbeat)"""
        with self.sessions_lock:
            if agent_id in self.sessions:
                self.sessions[agent_id]['last_seen'] = time.time()
                return True
        return False
    
    def remove_session(self, agent_id):
        """Session'ni o'chirish"""
        with self.sessions_lock:
            if agent_id in self.sessions:
                session = self.sessions.pop(agent_id)
                protocol = session['current_protocol']
                
                # Connection yopish
                self.close_protocol_connection(agent_id, protocol)
                
                # Stats yangilash
                self.global_stats['active_sessions'] -= 1
                self.protocol_load[protocol] -= 1
                
                print(f"❌ Session removed: {agent_id[:8]}")
                return True
        return False
    
    def _monitor_sessions(self):
        """Session'larni monitoring qilish"""
        while self.monitoring_active:
            try:
                time.sleep(30)  # Har 30 soniyada
                
                current_time = time.time()
                timeout_threshold = 120  # 2 minut
                
                with self.sessions_lock:
                    # Timeout bo'lgan session'lar
                    to_remove = []
                    for agent_id, session in self.sessions.items():
                        if current_time - session['last_seen'] > timeout_threshold:
                            session['status'] = 'timeout'
                            to_remove.append(agent_id)
                    
                    # Tozalash
                    for agent_id in to_remove:
                        self.remove_session(agent_id)
                    
                    if to_remove:
                        print(f"⚠️ {len(to_remove)} ta session timeout bo'ldi")
                
            except Exception as e:
                print(f"❌ Monitoring xatosi: {e}")
    
    def get_protocol_stats(self):
        """Har bir protokol uchun statistika"""
        stats = {}
        for protocol, pool in self.connection_pools.items():
            stats[protocol] = {
                'active_sessions': self.protocol_load[protocol],
                'pool_stats': pool.get_stats()
            }
        return stats
    
    def get_global_stats(self):
        """Global statistika"""
        uptime = time.time() - self.global_stats['uptime_start']
        
        return {
            'total_sessions': self.global_stats['total_sessions'],
            'active_sessions': self.global_stats['active_sessions'],
            'total_protocol_switches': self.global_stats['total_protocol_switches'],
            'protocol_distribution': dict(self.global_stats['protocol_distribution']),
            'protocol_load': dict(self.protocol_load),
            'uptime_seconds': uptime,
            'avg_switches_per_session': (
                self.global_stats['total_protocol_switches'] / self.global_stats['total_sessions']
                if self.global_stats['total_sessions'] > 0 else 0
            )
        }
    
    def print_dashboard(self):
        """Real-time dashboard"""
        stats = self.get_global_stats()
        proto_stats = self.get_protocol_stats()
        
        print(f"\n{'='*70}")
        print(f"📊 SCALABLE SESSION MANAGER DASHBOARD")
        print(f"{'='*70}\n")
        
        print(f"📈 Global Statistics:")
        print(f"   Total Sessions: {stats['total_sessions']}")
        print(f"   Active Sessions: {stats['active_sessions']}")
        print(f"   Total Protocol Switches: {stats['total_protocol_switches']}")
        print(f"   Avg Switches/Session: {stats['avg_switches_per_session']:.2f}")
        print(f"   Uptime: {stats['uptime_seconds']:.0f}s")
        
        print(f"\n📡 Protocol Distribution:")
        for protocol, count in stats['protocol_distribution'].items():
            print(f"   {protocol.upper():12} : {count:4} sessions")
        
        print(f"\n🔄 Current Protocol Load:")
        for protocol, count in stats['protocol_load'].items():
            print(f"   {protocol.upper():12} : {count:4} active")
        
        print(f"\n💾 Connection Pool Stats:")
        for protocol, pstats in proto_stats.items():
            pool = pstats['pool_stats']
            print(f"   {protocol.upper():12} :")
            print(f"      Created: {pool['total_created']:4} | "
                  f"Reused: {pool['total_reused']:4} | "
                  f"Active: {pool['current_active']:4} | "
                  f"Peak: {pool['peak_connections']:4}")
        
        print(f"\n{'='*70}\n")


# ==================== SIMULATION ====================

def simulate_1000_agents():
    """1000+ agent simulyatsiyasi"""
    import random
    
    print("🚀 Starting 1000+ Agent Simulation...\n")
    
    manager = ScalableSessionManager()
    
    # 1000 ta agent ro'yxatdan o'tkazish
    print("📝 Registering 1000 agents...")
    protocols = ['tcp', 'https', 'http', 'websocket', 'dns', 'icmp']
    
    for i in range(1000):
        agent_id = f"agent-{i:04d}-{random.randint(1000, 9999)}"
        protocol = random.choice(protocols)
        
        agent_data = {
            'hostname': f'host-{i}',
            'platform': random.choice(['Windows', 'Linux', 'Android'])
        }
        
        manager.register_session(agent_id, agent_data, protocol)
        
        if (i + 1) % 100 == 0:
            print(f"   ✅ {i + 1}/1000 registered")
    
    print("\n✅ 1000 agents registered!\n")
    time.sleep(1)
    
    # Dashboard
    manager.print_dashboard()
    
    # Protocol switching simulation
    print("🔄 Simulating protocol switches...\n")
    
    agent_ids = list(manager.sessions.keys())
    
    for i in range(500):  # 500 ta protocol switch
        agent_id = random.choice(agent_ids)
        new_protocol = random.choice(protocols)
        reason = random.choice([
            'Firewall changed',
            'Network optimization',
            'Large file transfer',
            'Stealth mode',
            'Connection timeout'
        ])
        
        manager.switch_protocol(agent_id, new_protocol, reason)
        
        if (i + 1) % 100 == 0:
            print(f"   🔄 {i + 1}/500 switches completed")
    
    print("\n✅ Protocol switches completed!\n")
    time.sleep(1)
    
    # Final dashboard
    manager.print_dashboard()
    
    # Performance metrics
    print("⚡ Performance Metrics:")
    stats = manager.get_global_stats()
    
    connection_efficiency = 0
    for proto_stats in manager.get_protocol_stats().values():
        pool = proto_stats['pool_stats']
        if pool['total_created'] > 0:
            reuse_rate = pool['total_reused'] / (pool['total_created'] + pool['total_reused'])
            connection_efficiency += reuse_rate
    
    connection_efficiency /= len(protocols)
    
    print(f"   Connection Reuse Rate: {connection_efficiency*100:.1f}%")
    print(f"   Avg Protocol Switches: {stats['avg_switches_per_session']:.2f}")
    print(f"   Total Overhead: {stats['total_protocol_switches']} switches")
    print(f"\n✅ Simulation completed successfully!")


if __name__ == "__main__":
    simulate_1000_agents()
