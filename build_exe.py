# -*- coding: utf-8 -*-
"""MonkeyHandler 桌面版打包入口（PyInstaller）。

版本号唯一来源 = pyproject.toml [project].version。两种构建：

  python build_exe.py             开发者版：dist/MonkeyHandler-dev.exe
                                  设置页版本号 = v<ver>-dev（本地构建 <时间>），窗口标题带「开发版」，不产 zip；
  python build_exe.py --release   发布版：dist/MonkeyHandler.exe + dist/MonkeyHandler-v<ver>-win64.zip
                                  （GitHub Release 资产；设置页版本号 = v<ver>，标题无标注）
                                  发布前自查：工作树干净且已推送、使用说明.txt 版本段已核对。

构建前会校验界面内联脚本的 JS 语法（防语法错误静默出厂；需本机有 node，无则跳过）。
"""
import datetime as _dt
import json as _json
import pathlib
import re
import shutil
import sys
import zipfile

import PyInstaller.__main__

ROOT = pathlib.Path(__file__).parent


def _version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    try:
        import tomllib
        return tomllib.loads(text)["project"]["version"]
    except ModuleNotFoundError:
        m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M)
        if not m:
            raise SystemExit("无法从 pyproject.toml 读取 version。")
        return m.group(1)


def _check_inline_js() -> bool:
    """构建前校验：提取界面内联脚本交给 node --check（若本机有 node）。"""
    import subprocess
    import tempfile

    html = (ROOT / "construction" / "demo" / "main.html").read_text(encoding="utf-8")
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


def _stage_ui(version: str, mode: str) -> pathlib.Path:
    """界面打桩目录：替换版本常量 + 写 _buildinfo.json（app.py 据此定窗口标题）。"""
    src = ROOT / "construction" / "demo"
    stage = ROOT / "build" / f"ui-stage-{mode}"
    if stage.exists():
        shutil.rmtree(stage)
    shutil.copytree(src, stage)
    if mode == "release":
        shown = f"v{version}"
    else:
        shown = f"v{version}-dev（本地构建 {_dt.datetime.now():%Y-%m-%d %H:%M}）"
    html = (stage / "main.html").read_text(encoding="utf-8")
    stamped, n = re.subn(r'const APP_VERSION = "[^"]*";', f'const APP_VERSION = "{shown}";', html)
    if n != 1:
        raise SystemExit("版本号写入失败：main.html 应恰有一处 APP_VERSION 常量。")
    (stage / "main.html").write_text(stamped, encoding="utf-8")
    (stage / "_buildinfo.json").write_text(
        _json.dumps({"mode": mode, "version": f"v{version}", "shown": shown}, ensure_ascii=False),
        encoding="utf-8",
    )
    return stage


def main() -> None:
    mode = "release" if "--release" in sys.argv[1:] else "dev"
    version = _version()
    name = "MonkeyHandler" if mode == "release" else "MonkeyHandler-dev"
    if not _check_inline_js():
        raise SystemExit("界面脚本语法校验未通过——请修复后再打包。")
    stage = _stage_ui(version, mode)

    PyInstaller.__main__.run([
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name", name,
        # 界面打桩目录打包进 exe（运行时解包到 _MEIPASS/ui）
        "--add-data", f"{stage};ui",
        # pywebview 及其运行时组件（Windows: pythonnet/clr + WebView2 装载器）
        "--collect-all", "webview",
        "--collect-all", "pythonnet",
        "--hidden-import", "clr",
        "--hidden-import", "monkeyhandler",
        "--hidden-import", "monkeyhandler.app",
        "--hidden-import", "monkeyhandler.cli",
        "entry_exe.py",
    ])

    dist = ROOT / "dist"
    exe = dist / f"{name}.exe"
    if mode == "release":
        zip_path = dist / f"MonkeyHandler-v{version}-win64.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(exe, exe.name)
            z.write(ROOT / "使用说明.txt", "使用说明 Read me.txt")
        print(f"发布版就绪：{exe}")
        print(f"发布包：{zip_path}")
    else:
        print(f"开发版就绪（不产 zip）：{exe}")


if __name__ == "__main__":
    main()
