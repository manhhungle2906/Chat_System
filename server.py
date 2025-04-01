import socket
import threading
from datetime import datetime

HOST = '0.0.0.0'
PORT = 5555

clients = {}  # socket: {nickname, channels: list, active_channel, last_message_time}
channels = {}  # channel: [sockets]
BANNED_WORDS = ['fuck', 'shit', 'bitch', 'asshole']

def timestamp():
    return datetime.now().strftime('%H:%M:%S')

def send(sock, message):
    try:
        sock.send(message.encode())
    except:
        sock.close()
        remove_client(sock)

def broadcast(message, channel, sender=None):
    for client in channels.get(channel, []):
        if client != sender and clients[client]['active_channel'] == channel:
            send(client, message)

def remove_client(sock):
    if sock in clients:
        info = clients[sock]
        nickname = info['nickname']
        for ch in info['channels']:
            if sock in channels.get(ch, []):
                channels[ch].remove(sock)
                if not channels[ch]:
                    del channels[ch]
        del clients[sock]
        for ch in info['channels']:
            broadcast(f"[{timestamp()}] {nickname} has left channel {ch}.", ch)

def handle_commands(sock, msg):
    info = clients[sock]
    nickname = info['nickname']
    active_channel = info['active_channel']

    if msg.startswith("/pm"):
        parts = msg.split(" ", 2)
        if len(parts) < 3:
            send(sock, "Usage: /pm <nickname> <message>")
            return
        target_nick, private_msg = parts[1], parts[2]
        if target_nick == nickname:
            send(sock, "You can't send a private message to yourself.")
            return
        for s, target_info in clients.items():
            if target_info['nickname'] == target_nick:
                send(s, f"[{timestamp()}] [PM from {nickname}]: {private_msg}")
                send(sock, f"[{timestamp()}] [PM to {target_nick}]: {private_msg}")
                return
        send(sock, f"User '{target_nick}' not found.")

    elif msg.startswith("/list"):
        users = [info['nickname'] for s, info in clients.items() if active_channel in info['channels']]
        send(sock, f"Users in channel '{active_channel}': {', '.join(users)}")

    elif msg.startswith("/whoami"):
        send(sock, f"You are '{nickname}', active channel: '{active_channel}', joined channels: {', '.join(info['channels'])}")

    elif msg.startswith("/channels"):
        send(sock, f"Active channels: {', '.join(channels.keys())}")

    elif msg.startswith("/join"):
        parts = msg.split(" ", 1)
        if len(parts) < 2 or not parts[1].strip():
            send(sock, "Usage: /join <channel>")
            return
        new_channel = parts[1].strip()

        if new_channel in channels and len(channels[new_channel]) >= 10:
            send(sock, f"❌ Channel '{new_channel}' is full (max 10 users).")
            return

        if new_channel not in info['channels']:
            info['channels'].append(new_channel)
            channels.setdefault(new_channel, []).append(sock)
            broadcast(f"[{timestamp()}] {nickname} has joined the channel.", new_channel, sock)
        send(sock, f"You have joined channel '{new_channel}'")

    elif msg.startswith("/switch"):
        parts = msg.split(" ", 1)
        if len(parts) < 2 or not parts[1].strip():
            send(sock, "Usage: /switch <channel>")
            return
        new_channel = parts[1].strip()

        if new_channel not in info['channels']:
            # auto join
            if new_channel in channels and len(channels[new_channel]) >= 10:
                send(sock, f"❌ Channel '{new_channel}' is full (max 10 users).")
                return
            info['channels'].append(new_channel)
            channels.setdefault(new_channel, []).append(sock)
            broadcast(f"[{timestamp()}] {nickname} has joined the channel.", new_channel, sock)

        info['active_channel'] = new_channel
        send(sock, f"Switched to channel '{new_channel}'")

    elif msg.startswith("/help"):
        help_text = (
            "\nAvailable commands:\n"
            "/pm <nickname> <message>  - Send a private message\n"
            "/list                     - List users in current channel\n"
            "/whoami                   - Show your nickname and channels\n"
            "/channels                 - Show all active channels\n"
            "/join <channel>           - Join a new channel\n"
            "/switch <channel>         - Switch your active channel\n"
            "/sendfile <user> <path>   - Send file to user\n"
            "/quit                     - Disconnect from the server\n"
            "/help                     - Show this help message\n"
        )
        send(sock, help_text)

    elif msg.startswith("/quit"):
        send(sock, "Goodbye!")
        raise Exception("Client quit")

    else:
        send(sock, "Unknown command. Type /help for a list of commands.")

def handle_client(sock):
    try:
        send(sock, "Enter your nickname:")
        while True:
            nickname = sock.recv(1024).decode().strip()
            if not nickname:
                send(sock, "Nickname cannot be empty. Try again:")
                continue
            if nickname in [info['nickname'] for info in clients.values()]:
                send(sock, "Nickname taken. Try another:")
            else:
                break

        send(sock, "Enter channel to join:")
        while True:
            channel = sock.recv(1024).decode().strip()
            if channel:
                break
            send(sock, "Channel name cannot be empty. Enter again:")

        if channel in channels and len(channels[channel]) >= 10:
            send(sock, f"❌ Channel '{channel}' is full (max 10 users). Disconnecting.")
            sock.close()
            return

        clients[sock] = {
            "nickname": nickname,
            "channels": [channel],
            "active_channel": channel,
            "last_message_time": 0
        }
        channels.setdefault(channel, []).append(sock)

        send(sock, f"Welcome {nickname}! Joined channel '{channel}'. Type /help for commands.")
        broadcast(f"[{timestamp()}] {nickname} has joined the channel.", channel, sock)

        while True:
            msg = sock.recv(1024).decode()
            if not msg:
                break
            if msg.startswith("/file"):
                parts = msg.split(" ", 3)
                if len(parts) < 4:
                    send(sock, "Invalid file header.")
                    continue
                target_nick, filename, filesize = parts[1], parts[2], int(parts[3])
                sender_nick = clients[sock]["nickname"]
                for s, info in clients.items():
                    if info['nickname'] == target_nick:
                        send(s, f"/file {sender_nick} {filename} {filesize}")
                        received = 0
                        while received < filesize:
                            chunk = sock.recv(min(1024, filesize - received))
                            if not chunk:
                                break
                            s.send(chunk)
                            received += len(chunk)
                        send(sock, f"✅ File '{filename}' sent to {target_nick}")
                        break
                else:
                    send(sock, f"❌ User '{target_nick}' not found.")
            elif msg.startswith("/"):
                handle_commands(sock, msg)
            else:
                if not msg.strip():
                    continue
                now = datetime.now().timestamp()
                last_time = clients[sock]["last_message_time"]
                if now - last_time < 1.0:
                    send(sock, "⚠️ Please slow down, you're sending too fast.")
                    continue
                clients[sock]["last_message_time"] = now

                if any(bad in msg.lower() for bad in BANNED_WORDS):
                    send(sock, "❌ Your message contains banned words and was not sent.")
                    continue

                active_channel = clients[sock]['active_channel']
                broadcast(f"[{timestamp()}] [{nickname}]: {msg}", active_channel, sock)
    except Exception as e:
        print(f"Client error or disconnect: {e}")
    finally:
        remove_client(sock)
        sock.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server started on {HOST}:{PORT}")
    while True:
        client_sock, _ = server.accept()
        threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()

if __name__ == '__main__':
    main()
