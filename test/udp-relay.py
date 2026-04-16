import socket
import threading

LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 5000

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 8000


def forward(src, dst, name):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    except Exception as e:
        print(f"[{name}] error: {e}")
    finally:
        src.close()
        dst.close()


def handle_client(client_sock):
    try:
        # Connect to target (port 8000)
        target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_sock.connect((TARGET_HOST, TARGET_PORT))

        print("[*] New connection → relaying")
        # Two-way forwarding
        t1 = threading.Thread(target=forward, args=(client_sock, target_sock, "C->T"))
        t2 = threading.Thread(target=forward, args=(target_sock, client_sock, "T->C"))

        t1.start()
        t2.start()

    except Exception as e:
        print(f"[!] Connection error: {e}")
        client_sock.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_HOST, LISTEN_PORT))
    server.listen(5)

    print(f"[*] Listening on {LISTEN_HOST}:{LISTEN_PORT} → forwarding to {TARGET_HOST}:{TARGET_PORT}")

    while True:
        client_sock, addr = server.accept()
        print(f"[+] Connection from {addr}")
        threading.Thread(target=handle_client, args=(client_sock,)).start()


if __name__ == "__main__":
    main()
