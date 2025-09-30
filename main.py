from http import server
from Backend.mcp_server import run_server
from Frontend.app import run_app
import threading

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    run_app()
