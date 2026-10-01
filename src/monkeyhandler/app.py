"""独立桌面窗口：不依附于浏览器标签页。

优先 pywebview（Windows 上走 Edge WebView2 原生窗口，数据持久化到本机
~/.monkeyhandler/webview）；未安装 pywebview 时回退 Edge/Chrome --app 模式
（Windows 自带 Edge，零依赖，同样是无地址栏的独立窗口）。
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def find_ui_dir() -> Path | None:
    """定位界面文件（construction/demo/main.html）。"""
    here = Path(__file__).resolve()
    for base in (here.parents[2], Path.cwd()):
        cand = base / "construction" / "demo"
        if (cand / "main.html").exists():
            return cand
    env = os.environ.get("MONKEYHANDLER_UI_DIR")
    if env and (Path(env) / "main.html").exists():
        return Path(env)
    return None


def launch() -> str:
    """启动独立桌面窗口并阻塞至关闭；返回实际使用的启动方式。"""
    ui = find_ui_dir()
    if ui is None:
        raise RuntimeError(
            "未找到界面文件（construction/demo/main.html）。"
            "可用环境变量 MONKEYHANDLER_UI_DIR 指定界面目录。"
        )
    url = (ui / "main.html").as_uri()
    try:
        import webview
    except ImportError:
        _app_mode(url)
        return "app-mode（Edge/Chrome 独立窗口）"
    storage = Path.home() / ".monkeyhandler" / "webview"
    storage.mkdir(parents=True, exist_ok=True)
    webview.create_window("MonkeyHandler", url, width=1120, height=840)
    webview.start(private_mode=False, storage_path=str(storage))
    return "pywebview（WebView2 原生窗口）"


def _app_mode(url: str) -> None:
    exe = shutil.which("msedge") or shutil.which("chrome")
    for p in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe"):
        if Path(p).exists():
            exe = p
            break
    if not exe:
        import webbrowser
        webbrowser.open(url)
        return
    profile = Path.home() / ".monkeyhandler" / "app-profile"
    profile.mkdir(parents=True, exist_ok=True)
    subprocess.Popen([exe, f"--app={url}", f"--user-data-dir={profile}", "--window-size=1120,840"])
