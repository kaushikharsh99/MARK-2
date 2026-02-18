import subprocess
import sys
import os
import time
import signal

def start_backend():
    print("🚀 Starting FastAPI Backend...")
    return subprocess.Popen([sys.executable, "-m", "backend.main"], cwd=os.getcwd())

def start_frontend():
    print("🎨 Starting React Frontend...")
    # Check if node_modules exists, if not, it might need install
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
        print("📦 Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_dir)
    
    return subprocess.Popen(["npm", "run", "dev"], cwd=frontend_dir)

def main():
    backend_proc = None
    frontend_proc = None
    
    try:
        backend_proc = start_backend()
        time.sleep(2) # Give backend a moment to start
        frontend_proc = start_frontend()
        
        print("\n✅ Jarvis MARK-III is starting up!")
        print("🔗 Backend: http://localhost:8000")
        print("🔗 Frontend: http://localhost:8080")
        print("Press Ctrl+C to shut down all systems.\n")
        
        # Keep the script alive
        backend_proc.wait()
        frontend_proc.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Jarvis...")
        if backend_proc: backend_proc.terminate()
        if frontend_proc: frontend_proc.terminate()
        print("👋 Goodbye, sir.")

if __name__ == "__main__":
    main()
