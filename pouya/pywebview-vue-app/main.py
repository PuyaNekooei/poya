import webview
import os
import sys
import errno
import threading
import time
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
from landscape_thermal_print import ThermalReceiptPrinter

class Api:
    def __init__(self):
        self.data = {"message": "Hello from Python!"}
        self.printer = ThermalReceiptPrinter()
    
    def get_data(self):
        return self.data
    
    def set_data(self, data):
        self.data = data
        return {"status": "success", "message": "Data updated successfully"}
    
    def print_receipt(self, receipt_data):
        """Print customer receipt via thermal printer"""
        try:
            print("🖨️ Received print request:", receipt_data)
            customer_data = receipt_data.get('customer', {})
            result = self.printer.print_receipt(customer_data)
            return result
        except Exception as e:
            print(f"❌ Print receipt error: {e}")
            return {"success": False, "error": f"خطا در چاپ: {str(e)}"}
    
    def test_printer(self, test_data=None):
        """Test thermal printer"""
        try:
            print("🖨️ Testing printer...")
            if test_data:
                print(f"Test data: {test_data}")
            result = self.printer.test_printer()
            return result
        except Exception as e:
            print(f"❌ Printer test error: {e}")
            return {"success": False, "error": f"خطا در تست چاپگر: {str(e)}"}

def get_frontend_path():
    """Get the path to the frontend build directory"""
    current_dir = Path(__file__).parent
    frontend_path = current_dir / "frontend" / "dist"
    
    if not frontend_path.exists():
        print("Frontend not built. Please run 'npm run build' in the frontend directory first.")
        sys.exit(1)
    
    return str(frontend_path)

def start_server(port=8001):
    """Start a local HTTP server to serve the frontend files"""
    frontend_path = get_frontend_path()
    
    class SPAHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=frontend_path, **kwargs)
        
        def end_headers(self):
            # Add CORS headers
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            super().end_headers()
        
        def do_GET(self):
            # Handle SPA routing - serve index.html for all non-file requests
            if not os.path.isfile(os.path.join(frontend_path, self.path.lstrip('/'))):
                if not self.path.startswith('/api/'):  # Don't redirect API calls
                    self.path = '/index.html'
            return super().do_GET()
        
        def do_OPTIONS(self):
            # Handle CORS preflight requests
            self.send_response(200)
            self.end_headers()
    
    # Bind in the calling thread so we know the real port before returning the
    # URL. Retry on the next port for any bind failure that is "port unusable":
    # EADDRINUSE (98 on Linux / 10048 on Windows) and WSAEACCES (10013 on
    # Windows, raised when a port is reserved/blocked/held with exclusive bind).
    retryable = {errno.EADDRINUSE, errno.EACCES, 10048, 10013}
    max_attempts = 20

    httpd = None
    for attempt in range(max_attempts):
        try:
            httpd = HTTPServer(("localhost", port), SPAHandler)
            break
        except OSError as e:
            if e.errno in retryable:
                print(f"Port {port} is unavailable ({e}). Trying port {port + 1}")
                port += 1
            else:
                raise

    if httpd is None:
        raise OSError(f"Could not bind a frontend port after {max_attempts} attempts")

    def run_server():
        with httpd:
            print(f"Serving frontend on http://localhost:{port}")
            httpd.serve_forever()

    # Serve in a background thread; the bound port is already known.
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Give the server a moment to start
    time.sleep(1)

    return f"http://localhost:{port}"

def main():
    # Create API instance
    api = Api()
    
    # Start the local HTTP server
    server_url = start_server()
    
    # Create window
    window = webview.create_window(
        title="پویا - سیستم مدیریت رستوران",
        url=server_url,
        js_api=api,
        width=1920,
        height=1080,
        resizable=True,
        min_size=(800, 600),
        maximized=True,
        on_top=False
    )
    
    # Start the application (disable debug to hide inspect window)
    webview.start(debug=False)

if __name__ == "__main__":
    main() 