# sender.py
import socket
import PIL.ImageGrab
import io
import argparse
from screeninfo import get_monitors
import mss
import struct

def send_data(sock, data):
    """Helper function to send data with length prefix"""
    size = len(data)
    size_data = struct.pack('!Q', size)  # Pack size as 8-byte unsigned long long
    sock.sendall(size_data)  # Send size first
    sock.sendall(data)       # Send data next

def capture_and_send_screenshot(host: str, port: int = 12345):
    """
    Captures screenshots from all monitors and sends them to a specified host/port
    
    Args:
        host (str): The IP address of the receiving computer
        port (int): The port number to use (default: 12345)
    """
    try:
        # Create TCP socket and connect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        
        # Use mss to capture all monitors
        with mss.mss() as sct:
            monitors = sct.monitors[1:]  # Skip the "all-in-one" monitor at index 0
            num_monitors = len(monitors)
            print(f"Found {num_monitors} monitors")
            
            # Send number of monitors
            sock.sendall(struct.pack('!B', num_monitors))
            
            # Capture and send each monitor's screenshot
            for i, monitor in enumerate(monitors, 1):
                print(f"Capturing monitor {i}...")
                screenshot = sct.grab(monitor)
                img = PIL.Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                
                # Verify image before sending
                test_save = io.BytesIO()
                img.save(test_save, format='PNG')
                img_data = test_save.getvalue()
                print(f"Screenshot {i} size: {len(img_data)} bytes")
                
                # Send the image data
                send_data(sock, img_data)
                print(f"Screenshot from monitor {i} sent successfully")
        
    except Exception as e:
        print(f"Error sending screenshots: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send screenshot to remote computer")
    parser.add_argument("host", help="IP address of the receiving computer")
    parser.add_argument("--port", type=int, default=12345, help="Port number (default: 12345)")
    args = parser.parse_args()
    
    capture_and_send_screenshot(args.host, args.port)
