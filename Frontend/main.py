"""Portfolio website: frontend only, written fully in Python (NiceGUI).

Run:
    pip install -r requirements.txt
    python main.py
Then open http://localhost:8080

Your text/details live in site_content.py. This file is only design + behaviour.
The "Ask Anything" page (/chat) talks to the FastAPI backend (POST /chat, POST /upload-jd).
"""
import asyncio
import json
import os
import time
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import httpx
from nicegui import app, ui

from site_content import GITHUB, PROFILE

# Where the FastAPI backend runs (override with: set BACKEND_URL=http://host:port)
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Visitor counter is saved in this file (created automatically next to main.py)
VISITS_FILE = Path(__file__).with_name("visits.json")

# Which resume the recruiter sees: key (sent to the backend) -> (icon, label)
PROFILE_CHOICES = {
    "it": ("computer", "IT / Software"),
    "core": ("build", "Core / Mechanical"),
}

NAV = [("About", "about"), ("Skills", "skills"), ("Projects", "projects"), ("Contact", "contact")]

# ----------------------------------------------------------------------------
# 1. STYLES  (palette: black / purple / white)
# ----------------------------------------------------------------------------
FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    "family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500"
    '&family=Space+Grotesk:wght@500;700&display=swap">'
)

CSS = """
:root{
  --bg:#08070d; --card:rgba(21,18,34,.78);
  --line:rgba(167,139,250,.16); --line-strong:rgba(167,139,250,.5);
  --ink:#f6f4ff; --muted:#a7a3bd;
  --v1:#a78bfa; --v2:#8b5cf6; --v3:#6d28d9;
  --display:'Space Grotesk',system-ui,sans-serif;
  --body:'Inter',system-ui,sans-serif;
  --mono:'JetBrains Mono',ui-monospace,monospace;
  --ease:cubic-bezier(.2,.7,.2,1);
  --pad:clamp(18px,5vw,56px);
  --nav-h:68px;
  color-scheme:dark;
  --accent-text:#a78bfa; --card-shadow:none;
  --glow-a:rgba(139,92,246,.30); --glow-b:rgba(109,40,217,.20); --glow-c:rgba(139,92,246,.17);
  --name-grad:linear-gradient(180deg,#fff 45%,#c4b5fd);
  --btn-bg:#fff; --btn-ink:#0a0812;
  --orb-face:linear-gradient(145deg,#1d1635,#0b0914); --ring-hi:#fff;
  --track:rgba(255,255,255,.08); --composer:rgba(21,18,34,.92); --hover-bg:rgba(167,139,250,.13);
}
html[data-theme=light]{
  color-scheme:light;
  --bg:#faf9ff; --card:rgba(255,255,255,.92); --line:rgba(109,40,217,.14); --line-strong:rgba(109,40,217,.42);
  --ink:#14111f; --muted:#5f5a78;
  --accent-text:#6d28d9; --card-shadow:0 2px 14px rgba(76,29,149,.07);
  --glow-a:rgba(139,92,246,.16); --glow-b:rgba(167,139,250,.14); --glow-c:rgba(139,92,246,.09);
  --name-grad:linear-gradient(180deg,#14111f 40%,#6d28d9);
  --btn-bg:#14111f; --btn-ink:#fff;
  --orb-face:linear-gradient(145deg,#ffffff,#ede9fe); --ring-hi:#c4b5fd;
  --track:rgba(109,40,217,.12); --composer:rgba(255,255,255,.95); --hover-bg:rgba(109,40,217,.08);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
html,body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);-webkit-font-smoothing:antialiased}
.nicegui-content{padding:0!important;gap:0!important;align-items:stretch!important}
a.btn,a.back,a.card,a.nav-link,a.brand,a.fab{text-decoration:none!important;color:inherit}
:focus-visible{outline:2px solid var(--v1);outline-offset:3px}
::selection{background:var(--v2);color:#fff}

/* ---------- background glow (cheap: gradients only, no blur filters) ---------- */
.glow{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden;
  background:
   radial-gradient(900px 520px at 50% -8%,var(--glow-a),transparent 70%),
   radial-gradient(760px 520px at 100% 100%,var(--glow-b),transparent 70%)}
.glow::after{content:"";position:absolute;width:55vmax;height:55vmax;left:-18vmax;top:32vh;border-radius:50%;
  background:radial-gradient(circle,var(--glow-c),transparent 65%);will-change:transform;
  animation:drift 26s ease-in-out infinite alternate}
@keyframes drift{to{transform:translate3d(16vmax,-8vmax,0) scale(1.15)}}

/* ---------- top navigation ---------- */
.nav{position:fixed;top:0;left:0;right:0;z-index:50;background:var(--bg);border-bottom:1px solid var(--line)}
.nav-in{max-width:1200px;margin:0 auto;height:var(--nav-h);padding:0 var(--pad);display:flex;align-items:center;gap:20px}
.brand{display:flex;align-items:center;gap:10px;font-family:var(--display);font-weight:700;font-size:1.05rem;letter-spacing:-.01em}
.brand-mark{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;font-size:.78rem;font-weight:700;
  background:linear-gradient(135deg,var(--v1),var(--v3));color:#fff}
.nav-links{display:flex;gap:4px;margin:0 auto}
.nav-link{padding:8px 14px;border-radius:10px;font-size:.92rem;color:var(--muted)!important;transition:color .2s,background .2s}
.nav-link:hover{color:var(--ink)!important;background:var(--hover-bg)}
.clock{display:flex;align-items:center;gap:8px;padding:6px 12px;border-radius:999px;border:1px solid var(--line);
  font-family:var(--mono);font-size:.74rem;color:var(--muted);white-space:nowrap}
.clock::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--v1);box-shadow:0 0 0 3px rgba(167,139,250,.22)}

/* ---------- dark / light toggle ---------- */
.theme-toggle{flex:none;width:38px;height:38px;border-radius:50%;display:grid;place-items:center;cursor:pointer;
  border:1px solid var(--line);background:transparent;color:var(--ink);padding:0;
  transition:border-color .2s,background .2s,transform .25s var(--ease)}
.theme-toggle:hover{border-color:var(--line-strong);background:var(--hover-bg);transform:rotate(18deg)}
.theme-toggle .q-icon{font-size:20px}
.theme-toggle .ic-moon{display:none}
html[data-theme=light] .theme-toggle .ic-sun{display:none}
html[data-theme=light] .theme-toggle .ic-moon{display:inline-flex}
.chat-head .theme-toggle{margin-left:auto}

/* ---------- page layout ---------- */
main.page{position:relative;z-index:1;padding-top:var(--nav-h)}
.wrap{width:100%;max-width:1200px;margin:0 auto;padding-inline:var(--pad)}
.rise{animation:rise .8s var(--ease) both;animation-delay:calc(var(--i,0) * 90ms)}
@keyframes rise{from{opacity:0;transform:translateY(18px)}}

/* ---------- hero ---------- */
.hero{display:grid;grid-template-columns:1.15fr .85fr;gap:48px;align-items:center;
  min-height:calc(100svh - var(--nav-h));padding-block:48px 72px}
.hello{display:flex;align-items:center;gap:10px;font-family:var(--mono);font-size:.9rem;color:var(--accent-text);letter-spacing:.06em}
.hello::before{content:"";width:28px;height:1px;background:var(--accent-text)}
.name{font-family:var(--display);font-weight:700;font-size:clamp(2.8rem,7vw,5.4rem);line-height:1;letter-spacing:-.04em;
  margin:14px 0 16px;text-wrap:balance;background:var(--name-grad);
  -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;color:transparent}
.role{font-family:var(--mono);font-size:clamp(.95rem,2vw,1.25rem);color:var(--accent-text);display:inline-block;overflow:hidden;
  white-space:nowrap;width:0;max-width:100%;border-right:2px solid var(--accent-text);
  animation:typing 2.2s steps(var(--chars)) .7s forwards,caret .8s step-end infinite}
@keyframes typing{to{width:calc(var(--chars) * 1ch)}}
@keyframes caret{50%{border-color:transparent}}
.tagline{color:var(--muted);line-height:1.7;font-size:clamp(1rem,1.6vw,1.15rem);max-width:52ch;margin:20px 0 28px}
.row{display:flex;flex-wrap:wrap;gap:12px}
.btn{display:inline-flex;align-items:center;gap:8px;padding:13px 22px;border-radius:12px;font-weight:600;font-size:.95rem;
  cursor:pointer;border:1px solid var(--line-strong);background:rgba(139,92,246,.12);color:var(--ink);font-family:var(--body);
  transition:transform .2s var(--ease),box-shadow .2s,background .2s}
.btn:hover{transform:translateY(-2px);background:rgba(139,92,246,.22)}
.btn.primary{border-color:transparent;background:var(--btn-bg);color:var(--btn-ink)!important}
.btn.primary:hover{background:var(--btn-bg);box-shadow:0 10px 30px rgba(139,92,246,.45)}
.btn .q-icon{font-size:19px}
.stats{display:flex;gap:44px;margin-top:44px}
.stat{padding-left:16px;border-left:2px solid var(--v2)}
.stat-n{font-family:var(--display);font-weight:700;font-size:2.1rem;line-height:1.1;font-variant-numeric:tabular-nums}
.stat-l{font-family:var(--mono);font-size:.72rem;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);margin-top:4px}

.orb{position:relative;justify-self:center;width:min(380px,100%);aspect-ratio:1;display:grid;place-items:center}
.orb::before{content:"";position:absolute;inset:0;border-radius:50%;will-change:transform;
  background:conic-gradient(var(--v1),var(--v3),var(--ring-hi),var(--v2),var(--v1));animation:spin 10s linear infinite;
  -webkit-mask:radial-gradient(farthest-side,transparent calc(100% - 4px),#000 calc(100% - 3px));
  mask:radial-gradient(farthest-side,transparent calc(100% - 4px),#000 calc(100% - 3px))}
.orb::after{content:"";position:absolute;inset:-18%;border-radius:50%;z-index:-1;
  background:radial-gradient(circle,rgba(139,92,246,.34),transparent 66%)}
@keyframes spin{to{transform:rotate(360deg)}}
.orb-face{width:88%;aspect-ratio:1;border-radius:50%;display:grid;place-items:center;
  background:var(--orb-face);font-family:var(--display);font-weight:700;
  font-size:clamp(2.6rem,9vw,5rem);letter-spacing:-.02em;animation:float 6s ease-in-out infinite}
@keyframes float{50%{transform:translateY(-8px)}}

/* ---------- sections ---------- */
.sec{padding-block:96px 0;scroll-margin-top:calc(var(--nav-h) + 8px)}
.kicker{display:flex;align-items:center;gap:10px;font-family:var(--mono);font-size:.78rem;text-transform:uppercase;
  letter-spacing:.16em;color:var(--accent-text)}
.kicker::before{content:"";width:24px;height:1px;background:var(--accent-text)}
.sec-title{font-family:var(--display);font-weight:700;font-size:clamp(1.9rem,4vw,2.7rem);letter-spacing:-.03em;margin:8px 0 30px}
.about-p{color:var(--muted);line-height:1.85;max-width:72ch;margin:0 0 14px;font-size:1.05rem}

.grid{display:grid;gap:18px;grid-template-columns:1fr}
@media(min-width:640px){.grid.g2,.grid.g3{grid-template-columns:repeat(2,1fr)}}
@media(min-width:980px){.grid.g3{grid-template-columns:repeat(3,1fr)}}
.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:22px;min-width:0;box-shadow:var(--card-shadow);
  transition:transform .25s var(--ease),border-color .25s,box-shadow .25s}
.card:hover{transform:translateY(-4px);border-color:var(--line-strong);box-shadow:0 16px 40px rgba(109,40,217,.2)}
a.card{display:block;cursor:pointer}
a.card.contact{display:flex}
.p-icon{width:48px;height:48px;border-radius:14px;display:grid;place-items:center;margin-bottom:16px;color:#fff;
  background:linear-gradient(135deg,var(--v2),var(--v3))}
.p-title{font-family:var(--display);font-weight:700;font-size:1.25rem;margin-bottom:8px}
.p-desc{color:var(--muted);font-size:.94rem;line-height:1.65;margin-bottom:16px}
.tag{font-family:var(--mono);font-size:.72rem;padding:4px 10px;border-radius:999px;border:1px solid var(--line);color:var(--accent-text)}
.gh-link{display:flex;align-items:center;gap:6px;margin-top:18px;font-family:var(--mono);font-size:.78rem;color:var(--ink)}
.gh-link .q-icon{font-size:16px;color:var(--accent-text)}

.skill-top{display:flex;justify-content:space-between;font-size:.95rem;margin-bottom:12px;font-weight:500}
.skill-top span:last-child{font-family:var(--mono);color:var(--muted);font-variant-numeric:tabular-nums}
.meter{height:6px;border-radius:99px;background:var(--track);overflow:hidden}
.meter i{display:block;height:100%;width:var(--w);border-radius:inherit;transform-origin:left;
  background:linear-gradient(90deg,var(--v3),var(--v1));animation:grow 1.2s var(--ease) .4s both}
@keyframes grow{from{transform:scaleX(0)}}

.contact{display:flex;align-items:center;gap:14px;font-size:.98rem;word-break:break-word}
.contact .q-icon{flex:none;width:42px;height:42px;border-radius:12px;display:grid;place-items:center;font-size:20px;
  color:#fff;background:linear-gradient(135deg,var(--v2),var(--v3))}
.foot{margin-top:96px;padding-block:28px 40px;border-top:1px solid var(--line);color:var(--muted);font-family:var(--mono);font-size:.78rem}

/* ---------- floating Ask Anything ---------- */
.fab{position:fixed;right:max(18px,env(safe-area-inset-right));bottom:max(18px,env(safe-area-inset-bottom));z-index:60;
  display:inline-flex;align-items:center;gap:8px;padding:14px 22px;border-radius:999px;font-weight:600;font-size:.95rem;
  color:#fff!important;background:linear-gradient(135deg,var(--v2),var(--v3));box-shadow:0 12px 32px rgba(109,40,217,.5);
  transition:transform .2s var(--ease)}
.fab:hover{transform:translateY(-3px) scale(1.03)}
.fab::after{content:"";position:absolute;inset:0;border-radius:inherit;border:2px solid var(--v1);animation:pulse 2.6s ease-out infinite}
@keyframes pulse{from{transform:scale(1);opacity:.8}to{transform:scale(1.3);opacity:0}}

/* ---------- reveal on scroll (supported browsers only; others just show everything) ---------- */
@supports (animation-timeline: view()){
  .reveal{animation:reveal linear both;animation-timeline:view();animation-range:entry 5% entry 40%}
  @keyframes reveal{from{opacity:0;transform:translateY(30px)}}
}

/* ---------- tablet / phone ---------- */
@media(max-width:899px){
  .hero{grid-template-columns:1fr;gap:28px;min-height:auto;padding-block:36px 40px}
  .orb{order:-1;width:min(230px,60vw)}
  .nav-links{display:none}
  .clock{margin-left:auto}
  .sec{padding-block:72px 0}
}
@media(max-width:480px){
  .clock{font-size:.68rem;padding:5px 10px}
  .stats{gap:28px}
  .fab{padding:15px;gap:0}
  .fab .q-icon{font-size:24px}
  .fab .fab-text{display:none}
}

/* ---------- chat page ---------- */
.chat-wrap{position:relative;z-index:1;height:100svh;display:flex;flex-direction:column;width:min(880px,100%);margin:0 auto;
  padding-inline:max(14px,env(safe-area-inset-left,0px)) max(14px,env(safe-area-inset-right,0px));
  padding-top:env(safe-area-inset-top,0px);padding-bottom:max(12px,env(safe-area-inset-bottom,0px))}
.chat-head{flex:none;display:flex;align-items:center;gap:12px;padding:14px 4px}
.back{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;background:var(--card);border:1px solid var(--line);
  transition:transform .2s var(--ease)}
.back:hover{transform:translateX(-3px)}
.avatar{width:44px;height:44px;border-radius:50%;display:grid;place-items:center;font-family:var(--display);font-weight:700;
  font-size:.8rem;background:linear-gradient(135deg,var(--v1),var(--v3));color:#fff}
.chat-title{font-family:var(--display);font-weight:700;font-size:1.15rem}
.chat-sub{color:var(--muted);font-size:.8rem;display:flex;align-items:center;gap:6px}
.chat-sub::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--v1)}
.chat-scroll{flex:1 1 0;min-height:0;height:auto!important;width:100%}
.msgs{width:100%;display:flex;flex-direction:column;gap:12px;padding:12px 4px 18px}
.bubble{max-width:min(82%,560px);padding:12px 16px;border-radius:18px;line-height:1.6;font-size:.95rem;
  white-space:pre-wrap;word-break:break-word;animation:rise .4s var(--ease) both}
.bubble.bot{align-self:flex-start;background:var(--card);border:1px solid var(--line);border-bottom-left-radius:6px}
.bubble.user{align-self:flex-end;color:#fff;font-weight:500;background:linear-gradient(135deg,var(--v2),var(--v3));border-bottom-right-radius:6px}
.typing{align-self:flex-start;display:flex;align-items:center;gap:5px;padding:14px 16px;border-radius:18px;background:var(--card);border:1px solid var(--line)}
.typing i{width:7px;height:7px;border-radius:50%;background:var(--muted);animation:bounce 1s infinite}
.wake-note{margin-left:8px;font-size:.8rem;color:var(--muted)}
.typing i:nth-child(2){animation-delay:.15s}.typing i:nth-child(3){animation-delay:.3s}
@keyframes bounce{40%{transform:translateY(-5px);background:var(--v1)}}
.chips{flex:none;display:flex;flex-wrap:wrap;gap:8px;padding:4px 4px 12px}
.chip{padding:8px 14px;border-radius:999px;font-size:.84rem;cursor:pointer;border:1px solid var(--line);background:var(--card);
  transition:background .2s,border-color .2s,transform .2s var(--ease)}
.chip:hover{background:rgba(139,92,246,.2);border-color:var(--line-strong);transform:translateY(-2px)}
.composer{flex:none;display:flex;align-items:center;gap:8px;padding:6px 6px 6px 12px;border-radius:999px;
  background:var(--composer);border:1px solid var(--line);transition:border-color .2s}
.composer:focus-within{border-color:var(--v2)}
.composer .q-field{flex:1}
.composer .q-field__native{color:var(--ink)!important;font-size:.98rem}
.composer .q-field__native::placeholder{color:var(--muted)}
.hidden-upload{display:none!important}
.pills{flex:none;display:flex;flex-wrap:wrap;gap:0 8px}
.choices{align-self:flex-start;display:flex;flex-wrap:wrap;gap:10px;margin-top:2px}
.choice{display:flex;align-items:center;gap:10px;padding:12px 18px;border-radius:14px;cursor:pointer;
  font:600 .95rem var(--body);color:var(--ink);background:var(--card);border:1px solid var(--line-strong);
  transition:transform .2s var(--ease),background .2s,box-shadow .2s}
.choice:hover{transform:translateY(-2px);background:rgba(139,92,246,.18);box-shadow:0 10px 26px rgba(109,40,217,.25)}
.choice .q-icon{color:var(--accent-text);font-size:22px}
.q-btn.attach,.q-btn.attach .q-icon{color:var(--muted)!important;background:transparent!important}
.q-btn.attach:hover .q-icon{color:var(--v1)!important}
.q-btn.attach{flex:none}
.attach .q-focus-helper,.send .q-focus-helper{display:none}
.jd-chip{flex:none;align-self:flex-start;display:flex;align-items:center;gap:8px;max-width:100%;margin:0 4px 8px;
  padding:4px 4px 4px 12px;border-radius:999px;font-size:.82rem;background:var(--card);border:1px solid var(--v2)}
.jd-chip .q-icon{color:var(--accent-text);font-size:18px}
.jd-chip>span,.jd-chip .jd-label{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.jd-x{color:var(--muted)!important}
.q-btn.send{width:44px;height:44px;border-radius:50%!important;background:linear-gradient(135deg,var(--v2),var(--v3))!important}
.q-btn.send,.q-btn.send .q-icon{color:#fff!important}

@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}
  .role{width:auto;border-right:0}
  .reveal{opacity:1!important;transform:none!important}
}
"""

# Live India time (IST) in the top bar. Runs in the visitor's browser, so it keeps ticking without
# any server work and always shows Indian time, wherever the visitor is.
CLOCK_JS = """
<script>
(function(){
  try{ var saved = localStorage.getItem('theme'); if(saved) document.documentElement.setAttribute('data-theme', saved); }catch(e){}
  document.addEventListener('click', function(ev){
    if(!ev.target.closest('.theme-toggle')) return;
    var next = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', next);
    try{ localStorage.setItem('theme', next); }catch(e){}
  });
})();
(function(){
  var fmt = new Intl.DateTimeFormat('en-US', {timeZone:'Asia/Kolkata', hour:'numeric', minute:'2-digit', hour12:true});
  function tick(){
    var p = {};
    fmt.formatToParts(new Date()).forEach(function(x){ p[x.type] = x.value; });
    var t = p.hour + ':' + p.minute + ' ' + p.dayPeriod;
    document.querySelectorAll('[data-clock]').forEach(function(el){ el.textContent = t; });
  }
  tick(); setInterval(tick, 1000);
})();
</script>
"""

ui.add_head_html(FONTS + f"<style>{CSS}</style>" + CLOCK_JS, shared=True)


def clock_text() -> str:
    """Initial IST time rendered by the server (the browser script keeps it updated)."""
    now = datetime.now(timezone(timedelta(hours=5, minutes=30)))  # India has no daylight saving
    return f"{now.hour % 12 or 12}:{now.minute:02d} {'AM' if now.hour < 12 else 'PM'}"


# ----------------------------------------------------------------------------
# 2. VISITOR COUNTER
# ----------------------------------------------------------------------------
def read_visits() -> int:
    try:
        return int(json.loads(VISITS_FILE.read_text()).get("count", 0))
    except (OSError, ValueError, AttributeError):
        return 0


def bump_visits() -> int:
    count = read_visits() + 1
    tmp = VISITS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps({"count": count}))
    tmp.replace(VISITS_FILE)
    return count


def register_visit() -> int:
    """Count one visit per browser per day (page refreshes do not inflate the number)."""
    today = date.today().isoformat()
    if app.storage.browser.get("last_visit") != today:
        app.storage.browser["last_visit"] = today
        return bump_visits()
    return read_visits()


# ----------------------------------------------------------------------------
# 3. HOMEPAGE
# ----------------------------------------------------------------------------
def theme_toggle() -> None:
    with ui.element("button").classes("theme-toggle").props(
        'type=button aria-label="Switch dark / light mode" title="Switch dark / light mode"'
    ):
        ui.icon("light_mode").classes("ic-sun")
        ui.icon("dark_mode").classes("ic-moon")


def navbar() -> None:
    with ui.element("header").classes("nav"):
        with ui.element("div").classes("nav-in"):
            with ui.link(target="/").classes("brand"):
                ui.label(PROFILE["initials"][:2]).classes("brand-mark")
                ui.label(PROFILE["name"])
            with ui.element("nav").classes("nav-links"):
                for label, target in NAV:
                    ui.link(label, f"#{target}").classes("nav-link")
            with ui.element("div").classes("clock").props('title="India time (IST)"'):
                ui.label("IST")
                ui.label(clock_text()).props("data-clock=time")
            theme_toggle()


def hero(visits: int) -> None:
    with ui.element("section").classes("hero wrap").props("id=top"):
        with ui.element("div").classes("orb rise").style("--i:0"):
            ui.label(PROFILE["initials"]).classes("orb-face")
        with ui.element("div"):
            ui.label("Hello, I am").classes("hello rise").style("--i:1")
            ui.label(PROFILE["name"]).classes("name rise").style("--i:2")
            ui.label(PROFILE["role"]).classes("role").style(f"--chars:{len(PROFILE['role'])}")
            ui.label(PROFILE["tagline"]).classes("tagline rise").style("--i:4")
            with ui.element("div").classes("row rise").style("--i:5"):
                with ui.link(target="#projects").classes("btn primary"):
                    ui.icon("arrow_downward")
                    ui.label("View my work")
                with ui.link(target="/chat").classes("btn"):
                    ui.icon("auto_awesome")
                    ui.label("Ask Anything")
            with ui.element("div").classes("stats rise").style("--i:6"):
                # only two numbers: total projects + total visitors
                projects_total = next(
                    (n for n, lab in PROFILE.get("stats", []) if lab.lower() == "projects"),
                    str(len(PROFILE["projects"])),
                )
                for number, label in [(projects_total, "Projects"), (f"{visits:,}", "Visitors")]:
                    with ui.element("div").classes("stat"):
                        ui.label(number).classes("stat-n")
                        ui.label(label).classes("stat-l")


def section_head(kicker: str, title: str) -> None:
    with ui.element("div").classes("reveal"):
        ui.label(kicker).classes("kicker")
        ui.label(title).classes("sec-title")


def about() -> None:
    with ui.element("section").classes("sec wrap").props("id=about"):
        section_head("About", "A bit about me")
        for paragraph in PROFILE["about"]:
            ui.label(paragraph).classes("about-p reveal")


def skills() -> None:
    with ui.element("section").classes("sec wrap").props("id=skills"):
        section_head("Skills", "What I work with")
        with ui.element("div").classes("grid g2"):
            for name, level in PROFILE["skills"]:
                with ui.element("div").classes("card reveal"):
                    with ui.element("div").classes("skill-top"):
                        ui.label(name)
                        ui.label(f"{level}%")
                    with ui.element("div").classes("meter"):
                        ui.element("i").style(f"--w:{level}%")


def projects() -> None:
    with ui.element("section").classes("sec wrap").props("id=projects"):
        section_head("Projects", "Selected work")
        with ui.element("div").classes("grid g3"):
            for item in PROFILE["projects"]:
                # the whole card is a link that opens the project's GitHub page in a new tab
                with ui.link(target=item.get("url") or GITHUB, new_tab=True).classes("card reveal").props(
                    f'aria-label="{item["title"]} on GitHub"'
                ):
                    with ui.element("div").classes("p-icon"):
                        ui.icon(item.get("icon", "folder")).props("size=24px")
                    ui.label(item["title"]).classes("p-title")
                    ui.label(item["desc"]).classes("p-desc")
                    with ui.element("div").classes("row").style("gap:6px"):
                        for tag in item.get("tags", []):
                            ui.label(tag).classes("tag")
                    with ui.element("div").classes("gh-link"):
                        ui.icon("code")
                        ui.label("View on GitHub")
                        ui.icon("arrow_outward")


def contact_href(icon: str, text: str) -> str | None:
    if icon == "mail":
        return f"mailto:{text}"
    if icon == "call":
        return "tel:" + "".join(c for c in text if c.isdigit() or c == "+")
    if icon == "code":
        return text if text.startswith("http") else "https://" + text
    return None


def contact() -> None:
    with ui.element("section").classes("sec wrap").props("id=contact"):
        section_head("Contact", "Let's build something")
        with ui.element("div").classes("grid g2"):
            for icon, text in PROFILE["contact"]:
                href = contact_href(icon, text)
                holder = ui.link(target=href, new_tab=icon == "code") if href else ui.element("div")
                with holder.classes("card contact reveal"):
                    ui.icon(icon)
                    ui.label(text)
        with ui.element("footer").classes("foot"):
            ui.label(f"© 2026 {PROFILE['name']}")


@ui.page("/")
def home() -> None:
    ui.page_title(f"{PROFILE['name']} | {PROFILE['role']}")
    visits = register_visit()
    ui.timer(0.5, wake_backend, once=True)  # start waking a sleeping backend while the visitor reads
    ui.element("div").classes("glow")
    navbar()
    with ui.element("main").classes("page"):
        hero(visits)
        about()
        skills()
        projects()
        contact()
    with ui.link(target="/chat").classes("fab").props('aria-label="Ask Anything"'):
        ui.icon("auto_awesome")
        ui.label("Ask Anything").classes("fab-text")


# ----------------------------------------------------------------------------
# 4. ASK ANYTHING (chat page)
# ----------------------------------------------------------------------------
# A free Render server falls asleep after 15 minutes without traffic and needs about a minute to wake up.
# These helpers wake it as soon as someone opens the site, and wait patiently instead of failing.
WAKE_TIMEOUT = httpx.Timeout(120, connect=60)


async def wake_backend() -> None:
    """Pings the backend so a sleeping server starts waking up while the visitor is still reading."""
    try:
        async with httpx.AsyncClient(timeout=WAKE_TIMEOUT) as client:
            await client.get(f"{BACKEND_URL}/")
    except httpx.HTTPError:
        pass


def _is_waking_up(error: httpx.HTTPError) -> bool:
    """True for the errors a sleeping (cold-starting) server produces."""
    if isinstance(error, httpx.HTTPStatusError):
        return error.response.status_code in (502, 503, 504)
    return isinstance(error, (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError))


async def stream_answer(question: str, session_id: str | None = None, profile: str | None = None):
    """Ask the FastAPI backend (POST /chat/stream) and yield the answer piece by piece.
    The session id lets the backend use the JD uploaded in this chat.
    If the server is still waking up, it retries a few times before giving up."""
    got_something = False
    attempts = 3
    for attempt in range(attempts):
        try:
            async with httpx.AsyncClient(timeout=WAKE_TIMEOUT) as client:
                async with client.stream(
                    "POST",
                    f"{BACKEND_URL}/chat/stream",
                    json={"question": question, "session_id": session_id, "profile": profile},
                ) as response:
                    response.raise_for_status()
                    async for piece in response.aiter_text():
                        if piece:
                            got_something = True
                            yield piece
            return
        except httpx.HTTPError as error:
            if got_something:
                yield "\n\n(The connection was interrupted. Please ask again.)"
                return
            if attempt < attempts - 1 and _is_waking_up(error):
                await asyncio.sleep(8)
                continue
            yield "Sorry, the assistant is not reachable right now. Please try again in a moment."
            return


async def upload_jd(session_id: str, filename: str, data: bytes) -> tuple[bool, str]:
    """Send the recruiter's JD PDF to the backend. Returns (ok, label_or_error)."""
    try:
        async with httpx.AsyncClient(timeout=WAKE_TIMEOUT) as client:
            response = await client.post(
                f"{BACKEND_URL}/upload-jd",
                data={"session_id": session_id},
                files={"file": (filename, data, "application/pdf")},
            )
        if response.status_code != 200:
            try:
                detail = response.json().get("detail", "Upload failed")
            except ValueError:
                detail = "Upload failed"
            return False, str(detail)
        info = response.json()
        label = " at ".join(x for x in (info.get("title"), info.get("company")) if x)
        return True, label or filename
    except httpx.HTTPError:
        return False, "Backend is not reachable"


async def remove_jd(session_id: str) -> None:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            await client.delete(f"{BACKEND_URL}/jd/{session_id}")
    except httpx.HTTPError:
        pass



def typing_dots():
    """Three bouncing dots. After 8 seconds a note explains the wait (a sleeping server needs ~1 minute)."""
    with ui.element("div").classes("typing") as typing:
        for _ in range(3):
            ui.element("i")
        note = ui.label("Waking up the assistant, this can take up to a minute...").classes("wake-note")
        note.set_visibility(False)
        ui.timer(8, lambda: note.set_visibility(True), once=True)
    return typing


@ui.page("/chat")
def chat() -> None:
    ui.page_title(f"Ask Anything | {PROFILE['name']}")
    ui.timer(0.5, wake_backend, once=True)
    ui.element("div").classes("glow")

    with ui.element("div").classes("chat-wrap"):
        with ui.element("header").classes("chat-head"):
            with ui.link(target="/").classes("back").props('aria-label="Back to portfolio"'):
                ui.icon("arrow_back")
            ui.label(PROFILE["initials"]).classes("avatar")
            with ui.element("div"):
                ui.label("Ask Anything").classes("chat-title")
                ui.label(f"Questions about {PROFILE['name']}'s work").classes("chat-sub")
            theme_toggle()

        scroll = ui.scroll_area().classes("chat-scroll")
        with scroll:
            messages = ui.element("div").classes("msgs")
            with messages:
                ui.label(f"Hi! I am here to answer anything about {PROFILE['name']}.").classes("bubble bot")

        chips = ui.element("div").classes("chips")
        chips.set_visibility(False)
        state = {"profile": None, "row": None}  # chosen company type + the open choice buttons

        # ---- JD upload (hidden picker, opened by the paperclip button) ----
        session_id = uuid.uuid4().hex
        MAX_PDF_BYTES = 5 * 1024 * 1024

        pills = ui.element("div").classes("pills")
        with pills:
            profile_chip = ui.element("div").classes("jd-chip")
            profile_chip.set_visibility(False)
            with profile_chip:
                ui.icon("badge")
                profile_label = ui.label("").classes("jd-label")
                profile_change = ui.button(icon="swap_horiz").props("flat round dense size=sm").classes("jd-x")
                profile_change.props('aria-label="Change company type" title="Change company type"')

            jd_chip = ui.element("div").classes("jd-chip")
            jd_chip.set_visibility(False)
            with jd_chip:
                ui.icon("description")
                jd_label = ui.label("").classes("jd-label")
                jd_remove = ui.button(icon="close").props("flat round dense size=sm").classes("jd-x")
                jd_remove.props('aria-label="Remove job description"')

        def say(text: str, kind: str = "bot") -> None:
            with messages:
                ui.label(text).classes(f"bubble {kind}")
            scroll.scroll_to(percent=1.0)

        def lock_input() -> None:
            box.set_enabled(False)
            send_btn.set_enabled(False)
            box.props('placeholder="Choose a company type above first"')

        def ask_choice() -> None:
            if state["row"] is not None:
                return
            say("First, which kind of company are you hiring for? I will show the resume that fits best.")
            with messages:
                with ui.element("div").classes("choices") as row:
                    for key, (icon, label) in PROFILE_CHOICES.items():
                        with ui.element("button").classes("choice").props("type=button").on(
                            "click", lambda k=key: choose(k)
                        ):
                            ui.icon(icon)
                            ui.label(label)
            state["row"] = row
            scroll.scroll_to(percent=1.0)

        async def choose(key: str) -> None:
            if state["row"] is not None:
                state["row"].delete()
                state["row"] = None
            state["profile"] = key
            label = PROFILE_CHOICES[key][1]
            say(f"{label} company", "user")
            profile_label.text = f"{label} resume"
            profile_chip.set_visibility(True)
            say(
                f"Great! I will show my {label} resume. Ask me anything, "
                "or upload your job description with the paperclip and I will compare it."
            )
            box.set_enabled(True)
            send_btn.set_enabled(True)
            box.props('placeholder="Ask anything..."')
            chips.set_visibility(True)
            box.run_method("focus")

        def change_profile() -> None:
            if state["row"] is not None:
                return
            state["profile"] = None
            profile_chip.set_visibility(False)
            chips.set_visibility(False)
            lock_input()
            ask_choice()

        profile_change.on_click(change_profile)

        async def handle_upload(e) -> None:
            # NiceGUI 3+/4 gives e.file; NiceGUI 2.x gives e.content / e.name
            if hasattr(e, "file"):
                filename, data = e.file.name, await e.file.read()
            else:
                filename, data = e.name, e.content.read()
            picker.reset()
            if not filename.lower().endswith(".pdf"):
                ui.notify("Please upload a PDF file", type="warning")
                return
            if len(data) > MAX_PDF_BYTES:
                ui.notify("PDF is too large (max 5 MB)", type="warning")
                return
            chips.set_visibility(False)
            say(f"Uploaded JD: {filename}", "user")
            with messages:
                typing = typing_dots()
            scroll.scroll_to(percent=1.0)
            ok, info = await upload_jd(session_id, filename, data)
            typing.delete()
            if ok:
                jd_label.text = info
                jd_chip.set_visibility(True)
                say(
                    f"Thanks! I have read the job description ({info}). "
                    "Ask me how well I match it, which requirements I meet, or anything else."
                )
            else:
                say(f"I could not use that JD: {info}. Please try another PDF.")

        async def clear_jd() -> None:
            await remove_jd(session_id)
            jd_chip.set_visibility(False)
            say("The job description has been removed.")

        jd_remove.on_click(clear_jd)

        picker = (
            ui.upload(on_upload=handle_upload, auto_upload=True, max_files=1, max_file_size=MAX_PDF_BYTES)
            .props("accept=.pdf")
            .classes("hidden-upload")
        )

        async def send(text: str | None = None) -> None:
            question = (text if text is not None else box.value or "").strip()
            if not question or state["profile"] is None:
                return
            box.value = ""
            chips.set_visibility(False)
            with messages:
                ui.label(question).classes("bubble user")
                typing = typing_dots()
            scroll.scroll_to(percent=1.0)
            bubble = None
            answer = ""
            last_paint = 0.0
            async for piece in stream_answer(question, session_id, state["profile"]):
                if bubble is None:  # first words arrived: swap the typing dots for the real bubble
                    typing.delete()
                    with messages:
                        bubble = ui.label("").classes("bubble bot")
                answer += piece
                now = time.monotonic()
                if now - last_paint > 0.05:  # repaint ~20 times a second, not once per token
                    bubble.text = answer
                    scroll.scroll_to(percent=1.0)
                    last_paint = now
            if bubble is None:
                typing.delete()
                with messages:
                    bubble = ui.label("").classes("bubble bot")
                answer = "I could not get an answer. Please try again."
            bubble.text = answer
            scroll.scroll_to(percent=1.0)

        with chips:
            for suggestion in PROFILE.get("chat_suggestions", []):
                ui.label(suggestion).classes("chip").on("click", lambda s=suggestion: send(s))

        with ui.element("div").classes("composer"):
            ui.button(icon="attach_file", on_click=lambda: picker.run_method("pickFiles")).props(
                'round flat dense aria-label="Upload job description (PDF)" title="Upload job description (PDF)"'
            ).classes("attach")
            box = (
                ui.input(placeholder="Ask anything...")
                .props("borderless dense autofocus")
                .on("keydown.enter", lambda: send())
            )
            send_btn = ui.button(icon="arrow_upward", on_click=lambda: send()).props("round flat").classes("send")

        lock_input()
        ask_choice()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title=f"{PROFILE['name']} | Portfolio",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),  # hosting platforms (Render, etc.) provide PORT
        reload=False,
        show=False,
        storage_secret=os.getenv("STORAGE_SECRET", "portfolio-visitor-cookie"),
    )
