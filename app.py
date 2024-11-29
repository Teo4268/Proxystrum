import socket
import threading


def forward(source, destination):
    """
    Chuyển tiếp dữ liệu giữa hai socket.
    """
    try:
        while True:
            data = source.recv(4096)
            if not data:
                break
            destination.sendall(data)
    except Exception as e:
        print(f"Lỗi khi chuyển tiếp: {e}")
    finally:
        source.close()
        destination.close()


def handle_client(client_socket):
    """
    Xử lý kết nối từ phần mềm đào coin.
    """
    try:
        # Nhận thông tin từ phần mềm (yêu cầu kết nối pool)
        request = client_socket.recv(4096).decode()
        print(f"Yêu cầu nhận được từ phần mềm: {request.strip()}")

        # Phân tích thông tin pool từ yêu cầu
        if "mining.subscribe" in request:
            # Lấy host và port từ yêu cầu kết nối
            parts = request.split()
            pool_info = parts[-1]  # Thường là "host:port"
            pool_host, pool_port = pool_info.split(":")
            pool_port = int(pool_port)
            print(f"Kết nối tới pool: {pool_host}:{pool_port}")

            # Kết nối tới pool thực tế
            pool_socket = socket.create_connection((pool_host, pool_port))

            # Chuyển tiếp dữ liệu giữa phần mềm và pool
            threading.Thread(target=forward, args=(client_socket, pool_socket), daemon=True).start()
            threading.Thread(target=forward, args=(pool_socket, client_socket), daemon=True).start()

        else:
            print("Không nhận diện được yêu cầu từ phần mềm!")
            client_socket.close()

    except Exception as e:
        print(f"Lỗi xử lý client: {e}")
        client_socket.close()


def start_proxy(proxy_host, proxy_port):
    """
    Khởi động proxy server.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((proxy_host, proxy_port))
    server.listen(5)
    print(f"Proxy đang lắng nghe trên {proxy_host}:{proxy_port}...")

    try:
        while True:
            client_socket, addr = server.accept()
            print(f"Kết nối từ phần mềm đào: {addr}")
            threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()
    except KeyboardInterrupt:
        print("Proxy đã dừng.")
    finally:
        server.close()


if __name__ == "__main__":
    # Địa chỉ proxy (phần mềm đào sẽ kết nối đến đây)
    proxy_host = "0.0.0.0"  # Proxy lắng nghe trên tất cả các địa chỉ
    proxy_port = 8080       # Cổng proxy (có thể thay đổi tùy ý)

    # Khởi động Proxy
    start_proxy(proxy_host, proxy_port)
