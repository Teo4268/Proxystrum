import socket
import threading

# Hàm đọc thông tin từ file dataset.txt
def load_dataset(file_path="dataset.txt"):
    data = {}
    with open(file_path, "r") as file:
        for line in file:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                if key == "port":
                    data[key] = int(value)
                else:
                    data[key] = value
    return data

# Đọc thông tin từ dataset.txt
config = load_dataset()
MINING_POOL_HOST = config.get("host", "example-pool.com")
MINING_POOL_PORT = config.get("port", 3333)

# Proxy lắng nghe trên tất cả IP và cổng mặc định 8080
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 8080

def forward(source, destination):
    """
    Chuyển tiếp dữ liệu từ source socket sang destination socket.
    """
    try:
        while True:
            data = source.recv(4096)
            if not data:
                break
            print(f"[FORWARD]: {data.decode('utf-8', errors='ignore')}")
            destination.sendall(data)
    except Exception as e:
        print(f"Lỗi chuyển tiếp: {e}")
    finally:
        source.close()
        destination.close()

def handle_client(client_socket):
    """
    Xử lý một kết nối từ máy đào.
    """
    print(f"Máy đào kết nối từ: {client_socket.getpeername()}")
    try:
        # Kết nối tới mining pool
        pool_socket = socket.create_connection((MINING_POOL_HOST, MINING_POOL_PORT))
        print(f"Kết nối tới pool {MINING_POOL_HOST}:{MINING_POOL_PORT}")

        # Tạo hai luồng chuyển tiếp dữ liệu
        threading.Thread(target=forward, args=(client_socket, pool_socket), daemon=True).start()
        threading.Thread(target=forward, args=(pool_socket, client_socket), daemon=True).start()

    except Exception as e:
        print(f"Lỗi khi kết nối tới pool: {e}")
        client_socket.close()

def start_server():
    """
    Khởi động proxy server.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((LISTEN_HOST, LISTEN_PORT))
    server.listen(5)
    print(f"Proxy server đang lắng nghe trên {LISTEN_HOST}:{LISTEN_PORT}...")
    print(f"Kết nối đến pool: {MINING_POOL_HOST}:{MINING_POOL_PORT}")

    try:
        while True:
            client_socket, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()
    except KeyboardInterrupt:
        print("Proxy server đã dừng.")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()
