# -*- coding: utf-8 -*-
"""MonkeyHandler 桌面版打包入口（PyInstaller）。

产物：单文件 MonkeyHandler.exe——双击即开主平台，无需安装 Python。
构建：python build_exe.py
构建前会校验界面内联脚本的 JS 语法（防语法错误静默出厂；需本机有 node，无则跳过）。
"""
import pathlib
import re

import PyInstaller.__main__


def _check_inline_js() -> bool:
    """构建前校验：提取界面内联脚本交给 node --check（若本机有 node）。"""
    import shutil
    import subprocess
    import tempfile

    html = (pathlib.Path(__file__).parent / "construction" / "demo" / "main.html").read_text(encoding="utf-8")
    scripts = re.findall(r"<script>([\s\S]*?)</script>", html)
    node = shutil.which("node")
    if not node:
        print("（未检测到 node，跳过 JS 语法校验）")
        return True
    ok = True
    tmp_path = None
    for i, script in enumerate(scripts):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(script)
            tmp_path = f.name
        r = subprocess.run([node, "--check", tmp_path], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"JS 语法错误（script #{i}）：", (r.stderr or "")[:300])
            ok = False
    if tmp_path:
        pathlib.Path(tmp_path).unlink(missing_ok=True)
    return ok


if not _check_inline_js():
    raise SystemExit("界面脚本语法校验未通过——请修复后再打包。")

PyInstaller.__main__.run([
    "--noconfirm",
    "--clean",
    "--onefile",
    "--name", "MonkeyHandler",
    # 界面文件打包进 exe（运行时解包到 _MEIPASS/ui）
    "--add-data", "construction/demo;ui",
    # pywebview 及其运行时组件（Windows: pythonnet/clr + WebView2 装载器）
    "--collect-all", "webview",
    "--collect-all", "pythonnet",
    "--hidden-import", "clr",
    "--hidden-import", "monkeyhandler",
    "--hidden-import", "monkeyhandler.app",
    "--hidden-import", "monkeyhandler.cli",
    "entry_exe.py",
])
