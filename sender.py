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
