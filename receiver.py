import socket
import PIL.Image
import io
import argparse
from datetime import datetime

def receive_screenshot(port: int = 12345, save_dir: str = "."):
    """
    Receives and saves a screenshot from the network

    Args:
        port (int): The port number to listen on (default: 12345)
        save_dir (str): Directory to save received screenshots (default: current directory)
    """
    # Create TCP socket and bind to port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)

    print(f"Listening for screenshots on port {port}...")

    while True:
        try:
            # Accept connection
            client_socket, address = server_socket.accept()
            print(f"Connection from {address}")

            # Receive image size first
            size_bytes = client_socket.recv(8)
            size = int.from_bytes(size_bytes, byteorder='big')

            # Receive the image data
            img_data = b""
            while len(img_data) < size:
                chunk = client_socket.recv(min(size - len(img_data), 8192))
                if not chunk:
                    raise ConnectionError("Connection lost")
                img_data += chunk

            # Convert bytes back to image
            image = PIL.Image.open(io.BytesIO(img_data))

            # Save the image with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{save_dir}/screenshot_{timestamp}.png"
            image.save(filename)
            print(f"Screenshot saved as {filename}")

        except Exception as e:
            print(f"Error receiving screenshot: {e}")
        finally:
            client_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Receive screenshots from remote computer")
    parser.add_argument("--port", type=int, default=12345, help="Port number (default: 12345)")
    parser.add_argument("--save-dir", default=".", help="Directory to save screenshots (default: current directory)")
    args = parser.parse_args()

    receive_screenshot(args.port, args.save_dir)
