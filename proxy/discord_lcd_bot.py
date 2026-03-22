import discord
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = "YOUR-DISCORD-BOT-TOKEN-HERE"
HTTP_PORT = 8000

intents = discord.Intents.default()
intents.message_content = True

latest_message = "No messages yet"

last_message_time = 0
COOLDOWN = 3
cooldown_warning = False

client = discord.Client(intents=intents)

# HTTP handler - responds to GET requests from the STM32
class MessageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        response = latest_message.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response)

    # silences the default request
    def log_message(self, format, *args):
        pass

def run_http_server():
    server = HTTPServer(('', HTTP_PORT), MessageHandler)
    server.serve_forever()

# start HTTP server in background 
threading.Thread(target=run_http_server, daemon=True).start()

@client.event
async def on_ready():
    print(f"Bot connected as {client.user}")

@client.event
async def on_message(message):
    global latest_message, last_message_time, cooldown_warning

    if message.author == client.user:
        return
    if not message.content.startswith("!lcd"):
        return

    current_time = time.time()

    if current_time - last_message_time < COOLDOWN:
        if not cooldown_warning:
            remaining = COOLDOWN - (current_time - last_message_time)
            await message.channel.send(f"Cooldown active, wait {remaining:.1f}s")
            cooldown_warning = True
        return

    cooldown_warning = False
    last_message_time = current_time

    text = message.content[4:].strip()
    username = message.author.name

    if not text:
        await message.channel.send("Please say something after !lcd")
        return

    # custom word-formatting for the LCD
    words = f"{username}: {text}".split()
    line1, line2 = "", ""
    for word in words:
        if len(line1) + len(word) + 1 <= 16:
            line1 += ("" if not line1 else " ") + word
        elif len(line2) + len(word) + 1 <= 16:
            line2 += ("" if not line2 else " ") + word
        else:
            break

    latest_message = f"{line1}\n{line2}"
    await message.channel.send(f"Sent to LCD: {latest_message}")

client.run(TOKEN)