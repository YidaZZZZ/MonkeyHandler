"""独立桌面窗口：不依附于浏览器标签页。

优先 pywebview（Windows 上走 Edge WebView2 原生窗口，数据持久化到本机
~/.monkeyhandler/webview）；未安装 pywebview 时回退 Edge/Chrome --app 模式
（Windows 自带 Edge，零依赖，同样是无地址栏的独立窗口）。

Bridge 类通过 pywebview js_api 暴露给页面：生成实例 / 列出实例 / 打开窗口。
生成在 Python 侧调用 LLM（无浏览器跨域限制），配置读 ~/.monkeyhandler/ai.json
或环境变量 MONKEYHANDLER_LLM_*。
"""
from __future__ import annotations

import datetime as _dt
import json as _json
import os
import shutil
import subprocess
import sys
import urllib.request as _request
from pathlib import Path

from .core.llm import OpenAICompatClient
from .domains.fitness.pack import FitnessPack
from .generate import InstanceGenerator
from .render import render_instance

AI_CONFIG = Path.home() / ".monkeyhandler" / "ai.json"


def _load_llm():
    cfg = None
    if AI_CONFIG.exists():
        try:
            cfg = _json.loads(AI_CONFIG.read_text(encoding="utf-8"))
        except Exception:
            cfg = None
    if not cfg:
        b = os.environ.get("MONKEYHANDLER_LLM_BASE_URL")
        k = os.environ.get("MONKEYHANDLER_LLM_API_KEY")
        m = os.environ.get("MONKEYHANDLER_LLM_MODEL")
        if b and k and m:
            cfg = {"base": b, "key": k, "model": m}
    if not cfg:
        return None
    return OpenAICompatClient(cfg["base"], cfg["key"], cfg["model"], timeout=300, max_tokens=7800)


class Bridge:
    """暴露给页面 JS（window.pywebview.api）的 Python 桥。"""

    DATA_HOME = Path.home() / ".monkeyhandler"

    def __init__(self, ui_dir: Path, llm=None):
        self.ui_dir = Path(ui_dir).resolve()
        self.llm = llm
        # N2 数据户口：实例与数据一律住用户主目录，仓库工作树只放代码与知识资产
        self.instances_dir = self.DATA_HOME / "instances"
        self.instances_dir.mkdir(parents=True, exist_ok=True)
        self.manifest = self.instances_dir / "manifest.json"
        self._migrate_legacy()

    def _migrate_legacy(self) -> None:
        old = self.ui_dir / "instances"
        old_manifest = old / "manifest.json"
        if not old_manifest.exists() or self.manifest.exists():
            return
        for f in old.glob("*.html"):
            (self.instances_dir / f.name).write_bytes(f.read_bytes())
        self.manifest.write_text(old_manifest.read_text(encoding="utf-8"), encoding="utf-8")
        for f in old.glob("*"):
            f.unlink()
        old_manifest.unlink(missing_ok=True)
        try:
            old.rmdir()
        except OSError:
            pass

    # ---- 生成 ---------------------------------------------------------
    LOG_DIR = DATA_HOME / "logs"

    def generate(self, goal: str, days: int = 20, time: int = 20,
                 sleep: float = 7.5, stress: str = "mid", level: str = "none",
                 pain: str = "no", style: str = "progress", history: str = "") -> dict:
        import datetime as _dt2
        goal = (goal or "").strip()
        if not goal:
            return {"ok": False, "error": "请先写一句目标。"}
        log = self.LOG_DIR / "generate.log"
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        def _log(msg: str) -> None:
            with log.open("a", encoding="utf-8") as f:
                f.write(f"[{_dt2.datetime.now().isoformat(timespec='seconds')}] {msg}\n")
        llm = self.llm or _load_llm()
        _log(f"开始生成：goal={goal!r} days={days} time={time}")
        if llm is None:
            return {"ok": False, "error": "尚未连接 AI 服务：请到「设置」页填入接口地址与密钥。"}
        gen = InstanceGenerator(self.pack_for(goal), llm=llm)
        answers = {
            "training_experience": level,
            "available_days_per_week": "7",
            "equipment": "home_minimal",
            "injuries": "无" if pain == "no" else pain,
            "sleep_hours": str(sleep),
            "stress_level": stress,
            "chronotype": "neither",
            "motivation_style": style,
            "time_budget": str(time * 7),
        }
        try:
            user, spec, via = gen.generate(goal, answers, horizon_days=int(days), history=history)
            _log(f"生成成功：via={via} 天数={len(spec.days)}")
        except Exception as e:
            _log(f"生成失败：{type(e).__name__}: {e}")
            return {"ok": False, "error": f"生成失败：{e}"}
        slug = _slug(goal)
        html = render_instance(goal=goal, spec=spec, user=user, via=via, storage_key=slug)
        file = self.instances_dir / f"instance-{slug}.html"
        file.write_text(html, encoding="utf-8")
        self._register(slug, file.name, goal, int(days))
        return {"ok": True, "slug": slug, "uri": file.as_uri(), "goal": goal,
                "horizon": int(days), "via": via}

    def _register(self, slug: str, filename: str, goal: str, horizon: int) -> None:
        manifest = self._manifest()
        manifest["instances"] = [x for x in manifest["instances"] if x["slug"] != slug]
        manifest["instances"].append({
            "slug": slug, "file": filename, "goal": goal, "horizon": horizon,
            "created": _dt.datetime.now().isoformat(timespec="seconds"),
        })
        self.manifest.write_text(_json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")

    def _manifest(self) -> dict:
        if self.manifest.exists():
            try:
                return _json.loads(self.manifest.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"instances": []}

    def list_instances(self) -> dict:
        return {"instances": self._manifest()["instances"]}

    def export_data(self, data_json: str) -> dict:
        """N13/D14：把页面汇总的导出 JSON 落到数据户口 exports/。"""
        out_dir = self.DATA_HOME / "exports"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"export-{_dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        path.write_text(data_json, encoding="utf-8")
        return {"ok": True, "path": str(path)}

    def open_uri(self, uri: str) -> None:
        import webview
        if len(webview.windows) < 6:
            webview.create_window("MonkeyHandler · 训练平台", uri, width=1000, height=820)

    def pack_for(self, goal: str) -> FitnessPack:
        return FitnessPack()


def _slug(goal: str) -> str:
    """ASCII 安全的实例标识：中文目标在 Windows 本地服务/文件名下不可靠。"""
    import hashlib
    ascii_part = "".join(ch for ch in goal if ch.isascii() and ch.isalnum())[:16] or "plan"
    digest = hashlib.md5((goal + _dt.datetime.now().isoformat()).encode("utf-8")).hexdigest()[:6]
    return f"{ascii_part}-{digest}"


# ---------------------------------------------------------------------------
# 窗口启动
# ---------------------------------------------------------------------------
def find_ui_dir() -> Path | None:
    # ① PyInstaller 打包资源（_MEIPASS/ui，由 build_exe.py --add-data 提供）
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass and (Path(meipass) / "ui" / "main.html").exists():
        return Path(meipass) / "ui"
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
    webview.create_window("MonkeyHandler", url, js_api=Bridge(ui), width=1120, height=840)
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
