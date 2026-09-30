#!/usr/bin/env python3
"""打包「下载即用」demo 包：MonkeyHandler-demo-<日期>.zip

产出（无需编程知识即可使用）：
- index.html   训练平台（双击即用）
- main.html    主平台（双击即用）
- 使用说明 Read me.txt（中英双语说明）

用法：python build_dist.py
输出：construction/demo/dist/
"""
import datetime
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent
DIST = ROOT / "dist"

GUIDE = """MonkeyHandler demo · 使用说明 / Read me
=============================================

【中文】
这是什么？
  两个网页文件：主平台（main.html）与一个训练平台（index.html，20 天脊柱侧弯运动与拉伸）。
  它们不是医疗处方；练习内容为通用运动常识。脊柱侧弯的专向训练（如施罗斯疗法）需要专业评估与认证指导。

怎么用（三步）？
  1. 解压本压缩包到任意文件夹；
  2. 双击 main.html —— 它会在你的浏览器里打开（推荐 Chrome/Edge/Firefox）；
  3. 点「打开训练平台 →」开始第一天训练。

你的数据在哪里？
  全部保存在你自己的浏览器里（本机），不上传、不需要注册。
  想删除：训练平台右上角「重置」即可一键清除。

可选：连接 AI 服务
  主平台 → 设置 → 选择服务商（智谱 GLM / OpenAI / DeepSeek / Ollama / 自定义），
  填入你自己的 API 密钥并保存。密钥只保存在本机浏览器。

声音与语言
  设置页可关闭完成音效；页头按钮可切换 中文 / English。

【English】
What is this?
  Two web pages: the main platform (main.html) and one training app (index.html —
  20 days of scoliosis exercise & stretching). Not medical advice; exercises are
  general fitness common sense. Scoliosis-specific training (e.g. Schroth) requires
  professional assessment and certified guidance.

How to use (3 steps):
  1. Unzip this package anywhere;
  2. Double-click main.html — it opens in your browser (Chrome/Edge/Firefox recommended);
  3. Press "Open training app" and start day one.

Where is my data?
  Entirely in your own browser (local). No upload, no account.
  To delete: press "Reset" in the training app's top bar.

Optional: connect an AI service
  Main platform → Settings → pick a provider (Zhipu GLM / OpenAI / DeepSeek / Ollama / Custom),
  paste your own API key and save. The key stays in this browser.

Sound & language
  Toggle the completion chime in Settings; switch 中文 / English from the header.
"""

def main():
    DIST.mkdir(exist_ok=True)
    name = f"MonkeyHandler-demo-{datetime.date.today().isoformat()}.zip"
    target = DIST / name
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for f in ("index.html", "main.html"):
            z.write(ROOT / f, f)
        z.writestr("使用说明 Read me.txt", GUIDE)
    print(f"OK -> {target}")

if __name__ == "__main__":
    main()
