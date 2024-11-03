# sender.py
import socket
import PIL.ImageGrab
import io
import argparse

def capture_and_send_screenshot(host: str, port: int = 12345):
    """
    Captures a screenshot and sends it to a specified host/port
    
    Args:
        host (str): The IP address of the receiving computer
        port (int): The port number to use (default: 12345)
    """
    try:
        # Capture the screenshot
        screenshot = PIL.ImageGrab.grab()
        
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Create TCP socket and connect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        
        # Send the size of the image first
        size = len(img_byte_arr)
        sock.send(size.to_bytes(8, byteorder='big'))
        
        # Send the image data
        sock.sendall(img_byte_arr)
        print(f"Screenshot sent successfully to {host}:{port}")
        
    except Exception as e:
        print(f"Error sending screenshot: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send screenshot to remote computer")
    parser.add_argument("host", help="IP address of the receiving computer")
    parser.add_argument("--port", type=int, default=12345, help="Port number (default: 12345)")
    args = parser.parse_args()
    
    capture_and_send_screenshot(args.host, args.port)

# receiver.py
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