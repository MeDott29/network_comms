# sender.py
import socket
import io
import argparse
import struct
import subprocess
import PIL.Image
import tempfile
import os
import re
from pathlib import Path

def get_monitor_geometry(monitor_index):
    """Get monitor geometry using xrandr
    
    Args:
        monitor_index (int): 0-based index of the monitor
        
    Returns:
        tuple: (x, y, width, height) or None if monitor not found
    """
    try:
        # Run xrandr to get display information
        output = subprocess.check_output(['xrandr', '--current']).decode()
        
        # Parse connected displays
        connected_displays = []
        for line in output.split('\n'):
            if ' connected' in line:
                # Look for resolution and position like 1920x1080+0+0
                match = re.search(r'(\d+x\d+\+\d+\+\d+)', line)
                if match:
                    geom = match.group(1)
                    # Parse geometry string (e.g., "1920x1080+0+0")
                    res, pos = geom.split('+', 1)
                    width, height = map(int, res.split('x'))
                    x, y = map(int, pos.split('+'))
                    connected_displays.append((x, y, width, height))
        
        # Return geometry for requested monitor index
        if 0 <= monitor_index < len(connected_displays):
            return connected_displays[monitor_index]
        return None
        
    except subprocess.CalledProcessError:
        print("Error running xrandr")
        return None
    except Exception as e:
        print(f"Error parsing xrandr output: {e}")
        return None

def get_screenshot_maim(output_file, monitor=None):
    """Capture screenshot using maim
    
    Args:
        output_file (str): Path to save the screenshot
        monitor (int, optional): Monitor number to capture (0-based index)
    """
    try:
        if monitor is not None:
            # Get monitor geometry
            geometry = get_monitor_geometry(monitor)
            if geometry:
                x, y, width, height = geometry
                # Use -g for geometry selection
                subprocess.run([
                    'maim',
                    '-g', f'{width}x{height}+{x}+{y}',  # geometry
                    output_file
                ], check=True)
                return True
            else:
                print(f"Could not find geometry for monitor {monitor}")
                return False
        else:
            # Capture full screen if no monitor specified
            subprocess.run(['maim', output_file], check=True)
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error running maim: {e}")
        return False
    except FileNotFoundError:
        print("maim not found - please install with: sudo apt-get install maim")
        return False

def send_data(sock, data):
    """Helper function to send data with length prefix"""
    size = len(data)
    size_data = struct.pack('!Q', size)  # Pack size as 8-byte unsigned long long
    sock.sendall(size_data)  # Send size first
    sock.sendall(data)       # Send data next

def capture_and_send_screenshot(host: str, port: int = 12345, monitor: int = None):
    """
    Captures screenshot and sends it to a specified host/port
    
    Args:
        host (str): The IP address of the receiving computer
        port (int): The port number to use (default: 12345)
        monitor (int, optional): Monitor number to capture (0-based index)
    """
    sock = None
    try:
        # Create a temporary file for the screenshot
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_filename = temp_file.name

        # Try to capture screenshot
        print(f"Capturing screenshot{' for monitor ' + str(monitor) if monitor is not None else ''}...")
        if not get_screenshot_maim(temp_filename, monitor):
            raise Exception("Failed to capture screenshot. Make sure maim is installed: sudo apt-get install maim")

        # Read the screenshot
        img = PIL.Image.open(temp_filename)
        
        # Create TCP socket and connect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        
        # Send number of monitors (1 in this case)
        sock.sendall(struct.pack('!B', 1))
        
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_data = img_byte_arr.getvalue()
        print(f"Screenshot size: {len(img_data)} bytes")
        
        # Send the image data
        send_data(sock, img_data)
        print("Screenshot sent successfully")
        
    except Exception as e:
        print(f"Error sending screenshot: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        if 'temp_filename' in locals():
            try:
                os.unlink(temp_filename)
            except:
                pass
        if sock:
            sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send screenshot to remote computer")
    parser.add_argument("host", help="IP address of the receiving computer")
    parser.add_argument("--port", type=int, default=12345, help="Port number (default: 12345)")
    parser.add_argument("--monitor", type=int, help="Monitor number to capture (0-based index)")
    args = parser.parse_args()
    
    capture_and_send_screenshot(args.host, args.port, args.monitor)