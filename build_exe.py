# -*- coding: utf-8 -*-
"""MonkeyHandler 桌面版打包入口（PyInstaller）。

产物：单文件 MonkeyHandler.exe——双击即开主平台，无需安装 Python。
构建：python build_exe.py
"""
import PyInstaller.__main__

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
