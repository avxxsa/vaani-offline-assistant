# actions/system_actions.py
import platform
import subprocess
import os

def get_platform():
    """Detect the operating system"""
    return platform.system()  # Returns 'Windows', 'Linux', or 'Darwin' (macOS)

def open_application(app_name: str):
    """
    Open an application by name.
    Works on both Windows and Linux.
    """
    system = get_platform()
    app_name_lower = app_name.lower()
    
    try:
        if system == "Windows":
            # Windows application mapping
            app_map = {
                "chrome": "chrome.exe",
                "google chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "file explorer": "explorer.exe",
                "explorer": "explorer.exe",
                "cmd": "cmd.exe",
                "command prompt": "cmd.exe",
                "powershell": "powershell.exe",
                "paint": "mspaint.exe",
                "word": "WINWORD.EXE",
                "excel": "EXCEL.EXE",
                "vs code": "code.exe",
                "vscode": "code.exe",
            }
            
            app_to_open = app_map.get(app_name_lower, app_name)
            subprocess.Popen(app_to_open, shell=True)
            return {"success": True, "app": app_name, "platform": "Windows"}
            
        elif system == "Linux":
            # Linux application mapping
            app_map = {
                "chrome": "google-chrome",
                "google chrome": "google-chrome",
                "firefox": "firefox",
                "text editor": "gedit",
                "notepad": "gedit",
                "calculator": "gnome-calculator",
                "files": "nautilus",
                "file manager": "nautilus",
                "terminal": "gnome-terminal",
                "vs code": "code",
                "vscode": "code",
            }
            
            app_to_open = app_map.get(app_name_lower, app_name)
            subprocess.Popen([app_to_open])
            return {"success": True, "app": app_name, "platform": "Linux"}
            
        else:
            return {"success": False, "error": "Unsupported platform"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_system_command(command: str):
    """
    Execute a system command safely.
    Use with caution - only for trusted commands.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return {
            "success": True,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_system_info():
    """Get basic system information"""
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version()
    }