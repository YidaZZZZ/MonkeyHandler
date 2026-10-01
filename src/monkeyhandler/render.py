"""实例渲染器：InstanceSpec → 单页自包含 HTML（双击即用，数据仅存本机浏览器）。"""
from __future__ import annotations

import datetime as _dt
import html as _html
import json as _json

from .generate import InstanceSpec
from .core.user_model import UserModel

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#f4f7f8;--card:#fff;--ink:#1d2a33;--muted:#52616c;--accent:#0f766e;--accent-soft:#e0f2f0;
      --warn-bg:#fef3c7;--warn-ink:#92400e;--dan-bg:#fee2e2;--dan-ink:#991b1b;--ok-bg:#dcfce7;--ok-ink:#166534;
      --line:#dde5e9}
*{box-sizing:border-box}
body{margin:0;background:linear-gradient(180deg,#eef4f2,#f4f7f8 300px);color:var(--ink);
     font:16px/1.65 system-ui,-apple-system,"Segoe UI","Microsoft YaHei",sans-serif}
header{padding:18px 22px;background:rgba(255,255,255,.85);backdrop-filter:blur(10px);border-bottom:1px solid var(--line);
       position:sticky;top:0}
header .g{font-weight:800;font-size:17px}
header .s{color:var(--muted);font-size:13px;margin-top:2px}
main{max-width:820px;margin:0 auto;padding:20px 16px 60px}
.card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:22px;margin:14px 0;
      box-shadow:0 1px 2px rgba(16,42,51,.05),0 3px 10px rgba(16,42,51,.06);animation:rise .28s ease both}
h1{font-size:22px;margin:6px 0;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
h2{font-size:16.5px;margin:0 0 10px;color:#115e59;display:flex;align-items:center;gap:7px}
.tag{display:inline-block;background:var(--accent-soft);color:var(--accent);border-radius:999px;padding:1px 10px;font-size:13px}
.muted{color:var(--muted)}
.banner{border-radius:12px;padding:11px 15px;margin:10px 0;font-size:14.5px}
.banner.warn{background:var(--warn-bg);color:var(--warn-ink)}
.banner.dan{background:var(--dan-bg);color:var(--dan-ink)}
.bar{height:9px;background:var(--line);border-radius:999px;overflow:hidden;margin:8px 0}
.bar>i{display:block;height:100%;background:var(--accent);border-radius:999px;transition:width .6s ease}
.ex{border-top:1px dashed var(--line);padding:10px 0}
.ex:first-child{border-top:none}
.ex .h{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:baseline}
.ex .n{font-weight:600}.ex .d{color:var(--accent);font-size:14px;white-space:nowrap}
details{margin-top:5px}summary{cursor:pointer;color:var(--accent);font-size:14px}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left}
th{color:var(--muted)}
button{font:inherit;cursor:pointer;border-radius:9px;border:1px solid var(--line);background:#fff;padding:8px 14px;
       transition:background .15s,transform .1s}
button:hover{background:var(--accent-soft)}
button:active{transform:scale(.98)}
button.primary{background:var(--accent);border-color:var(--accent);color:#fff}
button.ghost{border-color:transparent;color:var(--muted)}
select,input[type=text]{font:inherit;padding:8px;border:1px solid var(--line);border-radius:9px;width:100%;max-width:420px}
.banner,button,:focus-visible{scroll-margin:20px}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
@keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion: reduce){*{animation:none!important;transition:none!important}}
</style>
</head>
<body>
<header>
  <div class="g">__TITLE__</div>
  <div class="s">MonkeyHandler 生成的训练平台（阶段性产物） · __GEN_DATE__ 生成 · 路径：__VIA__ · 非医疗建议</div>
</header>
<main id="app"></main>
<footer style="max-width:820px;margin:0 auto;padding:16px;color:var(--muted);font-size:13px">
数据仅保存在本机浏览器，不上传。练习内容为通用运动常识，不构成医疗处方；脊柱侧弯的专向训练（如施罗斯疗法）需要专业评估与认证指导。
如果出现伤害自己的念头：心理援助热线 12356（中国，24 小时），或前往当地急诊。
</footer>
<script>
"use strict";
const DATA = __DATA__;
const KEY = "mhInst-__SLUG__";
let st = JSON.parse(localStorage.getItem(KEY) || "null") || {days: {}};
function save(){ localStorage.setItem(KEY, JSON.stringify(st)); }
function esc(s){ return (s||"").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c])); }
function done(d){ return !!(st.days[d] && st.days[d].done); }
function cur(){ for(let d=1; d<=DATA.horizon_days; d++){ if(!done(d)) return d; } return DATA.horizon_days + 1; }
function everHighPain(){ return Object.values(st.days).some(r => r.done && r.pain >= 4); }
function taper(d){ return d >= DATA.taper_from; }
function render(){
  const app = document.getElementById("app");
  const d = Math.min(cur(), DATA.horizon_days);
  const graduated = cur() > DATA.horizon_days;
  const locked = everHighPain();
  const dayData = DATA.days[d-1];
  let itemsHtml = "";
  if(!graduated){
    let items = dayData.items;
    const lightDay = locked || DATA.intensity <= 0.5;
    if(lightDay) items = items.slice(0, Math.min(3, items.length));
    itemsHtml = items.map(it =>
      `<div class="ex"><div class="h"><span class="n">${esc(it.name)}</span><span class="d">${esc(it.dur)}</span></div>
       <div class="muted" style="font-size:14.5px">${esc(it.cue)}</div>
       <details><summary>为什么练这个？</summary><div class="muted">${esc(it.why)}</div></details></div>`).join("");
  }
  let banners = "";
  if(locked) banners += `<div class="banner dan"><b>安全锁定中</b>：出现过疼痛 ≥4 → 只保留前几项，停止加量；建议就医评估后再恢复。</div>`;
  if(taper(d) && !graduated) banners += `<div class="banner warn"><b>减量段</b>：只做动作质量，不追负荷——变强发生在恢复里。</div>`;
  const doneN = Object.values(st.days).filter(r => r.done).length;
  const percent = Math.round(doneN / DATA.horizon_days * 100);
  let body;
  if(graduated){
    body = `<div class="card"><h2>周期完成 🎉</h2>
      <p>带着这份记录做一次专业评估；下一个周期会基于这些数据重新生成。</p>
      <p class="muted">共完成 ${doneN}/${DATA.horizon_days} 天。数据仍保存在本机浏览器。</p></div>`;
  } else {
    const doneToday = done(d);
    const r = st.days[d];
    body = `<div class="card">
      <div class="bar"><i style="width:${percent}%"></i></div>
      <p class="muted" style="margin:4px 0 0">完成 ${doneN}/${DATA.horizon_days}（${percent}%）</p></div>
      <div class="card">
        <h2>第 ${d} 天 · ${esc(dayData.focus)}</h2>
        ${itemsHtml}
      </div>
      <div class="card">
        <h2>${doneToday ? "今日已完成" : "完成后打卡"}</h2>
        ${doneToday ? `<div class="banner ok" style="background:var(--ok-bg);color:var(--ok-ink)">完成 ✓　RPE ${r.rpe} · 疼痛 ${r.pain}${r.note ? " · 「" + esc(r.note) + "」" : ""}</div>`
        : `<p><label>自觉强度 RPE（1-10）<br><select id="rpe">${[1,2,3,4,5,6,7,8,9,10].map(v=>`<option ${v===5?"selected":""}>${v}</option>`).join("")}</select></label></p>
           <p><label>疼痛（0-10；达到 4 分触发保护）<br><select id="pain">${[0,1,2,3,4,5,6,7,8,9,10].map(v=>`<option ${v===0?"selected":""}>${v}</option>`).join("")}</select></label></p>
           <p><label>一句感受（可选）<input type="text" id="note"></label></p>
           <p><button class="primary" id="submit">提交打卡</button></p>`}
      </div>`;
  }
  const rows = DATA.days.map(x => {
    const r = st.days[x.day];
    const s = r && r.done ? "✓" : (x.day === d && !graduated ? "今天" : "");
    return `<tr><td>${x.day}</td><td>${esc(x.phase)}</td><td>${esc(x.focus)}</td><td>${s}</td><td>${r&&r.done?r.rpe:"—"}</td><td>${r&&r.done?r.pain:"—"}</td></tr>`;
  }).join("");
  app.innerHTML = `
    <h1><span class="tag">训练平台</span><span class="tag">${esc(DATA.goal).slice(0,18)}…</span></h1>
    ${banners}
    ${body}
    <div class="card"><h2>全部日程</h2>
      <table><thead><tr><th>天</th><th>阶段</th><th>焦点</th><th>状态</th><th>RPE</th><th>疼痛</th></tr></thead><tbody>${rows}</tbody></table></div>
    <div class="card"><h2>计划依据（可解释）</h2><p class="muted">${esc(DATA.rationale)}</p>
      ${DATA.safety.map(s=>`<p class="muted small">· ${esc(s)}</p>`).join("")}</div>`;
  const sub = document.getElementById("submit");
  if(sub) sub.addEventListener("click", () => {
    const pain = +document.getElementById("pain").value;
    st.days[d] = {done:true, rpe:+document.getElementById("rpe").value, pain,
                  note: document.getElementById("note").value.trim(), ts: Date.now()};
    save(); render();
    if(pain >= 4) setTimeout(() => alert("疼痛达到 4 分及以上：计划已停止加量。建议就医评估——这比任何进度都重要。"), 60);
  });
}
render();
</script>
</body>
</html>
"""


def render_instance(goal: str, spec: InstanceSpec, user: UserModel, via: str,
                    storage_key: str | None = None) -> str:
    """把 InstanceSpec 渲染为单页自包含 HTML 实例（数据仅存本机浏览器）。

    storage_key：本实例在浏览器 localStorage 中的隔离键；缺省由目标+时间派生。
    """
    slug = storage_key or _slug(goal)
    data = spec.model_dump()
    data["taper_from"] = spec.horizon_days - max(2, round(spec.horizon_days * 0.1)) + 1
    title = f"MonkeyHandler 训练平台 · {_truncate(goal, 24)}"
    gen_date = _dt.date.today().isoformat()
    via_label = {"llm": "LLM 生成", "rule": "离线规则模板"}.get(via, via)
    return (TEMPLATE
            .replace("__TITLE__", _html.escape(title))
            .replace("__GEN_DATE__", _html.escape(gen_date))
            .replace("__VIA__", _html.escape(via_label))
            .replace("__SLUG__", _html.escape(slug))
            .replace("__DATA__", _json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))


def _slug(goal: str) -> str:
    base = _html.escape(goal, quote=True)
    base = _html.unescape(base)
    cleaned = "".join(ch for ch in base if ch.isalnum())[:24] or "goal"
    return f"{cleaned}-{_dt.date.today().isoformat()}"


def _truncate(text: str, n: int) -> str:
    return text if len(text) <= n else text[:n] + "…"
