import http.server
import socketserver
import webbrowser
import os
import time
import threading

def main():
    port = 8000

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"🚀 Сервер: http://localhost:{port}")
            print("⏹️  Ctrl+C для остановки")
            
            def open_browser():
                time.sleep(1)
                webbrowser.open(f'http://localhost:{port}')
            
            threading.Thread(target=open_browser, daemon=True).start()
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n⏹️  Остановлено")
    except OSError:
        print(f"❌ Порт {port} занят!")

if __name__ == "__main__":
    main()
