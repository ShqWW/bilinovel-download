import os
import shutil
import platform

def get_browser_path():
    """自动获取 Chrome 或 Edge 的浏览器可执行文件路径，兼容 Windows/macOS/Linux"""
    browser_paths = {
        "Windows": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        ],
        "Darwin": [  # macOS
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        ],
        "Linux": [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/microsoft-edge",
            "/usr/bin/microsoft-edge-stable"
        ]
    }
    
    system_os = platform.system()
    
    # 1. 先尝试 `shutil.which()` 获取可执行路径
    for browser in ["google-chrome", "google-chrome-stable", "chrome", "msedge", "microsoft-edge"]:
        path = shutil.which(browser)
        if path:
            return path

    # 2. 如果 `shutil.which()` 失败，尝试默认路径
    for path in browser_paths.get(system_os, []):
        if shutil.which(path) or os.path.exists(path):
            return path

    return None