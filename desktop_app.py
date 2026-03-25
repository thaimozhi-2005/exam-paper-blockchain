"""
Desktop App Launcher — Blockchain Exam Verification System

Opens the web application in a native desktop window using PyWebView.
Auto-starts the Flask backend in a background thread.

Usage:
    python3 desktop_app.py

Requirements:
    pip install pywebview
    # On Ubuntu/Debian Linux, also install:
    # sudo apt install python3-gi python3-gi-cairo gir1.2-webkit2-4.1
"""

import threading
import time
import sys
import os
import signal

def start_backend():
    """Start the Flask backend in a background thread"""
    # Add backend directory to path
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
    sys.path.insert(0, backend_dir)
    os.chdir(backend_dir)
    
    try:
        from app import app
        # Serve on 0.0.0.0 so network devices (Windows) can connect
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Backend failed to start: {e}")
        print("\n💡 Make sure Ganache is running and the contract is deployed.")
        print("   Run: ganache-cli --port 7545 &")
        print("   Then: cd blockchain && truffle migrate --reset")

def wait_for_backend(timeout=15):
    """Wait for the Flask backend to be ready"""
    import urllib.request
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Check on 127.0.0.1 for local health
            urllib.request.urlopen('http://127.0.0.1:5000/api/health')
            return True
        except:
            try:
                urllib.request.urlopen('http://127.0.0.1:5000/')
                return True
            except:
                time.sleep(0.5)
    return False

def main():
    try:
        import webview
    except ImportError:
        print("=" * 60)
        print("❌ PyWebView is not installed!")
        print()
        print("Install it with:")
        print("  pip install pywebview")
        print()
        print("On Ubuntu/Debian Linux, also run:")
        print("  sudo apt install python3-gi python3-gi-cairo gir1.2-webkit2-4.1")
        print("=" * 60)
        sys.exit(1)

    print("=" * 60)
    print("🔗 Blockchain Exam Verification System")
    print("   Starting Desktop Application...")
    print("=" * 60)

    # Start Flask backend in background thread
    print("⏳ Starting backend server...")
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()

    # Wait for backend to be ready
    print("⏳ Waiting for backend to be ready...")
    if wait_for_backend():
        print("✅ Backend is ready!")
    else:
        print("⚠️  Backend may not be fully ready. Opening app anyway...")

    # URL to load - Using port 5000 as Flask serves the frontend
    url = 'http://localhost:5000/login.html'

    print(f"🌐 Opening: {url}")
    print("=" * 60)

    # API to expose to JavaScript
    class JSApi:
        def save_decrypted_paper(self, filename, content_base64):
            """Save decrypted PDF to Downloads folder"""
            try:
                import base64
                
                # Get Downloads folder - Relative to backend
                backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
                download_dir = os.path.join(backend_dir, 'downloads')
                
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)
                
                # Full path
                file_path = os.path.join(download_dir, filename)
                
                # Decode and write
                file_data = base64.b64decode(content_base64)
                
                with open(file_path, "wb") as f:
                    f.write(file_data)
                
                return {"success": True, "path": file_path}
            except Exception as e:
                return {"success": False, "error": str(e)}

    # Create and start the desktop window
    window = webview.create_window(
        'Blockchain Exam Verification System',
        url,
        width=1200,
        height=850,
        resizable=True,
        min_size=(1000, 700),
        text_select=True,
        js_api=JSApi()
    )

    # Start the webview (this blocks until the window is closed)
    webview.start(debug=False)

    print("\n👋 Application closed. Goodbye!")

if __name__ == '__main__':
    main()
