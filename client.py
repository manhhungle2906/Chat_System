import socket
import threading
import os

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                print("Disconnected from server.")
                break
            if msg.startswith("/file"):
                parts = msg.split(" ", 3)
                sender, filename, filesize = parts[1], parts[2], int(parts[3])
                print(f"📦 Receiving file '{filename}' ({filesize} bytes) from {sender}...")
                with open(f"received_{filename}", "wb") as f:
                    received = 0
                    while received < filesize:
                        chunk = sock.recv(min(1024, filesize - received))
                        if not chunk:
                            break
                        f.write(chunk)
                        received += len(chunk)
                print(f"✅ File '{filename}' received and saved as 'received_{filename}'")
            else:
                print(msg)
        except:
            print("Error receiving message.")
            break

def main():
    ip = input("Enter server IP: ")
    port = 5555

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
    except Exception as e:
        print("Failed to connect to server:", e)
        return

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    try:
        while True:
            msg = input()
            if msg.strip().lower().startswith("/sendfile"):
                parts = msg.strip().split(" ", 2)
                if len(parts) < 3:
                    print("Usage: /sendfile <nickname> <filepath>")
                    continue
                target, filepath = parts[1], parts[2]
                if not os.path.isfile(filepath):
                    print("❌ File not found.")
                    continue
                filename = os.path.basename(filepath)
                filesize = os.path.getsize(filepath)
                sock.send(f"/file {target} {filename} {filesize}".encode())
                with open(filepath, "rb") as f:
                    while chunk := f.read(1024):
                        sock.send(chunk)
                print(f"✅ Sent file '{filename}' to {target}")
            elif msg.strip().lower() == "/quit":
                sock.send("/quit".encode())
                break
            else:
                sock.send(msg.encode())
    except Exception as e:
        print("Error sending message:", e)
    finally:
        sock.close()
        print("Disconnected.")

if __name__ == '__main__':
    main()
