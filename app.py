import os
import subprocess
import sys
import time
import webbrowser
import urllib.request

def check_install_uv():
    try:
        subprocess.check_call(['uv', '--version'], stdout=subprocess.PIPE)
        print("[SUCCESS] uv found:")
    except subprocess.CalledProcessError:
        print("[INFO] uv is not installed. Installing uv...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'uv'])
            print("[SUCCESS] uv installed successfully")
        except subprocess.CalledProcessError:
            print("[ERROR] Failed to install uv. Please install it manually with: pip install uv")
            sys.exit(1)

def check_virtual_env():
    if not os.path.exists('.venv'):
        print("[INFO] Virtual environment not found. Creating virtual environment...")
        try:
            subprocess.check_call(['uv', 'venv'])
            print("[SUCCESS] Virtual environment created successfully")
            
            if os.path.exists('requirements.txt'):
                print("[INFO] Installing dependencies from requirements.txt...")
                subprocess.check_call(['uv', 'pip', 'install', '-r', 'requirements.txt'])
                print("[SUCCESS] All dependencies installed successfully")
            else:
                print("[WARNING] requirements.txt not found, skipping dependency installation")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to create virtual environment or install dependencies: {e}")
            sys.exit(1)
    else:
        print("[SUCCESS] Virtual environment found in project root, skipping dependency installation")
        
def start_streamlit():
    if not os.path.exists('main.py'):
        print("Error: main.py not found")
        print("Please make sure you're in the correct directory")
        sys.exit(1)

    print("Starting Streamlit application with uv...")
    
    # Hide console window on Windows
    if sys.platform == 'win32':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        subprocess.Popen(
            ['uv', 'run', 'streamlit', 'run', './main.py', '--server.headless', 'true'],
            startupinfo=startupinfo,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    else:
        subprocess.Popen(
            ['uv', 'run', 'streamlit', 'run', './main.py', '--server.headless', 'true'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    
    print("[INFO] Waiting for Streamlit to start...")
    
    # Wait for Streamlit to be ready (check if server is responding)
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = urllib.request.urlopen('http://localhost:8501', timeout=1)
            if response.status == 200:
                print("[SUCCESS] Streamlit server is ready!")
                break
        except (urllib.error.URLError, OSError):
            if attempt < max_attempts - 1:
                time.sleep(1)
            else:
                print("[WARNING] Streamlit may not be ready, but opening browser anyway...")
    
    # Open browser
    print("[INFO] Opening browser...")
    try:
        webbrowser.open('http://localhost:8501')
        print("[SUCCESS] Browser opened at http://localhost:8501")
    except Exception as e:
        print(f"[ERROR] Failed to open browser: {e}")
        print("Please manually open http://localhost:8501 in your browser")
    

def get_project_root():
    """Get the project root directory, handling both script and exe execution"""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        exe_path = os.path.dirname(os.path.abspath(sys.executable))
        # Exe is in aiDAPTIV_Files\Installer\, so go up 2 levels to project root
        project_root = os.path.dirname(os.path.dirname(exe_path))
    else:
        # Running as script
        project_root = os.path.dirname(os.path.abspath(__file__))
    return project_root

if __name__ == '__main__':
    # Change to project root directory
    project_root = get_project_root()
    os.chdir(project_root)
    print(f"[INFO] Working directory: {os.getcwd()}")
    
    check_install_uv()
    check_virtual_env()
    start_streamlit()

# uv run pyinstaller --onefile --noconsole --name=app app.py