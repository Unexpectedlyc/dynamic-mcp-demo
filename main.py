from http import server
from pdb import run
from Backend.mcp_server import run_server
from Frontend.app import run_app
import threading
import uvicorn

if __name__ == "__main__":
    run_server()
    run_app()
