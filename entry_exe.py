# -*- coding: utf-8 -*-
"""MonkeyHandler.exe 打包入口：直接启动独立桌面窗口。"""
import traceback

try:
    from monkeyhandler.app import launch
    print("启动方式：", launch())
except Exception:
    import traceback
    traceback.print_exc()
    input("启动出错——按回车退出（错误信息已在上方）…")
