@echo off
rem MonkeyHandler 独立桌面窗口（主平台 + 训练平台）
cd /d "%~dp0"
python -m monkeyhandler app
if errorlevel 1 (
  echo.
  echo 启动失败：请先安装运行时组件  python -m pip install -e ".[app]"
  pause
)
