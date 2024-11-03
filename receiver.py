# receiver.py
import socket
import PIL.Image
import io
import argparse
import struct
from datetime import datetime

def receive_exactly(sock, n):
    """Helper function to receive exactly n bytes"""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            raise ConnectionError("Connection closed while receiving data")
        data.extend(packet)
    return data

def receive_data(sock):
    """Helper function to receive length-prefixed data"""
    size_data = receive_exactly(sock, 8)  # Get 8-byte size prefix
    size = struct.unpack('!Q', size_data)[0]  # Unpack as unsigned long long
    print(f"Expecting to receive {size} bytes of image data")
    return receive_exactly(sock, size)

def receive_screenshot(port: int = 12345, save_dir: str = "."):
    """
    Receives and saves screenshots from the network
    
    Args:
        port (int): The port number to listen on (default: 12345)
        save_dir (str): Directory to save received screenshots (default: current directory)
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)
    
    print(f"Listening for screenshots on port {port}...")
    
    while True:
        client_socket = None
        try:
            # Accept connection
            client_socket, address = server_socket.accept()
            print(f"Connection from {address}")
            
            # Receive number of monitors
            num_monitors = struct.unpack('!B', receive_exactly(client_socket, 1))[0]
            print(f"Expecting screenshots from {num_monitors} monitors")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Receive each monitor's screenshot
            for monitor_idx in range(num_monitors):
                print(f"Receiving screenshot {monitor_idx + 1} of {num_monitors}")
                
                # Receive the image data
                img_data = receive_data(client_socket)
                print(f"Received {len(img_data)} bytes for monitor {monitor_idx + 1}")
                
                # Verify the received data is actually a valid image
                try:
                    image = PIL.Image.open(io.BytesIO(img_data))
                    image.verify()  # Verify it's a valid image
                    print(f"Image verified successfully")
                    
                    # Reopen for saving (verify() closes the file)
                    image = PIL.Image.open(io.BytesIO(img_data))
                    
                    filename = f"{save_dir}/screenshot_{timestamp}_monitor{monitor_idx+1}.png"
                    image.save(filename)
                    print(f"Screenshot saved as {filename}")
                except Exception as e:
                    print(f"Error processing image data: {e}")
                    print(f"First 100 bytes of received data: {img_data[:100].hex()}")
                    raise
            
        except Exception as e:
            print(f"Error receiving screenshots: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if client_socket:
                client_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Receive screenshots from remote computer")
    parser.add_argument("--port", type=int, default=12345, help="Port number (default: 12345)")
    parser.add_argument("--save-dir", default=".", help="Directory to save screenshots (default: current directory)")
    args = parser.parse_args()
    
    receive_screenshot(args.port, args.save_dir)