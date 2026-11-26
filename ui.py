#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML-шаблон дашборда (винесено з game_tracker.py).

Логіки тут немає — тільки розмітка, стилі та JS. Єдине, що підставляється
ззовні: __FEE_CONFIG__ (комісії з Python, щоб не дублювати їх у JS).
"""

HTML = r"""<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ledger</title>
<script>window.__GT_LANG__="__GT_LANG_VALUE__";</script>
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Ledger">
<meta name="theme-color" content="#0d1017">
<script>window.__pwaEarly=null;window.addEventListener('beforeinstallprompt',function(e){e.preventDefault();window.__pwaEarly=e;});</script>
<link rel="manifest" href="/manifest.json?v=5">
<link rel="icon" href="/app-icon-32-v5.png" sizes="32x32">
<link rel="icon" type="image/svg+xml" href="/app-icon-v5.svg">
<link rel="icon" type="image/png" sizes="192x192" href="/app-icon-192-v5.png">
<link rel="apple-touch-icon" sizes="180x180" href="/app-icon-180-v5.png">
<link rel="apple-touch-icon-precomposed" sizes="180x180" href="/app-icon-180-v5.png">
<link rel="shortcut icon" href="/favicon-v5.ico">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-32-v5.png">
<link rel="mask-icon" href="/app-icon-v5.svg" color="#7ad3a1">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
/* ═══════════════════════════════════════════════════════════════
   v4.6 — нова тема: Manrope, більші шрифти, м'які картки
   Кольори — змінні, тому працюють 4 теми (Slate/Nord/Carbon/Light)
   ═══════════════════════════════════════════════════════════════ */
:root{
  --fs:1;
  --bg:#0d1017; --bg2:#11151e; --card:#151a24; --card2:#1b2130; --brd:#28303f;
  --a1:#7c8cff; --a2:#ff7a59; --a3:#a78bfa; --a4:#22d3ee; --a5:#34d399;
  --tx:#e9ebf2; --mu:#8b95a9; --gr:#34d399; --rd:#f87171; --yw:#fbbf24;
  --radius:14px; --shadow:0 8px 28px rgba(0,0,0,.28);
  --font:'Manrope',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;
}
/* ═══════════ ТЕМА LEDGER — лаконічна, без градієнтів ═══════════ */
[data-theme="ledger"]{
  --bg:#08090A;--bg2:#0B0C0E;--card:#0B0C0E;--card2:#111214;--brd:#1D1F23;
  --a1:#EDEEF0;--a2:#D9A05B;--a3:#8B95F0;--a4:#8FBFD9;--a5:#4CB782;
  --tx:#E6E6E6;--mu:#82878F;--gr:#4CB782;--rd:#E08A8A;--yw:#D9A05B;
  --radius:10px;--shadow:none;
}
[data-theme="ledger"] body::before{display:none}
[data-theme="ledger"] .panel{background:#0B0C0E;border:1px solid #1D1F23;border-radius:12px;box-shadow:none}
[data-theme="ledger"] .ph{font-weight:600;letter-spacing:.02em;border-bottom:1px solid #1D1F23}
[data-theme="ledger"] .logo-i{background:#111214;border:1px solid #262A30;box-shadow:none;font-size:0}
[data-theme="ledger"] h1{font-size:1rem;font-weight:600;letter-spacing:-.01em}
[data-theme="ledger"] .tabs{border-bottom:1px solid #1D1F23;gap:2px;padding:6px 0}
[data-theme="ledger"] .tab{border-radius:6px;border-bottom:0;padding:8px 11px;font-weight:500;font-size:.85rem}
[data-theme="ledger"] .tab:hover{background:#111214}
[data-theme="ledger"] .tab.on{background:#15161A;color:#EDEEF0;border-bottom:0}
[data-theme="ledger"] .btn{background:#131417;border-color:#262A30;border-radius:6px}
[data-theme="ledger"] .btn:hover{background:#17181C;border-color:#3A3E45;color:#fff}
[data-theme="ledger"] input,[data-theme="ledger"] select,[data-theme="ledger"] textarea{
  background:#0D0E10;border-color:#262A30;border-radius:6px}
[data-theme="ledger"] .bub{background:#0D0E10;border:1px solid #1D1F23;border-radius:10px;box-shadow:none}
[data-theme="ledger"] .bub:hover{border-color:#2A2D33;box-shadow:none}
[data-theme="ledger"] .al{border-radius:8px}
[data-theme="ledger"] .theme-btn{border-radius:8px}
/* ── Огляд ── */
.ov-tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.ov-tile{background:var(--card2);border:1px solid var(--brd);border-radius:10px;padding:13px 14px}
.ov-k{font-size:.76rem;color:var(--mu)}
.ov-v{font-size:1.35rem;font-weight:600;margin-top:6px;letter-spacing:-.02em}
.ov-v.gr{color:var(--gr)}.ov-v.rd{color:var(--rd)}
.ov-d{font-size:.72rem;color:var(--mu);margin-top:4px}
@media(max-width:860px){.ov-tiles{grid-template-columns:repeat(2,1fr)}}
*{margin:0;padding:0;box-sizing:border-box}
html{font-size:calc(16.5px * var(--fs));-webkit-text-size-adjust:100%}
body{
  background:var(--bg);color:var(--tx);font-family:var(--font);
  min-height:100vh;min-height:100dvh;font-size:1rem;line-height:1.45;overflow-x:hidden;
  font-variant-numeric:tabular-nums;
}
body::before{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background:
    radial-gradient(ellipse 60% 40% at 10% 0%,color-mix(in srgb, var(--a1) 10%, transparent),transparent 60%),
    radial-gradient(ellipse 50% 45% at 95% 100%,rgba(167,139,250,.08),transparent 60%);
}
.w{position:relative;z-index:1;max-width:none;width:100%;margin:0 auto;padding:0 clamp(12px,2.2vw,34px) 70px}

.ic{width:15px;height:15px;flex:none;display:inline-block;vertical-align:-2px;
  stroke:currentColor;fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
.ph .btn,.ph .ic{flex:none}
.onb{position:fixed;inset:0;background:rgba(0,0,0,.72);z-index:200;display:flex;
  align-items:center;justify-content:center;padding:20px}
.onb-card{background:var(--card);border:1px solid var(--brd);border-radius:16px;padding:26px 28px;
  width:100%;max-width:520px;box-shadow:0 24px 70px rgba(0,0,0,.5)}
.onb-card h2{font-size:1.15rem;margin-bottom:14px;font-weight:600;letter-spacing:-.01em}
.onb-step{font-size:11px;color:var(--mu);letter-spacing:.12em;margin-bottom:8px}
.onb-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:22px}
.onb-lang{display:flex;gap:8px;margin-top:6px}
.onb-lang button{flex:1;padding:14px;font-size:15px;border-radius:8px;border:1px solid var(--brd);background:var(--card2);
  color:var(--tx);font-family:var(--font);font-size:.9rem;cursor:pointer}
.onb-lang button.on{border-color:var(--a1);background:color-mix(in srgb, var(--a1) 14%, transparent)}
.tab .ic{width:15px;height:15px;flex:none;stroke:currentColor;fill:none;
  stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round;opacity:.85}
.tab.on .ic{opacity:1}
.tabs .tsep{width:1px;background:var(--brd);margin:6px 6px;flex:none}
.psel{position:relative;min-width:196px}
.psel-btn{display:flex;align-items:center;gap:8px;width:100%;padding:9px 11px;border-radius:8px;
  border:1px solid var(--brd);background:var(--card2);color:var(--tx);font-family:var(--font);
  font-size:.85rem;font-weight:500;cursor:pointer}
.psel-btn:hover{border-color:var(--a1)}
.psel-btn .car{margin-left:auto;color:var(--mu);font-size:.7rem}
.psel-logo{width:16px;height:16px;border-radius:3px;object-fit:contain;flex:none}
.psel-list{position:absolute;z-index:60;top:calc(100% + 4px);left:0;right:0;background:var(--card);
  border:1px solid var(--brd);border-radius:8px;padding:4px;box-shadow:0 10px 30px rgba(0,0,0,.45);display:none}
.psel.open .psel-list{display:block}
.psel-opt{display:flex;align-items:center;gap:8px;padding:7px 9px;border-radius:6px;cursor:pointer;
  font-size:.85rem;color:var(--tx)}
.psel-opt:hover{background:var(--card2)}
.psel-opt.on{background:var(--card2);font-weight:600}
.psel-opt .fee{margin-left:auto;color:var(--mu);font-size:.78rem}
.seg{display:inline-flex;gap:2px;background:var(--card2);border:1px solid var(--brd);border-radius:8px;padding:2px}
.seg-b{display:inline-flex;align-items:center;gap:6px;font-family:var(--font);font-size:.8rem;font-weight:500;
  padding:6px 11px;border-radius:6px;border:0;background:transparent;color:var(--mu);cursor:pointer}
.seg-b:hover{color:var(--tx)}
.seg-b.on{background:var(--card);color:var(--tx);box-shadow:0 0 0 1px var(--brd) inset}
.langbtn{font-size:.72rem;font-weight:700;letter-spacing:.06em;padding:6px 9px;border-radius:6px;
  border:1px solid var(--brd);background:transparent;color:var(--mu);cursor:pointer}
.langbtn.on{color:var(--tx);background:var(--card2);border-color:var(--a1)}
.social{display:inline-flex;align-items:center;gap:6px;padding:7px 10px;border-radius:8px;
  border:1px solid var(--brd);background:var(--card2);color:var(--tx);text-decoration:none;
  font-size:12px;font-weight:600;transition:.15s}
.social svg{width:15px;height:15px;fill:currentColor;stroke:none;flex:none}
.social.tg:hover{border-color:#2AABEE;color:#2AABEE}
.social.dc:hover{border-color:#5865F2;color:#5865F2}
@media(max-width:640px){.social span{display:none}.social{padding:7px 9px}}
.online-box{margin-top:12px;padding:10px 12px;border:1px solid var(--brd);border-radius:12px;
  background:linear-gradient(180deg,color-mix(in srgb,var(--card2) 86%,transparent),transparent)}
.online-head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px}
.online-title{display:flex;align-items:center;gap:7px;font-size:12.5px;font-weight:700;color:var(--tx)}
.online-dot{width:7px;height:7px;border-radius:50%;background:var(--mu);flex:none}
.online-dot.on{background:var(--gr);box-shadow:0 0 0 3px color-mix(in srgb,var(--gr) 18%,transparent)}
.online-dot.err{background:var(--rd)}
.online-dot.wait{background:var(--yw)}
.online-switch{position:relative;display:inline-block;width:34px;height:20px;flex:none;cursor:pointer}
.online-switch input{opacity:0;width:0;height:0;position:absolute}
.online-slider{position:absolute;inset:0;background:var(--brd);border-radius:999px;transition:.18s;cursor:pointer}
.online-slider:before{content:"";position:absolute;width:14px;height:14px;left:3px;top:3px;background:#fff;border-radius:50%;transition:.18s}
.online-switch input:checked+.online-slider{background:var(--gr)}
.online-switch input:checked+.online-slider:before{transform:translateX(14px)}
.online-times{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:7px}
.online-time{font-size:11px;padding:4px 6px;border:1px solid var(--brd);border-radius:7px;
  background:var(--card);color:var(--tx);font-family:inherit;width:94px;min-height:0!important}
.online-foot{display:flex;align-items:center;gap:7px;flex-wrap:wrap;font-size:11px;color:var(--mu)}
.online-state{font-weight:700}
.online-refresh{padding:3px 8px;font-size:10.5px;border-radius:6px;border:1px solid var(--brd);
  background:var(--card2);color:var(--tx);cursor:pointer}
.online-refresh:hover{border-color:var(--a1)}
/* ── header ── */
header{
  padding:22px 0 16px;border-bottom:1px solid var(--brd);margin-bottom:20px;
  display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;
}
.logo{display:flex;align-items:center;gap:14px}
@keyframes brandWiggle{0%,100%{transform:rotate(0) scale(1)}20%{transform:rotate(-12deg) scale(1.15)}40%{transform:rotate(12deg) scale(1.15)}60%{transform:rotate(-7deg) scale(1.08)}80%{transform:rotate(7deg) scale(1.08)}}
#brandMark.order-alert{animation:brandWiggle 1.1s ease-in-out infinite;color:var(--gr)!important;filter:drop-shadow(0 0 7px color-mix(in srgb,var(--gr) 70%,transparent))}
#orderBanner{position:fixed;top:10px;left:50%;transform:translateX(-50%);z-index:9998;display:none;align-items:center;gap:10px;background:linear-gradient(135deg,#0f3d2e,#0b2a21);border:1px solid var(--gr);color:#eafff6;padding:10px 14px;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.5);font-size:12.5px;animation:orderDrop .35s ease-out}
@keyframes orderDrop{from{opacity:0;transform:translate(-50%,-14px)}to{opacity:1;transform:translate(-50%,0)}}
.logo-i{
  width:44px;height:44px;border-radius:13px;display:flex;align-items:center;justify-content:center;
  font-size:22px;background:linear-gradient(135deg,var(--a1),var(--a3));box-shadow:var(--shadow);
}
h1{
  font-family:var(--font);font-size:1.38rem;font-weight:800;letter-spacing:-.02em;
  color:var(--tx);line-height:1.15;
}
h1 span{
  display:block;font-size:.72rem;font-weight:500;color:var(--mu);
  letter-spacing:.10em;margin-top:3px;text-transform:uppercase;
}
h1 span b{color:var(--a1);font-weight:700}
#hdrTitle #hdrName{display:inline;font-size:inherit;font-weight:inherit;color:inherit;letter-spacing:inherit;text-transform:none}
#hdrTitle #planBadge{display:none;align-items:center;justify-content:center;width:auto;height:auto;border-radius:0;background:none;color:var(--a3);font-size:inherit;font-weight:800;line-height:1;letter-spacing:-.02em;margin-left:1px;vertical-align:baseline;text-transform:none}

/* ── tabs ── */
.tabs{display:flex;gap:6px;border-bottom:1px solid var(--brd);margin-bottom:20px;overflow-x:auto;padding-bottom:2px}
.tab{
  display:inline-flex;align-items:center;gap:6px;
  padding:11px 18px;font-size:.92rem;font-weight:600;color:var(--mu);cursor:pointer;
  border-radius:10px 10px 0 0;border-bottom:2px solid transparent;white-space:nowrap;transition:.15s;
}
.tab:hover{color:var(--tx);background:color-mix(in srgb, var(--a1) 7%, transparent)}
.tab.on{color:var(--a1);border-bottom-color:var(--a1);background:color-mix(in srgb, var(--a1) 8%, transparent)}
.tc{display:none}.tc.on{display:block}
#mnav{display:none}

/* ── кнопки ── */
.btn{
  background:color-mix(in srgb, var(--a1) 8%, transparent);border:1px solid var(--brd);color:var(--tx);
  padding:9px 15px;border-radius:10px;font-family:var(--font);font-size:.86rem;font-weight:600;
  cursor:pointer;transition:.15s;display:inline-flex;align-items:center;gap:6px;line-height:1.2;
}
.btn:hover{border-color:var(--a1);color:var(--a1);background:color-mix(in srgb, var(--a1) 14%, transparent)}
.btn.gr{border-color:rgba(52,211,153,.45);color:var(--gr);background:rgba(52,211,153,.08)}
.btn.gr:hover{background:var(--gr);color:#06120d;border-color:var(--gr)}
.btn.yw{border-color:rgba(251,191,36,.45);color:var(--yw);background:rgba(251,191,36,.08)}
.btn.yw:hover{background:var(--yw);color:#1a1300;border-color:var(--yw)}
.btn.rd{border-color:rgba(248,113,113,.45);color:var(--rd);background:rgba(248,113,113,.08)}
.btn.rd:hover{background:var(--rd);color:#1c0505;border-color:var(--rd)}
.btn.pu{border-color:rgba(167,139,250,.5);color:var(--a3);background:rgba(167,139,250,.08)}
.btn.pu:hover{background:var(--a3);color:#120a24;border-color:var(--a3)}
.btn:disabled{opacity:.4;cursor:not-allowed;pointer-events:none}
.btn.on{background:var(--a1);color:#0a0d16;border-color:var(--a1)}

@keyframes spin{to{transform:rotate(360deg)}}
@keyframes slideIn{from{transform:translateX(120%);opacity:0}to{transform:translateX(0);opacity:1}}
.spin{animation:spin .8s linear infinite;display:inline-block}

/* ── панелі ── */
.panel{
  background:var(--card);border:1px solid var(--brd);border-radius:var(--radius);
  padding:20px;margin-bottom:16px;box-shadow:var(--shadow);
}
.ph{
  font-size:1rem;font-weight:800;color:var(--tx);letter-spacing:.01em;
  margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--brd);
  display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;
}
.ph > div{flex-wrap:wrap;row-gap:6px}
.al{padding:14px 18px;border-radius:11px;font-size:.92rem;margin-bottom:14px;border:1px solid}
.al.info{border-color:color-mix(in srgb, var(--a1) 35%, transparent);background:color-mix(in srgb, var(--a1) 8%, transparent);color:#c7cdff}
.al.ok{border-color:rgba(52,211,153,.35);background:rgba(52,211,153,.08);color:var(--gr)}
.al.warn{border-color:rgba(251,191,36,.35);background:rgba(251,191,36,.08);color:var(--yw)}
.al.err{border-color:rgba(248,113,113,.35);background:rgba(248,113,113,.08);color:var(--rd)}

/* ── поля вводу: 16px, щоб iOS не збільшував сторінку ── */
input,select,textarea{
  background:var(--bg2);border:1px solid var(--brd);border-radius:10px;
  padding:10px 13px;color:var(--tx);font-family:var(--font);font-size:.98rem;
  outline:none;transition:border-color .15s,box-shadow .15s;min-height:42px;
}
input:focus,select:focus,textarea:focus{border-color:var(--a1);box-shadow:0 0 0 3px color-mix(in srgb, var(--a1) 25%, transparent)}
input[type=checkbox]{min-height:auto;width:18px;height:18px;accent-color:var(--a1);cursor:pointer}
label{font-size:.92rem}
::placeholder{color:var(--mu);opacity:.9}

/* ── статистичні картки ── */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:18px}
.sc{
  background:var(--card);border:1px solid var(--brd);border-radius:12px;
  padding:14px 16px;position:relative;overflow:hidden;
}
.sc::before{content:'';position:absolute;top:0;left:0;right:0;height:3px}
.c1::before{background:linear-gradient(90deg,var(--a1),transparent)}
.c2::before{background:linear-gradient(90deg,var(--a2),transparent)}
.c3::before{background:linear-gradient(90deg,var(--a3),transparent)}
.c4::before{background:linear-gradient(90deg,var(--rd),transparent)}
.c5::before{background:linear-gradient(90deg,var(--yw),transparent)}
.cg::before{background:linear-gradient(90deg,var(--gr),transparent)}
.sl{font-size:.75rem;letter-spacing:.09em;color:var(--mu);text-transform:uppercase;margin-bottom:6px;font-weight:600}
.sv{font-size:clamp(1rem,1.35vw,1.55rem);font-weight:800;letter-spacing:-.01em;white-space:nowrap}

/* ── таблиці ── */
.sup-table{width:100%;border-collapse:collapse}
.sup-table th{
  padding:12px 14px;text-align:left;font-size:.72rem;letter-spacing:.10em;color:var(--mu);
  background:var(--bg2);border-bottom:1px solid var(--brd);font-weight:700;text-transform:uppercase;
}
.sup-table td{padding:13px 14px;border-bottom:1px solid rgba(40,48,63,.55);font-size:1rem;vertical-align:middle}
.sup-table tr:last-child td{border-bottom:none}
.sup-table tbody tr:hover td{background:color-mix(in srgb, var(--a1) 5%, transparent)}
.sup-table a{color:var(--tx);text-decoration:none}
.sup-table a:hover{color:var(--a1)}
/* клітинка з кнопками не ламає рамку рядка */
.sup-table td[style*="display:flex"]{display:table-cell!important;white-space:nowrap}
.sup-table td[style*="display:flex"] button{margin-right:4px}
/* 🫧 «бульбашки» записів (iOS-style) */
.bub-wrap{display:flex;flex-direction:column;gap:10px}
.bub{background:var(--card2);
     border:1px solid var(--brd);border-radius:20px;padding:14px 16px;transition:.15s}
.bub:hover{border-color:color-mix(in srgb, var(--a1) 45%, transparent);box-shadow:0 8px 28px rgba(0,0,0,.3)}
.bub-head{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:9px}
.bub-date{font-size:11px;color:var(--mu);background:color-mix(in srgb, var(--a1) 10%, transparent);padding:3px 9px;border-radius:999px;white-space:nowrap}
.bub-chip{font-size:11px;color:var(--a3);background:color-mix(in srgb, var(--a1) 8%, transparent);padding:3px 9px;border-radius:999px}
.bub-title{flex:1 1 200px;font-weight:700;font-size:.95rem;line-height:1.32;color:var(--tx)}
.bub-acts{display:flex;gap:6px;margin-left:auto}
.bub-btn{background:transparent;border:1px solid var(--brd);color:var(--a1);border-radius:12px;
         padding:5px 10px;font-size:12px;cursor:pointer;line-height:1}
.bub-btn:hover{border-color:var(--a1)}
.bub-btn.del{color:var(--rd)}
.bub-btn.del:hover{border-color:var(--rd)}
.bub-stats{display:flex;gap:8px;flex-wrap:wrap}
.bs{font-size:12px;color:var(--mu);background:rgba(255,255,255,.02);border:1px solid var(--brd);
    border-radius:12px;padding:6px 11px;white-space:nowrap}
.bs b{color:var(--tx);font-family:var(--font)}
.bs .neg{color:var(--rd)}
.bs.pos b{color:var(--gr)}
.bs.negp b{color:var(--rd)}
.bub-id{font-size:11px;color:var(--mu);margin-top:9px;font-family:var(--font);word-break:break-all;opacity:.85}
/* 🫧 «бульбашки» записів (iOS-style) */
.bub-wrap{display:flex;flex-direction:column;gap:10px}
.bub{background:var(--card2);
     border:1px solid var(--brd);border-radius:20px;padding:14px 16px;transition:.15s}
.bub:hover{border-color:color-mix(in srgb, var(--a1) 45%, transparent);box-shadow:0 8px 28px rgba(0,0,0,.3)}
.bub-head{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:9px}
.bub-date{font-size:11px;color:var(--mu);background:color-mix(in srgb, var(--a1) 10%, transparent);padding:3px 9px;border-radius:999px;white-space:nowrap}
.bub-chip{font-size:11px;color:var(--a3);background:color-mix(in srgb, var(--a1) 8%, transparent);padding:3px 9px;border-radius:999px}
.bub-title{flex:1 1 200px;font-weight:700;font-size:.95rem;line-height:1.32;color:var(--tx)}
.bub-acts{display:flex;gap:6px;margin-left:auto}
.bub-btn{background:transparent;border:1px solid var(--brd);color:var(--a1);border-radius:12px;
         padding:5px 10px;font-size:12px;cursor:pointer;line-height:1}
.bub-btn:hover{border-color:var(--a1)}
.bub-btn.del{color:var(--rd)}
.bub-btn.del:hover{border-color:var(--rd)}
.bub-stats{display:flex;gap:8px;flex-wrap:wrap}
.bs{font-size:12px;color:var(--mu);background:rgba(255,255,255,.02);border:1px solid var(--brd);
    border-radius:12px;padding:6px 11px;white-space:nowrap}
.bs b{color:var(--tx);font-family:var(--font)}
.bs .neg{color:var(--rd)}
.bs.pos b{color:var(--gr)}
.bs.negp b{color:var(--rd)}
.bub-id{font-size:11px;color:var(--mu);margin-top:9px;font-family:var(--font);word-break:break-all;opacity:.85}

/* ── бейджі / прогрес / пагінація ── */
.profit-pos{color:var(--gr)}.profit-neg{color:var(--rd)}.profit-neu{color:var(--mu)}
.ilnk{
  display:inline-flex;align-items:center;justify-content:center;padding:5px 10px;border-radius:8px;
  font-size:.78rem;font-weight:600;text-decoration:none;border:1px solid var(--brd);color:var(--mu);transition:.15s;
}
.ilnk:hover{border-color:var(--a1);color:var(--a1)}
.none{text-align:center;padding:34px;color:var(--mu);font-size:.95rem}
.pag{display:flex;justify-content:center;align-items:center;gap:5px;padding:14px 0 2px;flex-wrap:wrap}
.pb{
  background:transparent;border:1px solid var(--brd);color:var(--mu);padding:6px 12px;
  border-radius:8px;cursor:pointer;font-size:.85rem;font-family:var(--font);transition:.15s;
}
.pb:hover,.pb.on{border-color:var(--a1);color:var(--a1);background:color-mix(in srgb, var(--a1) 10%, transparent)}
.sort-btns{display:flex;gap:5px}
.sbtn{
  padding:6px 11px;border:1px solid var(--brd);border-radius:8px;font-size:.8rem;font-weight:600;
  cursor:pointer;background:transparent;color:var(--mu);font-family:var(--font);transition:.15s;
}
.sbtn:hover,.sbtn.on{border-color:var(--a1);color:var(--a1)}
.cmp-pr{font-weight:800;white-space:nowrap;font-variant-numeric:tabular-nums}
.pr-cheaper{color:var(--rd)}.pr-same{color:var(--yw)}.pr-expensive{color:var(--gr)}

/* ── записи P&L ── */
.pur-row{
  background:var(--card2);border:1px solid var(--brd);border-radius:11px;
  padding:12px 15px;margin-bottom:8px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;
}
.pur-title{flex:1;font-weight:700;font-size:.95rem;min-width:160px}
.pur-badge{font-size:.72rem;padding:3px 8px;border-radius:6px;font-weight:700;border:1px solid}
.sale-row{display:flex;gap:10px;align-items:center;padding:9px 0;border-bottom:1px solid rgba(40,48,63,.55);font-size:.9rem}
.sale-row:last-child{border-bottom:none}

/* ── сітки / налаштування ── */
.g2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.g3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}
.step{display:flex;gap:14px;margin-bottom:16px}
.snum{
  min-width:30px;height:30px;border-radius:9px;display:flex;align-items:center;justify-content:center;
  font-size:.85rem;font-weight:800;color:#0a0d16;background:linear-gradient(135deg,var(--a1),var(--a3));flex-shrink:0;
}
.stit{font-weight:700;margin-bottom:4px;font-size:.98rem}
.sdesc{font-size:.88rem;color:var(--mu);line-height:1.7}
code{
  background:var(--card2);border:1px solid var(--brd);padding:2px 7px;border-radius:6px;
  font-size:.86rem;color:var(--a1);font-family:ui-monospace,Consolas,monospace;
}
.theme-btn{
  display:flex;flex-direction:column;align-items:center;gap:7px;cursor:pointer;
  padding:11px 14px;border-radius:12px;border:2px solid transparent;transition:.15s;
  font-size:.82rem;color:var(--mu);font-weight:600;
}
.theme-btn:hover{border-color:var(--a1);color:var(--tx)}
.theme-btn.active{border-color:var(--a1);color:var(--a1);background:color-mix(in srgb, var(--a1) 10%, transparent)}

/* ── мобільний ── */
@media(max-width:780px){
  #tab-tracker .panel,#tab-eldorado .panel,#tab-inventory .panel,
  #tab-platforms .panel,#tab-stats .panel{overflow-x:auto}
  #tab-tracker .sup-table th,#tab-tracker .sup-table td,
  #tab-eldorado .sup-table th,#tab-eldorado .sup-table td,
  #tab-inventory .sup-table th,#tab-inventory .sup-table td{font-size:.82rem;padding:8px 6px}
  #tab-tracker .sup-table th:nth-child(3),#tab-tracker .sup-table td:nth-child(3),
  #tab-tracker .sup-table th:nth-child(4),#tab-tracker .sup-table td:nth-child(4),
  #tab-tracker .sup-table th:nth-child(6),#tab-tracker .sup-table td:nth-child(6),
  #tab-eldorado .sup-table th:nth-child(3),#tab-eldorado .sup-table td:nth-child(3),
  #tab-eldorado .sup-table th:nth-child(5),#tab-eldorado .sup-table td:nth-child(5),
  #tab-eldorado .sup-table th:nth-child(6),#tab-eldorado .sup-table td:nth-child(6),
  #tab-eldorado .sup-table th:nth-child(8),#tab-eldorado .sup-table td:nth-child(8),
  #tab-inventory .sup-table th:nth-child(3),#tab-inventory .sup-table td:nth-child(3),
  #tab-inventory .sup-table th:nth-child(5),#tab-inventory .sup-table td:nth-child(5){display:none}
  #tab-tracker .sup-table td:nth-child(2),#tab-eldorado .sup-table td:nth-child(2),
  #tab-inventory .sup-table td:nth-child(2){max-width:190px}
  #tab-tracker .sup-table td:nth-child(7),#tab-eldorado .sup-table td:nth-child(7){white-space:nowrap}
}

@media(max-width:780px){
  #tab-taobao .sup-table th:nth-child(5),
  #tab-taobao .sup-table td:nth-child(5),
  #tab-taobao .sup-table th:nth-child(6),
  #tab-taobao .sup-table td:nth-child(6){display:none}
  #tab-taobao .sup-table td{font-size:.9rem;padding:9px 6px}
  #tab-taobao .sup-table td:first-child{max-width:100%!important}
}
@media(max-width:860px){
  .tabs{flex-wrap:wrap;overflow:visible;position:static}
  .tabs .tsep{display:none}
  .panel table{display:block;overflow-x:auto;max-width:100%;-webkit-overflow-scrolling:touch}
}
@media(max-width:640px){
  .panel table{display:block;overflow-x:auto;max-width:100%;-webkit-overflow-scrolling:touch}
}
@media(max-width:780px){.g2,.g3{grid-template-columns:1fr}}
html,body{max-width:100%;overflow-x:hidden}
.w{max-width:100%;overflow-x:clip}
canvas{max-width:100%!important}
@media(max-width:640px){
  body{padding-bottom:calc(74px + env(safe-area-inset-bottom))}
  .w{padding:0 12px 18px}
  .tabs{
    position:static;background:var(--bg);
    flex-wrap:wrap;overflow:visible;padding:6px 2px;margin-bottom:12px;
  }
  .tabs .tsep{display:none}
  .tab{font-size:.75rem;padding:7px 8px;flex:0 1 auto}
  .tabs::-webkit-scrollbar{display:none}
  .tab{padding:9px 10px;font-size:.8rem;gap:5px}
  .tab .ic{width:16px;height:16px}
  .tabs .tsep{margin:4px 3px}
  #mnav{
    display:flex;position:fixed;left:0;right:0;bottom:0;z-index:1000;
    background:color-mix(in srgb,var(--card) 94%,transparent);
    border-top:1px solid var(--brd);
    padding:6px 4px calc(6px + env(safe-area-inset-bottom));
    backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  }
  .mn{
    flex:1;display:flex;flex-direction:column;align-items:center;gap:3px;
    padding:5px 2px;border:0;border-radius:9px;background:transparent;
    color:var(--mu);font-family:var(--font);font-size:10px;font-weight:600;
    cursor:pointer;line-height:1.15;min-width:0;
  }
  .mn .ic{width:19px;height:19px;stroke:currentColor;fill:none;stroke-width:1.7}
  .mn.on{color:var(--a1);background:color-mix(in srgb,var(--a1) 9%,transparent)}
  .mn span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%}
  input:not([type=checkbox]):not([type=radio]),select,textarea{font-size:16px!important;min-height:42px}
  .btn{min-height:40px}
  .bub-acts .bub-btn{width:36px;height:36px;font-size:16px}
  .sc{padding:12px}
  .pur-row,.bub{padding:12px}
  .psel{min-width:0;width:100%}
  .psel-btn{width:100%}
  .panel{padding:14px 12px;border-radius:12px}
  .ph{font-size:.95rem;margin-bottom:12px}
  .tabs{gap:4px}
  .tab{font-size:.8rem;padding:9px 10px;flex:0 0 auto}
  #chAll{overflow-x:auto;max-width:100%}
  #chAll table{min-width:0;width:100%}
  #chAll table th:nth-child(1),#chAll table td:nth-child(1),
  #chAll table th:nth-child(4),#chAll table td:nth-child(4){display:none}
  #tab-channels .panel{overflow-x:hidden}
  #tab-taobao .ph{flex-wrap:wrap}
  #tab-taobao .ph > span{display:flex;flex-wrap:wrap;width:100%;gap:8px}
  #tbStatus{flex:1 1 100%;min-width:0;line-height:1.55;word-break:normal}
  #tbList{overflow-x:auto}
  .pur-row{flex-direction:column;align-items:flex-start;gap:8px;padding:12px}
  .pur-title{font-size:.94rem;min-width:unset;width:100%}
  .sup-table td,.sup-table th{font-size:.92rem;padding:10px 8px}
  .stats{grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px}
  .sv{font-size:1.3rem}
}

/* ═══════════════════════════════════════════════════════════════
   ЗБІЛЬШЕННЯ ДРІБНИХ ІНЛАЙН-НАПИСІВ
   В HTML сотні style="font-size:9px" — вручну їх не переписати,
   тому масштабуємо через атрибутні селектори + --fs (кнопки A−/A+)
   ═══════════════════════════════════════════════════════════════ */
[style*="font-size:8px"],[style*="font-size:9px"],[style*="font-size:10px"]{
  font-size:calc(12px * var(--fs))!important;line-height:1.5
}
[style*="font-size:11px"],[style*="font-size:12px"]{
  font-size:calc(13px * var(--fs))!important;line-height:1.5
}
[style*="font-size:13px"]{font-size:calc(14px * var(--fs))!important}
[style*="font-size:14px"]{font-size:calc(15px * var(--fs))!important}

/* compact mode */
body.compact-ui .panel{padding:10px 12px;margin-bottom:10px}
body.compact-ui .ph{margin-bottom:8px}
body.compact-ui .ov-tile{padding:9px 11px}
body.compact-ui table td, body.compact-ui table th{padding:4px 7px}
body.compact-ui .tab{padding:7px 10px}
body.compact-ui .tabs{gap:4px}

</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js">
</script>
</head>
<body>
<svg style="display:none" aria-hidden="true">
<symbol id="ic-grid" viewBox="0 0 24 24"><rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.5"/></symbol>
<symbol id="ic-receipt" viewBox="0 0 24 24"><path d="M6.5 3.5h11v17l-2.75-1.8L12 20.5l-2.75-1.8L6.5 20.5v-17z"/><path d="M9.5 8.5h5M9.5 12h5"/></symbol>
<symbol id="ic-inbox" viewBox="0 0 24 24"><path d="M3.5 13.5l3-8h11l3 8v5.5a1 1 0 0 1-1 1h-15a1 1 0 0 1-1-1v-5.5z"/><path d="M3.5 13.5h4.5l1 2h6l1-2h4.5"/></symbol>
<symbol id="ic-store" viewBox="0 0 24 24"><path d="M4 9.5l1.5-5.5h13L20 9.5"/><path d="M4.5 9.5h15V19a1 1 0 0 1-1 1h-13a1 1 0 0 1-1-1V9.5z"/><path d="M9.5 20v-5.5h5V20"/></symbol>
<symbol id="ic-box" viewBox="0 0 24 24"><path d="M12 3.5l8.5 4.75v7.5L12 20.5 3.5 15.75v-7.5L12 3.5z"/><path d="M3.5 8.25L12 13l8.5-4.75M12 13v7.5"/></symbol>
<symbol id="ic-cart" viewBox="0 0 24 24"><circle cx="9.5" cy="19.5" r="1.3"/><circle cx="17.5" cy="19.5" r="1.3"/><path d="M3.5 4.5h2l2.4 10.5h10.2L20.5 7.5H6.5"/></symbol>
<symbol id="ic-tag" viewBox="0 0 24 24"><path d="M19.5 13.5l-6.5 6.5-8.5-8.5v-6h6l9 8z"/><circle cx="8.5" cy="8.5" r="1.3"/></symbol>
<symbol id="ic-layers" viewBox="0 0 24 24"><path d="M12 3.5l8.5 4.5-8.5 4.5L3.5 8 12 3.5z"/><path d="M3.5 13L12 17.5 20.5 13"/></symbol>
<symbol id="ic-chart" viewBox="0 0 24 24"><path d="M4.5 19.5V10M9.5 19.5V4.5M14.5 19.5v-6.5M19.5 19.5v-10M3 21h18"/></symbol>
<symbol id="ic-gear" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M12 3v2.5M12 18.5V21M3 12h2.5M18.5 12H21M5.6 5.6l1.8 1.8M16.6 16.6l1.8 1.8M18.4 5.6l-1.8 1.8M7.4 16.6l-1.8 1.8"/></symbol>
<symbol id="ic-plus" viewBox="0 0 24 24"><path d="M12 5.5v13M5.5 12h13"/></symbol>
<symbol id="ic-refresh" viewBox="0 0 24 24"><path d="M20 12a8 8 0 1 1-2.4-5.7"/><path d="M20 4.5V12h-7.5"/></symbol>
<symbol id="ic-ext" viewBox="0 0 24 24"><path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></symbol>
<symbol id="ic-scale" viewBox="0 0 24 24"><path d="M12 4v16M7 20h10"/><path d="M4 9l4-4 4 4"/><path d="M12 9l4-4 4 4"/><path d="M2 9h8M14 9h8"/></symbol>
<symbol id="ic-calc" viewBox="0 0 24 24"><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8.5 7h7M8.5 11.5h1M12 11.5h1M15.5 11.5h1M8.5 15h1M12 15h1M15.5 15h1M8.5 18.5h1M12 18.5h1M15.5 18.5h1"/></symbol>
<symbol id="ic-key" viewBox="0 0 24 24"><circle cx="8.5" cy="15.5" r="3.6"/><path d="M11.2 12.9L19 5.1M16.3 7.8l2.1 2.1M14.1 10l1.6 1.6"/></symbol>
<symbol id="ic-mark" viewBox="0 0 24 24"><path d="M12 3.6L21.2 20.4H2.8L12 3.6z" fill="currentColor" stroke="none"/></symbol>
<symbol id="ic-tg" viewBox="0 0 24 24"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212-.07-.062-.174-.041-.249-.024-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></symbol>
<symbol id="ic-dc" viewBox="0 0 24 24"><path d="M20.317 4.37a19.79 19.79 0 0 0-4.885-1.515.074.074 0 0 0-.078.037c-.211.375-.445.865-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.6 12.6 0 0 0-.618-1.25.077.077 0 0 0-.078-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.319 13.58.099 18.058a.082.082 0 0 0 .031.056c2.053 1.508 4.041 2.423 5.993 3.03a.078.078 0 0 0 .084-.028c.462-.63.873-1.295 1.226-1.994a.076.076 0 0 0-.042-.106c-.652-.247-1.274-.55-1.872-.892a.077.077 0 0 1-.007-.128c.126-.094.252-.192.372-.291a.074.074 0 0 1 .078-.011c3.928 1.793 8.18 1.793 12.061 0a.074.074 0 0 1 .079.01c.12.099.246.198.373.292a.077.077 0 0 1-.007.128 12.3 12.3 0 0 1-1.873.891.077.077 0 0 0-.04.107c.36.698.772 1.363 1.225 1.993a.076.076 0 0 0 .084.029c1.961-.607 3.95-1.522 6.002-3.03a.077.077 0 0 0 .032-.055c.5-5.177-.838-9.674-3.549-13.661a.061.061 0 0 0-.031-.028zM8.02 15.331c-1.183 0-2.157-1.086-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.211 0 2.176 1.095 2.157 2.419 0 1.333-.956 2.419-2.157 2.419zm7.975 0c-1.183 0-2.157-1.086-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.211 0 2.176 1.095 2.157 2.419 0 1.333-.946 2.419-2.157 2.419z"/></symbol>
</svg>
<div class="w">
<header>
  <div class="logo">
    <img id="brandMark" src="/brand-icon.png" width="50" height="50" style="border-radius:14px;flex:none;box-shadow:0 6px 18px rgba(0,0,0,.45)" alt="Ledger">
    <h1 id="hdrTitle"><span id="hdrName">Ledger</span><span id="planBadge" style="display:none">+</span><span data-i18n="hdr.sub">УГОДИ · КАНАЛИ · ПОШТА</span></h1>
  </div>
  <div style="display:flex;gap:7px;align-items:center;flex-wrap:wrap">
    <button class="langbtn" id="langUk" onclick="setLang('uk')" title="Українська">UA</button>
    <button class="langbtn" id="langEn" onclick="setLang('en')" title="English">EN</button>
    <button class="langbtn" id="langRu" onclick="setLang('ru')" title="Русский">RU</button>
    <a class="social tg" href="https://t.me/ledger_os" target="_blank" rel="noopener" title="Ledger OS — Telegram"><svg viewBox="0 0 24 24"><use href="#ic-tg"/></svg><span>Telegram</span></a>
    <a class="social dc" href="https://discord.gg/eMBXnKA3Pa" target="_blank" rel="noopener" title="Ledger OS — Discord"><svg viewBox="0 0 24 24"><use href="#ic-dc"/></svg><span>Discord</span></a>
    <button class="btn" onclick="location.reload()" title="Оновити сторінку" style="padding:7px 12px">↺</button>
  </div>
</header>
<div id="orderBanner"><span style="font-size:17px">🔔</span><b id="orderBannerText" data-i18n="order.new">Нове замовлення</b><button class="btn gr" style="padding:5px 10px;font-size:11px" onclick="goOrders()" data-i18n="order.open">Відкрити</button></div>

<div id="onb" class="onb" style="display:none">
  <div class="onb-card">
    <div class="onb-step" id="onbStepInfo">1 / 3</div>
    <h2 id="onbTitle">Welcome to Ledger</h2>
    <div id="onbBody"></div>
    <div class="onb-actions">
      <button class="btn" onclick="onbSkip()" id="onbSkip">Skip</button>
      <button class="btn gr" onclick="onbNext()" id="onbNext">Next →</button>
    </div>
  </div>
</div>

<div class="tabs">
  <div class="tab on" onclick="sw('overview',this)"><svg class="ic"><use href="#ic-grid"/></svg><span data-i18n="nav.overview">Огляд</span></div>
  <div class="tab" onclick="sw('tracker',this)"><svg class="ic"><use href="#ic-receipt"/></svg><span data-i18n="nav.deals">Угоди</span></div>
  <div class="tab" onclick="sw('mail',this);loadMailQueue()"><svg class="ic"><use href="#ic-inbox"/></svg><span data-i18n="nav.orders">Замовлення</span><span id="mailBadge"></span></div>
  <div class="tab" onclick="sw('channels',this);loadPlatforms();loadEldorado()"><svg class="ic"><use href="#ic-store"/></svg><span data-i18n="nav.channels">Канали</span></div>
  <div class="tsep"></div>
  <div class="tab" onclick="sw('supply',this);loadSupply()"><svg class="ic"><use href="#ic-box"/></svg><span data-i18n="nav.catalog">Каталог</span></div>
  <div class="tab" onclick="sw('buy',this);loadBuyList(true)"><svg class="ic"><use href="#ic-cart"/></svg><span data-i18n="nav.plan">План</span></div>
  <div class="tab" onclick="sw('taobao',this);loadTaobao()"><svg class="ic"><use href="#ic-tag"/></svg><span data-i18n="nav.taobao">Taobao</span></div>
  <div class="tab" onclick="sw('inventory',this);loadInventory()"><svg class="ic"><use href="#ic-layers"/></svg><span data-i18n="nav.inventory">Інвентар</span></div>
  <div class="tsep"></div>
  <div class="tab" onclick="sw('stats',this);renderStats();setTimeout(renderRevenueChart,80)"><svg class="ic"><use href="#ic-chart"/></svg><span data-i18n="nav.analytics">Аналітика</span></div>
  <div class="tab" onclick="sw('plus',this);loadPlus()"><span style="font-size:14px;font-weight:900;color:var(--gr)">✦</span><span data-i18n="nav.plus">Ledger+</span></div>
  <div class="tab" onclick="sw('setup',this);loadBackupList();loadSettings();loadMobile();initDesktopPrefs()"><svg class="ic"><use href="#ic-gear"/></svg></div>
</div>

<nav id="mnav" aria-label="Mobile navigation">
  <button type="button" class="mn on" data-tab="overview" onclick="mnavGo('overview')"><svg class="ic"><use href="#ic-grid"/></svg><span data-i18n="nav.overview">Огляд</span></button>
  <button type="button" class="mn" data-tab="tracker" onclick="mnavGo('tracker')"><svg class="ic"><use href="#ic-receipt"/></svg><span data-i18n="nav.deals">Угоди</span></button>
  <button type="button" class="mn" data-tab="mail" onclick="mnavGo('mail')"><svg class="ic"><use href="#ic-inbox"/></svg><span data-i18n="nav.orders">Замовлення</span></button>
  <button type="button" class="mn" data-tab="inventory" onclick="mnavGo('inventory')"><svg class="ic"><use href="#ic-layers"/></svg><span data-i18n="nav.inventory">Інвентар</span></button>
  <button type="button" class="mn" data-tab="stats" onclick="mnavGo('stats')"><svg class="ic"><use href="#ic-chart"/></svg><span data-i18n="nav.analytics">Аналітика</span></button>
</nav>

<div id="tab-overview" class="tc on">
  <div class="panel">
    <div class="ph"><span data-i18n="ov.today">Сьогодні</span>
      <div style="display:flex;gap:6px;flex-wrap:wrap">
        <button class="btn" onclick="sw('tracker',document.querySelectorAll('.tab')[1])"><svg class="ic"><use href="#ic-plus"/></svg><span data-i18n="ov.add">Угода</span></button>
        <button class="btn" onclick="sw('channels',document.querySelectorAll('.tab')[3]);loadPlatforms(true)"><svg class="ic"><use href="#ic-refresh"/></svg><span data-i18n="ov.channels">Канали</span></button>
        <button class="btn" onclick="sw('taobao',document.querySelectorAll('.tab')[6])"><span>Taobao</span></button>
      </div>
    </div>
    <div class="ov-tiles">
      <div class="ov-tile"><div class="ov-k" data-i18n="ov.profit">Прибуток · місяць</div><div class="ov-v gr" id="ovProfit">—</div><div class="ov-d" id="ovProfitD"></div></div>
      <div class="ov-tile"><div class="ov-k" data-i18n="ov.actions">Потребує дії</div><div class="ov-v" id="ovActions">—</div><div class="ov-d" id="ovActionsD"></div></div>
      <div class="ov-tile"><div class="ov-k" data-i18n="ov.stock">Склад</div><div class="ov-v" id="ovStock">—</div><div class="ov-d" id="ovStockD"></div></div>
      <div class="ov-tile"><div class="ov-k" data-i18n="ov.health">Стан системи</div><div class="ov-v" id="ovHealth" style="font-size:.95rem">—</div><div class="ov-d" id="ovHealthD"></div></div>
    </div>
  </div>
  <div class="panel" id="quickStart" style="display:none">
    <div class="ph"><span>🚀 <span data-i18n="qs.title">Швидкий старт</span></span></div>
    <div style="font-size:12px;color:var(--mu);margin-bottom:10px" data-i18n="qs.hint">Ще немає угод. Почни з однієї з дій — дані одразу з’являться в огляді.</div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:8px">
      <button class="btn gr" style="padding:12px" onclick="sw('tracker',document.querySelectorAll('.tab')[1])">➕ <span data-i18n="qs.deal">Додати угоду</span></button>
      <button class="btn" style="padding:12px" onclick="sw('channels',document.querySelectorAll('.tab')[3]);loadPlatforms(true)">🔗 <span data-i18n="qs.channels">Підключити канал</span></button>
      <button class="btn" style="padding:12px" onclick="sw('mail',document.querySelectorAll('.tab')[2]);loadMailQueue()">📥 <span data-i18n="qs.orders">Імпорт замовлень</span></button>
      <button class="btn" style="padding:12px" onclick="createDemoOrder()">🧪 <span data-i18n="qs.demo">Демо-замовлення</span></button>
    </div>
  </div>
  <div class="panel">
    <div class="ph"><span data-i18n="ov.feed">Що сталось</span></div>
    <div id="ovFeed" class="bub-wrap"></div>
  </div>
</div>

<div id="tab-channels" class="tc">
  <div class="panel">
    <div class="ph"><span data-i18n="ph.allch">Усі канали — останні продажі</span>
      <div style="font-size:12px;color:var(--mu)" id="chAllSum"></div>
    </div>
    <div id="chAll"><div class="none">⏳ …</div></div>
  </div>
  <div class="panel" style="padding:14px 16px">
    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
      <div class="seg" id="chSeg">
        <button class="seg-b on" onclick="chView('bal')"><svg class="ic"><use href="#ic-store"/></svg><span data-i18n="ch.bal">Баланси</span></button>
        <button class="seg-b" onclick="chView('ed')"><svg class="ic"><use href="#ic-receipt"/></svg><span>Eldorado — продажі</span></button>
      </div>
      <div style="flex:1"></div>
      <button class="btn" onclick="loadPlatforms(true)"><svg class="ic"><use href="#ic-refresh"/></svg><span data-i18n="ch.refresh">Оновити</span></button>
    </div>
  </div>
</div>

<div id="tab-tracker" class="tc">
  <!-- Додати запис -->
  <div class="panel">
    <div class="ph"><span data-i18n="ph.newDeal">+ НОВИЙ ПРОДАЖ</span></div>
    <div style="font-size:10.5px;color:var(--mu);margin:-6px 0 10px" data-i18n="f.currencyHint">Суми вводяться у валюті угоди. Курс — скільки одиниць валюти за 1 USD; він зберігається для історії.</div>
    <div id="invSellBanner" style="display:none;margin:0 0 10px;padding:8px 11px;border:1px solid var(--gr);border-radius:8px;background:color-mix(in srgb,var(--gr) 8%,transparent);font-size:12px;display:none;align-items:center;gap:8px">
      <span>📦 <b data-i18n="inv.sellFromStock">Продаж зі складу:</b> <span id="invSellText"></span></span>
      <button class="btn" style="margin-left:auto;padding:3px 8px;font-size:11px" onclick="clearInvSell()">✕</button>
    </div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
      <div>
        <div style="font-size:9px;color:var(--mu);letter-spacing:1px;margin-bottom:3px" data-i18n="f.title">НАЗВА (необов.)</div>
        <input id="plTitle" data-i18n-ph="ph.dealTitle" placeholder="напр. Arknights Starter" style="width:220px" oninput="applyProfileFee()">
      </div>
      <div>
        <div style="font-size:9px;color:var(--mu);letter-spacing:1px;margin-bottom:3px" data-i18n="f.platform">ПЛАТФОРМА</div>
        <input type="hidden" id="plPlatform" value="zeusx">
        <div class="psel" id="plPlatSel">
          <button type="button" class="psel-btn" onclick="plPlatToggle(event)">
            <img class="psel-logo" id="plPlatLogo" src="/logo/zeusx.png" alt="">
            <span id="plPlatName">ZeusX</span><span class="car">▾</span>
          </button>
          <div class="psel-list">
            <div class="psel-opt on" data-val="zeusx" onclick="plPlatPick('zeusx')">
              <img class="psel-logo" src="/logo/zeusx.png" alt=""><span>ZeusX</span><span class="fee">−5–10%</span></div>
            <div class="psel-opt" data-val="funpay" onclick="plPlatPick('funpay')">
              <img class="psel-logo" src="/logo/funpay.png" alt=""><span>FunPay</span><span class="fee">−10%</span></div>
            <div class="psel-opt" data-val="eldorado" onclick="plPlatPick('eldorado')">
              <img class="psel-logo" src="/logo/eldorado.png" alt=""><span>Eldorado</span><span class="fee">−10%</span></div>
            <div class="psel-opt" data-val="other" onclick="plPlatPick('other')">
              <svg class="ic"><use href="#ic-grid"/></svg><span data-i18n="f.other">Інше</span><span class="fee">0%</span></div>
          </div>
        </div>
      </div>
      <div id="plZeusRankWrap" style="display:none">
        <div style="font-size:9px;color:var(--mu);letter-spacing:1px;margin-bottom:3px" data-i18n="f.zeusRank">РАНГ ZEUSX</div>
        <select id="plZeusRank" onchange="plZeusRankPick()" style="width:120px"></select>
      </div>
      <div>
        <div style="font-size:9px;color:var(--mu);letter-spacing:1px;margin-bottom:3px" data-i18n="f.currency">ВАЛЮТА УГОДИ</div>
        <select id="plCur" onchange="plCurPick()" style="width:115px;font-size:12px"></select>
      </div>
      <div>
        <div style="font-size:9px;color:var(--mu);letter-spacing:1px;margin-bottom:3px" data-i18n="f.rate">КУРС / USD</div>
        <input type="number" id="plFx" value="1" step="0.0001" min="0.000001" style="width:95px" oninput="updateFeePreview()">
      </div>
      <div>
        <div style="font-size:9px;color:var(--mu);letter-spacing:1px;margin-bottom:3px" data-i18n="f.feePct">КОМІСІЯ %</div>
        <input type="number" id="plFeePct" value="9.5" step="0.1" min="0" max="100" style="width:82px" oninput="updateFeePreview()">
      </div>
      <div>
        <div style="font-size:9px;color:var(--mu);letter-spacing:1px;margin-bottom:3px" data-i18n="f.expenses">ІНШІ ВИТРАТИ</div>
        <input type="number" id="plExpenses" value="0" step="0.01" min="0" style="width:95px" oninput="updateFeePreview()">
      </div>
      <div>
        <div style="font-size:9px;color:var(--mu);letter-spacing:1px;margin-bottom:3px" data-i18n="f.buy">КУПИВ</div>
        <input type="number" id="plBuy" placeholder="0.00" step="0.01" min="0" style="width:90px" oninput="updateFeePreview()">
      </div>
      <div>
        <div style="font-size:9px;color:var(--mu);letter-spacing:1px;margin-bottom:3px" data-i18n="f.sell">ПРОДАВ</div>
        <input type="number" id="plSell" placeholder="0.00" step="0.01" min="0" style="width:90px" oninput="updateFeePreview()">
      </div>
      <div>
        <div style="font-size:9px;color:var(--mu);letter-spacing:1px;margin-bottom:3px" data-i18n="f.after">ПІСЛЯ КОМІСІЇ</div>
        <div id="plFeePreview" style="font-family:var(--font);font-size:14px;font-weight:700;color:var(--gr);padding:6px 0">$0.00</div>
      </div>
      <div>
        <div style="font-size:9px;color:var(--mu);letter-spacing:1px;margin-bottom:3px" data-i18n="f.net">ЧИСТИЙ ПРИБУТОК</div>
        <div id="plNetPreview" style="font-family:var(--font);font-size:14px;font-weight:800;color:var(--gr);padding:6px 0">$0.00</div>
      </div>
      <div>
        <div style="font-size:9px;color:var(--mu);letter-spacing:1px;margin-bottom:3px" data-i18n="f.date">ДАТА</div>
        <input type="date" id="plDate" style="width:130px">
      </div>
      <button class="btn gr" onclick="addPLRecord()" data-i18n="b.add">+ ДОДАТИ</button>
      <button class="btn" style="font-size:13px" onclick="syncPLToServer()" data-i18n="b.sync">СИНХРОНІЗУВАТИ</button>
      <button class="btn pu" style="font-size:13px" onclick="openBulkRename()" data-i18n="b.bulk">МАСОВО</button>
      <button class="btn" style="font-size:13px" onclick="openBulkFee()">% <span data-i18n="b.bulkFee">КОМІСІЯ</span></button>
    </div>
  </div>

  <!-- Таблиця -->
  <div class="panel">
    <div class="ph">
      <span><span data-i18n="k.records">ЗАПИСИ</span> (<span id="purCnt">0</span>)</span>
      <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center">
        <input id="purQ" data-i18n-ph="k.search" placeholder="Пошук..." oninput="renderPurchases()" style="width:150px">
        <select id="purFilter" onchange="renderPurchases()" style="font-size:11px">
          <option value="" data-i18n="allPlat">Всі платформи</option>
          <option value="zeusx">⚡ ZeusX</option>
          <option value="funpay">🔵 FunPay</option>
          <option value="eldorado">Eldorado</option>
          <option value="notitle" data-i18n="s.noTitle">⚠ Без назви</option>
        </select>
        <select id="plDateFilter" onchange="toggleCustomDateRange();renderPurchases()" style="font-size:11px">
          <option value="" data-i18n="per.all">Весь час</option>
          <option value="today" data-i18n="per.today">Сьогодні</option>
          <option value="week" data-i18n="per.week">Цей тиждень</option>
          <option value="month" data-i18n="per.month">Цей місяць</option>
          <optgroup label="Місяці" id="plMonthGroup" data-i18n-label="per.months"></optgroup>
          <option value="custom">📅 <span data-i18n="per.custom">Свій період</span></option>
        </select>
        <div id="plCustomRange" style="display:none;align-items:center;gap:4px">
          <input type="date" id="plDateFrom" onchange="renderPurchases()" style="font-size:11px;padding:3px 5px;background:var(--card2);border:1px solid var(--brd);border-radius:4px;color:var(--tx)">
          <span style="color:var(--mu);font-size:11px">—</span>
          <input type="date" id="plDateTo" onchange="renderPurchases()" style="font-size:11px;padding:3px 5px;background:var(--card2);border:1px solid var(--brd);border-radius:4px;color:var(--tx)">
        </div>
        <select id="plSortF" onchange="renderPurchases()" style="font-size:11px">
          <option value="date_d" data-i18n="s.dateDesc">Дата ↓</option>
          <option value="date_a" data-i18n="s.dateAsc">Дата ↑</option>
          <option value="profit_d" data-i18n="s.profitDesc">Прибуток ↓</option>
          <option value="sell_d" data-i18n="s.sellDesc">Продаж ↓</option>
        </select>
        <button class="btn" style="font-size:8px" onclick="exportCSV()">⬇ CSV</button>
        <button class="btn gr" style="font-size:8px" onclick="exportFullExcel()">📊 Excel (всі дані)</button>
        <button class="btn rd" style="font-size:8px" onclick="if(confirm('Очистити всі записи?')){purchases=[];savePL();renderPurchases();}">🗑 Очистити</button>
      </div>
    </div>
    <div id="purList"><div class="none">Ще немає записів</div></div>
    <div id="plPag" class="pag" style="display:none"></div>
  </div>
</div>

<div id="tab-eldorado" data-nested="1">
  <div class="panel">
    <div class="ph"><span data-i18n="ph.edsales">Eldorado — продажі</span></div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;align-items:center">
      <input type="date" id="edDate" style="font-size:13px;padding:5px 8px;background:var(--card2);border:1px solid var(--brd);border-radius:5px;color:var(--tx)">
      <input type="text" id="edTitle" data-i18n-ph="ed.title" placeholder="Назва товару" onblur="suggestEdBuy()" style="font-size:13px;padding:5px 8px;background:var(--card2);border:1px solid var(--brd);border-radius:5px;color:var(--tx);flex:1;min-width:150px">
      <input type="number" id="edBuy" data-i18n-ph="ed.buy" placeholder="Ціна купівлі $" step="0.01" style="font-size:13px;padding:5px 8px;background:var(--card2);border:1px solid var(--brd);border-radius:5px;color:var(--tx);width:110px">
      <input type="number" id="edPrice" data-i18n-ph="ed.sell" placeholder="Ціна продажу $" step="0.01" style="font-size:13px;padding:5px 8px;background:var(--card2);border:1px solid var(--brd);border-radius:5px;color:var(--tx);width:110px">
      <input type="text" id="edOrderId" data-i18n-ph="ed.oid" placeholder="Order ID (необов'язково)" style="font-size:13px;padding:5px 8px;background:var(--card2);border:1px solid var(--brd);border-radius:5px;color:var(--tx);width:200px">
      <input type="text" id="edCat" list="edCatList" data-i18n-ph="ed.cat" placeholder="Категорія (необов'язково)" style="font-size:13px;padding:5px 8px;background:var(--card2);border:1px solid var(--brd);border-radius:5px;color:var(--tx);width:190px">
      <datalist id="edCatList"></datalist>
      <button onclick="addEdorado()" class="btn" style="padding:7px 16px;font-size:13px">➕ Додати</button>
      <label class="btn" style="padding:7px 16px;font-size:13px;cursor:pointer;background:var(--a2)">📥 Імпорт CSV<input type="file" id="edCsvFile" accept=".csv,.tsv" style="display:none" onchange="importEdCsv(this)"></label>
    </div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:12px">
      <input id="edQ" placeholder="🔍 Пошук..." oninput="edPg=1;renderEldorado()" style="width:200px;font-size:13px">
      <select id="edDateFilter" onchange="toggleEdRange();edPg=1;renderEldorado()" style="font-size:13px">
        <option value="" data-i18n="per.all">Весь час</option>
        <option value="today" data-i18n="per.today">Сьогодні</option>
        <option value="week" data-i18n="per.week">Цей тиждень</option>
        <option value="month" data-i18n="per.month">Цей місяць</option>
        <option value="custom" data-i18n="per.custom">📅 Свій період</option>
      </select>
      <div id="edCustomRange" style="display:none;align-items:center;gap:4px">
        <input type="date" id="edFrom" onchange="edPg=1;renderEldorado()" style="font-size:13px">
        <span style="color:var(--mu)">—</span>
        <input type="date" id="edTo" onchange="edPg=1;renderEldorado()" style="font-size:13px">
      </div>
      <button class="btn" onclick="exportEdCsv()" style="font-size:10px">⬇ <span data-i18n="ed.csvbtn">CSV (фільтр)</span></button>
    </div>
    <div id="edList"><div class="none" data-i18n="ed.empty">Ще немає записів</div></div>
    <div id="edPag" class="pag" style="display:none"></div>
  </div>
  <div class="panel" style="margin-top:14px">
    <div class="ph"><span data-i18n="ph.cats">РОЗБИВКА ПО КАТЕГОРІЯХ</span></div>
    <div id="edBreakdown"><div class="none">Немає даних</div></div>
  </div>
</div>
<div id="tab-buy" class="tc">
  <div class="panel">
    <div class="ph" style="display:flex;justify-content:space-between;align-items:center">
      <span data-i18n="plan.title">ЩО КУПИТИ СЬОГОДНІ</span>
      <button class="btn" style="font-size:12px;padding:5px 11px" onclick="loadBuyList(true)"><svg class="ic"><use href="#ic-refresh"/></svg><span data-i18n="btn.refresh">Оновити</span></button>
    </div>
    <div style="font-size:12px;color:var(--mu);margin-bottom:12px" data-i18n="plan.hint">Ціна постачальника проти вашої медіани продажу по схожих лотах, комісія ZeusX 5–10% за рангом.</div>
    <div id="restockBox" style="margin-bottom:14px"></div>
    <div id="buyList"><div class="none">⏳ Рахую...</div></div>
  </div>
</div>

<div id="tab-supply" class="tc">
  <div id="supAl" class="al info">⏳ Завантаження постачальників...</div>
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px">
    <div class="sc"><div class="sl">ВСЬОГО</div><div class="sv" id="supTotal">—</div></div>
    <div id="supCards" style="display:flex;gap:8px;flex-wrap:wrap"></div>
  </div>
  <div class="panel">
    <div class="ph"><span><span data-i18n="ph.products">ТОВАРИ</span> (<span id="supCnt">0</span>)</span>
      <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center">
        <input id="supQ" data-i18n-ph="cf.search" placeholder="🔍 Пошук..." oninput="renderSupply()" style="width:180px">
        <select id="supSrc" onchange="loadSupply()" style="font-size:13px"><option value="" data-i18n="all">All</option></select>
        <select id="supSort" onchange="renderSupply()" style="font-size:11px">
          <option value="" data-i18n="cf.sortNone">Без сорт.</option>
          <option value="new" selected data-i18n="cf.sortNew">Нові першими</option>
          <option value="updated" data-i18n="cf.sortUpdated">Оновлені першими</option>
          <option value="pa" data-i18n="cf.priceUp">Ціна ↑</option>
          <option value="pd" data-i18n="cf.priceDown">Ціна ↓</option>
          <option value="sale" data-i18n="cf.saleFirst">Sale першими</option>
        </select>
        <label style="font-size:11px;color:var(--mu);display:flex;align-items:center;gap:4px;cursor:pointer">
          <input type="checkbox" id="supAvail" onchange="renderSupply()"> <span data-i18n="cf.avail">є в наявності</span>
        </label>
        <label style="font-size:11px;color:var(--mu);display:flex;align-items:center;gap:4px;cursor:pointer" title="Товари, які зникли з полиць магазинів за останні 14 днів">
          <input type="checkbox" id="supGone" onchange="renderSupply()"> <span data-i18n="cf.gone">зниклі</span>
        </label>
        <label style="font-size:11px;color:var(--mu);display:flex;align-items:center;gap:4px;cursor:pointer" title="Товари, які в іншому магазині дешевші">
          <input type="checkbox" id="supCheaper" onchange="renderSupply()"> <span data-i18n="cf.cheaper">дешевше</span>
        </label>
        <button class="btn" style="font-size:12px;padding:5px 11px" onclick="checkNews()" title="Швидка перевірка новинок через sitemap (безкоштовно)">🆕 Новинки</button>
        <button class="btn" style="font-size:12px;padding:5px 11px" onclick="refreshSuppliers()" title="Повне оновлення бази (витрачає кредити ScraperAPI)">↻ Оновити зараз</button>
        <span id="supStatus" style="font-size:11px;color:var(--mu)"></span>
        <button class="btn" style="font-size:9px;padding:3px 9px" onclick="loadSupply(1,true)">↺</button>
      </div>
    </div>
    <div id="supList"><div class="none"><span class="spin">⏳</span></div></div>
    <div id="supPag" class="pag" style="display:none"></div>
  </div>
</div>

<!-- 📥 ЗАМОВЛЕННЯ З ПОШТИ -->
<div id="tab-mail" class="tc">
  <div class="panel">
    <div class="ph"><span data-i18n="ph.orders">ЗАМОВЛЕННЯ З ПОШТИ</span>
      <button class="btn" style="font-size:12px;padding:5px 11px" onclick="clearMailQueue()">🗑 <span data-i18n="order.clear">Очистити всі</span></button>
      <div style="display:flex;gap:8px;align-items:center">
        <span id="mailStat" style="font-size:12px;color:var(--mu)"></span>
        <button class="btn" id="orderNotifyBtn" style="padding:5px 10px;font-size:11px" onclick="enableOrderNotifications()">🔔 <span data-i18n="order.notify">Сповіщення</span></button>
        <button class="btn" style="padding:5px 10px;font-size:11px" onclick="playOrderSound()" title="Test sound">🔊</button>
        <button class="btn" style="padding:5px 10px;font-size:11px" onclick="createDemoOrder()">🧪 <span data-i18n="order.demo">Демо</span></button>
        <label style="font-size:11px;color:var(--mu);display:flex;align-items:center;gap:4px"><input id="orderSound" type="checkbox" checked> <span data-i18n="order.sound">звук</span></label>
        <label style="font-size:11px;color:var(--mu);display:flex;align-items:center;gap:4px" title="Auto-create a deal from each new order that already has a price"><input id="autoAddOrders" type="checkbox" onchange="saveAutoAddOrders()"> <span data-i18n="order.autoAdd">авто в P&L</span></label>
        <button class="btn" onclick="loadMailQueue(true)">↺ <span data-i18n="an.refresh">Оновити</span></button>
      </div>
    </div>
    <div style="font-size:13px;color:var(--mu);margin-bottom:14px">
      <span data-i18n="mail.desc">Листи від FunPay / ZeusX / Eldorado, які трекер уже розпізнав. Нічого не додається автоматично: перенесіть одним кліком у ELDORADO або P&amp;L, або проігноруйте.</span>
    </div>
    <div id="mailHint"></div>
    <div id="mailList"><div class="none">⏳ Завантаження...</div></div>
  </div>
</div>

<div id="replyModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.72);z-index:10000;align-items:center;justify-content:center;padding:16px">
  <div style="background:var(--card);border:1px solid var(--brd);border-radius:14px;padding:18px;width:min(920px,96vw);max-height:90vh;overflow-y:auto">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:4px">
      <div style="font-size:15px;font-weight:800" id="replyTitle">💬</div>
      <button class="btn" onclick="closeReplyGenerator()" style="padding:4px 10px">✕</button>
    </div>
    <div id="replyHint" style="font-size:11px;color:var(--mu);margin-bottom:12px"></div>
    <div id="replyBody" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px"></div>
    <div style="display:flex;justify-content:flex-end;margin-top:12px">
      <button class="btn gr" onclick="regenReply()" id="replyRegen">↻</button>
    </div>
  </div>
</div>

<!-- 💼 ПЛАТФОРМИ -->
<div id="tab-platforms" data-nested="1">
  <div class="panel">
    <div class="ph"><span data-i18n="ph.channels">Канали</span>
      <button class="btn" onclick="loadPlatforms(true)">↺ Оновити з кабінетів</button>
    </div>
    <div style="font-size:13px;color:var(--mu);margin-bottom:14px">
      <span data-i18n="ch.src">Дані читаються з ваших кабінетів за збереженими cookie (ZeusX — API, FunPay — сторінка замовлень). Оновлюється не частіше ніж раз на 2 хвилини.</span>
    </div>
    <div style="background:var(--card2);border:1px solid var(--brd);border-radius:10px;padding:12px;margin-bottom:14px">
      <div style="font-size:13px;font-weight:800;margin-bottom:8px"><svg class="ic" style="margin-right:2px"><use href="#ic-key"/></svg> Cookie кабінетів
        <span id="ckStatus" style="font-weight:400;color:var(--mu);font-size:12px"></span></div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end">
        <label style="font-size:12px;color:var(--mu)">FunPay (golden_key)<br>
          <input id="ckFunpay" type="password" placeholder="golden_key=…" style="width:300px;margin-top:4px"></label>
        <label style="font-size:12px;color:var(--mu)">ZeusX (access_token)<br>
          <input id="ckZeusx" type="password" placeholder="access_token=…" style="width:300px;margin-top:4px"></label>
        <button class="btn gr" style="font-size:12px;padding:6px 12px" onclick="saveCookies()">Зберегти cookie</button>
        <button class="btn" style="font-size:12px;padding:6px 12px" onclick="cookieFromBrowser()" title="Прочитати cookie з відкритого вікна браузера (FunPay/ZeusX)">Взяти з браузера</button>
        <button class="btn rd" style="font-size:12px;padding:6px 12px" onclick="clearCookies()" data-i18n="set.cookieDisconnect">Disconnect cookies</button>
      </div>
      <div style="font-size:11px;color:var(--mu);margin-top:8px" data-i18n="ch.cookieHelp">Chrome/Edge: F12 → Application → Cookies → funpay.com → скопіюйте значення golden_key. Зберігається лише на сервері. Без FunPay-cookie замовлення з FunPay не надходять.</div>
    </div>
    <div id="platList"><div class="none">⏳ Завантаження...</div></div>

    <div style="margin-top:16px;padding-top:14px;border-top:1px solid var(--brd)">
      <div style="font-size:15px;font-weight:800;margin-bottom:10px">🏦 Де вигідніше продавати</div>
      <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:flex-end;margin-bottom:12px">
        <label style="font-size:13px;color:var(--mu)">Ціна продажу, USD<br>
          <input id="mpPrice" type="number" min="0" step="1" value="10" oninput="calcMarkets()" style="width:120px;margin-top:4px">
        </label>
        <label style="font-size:13px;color:var(--mu)">Собівартість, USD<br>
          <input id="mpCost" type="number" min="0" step="1" value="5" oninput="calcMarkets()" style="width:120px;margin-top:4px">
        </label>
        <span style="font-size:12px;color:var(--mu)">Комісії орієнтовні — уточнюйте тарифи майданчика</span>
      </div>
      <div id="mpTable"></div>
    </div>

    <div style="margin-top:16px;padding-top:14px;border-top:1px solid var(--brd)">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
        <div style="font-size:15px;font-weight:800">🏷 Мої лоти на ZeusX</div>
        <button class="btn" style="font-size:12px;padding:5px 11px" onclick="loadOffers(true)">↻ Оновити</button>
      </div>
      <div id="offersList"><div class="none">⏳ Завантаження...</div></div>
    </div>
  </div>
</div>

<!-- 🇨🇳 TAOBAO -->
<div id="tab-taobao" class="tc">
  <div class="panel" id="tbHero" style="margin-bottom:14px;background:radial-gradient(700px 260px at 0% 0%,rgba(52,211,153,.16),transparent 60%),linear-gradient(135deg,var(--card),var(--card2));border-color:color-mix(in srgb,var(--gr) 28%,var(--brd))">
    <div style="display:inline-flex;align-items:center;gap:7px;padding:4px 9px;border:1px solid color-mix(in srgb,var(--gr) 45%,var(--brd));border-radius:999px;font-size:10px;letter-spacing:.14em;color:var(--gr);font-weight:800;margin-bottom:12px">⚡ <span data-i18n="tb.heroBadge">АВТОМАТИЗАЦІЯ TAOBAO</span></div>
    <div style="display:flex;gap:22px;align-items:flex-start;flex-wrap:wrap">
      <div style="flex:1;min-width:280px">
        <div style="font-size:24px;font-weight:800;line-height:1.18;letter-spacing:-.02em;margin-bottom:8px" data-i18n="tb.heroTitle">Купуйте акаунти з Таобао дешевше — без ручного пошуку</div>
        <div style="font-size:13px;color:var(--mu);line-height:1.65;max-width:720px" data-i18n="tb.heroSub">Ledger щогодини збирає лоти, переводить юані в долари, показує потенційну маржу й підсвічує вигідні. Ви купуєте тільки те, що реально продається.</div>
        <div id="tbStatus" style="font-size:12px;color:var(--mu);font-weight:400;margin-top:10px"></div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:12px">
          <button data-paid-only class="btn gr" style="font-size:12px;padding:7px 12px" onclick="tbRequest()">⚡ <span data-i18n="tb.collect">Зібрати зараз</span></button>
          <button data-paid-only class="btn" style="font-size:12px;padding:7px 12px" onclick="tbAddManual()">＋ <span data-i18n="tb.lot">Додати лот</span></button>
          <button data-paid-only class="btn" style="font-size:12px;padding:7px 12px" onclick="tbEnrich()">💳 <span data-i18n="tb.checkPay">Перевірити оплату</span></button>
          <button data-free-only class="btn" style="font-size:12px;padding:7px 12px" onclick="document.getElementById('tbHow').open=true;document.getElementById('tbHow').scrollIntoView({behavior:'smooth'})">📖 <span data-i18n="tb.learnMore">Як це працює</span></button>
        </div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;min-width:260px;flex:0 1 330px">
        <div style="background:var(--card);border:1px solid var(--brd);border-radius:10px;padding:10px 12px"><div style="font-size:10px;color:var(--mu)" data-i18n="tb.stat1">Економія часу</div><div style="font-size:19px;font-weight:800;color:var(--gr)">3–5 <span style="font-size:11px" data-i18n="tb.stat1u">год/день</span></div></div>
        <div style="background:var(--card);border:1px solid var(--brd);border-radius:10px;padding:10px 12px"><div style="font-size:10px;color:var(--mu)" data-i18n="tb.stat2">Ціни</div><div style="font-size:19px;font-weight:800">¥ → $</div></div>
        <div style="background:var(--card);border:1px solid var(--brd);border-radius:10px;padding:10px 12px"><div style="font-size:10px;color:var(--mu)" data-i18n="tb.stat3">Оновлення</div><div style="font-size:19px;font-weight:800;color:var(--a1)" data-i18n="tb.stat3v">у фоні</div></div>
        <div style="background:var(--card);border:1px solid var(--brd);border-radius:10px;padding:10px 12px"><div style="font-size:10px;color:var(--mu)" data-i18n="tb.stat4">Маржа</div><div style="font-size:19px;font-weight:800;color:var(--gr)" data-i18n="tb.stat4v">одразу</div></div>
      </div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:8px;margin-top:14px">
      <div style="background:var(--card);border:1px solid var(--brd);border-radius:10px;padding:10px 12px"><div style="font-size:12px;font-weight:700;margin-bottom:3px" data-i18n="tb.ben1t">Автоматичний збір</div><div style="font-size:10.5px;color:var(--mu);line-height:1.45" data-i18n="tb.ben1d">Агент сам відкриває Таобао, оновлює лоти й чекає, поки ви пройдете капчу.</div></div>
      <div style="background:var(--card);border:1px solid var(--brd);border-radius:10px;padding:10px 12px"><div style="font-size:12px;font-weight:700;margin-bottom:3px" data-i18n="tb.ben2t">Маржа замість вгадування</div><div style="font-size:10.5px;color:var(--mu);line-height:1.45" data-i18n="tb.ben2d">Ціна в юанях, орієнтовний долар, ваша ціна продажу та потенційний прибуток — в одному рядку.</div></div>
      <div style="background:var(--card);border:1px solid var(--brd);border-radius:10px;padding:10px 12px"><div style="font-size:12px;font-weight:700;margin-bottom:3px" data-i18n="tb.ben3t">Один клік до угоди</div><div style="font-size:10.5px;color:var(--mu);line-height:1.45" data-i18n="tb.ben3d">Знайшли вигідний лот — додайте його в P&L, і він одразу стане частиною вашого обліку.</div></div>
    </div>
    <div data-no-currency style="margin-top:12px;background:var(--card);border:1px solid var(--brd);border-radius:12px;padding:12px">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:8px">
        <div style="font-size:11px;font-weight:800;letter-spacing:.08em;color:var(--mu)" data-i18n="taobao.demoTitle">ЯК ЦЕ ВИГЛЯДАЄ В РОБОТІ</div>
        <div style="font-size:9px;padding:2px 7px;border:1px solid var(--brd);border-radius:999px;color:var(--mu)" data-i18n="taobao.demoBadge">ДЕМО-ПРИКЛАД</div>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px">
        <div style="background:var(--card2);border:1px solid var(--brd);border-radius:9px;padding:9px 11px">
          <div style="display:flex;justify-content:space-between;gap:6px"><b style="font-size:12px">Genshin AR60</b><span style="font-size:9px;color:var(--gr);border:1px solid color-mix(in srgb,var(--gr) 40%,var(--brd));border-radius:5px;padding:1px 5px"> <span data-i18n="taobao.hot">HOT</span></span></div>
          <div style="font-size:10px;color:var(--mu);margin:3px 0 6px">EU · 5★ · e-mail</div>
          <div style="display:flex;justify-content:space-between;font-size:11px"><span data-i18n="taobao.buy">Купити</span><b>¥128 <span style="color:var(--mu)">≈$17.8</span></b></div>
          <div style="display:flex;justify-content:space-between;font-size:11px;margin-top:2px"><span data-i18n="taobao.sell">Продати</span><b>$39</b></div>
          <div style="display:flex;justify-content:space-between;font-size:11px;margin-top:2px;color:var(--gr)"><span data-i18n="taobao.margin">Маржа</span><b>+$21.2 · 54%</b></div>
        </div>
        <div style="background:var(--card2);border:1px solid var(--brd);border-radius:9px;padding:9px 11px">
          <div style="display:flex;justify-content:space-between;gap:6px"><b style="font-size:12px">Honkai: Star Rail</b><span style="font-size:9px;color:var(--yw);border:1px solid color-mix(in srgb,var(--yw) 40%,var(--brd));border-radius:5px;padding:1px 5px"> <span data-i18n="taobao.new">NEW</span></span></div>
          <div style="font-size:10px;color:var(--mu);margin:3px 0 6px">Global · starter · 5★</div>
          <div style="display:flex;justify-content:space-between;font-size:11px"><span data-i18n="taobao.buy">Купити</span><b>¥80 <span style="color:var(--mu)">≈$11.1</span></b></div>
          <div style="display:flex;justify-content:space-between;font-size:11px;margin-top:2px"><span data-i18n="taobao.sell">Продати</span><b>$29</b></div>
          <div style="display:flex;justify-content:space-between;font-size:11px;margin-top:2px;color:var(--gr)"><span data-i18n="taobao.margin">Маржа</span><b>+$14.9 · 51%</b></div>
        </div>
        <div style="background:var(--card2);border:1px solid var(--brd);border-radius:9px;padding:9px 11px">
          <div style="display:flex;justify-content:space-between;gap:6px"><b style="font-size:12px">Wuthering Waves</b><span style="font-size:9px;color:var(--a1);border:1px solid color-mix(in srgb,var(--a1) 40%,var(--brd));border-radius:5px;padding:1px 5px"> <span data-i18n="taobao.value">VALUE</span></span></div>
          <div style="font-size:10px;color:var(--mu);margin:3px 0 6px">Asia · 2×5★ · linked</div>
          <div style="display:flex;justify-content:space-between;font-size:11px"><span data-i18n="taobao.buy">Купити</span><b>¥245 <span style="color:var(--mu)">≈$34.0</span></b></div>
          <div style="display:flex;justify-content:space-between;font-size:11px;margin-top:2px"><span data-i18n="taobao.sell">Продати</span><b>$59</b></div>
          <div style="display:flex;justify-content:space-between;font-size:11px;margin-top:2px;color:var(--gr)"><span data-i18n="taobao.margin">Маржа</span><b>+$19.1 · 32%</b></div>
        </div>
      </div>
      <div style="font-size:10px;color:var(--mu);margin-top:7px" data-i18n="taobao.demoNote">Це демонстраційний приклад у USD. Реальні лоти, ціни й маржа з’являться після запуску агента.</div>
    </div>
    <details id="tbHow" style="margin-top:12px;font-size:11.5px;color:var(--mu);line-height:1.6">
      <summary style="cursor:pointer;color:var(--tx);font-weight:600" data-i18n="tb.how">Як працює агент і що потрібно</summary>
      <div data-i18n="tb.d1" style="margin-top:8px">Збирається колектором на вашому ПК. Агент працює у фоні (автозапуск при вході в Windows) і сам відкриває вікно браузера, якщо його немає. Капчу проходите ви — колектор чекає. Ціни в юанях, нижче — орієнтовний долар.</div>
      <div data-i18n="tb.d2" style="margin-top:6px">Мітки: натисніть 💳 біля лота, якщо там оплата карткою, і 🎛 — скільки варіантів акаунтів. Taobao часто блокує автоматичне читання сторінок лотів, тому ручна мітка — найнадійніше.</div>
      <div data-i18n="tb.need" style="margin-top:8px;padding-top:8px;border-top:1px solid var(--brd);color:var(--tx)">Щоб збір запрацював, потрібно: 1) агент збору на вашому ПК (окремий файл, запускається разом із Windows); 2) акаунт Taobao; 3) один раз увійти в браузері агента — сканування QR-коду з телефона; 4) капчу при першому запиті проходите ви вручну. Після цього лоти оновлюються у фоні, а ви бачите ціни тут.</div>
      <div data-i18n="tb.d3" style="margin-top:6px">Оплата: картка / Apple Pay через Alipay International (платформа, не продавець). Лоти «代充 / 充值 / 话费» (поповнення балансу, телефон, ключі) не підходять під таку оплату — вони вже відфільтровані.</div>
    </details>
    <div id="tbProgress" style="display:none;margin-top:12px">
      <div style="display:flex;justify-content:space-between;font-size:12px;color:var(--mu);margin-bottom:5px">
        <span id="tbProgText">—</span><span id="tbProgPct">0%</span>
      </div>
      <div style="height:8px;background:var(--card2);border:1px solid var(--brd);border-radius:999px;overflow:hidden">
        <div id="tbProgBar" style="height:100%;width:0%;background:linear-gradient(90deg,var(--a1),var(--gr));transition:width .4s"></div>
      </div>
    </div>
  </div>
  <div class="panel" id="tbWorkPanel">
    <div id="tbPaidBar" style="display:none;margin-bottom:12px">
      <div class="ph" style="margin-bottom:10px">TAOBAO — ціни з Китаю</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
        <button class="btn gr" style="font-size:12px;padding:6px 11px" onclick="tbRequest()">⚡ <span data-i18n="tb.collect">Зібрати зараз</span></button>
        <button class="btn" style="font-size:12px;padding:6px 11px" onclick="tbAddManual()">＋ <span data-i18n="tb.lot">Додати лот</span></button>
        <button class="btn" style="font-size:12px;padding:6px 11px" onclick="tbEnrich()">💳 <span data-i18n="tb.checkPay">Перевірити оплату</span></button>
      </div>
    </div>
    <details id="agentSetup" data-paid-only style="margin-bottom:12px;background:var(--card2);border:1px solid var(--brd);border-radius:9px;padding:10px 12px">
      <summary style="cursor:pointer;font-size:12px;font-weight:700">⚙ Налаштування Taobao-агента</summary>
      <div style="font-size:11.5px;color:var(--mu);line-height:1.55;margin-top:8px">
        <div>Сервер: <code id="agentServer">—</code> <button class="btn" style="padding:2px 7px;font-size:10px" onclick="copyAgent('agentServer')">Копіювати</button></div>
        <div style="margin-top:4px">Токен: <code id="agentToken">—</code> <button class="btn" style="padding:2px 7px;font-size:10px" onclick="copyAgent('agentToken')">Копіювати</button></div>
        <div style="margin-top:6px">На ПК: запусти <b>launchers\install_taobao_agent.bat</b> з папки Ledger, встав ці два значення, дочекайся Chromium. Потім один раз увійди в Taobao через QR.</div>
      </div>
    </details>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:12px">
      <input id="tbQ" placeholder="🔍 Пошук по назві..." oninput="renderTaobao()" style="width:220px">
      <label style="font-size:12px;color:var(--mu);display:flex;align-items:center;gap:5px">
        мін. ціна ¥<input id="tbMinCny" type="number" min="0" step="0.5" value="2"
             style="width:64px;font-size:12px" onchange="tbSaveMin()">
      </label>
      <select id="tbGame" onchange="tbGame=this.value;renderTaobao()" style="font-size:13px">
        <option value="" data-i18n="ta.allGames">Всі ігри</option>
      </select>
      <select id="tbSeg" onchange="tbSeg=this.value;renderTaobao()" style="font-size:13px">
        <option value="" data-i18n="ta.allTypes">Всі типи</option>
        <option value="starter" data-i18n="s.starter">Стартові</option>
        <option value="developed" data-i18n="s.developed">Розвинені</option>
        <option value="endgame" data-i18n="s.endgame">Ендгейм</option>
      </select>
      <select id="tbRegion" onchange="tbRegion=this.value;renderTaobao()" style="font-size:13px">
        <option value="" data-i18n="ta.allRegions">Всі регіони</option>
        <option value="Global">Global</option>
        <option value="Asia">Asia</option>
        <option value="EU">EU</option>
        <option value="NA">NA</option>
        <option value="JP">JP</option>
        <option value="TW">TW</option>
        <option value="KR">KR</option>
        <option value="CN">CN</option>
      </select>
      <select id="tbSort" onchange="tbSort=this.value;renderTaobao()" style="font-size:13px">
        <option value="price" data-i18n="s.cheapFirst">Дешевші спершу</option>
        <option value="exp" data-i18n="s.expFirst">Дорожчі спершу</option>
        <option value="variant" data-i18n="s.moreVariants">🎛 Більше варіантів</option>
        <option value="card" data-i18n="s.cardOnly">💳 Тільки з оплатою карткою</option>
      </select>
    </div>
    <div id="tbCartInfo" style="font-size:12px;margin-bottom:10px"></div>
    <div id="tbEnrichInfo" style="font-size:12px;color:var(--mu);margin-bottom:10px"></div>
    <div id="tbSummary" style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px"></div>
    <div id="tbList"><div class="none">⏳ Завантаження...</div></div>
    <div id="tbRuns" style="font-size:11px;color:var(--mu);margin-top:10px"></div>
  </div>
</div>

<!-- 📦 СКЛАД -->
<div id="tab-inventory" class="tc">
  <div class="panel">
    <div class="ph"><span data-i18n="ph.stock">СКЛАД — куплені акаунти</span>
      <button class="btn" style="font-size:12px;padding:5px 11px" onclick="loadInventory()">↻ Оновити</button></div>
    <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:12px">
      <label style="font-size:12px;color:var(--mu);display:flex;align-items:center;gap:6px;cursor:pointer">
        <input id="vaultEnabled" type="checkbox" onchange="saveVault()">
        <span data-i18n="vault.label">Шифрувати дані акаунтів</span>
      </label>
      <span style="font-size:11px;color:var(--mu)" data-i18n="vault.hint">Ключ у .gt_secrets.json; список показує лише маску, повний логін — по кнопці «Показати».</span>
    </div>
    <div style="font-size:13px;color:var(--mu);margin-bottom:14px" data-i18n="inv.intro">Bought accounts: what they cost, from whom, and whether they sold. Shows real margin and how much money is frozen.</div>
    <div id="invSummary" style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px"></div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end;margin-bottom:14px">
      <label style="font-size:12px;color:var(--mu)"><span data-i18n="inv.name">Назва</span><br><input id="invTitle" placeholder="Arknights starter" style="width:200px;margin-top:4px"></label>
      <label style="font-size:12px;color:var(--mu)"><span data-i18n="inv.game">Гра</span><br><input id="invGame" placeholder="Arknights" style="width:110px;margin-top:4px"></label>
      <label style="font-size:12px;color:var(--mu)"><span data-i18n="inv.cost">Собівартість, USD</span><br><input id="invCost" type="number" min="0" step="0.01" value="0" style="width:90px;margin-top:4px"></label>
      <label style="font-size:12px;color:var(--mu)"><span data-i18n="inv.source">Джерело</span><br><input id="invSource" placeholder="Taobao / store name" style="width:120px;margin-top:4px"></label>
      <label style="font-size:12px;color:var(--mu);flex:1;min-width:260px"><span data-i18n="inv.account">Дані акаунта (логін / пароль / пошта)</span><br>
        <textarea id="invAccount" data-i18n-ph="inv.ph" placeholder="логін: user@mail.com&#10;пароль: 12345&#10;пошта: user@mail.com" style="width:100%;height:64px;margin-top:4px;font-family:var(--font);font-size:12px"></textarea>
      </label>
      <button class="btn gr" style="font-size:12px;padding:6px 12px" onclick="invAdd()">＋ <span data-i18n="btn.add">Додати</span></button>
      <input id="lotMarkup" type="hidden" value="30">
      <button class="btn" style="font-size:11px;padding:6px 9px" onclick="lotsCsv('inventory')" title="CSV лотів зі складу (ціна = собівартість × 1.3)">⬇ <span data-i18n="inv.csvStock">CSV (stock, +30%)</span></button>
      <button class="btn" style="font-size:11px;padding:6px 9px" onclick="lotsCsv('suppliers')" title="CSV лотів із каталогу постачальників (ціна = закупівля × 1.3)">⬇ <span data-i18n="inv.csvSup">CSV (suppliers, +30%)</span></button>
      <select id="invFilter" onchange="renderInventory()" style="font-size:13px;margin-left:auto">
        <option value="" data-i18n="inv.all">Всі</option>
        <option value="in_stock" data-i18n="inv.inStock">На складі</option>
        <option value="sold" data-i18n="inv.sold">Продані</option>
        <option value="written_off" data-i18n="inv.off">Списані</option>
      </select>
    </div>
    <div id="invAging" style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px"></div>
    <div id="invOld" style="font-size:12px;margin-bottom:10px"></div>
    <div id="invList"><div class="none">⏳ Завантаження...</div></div>
  </div>
</div>

<div id="invModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.65);z-index:900;align-items:center;justify-content:center;padding:20px">
  <div style="background:var(--card);border:1px solid var(--brd);border-radius:14px;max-width:560px;width:100%;padding:18px">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
      <div style="font-size:15px;font-weight:800" id="invModalTitle" data-i18n="inv.account">Дані акаунта</div>
      <button class="btn" onclick="closeInvSecret()" style="padding:4px 10px">✕</button>
    </div>
    <pre id="invModalText" style="background:var(--bg2);border:1px solid var(--brd);border-radius:10px;padding:12px;font-size:13px;white-space:pre-wrap;word-break:break-word;max-height:320px;overflow:auto;margin:0"></pre>
    <div style="display:flex;gap:8px;margin-top:12px">
      <button class="btn gr" style="font-size:12px;padding:6px 12px" onclick="copyInvSecret()">📋 <span data-i18n="copy">Копіювати</span></button>
      <button class="btn" style="font-size:12px;padding:6px 12px" onclick="closeInvSecret()" data-i18n="close">Закрити</button>
    </div>
  </div>
</div>

<!-- 📊 СТАТИСТИКА ПО ІГРАХ -->
<div id="tab-stats" class="tc">
  <div class="panel" style="margin-bottom:14px">
    <div class="ph" style="margin-bottom:12px">📊 <span data-i18n="an.mergedTitle">ЗВЕДЕНО — ВСІ ЦИФРИ В ОДНОМУ МІСЦІ</span></div>

    <div style="font-size:11px;letter-spacing:1px;color:var(--mu);margin-bottom:6px">🛒 <span data-i18n="an.merged">P&amp;L + ELDORADO — разом</span></div>
    <div class="stats" id="plStats">
      <div class="sc cg"><div class="sl" data-i18n="pl.profit">ПРИБУТОК</div><div class="sv" id="plProfit">$0</div></div>
      <div class="sc c1"><div class="sl" data-i18n="pl.revenue">ВИРУЧКА</div><div class="sv" id="plRevenue">$0</div></div>
      <div class="sc c2"><div class="sl" data-i18n="pl.cost">ВКЛАДЕНО</div><div class="sv" id="plCost">$0</div></div>
      <div class="sc c3"><div class="sl" data-i18n="pl.margin">МАРЖА</div><div class="sv" id="plMargin">0%</div></div>
      <div class="sc c4"><div class="sl" data-i18n="pl.deals">УГОД</div><div class="sv" id="plCount">0</div></div>
      <div class="sc c5"><div class="sl" data-i18n="pl.fees">КОМІСІЇ</div><div class="sv" id="plFees">$0</div></div>
      <div class="sc c4"><div class="sl" data-i18n="pl.expenses">ВИТРАТИ</div><div class="sv" id="plExpenses">$0</div></div>
    </div>

    <div id="edSummary" style="display:none"></div>

    <div style="border-top:1px dashed var(--brd);margin:16px 0 12px"></div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
      <div style="font-size:12px;font-weight:700;color:var(--mu)">📊 <span data-i18n="an.revenueDays">ВИТОРГ ПО ДНЯХ (30 днів)</span></div>
      <button class="btn" onclick="renderRevenueChart()" style="font-size:10px;padding:3px 10px">↺ <span data-i18n="an.refresh">Оновити</span></button>
    </div>
    <div style="height:200px;position:relative">
      <canvas id="revenueChart"></canvas>
    </div>
  </div>
  <div class="panel" style="margin-bottom:14px">
    <div class="ph" style="margin-bottom:12px">📈 <span data-i18n="an.gamesTitle">АНАЛІТИКА</span></div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
      <a class="btn" href="/api/export/csv?what=pl" style="font-size:12px;padding:6px 11px;text-decoration:none">⬇ P&L у CSV</a>
      <a class="btn" href="/api/export/csv?what=ed" style="font-size:12px;padding:6px 11px;text-decoration:none">⬇ ELDORADO у CSV</a>
      <button class="btn" style="font-size:12px;padding:6px 11px" onclick="loadAnalytics()">↻ <span data-i18n="an.refresh">Оновити</span></button>
    </div>
    <div id="anSummary" style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px"></div>
    <div style="display:flex;gap:16px;flex-wrap:wrap">
      <div style="flex:1;min-width:300px"><div style="font-size:12px;color:var(--mu);margin-bottom:6px" data-i18n="an.byGames">ПО ІГРАХ</div><div id="anGames"></div></div>
      <div style="flex:1;min-width:260px"><div style="font-size:12px;color:var(--mu);margin-bottom:6px" data-i18n="an.byMonths">ПО МІСЯЦЯХ</div><div id="anMonths"></div></div>
    </div>
    <div style="margin-top:16px;padding-top:14px;border-top:1px solid var(--brd)">
      <div style="font-size:14px;font-weight:800;margin-bottom:4px">⚙️ <span data-i18n="sched.title">Розклад і ліміти</span></div>
      <div style="font-size:12px;color:var(--mu);line-height:1.55;margin-bottom:12px" data-i18n="sched.intro">Це автоматичні інтервали Ledger: як часто оновлювати ціни, шукати новинки та коли надсилати звіт. Менший інтервал = свіжіші дані, але більше запитів і кредитів.</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(225px,1fr));gap:10px">
        <label style="display:block;background:var(--card2);border:1px solid var(--brd);border-radius:9px;padding:10px 11px">
          <div style="font-size:12px;font-weight:700;margin-bottom:3px" data-i18n="sched.sup.label">Оновлення каталогу</div>
          <div style="font-size:10.5px;color:var(--mu);line-height:1.45;margin-bottom:6px" data-i18n="sched.sup.desc">Як часто перевіряти ціни та наявність у постачальників. 6 год = 4 рази на добу.</div>
          <div style="display:flex;align-items:center;gap:5px"><input id="stSupHours" type="number" min="1" max="48" step="1" style="width:80px"><span style="font-size:11px;color:var(--mu)" data-i18n="sched.hours">год</span></div>
        </label>
        <label style="display:block;background:var(--card2);border:1px solid var(--brd);border-radius:9px;padding:10px 11px">
          <div style="font-size:12px;font-weight:700;margin-bottom:3px" data-i18n="sched.news.label">Пошук новинок</div>
          <div style="font-size:10.5px;color:var(--mu);line-height:1.45;margin-bottom:6px" data-i18n="sched.news.desc">Як часто шукати нові товари та зміни на сайтах. 1 год = щогодини.</div>
          <div style="display:flex;align-items:center;gap:5px"><input id="stNewsHours" type="number" min="0.25" max="24" step="0.25" style="width:80px"><span style="font-size:11px;color:var(--mu)" data-i18n="sched.hours">год</span></div>
        </label>
        <label style="display:block;background:var(--card2);border:1px solid var(--brd);border-radius:9px;padding:10px 11px">
          <div style="font-size:12px;font-weight:700;margin-bottom:3px" data-i18n="sched.credits.label">Ліміт кредитів</div>
          <div style="font-size:10.5px;color:var(--mu);line-height:1.45;margin-bottom:6px" data-i18n="sched.credits.desc">Скільки кредитів ScraperAPI можна витратити за добу. Не користуєшся — не змінюй.</div>
          <div style="display:flex;align-items:center;gap:5px"><input id="stScraperLimit" type="number" min="1" max="5000" step="1" style="width:80px"><span style="font-size:11px;color:var(--mu)" data-i18n="sched.credits.unit">кр./день</span></div>
        </label>
        <label style="display:block;background:var(--card2);border:1px solid var(--brd);border-radius:9px;padding:10px 11px">
          <div style="font-size:12px;font-weight:700;margin-bottom:3px" data-i18n="sched.digest.label">Час дайджесту</div>
          <div style="font-size:10.5px;color:var(--mu);line-height:1.45;margin-bottom:6px" data-i18n="sched.digest.desc">Година, коли надсилати підсумок дня в Telegram (0–23).</div>
          <div style="display:flex;align-items:center;gap:5px"><input id="stDigestHour" type="number" min="0" max="23" step="1" style="width:80px"><span style="font-size:11px;color:var(--mu)" data-i18n="sched.hour">год</span></div>
        </label>
        <label style="display:block;background:var(--card2);border:1px solid var(--brd);border-radius:9px;padding:10px 11px">
          <div style="font-size:12px;font-weight:700;margin-bottom:3px" data-i18n="sched.deal.label">Поріг вигідного лоту</div>
          <div style="font-size:10.5px;color:var(--mu);line-height:1.45;margin-bottom:6px" data-i18n="sched.deal.desc">У скільки разів ціна має бути нижчою за твою, щоб прийшов алерт. 5× = ціна ≤ 20% твоєї.</div>
          <div style="display:flex;align-items:center;gap:5px"><input id="stDealX" type="number" min="1" max="100" step="0.5" style="width:80px"><span style="font-size:11px;color:var(--mu)">×</span></div>
        </label>
      </div>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:10px">
        <button class="btn" style="font-size:12px;padding:6px 12px" onclick="saveSchedule()">💾 <span data-i18n="sched.save">Зберегти розклад</span></button>
        <span style="font-size:10.5px;color:var(--mu)" data-i18n="sched.hint">Не впевнений? Залиш значення як є — це безпечні дефолти.</span>
      </div>
    </div>
    <div style="margin-top:16px;padding-top:14px;border-top:1px solid var(--brd)">
      <div style="font-size:14px;font-weight:800;margin-bottom:4px">🎯 <span data-i18n="target.title">ЦІЛЬОВІ ЦІНИ</span></div>
      <div style="font-size:12px;color:var(--mu);line-height:1.55;margin-bottom:8px" data-i18n="target.hint">Напиши назву гри/лота й максимальну ціну в доларах. Ledger перевіряє кеш постачальників і надсилає Telegram-алерт, коли ціна досягає порогу. Один рядок = одна ціль.</div>
      <textarea id="targetPrices" placeholder="Genshin | 15&#10;Honkai Star Rail | 12" style="width:100%;height:74px;font-family:var(--font);font-size:12px"></textarea>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:6px">
        <button class="btn gr" style="font-size:12px;padding:6px 12px" onclick="savePriceTargets()">💾 <span data-i18n="target.save">Зберегти цілі</span></button>
        <span style="font-size:10.5px;color:var(--mu)" data-i18n="target.needPrice">Потрібно увімкнути Telegram-сповіщення «Падіння цін».</span>
      </div>
    </div>
    <div style="margin-top:16px;padding-top:14px;border-top:1px solid var(--brd)">
      <div style="display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap;margin-bottom:10px">
        <div style="font-size:14px;font-weight:800">📄 <span data-i18n="rep.title">Місячний звіт</span></div>
        <input id="repMonth" type="month" style="font-size:13px">
        <label style="font-size:11px;color:var(--mu)"><span data-i18n="rep.tax">Податок %</span> <input id="repTaxRate" type="number" min="0" max="50" step="0.1" style="width:64px" onchange="saveTaxRate()"></label>
        <button class="btn" style="font-size:12px;padding:6px 11px" onclick="loadReport()" data-i18n="rep.show">Показати</button>
        <a class="btn" id="repCsv" style="font-size:12px;padding:6px 11px;text-decoration:none" href="#">⬇ CSV</a>
        <button class="btn" style="font-size:12px;padding:6px 11px" onclick="reportPdf()">🖨 PDF</button>
      </div>
      <div id="repBox"><div class="none" data-i18n="rep.choose">Виберіть місяць</div></div>
    </div>
    <div id="anDead" style="margin-top:14px"></div>
  </div>
  <div class="panel" style="margin-bottom:14px">
    <div class="ph">💵 <span data-i18n="cf.title">CASHFLOW / PAYOUTS</span></div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px" id="cfCards"></div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end;margin-bottom:10px">
      <select id="cfPlatform" style="font-size:12px">
        <option value="g2g">G2G</option><option value="gameflip">Gameflip</option>
        <option value="pa">PlayerAuctions</option><option value="zeusx">ZeusX</option>
        <option value="funpay">FunPay</option><option value="eldorado">Eldorado</option><option value="other" data-i18n="f.other">Інше</option>
      </select>
      <input id="cfAmount" type="number" min="0.01" step="0.01" placeholder="Сума $" data-i18n-ph="cf.amount" style="width:120px">
      <select id="cfStatus" style="font-size:12px"><option value="hold" data-i18n="cf.hold">Hold</option><option value="available" data-i18n="cf.available">Available</option><option value="withdrawn" data-i18n="cf.withdrawn">Withdrawn</option></select>
      <input id="cfDate" type="date" style="width:140px">
      <input id="cfAvailable" type="date" title="Доступно з (Hold → Available)" style="width:140px">
      <input id="cfNote" placeholder="Коментар" data-i18n-ph="cf.note" style="width:150px">
      <button class="btn gr" onclick="cashflowAdd()">＋ <span data-i18n="cf.add">Додати</span></button>
      <label class="btn" style="font-size:11px;cursor:pointer">⬆ <span data-i18n="cf.payoutCsv">Payout CSV</span><input id="cfImport" type="file" accept=".csv,text/csv" onchange="importCashflowCsv(this)" style="display:none"></label>
    </div>
    <details style="margin-bottom:10px;font-size:11px;color:var(--mu)">
      <summary style="cursor:pointer;font-weight:700">⚙ <span data-i18n="cf.rules">Правила payout (днів до Available)</span></summary>
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end;margin-top:7px" id="pdRules">
        <label>G2G <input id="pd_g2g" type="number" min="0" max="90" style="width:56px"></label>
        <label>Gameflip <input id="pd_gameflip" type="number" min="0" max="90" style="width:56px"></label>
        <label>PA <input id="pd_pa" type="number" min="0" max="90" style="width:56px"></label>
        <label>ZeusX <input id="pd_zeusx" type="number" min="0" max="90" style="width:56px"></label>
        <label>FunPay <input id="pd_funpay" type="number" min="0" max="90" style="width:56px"></label>
        <label>Eldorado <input id="pd_eldorado" type="number" min="0" max="90" style="width:56px"></label>
        <label><span data-i18n="f.other">Інше</span> <input id="pd_other" type="number" min="0" max="90" style="width:56px"></label>
        <button class="btn" style="font-size:11px;padding:4px 9px" onclick="savePayoutRules()" data-i18n="cf.save">Зберегти</button>
        <span data-i18n="cf.priority">Дата в полі «Доступно з» має пріоритет.</span>
      </div>
    </details>
    <div id="cfList"><div class="none">⏳ …</div></div>
  </div>
  <div class="panel" style="margin-bottom:14px">
    <div class="ph">📥 <span data-i18n="imp.title">ІМПОРТ ПРОДАЖІВ</span></div>
    <div style="font-size:11.5px;color:var(--mu);margin:-4px 0 9px" data-i18n="imp.hint">CSV з G2G / Gameflip / PlayerAuctions. Колонки: date, title/item, price/amount, fee (необов’язково), order id (необов’язково). Собівартість підтягується зі складу, якщо є збіг.</div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
      <select id="impPlatform" style="font-size:12px"><option value="g2g">G2G</option><option value="gameflip">Gameflip</option><option value="pa">PlayerAuctions</option></select>
      <input id="impFile" type="file" accept=".csv,text/csv" onchange="importCsvFile(this)" style="font-size:11px">
      <label style="font-size:11px;color:var(--mu);display:flex;align-items:center;gap:4px"><input id="impCashflow" type="checkbox" checked> <span data-i18n="imp.createHold">створити Hold</span></label>
      <button class="btn gr" id="impRun" style="display:none" onclick="runSalesImport()" data-i18n="imp.import">Імпортувати</button>
      <span id="impInfo" style="font-size:11px;color:var(--mu)"></span>
    </div>
    <div id="impPreview" style="margin-top:9px"></div>
  </div>

  <div class="panel" style="margin-bottom:14px">
    <div class="ph">🏭 <span data-i18n="roi.title">SUPPLIER ROI</span></div>
    <div style="font-size:11.5px;color:var(--mu);margin:-4px 0 9px" data-i18n="roi.hint">Прибуток, ROI і sell-through по постачальниках — на основі складу та прив’язаних продажів.</div>
    <div id="supRoi"><div class="none">⏳ …</div></div>
  </div>
  <div class="panel">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px">
      <div class="ph" style="margin:0">📊 СТАТИСТИКА ПО ІГРАХ</div>
      <div style="display:flex;gap:8px;align-items:center">
        <select id="statsPlatform" onchange="renderStats()" style="font-size:11px;padding:4px 8px;background:var(--bg2);border:1px solid var(--brd);border-radius:4px;color:var(--tx)">
          <option value="" data-i18n="allPlat">Всі платформи</option>
          <option value="zeusx">⚡ ZeusX</option>
          <option value="funpay">🔵 FunPay</option>
          <option value="eldorado">Eldorado</option>
        </select>
        <select id="statsPeriod" onchange="renderStats()" style="font-size:11px;padding:4px 8px;background:var(--bg2);border:1px solid var(--brd);border-radius:4px;color:var(--tx)">
          <option value="" data-i18n="per.all">Весь час</option>
          <option value="month" data-i18n="per.month">Цей місяць</option>
          <optgroup label="Місяці" id="statsMonthGroup"></optgroup>
        </select>
      </div>
    </div>
    <!-- Загальна статистика -->
    <div id="statsCards" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-bottom:18px"></div>
    <div id="platformStats" style="margin-bottom:18px"></div>
    <div id="statsCompare" style="margin-bottom:18px"></div>
    <!-- Графік по іграх -->
    <div style="margin-bottom:18px">
      <div style="font-size:11px;color:var(--mu);letter-spacing:1px;margin-bottom:8px">ТОП ІГРИ ПО ПРИБУТКУ</div>
      <div style="height:280px;position:relative"><canvas id="statsChart"></canvas></div>
    </div>
    <!-- Таблиця по іграх -->
    <div style="font-size:11px;color:var(--mu);letter-spacing:1px;margin-bottom:8px" data-i18n="an.detail">ДЕТАЛЬНА ТАБЛИЦЯ</div>
    <div id="statsTable"></div>
  </div>
</div>

<!-- ⚙️ НАЛАШТУВАННЯ -->
<div id="tab-plus" class="tc" data-no-currency>
  <div class="panel">
    <div class="ph"><span>LEDGER+</span><span id="plusStatus" style="font-size:12px;color:var(--mu)"></span></div>
    <div id="plusBody"><div class="none">⏳</div></div>
  </div>
</div>

<div id="tab-setup" class="tc">

  <div class="panel" id="pwaPanel" style="margin-bottom:14px">
    <div class="ph"><span data-i18n="app.title">ЗАСТОСУНОК</span></div>
    <div style="font-size:12.5px;color:var(--mu);line-height:1.6;margin-bottom:9px" data-i18n="app.desc">Встанови Ledger як застосунок на телефон або комп’ютер: іконка на робочому столі, повноекранний режим, швидший запуск.</div>
    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
      <button class="btn gr" id="pwaInstallBtn" onclick="pwaInstall()">⬇ <span data-i18n="app.install">Встановити Ledger</span></button>
      <span id="pwaStatus" style="font-size:11.5px;color:var(--mu)"></span>
    </div>
    <div style="font-size:11px;color:var(--mu);margin-top:7px" data-i18n="app.hint">Android/Chrome: кнопка вище або меню ⋮ → «Встановити застосунок». iPhone/Safari: «Поділитися» → «На екран Домівки».</div>
  </div>

  <div class="panel" id="mobilePanel" style="margin-bottom:14px">
    <div class="ph"><span>📱 <span data-i18n="mobile.title">Мобільний доступ</span></span><button class="btn" onclick="refreshMobile()" style="font-size:12px;padding:6px 10px">↻ <span data-i18n="mobile.refresh">Оновити</span></button></div>
    <div id="mobileBody" style="font-size:12.5px;color:var(--mu)">…</div>
    <div id="mobileUpdated" style="font-size:11px;color:var(--gr);margin-top:4px"></div>
  </div>

  <div class="panel" id="desktopPanel" style="display:none;margin-bottom:14px">
    <div class="ph"><span>🖥 <span data-i18n="desk.title">Вікно застосунку</span></span></div>
    <label style="display:flex;align-items:center;gap:8px;font-size:13px;cursor:pointer">
      <input type="checkbox" id="closeToTray">
      <span data-i18n="desk.tray">Закривати у трей, а не виходити</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px;font-size:13px;cursor:pointer;margin-top:8px">
      <input type="checkbox" id="compactMode" onchange="setCompact(this.checked)">
      <span data-i18n="desk.compact">Компактний режим (більше рядків на екрані)</span>
    </label>
    <div style="font-size:11.5px;color:var(--mu);margin-top:6px" data-i18n="desk.hint">Хрестик ховає вікно в трей; вийти повністю можна через меню трея.</div>
    <div style="margin-top:9px"><button class="btn gr" onclick="saveDesktopPrefs()">✓ <span data-i18n="desk.save">Зберегти</span></button></div>
  </div>

  <div id="pwaHelpModal" onclick="if(event.target===this)closePwaHelp()" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.72);z-index:10000;align-items:center;justify-content:center;padding:16px">
    <div style="background:var(--card);border:1px solid var(--brd);border-radius:14px;padding:18px;width:min(560px,96vw);max-height:88vh;overflow-y:auto">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:8px">
        <div style="font-size:15px;font-weight:800" id="pwaHelpTitle">⬇</div>
        <button type="button" class="btn" onclick="closePwaHelp();return false" style="padding:4px 10px">✕</button>
      </div>
      <div id="pwaHelpBody" style="font-size:12.5px;line-height:1.6;color:var(--mu)"></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:14px">
        <button class="btn gr" onclick="pwaDownloadShortcut()" id="pwaShortcutBtn">⬇</button>
        <button class="btn" onclick="pwaCopyLink()" id="pwaCopyBtn">📋</button>
        <button type="button" class="btn" onclick="closePwaHelp();return false" id="pwaCloseBtn">OK</button>
      </div>
    </div>
  </div>

  <div class="panel" id="pwPanel" style="margin-bottom:14px">
    <div class="ph"><span data-i18n="pw.optional">PASSWORD (OPTIONAL)</span></div>
    <div style="font-size:12.5px;color:var(--mu);margin-bottom:10px" id="pwStatus">—</div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
      <label style="font-size:12px;color:var(--mu)"><span data-i18n="pw.new8">New password (min 8)</span>
        <br><input id="pwEnableNew" type="password" placeholder="••••••••" style="width:220px;margin-top:4px" autocomplete="new-password"></label>
      <button class="btn gr" id="pwEnableBtn" onclick="pwEnable()" data-i18n="pw.enable">Enable password</button>
      <button class="btn" id="pwDisableBtn" onclick="pwDisable()" data-i18n="pw.disable">Disable password</button>
    </div>
    <div style="font-size:11.5px;color:var(--mu);margin-top:8px" data-i18n="pw.hint">Without a password anyone who opens the link gets in. Set one if the app is reachable from the internet.</div>
  </div>

  <div class="panel" id="auditPanel" style="margin-bottom:14px">
    <div class="ph" style="display:flex;justify-content:space-between;align-items:center">
      <span data-i18n="audit.title">ЖУРНАЛ ДІЙ</span>
      <button class="btn" style="font-size:11px;padding:4px 10px" onclick="loadAudit()">↻</button>
    </div>
    <div style="font-size:11px;color:var(--mu);margin-bottom:8px" data-i18n="audit.hint">Останні зміни угод, комісій, складу й налаштувань. Секрети й паролі не пишуться.</div>
    <div id="auditList" style="max-height:280px;overflow:auto"><div class="none">Завантаження…</div></div>
  </div>

  <div class="panel" id="twofaPanel" style="margin-bottom:14px">
    <div class="ph"><span data-i18n="twofa.title">ДВОФАКТОРНИЙ ВХІД (2FA)</span></div>
    <div style="font-size:12.5px;color:var(--mu);margin-bottom:10px" id="twofaStatus">—</div>
    <div id="twofaSetup" style="display:none">
      <div style="font-size:11.5px;color:var(--mu);margin-bottom:8px" data-i18n="twofa.hint">Додай секрет в Authenticator (Google Authenticator, Aegis, 1Password), потім введи 6-значний код.</div>
      <div style="font-size:11px;color:var(--mu)">SECRET</div>
      <code id="twofaSecret" style="display:block;background:var(--bg2);border:1px solid var(--brd);border-radius:8px;padding:8px 10px;font-size:13px;word-break:break-all;margin-bottom:6px"></code>
      <div style="font-size:10px;color:var(--mu);word-break:break-all;margin-bottom:10px" id="twofaUri"></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
        <div><div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px" data-i18n="twofa.code">КОД 6 ЦИФР</div>
          <input id="twofaCode" inputmode="numeric" maxlength="6" autocomplete="one-time-code" style="width:120px;letter-spacing:.2em"></div>
        <button class="btn gr" onclick="enable2FA()">✓ <span data-i18n="twofa.enable">Увімкнути 2FA</span></button>
      </div>
    </div>
    <div id="twofaEnabled" style="display:none">
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
        <div><div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px" data-i18n="twofa.code">КОД 6 ЦИФР</div>
          <input id="twofaDisableCode" inputmode="numeric" maxlength="6" autocomplete="one-time-code" style="width:120px;letter-spacing:.2em"></div>
        <button class="btn rd" onclick="disable2FA()">✕ <span data-i18n="twofa.disable">Вимкнути 2FA</span></button>
        <button class="btn" onclick="regenRecovery()">🔑 <span data-i18n="twofa.recovery">Recovery-коди</span></button>
        <button class="btn rd" onclick="logoutAll()" data-i18n="twofa.logoutAll">Вийти на всіх пристроях</button>
      </div>
      <div id="twofaRecovery" style="display:none;margin-top:10px;padding:10px;border:1px solid var(--yw);border-radius:8px;background:color-mix(in srgb,var(--yw) 8%,transparent)">
        <div style="font-size:11px;color:var(--yw);margin-bottom:6px" data-i18n="twofa.keepCodes">Збережи ці коди. Кожен працює один раз.</div>
        <pre id="twofaRecoveryList" style="margin:0;white-space:pre-wrap;font-size:13px;line-height:1.6"></pre>
        <button class="btn" style="margin-top:8px;font-size:11px;padding:5px 10px" onclick="copyRecovery()">📋 <span data-i18n="twofa.copy">Копіювати</span></button>
      </div>
    </div>
    <div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap">
      <button class="btn" onclick="setup2FA()">🔐 <span data-i18n="twofa.setup">Згенерувати новий секрет</span></button>
      <button class="btn" onclick="load2FA()">↻ <span data-i18n="twofa.refresh">Оновити</span></button>
    </div>
    <div style="font-size:11px;color:var(--mu);margin-top:8px" data-i18n="twofa.note">2FA працює разом із паролем входу. Пристрій, який уже увійшов, залишається в системі до виходу.</div>
  </div>

  <div class="panel" id="updatePanel" style="margin-bottom:14px">
    <div class="ph" style="display:flex;justify-content:space-between;align-items:center">
      <span data-i18n="upd.title">ОНОВЛЕННЯ</span>
      <button class="btn" style="font-size:11px;padding:4px 10px" onclick="checkUpdates()">↻ <span data-i18n="upd.check">Перевірити</span></button>
    </div>
    <div id="updateInfo" style="font-size:12px;color:var(--mu)" data-i18n="upd.hint">Натисни «Перевірити», щоб дізнатися останню версію.</div>
  </div>

  <div class="panel" id="dataPanel" style="margin-bottom:14px">
    <div class="ph"><span data-i18n="diag.title">ДАНІ Й ДІАГНОСТИКА</span>
      <button class="btn" style="font-size:12px" onclick="diagLoad();tokensCheck()" data-i18n="tk.check">Перевірити токени</button></div>
    <div id="diagBox" style="font-size:12.5px;color:var(--mu);margin-bottom:12px" data-i18n="diag.press">натисніть ↻ Оновити</div>
    <div id="tokenStates" style="font-size:12.5px;color:var(--mu);margin-bottom:12px"></div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px">
      <button class="btn" onclick="demoLoad()">Завантажити демо-дані</button>
      <button class="btn" onclick="demoClear()">Стерти дані</button>
      <a class="btn" href="/api/backup/export">Експорт усіх даних</a>
      <label class="btn" style="cursor:pointer">Імпорт CSV
        <input type="file" id="csvFile" accept=".csv,text/csv" onchange="csvImport(this)" style="display:none">
      </label>
    </div>
    <div style="border-top:1px solid var(--brd);padding-top:12px">
      <div style="font-size:12.5px;color:var(--mu);margin-bottom:6px">Мій постачальник (Shopify)</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
        <input id="supNewName" placeholder="Назва магазину" style="width:190px">
        <input id="supNewBase" placeholder="https://shop.example.com" style="width:260px">
        <button class="btn gr" onclick="supAdd()">Додати</button>
      </div>
      <div style="font-size:11.5px;color:var(--mu);margin-top:6px">Працює для Shopify-магазинів (/products.json).</div>
    </div>
  </div>

  <div class="panel" id="contactPanel" style="margin-bottom:14px">
    <div class="ph"><span data-i18n="ph.contact">ПОТРІБНА АВТОМАТИЗАЦІЯ?</span></div>
    <div style="display:flex;gap:18px;align-items:center;flex-wrap:wrap">
      <img src="data:image/png;base64,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" alt="Telegram QR" width="132" height="132"
           style="border-radius:12px;border:1px solid var(--brd);background:#fff;padding:6px;flex:none">
      <div style="flex:1;min-width:240px;font-size:13px;line-height:1.55">
        <div style="font-weight:700;font-size:15px;margin-bottom:6px">Ledger OS community</div>
        <div style="color:var(--mu);margin-bottom:10px" data-i18n="ph.contact.desc">Автоматизація, гайди та оновлення — приєднуйся до Telegram або Discord.</div>
        <div style="font-size:12.5px;margin-bottom:8px">
          <span style="color:var(--mu)">Email</span>
          <a href="mailto:ledgeros.gg@gmail.com" style="color:var(--tx);text-decoration:none">ledgeros.gg@gmail.com</a>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <a class="social tg" href="https://t.me/ledger_os" target="_blank" rel="noopener"><svg viewBox="0 0 24 24"><use href="#ic-tg"/></svg><span>Telegram</span></a>
          <a class="social dc" href="https://discord.gg/eMBXnKA3Pa" target="_blank" rel="noopener"><svg viewBox="0 0 24 24"><use href="#ic-dc"/></svg><span>Discord</span></a>
          <a class="btn" id="demoBtn" href="/demo" target="_blank" rel="noopener" data-i18n="cta.screens">Скріншоти функцій →</a>
        </div>
      </div>
      </div>
    </div>

  <!-- 🎨 ТЕМА -->
  <div class="panel" style="margin-bottom:14px">
    <div class="ph"><span data-i18n="ph.theme">ТЕМА ІНТЕРФЕЙСУ</span></div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:10px" id="themePicker">
      <div class="theme-btn" onclick="pickTheme('ledger')" data-theme="ledger" title="Ledger — лаконічна, без градієнтів">
        <div style="width:30px;height:30px;border-radius:50%;background:#0B0C0E;border:1px solid #2A2D33;position:relative">
          <img src="/brand-icon.png" alt="" style="position:absolute;inset:3px;width:24px;height:24px;border-radius:6px"></div>
        <span>Ledger</span>
      </div>
      <div class="theme-btn" onclick="pickTheme('slate')" data-theme="slate" title="Slate — попередня тема">
        <div style="width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#0d1017,#7c8cff)"></div>
        <span>Slate</span>
      </div>
      <div class="theme-btn" onclick="pickTheme('nord')" data-theme="nord" title="Nord — холодний синьо-сірий">
        <div style="width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#0b1220,#5aa9e6)"></div>
        <span>Nord</span>
      </div>
      <div class="theme-btn" onclick="pickTheme('carbon')" data-theme="carbon" title="Carbon — теплий графіт">
        <div style="width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#12100e,#e8a33d)"></div>
        <span>Carbon</span>
      </div>
      <div class="theme-btn" onclick="pickTheme('light')" data-theme="light" title="Світла тема (день)">
        <div style="width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#f5f6fa,#7c8cff)"></div>
        <span>Світла</span>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;border-top:1px solid var(--brd);padding-top:12px">
      <span style="font-size:12px;color:var(--mu)" data-i18n="fs.title">Розмір шрифту</span>
      <button class="btn" onclick="setFs(-0.05)" title="A−" style="padding:5px 12px">A−</button>
      <span id="fsVal" style="font-size:12px;color:var(--mu);min-width:42px;text-align:center">100%</span>
      <button class="btn" onclick="setFs(0.05)" title="A+" style="padding:5px 12px">A+</button>
      <button class="btn" onclick="resetFs()" style="padding:5px 12px;font-size:11px" data-i18n="fs.reset">100%</button>
    </div>
  </div>
  <div class="panel" style="margin-bottom:14px">
    <div class="ph"><span data-i18n="bk.panelTitle">БЕКАП P&L</span>
      <button class="btn" style="font-size:10px;padding:3px 10px" onclick="runBackup()">↺ <span data-i18n="bk.runNow">Зробити зараз</span></button>
    </div>
    <div style="font-size:11px;color:var(--mu);margin-bottom:10px" data-i18n="bk.hint">Авто-бекап раз на день у папку gt_backups/ поруч з трекером. Зберігаються останні 30 файлів (P&L, ELDORADO, ціль).</div>
    <div id="backupList" style="font-size:11px;color:var(--mu)" data-i18n="bk.loading">⏳ Завантаження...</div>
    <div style="border-top:1px solid var(--brd);margin:12px 0"></div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
      <a class="btn gr" href="/api/backup/export" download style="text-decoration:none">⬇ <span data-i18n="bk.exportZip">Експорт усіх даних (zip)</span></a>
      <button class="btn" onclick="exportEncrypted()">🔒 <span data-i18n="bk.exportEnc">Експорт зашифрований</span></button>
      <label class="btn" style="cursor:pointer">⬆ <span data-i18n="bk.import">Імпорт zip / .enc</span>
        <input type="file" id="importZip" accept=".zip,.enc" style="display:none" onchange="importBackup(this)">
      </label>
      <span style="font-size:10px;color:var(--mu)" data-i18n="bk.note">P&L + ELDORADO + ціль + налаштування · без паролів і токенів · sha256-перевірка</span>
    </div>
  </div>
  <div class="panel" style="margin-bottom:14px">
    <div class="ph"><span id="rateTitle">CURRENCY · USD → UAH</span></div>
    <div style="font-size:11px;color:var(--mu);margin:-4px 0 4px" data-i18n="cur.auto">Курс оновлюється автоматично раз на 6 годин. Кнопка ↻ — примусове оновлення.</div>
    <div style="font-size:11px;color:var(--mu);margin:0 0 10px" data-i18n="cur.manualHint">Можна вибрати будь-яку валюту вручну. Після цього зміна мови не змінюватиме валюту.</div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end">
      <div>
        <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px" data-i18n="cur.title">CURRENCY</div>
        <select id="curSel" onchange="pickCurrency()" style="font-size:13px">
          <option value="UAH">UAH ₴</option>
          <option value="EUR">EUR €</option>
          <option value="USD">USD $</option>
          <option value="PLN">PLN zł</option>
          <option value="CZK">CZK Kč</option>
          <option value="TRY">TRY ₺</option>
          <option value="GBP">GBP £</option>
          <option value="KZT">KZT ₸</option>
          <option value="GEL">GEL ₾</option>
          <option value="RUB">RUB ₽</option>
        </select>
      </div>
      <div>
        <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px" id="rateLbl" data-no-currency data-i18n="cur.rate">RATE (₴ per $1)</div>
        <input id="rateVal" type="number" step="0.01" min="0" placeholder="41.50" style="width:120px;font-family:var(--font)">
      </div>
      <div style="font-size:11px;color:var(--mu);padding-bottom:9px" id="rateInfo">—</div>
      <button class="btn" onclick="refreshRate()">↻ <span data-i18n="cur.refresh">Refresh rate</span></button>
      <button class="btn gr" onclick="saveRate()">✓ <span data-i18n="cur.save">Save</span></button>
    </div>
  </div>
  <div class="panel" style="margin-bottom:14px">
    <div class="ph"><span data-i18n="feeProf.title">КОМІСІЇ ЗА ЗАМОВЧУВАННЯМ</span></div>
    <div style="font-size:11px;color:var(--mu);margin-bottom:10px" data-i18n="feeProf.hint">Дефолти для нових угод. Старі угоди зберігають свою комісію. ZeusX керується рангом у формі угоди.</div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end">
      <div><div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px">FunPay %</div><input id="feeFunpay" type="number" step="0.1" min="0" max="100" style="width:90px"></div>
      <div><div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px">Eldorado %</div><input id="feeEldorado" type="number" step="0.1" min="0" max="100" style="width:90px"></div>
      <div><div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px" data-i18n="f.other">Інше</div><input id="feeOther" type="number" step="0.1" min="0" max="100" style="width:90px"></div>
      <button class="btn gr" onclick="saveFeeProfiles()">✓ <span data-i18n="save">Зберегти</span></button>
    </div>
    <div style="margin-top:10px">
      <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px" data-i18n="feeProf.games">ОКРЕМІ ІГРИ (назва | платформа | %)</div>
      <textarea id="feeGames" placeholder="GTA 5 | eldorado | 30&#10;Fortnite | eldorado | 20" style="width:100%;height:58px;font-family:var(--font);font-size:12px"></textarea>
      <div style="font-size:10px;color:var(--mu);margin-top:4px" data-i18n="feeProf.gamesHint">Один рядок на гру. Платформа: funpay / eldorado / other. Порожньо — без overrides.</div>
    </div>
  </div>
  <div class="panel" style="margin-bottom:14px">
    <div class="ph"><span data-i18n="ph.tg">TELEGRAM-СПОВІЩЕННЯ</span></div>
    <div style="font-size:11px;color:var(--mu);margin-bottom:10px" data-i18n="tg.hint">Бот пише лише про те, що прийшло з пошти (нові замовлення й повідомлення FunPay / ZeusX / Eldorado) та про досягнення цілі. Ручне внесення продажу в таблицю не сповіщає. Створи бота у @BotFather, встав токен і свій chat_id (дізнатись у @userinfobot).</div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
      <div>
        <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px" data-i18n="set.botToken">ТОКЕН БОТА</div>
        <input id="tgToken" type="password" placeholder="123456789:AA..." autocomplete="off" style="width:250px">
      </div>
      <div>
        <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px">CHAT ID</div>
        <input id="tgChat" placeholder="123456789" style="width:150px">
      </div>
      <button class="btn gr" onclick="saveTg()">✓ <span data-i18n="save">Зберегти</span></button>
      <button class="btn" onclick="testTg()">📨 <span data-i18n="set.test">Тест</span></button>
      <button class="btn rd" onclick="tgDisconnect()" data-i18n="set.telegramDisconnect">Disconnect Telegram</button>
    </div>
    <div style="display:flex;gap:16px;flex-wrap:wrap;margin-top:10px;font-size:12px;align-items:center">
      <label style="cursor:pointer"><input type="checkbox" id="tgEnabled"> Увімкнено</label>
    </div>
    <div style="font-size:12px;color:var(--mu);margin-top:12px" data-i18n="set.whatToSend">Що надсилати в Telegram (кожен тип окремо):</div>
    <div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:6px;font-size:12px;align-items:center">
      <label style="cursor:pointer"><input type="checkbox" id="ntOrder"> <span data-i18n="nt.order">💰 Продажі (замовлення)</span></label>
      <label style="cursor:pointer"><input type="checkbox" id="ntMessage"> <span data-i18n="nt.message">💬 Повідомлення покупців</span></label>
      <label style="cursor:pointer"><input type="checkbox" id="ntWatchdog"> <span data-i18n="nt.watchdog">⚠️ Watchdog сайту</span></label>
      <label style="cursor:pointer"><input type="checkbox" id="ntAgent"> <span data-i18n="nt.agent">⚠️ Watchdog агента Taobao</span></label>
      <label style="cursor:pointer"><input type="checkbox" id="ntDigest"> <span data-i18n="nt.digest">📊 Дайджест (20:00)</span></label>
      <label style="cursor:pointer"><input type="checkbox" id="ntNew"> <span data-i18n="nt.new">🆕 Нові акаунти</span></label>
      <label style="cursor:pointer"><input type="checkbox" id="ntPrice"> <span data-i18n="nt.price">💸 Падіння цін</span></label>
      <label style="cursor:pointer"><input type="checkbox" id="ntRestock"> <span data-i18n="nt.restock">🔄 Ресток</span></label>
      <label style="cursor:pointer"><input type="checkbox" id="ntDeal"> <span data-i18n="nt.deal">🔥 Вигідні лоти Taobao</span></label>
      <label style="cursor:pointer"><input type="checkbox" id="ntDeadstock"> <span data-i18n="nt.deadstock">🧊 Мертвий склад (30+ днів)</span></label>
    </div>
    <button class="btn gr" style="margin-top:8px;font-size:12px;padding:6px 12px" onclick="saveNotify()">💾 <span data-i18n="set.notifySave">Зберегти сповіщення</span></button>
    <div style="display:none">
    </div>
    <div style="font-size:12px;color:var(--mu);margin-top:10px;line-height:1.6" data-i18n="tg.cmds">Бот відповідає на команди (тільки ваш чат): /stats — продажі сьогодні й за місяць · /balance — баланс ZeusX / FunPay / Eldorado · /new — останні замовлення · /taobao — топ вигідних лотів · /help</div>
  </div>
  <div class="panel" style="margin-bottom:14px">
    <div class="ph">GMAIL → TELEGRAM
      <span id="gmailBadge" style="font-size:10px;color:var(--mu)"></span>
    </div>
    <div style="font-size:11px;color:var(--mu);margin-bottom:10px" data-i18n="gm.hint">Трекер читає пошту (IMAP) і надсилає в Telegram нові замовлення та повідомлення FunPay / ZeusX / Eldorado. Потрібен App Password (не звичайний пароль): Google Account → Security → 2-Step Verification → App passwords + увімкнений IMAP у Gmail.</div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
      <div>
        <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px" data-i18n="set.gmailLabel">GMAIL</div>
        <input id="gmailUser" placeholder="you@gmail.com" autocomplete="off" style="width:230px">
      </div>
      <div>
        <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px" data-i18n="set.appPass">APP PASSWORD</div>
        <input id="gmailPass" type="password" placeholder="xxxx xxxx xxxx xxxx" autocomplete="off" style="width:200px">
      </div>
      <button class="btn gr" onclick="saveGmail()">✓ <span data-i18n="save">Зберегти</span></button>
      <button class="btn" onclick="checkGmailNow()">📥 <span data-i18n="set.checkNow">Перевірити зараз</span></button>
      <button class="btn rd" onclick="gmailDisconnect()" data-i18n="set.gmailDisconnect">Disconnect Gmail</button>
    </div>
    <div id="gmailInfo" style="font-size:11px;color:var(--mu);margin-top:8px">—</div>
  </div>
  <div class="panel" style="margin-bottom:14px">
    <div class="ph"><span data-i18n="ph.cloud">ХМАРНИЙ БЕКАП</span></div>
    <div style="font-size:11px;color:var(--mu);margin-bottom:10px" data-i18n="set.cloudHint">Копія бекапів у OneDrive (або будь-яка папка). Порожнє поле = авто: OneDrive/GameTrackerBackups.</div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
      <div style="flex:1;min-width:240px">
        <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px" data-i18n="set.folder">ПАПКА</div>
        <input id="cloudDir" placeholder="C:/Users/User/OneDrive/GameTrackerBackups" style="width:100%">
      </div>
      <button class="btn gr" onclick="saveCloud()">✓ <span data-i18n="cloud.save">Зберегти</span></button>
    </div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end;margin-top:10px">
      <label style="font-size:11px;color:var(--mu)"><span data-i18n="cloud.every">Кожні</span> <input id="backupHours" type="number" min="1" max="168" style="width:64px"> <span data-i18n="cloud.hours">год</span></label>
      <label style="font-size:11px;color:var(--mu)"><span data-i18n="cloud.keep">Тримати</span> <input id="backupKeep" type="number" min="1" max="365" style="width:64px"> <span data-i18n="cloud.copies">копій</span></label>
      <button class="btn" style="font-size:11px;padding:5px 10px" onclick="saveBackupSettings()">✓ <span data-i18n="cloud.save">Зберегти</span></button>
      <button class="btn gr" style="font-size:11px;padding:5px 10px" onclick="backupNow()">💾 <span data-i18n="cloud.now">Бекап зараз</span></button>
      <button class="btn" style="font-size:11px;padding:5px 10px" onclick="backupVerify()">🔍 <span data-i18n="cloud.verify">Перевірити</span></button>
      <button class="btn" style="font-size:11px;padding:5px 10px" onclick="backupRestoreTest()">🧪 <span data-i18n="cloud.restoreTest">Тест відновлення</span></button>
    </div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:9px">
      <label style="font-size:11px;display:flex;align-items:center;gap:5px"><input id="backupEncrypt" type="checkbox"> 🔒 <span data-i18n="cloud.encrypt">Шифрувати автоматичні бекапи</span></label>
      <input id="backupPass" type="password" placeholder="Пароль шифрування" data-i18n-ph="cloud.password" autocomplete="new-password" style="width:190px;font-size:11px">
      <button class="btn" style="font-size:11px;padding:4px 9px" onclick="saveBackupEncryption()" data-i18n="cloud.save">Зберегти</button>
      <span style="font-size:10px;color:var(--mu)" data-i18n="cloud.passwordHint">Пароль зберігається в secrets; без нього бекап не відкрити.</span>
    </div>
    <div id="backupInfo" style="font-size:11px;color:var(--mu);margin-top:7px">—</div>
    <div id="cloudInfo" style="font-size:11px;color:var(--mu);margin-top:8px">—</div>
  </div>
  <div class="panel" style="margin-bottom:14px">
    <div class="ph"><span data-i18n="ph.sec">БЕЗПЕКА</span></div>
    <div id="authModeInfo" style="font-size:13px;margin-bottom:10px;display:none"></div>
    <div style="font-size:11px;color:var(--mu);margin-bottom:10px">Зміна пароля діє одразу (браузер попросить його після перезавантаження). HTTPS — для прямого доступу; на хостингу зазвичай уже є проксі з HTTPS.</div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
      <div>
        <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px">ПОТОЧНИЙ ПАРОЛЬ</div>
        <input id="pwOld" type="password" autocomplete="current-password" style="width:180px">
      </div>
      <div>
        <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px">НОВИЙ ПАРОЛЬ</div>
        <input id="pwNew" type="password" autocomplete="new-password" data-i18n-ph="ph.pw6" placeholder="мін. 6 символів" style="width:180px">
      </div>
      <div>
        <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px">ПОВТОРИ</div>
        <input id="pwNew2" type="password" autocomplete="new-password" style="width:160px">
      </div>
      <button class="btn gr" onclick="changePassword()">✓ Змінити пароль</button>
    </div>
    <div style="border-top:1px solid var(--brd);margin:14px 0"></div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
      <label style="display:flex;align-items:center;gap:7px;font-size:12px;padding-bottom:9px;cursor:pointer"><input type="checkbox" id="httpsEnabled"> HTTPS</label>
      <div>
        <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px">CERT (pem/crt)</div>
        <input id="httpsCert" placeholder="C:/certs/server.crt" style="width:220px">
      </div>
      <div>
        <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px">KEY (pem/key)</div>
        <input id="httpsKey" placeholder="C:/certs/server.key" style="width:220px">
      </div>
      <button class="btn gr" onclick="saveHttps()">✓ Зберегти</button>
      <button class="btn" onclick="genHttps()">🔑 Згенерувати self-signed</button>
    </div>
    <div id="httpsInfo" style="font-size:11px;color:var(--mu);margin-top:8px">—</div>
    <div id="tunnelInfo" style="font-size:12px;color:var(--mu);margin-top:10px;padding-top:10px;border-top:1px solid var(--brd)">—</div>
  </div>
</div>
</div>

<!-- ➕ МОДАЛ СТВОРЕННЯ ЛОТУ -->
<div id="bulkRenameModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:10000;align-items:center;justify-content:center">
  <div style="background:var(--card);border:1px solid var(--brd);border-radius:12px;padding:24px;width:min(600px,95vw);max-height:90vh;overflow-y:auto">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
      <span style="font-weight:700;font-size:15px">✏ <span data-i18n="deal.bulkTitle">Масове заповнення назв</span></span>
      <button onclick="g('bulkRenameModal').style.display='none'" style="background:none;border:none;color:var(--mu);font-size:18px;cursor:pointer">✕</button>
    </div>
    <div style="font-size:11px;color:var(--mu);margin-bottom:14px" data-i18n="deal.bulkDesc">Записи згруповані по сумі продажу. Введи назву — вона застосується до всіх записів з цією сумою без назви.</div>
    <div id="bulkRenameList"></div>
    <div style="display:flex;gap:8px;margin-top:16px;justify-content:flex-end">
      <button class="btn" onclick="g('bulkRenameModal').style.display='none'" data-i18n="cancel">Скасувати</button>
      <button class="btn gr" onclick="applyBulkRename()">✅ <span data-i18n="apply">Застосувати</span></button>
    </div>
  </div>
</div>

<!-- 💵 МАСОВА КОМІСІЯ -->
<div id="bulkFeeModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:10000;align-items:center;justify-content:center">
  <div style="background:var(--card);border:1px solid var(--brd);border-radius:12px;padding:24px;width:min(480px,95vw)">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
      <span style="font-weight:700;font-size:15px">% <span data-i18n="deal.bulkFeeTitle">Масова комісія</span></span>
      <button onclick="g('bulkFeeModal').style.display='none'" style="background:none;border:none;color:var(--mu);font-size:18px;cursor:pointer">✕</button>
    </div>
    <div style="font-size:12px;color:var(--mu);margin-bottom:12px">
      <span data-i18n="deal.bulkFeeDesc">Застосується до поточного фільтра. Перерахує комісію, after-fee і чистий прибуток.</span><br>
      <b id="bulkFeeCount" style="color:var(--tx)"></b>
    </div>
    <div style="display:flex;gap:10px;align-items:flex-end">
      <div>
        <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px" data-i18n="f.feePct">КОМІСІЯ %</div>
        <input id="bulkFeePct" type="number" min="0" max="100" step="0.1" placeholder="10" style="width:110px">
      </div>
      <div style="font-size:11px;color:var(--mu);padding-bottom:8px" data-i18n="deal.bulkFeeHint">0–100. Інші витрати не змінюються.</div>
    </div>
    <div style="display:flex;gap:8px;margin-top:16px;justify-content:flex-end">
      <button class="btn" onclick="g('bulkFeeModal').style.display='none'" data-i18n="cancel">Скасувати</button>
      <button class="btn gr" onclick="applyBulkFee()">✅ <span data-i18n="apply">Застосувати</span></button>
    </div>
  </div>
</div>

<!-- 💰 КАЛЬКУЛЯТОР ЦІНИ -->
<div id="lotModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:10000;align-items:center;justify-content:center">
  <div style="background:var(--card);border:1px solid var(--brd);border-radius:12px;padding:24px;width:min(560px,95vw);max-height:90vh;overflow-y:auto">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:18px">
      <div style="font-family:var(--font);font-size:13px;letter-spacing:2px;color:var(--a1)">💰 <span data-i18n="lot.title">КАЛЬКУЛЯТОР ЦІНИ</span></div>
      <button onclick="closeLotModal()" style="background:transparent;border:none;color:var(--mu);font-size:20px;cursor:pointer">✕</button>
    </div>
    <div style="display:flex;gap:8px;margin-bottom:16px">
      <button id="lmBtnZX" class="btn on" onclick="setLotPlatform('zeusx')" style="flex:1;font-size:11px">⚡ ZeusX (10%)</button>
      <button id="lmBtnFP" class="btn" onclick="setLotPlatform('funpay')" style="flex:1;font-size:11px">🔵 FunPay (7%)</button>
    </div>
    <div style="display:flex;flex-direction:column;gap:12px">
      <div>
        <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px" data-i18n="lot.name">НАЗВА ТОВАРУ</div>
        <input id="lmTitle" style="width:100%;padding:8px 12px;background:var(--bg2);border:1px solid var(--brd);border-radius:6px;color:var(--tx);font-size:13px" placeholder="Назва...">
      </div>
      <div style="display:flex;gap:10px">
        <div style="flex:1">
          <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px" data-i18n="lot.buy">ЗАКУПІВЛЯ ($)</div>
          <input id="lmBuyPrice" type="number" step="0.01" style="width:100%;padding:8px 12px;background:var(--bg2);border:1px solid var(--brd);border-radius:6px;color:var(--tx);font-size:13px;font-family:var(--font)" oninput="calcLotPrice()">
        </div>
        <div style="flex:1">
          <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px" data-i18n="lot.markup">НАЦІНКА %</div>
          <input id="lmMarkup" type="number" value="30" min="0" max="500" style="width:100%;padding:8px 12px;background:var(--bg2);border:1px solid var(--brd);border-radius:6px;color:var(--tx);font-size:13px;font-family:var(--font)" oninput="calcLotPrice()">
        </div>
        <div style="flex:1">
          <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px" data-i18n="lot.sell">ПРОДАЖ ($)</div>
          <input id="lmSellPrice" type="number" step="0.01" style="width:100%;padding:8px 12px;background:var(--bg2);border:1px solid var(--brd);border-radius:6px;color:var(--gr);font-size:13px;font-family:var(--font);font-weight:700">
        </div>
      </div>
      <div>
        <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px" data-i18n="lot.gameSource">ГРА / ДЖЕРЕЛО</div>
        <input id="lmGame" style="width:100%;padding:8px 12px;background:var(--bg2);border:1px solid var(--brd);border-radius:6px;color:var(--tx);font-size:13px" placeholder="Genshin Impact...">
      </div>
      <div>
        <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px" data-i18n="lot.desc">ОПИС</div>
        <textarea id="lmDesc" rows="3" style="width:100%;padding:8px 12px;background:var(--bg2);border:1px solid var(--brd);border-radius:6px;color:var(--tx);font-size:12px;resize:vertical" data-i18n-ph="ph.desc" placeholder="Опис..."></textarea>
      </div>
    </div>
    <div id="lmSummary" style="margin-top:14px;padding:10px 14px;background:var(--bg2);border-radius:8px;font-size:12px;display:none">
      <span style="color:var(--mu)"><span data-i18n="an.profit">Прибуток</span>: </span><span id="lmProfit" style="font-family:var(--font);font-weight:700"></span>
      <span style="color:var(--mu);margin-left:12px" data-i18n="lot.afterFee">Після комісії: </span><span id="lmAfterFee" style="font-family:var(--font);font-weight:700;color:var(--gr)"></span>
    </div>
    <div style="display:flex;gap:8px;margin-top:18px">
      <button onclick="copyLotLink()" class="btn gr" style="flex:1;font-size:12px;padding:10px">📋 <span data-i18n="lot.copy">КОПІЮВАТИ ДЛЯ ЛОТУ</span></button>
      <button onclick="closeLotModal()" class="btn" style="font-size:12px;padding:10px">✕</button>
    </div>
    <div id="lmResult" style="margin-top:10px;font-size:12px;text-align:center"></div>
  </div>
</div>

<!-- ⚖ ПОРІВНЯННЯ ЦІН МІЖ МАГАЗИНАМИ -->
<div id="cmpModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.72);z-index:10000;align-items:center;justify-content:center">
  <div style="background:var(--card);border:1px solid var(--brd);border-radius:12px;padding:22px;width:min(680px,95vw);max-height:88vh;overflow-y:auto">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
      <div class="ph" style="margin:0">⚖ <span data-i18n="sup.compareTitle">ПОРІВНЯННЯ ЦІН</span></div>
      <button onclick="closeCmp()" style="background:none;border:none;color:var(--mu);font-size:20px;cursor:pointer">✕</button>
    </div>
    <div id="cmpBody"></div>
  </div>
</div>

<!-- 📈 ІСТОРІЯ ЦІНИ -->
<div id="histModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.72);z-index:10000;align-items:center;justify-content:center">
  <div style="background:var(--card);border:1px solid var(--brd);border-radius:14px;padding:22px;width:min(640px,95vw);max-height:88vh;overflow-y:auto">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
      <div class="ph" style="margin:0">📈 <span data-i18n="sup.historyTitle">ІСТОРІЯ ЦІНИ</span></div>
      <button onclick="closeHist()" style="background:none;border:none;color:var(--mu);font-size:22px;cursor:pointer">✕</button>
    </div>
    <div id="histBody"></div>
  </div>
</div>
<script>
// (v4.5: 326 демо-записів IMPORTED_DATA видалено — вони засівались у реальний P&L)
// (v4.6: ручне внесення продажу більше не шле Telegram — тільки пошта + ціль)
// ═══════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════
let purchases=[];
let plPg=1, plFilt=[];
// Комісії приходять з Python (єдине джерело істини: PLATFORM_FEES/PAYOUT_FEES/ED_FEE)
const FEE_CFG = __FEE_CONFIG__;
const GT_PAID = __PAID_MODE__;
const FEES        = FEE_CFG.fees;                 // комісія майданчика → P&L
const PAYOUT_FEES = FEE_CFG.payout;               // вивід грошей → калькулятор
const ED_FEE      = FEE_CFG.ed;                   // ELDORADO
let FEE_PROFILES = {funpay: FEES.funpay, eldorado: ED_FEE, other: (FEES.other||0), games:{}};
const PLATFORM_FEES = {                           // калькулятор = майданчик + вивід
  zeusx:  (FEES.zeusx  || 0) + (PAYOUT_FEES.zeusx  || 0),
  funpay: (FEES.funpay || 0) + (PAYOUT_FEES.funpay || 0),
};
let supLoaded=false;
const PP=25; // per page

// Локальна дата YYYY-MM-DD (toISOString() дає UTC: з 00:00 до 03:00 в Україні
// «сьогодні» показувало вчорашній день і записи падали в чужий місяць)
function localDate(d){
  const x = d ? new Date(d) : new Date();
  return new Date(x.getTime() - x.getTimezoneOffset()*60000).toISOString().slice(0,10);
}
function todayLocal(){ return localDate(); }
function safeParse(text, fallback){
  try{ const v = JSON.parse(text); return v==null ? fallback : v; }
  catch(e){ return fallback; }
}
function safeArray(text){
  const v = safeParse(text, []);
  return Array.isArray(v) ? v : [];
}

// Динамічні місяці у фільтрах (замість захардкожених «Січень/Лютий 2026»)
const MONTH_NAMES={
  uk:['Січень','Лютий','Березень','Квітень','Травень','Червень',
      'Липень','Серпень','Вересень','Жовтень','Листопад','Грудень'],
  en:['January','February','March','April','May','June',
      'July','August','September','October','November','December'],
  ru:['Январь','Февраль','Март','Апрель','Май','Июнь',
      'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
};
let _monthsSig='';
function monthLabel(key){
  const p=String(key).split('-');
  const names=MONTH_NAMES[LANG]||MONTH_NAMES.uk;
  return (names[(+p[1])-1]||key)+' '+p[0];
}
function fillMonthOptions(){
  const keys=[...new Set(purchases.map(p=>(p.date||'').slice(0,7)).filter(k=>/^\d{4}-\d{2}$/.test(k)))]
    .sort().reverse();
  const sig=LANG+'|'+keys.join(',');
  if(sig===_monthsSig) return;
  _monthsSig=sig;
  const html=keys.map(k=>`<option value="m:${k}">${monthLabel(k)}</option>`).join('');
  const a=g('plMonthGroup'), b=g('statsMonthGroup');
  if(a) a.innerHTML=html;
  if(b) b.innerHTML=html;
  // після перебудови optgroup повертаємо вибір користувача
  ['plDateFilter','statsPeriod'].forEach(id=>{
    const el=g(id); if(!el) return; const v=el.value; el.value=v;
  });
}
// INIT


function g(i){return document.getElementById(i)}

// ═══════════════════════════════════════════════
// 🔐 CSRF: токен з cookie → заголовок X-GT-CSRF для всіх мутацій
//    (працює за будь-яким доменом/проксі; без нього POST відхиляється)
// ═══════════════════════════════════════════════
function csrfToken(){
  const m = document.cookie.match(/(?:^|;\s*)gt_csrf=([^;]+)/);
  return m ? decodeURIComponent(m[1]) : '';
}
const _nativeFetch = window.fetch.bind(window);
window.fetch = function(url, opts){
  opts = opts || {};
  const method = (opts.method || 'GET').toUpperCase();
  if(method !== 'GET' && method !== 'HEAD'){
    const t = csrfToken();
    if(t){
      const h = new Headers(opts.headers || {});
      h.set('X-GT-CSRF', t);
      opts.headers = h;
    }
  }
  return _nativeFetch(url, opts);
};

// ═══════════════════════════════════════════════
// 🎨 ТЕМИ
// ═══════════════════════════════════════════════
const THEMES = {
  ledger:{bg:'#08090A',bg2:'#0B0C0E',card:'#0B0C0E',card2:'#111214',brd:'#1D1F23',
          a1:'#EDEEF0',a2:'#D9A05B',a3:'#8B95F0',a4:'#8FBFD9',a5:'#4CB782',
          tx:'#E6E6E6',mu:'#82878F',gr:'#4CB782',rd:'#E08A8A',yw:'#D9A05B'},
  slate:{bg:'#0d1017',bg2:'#11151e',card:'#151a24',card2:'#1b2130',brd:'#28303f',
         a1:'#7c8cff',a2:'#ff7a59',a3:'#a78bfa',a4:'#22d3ee',a5:'#34d399',
         tx:'#e9ebf2',mu:'#8b95a9',gr:'#34d399',rd:'#f87171',yw:'#fbbf24'},
  nord:{bg:'#0b1220',bg2:'#0f1728',card:'#131c2e',card2:'#182236',brd:'#26334a',
        a1:'#5aa9e6',a2:'#f4a259',a3:'#9d8df1',a4:'#38bdf8',a5:'#4ade80',
        tx:'#e6edf6',mu:'#8ea1bb',gr:'#4ade80',rd:'#fb7185',yw:'#facc15'},
  carbon:{bg:'#12100e',bg2:'#181512',card:'#1e1a16',card2:'#26211b',brd:'#3a322a',
        a1:'#e8a33d',a2:'#f2705a',a3:'#c4a2f0',a4:'#68c4b8',a5:'#9ecb6a',
        tx:'#f2ece4',mu:'#a89a89',gr:'#9ecb6a',rd:'#f2705a',yw:'#e8c547'},
  light:{bg:'#f5f6fa',bg2:'#ffffff',card:'#ffffff',card2:'#f1f3f8',brd:'#dde2ec',
        a1:'#4f5bd5',a2:'#e05f3c',a3:'#7c5cd6',a4:'#0e8fa8',a5:'#12876f',
        tx:'#141a24',mu:'#5d6675',gr:'#0f7a5a',rd:'#c0392b',yw:'#a86a00'},
};
const THEME_VARS = ['bg','bg2','card','card2','brd','a1','a2','a3','a4','a5','tx','mu','gr','rd','yw'];

function setTheme(name){
  const t = THEMES[name] || THEMES.slate;
  if(!THEMES[name]) name = 'slate';
  const r = document.documentElement.style;
  THEME_VARS.forEach(k => { if(t[k]) r.setProperty('--'+k, t[k]); });
  localStorage.setItem('gt_theme2', name);
  document.documentElement.dataset.theme = name;
  document.querySelectorAll('.theme-btn').forEach(b=>{
    b.classList.toggle('active', b.dataset.theme===name);
  });
}

function pickTheme(name){
  try{ localStorage.setItem('gt_theme_pick','1'); }catch(e){}
  setTheme(name);
}

function loadTheme(){
  _mergeChannels();
  const picked = localStorage.getItem('gt_theme_pick') === '1';
  const t = localStorage.getItem('gt_theme2');
  setTheme((picked && THEMES[t]) ? t : 'ledger');
}

// ── розмір шрифту (A− / A+), запам'ятовується в браузері ──
let _fs = parseFloat(localStorage.getItem('gt_fs') || '1');
function applyFs(){
  _fs = Math.min(1.35, Math.max(0.85, Math.round(_fs*100)/100));
  document.documentElement.style.setProperty('--fs', _fs);
  localStorage.setItem('gt_fs', _fs);
  const b = document.getElementById('fsVal');
  if(b) b.textContent = Math.round(_fs*100)+'%';
}
function setFs(d){ _fs += d; applyFs(); }
function resetFs(){ _fs = 1; applyFs(); }
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;')}

// ═══════════════════════════════════════════════
//  МОВА (UA / EN)
// ═══════════════════════════════════════════════


const I18N = {
  uk:{'ch.src':'Дані читаються з ваших кабінетів за збереженими cookie (ZeusX — API, FunPay — сторінка замовлень). Оновлюється не частіше ніж раз на 2 хвилини.','an.detail':'ДЕТАЛЬНА ТАБЛИЦЯ','f.other2':'Інше','ta.allGames':'Всі ігри','ta.allTypes':'Всі типи','ta.allRegions':'Всі регіони','s.dateDesc':'Дата ↓','s.dateAsc':'Дата ↑','s.profitDesc':'Прибуток ↓','s.sellDesc':'Продаж ↓','s.cheapFirst':'Дешевші спершу','s.expFirst':'Дорожчі спершу','s.starter':'Стартові','s.developed':'Розвинені','s.endgame':'Ендгейм','s.noTitle':'⚠ Без назви','s.moreVariants':'🎛 Більше варіантів','s.cardOnly':'💳 Тільки з оплатою карткою','ed.title':'Назва товару','ph.dealTitle':'напр. Arknights Starter','ph.pw6':'мін. 6 символів','ph.desc':'Опис...','ed.buy':'Ціна купівлі $','ed.sell':'Ціна продажу $','ed.oid':'Order ID (необов язково)','ed.cat':'Категорія (необов язково)','ed.csvbtn':'CSV (фільтр)','ed.empty':'Ще немає записів', 'nav.overview':'Огляд','nav.deals':'Угоди','nav.orders':'Замовлення','nav.channels':'Канали',
       'nav.catalog':'Каталог','nav.plan':'План','nav.taobao':'Taobao','nav.inventory':'Інвентар',
       'nav.analytics':'Аналітика','hdr.sub':'УГОДИ · КАНАЛИ · ПОШТА',
       'ov.today':'Сьогодні','ov.add':'Угода','ov.channels':'Канали','ov.profit':'Прибуток · місяць',
       'ov.actions':'Потребує дії','ov.stock':'Склад','ov.health':'Стан системи','ov.feed':'Що сталось',
       'ch.title':'Канали','ch.refresh':'Оновити','ch.bal':'Баланси',
       'th.date':'Дата','th.channel':'Канал','th.game':'Гра','th.buy':'Купив','th.sell':'Продав',
       'th.fee':'Комісія','th.profit':'Прибуток','st.ok':'Все гаразд','st.bad':'Є проблеми',
       'u.orders':'замовлення в черзі','u.none':'нічого не чекає','u.frozen':'заморожено',
       'u.agent':'агент','u.online':'онлайн','u.offline':'офлайн','u.vs':'проти',
       'ph.newDeal':'+ НОВИЙ ПРОДАЖ','ph.records':'ЗАПИСИ','ph.cats':'РОЗБИВКА ПО КАТЕГОРІЯХ',
       'ph.products':'ТОВАРИ','ph.orders':'ЗАМОВЛЕННЯ З ПОШТИ','ph.channels':'Канали',
       'ph.taobao':'TAOBAO — ціни з Китаю','ph.stock':'СКЛАД — куплені акаунти',
       'ph.theme':'ТЕМА ІНТЕРФЕЙСУ','ph.backup':'БЕКАП P&L','ph.rate':'КУРС USD → UAH',
       'ph.tg':'TELEGRAM-СПОВІЩЕННЯ','ph.gmail':'GMAIL → TELEGRAM','ph.cloud':'ХМАРНИЙ БЕКАП',
       'ph.sec':'БЕЗПЕКА','ph.contact':'ПОТРІБНА АВТОМАТИЗАЦІЯ?','ph.contact.desc':'Автоматизація, гайди та оновлення — приєднуйся до Telegram або Discord.','ph.allch':'Усі канали — останні продажі','ph.edsales':'Eldorado — продажі',
       'btn.add':'Додати','btn.refresh':'Оновити','btn.save':'Зберегти','btn.clear':'Очистити',
       'btn.csv':'CSV','btn.excel':'Excel (всі дані)','btn.search':'Пошук…','btn.month':'Весь час',
       'f.title':'НАЗВА (необов.)','f.platform':'ПЛАТФОРМА','f.feePct':'КОМІСІЯ %','f.zeusRank':'РАНГ ZEUSX','f.buy':'КУПИВ $','f.sell':'ПРОДАВ $',
       'f.after':'ПІСЛЯ КОМІСІЇ','f.date':'ДАТА','f.other':'Інше',
       'b.add':'+ ДОДАТИ','b.sync':'СИНХРОНІЗУВАТИ','b.bulk':'МАСОВО','b.bulkFee':'КОМІСІЯ','b.clear':'Очистити',
       'search':'Пошук…','allPlat':'Всі платформи','allTime':'Весь час','byDate':'Дата ↓',
       'cf.search':'Пошук...','cf.sortNone':'Без сорт.','cf.sortNew':'Нові першими','cf.sortUpdated':'Оновлені першими','cf.priceUp':'Ціна ↑','cf.priceDown':'Ціна ↓','cf.saleFirst':'Sale першими','cf.avail':'є в наявності','cf.gone':'зниклі','cf.cheaper':'дешевше','ct.name':'НАЗВА','ct.src':'ДЖЕРЕЛО','ct.price':'ЦІНА','ct.disc':'ЗНИЖКА','ct.avail':'НАЯ.','ct.date':'ДАТА','cb.shop':'Магазин','cb.history':'Історія','cb.compare':'Порівняти','cb.lot':'Лот','tb.lot':'Лот','tb.checkPay':'Перевірити оплату','tb.collect':'Зібрати зараз','plan.title':'ЩО КУПИТИ СЬОГОДНІ','plan.hint':'Ціна постачальника проти вашої медіани продажу по схожих лотах (та сама гра + спільні слова назви), комісія ZeusX 5–10% за рангом.','inv.name':'Назва','inv.game':'Гра','inv.cost':'Собівартість, $','inv.source':'Джерело','inv.account':'Дані акаунта (логін / пароль / пошта)','inv.all':'Всі','inv.inStock':'На складі','inv.sold':'Продані','inv.off':'Списані','inv.intro':'Тут куплені акаунти: скільки коштували, у кого, і чи продані. Дає реальну маржу й показує, скільки грошей «заморожено».','inv.csvStock':'CSV (склад, +30%)','inv.csvSup':'CSV (постач., +30%)','tbth.lot':'ЛОТ','tbth.game':'ГРА','tbth.price':'ЦІНА','tbth.atSup':'У ПОСТАЧАЛЬНИКА','tbth.diff':'РІЗНИЦЯ','tbth.qty':'К-СТЬ','tbth.withAgent':'З ПОСЕРЕДНИКОМ','per.all':'Весь час','per.today':'Сьогодні','per.week':'Цей тиждень','per.month':'Цей місяць','per.months':'Місяці','per.custom':'Свій період','st.setup':'Готово до роботи','tb.d1':'Збирається колектором на вашому ПК. Агент працює у фоні (автозапуск при вході в Windows) і сам відкриває вікно браузера, якщо його немає. Капчу проходите ви — колектор чекає. Ціни в юанях, нижче — орієнтовний долар.','tb.d2':'Мітки: натисніть 💳 біля лота, якщо там оплата карткою, і 🎛 — скільки варіантів акаунтів. Taobao часто блокує автоматичне читання сторінок лотів, тому ручна мітка — найнадійніше.','tb.d3':'Оплата: картка / Apple Pay через Alipay International (платформа, не продавець). Лоти «代充 / 充值 / 话费» (поповнення балансу, телефон, ключі) не підходять під таку оплату — вони вже відфільтровані.','tg.hint':'Бот пише лише про те, що прийшло з пошти (нові замовлення й повідомлення FunPay / ZeusX / Eldorado) та про досягнення цілі. Ручне внесення продажу в таблицю не сповіщає. Створи бота у @BotFather, встав токен і свій chat_id (дізнатись у @userinfobot).','pw.hint':'Без пароля будь-хто, хто відкриє посилання, отримає доступ. Увімкніть пароль, якщо застосунок доступний з інтернету.','tg.cmds':'Бот відповідає на команди (тільки ваш чат): /stats — продажі сьогодні й за місяць · /balance — баланс ZeusX / FunPay / Eldorado · /new — останні замовлення · /taobao — топ вигідних лотів · /help','gm.hint':'Трекер читає пошту (IMAP) і надсилає в Telegram нові замовлення та повідомлення FunPay / ZeusX / Eldorado. Потрібен App Password (не звичайний пароль): Google Account → Security → 2-Step Verification → App passwords + увімкнений IMAP у Gmail.','inv.ph':'логін: user@mail.com\nпароль: 12345\nпошта: user@mail.com','tb.need':'Щоб збір запрацював, потрібно: 1) агент збору на вашому ПК (окремий файл, запускається разом із Windows); 2) акаунт Taobao; 3) один раз увійти в браузері агента — сканування QR-коду з телефона; 4) капчу при першому запиті проходите ви вручну. Після цього лоти оновлюються у фоні, а ви бачите ціни тут.','cta.screens':'Скріншоти функцій →','ed.buy':'Ціна купівлі $','ed.sell':'Ціна продажу $','ed.oid':'Order ID (необов\'язково)','ed.cat':'Категорія (необов\'язково)','ed.csvbtn':'CSV (фільтр)','ed.empty':'Ще немає записів','k.buy':'Купив','k.sell':'Продав','k.fee':'Комісія','k.profit':'Прибуток','feeProf.title':'КОМІСІЇ ЗА ЗАМОВЧУВАННЯМ','feeProf.hint':'Дефолти для нових угод. Старі угоди зберігають свою комісію. ZeusX керується рангом у формі угоди.','feeProf.games':'ОКРЕМІ ІГРИ (назва | платформа | %)','feeProf.gamesHint':'Один рядок на гру. Платформа: funpay / eldorado / other. Порожньо — без overrides.','k.expenses':'Витрати','k.net':'Чистий','pl.expenses':'ВИТРАТИ','f.expenses':'ІНШІ ВИТРАТИ $','f.net':'ЧИСТИЙ ПРИБУТОК','inv.sellFromStock':'Продаж зі складу',
       'k.records':'ЗАПИСИ','k.search':'Пошук…','k.clear':'Очистити',

     },
  en:{'ch.src':'Data is read from your accounts using saved cookies (ZeusX — API, FunPay — order page). Refreshed no more than once every 2 minutes.','an.detail':'DETAIL TABLE','f.other2':'Other','ta.allGames':'All games','ta.allTypes':'All types','ta.allRegions':'All regions','s.dateDesc':'Date ↓','s.dateAsc':'Date ↑','s.profitDesc':'Profit ↓','s.sellDesc':'Sale ↓','s.cheapFirst':'Cheapest first','s.expFirst':'Most expensive first','s.starter':'Starter','s.developed':'Developed','s.endgame':'Endgame','s.noTitle':'⚠ Untitled','s.moreVariants':'🎛 More variants','s.cardOnly':'💳 Card payment only','ed.title':'Product name','ph.dealTitle':'e.g. Arknights Starter','ph.pw6':'min. 6 chars','ph.desc':'Description...','ed.buy':'Purchase price $','ed.sell':'Sale price $','ed.oid':'Order ID (optional)','ed.cat':'Category (optional)','ed.csvbtn':'CSV (filter)','ed.empty':'No records yet', 'nav.overview':'Overview','nav.deals':'Deals','nav.orders':'Orders','nav.channels':'Channels',
       'nav.catalog':'Catalog','nav.plan':'Plan','nav.taobao':'Taobao','nav.inventory':'Inventory',
       'nav.analytics':'Analytics','hdr.sub':'DEALS · CHANNELS · MAIL',
       'ov.today':'Today','ov.add':'Deal','ov.channels':'Channels','ov.profit':'Profit · month',
       'ov.actions':'Needs action','ov.stock':'Stock','ov.health':'System','ov.feed':'What happened',
       'ch.title':'Channels','ch.refresh':'Refresh','ch.bal':'Balances',
       'th.date':'Date','th.channel':'Channel','th.game':'Game','th.buy':'Bought','th.sell':'Sold',
       'th.fee':'Fee','th.profit':'Profit','st.ok':'All good','st.bad':'Issues found',
       'u.orders':'orders in queue','u.none':'nothing waiting','u.frozen':'frozen',
       'u.agent':'agent','u.online':'online','u.offline':'offline','u.vs':'vs',
       'ph.newDeal':'+ NEW DEAL','ph.records':'RECORDS','ph.cats':'BREAKDOWN BY CATEGORY',
       'ph.products':'PRODUCTS','ph.orders':'ORDERS FROM MAIL','ph.channels':'Channels',
       'ph.taobao':'TAOBAO — prices from China','ph.stock':'STOCK — bought accounts',
       'ph.theme':'INTERFACE THEME','ph.backup':'P&L BACKUP','ph.rate':'USD → UAH RATE',
       'ph.tg':'TELEGRAM NOTIFICATIONS','ph.gmail':'GMAIL → TELEGRAM','ph.cloud':'CLOUD BACKUP',
       'ph.sec':'SECURITY','ph.contact':'NEED AUTOMATION?','ph.contact.desc':'Automation, guides and updates — join us on Telegram or Discord.','ph.allch':'All channels — recent sales','ph.edsales':'Eldorado — sales',
       'btn.add':'Add','btn.refresh':'Refresh','btn.save':'Save','btn.clear':'Clear',
       'btn.csv':'CSV','btn.excel':'Excel (all data)','btn.search':'Search…','btn.month':'All time',
       'f.title':'TITLE (optional)','f.platform':'PLATFORM','f.feePct':'FEE %','f.zeusRank':'ZEUSX TIER','f.buy':'BOUGHT $','f.sell':'SOLD $',
       'f.after':'AFTER FEE','f.date':'DATE','f.other':'Other',
       'b.add':'+ ADD','b.sync':'SYNC','b.bulk':'BULK','b.bulkFee':'COMMISSION','b.clear':'Clear',
       'search':'Search…','allPlat':'All platforms','allTime':'All time','byDate':'Date ↓',
       'cf.search':'Search...','cf.sortNone':'No sorting','cf.sortNew':'Newest first','cf.sortUpdated':'Recently updated','cf.priceUp':'Price ↑','cf.priceDown':'Price ↓','cf.saleFirst':'On sale first','cf.avail':'in stock','cf.gone':'gone','cf.cheaper':'cheaper','ct.name':'NAME','ct.src':'SOURCE','ct.price':'PRICE','ct.disc':'DISCOUNT','ct.avail':'STOCK','ct.date':'DATE','cb.shop':'Shop','cb.history':'History','cb.compare':'Compare','cb.lot':'Lot','tb.lot':'Lot','tb.checkPay':'Check payment','tb.collect':'Collect now','plan.title':'WHAT TO BUY TODAY','plan.hint':'Supplier price against your median sale price for similar lots (same game + shared title words), ZeusX fee 5–10% by tier.','inv.name':'Name','inv.game':'Game','inv.cost':'Cost, $','inv.source':'Source','inv.account':'Account data (login / password / mail)','inv.all':'All','inv.inStock':'In stock','inv.sold':'Sold','inv.off':'Written off','inv.intro':'Bought accounts: what they cost, from whom, and whether they sold. Shows real margin and how much money is frozen.','inv.csvStock':'CSV (stock, +30%)','inv.csvSup':'CSV (suppliers, +30%)','tbth.lot':'LOT','tbth.game':'GAME','tbth.price':'PRICE','tbth.atSup':'AT SUPPLIER','tbth.diff':'DIFF','tbth.qty':'QTY','tbth.withAgent':'WITH AGENT','per.all':'All time','per.today':'Today','per.week':'This week','per.month':'This month','per.months':'Months','per.custom':'Custom range','st.setup':'Ready to use','tb.d1':'Collected by the agent on your PC. The agent runs in the background (autostart on Windows sign-in) and opens the browser window itself if needed. You pass the captcha — the agent waits. Prices are in CNY; approximate USD below.','tb.d2':'Marks: press 💳 next to a lot if card payment is available there, and 🎛 for how many account variants. Taobao often blocks automatic page reading of lots, so the manual mark is the most reliable.','tb.d3':'Payment: card / Apple Pay via Alipay International (platform, not a seller). Lots «代充 / 充值 / 话费» (balance top-up, phone, keys) do not support this payment — they are already filtered out.','tg.hint':'The bot writes only about what came from mail (new orders and messages from FunPay / ZeusX / Eldorado) and about reaching the goal. Manual sale entries in the table do not notify. Create a bot at @BotFather, paste the token and your chat_id (find it at @userinfobot).','pw.hint':'Without a password anyone who opens the link gets in. Set one if the app is reachable from the internet.','tg.cmds':'The bot answers commands (your chat only): /stats — sales today and for the month · /balance — ZeusX / FunPay / Eldorado balance · /new — latest orders · /taobao — top profitable lots · /help','gm.hint':'The tracker reads mail (IMAP) and sends new orders and messages from FunPay / ZeusX / Eldorado to Telegram. An App Password is required (not a regular password): Google Account → Security → 2-Step Verification → App passwords + IMAP enabled in Gmail.','inv.ph':'login: user@mail.com\npassword: 12345\nmail: user@mail.com','tb.need':'To start collecting you need: 1) the collector agent on your PC (separate file, starts with Windows); 2) a Taobao account; 3) sign in once in the agent\'s browser — scan the QR code with your phone; 4) pass the first captcha yourself. After that lots refresh in the background and you see prices here.','cta.screens':'Feature screenshots →','ed.buy':'Purchase price $','ed.sell':'Sale price $','ed.oid':'Order ID (optional)','ed.cat':'Category (optional)','ed.csvbtn':'CSV (filter)','ed.empty':'No records yet','k.buy':'Bought','k.sell':'Sold','k.fee':'Fee','k.profit':'Profit','feeProf.title':'DEFAULT MARKETPLACE FEES','feeProf.hint':'Defaults for new deals. Existing deals keep their saved fee. ZeusX is controlled by the tier in the deal form.','feeProf.games':'GAME OVERRIDES (name | platform | %)','feeProf.gamesHint':'One line per game. Platform: funpay / eldorado / other. Empty means no overrides.','k.expenses':'Expenses','k.net':'Net','pl.expenses':'EXPENSES','f.expenses':'OTHER EXPENSES $','f.net':'NET PROFIT','inv.sellFromStock':'Sell from stock',
       'k.records':'RECORDS','k.search':'Search…','k.clear':'Clear',

     },
  ru:{'ch.src':'Данные читаются из ваших кабинетов по сохранённым cookie (ZeusX — API, FunPay — страница заказов). Обновляется не чаще раза в 2 минуты.','an.detail':'ДЕТАЛЬНАЯ ТАБЛИЦА','f.other2':'Другое','ta.allGames':'Все игры','ta.allTypes':'Все типы','ta.allRegions':'Все регионы','s.dateDesc':'Дата ↓','s.dateAsc':'Дата ↑','s.profitDesc':'Прибыль ↓','s.sellDesc':'Продажа ↓','s.cheapFirst':'Дешевле сначала','s.expFirst':'Дороже сначала','s.starter':'Стартовые','s.developed':'Развитые','s.endgame':'Эндгейм','s.noTitle':'⚠ Без названия','s.moreVariants':'🎛 Больше вариантов','s.cardOnly':'💳 Только с оплатой картой','ed.title':'Название товара','ph.dealTitle':'напр. Arknights Starter','ph.pw6':'мин. 6 символов','ph.desc':'Описание...','ed.buy':'Цена покупки $','ed.sell':'Цена продажи $','ed.oid':'Order ID (необязательно)','ed.cat':'Категория (необязательно)','ed.csvbtn':'CSV (фильтр)','ed.empty':'Пока нет записей', 'nav.overview':'Обзор','nav.deals':'Сделки','nav.orders':'Заказы','nav.channels':'Каналы',
       'nav.catalog':'Каталог','nav.plan':'План','nav.taobao':'Taobao','nav.inventory':'Инвентарь',
       'nav.analytics':'Аналитика','hdr.sub':'СДЕЛКИ · КАНАЛЫ · ПОЧТА',
       'ov.today':'Сегодня','ov.add':'Сделка','ov.channels':'Каналы','ov.profit':'Прибыль · месяц',
       'ov.actions':'Требует действия','ov.stock':'Склад','ov.health':'Состояние системы','ov.feed':'Что произошло',
       'ch.title':'Каналы','ch.refresh':'Обновить','ch.bal':'Балансы',
       'th.date':'Дата','th.channel':'Канал','th.game':'Игра','th.buy':'Купил','th.sell':'Продал',
       'th.fee':'Комиссия','th.profit':'Прибыль','st.ok':'Всё хорошо','st.bad':'Есть проблемы',
       'u.orders':'заказов в очереди','u.none':'ничего не ждёт','u.frozen':'заморожено',
       'u.agent':'агент','u.online':'онлайн','u.offline':'офлайн','u.vs':'против',
       'ph.newDeal':'+ НОВАЯ ПРОДАЖА','ph.records':'ЗАПИСИ','ph.cats':'РАЗБИВКА ПО КАТЕГОРИЯМ',
       'ph.products':'ТОВАРЫ','ph.orders':'ЗАКАЗЫ ИЗ ПОЧТЫ','ph.channels':'Каналы',
       'ph.taobao':'TAOBAO — цены из Китая','ph.stock':'СКЛАД — купленные аккаунты',
       'ph.theme':'ТЕМА ИНТЕРФЕЙСА','ph.backup':'БЭКАП P&L','ph.rate':'КУРС USD → UAH',
       'ph.tg':'TELEGRAM-УВЕДОМЛЕНИЯ','ph.gmail':'GMAIL → TELEGRAM','ph.cloud':'ОБЛАЧНЫЙ БЭКАП',
       'ph.sec':'БЕЗОПАСНОСТЬ','ph.contact':'НУЖНА АВТОМАТИЗАЦИЯ?','ph.contact.desc':'Автоматизация, гайды и обновления — присоединяйся в Telegram или Discord.','ph.allch':'Все каналы — последние продажи','ph.edsales':'Eldorado — продажи',
       'btn.add':'Добавить','btn.refresh':'Обновить','btn.save':'Сохранить','btn.clear':'Очистить',
       'btn.csv':'CSV','btn.excel':'Excel (все данные)','btn.search':'Поиск…','btn.month':'Всё время',
       'f.title':'НАЗВАНИЕ (необяз.)','f.platform':'ПЛАТФОРМА','f.feePct':'КОМИССИЯ %','f.zeusRank':'РАНГ ZEUSX','f.buy':'КУПИЛ $','f.sell':'ПРОДАЛ $',
       'f.after':'ПОСЛЕ КОМИССИИ','f.date':'ДАТА','f.other':'Другое',
       'b.add':'+ ДОБАВИТЬ','b.sync':'СИНХРОНИЗИРОВАТЬ','b.bulk':'МАССОВО','b.bulkFee':'КОМИССИЯ','b.clear':'Очистить',
       'search':'Поиск…','allPlat':'Все платформы','allTime':'Всё время','byDate':'Дата ↓',
       'cf.search':'Поиск...','cf.sortNone':'Без сорт.','cf.sortNew':'Новые первыми','cf.sortUpdated':'Обновлённые','cf.priceUp':'Цена ↑','cf.priceDown':'Цена ↓','cf.saleFirst':'Sale первыми','cf.avail':'в наличии','cf.gone':'исчезли','cf.cheaper':'дешевле','ct.name':'НАЗВАНИЕ','ct.src':'ИСТОЧНИК','ct.price':'ЦЕНА','ct.disc':'СКИДКА','ct.avail':'В НАЛ.','ct.date':'ДАТА','cb.shop':'Магазин','cb.history':'История','cb.compare':'Сравнить','cb.lot':'Лот','tb.lot':'Лот','tb.checkPay':'Проверить оплату','tb.collect':'Собрать сейчас','plan.title':'ЧТО КУПИТЬ СЕГОДНЯ','plan.hint':'Цена поставщика против вашей медианы продажи по похожим лотам (та же игра + общие слова названия), комиссия ZeusX 5–10% по рангу.','inv.name':'Название','inv.game':'Игра','inv.cost':'Себестоимость, $','inv.source':'Источник','inv.account':'Данные аккаунта (логин / пароль / почта)','inv.all':'Все','inv.inStock':'На складе','inv.sold':'Проданы','inv.off':'Списаны','inv.intro':'Купленные аккаунты: сколько стоили, у кого, и проданы ли. Даёт реальную маржу и показывает, сколько денег «заморожено».','inv.csvStock':'CSV (склад, +30%)','inv.csvSup':'CSV (постав., +30%)','tbth.lot':'ЛОТ','tbth.game':'ИГРА','tbth.price':'ЦЕНА','tbth.atSup':'У ПОСТАВЩИКА','tbth.diff':'РАЗНИЦА','tbth.qty':'КОЛ-ВО','tbth.withAgent':'С ПОСРЕДНИКОМ','per.all':'Все время','per.today':'Сегодня','per.week':'Эта неделя','per.month':'Этот месяц','per.months':'Месяцы','per.custom':'Свой период','st.setup':'Готово к работе','tb.d1':'Собирается коллектором на вашем ПК. Агент работает в фоне (автозапуск при входе в Windows) и сам открывает окно браузера, если его нет. Капчу проходите вы — коллектор ждёт. Цены в юанях, ниже — ориентировочный доллар.','tb.d2':'Метки: нажмите 💳 у лота, если там оплата картой, и 🎛 — сколько вариантов аккаунтов. Taobao часто блокирует автоматическое чтение страниц лотов, поэтому ручная метка — надёжнее всего.','tb.d3':'Оплата: карта / Apple Pay через Alipay International (площадка, не продавец). Лоты «代充 / 充值 / 话费» (пополнение баланса, телефон, ключи) не поддерживают такую оплату — они уже отфильтрованы.','tg.hint':'Бот пишет только о том, что пришло из почты (новые заказы и сообщения FunPay / ZeusX / Eldorado) и о достижении цели. Ручное внесение продажи в таблицу не уведомляет. Создай бота в @BotFather, вставь токен и свой chat_id (узнать в @userinfobot).','pw.hint':'Без пароля любой, кто откроет ссылку, получит доступ. Включите пароль, если приложение доступно из интернета.','tg.cmds':'Бот отвечает на команды (только ваш чат): /stats — продажи сегодня и за месяц · /balance — баланс ZeusX / FunPay / Eldorado · /new — последние заказы · /taobao — топ выгодных лотов · /help','gm.hint':'Трекер читает почту (IMAP) и отправляет в Telegram новые заказы и сообщения FunPay / ZeusX / Eldorado. Нужен App Password (не обычный пароль): Google Account → Security → 2-Step Verification → App passwords + включённый IMAP в Gmail.','inv.ph':'логин: user@mail.com\nпароль: 12345\nпочта: user@mail.com','tb.need':'Чтобы сбор заработал, нужно: 1) агент сбора на вашем ПК (отдельный файл, запускается вместе с Windows); 2) аккаунт Taobao; 3) один раз войти в браузере агента — сканирование QR-кода с телефона; 4) капчу при первом запросе проходите вы вручную. После этого лоты обновляются в фоне, а вы видите цены здесь.','cta.screens':'Скриншоты функций →','ed.buy':'Цена покупки $','ed.sell':'Цена продажи $','ed.oid':'Order ID (необязательно)','ed.cat':'Категория (необязательно)','ed.csvbtn':'CSV (фильтр)','ed.empty':'Пока нет записей','k.buy':'Купил','k.sell':'Продал','k.fee':'Комиссия','k.profit':'Прибыль','feeProf.title':'КОМИССИИ ПО УМОЛЧАНИЮ','feeProf.hint':'Дефолты для новых сделок. Старые сделки сохраняют свою комиссию. ZeusX управляется рангом в форме сделки.','feeProf.games':'ОТДЕЛЬНЫЕ ИГРЫ (название | платформа | %)','feeProf.gamesHint':'Одна строка на игру. Платформа: funpay / eldorado / other. Пусто — без overrides.','k.expenses':'Расходы','k.net':'Чистая','pl.expenses':'РАСХОДЫ','f.expenses':'ДРУГИЕ РАСХОДЫ $','f.net':'ЧИСТАЯ ПРИБЫЛЬ','inv.sellFromStock':'Продажа со склада',
       'k.records':'ЗАПИСИ','k.search':'Поиск…','k.clear':'Очистить' },
};
// ── Додаткові ключі для динамічного UI (не чіпаючи великі словники вище) ──
const EXTRA_I18N = {
  uk: {
    "all":"Всі","total":"ВСЬОГО","loading":"Завантаження…","noData":"Немає даних",
    "save":"Зберегти","close":"Закрити","copy":"Копіювати","delete":"Видалити",
    "edit":"Редагувати","show":"Показати","refresh":"Оновити","cancel":"Скасувати",
    "apply":"Застосувати","disconnect":"Відключити",
    "inv.costShort":"Собівартість","inv.status":"Статус","inv.inStockShort":"на складі",
    "inv.soldShort":"продано","inv.offShort":"списано","inv.sourceShort":"Джерело",
    "inv.empty":"Порожньо — додайте першу закупівлю","inv.dead":"Мертвий склад",
    "inv.noDead":"Мертвого складу немає","inv.oldest":"найстаріша позиція",
    "inv.added":"Додано на склад","inv.soldToast":"Позначено як продано",
    "inv.offToast":"Списано","inv.returnToast":"Повернуто на склад","inv.deleted":"Видалено",
    "inv.deleteConfirm":"Видалити запис зі складу?","inv.noAccount":"(даних немає)",
    "inv.enterName":"Введіть назву",
    "an.deals":"Угод","an.revenue":"Виручка","an.profit":"Прибуток","an.margin":"Маржа","an.platforms":"ПРИБУТОК ПО ПЛАТФОРМАХ","an.platform":"ПЛАТФОРМА","an.feeCol":"КОМІСІЇ","an.expenseCol":"ВИТРАТИ","an.netCol":"ЧИСТИЙ","an.netPct":"NET %",
    "an.games":"Різних ігор","an.best":"Найкраща","an.total":"РАЗОМ P&L + ELD",
    "an.totalIn":"Разом у","an.game":"ГРА","an.dealsCol":"УГОД","an.revenueCol":"ВИРУЧКА",
    "an.profitCol":"ПРИБУТОК","an.marginCol":"МАРЖА",
    "an.thisVsLast":"ЦЕЙ МІСЯЦЬ ПРОТИ МИНУЛОГО","an.profitPL":"Прибуток P&L",
    "an.revenuePL":"Виторг P&L","an.profitED":"Прибуток ELDORADO",
    "an.totalProfit":"Разом прибуток","an.was":"було","an.new":"новий",
    "an.revenueChart":"Виторг","an.profitChart":"Прибуток","an.noData":"Немає даних",
    "rep.count":"Продажів","rep.revenue":"Виторг","rep.fees":"Комісії",
    "rep.cogs":"Собівартість проданого","rep.profit":"Прибуток",
    "rep.purchases":"Закупівлі за місяць","rep.cash":"Касовий потік",
    "rep.stock":"На складі зараз",
    "rep.formula":"Прибуток = виторг − комісії − собівартість проданого. Касовий потік = виторг − комісії − закупівлі цього місяця.",
    "rep.calculating":"Рахую…",
    "sup.noSuppliers":"Ще немає постачальників — додайте у ⚙ → Постачальники",
    "sup.none":"Нічого не знайдено","sup.empty":"База порожня — натисни ↺ або зачекай оновлення",
    "sup.sale":"ЗНИЖКА","sup.availYes":"є","sup.availNo":"нема","sup.gone":"зник",
    "sup.compareTitle":"Порівняння цін","sup.compareBase":"Базовий",
    "sup.compareFound":"Схожі товари в інших магазинах","sup.compareNone":"Схожих товарів не знайдено",
    "sup.historyTitle":"Історія ціни",
    "sup.historyEmpty":"Історії ще немає. Вона зʼявляється після змін ціни (каталог оновлюється раз на добу).",
    "sup.notFound":"Товар не знайдено","sup.added":"Постачальника додано",
    "sup.enterName":"Введіть назву магазину та URL",
    "sup.badUrl":"URL має починатися з http:// або https://",
    "plan.supplier":"Постачальник","plan.yourSale":"Ваш продаж","plan.margin":"Маржа",
    "plan.demand":"Попит","plan.sales":"продажів",
    "tb.type":"ТИП","tb.lastRuns":"Останні збори","tb.cartEmpty":"Кошик порожній — натисніть 🛒 біля лота, щоб додати",
    "tb.cart":"Кошик","tb.lotOne":"лот","tb.lotMany":"лотів",
    "tb.cardWithMiddleman":"на картці з посередником","tb.clear":"Очистити",
    "tb.fromSupplier":"у постачальника від",
    "tb.notChecked":"Ще не перевіряли. Натисніть «💳 Перевірити оплату» — потрібен вхід у Taobao у вікні браузера.",
    "tb.added":"Лот додано","tb.pricePositive":"Ціна має бути > 0",
    "tb.manualLink":"Посилання на лот Taobao (item.taobao.com/item.htm?id=…)",
    "tb.manualTitle":"Назва лота (коротко)","tb.manualPrice":"Ціна в юанях (¥)",
    "tb.cardQuestion":"Оплата карткою доступна в цьому лоті?",
    "tb.optionsQuestion":"Скільки варіантів акаунтів у лоті? (0 — невідомо)",
    "tb.markedCard":"Позначено: оплата карткою","tb.cardRemoved":"Мітку знято",
    "tb.options":"Варіантів",
    "tb.clearCartConfirm":"Очистити кошик (зняти мітки 🛒 з усіх лотів)?",
    "tb.checkConfirm":"Перевірити оплату карткою та кількість варіантів у топ-25 лотів?\n\nКолектор відкриє кожен лот у браузері (~2 хв). Потрібен вхід у Taobao.",
    "tb.collectConfirm":"Запустити збір з Taobao зараз?\n\nЯкщо вікно браузера закрите — агент відкриє його сам (start_cf_debug.bat). Увійдіть у Taobao і пройдіть капчу, збір почнеться автоматично.",
    "tb.collectCooldown":"Збір уже був %s хв тому (кулдаун 3 год). Все одно запустити зараз?",
    "tb.collectRequested":"Запит надіслано",
    "bk.typePL":"P&L","bk.typeED":"ELDORADO","bk.typeGoal":"Ціль",
    "bk.typeSettings":"Налаштування","bk.typeMail":"Пошта","bk.typeInventory":"Склад",
    "bk.typeArchive":"Архів","bk.typeOther":"Інше","bk.restore":"Відновити",
    "bk.notRestorable":"—","bk.none":"Бекапів ще немає",
    "bk.restoreConfirm":"Відновити «%s»?\n\nПоточна версія буде збережена як …_before_restore_….json",
    "bk.restored":"Відновлено","bk.saved":"Бекап збережено! Файлів:","bk.error":"Помилка бекапу:",
    "pw.optional":"ПАРОЛЬ (НЕОБОВ'ЯЗКОВО)","audit.title":"ЖУРНАЛ ДІЙ","audit.hint":"Останні зміни угод, комісій, складу й налаштувань. Секрети й паролі не пишуться.","twofa.title":"ДВОФАКТОРНИЙ ВХІД (2FA)","twofa.hint":"Додай секрет в Authenticator (Google Authenticator, Aegis, 1Password), потім введи 6-значний код.","twofa.enable":"Увімкнути 2FA","twofa.disable":"Вимкнути 2FA","twofa.setup":"Згенерувати новий секрет","twofa.refresh":"Оновити","twofa.note":"2FA працює разом із паролем входу. Пристрій, який уже увійшов, залишається в системі до виходу.","pw.new8":"Новий пароль (мін. 8)",
    "pw.enable":"Увімкнути пароль","pw.disable":"Вимкнути пароль",
    "pw.statusOn":"Пароль увімкнено","pw.statusOff":"Без пароля",
    "pw.enabledToast":"Пароль увімкнено. Перезавантажте сторінку і увійдіть.",
    "pw.disabledToast":"Пароль вимкнено","pw.short":"Пароль має бути мінімум 8 символів",
    "pw.mismatch":"Паролі не співпадають",
    "pw.changed":"Пароль змінено. Перезавантажте сторінку і увійдіть.",
    "cur.title":"ВАЛЮТА","cur.rate":"КУРС (₴ за $1)","cur.refresh":"Оновити курс",
    "cur.save":"Зберегти","cur.updated":"оновлено","cur.manual":"вручну","cur.base":"база",
    "cur.baseToast":"USD — базова валюта (1.00)","cur.set":"Курс збережено",
    "cur.nbu":"Оновлюю курс з НБУ…","cur.nbuFail":"НБУ недоступний — введіть курс вручну",
    "cur.refreshed":"Курс:","nt.saved":"Сповіщення: увімкнено %s з 9",
    "diag.refresh":"Оновити","diag.loading":"Завантажую діагностику…",
    "diag.counts":"Записи","diag.tokens":"Токени","diag.version":"Версія",
    "diag.error":"Помилка діагностики:",
    "demo.loadConfirm":"Завантажити демо-дані? Поточні дані буде замінено.",
    "demo.loaded":"Демо-дані завантажено",
    "demo.clearConfirm":"Стерти всі дані? Це незворотно.","demo.cleared":"Дані стерто",
    "csv.importConfirm":"Імпортувати «%s»?\n\nПоточні дані буде збережено в gt_backups/ перед заміною.",
    "csv.imported":"Імпортовано: додано %s, пропущено %s","csv.empty":"Порожній файл",
    "mail.empty":"Поки порожньо. Сюди потрапляють нові замовлення й повідомлення, які трекер знайшов у пошті.",
    "mail.stat":"листів · нових","mail.clearConfirm":"Очистити всю чергу?\n\nВидалені замовлення більше не зявляться.",
    "mail.cleared":"Видалено:","mail.amountPrompt":"У листі немає суми. Введіть суму замовлення, $?",
    "mail.amountPositive":"Сума має бути більшою за 0",
    "mail.gamePrompt":"Гра (для статистики):\nнапр. Identity V, Zenless Zone Zero, Genshin",
    "mail.inStock":"На складі: %s — $%s\nСобівартість для обліку, $? (Enter = взяти зі складу)",
    "mail.costPrompt":"Скільки коштував цей акаунт (собівартість), $?\n0 — якщо купували не ви",
    "mail.added":"Додано в","mail.fromStock":"(зі складу)","mail.ignored":"Проігноровано","mail.removed":"Видалено",
    "deal.enterPrices":"Введи ціни!","deal.added":"Запис додано","deal.addedED":"Додано в Eldorado",
    "deal.updated":"Запис оновлено","deal.deleteConfirm":"Видалити цей запис?",
    "deal.bulkTitle":"Масове заповнення назв",
    "deal.bulkDesc":"Записи згруповані по сумі продажу. Введи назву — вона застосується до всіх записів з цією сумою без назви.",
    "deal.bulkPlaceholder":"Введи назву...","deal.bulkEmpty":"Немає записів без назви",
    "deal.bulkNeedName":"Нічого не змінено — введи хоча б одну назву",
    "deal.bulkDone":"Заповнено %s записів","deal.bulkNoTitles":"Всі записи вже мають назви!","deal.bulkFeeTitle":"Масова комісія","deal.bulkFeeDesc":"Застосується до поточного фільтра. Перерахує комісію, after-fee і чистий прибуток.","deal.bulkFeeHint":"0–100. Інші витрати не змінюються.","deal.bulkFeeCount":"угод у фільтрі","deal.bulkFeeConfirm":"Застосувати %s%% до %n угод?","deal.bulkFeeNeed":"Введи комісію 0–100%","deal.bulkFeeDone":"Оновлено %s угод",
    "deal.synced":"Синхронізовано %s записів","deal.syncError":"Помилка синхронізації:",
    "deal.csvDone":"CSV завантажено","deal.excelDone":"Excel завантажено! 4 аркуші",
    "deal.clearConfirm":"Очистити всі записи?",
    "deal.recalcPurchase":"Підставлено закупівлю $%s з P&L",
    "ed.editTitle":"Редагувати запис ELDORADO","ed.category":"Категорія",
    "ed.profitHint":"Прибуток рахується сам: продав − комісія − купив",
    "ed.deleteConfirm":"Видалити цей запис Eldorado?","ed.csvDone":"CSV ELDORADO завантажено",
    "lot.title":"КАЛЬКУЛЯТОР ЦІНИ","lot.name":"НАЗВА ТОВАРУ","lot.buy":"ЗАКУПІВЛЯ ($)",
    "lot.markup":"НАЦІНКА %","lot.sell":"ПРОДАЖ ($)","lot.gameSource":"ГРА / ДЖЕРЕЛО",
    "lot.desc":"ОПИС","lot.afterFee":"Після комісії:","lot.copy":"КОПІЮВАТИ ДЛЯ ЛОТУ",
    "lot.copied":"Скопійовано для лоту!","lot.enterName":"Введи назву",
    "lot.clipboard":"Буфер обміну недоступний",
    "onb.hint":"Мову й валюту можна змінити пізніше в ⚙ Налаштування",
    "set.whatToSend":"Що надсилати в Telegram (кожен тип окремо):",
    "set.notifySave":"Зберегти сповіщення","set.chatId":"CHAT ID",
    "set.gmail":"GMAIL","set.appPass":"APP PASSWORD","set.selfSigned":"Згенерувати self-signed",
    "set.cert":"CERT (pem/crt)","set.key":"KEY (pem/key)","set.https":"HTTPS",
    "set.watchdogSite":"⚠️ Watchdog сайту","set.watchdogAgent":"⚠️ Watchdog агента Taobao"
  },
  en: {
    "all":"All","total":"TOTAL","loading":"Loading…","noData":"No data",
    "save":"Save","close":"Close","copy":"Copy","delete":"Delete","edit":"Edit","show":"Show",
    "refresh":"Refresh","cancel":"Cancel","apply":"Apply","disconnect":"Disconnect",
    "inv.costShort":"Cost","inv.status":"Status","inv.inStockShort":"in stock",
    "inv.soldShort":"sold","inv.offShort":"written off","inv.sourceShort":"Source",
    "inv.empty":"Empty — add your first purchase","inv.dead":"Dead stock",
    "inv.noDead":"No dead stock","inv.oldest":"oldest item",
    "inv.added":"Added to stock","inv.soldToast":"Marked as sold","inv.offToast":"Written off",
    "inv.returnToast":"Returned to stock","inv.deleted":"Deleted",
    "inv.deleteConfirm":"Delete this stock item?","inv.noAccount":"(no data)","inv.enterName":"Enter a name",
    "an.deals":"Deals","an.revenue":"Revenue","an.profit":"Profit","an.margin":"Margin","an.platforms":"PROFIT BY PLATFORM","an.platform":"PLATFORM","an.feeCol":"FEES","an.expenseCol":"EXPENSES","an.netCol":"NET","an.netPct":"NET %",
    "an.games":"Different games","an.best":"Best","an.total":"TOTAL P&L + ELD",
    "an.totalIn":"Total in","an.game":"GAME","an.dealsCol":"DEALS","an.revenueCol":"REVENUE",
    "an.profitCol":"PROFIT","an.marginCol":"MARGIN",
    "an.thisVsLast":"THIS MONTH VS LAST","an.profitPL":"Profit P&L","an.revenuePL":"Revenue P&L",
    "an.profitED":"Profit ELDORADO","an.totalProfit":"Total profit","an.was":"was","an.new":"new",
    "an.revenueChart":"Revenue","an.profitChart":"Profit","an.noData":"No data",
    "rep.count":"Sales","rep.revenue":"Revenue","rep.fees":"Fees",
    "rep.cogs":"Cost of goods sold","rep.profit":"Profit","rep.purchases":"Purchases this month",
    "rep.cash":"Cash flow","rep.stock":"In stock now",
    "rep.formula":"Profit = revenue − fees − cost of goods sold. Cash flow = revenue − fees − purchases this month.",
    "rep.calculating":"Calculating…",
    "sup.noSuppliers":"No suppliers yet — add one in ⚙ → Suppliers",
    "sup.none":"Nothing found","sup.empty":"Database is empty — press ↺ or wait for refresh",
    "sup.sale":"SALE","sup.availYes":"in stock","sup.availNo":"out of stock","sup.gone":"gone",
    "sup.compareTitle":"Price comparison","sup.compareBase":"Base",
    "sup.compareFound":"Similar products in other shops","sup.compareNone":"No similar products found",
    "sup.historyTitle":"Price history",
    "sup.historyEmpty":"No history yet. It appears after price changes (catalog refreshes once a day).",
    "sup.notFound":"Product not found","sup.added":"Supplier added",
    "sup.enterName":"Enter shop name and URL","sup.badUrl":"URL must start with http:// or https://",
    "plan.supplier":"Supplier","plan.yourSale":"Your sale","plan.margin":"Margin",
    "plan.demand":"Demand","plan.sales":"sales",
    "tb.type":"TYPE","tb.lastRuns":"Last runs","tb.cartEmpty":"Cart is empty — press 🛒 next to a lot to add it",
    "tb.cart":"Cart","tb.lotOne":"lot","tb.lotMany":"lots",
    "tb.cardWithMiddleman":"card + middleman","tb.clear":"Clear",
    "tb.fromSupplier":"at supplier from",
    "tb.notChecked":"Not checked yet. Press «💳 Check payment» — sign in to Taobao in the browser window.",
    "tb.added":"Lot added","tb.pricePositive":"Price must be > 0",
    "tb.manualLink":"Taobao lot link (item.taobao.com/item.htm?id=…)",
    "tb.manualTitle":"Lot title (short)","tb.manualPrice":"Price in CNY (¥)",
    "tb.cardQuestion":"Is card payment available for this lot?",
    "tb.optionsQuestion":"How many account variants? (0 — unknown)",
    "tb.markedCard":"Card payment marked","tb.cardRemoved":"Card mark removed",
    "tb.options":"Variants",
    "tb.clearCartConfirm":"Clear cart (remove 🛒 marks from all lots)?",
    "tb.checkConfirm":"Check card payment and account variants for top 25 lots?\n\nThe collector will open each lot in a browser (~2 min). Taobao sign-in required.",
    "tb.collectConfirm":"Start Taobao collection now?\n\nIf the browser window is closed, the agent will open it (start_cf_debug.bat). Sign in to Taobao and pass the captcha; collection starts automatically.",
    "tb.collectCooldown":"Collection ran %s min ago (3 h cooldown). Start anyway?",
    "tb.collectRequested":"Request sent",
    "bk.typePL":"P&L","bk.typeED":"ELDORADO","bk.typeGoal":"Goal",
    "bk.typeSettings":"Settings","bk.typeMail":"Mail","bk.typeInventory":"Inventory",
    "bk.typeArchive":"Archive","bk.typeOther":"Other","bk.restore":"Restore",
    "bk.notRestorable":"—","bk.none":"No backups yet",
    "bk.restoreConfirm":"Restore «%s»?\n\nThe current version will be saved as …_before_restore_….json",
    "bk.restored":"Restored","bk.saved":"Backup saved! Files:","bk.error":"Backup error:",
    "pw.optional":"PASSWORD (OPTIONAL)","audit.title":"ACTION LOG","audit.hint":"Recent changes to deals, fees, stock and settings. Secrets and passwords are never written.","twofa.title":"TWO-FACTOR LOGIN (2FA)","twofa.hint":"Add the secret to an authenticator (Google Authenticator, Aegis, 1Password), then enter the 6-digit code.","twofa.enable":"Enable 2FA","twofa.disable":"Disable 2FA","twofa.setup":"Generate a new secret","twofa.refresh":"Refresh","twofa.note":"2FA works together with the login password. A device that is already signed in stays signed in until logout.","pw.new8":"New password (min 8)",
    "pw.enable":"Enable password","pw.disable":"Disable password",
    "pw.statusOn":"Password enabled","pw.statusOff":"No password",
    "pw.enabledToast":"Password enabled. Reload and sign in.",
    "pw.disabledToast":"Password disabled","pw.short":"Password must be at least 8 characters",
    "pw.mismatch":"Passwords do not match",
    "pw.changed":"Password changed. Reload and sign in.",
    "cur.title":"CURRENCY","cur.rate":"RATE ($ per $1)","cur.refresh":"Refresh rate",
    "cur.save":"Save","cur.updated":"updated","cur.manual":"manual","cur.base":"base",
    "cur.baseToast":"USD is the base currency (1.00)","cur.set":"Rate saved",
    "cur.nbu":"Updating rate from NBU…","cur.nbuFail":"NBU unavailable — enter rate manually",
    "cur.refreshed":"Rate:","nt.saved":"Notifications: %s of 9 enabled",
    "diag.refresh":"Refresh","diag.loading":"Loading diagnostics…",
    "diag.counts":"Records","diag.tokens":"Tokens","diag.version":"Version",
    "diag.error":"Diagnostics error:",
    "demo.loadConfirm":"Load demo data? Current data will be replaced.",
    "demo.loaded":"Demo data loaded",
    "demo.clearConfirm":"Erase all data? This cannot be undone.","demo.cleared":"Data erased",
    "csv.importConfirm":"Import «%s»?\n\nCurrent data will be saved to gt_backups/ before replacing.",
    "csv.imported":"Imported: added %s, skipped %s","csv.empty":"Empty file",
    "mail.empty":"Empty for now. New orders and messages that the tracker found in mail land here.",
    "mail.stat":"emails · new","mail.clearConfirm":"Clear the whole queue?\n\nDeleted orders will not come back.",
    "mail.cleared":"Removed:","mail.amountPrompt":"No amount in the email. Enter order amount, $?",
    "mail.amountPositive":"Amount must be greater than 0",
    "mail.gamePrompt":"Game (for stats):\ne.g. Identity V, Zenless Zone Zero, Genshin",
    "mail.inStock":"In stock: %s — $%s\nCost for accounting, $? (Enter = take from stock)",
    "mail.costPrompt":"How much did this account cost? $?\n0 — if you did not buy it",
    "mail.added":"Added to","mail.fromStock":"(from stock)","mail.ignored":"Ignored","mail.removed":"Deleted",
    "deal.enterPrices":"Enter prices!","deal.added":"Record added","deal.addedED":"Added to Eldorado",
    "deal.updated":"Record updated","deal.deleteConfirm":"Delete this record?",
    "deal.bulkTitle":"Bulk rename",
    "deal.bulkDesc":"Records are grouped by sale amount. Enter a name — it will be applied to all records with that amount without a name.",
    "deal.bulkPlaceholder":"Enter a name...","deal.bulkEmpty":"No records without a name",
    "deal.bulkNeedName":"Nothing changed — enter at least one name",
    "deal.bulkDone":"Filled %s records","deal.bulkNoTitles":"All records already have names!","deal.bulkFeeTitle":"Bulk commission","deal.bulkFeeDesc":"Applies to the current filter. Recalculates fee, after-fee and net profit.","deal.bulkFeeHint":"0–100. Other expenses are not changed.","deal.bulkFeeCount":"deals in filter","deal.bulkFeeConfirm":"Apply %s%% to %n deals?","deal.bulkFeeNeed":"Enter a commission from 0 to 100%","deal.bulkFeeDone":"Updated %s deals",
    "deal.synced":"Synced %s records","deal.syncError":"Sync error:",
    "deal.csvDone":"CSV downloaded","deal.excelDone":"Excel downloaded: 4 sheets",
    "deal.clearConfirm":"Clear all records?",
    "deal.recalcPurchase":"Purchase price $%s filled from P&L",
    "ed.editTitle":"Edit ELDORADO record","ed.category":"Category",
    "ed.profitHint":"Profit is calculated automatically: sold − fee − bought",
    "ed.deleteConfirm":"Delete this Eldorado record?","ed.csvDone":"ELDORADO CSV downloaded",
    "lot.title":"PRICE CALCULATOR","lot.name":"PRODUCT NAME","lot.buy":"PURCHASE ($)",
    "lot.markup":"MARKUP %","lot.sell":"SALE ($)","lot.gameSource":"GAME / SOURCE",
    "lot.desc":"DESCRIPTION","lot.afterFee":"After fee:","lot.copy":"COPY FOR LOT",
    "lot.copied":"Copied for lot!","lot.enterName":"Enter a name",
    "lot.clipboard":"Clipboard unavailable",
    "onb.hint":"You can change language and currency later in ⚙ Settings",
    "set.whatToSend":"What to send to Telegram (each type separately):",
    "set.notifySave":"Save notifications","set.chatId":"CHAT ID",
    "set.gmail":"GMAIL","set.appPass":"APP PASSWORD","set.selfSigned":"Generate self-signed",
    "set.cert":"CERT (pem/crt)","set.key":"KEY (pem/key)","set.https":"HTTPS",
    "set.watchdogSite":"⚠️ Site watchdog","set.watchdogAgent":"⚠️ Taobao agent watchdog"
  },
  ru: {
    "all":"Все","total":"ВСЕГО","loading":"Загрузка…","noData":"Нет данных",
    "save":"Сохранить","close":"Закрыть","copy":"Копировать","delete":"Удалить","edit":"Редактировать",
    "show":"Показать","refresh":"Обновить","cancel":"Отмена","apply":"Применить","disconnect":"Отключить",
    "inv.costShort":"Себестоимость","inv.status":"Статус","inv.inStockShort":"на складе",
    "inv.soldShort":"продан","inv.offShort":"списан","inv.sourceShort":"Источник",
    "inv.empty":"Пусто — добавьте первую закупку","inv.dead":"Мёртвый склад",
    "inv.noDead":"Мёртвого склада нет","inv.oldest":"самая старая позиция",
    "inv.added":"Добавлено на склад","inv.soldToast":"Отмечено как продан",
    "inv.offToast":"Списано","inv.returnToast":"Возвращено на склад","inv.deleted":"Удалено",
    "inv.deleteConfirm":"Удалить запись со склада?","inv.noAccount":"(данных нет)",
    "inv.enterName":"Введите название",
    "an.deals":"Сделок","an.revenue":"Выручка","an.profit":"Прибыль","an.margin":"Маржа","an.platforms":"ПРИБЫЛЬ ПО ПЛАТФОРМАМ","an.platform":"ПЛАТФОРМА","an.feeCol":"КОМИССИИ","an.expenseCol":"РАСХОДЫ","an.netCol":"ЧИСТАЯ","an.netPct":"NET %",
    "an.games":"Разных игр","an.best":"Лучшая","an.total":"ИТОГО P&L + ELD",
    "an.totalIn":"Итого в","an.game":"ИГРА","an.dealsCol":"СДЕЛОК","an.revenueCol":"ВЫРУЧКА",
    "an.profitCol":"ПРИБЫЛЬ","an.marginCol":"МАРЖА",
    "an.thisVsLast":"ЭТОТ МЕСЯЦ ПРОТИВ ПРОШЛОГО","an.profitPL":"Прибыль P&L",
    "an.revenuePL":"Выручка P&L","an.profitED":"Прибыль ELDORADO",
    "an.totalProfit":"Итого прибыль","an.was":"было","an.new":"новый",
    "an.revenueChart":"Выручка","an.profitChart":"Прибыль","an.noData":"Нет данных",
    "rep.count":"Продаж","rep.revenue":"Выручка","rep.fees":"Комиссии",
    "rep.cogs":"Себестоимость проданного","rep.profit":"Прибыль",
    "rep.purchases":"Закупки за месяц","rep.cash":"Денежный поток",
    "rep.stock":"На складе сейчас",
    "rep.formula":"Прибыль = выручка − комиссии − себестоимость проданного. Денежный поток = выручка − комиссии − закупки за месяц.",
    "rep.calculating":"Считаю…",
    "sup.noSuppliers":"Пока нет поставщиков — добавьте в ⚙ → Поставщики",
    "sup.none":"Ничего не найдено","sup.empty":"База пуста — нажми ↺ или подожди обновления",
    "sup.sale":"СКИДКА","sup.availYes":"в наличии","sup.availNo":"нет в наличии","sup.gone":"исчез",
    "sup.compareTitle":"Сравнение цен","sup.compareBase":"Базовый",
    "sup.compareFound":"Похожие товары в других магазинах","sup.compareNone":"Похожих товаров не найдено",
    "sup.historyTitle":"История цены",
    "sup.historyEmpty":"Истории ещё нет. Она появляется после изменения цены (каталог обновляется раз в сутки).",
    "sup.notFound":"Товар не найден","sup.added":"Поставщик добавлен",
    "sup.enterName":"Введите название магазина и URL",
    "sup.badUrl":"URL должен начинаться с http:// или https://",
    "plan.supplier":"Поставщик","plan.yourSale":"Ваша продажа","plan.margin":"Маржа",
    "plan.demand":"Спрос","plan.sales":"продаж",
    "tb.type":"ТИП","tb.lastRuns":"Последние сборы","tb.cartEmpty":"Корзина пуста — нажмите 🛒 у лота, чтобы добавить",
    "tb.cart":"Корзина","tb.lotOne":"лот","tb.lotMany":"лотов",
    "tb.cardWithMiddleman":"на карте с посредником","tb.clear":"Очистить",
    "tb.fromSupplier":"у поставщика от",
    "tb.notChecked":"Ещё не проверяли. Нажмите «💳 Проверить оплату» — нужен вход в Taobao в окне браузера.",
    "tb.added":"Лот добавлен","tb.pricePositive":"Цена должна быть > 0",
    "tb.manualLink":"Ссылка на лот Taobao (item.taobao.com/item.htm?id=…)",
    "tb.manualTitle":"Название лота (кратко)","tb.manualPrice":"Цена в юанях (¥)",
    "tb.cardQuestion":"Оплата картой доступна в этом лоте?",
    "tb.optionsQuestion":"Сколько вариантов аккаунтов в лоте? (0 — неизвестно)",
    "tb.markedCard":"Отмечено: оплата картой","tb.cardRemoved":"Метка снята",
    "tb.options":"Вариантов",
    "tb.clearCartConfirm":"Очистить корзину (снять метки 🛒 со всех лотов)?",
    "tb.checkConfirm":"Проверить оплату картой и количество вариантов у топ-25 лотов?\n\nКоллектор откроет каждый лот в браузере (~2 мин). Нужен вход в Taobao.",
    "tb.collectConfirm":"Запустить сбор с Taobao сейчас?\n\nЕсли окно браузера закрыто — агент откроет его сам (start_cf_debug.bat). Войдите в Taobao и пройдите капчу, сбор начнётся автоматически.",
    "tb.collectCooldown":"Сбор уже был %s мин назад (кулдаун 3 ч). Всё равно запустить сейчас?",
    "tb.collectRequested":"Запрос отправлен",
    "bk.typePL":"P&L","bk.typeED":"ELDORADO","bk.typeGoal":"Цель",
    "bk.typeSettings":"Настройки","bk.typeMail":"Почта","bk.typeInventory":"Склад",
    "bk.typeArchive":"Архив","bk.typeOther":"Другое","bk.restore":"Восстановить",
    "bk.notRestorable":"—","bk.none":"Бэкапов ещё нет",
    "bk.restoreConfirm":"Восстановить «%s»?\n\nТекущая версия будет сохранена как …_before_restore_….json",
    "bk.restored":"Восстановлено","bk.saved":"Бэкап сохранён! Файлов:","bk.error":"Ошибка бэкапа:",
    "pw.optional":"ПАРОЛЬ (ОПЦИОНАЛЬНО)","audit.title":"ЖУРНАЛ ДЕЙСТВИЙ","audit.hint":"Последние изменения сделок, комиссий, склада и настроек. Секреты и пароли не пишутся.","twofa.title":"ДВУХФАКТОРНЫЙ ВХОД (2FA)","twofa.hint":"Добавь секрет в Authenticator (Google Authenticator, Aegis, 1Password), затем введи 6-значный код.","twofa.enable":"Включить 2FA","twofa.disable":"Выключить 2FA","twofa.setup":"Сгенерировать новый секрет","twofa.refresh":"Обновить","twofa.note":"2FA работает вместе с паролем входа. Устройство, которое уже вошло, остаётся в системе до выхода.","pw.new8":"Новый пароль (мин. 8)",
    "pw.enable":"Включить пароль","pw.disable":"Отключить пароль",
    "pw.statusOn":"Пароль включён","pw.statusOff":"Без пароля",
    "pw.enabledToast":"Пароль включён. Перезагрузите страницу и войдите.",
    "pw.disabledToast":"Пароль отключён","pw.short":"Пароль должен быть минимум 8 символов",
    "pw.mismatch":"Пароли не совпадают",
    "pw.changed":"Пароль изменён. Перезагрузите страницу и войдите.",
    "cur.title":"ВАЛЮТА","cur.rate":"КУРС (₴ за $1)","cur.refresh":"Обновить курс",
    "cur.save":"Сохранить","cur.updated":"обновлено","cur.manual":"вручную","cur.base":"база",
    "cur.baseToast":"USD — базовая валюта (1.00)","cur.set":"Курс сохранён",
    "cur.nbu":"Обновляю курс из НБУ…","cur.nbuFail":"НБУ недоступен — введите курс вручную",
    "cur.refreshed":"Курс:","nt.saved":"Уведомления: включено %s из 9",
    "diag.refresh":"Обновить","diag.loading":"Загружаю диагностику…",
    "diag.counts":"Записи","diag.tokens":"Токены","diag.version":"Версия",
    "diag.error":"Ошибка диагностики:",
    "demo.loadConfirm":"Загрузить демо-данные? Текущие данные будут заменены.",
    "demo.loaded":"Демо-данные загружены",
    "demo.clearConfirm":"Стереть все данные? Это необратимо.","demo.cleared":"Данные стёрты",
    "csv.importConfirm":"Импортировать «%s»?\n\nТекущие данные будут сохранены в gt_backups/ перед заменой.",
    "csv.imported":"Импортировано: добавлено %s, пропущено %s","csv.empty":"Пустой файл",
    "mail.empty":"Пока пусто. Сюда попадают новые заказы и сообщения, которые трекер нашёл в почте.",
    "mail.stat":"писем · новых","mail.clearConfirm":"Очистить всю очередь?\n\nУдалённые заказы больше не появятся.",
    "mail.cleared":"Удалено:","mail.amountPrompt":"В письме нет суммы. Введите сумму заказа, $?",
    "mail.amountPositive":"Сумма должна быть больше 0",
    "mail.gamePrompt":"Игра (для статистики):\nнапр. Identity V, Zenless Zone Zero, Genshin",
    "mail.inStock":"На складе: %s — $%s\nСебестоимость для учёта, $? (Enter = взять со склада)",
    "mail.costPrompt":"Сколько стоил этот аккаунт (себестоимость), $?\n0 — если покупали не вы",
    "mail.added":"Добавлено в","mail.fromStock":"(со склада)","mail.ignored":"Проигнорировано","mail.removed":"Удалено",
    "deal.enterPrices":"Введи цены!","deal.added":"Запись добавлена","deal.addedED":"Добавлено в Eldorado",
    "deal.updated":"Запись обновлена","deal.deleteConfirm":"Удалить эту запись?",
    "deal.bulkTitle":"Массовое заполнение названий",
    "deal.bulkDesc":"Записи сгруппированы по сумме продажи. Введи название — оно применится ко всем записям с этой суммой без названия.",
    "deal.bulkPlaceholder":"Введи название...","deal.bulkEmpty":"Нет записей без названия",
    "deal.bulkNeedName":"Ничего не изменено — введи хотя бы одно название",
    "deal.bulkDone":"Заполнено %s записей","deal.bulkNoTitles":"Все записи уже имеют названия!","deal.bulkFeeTitle":"Массовая комиссия","deal.bulkFeeDesc":"Применяется к текущему фильтру. Пересчитывает комиссию, after-fee и чистую прибыль.","deal.bulkFeeHint":"0–100. Другие расходы не меняются.","deal.bulkFeeCount":"сделок в фильтре","deal.bulkFeeConfirm":"Применить %s%% к %n сделкам?","deal.bulkFeeNeed":"Введи комиссию 0–100%","deal.bulkFeeDone":"Обновлено %s сделок",
    "deal.synced":"Синхронизировано %s записей","deal.syncError":"Ошибка синхронизации:",
    "deal.csvDone":"CSV загружен","deal.excelDone":"Excel загружен! 4 листа",
    "deal.clearConfirm":"Очистить все записи?",
    "deal.recalcPurchase":"Подставлена закупка $%s из P&L",
    "ed.editTitle":"Редактировать запись ELDORADO","ed.category":"Категория",
    "ed.profitHint":"Прибыль считается сама: продал − комиссия − купил",
    "ed.deleteConfirm":"Удалить эту запись Eldorado?","ed.csvDone":"CSV ELDORADO загружен",
    "lot.title":"КАЛЬКУЛЯТОР ЦЕНЫ","lot.name":"НАЗВАНИЕ ТОВАРА","lot.buy":"ЗАКУПКА ($)",
    "lot.markup":"НАЦЕНКА %","lot.sell":"ПРОДАЖА ($)","lot.gameSource":"ИГРА / ИСТОЧНИК",
    "lot.desc":"ОПИСАНИЕ","lot.afterFee":"После комиссии:","lot.copy":"КОПИРОВАТЬ ДЛЯ ЛОТА",
    "lot.copied":"Скопировано для лота!","lot.enterName":"Введи название",
    "lot.clipboard":"Буфер обмена недоступен",
    "onb.hint":"Язык и валюту можно изменить позже в ⚙ Настройки",
    "set.whatToSend":"Что отправлять в Telegram (каждый тип отдельно):",
    "set.notifySave":"Сохранить уведомления","set.chatId":"CHAT ID",
    "set.gmail":"GMAIL","set.appPass":"APP PASSWORD","set.selfSigned":"Сгенерировать self-signed",
    "set.cert":"CERT (pem/crt)","set.key":"KEY (pem/key)","set.https":"HTTPS",
    "set.watchdogSite":"⚠️ Watchdog сайта","set.watchdogAgent":"⚠️ Watchdog агента Taobao"
  }
};
Object.keys(EXTRA_I18N).forEach(function(l){ Object.assign(I18N[l], EXTRA_I18N[l]); });
const EXTRA_I18N2 = {
  uk: {"set.telegramSaved":"✅ Telegram збережено","set.cloudSaved":"✅ Папку хмари збережено",
       "set.gmailOk":"✅ Gmail підключено — сповіщення активні",
       "set.httpsSaved":"✅ HTTPS-налаштування збережено. Перезапусти трекер.",
       "set.certCreated":"🔑 Сертифікат створено. Натисни «Зберегти» і перезапусти.",
       "set.gmailNeed":"⚠ Введи Gmail-адресу","set.gmailBad":"⚠ Невірна Gmail-адреса",
       "set.cookieNeed":"⚠ Вставте хоча б один cookie","set.telegramDisconnect":"Відключити Telegram",
       "set.gmailDisconnect":"Відключити Gmail","set.cookieDisconnect":"Відключити cookie"},
  en: {"set.telegramSaved":"✅ Telegram saved","set.cloudSaved":"✅ Cloud folder saved",
       "set.gmailOk":"✅ Gmail connected — notifications active",
       "set.httpsSaved":"✅ HTTPS settings saved. Restart the tracker.",
       "set.certCreated":"🔑 Certificate created. Press “Save” and restart.",
       "set.gmailNeed":"⚠ Enter a Gmail address","set.gmailBad":"⚠ Invalid Gmail address",
       "set.cookieNeed":"⚠ Paste at least one cookie","set.telegramDisconnect":"Disconnect Telegram",
       "set.gmailDisconnect":"Disconnect Gmail","set.cookieDisconnect":"Disconnect cookies"},
  ru: {"set.telegramSaved":"✅ Telegram сохранён","set.cloudSaved":"✅ Папка облака сохранена",
       "set.gmailOk":"✅ Gmail подключён — уведомления активны",
       "set.httpsSaved":"✅ Настройки HTTPS сохранены. Перезапусти трекер.",
       "set.certCreated":"🔑 Сертификат создан. Нажми «Сохранить» и перезапусти.",
       "set.gmailNeed":"⚠ Введи Gmail-адрес","set.gmailBad":"⚠ Неверный Gmail-адрес",
       "set.cookieNeed":"⚠ Вставь хотя бы один cookie","set.telegramDisconnect":"Отключить Telegram",
       "set.gmailDisconnect":"Отключить Gmail","set.cookieDisconnect":"Отключить cookie"}
};
Object.keys(EXTRA_I18N2).forEach(function(l){ Object.assign(I18N[l], EXTRA_I18N2[l]); });
const EXTRA_I18N3 = {
  uk: {"set.test":"Тест","set.checkNow":"Перевірити зараз","set.botToken":"ТОКЕН БОТА",
       "set.folder":"ПАПКА","set.gmailLabel":"GMAIL","set.appPass":"APP PASSWORD",
       "set.cloudHint":"Копія бекапів у OneDrive (або будь-яка папка). Порожнє поле = авто: OneDrive/GameTrackerBackups.",
       "nt.order":"💰 Продажі (замовлення)","nt.message":"💬 Повідомлення покупців",
       "nt.watchdog":"⚠️ Watchdog сайту","nt.agent":"⚠️ Watchdog агента Taobao",
       "nt.digest":"📊 Дайджест (20:00)","nt.new":"🆕 Нові акаунти",
       "nt.price":"💸 Падіння цін","nt.restock":"🔄 Ресток","nt.deal":"🔥 Вигідні лоти Taobao","nt.deadstock":"🧊 Мертвий склад (30+ днів)"},
  en: {"set.test":"Test","set.checkNow":"Check now","set.botToken":"BOT TOKEN",
       "set.folder":"FOLDER","set.gmailLabel":"GMAIL","set.appPass":"APP PASSWORD",
       "set.cloudHint":"Copy backups to OneDrive (or any folder). Empty field = auto: OneDrive/GameTrackerBackups.",
       "nt.order":"💰 Sales (orders)","nt.message":"💬 Buyer messages",
       "nt.watchdog":"⚠️ Site watchdog","nt.agent":"⚠️ Taobao agent watchdog",
       "nt.digest":"📊 Digest (20:00)","nt.new":"🆕 New accounts",
       "nt.price":"💸 Price drops","nt.restock":"🔄 Restock","nt.deal":"🔥 Profitable Taobao lots","nt.deadstock":"🧊 Dead stock (30+ days)"},
  ru: {"set.test":"Тест","set.checkNow":"Проверить сейчас","set.botToken":"ТОКЕН БОТА",
       "set.folder":"ПАПКА","set.gmailLabel":"GMAIL","set.appPass":"APP PASSWORD",
       "set.cloudHint":"Копия бэкапов в OneDrive (или любая папка). Пустое поле = авто: OneDrive/GameTrackerBackups.",
       "nt.order":"💰 Продажи (заказы)","nt.message":"💬 Сообщения покупателей",
       "nt.watchdog":"⚠️ Watchdog сайта","nt.agent":"⚠️ Watchdog агента Taobao",
       "nt.digest":"📊 Дайджест (20:00)","nt.new":"🆕 Новые аккаунты",
       "nt.price":"💸 Падение цен","nt.restock":"🔄 Ресток","nt.deal":"🔥 Выгодные лоты Taobao","nt.deadstock":"🧊 Мертвый склад (30+ дней)"}
};
Object.keys(EXTRA_I18N3).forEach(function(l){ Object.assign(I18N[l], EXTRA_I18N3[l]); });
I18N.uk['ph.pw6'] = 'мін. 8 символів';
I18N.en['ph.pw6'] = 'min. 8 chars';
I18N.ru['ph.pw6'] = 'мин. 8 символов';
I18N.uk['cf.saleFirst'] = 'Спочатку зі знижкою';
I18N.ru['cf.saleFirst'] = 'Сначала со скидкой';
I18N.uk['ch.cookieHelp'] = 'Chrome/Edge: F12 → Application → Cookies → funpay.com → скопіюйте значення golden_key. Зберігається лише на сервері. Без FunPay-cookie замовлення з FunPay не надходять.';
I18N.en['ch.cookieHelp'] = 'Chrome/Edge: F12 → Application → Cookies → funpay.com → copy the golden_key value. Stored on the server only. Without a FunPay cookie, FunPay orders do not arrive.';
I18N.ru['ch.cookieHelp'] = 'Chrome/Edge: F12 → Application → Cookie → funpay.com → скопируйте значение golden_key. Хранится только на сервере. Без FunPay-cookie заказы с FunPay не поступают.';
I18N.uk['set.appPass'] = 'ПАРОЛЬ ДОДАТКА';
I18N.ru['set.appPass'] = 'ПАРОЛЬ ПРИЛОЖЕНИЯ';
const PLURAL = {
  uk: {products:["товар","товари","товарів"],records:["запис","записи","записів"],
       sales:["продаж","продажі","продажів"],lots:["лот","лоти","лотів"],
       emails:["лист","листи","листів"]},
  en: {products:["product","products","products"],records:["record","records","records"],
       sales:["sale","sales","sales"],lots:["lot","lots","lots"],
       emails:["email","emails","emails"]},
  ru: {products:["товар","товара","товаров"],records:["запись","записи","записей"],
       sales:["продажа","продажи","продаж"],lots:["лот","лота","лотов"],
       emails:["письмо","письма","писем"]}
};

Object.assign(I18N.uk, {
  'aud.time':'Час','aud.action':'Дія','aud.details':'Деталі','aud.none':'Ще немає подій',
  'aud.e.settings_save':'Налаштування','aud.e.deals_save':'Угоди','aud.e.eldorado_save':'Eldorado',
  'aud.e.inventory_add':'Склад +','aud.e.inventory_status':'Статус складу','aud.e.inventory_delete':'Склад −',
  'aud.e.auth_login':'Вхід','aud.e.auth_logout_all':'Вихід з усіх пристроїв',
  'aud.e.2fa_setup':'2FA секрет','aud.e.2fa_enabled':'2FA увімкнено','aud.e.2fa_disabled':'2FA вимкнено',
  'aud.e.2fa_recovery':'Recovery-коди'
});
Object.assign(I18N.en, {
  'aud.time':'Time','aud.action':'Action','aud.details':'Details','aud.none':'No events yet',
  'aud.e.settings_save':'Settings','aud.e.deals_save':'Deals','aud.e.eldorado_save':'Eldorado',
  'aud.e.inventory_add':'Stock +','aud.e.inventory_status':'Stock status','aud.e.inventory_delete':'Stock −',
  'aud.e.auth_login':'Login','aud.e.auth_logout_all':'Logout all devices',
  'aud.e.2fa_setup':'2FA setup','aud.e.2fa_enabled':'2FA enabled','aud.e.2fa_disabled':'2FA disabled',
  'aud.e.2fa_recovery':'Recovery codes'
});
Object.assign(I18N.ru, {
  'aud.time':'Время','aud.action':'Действие','aud.details':'Детали','aud.none':'Пока нет событий',
  'aud.e.settings_save':'Настройки','aud.e.deals_save':'Сделки','aud.e.eldorado_save':'Eldorado',
  'aud.e.inventory_add':'Склад +','aud.e.inventory_status':'Статус склада','aud.e.inventory_delete':'Склад −',
  'aud.e.auth_login':'Вход','aud.e.auth_logout_all':'Выход со всех устройств',
  'aud.e.2fa_setup':'2FA секрет','aud.e.2fa_enabled':'2FA включена','aud.e.2fa_disabled':'2FA отключена',
  'aud.e.2fa_recovery':'Recovery-коды'
});

Object.assign(I18N.uk, {
  'sched.title':'Розклад і ліміти','sched.intro':'Це автоматичні інтервали Ledger: як часто оновлювати ціни, шукати новинки та коли надсилати звіт. Менший інтервал = свіжіші дані, але більше запитів і кредитів.',
  'sched.sup.label':'Оновлення каталогу','sched.sup.desc':'Як часто перевіряти ціни та наявність у постачальників. 6 год = 4 рази на добу.',
  'sched.news.label':'Пошук новинок','sched.news.desc':'Як часто шукати нові товари та зміни на сайтах. 1 год = щогодини.',
  'sched.credits.label':'Ліміт кредитів','sched.credits.desc':'Скільки кредитів ScraperAPI можна витратити за добу. Не користуєшся — не змінюй.',
  'sched.credits.unit':'кр./день','sched.digest.label':'Час дайджесту','sched.digest.desc':'Година, коли надсилати підсумок дня в Telegram (0–23).',
  'sched.deal.label':'Поріг вигідного лоту','sched.deal.desc':'У скільки разів ціна має бути нижчою за твою, щоб прийшов алерт. 5× = ціна ≤ 20% твоєї.',
  'sched.hours':'год','sched.hour':'год','sched.save':'Зберегти розклад','sched.hint':'Не впевнений? Залиш значення як є — це безпечні дефолти.'
});
Object.assign(I18N.en, {
  'sched.title':'Schedule & limits','sched.intro':'These are automatic intervals: how often Ledger refreshes prices, looks for new items and when it sends the digest. Lower interval = fresher data, but more requests and credits.',
  'sched.sup.label':'Catalog refresh','sched.sup.desc':'How often to check supplier prices and availability. 6 h = 4 times a day.',
  'sched.news.label':'New items scan','sched.news.desc':'How often to look for new products and site changes. 1 h = hourly.',
  'sched.credits.label':'Credit limit','sched.credits.desc':'ScraperAPI credits allowed per day. If you do not use it, leave unchanged.',
  'sched.credits.unit':'credits/day','sched.digest.label':'Digest time','sched.digest.desc':'Hour when the daily summary is sent to Telegram (0–23).',
  'sched.deal.label':'Good-deal threshold','sched.deal.desc':'How many times cheaper than your price a lot must be to trigger an alert. 5× = price ≤ 20% of yours.',
  'sched.hours':'h','sched.hour':'h','sched.save':'Save schedule','sched.hint':'Not sure? Leave the defaults — they are safe.'
});
Object.assign(I18N.ru, {
  'sched.title':'Расписание и лимиты','sched.intro':'Это автоматические интервалы Ledger: как часто обновлять цены, искать новинки и когда отправлять отчёт. Меньше интервал — свежее данные, но больше запросов и кредитов.',
  'sched.sup.label':'Обновление каталога','sched.sup.desc':'Как часто проверять цены и наличие у поставщиков. 6 ч = 4 раза в сутки.',
  'sched.news.label':'Поиск новинок','sched.news.desc':'Как часто искать новые товары и изменения на сайтах. 1 ч = каждый час.',
  'sched.credits.label':'Лимит кредитов','sched.credits.desc':'Сколько кредитов ScraperAPI можно потратить за сутки. Не пользуешься — не меняй.',
  'sched.credits.unit':'кр./день','sched.digest.label':'Время дайджеста','sched.digest.desc':'Час, когда отправлять итоги дня в Telegram (0–23).',
  'sched.deal.label':'Порог выгодного лота','sched.deal.desc':'Во сколько раз цена должна быть ниже твоей, чтобы пришёл алерт. 5× = цена ≤ 20% твоей.',
  'sched.hours':'ч','sched.hour':'ч','sched.save':'Сохранить расписание','sched.hint':'Не уверен? Оставь значения как есть — это безопасные дефолты.'
});
Object.assign(I18N.uk, {'cur.auto':'Курс оновлюється автоматично раз на 6 годин. Кнопка ↻ — примусове оновлення.','cur.manualHint':'Можна вибрати будь-яку валюту вручну. Після цього зміна мови не змінюватиме валюту.'});
Object.assign(I18N.en, {'cur.auto':'The rate refreshes automatically every 6 hours. The ↻ button refreshes it now.','cur.manualHint':'You can choose any currency manually. After that, changing the language will not change the currency.'});
Object.assign(I18N.ru, {'cur.auto':'Курс обновляется автоматически раз в 6 часов. Кнопка ↻ — принудительное обновление.','cur.manualHint':'Можно выбрать любую валюту вручную. После этого смена языка не будет менять валюту.'});
Object.assign(I18N.uk, {
  'tb.heroBadge':'АВТОМАТИЗАЦІЯ TAOBAO','tb.heroTitle':'Вигідні акаунти з Taobao — до того, як їх розкуплять',
  'tb.heroSub':'Ledger сам збирає лоти, показує ціну в юанях і доларах та одразу рахує маржу. Вам залишається вибрати найкращий лот і купити.',
  'tb.stat1':'Економія часу','tb.stat1u':'год/день','tb.stat2':'Ціни','tb.stat3':'Оновлення','tb.stat3v':'у фоні','tb.stat4':'Маржа','tb.stat4v':'відразу',
  'tb.ben1t':'Збір на автопілоті','tb.ben1d':'Агент відкриває Taobao, оновлює лоти й чекає, поки ви пройдете капчу. Без ручного копіювання.',
  'tb.ben2t':'Маржа видна одразу','tb.ben2d':'Ціна в юанях, орієнтовний долар, ваша ціна продажу й прибуток — в одному рядку.',
  'tb.ben3t':'Від лоту до угоди — один клік','tb.ben3d':'Сподобався лот? Додайте його в P&L, і він одразу потрапить в облік.',
  'tb.how':'Як працює агент і що потрібно','tb.learnMore':'Як це працює',
  'taobao.demoTitle':'ЯК ЦЕ ВИГЛЯДАЄ В РОБОТІ','taobao.demoBadge':'ДЕМО-ПРИКЛАД','taobao.demoNote':'Демо-приклад у USD: реальні лоти, ціни й маржа з’являться після запуску агента.',
  'taobao.buy':'Купити','taobao.sell':'Продати','taobao.margin':'Маржа','taobao.hot':'ТОП','taobao.new':'НОВЕ','taobao.value':'ВИГІДНО'
});
Object.assign(I18N.en, {
  'tb.heroBadge':'TAOBAO AUTOMATION','tb.heroTitle':'Find underpriced Taobao accounts before they’re gone',
  'tb.heroSub':'Ledger collects lots for you, shows yuan and dollar prices, and calculates margin on the spot. All you do is pick the best lot and buy.',
  'tb.stat1':'Time saved','tb.stat1u':'h/day','tb.stat2':'Prices','tb.stat3':'Refresh','tb.stat3v':'in background','tb.stat4':'Margin','tb.stat4v':'instantly',
  'tb.ben1t':'Collection on autopilot','tb.ben1d':'The agent opens Taobao, refreshes lots and waits while you solve the captcha. No manual copying.',
  'tb.ben2t':'Margin at a glance','tb.ben2d':'Yuan price, estimated dollars, your sale price and profit — all in one row.',
  'tb.ben3t':'From lot to deal in one click','tb.ben3d':'Like a lot? Add it to P&L and it becomes part of your ledger.',
  'tb.how':'How the agent works and what you need','tb.learnMore':'How it works',
  'taobao.demoTitle':'WHAT IT LOOKS LIKE IN USE','taobao.demoBadge':'DEMO','taobao.demoNote':'Demo example in USD. Real lots, prices and margin appear once the agent starts.',
  'taobao.buy':'Buy','taobao.sell':'Sell','taobao.margin':'Margin','taobao.hot':'HOT','taobao.new':'NEW','taobao.value':'VALUE'
});
Object.assign(I18N.ru, {
  'tb.heroBadge':'АВТОМАТИЗАЦИЯ TAOBAO','tb.heroTitle':'Выгодные аккаунты с Taobao — раньше, чем их разберут',
  'tb.heroSub':'Ledger сам собирает лоты, показывает цену в юанях и долларах и сразу считает маржу. Вам остаётся выбрать лучший лот и купить.',
  'tb.stat1':'Экономия времени','tb.stat1u':'ч/день','tb.stat2':'Цены','tb.stat3':'Обновление','tb.stat3v':'в фоне','tb.stat4':'Маржа','tb.stat4v':'сразу',
  'tb.ben1t':'Сбор на автопилоте','tb.ben1d':'Агент открывает Taobao, обновляет лоты и ждёт, пока вы пройдёте капчу. Без ручного копирования.',
  'tb.ben2t':'Маржа видна сразу','tb.ben2d':'Цена в юанях, примерный доллар, ваша цена продажи и прибыль — в одной строке.',
  'tb.ben3t':'От лота до сделки — один клик','tb.ben3d':'Понравился лот? Добавьте его в P&L, и он сразу попадёт в учёт.',
  'tb.how':'Как работает агент и что нужно','tb.learnMore':'Как это работает',
  'taobao.demoTitle':'КАК ЭТО ВЫГЛЯДИТ В РАБОТЕ','taobao.demoBadge':'ДЕМО-ПРИМЕР','taobao.demoNote':'Демо-пример в USD: реальные лоты, цены и маржа появятся после запуска агента.',
  'taobao.buy':'Купить','taobao.sell':'Продать','taobao.margin':'Маржа','taobao.hot':'ТОП','taobao.new':'НОВОЕ','taobao.value':'ВЫГОДНО'
});
Object.assign(I18N.uk, {
  'app.title':'ЗАСТОСУНОК','app.desc':'Встанови Ledger як застосунок на телефон або комп’ютер: іконка на робочому столі, повноекранний режим, швидший запуск.','app.install':'Встановити Ledger','app.hint':'Android/Chrome: кнопка вище або меню ⋮ → «Встановити застосунок». iPhone/Safari: «Поділитися» → «На екран Домівки».',
  'target.title':'ЦІЛЬОВІ ЦІНИ','target.hint':'Напиши назву гри/лота й максимальну ціну в доларах. Ledger перевіряє кеш постачальників і надсилає Telegram-алерт, коли ціна досягає порогу. Один рядок = одна ціль.','target.save':'Зберегти цілі','target.needPrice':'Потрібно увімкнути Telegram-сповіщення «Падіння цін».'
});
Object.assign(I18N.en, {
  'app.title':'APP','app.desc':'Install Ledger as an app on your phone or computer: desktop icon, full-screen mode, faster launch.','app.install':'Install Ledger','app.hint':'Android/Chrome: button above or menu ⋮ → Install app. iPhone/Safari: Share → Add to Home Screen.',
  'target.title':'TARGET PRICES','target.hint':'Write a game/lot name and the maximum price in USD. Ledger checks the supplier cache and sends a Telegram alert when the price reaches the target. One line = one target.','target.save':'Save targets','target.needPrice':'Enable Telegram notifications for "Price drops".'
});
Object.assign(I18N.ru, {
  'app.title':'ПРИЛОЖЕНИЕ','app.desc':'Установи Ledger как приложение на телефон или компьютер: иконка на рабочем столе, полноэкранный режим, быстрый запуск.','app.install':'Установить Ledger','app.hint':'Android/Chrome: кнопка выше или меню ⋮ → «Установить приложение». iPhone/Safari: «Поделиться» → «На экран Домой».',
  'target.title':'ЦЕЛЕВЫЕ ЦЕНЫ','target.hint':'Напиши название игры/лота и максимальную цену в долларах. Ledger проверяет кеш поставщиков и отправляет Telegram-алерт, когда цена достигает порога. Одна строка = одна цель.','target.save':'Сохранить цели','target.needPrice':'Нужно включить Telegram-уведомления «Падение цен».'
});
Object.assign(I18N.uk, {
  'an.mergedTitle':'ЗВЕДЕНО — ВСІ ЦИФРИ В ОДНОМУ МІСЦІ','an.merged':'P&L + ELDORADO — разом',
  'an.revenueDays':'ВИТОРГ ПО ДНЯХ (30 днів)','an.gamesTitle':'АНАЛІТИКА','an.byGames':'ПО ІГРАХ','an.byMonths':'ПО МІСЯЦЯХ','an.refresh':'Оновити',
  'pl.profit':'ПРИБУТОК','pl.revenue':'ВИРУЧКА','pl.cost':'ВКЛАДЕНО','pl.margin':'МАРЖА','pl.deals':'УГОД','pl.fees':'КОМІСІЇ',
  'cf.title':'CASHFLOW / ВИПЛАТИ','cf.hold':'Холд','cf.available':'Доступно','cf.withdrawn':'Виведено','cf.total':'Всього',
  'cf.date':'Дата','cf.platform':'Платформа','cf.amount':'Сума','cf.status':'Статус','cf.availableDate':'Доступно з','cf.note':'Коментар',
  'mp.marketplace':'МАЙДАНЧИК','mp.fee':'КОМІСІЯ','mp.net':'НА РУКИ','mp.profit':'ПРИБУТОК','mp.margin':'МАРЖА',
  'cf.add':'Додати','cf.payoutCsv':'Виплати CSV','cf.empty':'Немає записів. Додай Hold, Available або Withdrawn.',
  'cf.rules':'Правила payout (днів до Available)','cf.priority':'Дата в полі «Доступно з» має пріоритет.','cf.save':'Зберегти',
  'cf.deleteConfirm':'Видалити запис?','cf.amountRequired':'Введи суму','cf.invalidPrice':'Некоректна ціна',
  'imp.title':'ІМПОРТ ПРОДАЖІВ','imp.hint':'CSV з G2G / Gameflip / PlayerAuctions. Колонки: date, title/item, price/amount, fee (необов’язково), order id (необов’язково). Собівартість підтягується зі складу, якщо є збіг.',
  'imp.createHold':'створити Hold','imp.import':'Імпортувати','imp.emptyCsv':'CSV порожній','imp.noColumns':'Не знайдено колонок title/price',
  'imp.noRows':'Немає рядків з ціною','imp.foundCost':'знайдено собівартість','imp.imported':'Імпортовано','imp.skipped':'пропущено дублів',
  'imp.price':'Ціна','imp.fee':'Комісія','imp.cost':'Собівартість','imp.stock':'Склад','imp.titleCol':'Дата','imp.name':'Назва',
  'taobao.demoTitle':'ЯК ЦЕ ВИГЛЯДАЄ В РОБОТІ','taobao.demoBadge':'ДЕМО-ПРИКЛАД','taobao.demoNote':'Демо-приклад у USD: реальні лоти, ціни й маржа з’являться після запуску агента.',
  'roi.title':'ROI ПОСТАЧАЛЬНИКІВ','roi.hint':'Прибуток, ROI і sell-through по постачальниках — на основі складу та прив’язаних продажів.',
  'roi.empty':'Немає даних: додай товар на склад із постачальником.','roi.supplier':'Постачальник','roi.items':'Товари','roi.sold':'Продано',
  'roi.stock':'Склад','roi.cost':'Витрати','roi.revenue':'Виручка','roi.profit':'Прибуток','roi.roi':'ROI','roi.st':'ST%','roi.days':'Днів',
  'order.new':'Нове замовлення','order.open':'Відкрити','order.notify':'Сповіщення','order.clear':'Очистити всі','mail.desc':'Листи від FunPay / ZeusX / Eldorado, які трекер уже розпізнав. Нічого не додається автоматично: перенесіть одним кліком у ELDORADO або P&L, або проігноруйте.','order.enabled':'Увімкнено','order.blocked':'Заблоковано',
  'order.demo':'Демо','order.sound':'звук','order.testSound':'Перевірити звук','order.permissionDenied':'Сповіщення не дозволено',
  'order.granted':'Сповіщення увімкнено','order.demoCreated':'Демо-замовлення створено',
  'rep.title':'Місячний звіт','rep.tax':'Податок %','rep.show':'Показати','rep.choose':'Виберіть місяць','rep.deals':'Угоди за місяць','rep.cashTax':'Cashflow / податок','rep.taxBase':'Податкова база (net profit)','rep.taxRate':'Ставка податку','rep.taxEst':'Оцінка податку'
});
Object.assign(I18N.en, {
  'an.mergedTitle':'COMBINED — ALL NUMBERS IN ONE PLACE','an.merged':'P&L + ELDORADO — combined',
  'an.revenueDays':'REVENUE BY DAY (30 days)','an.gamesTitle':'ANALYTICS','an.byGames':'BY GAME','an.byMonths':'BY MONTH','an.refresh':'Refresh',
  'pl.profit':'PROFIT','pl.revenue':'REVENUE','pl.cost':'INVESTED','pl.margin':'MARGIN','pl.deals':'DEALS','pl.fees':'FEES',
  'cf.title':'CASHFLOW / PAYOUTS','cf.hold':'Hold','cf.available':'Available','cf.withdrawn':'Withdrawn','cf.total':'Total',
  'cf.date':'Date','cf.platform':'Platform','cf.amount':'Amount','cf.status':'Status','cf.availableDate':'Available from','cf.note':'Note',
  'mp.marketplace':'MARKETPLACE','mp.fee':'FEE','mp.net':'NET','mp.profit':'PROFIT','mp.margin':'MARGIN',
  'cf.add':'Add','cf.payoutCsv':'Payout CSV','cf.empty':'No entries. Add Hold, Available or Withdrawn.',
  'cf.rules':'Payout rules (days to Available)','cf.priority':'The date in "Available from" overrides the rule.','cf.save':'Save',
  'cf.deleteConfirm':'Delete this entry?','cf.amountRequired':'Enter an amount','cf.invalidPrice':'Invalid price',
  'imp.title':'SALES IMPORT','imp.hint':'CSV from G2G / Gameflip / PlayerAuctions. Columns: date, title/item, price/amount, fee (optional), order id (optional). Cost is matched from stock when possible.',
  'imp.createHold':'create Hold','imp.import':'Import','imp.emptyCsv':'CSV is empty','imp.noColumns':'No title/price columns found',
  'imp.noRows':'No rows with a price','imp.foundCost':'cost matched','imp.imported':'Imported','imp.skipped':'duplicates skipped',
  'imp.price':'Price','imp.fee':'Fee','imp.cost':'Cost','imp.stock':'Stock','imp.titleCol':'Date','imp.name':'Name',
  'taobao.demoTitle':'WHAT IT LOOKS LIKE IN USE','taobao.demoBadge':'DEMO','taobao.demoNote':'Demo example in USD. Real lots, prices and margin appear once the agent starts.',
  'roi.title':'SUPPLIER ROI','roi.hint':'Profit, ROI and sell-through by supplier, based on stock and linked sales.',
  'roi.empty':'No data: add stock with a supplier.','roi.supplier':'Supplier','roi.items':'Items','roi.sold':'Sold',
  'roi.stock':'Stock','roi.cost':'Cost','roi.revenue':'Revenue','roi.profit':'Profit','roi.roi':'ROI','roi.st':'ST%','roi.days':'Days',
  'order.new':'New order','order.open':'Open','order.notify':'Notifications','order.clear':'Clear all','mail.desc':'Emails from FunPay / ZeusX / Eldorado that the tracker recognized. Nothing is added automatically: move one to ELDORADO or P&L, or ignore it.','order.enabled':'Enabled','order.blocked':'Blocked',
  'order.demo':'Demo','order.sound':'sound','order.testSound':'Test sound','order.permissionDenied':'Notifications not allowed',
  'order.granted':'Notifications enabled','order.demoCreated':'Demo order created',
  'rep.title':'Monthly report','rep.tax':'Tax %','rep.show':'Show','rep.choose':'Choose a month','rep.deals':'Deals this month','rep.cashTax':'Cashflow / tax','rep.taxBase':'Tax base (net profit)','rep.taxRate':'Tax rate','rep.taxEst':'Estimated tax'
});
Object.assign(I18N.ru, {
  'an.mergedTitle':'СВЕДЕНО — ВСЕ ЦИФРЫ В ОДНОМ МЕСТЕ','an.merged':'P&L + ELDORADO — вместе',
  'an.revenueDays':'ВЫРУЧКА ПО ДНЯМ (30 дней)','an.gamesTitle':'АНАЛИТИКА','an.byGames':'ПО ИГРАМ','an.byMonths':'ПО МЕСЯЦАМ','an.refresh':'Обновить',
  'pl.profit':'ПРИБЫЛЬ','pl.revenue':'ВЫРУЧКА','pl.cost':'ВЛОЖЕНО','pl.margin':'МАРЖА','pl.deals':'СДЕЛОК','pl.fees':'КОМИССИИ',
  'cf.title':'CASHFLOW / ВЫПЛАТЫ','cf.hold':'Холд','cf.available':'Доступно','cf.withdrawn':'Выведено','cf.total':'Всего',
  'cf.date':'Дата','cf.platform':'Платформа','cf.amount':'Сумма','cf.status':'Статус','cf.availableDate':'Доступно с','cf.note':'Комментарий',
  'mp.marketplace':'ПЛОЩАДКА','mp.fee':'КОМИССИЯ','mp.net':'НА РУКИ','mp.profit':'ПРИБЫЛЬ','mp.margin':'МАРЖА',
  'cf.add':'Добавить','cf.payoutCsv':'Выплаты CSV','cf.empty':'Нет записей. Добавь Hold, Available или Withdrawn.',
  'cf.rules':'Правила payout (дней до Available)','cf.priority':'Дата в поле «Доступно с» имеет приоритет.','cf.save':'Сохранить',
  'cf.deleteConfirm':'Удалить запись?','cf.amountRequired':'Введи сумму','cf.invalidPrice':'Неверная цена',
  'imp.title':'ИМПОРТ ПРОДАЖ','imp.hint':'CSV из G2G / Gameflip / PlayerAuctions. Колонки: date, title/item, price/amount, fee (необязательно), order id (необязательно). Себестоимость подтягивается со склада при совпадении.',
  'imp.createHold':'создать Hold','imp.import':'Импортировать','imp.emptyCsv':'CSV пустой','imp.noColumns':'Не найдены колонки title/price',
  'imp.noRows':'Нет строк с ценой','imp.foundCost':'найдена себестоимость','imp.imported':'Импортировано','imp.skipped':'пропущено дублей',
  'imp.price':'Цена','imp.fee':'Комиссия','imp.cost':'Себестоимость','imp.stock':'Склад','imp.titleCol':'Дата','imp.name':'Название',
  'taobao.demoTitle':'КАК ЭТО ВЫГЛЯДИТ В РАБОТЕ','taobao.demoBadge':'ДЕМО-ПРИМЕР','taobao.demoNote':'Демо-пример в USD: реальные лоты, цены и маржа появятся после запуска агента.',
  'roi.title':'ROI ПОСТАВЩИКОВ','roi.hint':'Прибыль, ROI и sell-through по поставщикам — на основе склада и связанных продаж.',
  'roi.empty':'Нет данных: добавь товар на склад с поставщиком.','roi.supplier':'Поставщик','roi.items':'Товары','roi.sold':'Продано',
  'roi.stock':'Склад','roi.cost':'Затраты','roi.revenue':'Выручка','roi.profit':'Прибыль','roi.roi':'ROI','roi.st':'ST%','roi.days':'Дней',
  'order.new':'Новый заказ','order.open':'Открыть','order.notify':'Уведомления','order.clear':'Очистить все','mail.desc':'Письма от FunPay / ZeusX / Eldorado, которые трекер распознал. Ничего не добавляется автоматически: перенесите одним кликом в ELDORADO или P&L, либо проигнорируйте.','order.enabled':'Включено','order.blocked':'Заблокировано',
  'order.demo':'Демо','order.sound':'звук','order.testSound':'Проверить звук','order.permissionDenied':'Уведомления не разрешены',
  'order.granted':'Уведомления включены','order.demoCreated':'Демо-заказ создан',
  'rep.title':'Месячный отчёт','rep.tax':'Налог %','rep.show':'Показать','rep.choose':'Выберите месяц','rep.deals':'Сделки за месяц','rep.cashTax':'Cashflow / налог','rep.taxBase':'Налоговая база (net profit)','rep.taxRate':'Ставка налога','rep.taxEst':'Оценка налога'
});
Object.assign(I18N.uk, {
  'f.title':'НАЗВА (необов.)','f.platform':'ПЛАТФОРМА','f.zeusRank':'РАНГ ZEUSX','f.currency':'ВАЛЮТА УГОДИ','f.rate':'КУРС / USD',
  'f.feePct':'КОМІСІЯ %','f.expenses':'ІНШІ ВИТРАТИ','f.buy':'КУПЛЕНО','f.sell':'ПРОДАНО','f.after':'ПІСЛЯ КОМІСІЇ','f.net':'ЧИСТИЙ ПРИБУТОК','f.date':'ДАТА',
  'f.currencyHint':'Суми — у валюті угоди. Курс — скільки одиниць цієї валюти за 1 USD; він зберігається для історії.',
  'b.add':'+ ДОДАТИ','b.sync':'СИНХРОНІЗУВАТИ','b.bulk':'МАСОВО','b.bulkFee':'КОМІСІЯ'
});
Object.assign(I18N.en, {
  'f.title':'TITLE (optional)','f.platform':'PLATFORM','f.zeusRank':'ZEUSX TIER','f.currency':'DEAL CURRENCY','f.rate':'RATE / USD',
  'f.feePct':'FEE %','f.expenses':'OTHER EXPENSES','f.buy':'BOUGHT','f.sell':'SOLD','f.after':'AFTER FEE','f.net':'NET PROFIT','f.date':'DATE',
  'f.currencyHint':'Amounts are in the deal currency. The rate is units of that currency per 1 USD and is saved for history.',
  'b.add':'+ ADD','b.sync':'SYNC','b.bulk':'BULK','b.bulkFee':'COMMISSION'
});
Object.assign(I18N.ru, {
  'f.title':'НАЗВАНИЕ (необяз.)','f.platform':'ПЛАТФОРМА','f.zeusRank':'РАНГ ZEUSX','f.currency':'ВАЛЮТА СДЕЛКИ','f.rate':'КУРС / USD',
  'f.feePct':'КОМИССИЯ %','f.expenses':'ДРУГИЕ РАСХОДЫ','f.buy':'КУПЛЕНО','f.sell':'ПРОДАНО','f.after':'ПОСЛЕ КОМИССИИ','f.net':'ЧИСТАЯ ПРИБЫЛЬ','f.date':'ДАТА',
  'f.currencyHint':'Суммы — в валюте сделки. Курс — сколько единиц этой валюты за 1 USD; он сохраняется для истории.',
  'b.add':'+ ДОБАВИТЬ','b.sync':'СИНХРОНИЗИРОВАТЬ','b.bulk':'МАССОВО','b.bulkFee':'КОМИССИЯ'
});
Object.assign(I18N.uk, {
  'upd.title':'ОНОВЛЕННЯ','upd.check':'Перевірити','upd.hint':'Натисни «Перевірити», щоб дізнатися останню версію.',
  'bk.panelTitle':'БЕКАП P&L','bk.runNow':'Зробити зараз','bk.hint':'Авто-бекап раз на день у папку gt_backups/ поруч з трекером. Зберігаються останні 30 файлів (P&L, ELDORADO, ціль).','bk.loading':'⏳ Завантаження...',
  'bk.exportZip':'Експорт усіх даних (zip)','bk.exportEnc':'Експорт зашифрований','bk.import':'Імпорт zip / .enc','bk.note':'P&L + ELDORADO + ціль + налаштування · без паролів і токенів · sha256-перевірка',
  'ph.cloud':'ХМАРНИЙ БЕКАП','set.cloudHint':'Копія бекапів у OneDrive (або будь-яка папка). Порожнє поле = авто: OneDrive/GameTrackerBackups.','set.folder':'ПАПКА',
  'cloud.save':'Зберегти','cloud.every':'Кожні','cloud.hours':'год','cloud.keep':'Тримати','cloud.copies':'копій','cloud.now':'Бекап зараз','cloud.verify':'Перевірити','cloud.restoreTest':'Тест відновлення',
  'cloud.encrypt':'Шифрувати автоматичні бекапи','cloud.password':'Пароль шифрування','cloud.passwordHint':'Пароль зберігається в secrets; без нього бекап не відкрити.'
});
Object.assign(I18N.en, {
  'upd.title':'UPDATES','upd.check':'Check','upd.hint':'Press Check to see the latest version.',
  'bk.panelTitle':'P&L BACKUP','bk.runNow':'Run now','bk.hint':'Auto-backup once a day to gt_backups/ next to the tracker. The latest 30 files are kept (P&L, ELDORADO, goal).','bk.loading':'⏳ Loading...',
  'bk.exportZip':'Export all data (zip)','bk.exportEnc':'Export encrypted','bk.import':'Import zip / .enc','bk.note':'P&L + ELDORADO + goal + settings · no passwords or tokens · sha256 verification',
  'ph.cloud':'CLOUD BACKUP','set.cloudHint':'Copy backups to OneDrive (or any folder). Empty field = auto: OneDrive/GameTrackerBackups.','set.folder':'FOLDER',
  'cloud.save':'Save','cloud.every':'Every','cloud.hours':'h','cloud.keep':'Keep','cloud.copies':'copies','cloud.now':'Backup now','cloud.verify':'Check','cloud.restoreTest':'Restore test',
  'cloud.encrypt':'Encrypt automatic backups','cloud.password':'Encryption password','cloud.passwordHint':'The password is stored in secrets; without it the backup cannot be opened.'
});
Object.assign(I18N.ru, {
  'upd.title':'ОБНОВЛЕНИЯ','upd.check':'Проверить','upd.hint':'Нажми «Проверить», чтобы узнать последнюю версию.',
  'bk.panelTitle':'БЭКАП P&L','bk.runNow':'Сделать сейчас','bk.hint':'Авто-бэкап раз в день в папку gt_backups/ рядом с трекером. Хранятся последние 30 файлов (P&L, ELDORADO, цель).','bk.loading':'⏳ Загрузка...',
  'bk.exportZip':'Экспорт всех данных (zip)','bk.exportEnc':'Экспорт зашифрованный','bk.import':'Импорт zip / .enc','bk.note':'P&L + ELDORADO + цель + настройки · без паролей и токенов · sha256-проверка',
  'ph.cloud':'ОБЛАЧНЫЙ БЭКАП','set.cloudHint':'Копия бэкапов в OneDrive (или любая папка). Пустое поле = авто: OneDrive/GameTrackerBackups.','set.folder':'ПАПКА',
  'cloud.save':'Сохранить','cloud.every':'Каждые','cloud.hours':'ч','cloud.keep':'Хранить','cloud.copies':'копий','cloud.now':'Бэкап сейчас','cloud.verify':'Проверить','cloud.restoreTest':'Тест восстановления',
  'cloud.encrypt':'Шифровать автоматические бэкапы','cloud.password':'Пароль шифрования','cloud.passwordHint':'Пароль хранится в secrets; без него бэкап не открыть.'
});
Object.assign(I18N.uk, {
  'reply.title':'ГЕНЕРАТОР ВІДПОВІДІ','reply.hint':'Три готові варіанти — обери мову, скопіюй і встав у чат. Кнопка «Інший варіант» змінює формулювання.','reply.copy':'Копіювати','reply.copied':'Скопійовано','reply.regen':'Інший варіант','reply.notFound':'Замовлення не знайдено','reply.copyFail':'Не вдалося скопіювати'
});
Object.assign(I18N.en, {
  'reply.title':'REPLY GENERATOR','reply.hint':'Three ready-to-use variants — pick a language, copy and paste into the chat. “Another variant” changes the wording.','reply.copy':'Copy','reply.copied':'Copied','reply.regen':'Another variant','reply.notFound':'Order not found','reply.copyFail':'Could not copy'
});
Object.assign(I18N.ru, {
  'reply.title':'ГЕНЕРАТОР ОТВЕТА','reply.hint':'Три готовых варианта — выбери язык, скопируй и вставь в чат. Кнопка «Другой вариант» меняет формулировку.','reply.copy':'Копировать','reply.copied':'Скопировано','reply.regen':'Другой вариант','reply.notFound':'Заказ не найден','reply.copyFail':'Не удалось скопировать'
});
Object.assign(I18N.uk, {
'mobile.title':'Мобільний доступ','mobile.refresh':'Оновити','desk.title':'Вікно застосунку',
'desk.tray':'Закривати у трей, а не виходити','desk.hint':'Хрестик ховає вікно в трей; вийти повністю можна через меню трея.',
'desk.save':'Зберегти','desk.compact':'Компактний режим (більше рядків на екрані)',
'qs.title':'Швидкий старт','qs.hint':'Ще немає угод. Почни з однієї з дій — дані одразу з’являться в огляді.',
'qs.deal':'Додати угоду','qs.channels':'Підключити канал','qs.orders':'Імпорт замовлень','qs.demo':'Демо-замовлення'
});
Object.assign(I18N.en, {
'mobile.title':'Mobile access','mobile.refresh':'Refresh','desk.title':'App window',
'desk.tray':'Close to tray instead of exiting','desk.hint':'X hides the window to the tray; use the tray menu to exit completely.',
'desk.save':'Save','desk.compact':'Compact mode (more rows on screen)',
'qs.title':'Quick start','qs.hint':'No deals yet. Start with one of these actions — the overview will fill in.',
'qs.deal':'Add deal','qs.channels':'Connect channel','qs.orders':'Import orders','qs.demo':'Demo order'
});
Object.assign(I18N.ru, {
'mobile.title':'Мобильный доступ','mobile.refresh':'Обновить','desk.title':'Окно приложения',
'desk.tray':'Сворачивать в трей, а не выходить','desk.hint':'Крестик скрывает окно в трей; выйти полностью можно через меню трея.',
'desk.save':'Сохранить','desk.compact':'Компактный режим (больше строк на экране)',
'qs.title':'Быстрый старт','qs.hint':'Пока нет сделок. Начни с одного из действий — данные сразу появятся в обзоре.',
'qs.deal':'Добавить сделку','qs.channels':'Подключить канал','qs.orders':'Импорт заказов','qs.demo':'Демо-заказ'
});

function plural(n, key){
  const forms = (PLURAL[LANG] || PLURAL.uk)[key] || ["","",""];
  n = Math.abs(Number(n) || 0);
  if(LANG === 'en') return n === 1 ? forms[0] : forms[1];
  const n10 = n % 10, n100 = n % 100;
  if(n10 === 1 && n100 !== 11) return forms[0];
  if(n10 >= 2 && n10 <= 4 && (n100 < 10 || n100 >= 20)) return forms[1];
  return forms[2];
}
let LANG = localStorage.getItem('gt_lang') || window.__GT_LANG__ || 'en';
function t(k){ return (I18N[LANG] && I18N[LANG][k]) || (I18N.uk[k] || k); }
function dateLocale(){ return LANG==='ru' ? 'ru-RU' : LANG==='en' ? 'en-GB' : 'uk-UA'; }
function fmtNum(v,d=2){ return Number(v||0).toLocaleString(dateLocale(),{minimumFractionDigits:d,maximumFractionDigits:d}); }
function fmtDate(v){
  const s=String(v||''); if(!s) return '';
  const dt=new Date(s.length<=10 ? s+'T00:00:00' : s);
  if(isNaN(dt.getTime())) return s;
  return dt.toLocaleDateString(dateLocale());
}

// ── Переклад діалогів/тостів: точні рядки + шаблони ──
const DIALOG_EXACT = {
  "Введи ціни!":"deal.enterPrices",
  "✅ Запис додано!":"deal.added",
  "✅ Додано в Eldorado":"deal.addedED",
  "✅ Запис оновлено!":"deal.updated",
  "✅ Запис оновлено":"deal.updated",
  "✅ Всі записи вже мають назви!":"deal.bulkNoTitles",
  "Нічого не змінено — введи хоча б одну назву":"deal.bulkNeedName",
  "✅ CSV завантажено!":"deal.csvDone",
  "✅ CSV ELDORADO завантажено!":"ed.csvDone",
  "✅ Додано на склад":"inv.added",
  "✅ Позначено як продано":"inv.soldToast",
  "🚫 Списано":"inv.offToast",
  "↩ Повернуто на склад":"inv.returnToast",
  "🗑 Видалено":"inv.deleted",
  "Видалити запис зі складу?":"inv.deleteConfirm",
  "Введіть назву":"inv.enterName",
  "📋 Скопійовано":"lot.copied",
  "📋 Скопійовано для лоту!":"lot.copied",
  "Очистити всі записи?":"deal.clearConfirm",
  "Очистити кошик (зняти мітки 🛒 з усіх лотів)?":"tb.clearCartConfirm",
  "Видалити цей запис?":"deal.deleteConfirm",
  "Видалити цей запис Eldorado?":"ed.deleteConfirm",
  "Скільки коштував цей акаунт (собівартість), $?\n0 — якщо купували не ви":"mail.costPrompt",
  "Гра (для статистики):\nнапр. Identity V, Zenless Zone Zero, Genshin":"mail.gamePrompt",
  "У листі немає суми. Введіть суму замовлення, $?":"mail.amountPrompt",
  "Скільки варіантів акаунтів у лоті? (0 — невідомо)":"tb.optionsQuestion",
  "Оплата карткою доступна в цьому лоті?":"tb.cardQuestion",
  "Очистити всю чергу?\n\nВидалені замовлення більше не зявляться.":"mail.clearConfirm",
  "Перевірити оплату карткою та кількість варіантів у топ-25 лотів?\n\nКолектор відкриє кожен лот у браузері (~2 хв). Потрібен вхід у Taobao.":"tb.checkConfirm",
  "Запустити збір з Taobao зараз?\n\nЯкщо вікно браузера закрите — агент відкриє його сам (start_cf_debug.bat). Увійдіть у Taobao і пройдіть капчу, збір почнеться автоматично.":"tb.collectConfirm",
  "✅ Лот додано":"tb.added",
  "💳 Позначено: оплата карткою":"tb.markedCard",
  "💳 Мітку знято":"tb.cardRemoved",
  "✅ Telegram збережено":"set.telegramSaved",
  "✅ Папку хмари збережено":"set.cloudSaved",
  "✅ Збережено":"save",
  "✅ Gmail підключено — сповіщення активні":"set.gmailOk",
  "✅ HTTPS-налаштування збережено. Перезапусти трекер.":"set.httpsSaved",
  "🔑 Сертифікат створено. Натисни «Зберегти» і перезапусти.":"set.certCreated",
  "✅ Sale додано!":"deal.addedED",
  "⚠ Порожній файл":"csv.empty",
  "⚠ Введи Gmail-адресу":"set.gmailNeed",
  "⚠ Невірна Gmail-адреса":"set.gmailBad",
  "⚠ Вставте хоча б один cookie":"set.cookieNeed",
  "⚠ Сума має бути більшою за 0":"mail.amountPositive",
  "⚠ Ціна має бути > 0":"tb.pricePositive",
  "⚠ Новий пароль — мінімум 6 символів":"pw.short",
  "⚠ Паролі не співпадають":"pw.mismatch",
  "⚠ Сума має бути більшою за 0 ":"mail.amountPositive"
};
const DIALOG_PATTERNS = [
  [/^✅ Заповнено (\d+) записів!$/, m => t('deal.bulkDone').replace('%s', m[1])],
  [/^☁ Синхронізовано (\d+) записів!$/, m => t('deal.synced').replace('%s', m[1])],
  [/^✅ Cookie збережено: (.+)$/, m => LANG==='ru' ? ('Cookie сохранены: '+m[1]) : (LANG==='en' ? ('Cookies saved: '+m[1]) : m[0])],
  [/^✅ Cookie скопійовано з браузера$/, () => LANG==='ru' ? 'Cookie скопированы из браузера' : (LANG==='en' ? 'Cookies copied from browser' : '✅ Cookie скопійовано з браузера')],
  [/^⏳ Прошу агента скопіювати cookie з браузера…$/, () => LANG==='ru' ? 'Прошу агента скопировать cookie из браузера…' : (LANG==='en' ? 'Asking the agent to copy cookies from the browser…' : '⏳ Прошу агента скопіювати cookie з браузера…')],
  [/^⚠ Не вдалось: відкрийте funpay\.com і zeusx\.com у вікні агента$/, () => LANG==='ru' ? 'Не удалось: откройте funpay.com и zeusx.com в окне агента' : (LANG==='en' ? 'Failed: open funpay.com and zeusx.com in the agent window' : '⚠ Не вдалось: відкрийте funpay.com і zeusx.com у вікні агента')],
  [/^⚠ Помилка: (.*)$/, m => LANG==='ru' ? ('Ошибка: '+m[1]) : (LANG==='en' ? ('Error: '+m[1]) : m[0])],
  [/^⚠ Помилка синхронізації: (.*)$/, m => LANG==='ru' ? ('Ошибка синхронизации: '+m[1]) : (LANG==='en' ? ('Sync error: '+m[1]) : m[0])],
  [/^💾 Бекап збережено! Файлів: (\d+)(.*)$/, m => LANG==='ru' ? ('Бэкап сохранён! Файлов: '+m[1]+m[2]) : (LANG==='en' ? ('Backup saved! Files: '+m[1]+m[2]) : m[0])],
  [/^⚠ Помилка бекапу: (.*)$/, m => LANG==='ru' ? ('Ошибка бэкапа: '+m[1]) : (LANG==='en' ? ('Backup error: '+m[1]) : m[0])],
  [/^✅ Відновлено: (.+?) · (\d+) записів$/, m => LANG==='ru' ? ('Восстановлено: '+m[1]+' · '+m[2]+' записей') : (LANG==='en' ? ('Restored: '+m[1]+' · '+m[2]+' records') : m[0])],
  [/^✅ Імпортовано: (.*)$/, m => LANG==='ru' ? ('Импортировано: '+m[1]) : (LANG==='en' ? ('Imported: '+m[1]) : m[0])],
  [/^✅ Excel завантажено! 4 аркуші: (.*)$/, m => LANG==='ru' ? ('Excel загружен! 4 листа: '+m[1]) : (LANG==='en' ? ('Excel downloaded: 4 sheets: '+m[1]) : m[0])],
  [/^⬇ CSV лотів \((.+), націнка (\d+)%\)$/, m => LANG==='ru' ? ('⬇ CSV лотов ('+m[1]+', наценка '+m[2]+'%)') : (LANG==='en' ? ('⬇ CSV lots ('+m[1]+', markup '+m[2]+'%)') : m[0])],
  [/^🎛 Варіантів: (\d+)$/, m => LANG==='ru' ? ('Вариантов: '+m[1]) : (LANG==='en' ? ('Variants: '+m[1]) : m[0])],
  [/^✅ Мінімальна ціна ¥([\d.]+) — нові лоти нижче не зберігаються$/, m => LANG==='ru' ? ('Минимальная цена ¥'+m[1]+' — новые лоты ниже не сохраняются') : (LANG==='en' ? ('Minimum price ¥'+m[1]+' — new lots below are not saved') : m[0])],
  [/^💱 Курс: ([\d.]+) ₴$/, m => LANG==='ru' ? ('Курс: '+m[1]+' ₴') : (LANG==='en' ? ('Rate: '+m[1]+' ₴') : m[0])],
  [/^📧 Листів: (\d+) · надіслано: (\d+)$/, m => LANG==='ru' ? ('Писем: '+m[1]+' · отправлено: '+m[2]) : (LANG==='en' ? ('Emails: '+m[1]+' · sent: '+m[2]) : m[0])],
  [/^✅ Сповіщення: увімкнено (\d+) з 9$/, m => LANG==='ru' ? ('Уведомления: включено '+m[1]+' из 9') : (LANG==='en' ? ('Notifications: '+m[1]+' of 9 enabled') : m[0])],
  [/^✅ Додано в (.+)$/, m => LANG==='ru' ? ('Добавлено в '+m[1]) : (LANG==='en' ? ('Added to '+m[1]) : m[0])],
  [/^Відновити «(.+)»\?\n\n.*$/, m => t('bk.restoreConfirm').replace('%s', m[1])],
  [/^Імпортувати «(.+)»\?\n\n.*$/, m => t('csv.importConfirm').replace('%s', m[1])],
  [/^Збір уже був (\d+) хв тому.*$/, m => t('tb.collectCooldown').replace('%s', m[1])],
  [/^Посилання на лот Taobao.*$/, () => t('tb.manualLink')],
  [/^Назва лота \(коротко\).*$/, () => t('tb.manualTitle')],
  [/^Ціна в юанях \(¥\).*$/, () => t('tb.manualPrice')],
  [/^На складі: (.+) — \$([\d.]+)\nСобівартість для обліку, \$\? \(Enter = взяти зі складу\)$/, m => t('mail.inStock').replace('%s', m[1]).replace('%s', m[2])],
  [/^Схожий запис уже є:\n(.+)$/, m => LANG==='ru' ? ('Похожая запись уже есть:\n'+m[1]) : (LANG==='en' ? ('A similar record already exists:\n'+m[1]) : m[0])]
];
function trDialog(msg){
  if(LANG === 'uk') return msg;
  const key = DIALOG_EXACT[msg];
  if(key) return t(key);
  for(const pair of DIALOG_PATTERNS){
    const m = String(msg).match(pair[0]);
    if(m) return pair[1](m);
  }
  try{ return _trText(String(msg)); }catch(e){ return msg; }
}
const _nativeConfirm = window.confirm.bind(window);
const _nativePrompt = window.prompt.bind(window);
const _nativeAlert = window.alert.bind(window);
window.confirm = function(m){ return _nativeConfirm(trDialog(m)); };
window.prompt = function(m, d){ return _nativePrompt(trDialog(m), d); };
window.alert = function(m){ return _nativeAlert(trDialog(m)); };

function _brandName(){
  return String(window._appName || 'Ledger').replace(/\+$/,'');
}
function _brandTitle(){
  const nm=_brandName();
  return (typeof GT_PAID!=='undefined' && GT_PAID) ? nm+'+' : nm;
}
function applyAppName(){
  const nm = _brandName();
  const nameEl = g('hdrName');
  if(nameEl) nameEl.textContent = nm;
  const badge = g('planBadge');
  if(badge) badge.style.display = (typeof GT_PAID!=='undefined' && GT_PAID) ? 'inline-flex' : 'none';
  document.title = _brandTitle();
  try{ setDefaultFavicon(); }catch(e){}
}

function syncDemoLink(){
  const a = g('demoBtn'); if(a) a.href = '/demo?lang=' + LANG;
}
function applyLang(){
  document.documentElement.lang = LANG;
  const _mg = document.getElementById('plMonthGroup');
  if(_mg) _mg.setAttribute('label', t('per.months'));
  document.querySelectorAll('[data-i18n]').forEach(el=>{ el.textContent = t(el.dataset.i18n); });
  document.querySelectorAll('[data-i18n-ph]').forEach(el=>{ el.placeholder = t(el.dataset.i18nPh); });
  if(g('langUk')) g('langUk').classList.toggle('on', LANG==='uk');
  if(g('langEn')) g('langEn').classList.toggle('on', LANG==='en');
  if(g('langRu')) g('langRu').classList.toggle('on', LANG==='ru');
  document.title = _brandTitle();
  try{ syncDemoLink(); }catch(e){}
}
async function refreshActiveTab(){
  const act = document.querySelector('.tc.on');
  const id = act ? act.id.replace('tab-','') : '';
  try{
    if(id==='tracker'){ renderPurchases(); if(typeof renderRevenueChart==='function') renderRevenueChart(); }
    else if(id==='mail'){ await loadMailQueue(true); }
    else if(id==='channels'){ await loadPlatforms(); await renderChAll(); renderEldorado(); }
    else if(id==='supply'){ await loadSupply(1, true); }
    else if(id==='buy'){ await loadBuyList(true); }
    else if(id==='taobao'){ await loadTaobao(); }
    else if(id==='inventory'){ await loadInventory(); }
    else if(id==='stats'){ renderStats(); if(typeof renderRevenueChart==='function') renderRevenueChart(); }
    else if(id==='setup'){ await loadSettings(); loadBackupList(); }
    else if(id==='overview'){ renderOverview(); }
    try{ translateAll(); }catch(e){}
  }catch(e){}
}
async function setLang(l){
  LANG = (l==='en') ? 'en' : (l==='ru' ? 'ru' : 'uk');
  try{ localStorage.setItem('gt_lang', LANG); }catch(e){}
  // Мова й валюта — незалежні: зміна мови не чіпає вибрану валюту.
  // Повне перезавантаження: динамічні рендери й кеш перекладів більше не
  // змішують мови (раніше після UA→RU лишалися англійські/українські рядки).
  try{ await fetch('/api/settings/save',{method:'POST',headers:{'Content-Type':'application/json'},
        body: JSON.stringify({lang: LANG, currency: _cur, currency_manual: _currencyManual})}); }catch(e){}
  try{ localStorage.setItem('gt_cur', _cur); localStorage.setItem('gt_cur_manual', _currencyManual ? '1' : '0'); }catch(e){}
  location.reload();
}

// ═══════════════════════════════════════════════
//  ОГЛЯД
// ═══════════════════════════════════════════════
function _mon(d){ return String(d||'').slice(0,7); }
async function renderOverview(){
  try{
    const [pl, q, tb, inv, ed] = await Promise.all([
      fetch('/api/pl').then(r=>r.json()).catch(()=>({})),
      fetch('/api/mail/queue').then(r=>r.json()).catch(()=>({})),
      fetch('/api/taobao').then(r=>r.json()).catch(()=>({})),
      fetch('/api/inventory').then(r=>r.json()).catch(()=>({})),
      fetch('/api/eldorado').then(r=>r.json()).catch(()=>({}))
    ]);
    const pur = Array.isArray(pl.purchases) ? pl.purchases : [];
    const now = new Date();
    const cur = now.toISOString().slice(0,7);
    const prevD = new Date(now.getFullYear(), now.getMonth()-1, 15);
    const prev = prevD.toISOString().slice(0,7);
    const edRows = (ed.sales||[]).map(x=>({date:x.date, title:x.title, src:'eldorado',
      srcName:'Eldorado', sell:Number(x.price||0), buy:Number(x.buy||0),
      afterFee:Number(x.profit||0), _ed:true}));
    const all = (pl.purchases||[]).concat(edRows);
    try{ const qs=g('quickStart'); if(qs) qs.style.display = (all.length ? 'none' : 'block'); }catch(e){}
    const sum = (m)=> all.filter(r=>_mon(r.date)===m)
                        .reduce((a,r)=>a+Number(r.afterFee||0),0);
    const profit = sum(cur), profitPrev = sum(prev);
    const delta = profitPrev ? ((profit-profitPrev)/Math.abs(profitPrev)*100) : 0;
    if(g('ovProfit')) g('ovProfit').textContent = (profit>=0?'+':'-')+locMoney(Math.abs(profit));
    if(g('ovProfitD')) g('ovProfitD').textContent = profitPrev
      ? (t('u.vs')+' '+(delta>=0?'+':'')+fmtPct(delta)) : '';
    const nq = Number(q.new||0);
    if(g('ovActions')) g('ovActions').textContent = nq;
    if(g('ovActionsD')) g('ovActionsD').textContent = nq ? t('u.orders') : t('u.none');
    if(g('ovStock')) g('ovStock').textContent = Number(inv.in_stock||0);
    if(g('ovStockD')) g('ovStockD').textContent = t('u.frozen')+' '+locMoney(inv.frozen);
    const agentOk = !!tb.agent_online;
    const bad = !agentOk;
    if(g('ovHealth')){
      // нейтрально: агент — опційна функція, його відсутність не «проблема»
      g('ovHealth').textContent = bad ? t('st.setup') : t('st.ok');
      g('ovHealth').style.color = bad ? 'var(--mu)' : 'var(--gr)';
    }
    if(g('ovHealthD')) g('ovHealthD').textContent =
      t('u.agent')+': '+(agentOk?t('u.online'):t('u.offline'));
    const feed = all.slice().sort((a,b)=>String(b.date||'').localeCompare(String(a.date||''))).slice(0,6);
    if(g('ovFeed')){
      g('ovFeed').innerHTML = feed.length ? feed.map(r=>{
        const p = Number(r.afterFee||0);
        return '<div class="bub" style="padding:11px 13px">'
          + '<div style="display:flex;justify-content:space-between;gap:10px">'
          + '<div style="font-weight:600;font-size:.86rem">'+esc(String(r.title||'—')).slice(0,80)+'</div>'
          + '<div style="color:'+(p>=0?'var(--gr)':'var(--rd)')+';font-weight:600;white-space:nowrap">'
          + (p>=0?'+':'-')+locMoney(Math.abs(p))+'</div></div>'
          + '<div style="font-size:.72rem;color:var(--mu);margin-top:4px">'+esc(fmtDate(r.date))
          + ' · '+esc(String(r.srcName||r.src||''))+'</div></div>';
      }).join('') : '<div class="none">'+(LANG==='en'?'No deals yet':LANG==='ru'?'Пока нет сделок':'Ще немає угод')+'</div>';
    }
  }catch(e){ console.warn('overview', e); }
}

// ═══════════════════════════════════════════════
//  КАНАЛИ: Eldorado + Платформи в одній вкладці
// ═══════════════════════════════════════════════
async function renderChAll(){
  const box = g('chAll'); if(!box) return;
  try{
    const [pl, ed] = await Promise.all([
      fetch('/api/pl').then(r=>r.json()).catch(()=>({})),
      fetch('/api/eldorado').then(r=>r.json()).catch(()=>({}))
    ]);
    const rows = [];
    const clean = (t)=>String(t||'').replace(/^[\u{1F000}-\u{1FAFF}\u2600-\u27BF]+\s*/u,'');
    (pl.purchases||[]).forEach(r=>rows.push({d:r.date, ch:clean(r.srcName||r.src||'—'),
      game:String(r.title||'—'), sell:Number(r.sell||0), pf:Number(r.afterFee||0)}));
    (ed.sales||[]).forEach(r=>rows.push({d:r.date, ch:'Eldorado',
      game:String(r.title||'—'), sell:Number(r.price||0), pf:Number(r.profit||0)}));
    rows.sort((a,b)=>String(b.d||'').localeCompare(String(a.d||'')));
    const top = rows.slice(0, 15);
    const month = new Date().toISOString().slice(0,7);
    const msum = rows.filter(r=>String(r.d||'').startsWith(month)).reduce((s,r)=>s+r.pf,0);
    if(g('chAllSum')) g('chAllSum').textContent = (LANG==='ru'?'прибыль за месяц: ':LANG==='en'?'profit this month: ':'прибуток за місяць: ') + (msum>=0?'+':'-') + locMoney(Math.abs(msum));
    if(!top.length){ box.innerHTML = '<div class="none">'+(LANG==='ru'?'Пока нет продаж':LANG==='en'?'No sales yet':'Ще немає продажів')+'</div>'; return; }
    const LOGO = {'FunPay':'/logo/funpay.png','Eldorado':'/logo/eldorado.png','ZeusX':'/logo/zeusx.png'};
    const logoOf = (ch)=> LOGO[ch] ? '<img src="'+LOGO[ch]+'" alt="" style="width:14px;height:14px;border-radius:3px;object-fit:contain">' : '';
    const th = (al, t) => '<th style="text-align:'+al+';font-size:11px;color:var(--mu);padding:6px 8px;border-bottom:1px solid var(--brd)">'+t+'</th>';
    box.innerHTML = '<table style="width:100%;border-collapse:collapse;font-size:.85rem">'
      + '<tr>' + th('left',t('th.date')) + th('left',t('th.channel')) + th('left',t('th.game')) + th('right',t('th.sell')) + th('right',t('th.profit')) + '</tr>'
      + top.map(r=>'<tr><td style="padding:8px;color:var(--mu);white-space:nowrap">'+esc(String(r.d||''))+'</td>'
        + '<td style="padding:8px"><span style="display:inline-flex;align-items:center;gap:6px">'
        + logoOf(r.ch)
        + esc(r.ch)+'</span></td>'
        + '<td style="padding:8px;max-width:520px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+esc(r.game.slice(0,90))+'</td>'
        + '<td style="padding:8px;text-align:right;white-space:nowrap">'+locMoney(r.sell)+'</td>'
        + '<td style="padding:8px;text-align:right;white-space:nowrap;color:'+(r.pf>=0?'var(--gr)':'var(--rd)')+';font-weight:600">'
        + (r.pf>=0?'+':'-')+locMoney(Math.abs(r.pf))+'</td></tr>').join('')
      + '</table>';
  }catch(e){ box.innerHTML = '<div class="none">Помилка: '+esc(String(e))+'</div>'; }
}

function openCookiePanel(){
  try{ mnavGo('channels'); }catch(e){}
  setTimeout(function(){
    try{ chView('bal'); }catch(e){}
    try{ const el=g('ckFunpay'); if(el) el.scrollIntoView({behavior:'smooth',block:'center'}); }catch(e){}
  }, 250);
}

function chView(v){
  const host = g('tab-channels'); if(!host) return;
  const pl = g('tab-platforms'), ed = g('tab-eldorado');
  if(pl) pl.style.display = (v === 'ed') ? 'none' : 'block';
  if(ed) ed.style.display = (v === 'ed') ? 'block' : 'none';
  document.querySelectorAll('#chSeg .seg-b').forEach((b,i)=>{
    b.classList.toggle('on', (i===0 && v!=='ed') || (i===1 && v==='ed'));
  });
}

function _mergeChannels(){
  const host = g('tab-channels'); if(!host) return;
  ['tab-platforms','tab-eldorado'].forEach(id=>{
    const el = g(id);
    if(el && el.parentElement !== host){
      host.appendChild(el);
    }
  });
  chView('bal');
  renderChAll();
}

function syncMnav(id){
  document.querySelectorAll('#mnav .mn').forEach(b=>b.classList.toggle('on', b.dataset.tab===id));
}
function mnavGo(id){
  const tab=[...document.querySelectorAll('.tabs .tab')].find(x=>String(x.getAttribute('onclick')||'').includes("'"+id+"'"));
  if(!tab) return;
  sw(id,tab);
  if(id==='mail'){ clearOrderAlert(); try{ loadMailQueue(); }catch(e){} }
  if(id==='stats'){ try{ loadSupplierROI(); loadCashflow(); loadReport(); loadAnalytics(); }catch(e){} }
  if(id==='taobao'){ try{ loadAgentCfg(); }catch(e){} }
  if(id==='inventory'){ try{ loadInventory(); }catch(e){} }
  if(id==='stats'){ try{ renderStats(); setTimeout(renderRevenueChart,80); }catch(e){} }
}
function sw(id,el){
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('on'));
  document.querySelectorAll('.tc').forEach(t=>t.classList.remove('on'));
  el.classList.add('on'); g('tab-'+id).classList.add('on');
  try{ syncMnav(id); }catch(e){}
  try{ window.scrollTo({top:0,behavior:'smooth'}); }catch(e){}
  if(id==='overview'){ renderOverview(); }
  if(id==='mail'){ clearOrderAlert(); try{ loadMailQueue(); }catch(e){} }
  if(id==='tracker'){ setTimeout(()=>{ renderPurchases(); renderRevenueChart(); },50); }
  if(id==='channels'){ renderChAll(); setTimeout(()=>{ try{ translateAll(); }catch(e){} }, 700); }
  if(id==='stats'){ try{ loadSupplierROI(); loadCashflow(); loadReport(); loadAnalytics(); }catch(e){} }
  if(id==='taobao'){ try{ loadAgentCfg(); }catch(e){} }
  if(id==='inventory'){ try{ loadInventory(); }catch(e){} }
}
function toast(msg,ok=true){
  const t=document.createElement('div');
  t.style.cssText=`position:fixed;bottom:28px;right:28px;background:${ok?'#10b981':'#ef4444'};color:#fff;padding:11px 18px;border-radius:8px;font-family:var(--font);font-size:11px;z-index:9999;box-shadow:0 4px 20px rgba(0,0,0,.3)`;
  t.textContent=trDialog(msg);document.body.appendChild(t);setTimeout(()=>t.remove(),3000);
}

// ═══════════════════════════════════════════════
// 💰 P&L ТРЕКЕР
// ═══════════════════════════════════════════════

// Встановлюємо сьогоднішню дату в формі
;(()=>{ const d=g('plDate'); if(d) d.value=todayLocal(); })();

let _zeusxTier = (()=>{ try{ return localStorage.getItem('gt_zeusx_tier') || 'iron'; }catch(e){ return 'iron'; } })();
function defaultFeePct(src, title){
  let base = src==='eldorado' ? Number(FEE_PROFILES.eldorado ?? ED_FEE)
           : (FEE_PROFILES[src] ?? FEES[src] ?? 0);
  const games = FEE_PROFILES.games || {};
  const t = String(title || '').trim().toLowerCase();
  if(t){
    for(const name of Object.keys(games)){
      if(name && t.includes(String(name).toLowerCase())){
        const row = games[name] || {};
        if(row[src] != null) return Number(row[src]) || 0;
        break;
      }
    }
  }
  return base;
}
function applyProfileFee(){
  const plat=g('plPlatform')?.value, fp=g('plFeePct');
  if(!plat || !fp) return;
  const title=g('plTitle')?.value || '';
  const base=defaultFeePct(plat, '');
  const cur=parseFloat(fp.value);
  if(!Number.isFinite(cur) || Math.abs(cur/100 - base) < 1e-6){
    fp.value=(defaultFeePct(plat,title)*100).toFixed(1).replace(/\.0$/,'');
    updateFeePreview();
  }
}
async function saveFeeProfiles(){
  const pct=id=>{ const v=parseFloat(g(id)?.value); return Number.isFinite(v)?Math.max(0,Math.min(100,v))/100:0; };
  const games={};
  String(g('feeGames')?.value||'').split(/\r?\n/).forEach(line=>{
    const parts=line.split('|').map(s=>s.trim());
    if(parts.length<3) return;
    const name=parts[0].slice(0,80);
    const plat=parts[1].toLowerCase();
    if(!name || !['funpay','eldorado','other'].includes(plat)) return;
    let v=parseFloat(String(parts[2]).replace('%','').replace(',','.'));
    if(!Number.isFinite(v)) return;
    if(v>1) v/=100;
    v=Math.max(0,Math.min(1,v));
    (games[name]=games[name]||{})[plat]=v;
  });
  FEE_PROFILES={funpay:pct('feeFunpay'), eldorado:pct('feeEldorado'), other:pct('feeOther'), games};
  try{
    const r=await fetch('/api/settings/save',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({fee_profiles:FEE_PROFILES})});
    if(!r.ok) throw new Error('HTTP '+r.status);
    toast('✅ Комісії збережено');
    applyProfileFee();
  }catch(e){ toast('⚠ '+e, false); }
}
function zeusxTiers(){
  return (FEE_CFG.zeusx_tiers && FEE_CFG.zeusx_tiers.length) ? FEE_CFG.zeusx_tiers : [
    {id:'iron',name:'Iron',fee:0.10},{id:'bronze',name:'Bronze',fee:0.09},
    {id:'silver',name:'Silver',fee:0.08},{id:'gold',name:'Gold',fee:0.07},
    {id:'platinum',name:'Platinum',fee:0.06},{id:'vibranium',name:'Vibranium',fee:0.05}
  ];
}
function fillZeusRanks(){
  const sel=g('plZeusRank'); if(!sel) return;
  sel.innerHTML=zeusxTiers().map(t=>'<option value="'+t.id+'" title="'+esc(t.criteria||'')+'">'+t.name+' · '+(t.fee*100).toFixed(0)+'%</option>').join('');
}
function applyZeusTier(id, save){
  const tiers=zeusxTiers();
  const t=tiers.find(x=>x.id===id) || tiers[0];
  _zeusxTier=t.id;
  fillZeusRanks();
  const sel=g('plZeusRank'), fp=g('plFeePct');
  if(sel) sel.value=t.id;
  if(fp) fp.value=(t.fee*100).toFixed(1).replace(/\.0$/,'');
  try{ localStorage.setItem('gt_zeusx_tier', t.id); }catch(e){}
  if(save){
    try{
      fetch('/api/settings/save',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({zeusx_tier:t.id})}).catch(()=>{});
    }catch(e){}
  }
  updateFeePreview();
}
function plZeusRankPick(){
  const sel=g('plZeusRank');
  if(!sel) return;
  applyZeusTier(sel.value, true);
}
function feePctOf(p){
  if(!p) return 0;
  if(p._ed){
    const sell=Number(p.sell||0);
    if(sell>0) return Math.max(0, Math.min(1, Number(p.fee||0)/sell));
    return ED_FEE;
  }
  let raw = Number(p.feePct);
  if(p.feePct!=null && Number.isFinite(raw)){
    if(raw>1 && raw<=100) raw/=100;
    if(raw>=0 && raw<=1) return raw;
  }
  const sell=Number(p.sell||0), buy=Number(p.buy||0), aft=Number(p.afterFee);
  if(p.afterFee!=null && sell>0 && Number.isFinite(aft)){
    const v=(sell-buy-aft)/sell;
    if(v>=0 && v<=1) return v;
  }
  return defaultFeePct(p.src);
}
function updateFeePreview(){
  const sell = parseFloat(g('plSell').value)||0;
  const buy  = parseFloat(g('plBuy').value)||0;
  const raw  = parseFloat(g('plFeePct')?.value);
  const fee  = Number.isFinite(raw) ? Math.max(0, Math.min(100, raw))/100 : 0;
  const exp  = parseFloat(g('plExpenses')?.value)||0;
  const after = sell*(1-fee) - buy;
  const net = after - exp;
  const _dc = g('plCur')?.value || 'USD';
  const _ds = dealSym(_dc) + ' ';
  const el = g('plFeePreview');
  el.textContent = (after>=0?'+':'')+_ds+after.toFixed(2);
  el.style.color = after>0?'var(--gr)':after<0?'var(--rd)':'var(--mu)';
  const ne = g('plNetPreview');
  if(ne){
    ne.textContent = (net>=0?'+':'')+_ds+net.toFixed(2);
    ne.style.color = net>0?'var(--gr)':net<0?'var(--rd)':'var(--mu)';
  }
}

const PKEY = 'gt4_pl_v2';
let _plSaving = 0;
let _plDirty = false;      // локальні зміни ще не на сервері
let _plRetry = null;
async function savePL(){
  _plSaving++;
  try{
    const r = await fetch('/api/pl/save',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({purchases, force: purchases.length === 0})});
    const res = await r.json().catch(()=>({}));
    if(!r.ok || res.ok === false) throw new Error(res.error || ('HTTP '+r.status));
    _plDirty = false;
  }catch(e){
    // локальна копія + повтор, щоб авто-синхронізація не затерла запис
    _plDirty = true;
    try{ localStorage.setItem(PKEY, JSON.stringify(purchases)); }catch(e2){}
    toast('⚠ Не збережено на сервері: '+e+' — повторю', false);
    if(_plRetry) clearTimeout(_plRetry);
    _plRetry = setTimeout(()=>{ _plRetry=null; if(_plDirty) savePL(); }, 10000);
  } finally {
    _plSaving--;
  }
}

async function runBackup(){
  try{
    const r = await fetch('/api/backup/run',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}).then(x=>x.json());
    if(r.ok){
      const cl = r.cloud||{};
      const extra = cl.copied && cl.copied.length ? (' · ☁ '+cl.copied.length) : (cl.error ? (' · ⚠ '+cl.error) : '');
      toast(t('bk.saved')+' '+(r.files||[]).length+extra);
      loadBackupList(); loadSettings();
    }
  }catch(e){ toast(t('bk.error')+' '+e, false); }
}

async function diagLoad(){
  const box = g('diagBox'); if(!box) return;
  box.textContent = t('diag.loading');
  try{
    const d = await fetch('/api/diag').then(r=>r.json());
    if(!d.ok) throw new Error(d.error || '');
    const c = d.counts || {}, tk = d.tokens || {};
    box.innerHTML = '<div style="line-height:1.7">'
      + '<b>'+t('diag.version')+':</b> '+esc(d.version||'—')+' · uptime '+Math.round(d.uptime||0)+' s<br>'
      + '<b>'+t('diag.counts')+':</b> P&L '+Number(c.purchases||0)
      + ' · ELDORADO '+Number(c.eldorado||0)
      + ' · '+t('bk.typeInventory')+' '+Number(c.inventory||0)
      + ' · '+(LANG==='ru'?'товаров ':LANG==='en'?'products ':'товарів ')+Number(c.suppliers||0)+'<br>'
      + '<b>'+t('diag.tokens')+':</b> '+(LANG==='ru'?'нажмите «Проверить токены»':LANG==='en'?'press “Check tokens”':'натисніть «Перевірити токени»')+'</div>';
  }catch(e){
    box.innerHTML = '<span style="color:var(--rd)">⚠ '+esc(String(e))+'</span>';
  }
}

async function tokensCheck(){
  const el=g('tokenStates'); if(!el) return;
  el.innerHTML='⏳ '+t('tk.checking');
  try{
    const d=await fetch('/api/tokens/check').then(r=>r.json());
    if(!d.ok) throw new Error(d.error||'');
    const L=({uk:{valid:'активний',expired:'прострочений',missing:'не задано',error:'не вдалося перевірити'},
             en:{valid:'active',expired:'expired',missing:'not set',error:'check failed'},
             ru:{valid:'активен',expired:'просрочен',missing:'не задан',error:'не удалось проверить'}})[LANG]
           || {valid:'active',expired:'expired',missing:'not set',error:'check failed'};
    const icon={valid:'✅',expired:'⚠',missing:'—',error:'❔'};
    const row=(name,key)=>{
      const st=(d.states||{})[key]||'error';
      const msg=(d.details||{})[key]||'';
      return '<div style="margin:2px 0">'+(icon[st]||'❔')+' <b>'+name+'</b>: '+(L[st]||st)
        + (msg?' <span style="opacity:.65">· '+esc(String(msg))+'</span>':'')+'</div>';
    };
    el.innerHTML=row('FunPay','funpay')+row('ZeusX','zeusx')+row('Gmail','gmail')+row('Telegram','telegram');
  }catch(e){ el.innerHTML='<span style="color:var(--rd)">⚠ '+esc(String(e))+'</span>'; }
}

async function reloadAllData(){
  try{ const pl = await fetch('/api/pl').then(r=>r.json()); purchases = pl.purchases || []; }catch(e){}
  try{ const ed = await fetch('/api/eldorado').then(r=>r.json()); edSales = ed.sales || []; edLoaded = true; }catch(e){}
  try{ await loadInventory(); }catch(e){}
  try{ renderPurchases(); renderEldorado(); renderStats(); renderOverview(); }catch(e){}
}

async function demoLoad(){
  if(!confirm(t('demo.loadConfirm'))) return;
  try{
    const d = await fetch('/api/demo/load',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    await reloadAllData();
    toast(t('demo.loaded'));
    loadSettings();
  }catch(e){ toast('⚠ '+e, false); }
}

async function demoClear(){
  if(!confirm(t('demo.clearConfirm'))) return;
  try{
    const d = await fetch('/api/demo/clear',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    await reloadAllData();
    toast(t('demo.cleared'));
  }catch(e){ toast('⚠ '+e, false); }
}

async function csvImport(input){
  const f = input && input.files && input.files[0];
  if(input) input.value = '';
  if(!f) return;
  if(!confirm(t('csv.importConfirm').replace('%s', f.name))) return;
  try{
    const text = await f.text();
    if(!text.trim()){ toast(t('csv.empty'), false); return; }
    const d = await fetch('/api/import/csv',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({csv:text})}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    await reloadAllData();
    toast(t('csv.imported').replace('%s', d.added||0).replace('%s', d.skipped||0));
  }catch(e){ toast('⚠ '+e, false); }
}

async function supAdd(){
  const name = (g('supNewName')?.value || '').trim();
  const base = (g('supNewBase')?.value || '').trim();
  if(!name || !base){ toast(t('sup.enterName'), false); return; }
  if(!/^https?:\/\//i.test(base)){ toast(t('sup.badUrl'), false); return; }
  try{
    const d = await fetch('/api/suppliers/add',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({name, base})}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    g('supNewName').value=''; g('supNewBase').value='';
    toast(t('sup.added'));
    loadSupStatus(); loadSupply(1, true);
  }catch(e){ toast('⚠ '+e, false); }
}

async function pwEnable(){
  const el = g('pwEnableNew'); const pw = (el && el.value) || '';
  if(pw.length < 8){ toast(t('pw.short'), false); return; }
  try{
    const d = await fetch('/api/auth/toggle',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({enabled:true,new:pw})}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    if(el) el.value='';
    toast(t('pw.enabledToast'));
    setTimeout(()=>location.reload(), 1000);
  }catch(e){ toast('⚠ '+e, false); }
}

async function pwDisable(){
  if(!confirm(t('pw.disable')+'?')) return;
  try{
    const d = await fetch('/api/auth/toggle',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({enabled:false})}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    toast(t('pw.disabledToast'));
    loadSettings();
  }catch(e){ toast('⚠ '+e, false); }
}

function backupTypeKey(f){
  if(f.startsWith('gt_eldorado_') || f.startsWith('snap_ed_') || /^gt_eldorado_before_restore/.test(f)) return 'bk.typeED';
  if(f.startsWith('gt_goal_')) return 'bk.typeGoal';
  if(f.startsWith('gt_pl_') || f.startsWith('snap_pl_') || /^gt_pl_before_restore/.test(f)) return 'bk.typePL';
  if(f.startsWith('gt_settings_') || f.startsWith('snap_settings_')) return 'bk.typeSettings';
  if(f.startsWith('gt_inventory_') || f.startsWith('snap_inv_')) return 'bk.typeInventory';
  if(f.startsWith('gt_mail_') || f.startsWith('snap_mail_')) return 'bk.typeMail';
  if(f.startsWith('archive')) return 'bk.typeArchive';
  return 'bk.typeOther';
}
function backupRestorable(f){
  return /^(gt_pl_|gt_eldorado_|gt_goal_|snap_pl_|snap_ed_|snap_settings_|snap_inv_|snap_mail_)/.test(f);
}

async function loadBackupList(){
  try{
    const r = await fetch('/api/backup/list').then(x=>x.json());
    const el = g('backupList');
    if(!el) return;
    if(!r.files||!r.files.length){ el.textContent=t('bk.none'); return; }
    el.innerHTML = r.files.map(f=>{
      const type = t(backupTypeKey(f));
      const btn = backupRestorable(f)
        ? '<button class="btn" data-restore="'+esc(f)+'" style="font-size:9px;padding:2px 8px;white-space:nowrap">↩ '+t('bk.restore')+'</button>'
        : '<span style="font-size:9px;color:var(--mu)">'+t('bk.notRestorable')+'</span>';
      return '<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;padding:4px 0;border-bottom:1px solid var(--brd)">'
        + '<span style="font-size:11px">📄 '+esc(f)+' <span style="color:var(--a3);font-size:9px;margin-left:4px">'+type+'</span></span>'
        + btn
        + '</div>';
    }).join('');
  }catch(e){}
}

async function restoreBackup(name){
  if(!confirm(t('bk.restoreConfirm').replace('%s', name))) return;
  try{
    const d = await fetch('/api/backup/restore',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({file:name})}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||'error'), false); return; }
    await reloadAllData();
    try{ await loadSettings(); }catch(e){}
    try{ await loadMailQueue(); }catch(e){}
    loadBackupList();
    toast(t('bk.restored')+': '+name+(d.count!=null?(' · '+d.count+' '+plural(d.count,'records')):''));
    if(d.kind === 'settings') setTimeout(()=>location.reload(), 1100);
  }catch(e){ toast('⚠ '+e, false); }
}

async function exportEncrypted(){
  const pw = prompt('Пароль для зашифрованого бекапу (мін. 4 символи)');
  if(!pw) return;
  if(pw.length < 4){ toast('⚠ Пароль закороткий', false); return; }
  try{
    toast('🔒 Шифрую бекап…');
    const r = await fetch('/api/backup/export/encrypted',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({password:pw})});
    if(!r.ok){ const d=await r.json().catch(()=>({})); toast('⚠ '+(d.error||('HTTP '+r.status)), false); return; }
    const blob=await r.blob();
    const a=document.createElement('a'); a.href=URL.createObjectURL(blob);
    a.download='ledger_backup_'+new Date().toISOString().slice(0,16).replace(/[:T]/g,'-')+'.ledger.enc';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(()=>URL.revokeObjectURL(a.href),3000);
    toast('✅ Зашифрований бекап завантажено');
  }catch(e){ toast('⚠ '+e, false); }
}
async function importBackup(input){
  const f = input.files && input.files[0];
  input.value = '';
  if(!f) return;
  const enc = /\.enc$/i.test(f.name);
  const pw = enc ? prompt('Пароль від зашифрованого бекапу') : '';
  if(enc && !pw) return;
  try{
    toast(t('loading'));
    const headers={'Content-Type':'application/octet-stream'};
    if(enc) headers['X-Backup-Password']=pw;
    const buf=await f.arrayBuffer();
    const insp=await fetch('/api/backup/inspect',{method:'POST',headers,body:buf}).then(r=>r.json());
    if(!insp.ok){ toast('⚠ '+(insp.error||'invalid backup'), false); return; }
    const c=insp.counts||{};
    const msg='Бекап: '+(insp.created||'—')+'\nФайлів: '+(insp.files||[]).length+'\nP&L: '+(c.pl||0)+' · Eldorado: '+(c.ed||0)+'\n\nВідновити? Поточна версія буде збережена.';
    if(!confirm(msg)) return;
    const r = await fetch('/api/backup/import',{method:'POST',
      headers, body:buf});
    const d = await r.json().catch(()=>({}));
    if(!r.ok || d.ok === false){ toast('⚠ '+(d.error||('HTTP '+r.status)), false); return; }
    await reloadAllData();
    loadSettings(); loadBackupList();
    toast(LANG==='ru' ? ('Импортировано: '+(d.files||[]).join(', ')) : LANG==='en' ? ('Imported: '+(d.files||[]).join(', ')) : ('✅ Імпортовано: '+(d.files||[]).join(', ')));
    setTimeout(()=>location.reload(), 1100);
  }catch(e){ toast('⚠ '+e, false); }
}

// ═══════════════════════════════════════════════
// ⚙️ НАЛАШТУВАННЯ: курс, Telegram, хмара
// ═══════════════════════════════════════════════
let _rate = 0;
let _rateAutoDone = false;

const CUR_SYM = {UAH:'₴', EUR:'€', USD:'$', PLN:'zł', CZK:'Kč', TRY:'₺', GBP:'£', KZT:'₸', GEL:'₾', RUB:'₽',
  CHF:'Fr', CAD:'C$', AUD:'A$', NZD:'NZ$', JPY:'¥', CNY:'¥', HKD:'HK$', SGD:'S$', INR:'₹', KRW:'₩',
  BRL:'R$', MXN:'MX$', ZAR:'R', SEK:'kr', NOK:'kr', DKK:'kr', ILS:'₪', AED:'د.إ', SAR:'﷼'};
const CURRENCIES = ['USD','EUR','GBP','UAH','PLN','CZK','TRY','CHF','CAD','AUD','NZD','JPY','CNY','HKD','SGD','INR','KRW','BRL','MXN','ZAR','SEK','NOK','DKK','ILS','AED','SAR','KZT','GEL','RUB'];
let _cur = 'USD';
let _currencyManual = false;
function curSym(){ return CUR_SYM[_cur] || _cur; }
function dealSym(c){ return c==='USD' ? 'USD' : (CUR_SYM[c] || c); }
function dealMoney(v,c){ return dealSym(c)+' '+fmtNum(v,2); }
function currencyOptions(sel){
  return CURRENCIES.map(c=>'<option value="'+c+'"'+(c===sel?' selected':'')+'>'+c+' '+(CUR_SYM[c]||'')+'</option>').join('');
}
function initCurrencySelects(){
  if(g('curSel')) g('curSel').innerHTML = currencyOptions(_cur);
  if(g('plCur')){
    const keep=g('plCur').value || _cur;
    g('plCur').innerHTML = currencyOptions(keep);
    g('plCur').value = keep;
  }
}
function fmtUah(usd){
  const v=Number(usd||0);
  if(_cur==='USD') return '$'+v.toLocaleString(dateLocale(),{minimumFractionDigits:2,maximumFractionDigits:2});
  return _rate ? curSym()+(v*_rate).toLocaleString(dateLocale(),{minimumFractionDigits:2,maximumFractionDigits:2}) : '';
}
function fmtPct(v,d=1){
  return Number(v||0).toLocaleString(dateLocale(),{minimumFractionDigits:d,maximumFractionDigits:d})+'%';
}
function locMoney(usd){
  const v=Number(usd||0);
  const loc=dateLocale();
  if(_cur==='USD') return '$'+v.toLocaleString(loc,{minimumFractionDigits:2,maximumFractionDigits:2});
  if(!_rate) return '$'+v.toLocaleString(loc,{minimumFractionDigits:2,maximumFractionDigits:2});
  return curSym()+(v*_rate).toLocaleString(loc,{minimumFractionDigits:2,maximumFractionDigits:2});
}
let _moneyNodes=[];
let _moneyOrig=new WeakMap();
let _moneyTimer=null;
function _canMoneyNode(node){
  const el=node && node.parentElement;
  if(!el) return false;
  if(el.closest('script,style,input,textarea,select,option,code,pre,[data-no-currency]')) return false;
  return true;
}
function _moneyConvertNode(node){
  if(!_canMoneyNode(node)) return;
  const txt=node.nodeValue||'';
  if(txt.indexOf('$') < 0) return;
  const rate=parseFloat(_rate)||0;
  if(!rate || _cur==='USD') return;
  // вже перераховано для цієї валюти — не чіпаємо (інакше C$ → CC$ → CCC$)
  if(node.__moneyCur === _cur) return;
  // $ не має бути частиною C$, A$, NZ$, S$, R$, HK$ тощо
  const re=/(^|[^A-Za-z])\$(\d[\d,]*(?:\.\d+)?)/g;
  if(!re.test(txt)) return;
  // Оригінал тримаємо на самому вузлі: після перерендеру WeakMap втрачав
  // звʼязок, і сума лишалася перерахованою за старим курсом.
  if(node.__moneyOrig === undefined) node.__moneyOrig = txt;
  _moneyNodes.push(node);
  node.nodeValue=txt.replace(re,(m,pre,num)=>{
    const v=(parseFloat(num.replace(/,/g,''))||0)*rate;
    return pre+curSym()+v.toFixed(2);
  });
  node.__moneyCur=_cur;
}
function convertMoneyText(root){
  if(_cur==='USD' || !_rate) return;
  const base=root||document.body;
  if(!base) return;
  if(base.nodeType===3){ _moneyConvertNode(base); return; }
  const w=document.createTreeWalker(base, NodeFilter.SHOW_TEXT, null);
  let n; while((n=w.nextNode())) _moneyConvertNode(n);
}
function restoreMoneyText(){
  try{
    const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
    let n;
    while((n=w.nextNode())){
      if(n.__moneyOrig !== undefined){
        try{ n.nodeValue=n.__moneyOrig; }catch(e){}
        delete n.__moneyOrig; delete n.__moneyCur;
      }
    }
  }catch(e){}
  _moneyNodes=[]; _moneyOrig=new WeakMap();
}
function scheduleMoneyConvert(){
  clearTimeout(_moneyTimer);
  _moneyTimer=setTimeout(()=>{ try{ convertMoneyText(document.body); }catch(e){} }, 40);
}
try{
  const mo=new MutationObserver(()=>scheduleMoneyConvert());
  mo.observe(document.body,{childList:true,subtree:true,characterData:true});
}catch(e){}
function plCurPick(){
  const c=g('plCur')?.value || 'USD';
  const fx=g('plFx');
  if(fx){
    if(c === _cur && _rate) fx.value = Number(_rate).toFixed(4);
    else if(c === 'USD') fx.value = '1';
    else if(!parseFloat(fx.value)) fx.value = '';
  }
  updateFeePreview();
}
function applyCurrency(){
  restoreMoneyText();
  initCurrencySelects();
  if(g('curSel')) g('curSel').value = _cur;
  const s = curSym();
  const L = ({uk:{t:'ВАЛЮТА',l:'КУРС (',p:' за $1)'},en:{t:'CURRENCY',l:'RATE (',p:' per $1)'},ru:{t:'ВАЛЮТА',l:'КУРС (',p:' за $1)'}})[LANG] || {t:'CURRENCY',l:'RATE (',p:' per $1)'};
  if(g('rateLbl')) g('rateLbl').textContent = L.l + s + L.p;
  if(g('rateTitle')) g('rateTitle').textContent = _cur==='USD' ? (L.t+' · USD') : (L.t+' · USD → '+_cur);
  scheduleMoneyConvert();
  // Перерахувати одразу: після зміни курсу/валюти суми не мають лишатися
  // порахованими за попереднім курсом до наступного тіка таймера.
  try{ restoreMoneyText(); convertMoneyText(document.body); }catch(e){}
}
async function pickCurrency(){
  _cur = (g('curSel') && g('curSel').value) || 'USD';
  _currencyManual = true;
  applyCurrency();
  try{
    await fetch('/api/settings/save',{method:'POST',headers:{'Content-Type':'application/json'},
      body: JSON.stringify({currency: _cur, currency_manual: true})});
    await refreshRate();
    setTimeout(()=>location.reload(),300);
  }catch(e){}
}

async function checkUpdates(){
  const el=g('updateInfo'); if(el) el.innerHTML=t('upd.checking');
  try{
    const d=await fetch('/api/update/check').then(r=>r.json());
    if(!d.ok){ el.innerHTML=t('upd.fail')+' '+esc(d.error||''); return; }
    const same=String(d.latest||'').replace(/^v/,'')===String(d.current||'').replace(/^v/,'');
    el.innerHTML='<div>'+t('upd.current')+': <b>v'+esc(d.current||'?')+'</b> · '+t('upd.latest')+': <b>'+esc(d.latest||'?')+'</b></div>'+
      '<div style="margin-top:4px;color:'+(same?'var(--gr)':'var(--yw)')+'">'+(same?t('upd.same'):t('upd.newer'))+'</div>'+
      (d.url?'<div style="margin-top:8px"><a class="btn" style="text-decoration:none" href="'+esc(d.url)+'" target="_blank" rel="noopener">'+t('upd.open')+'</a></div>':'')+
      (d.body?'<pre style="margin-top:8px;max-height:180px;overflow:auto;white-space:pre-wrap;font-size:11px">'+esc(d.body)+'</pre>':'');
  }catch(e){ el.innerHTML=t('upd.fail')+' '+esc(String(e)); }
}

async function loadAudit(){
  const el=g('auditList'); if(!el) return;
  const labelOf=ev=>{
    const key='aud.e.'+String(ev||'').replace(/\./g,'_');
    const v=t(key);
    return (v && v!==key) ? v : (ev||'');
  };
  try{
    const d=await fetch('/api/audit').then(r=>r.json());
    const rows=d.rows||[];
    if(!rows.length){ el.innerHTML='<div class="none">'+t('aud.none')+'</div>'; return; }
    el.innerHTML='<table class="sup-table"><thead><tr><th>'+t('aud.time')+'</th><th>'+t('aud.action')+'</th><th>'+t('aud.details')+'</th></tr></thead><tbody>'+
      rows.map(r=>{
        const dt=new Date((r.ts||0)*1000);
        const ts=dt.toLocaleString(dateLocale());
        const _L={uk:{title:'назва',cost:'ціна',price:'ціна',count:'кількість',status:'статус',platform:'платформа',game:'гра',qty:'кільк.',name:'назва'},en:{title:'title',cost:'cost',price:'price',count:'count',status:'status',platform:'platform',game:'game',qty:'qty',name:'name'},ru:{title:'название',cost:'цена',price:'цена',count:'количество',status:'статус',platform:'платформа',game:'игра',qty:'кол-во',name:'название'}}[LANG]||{};
        const det=Object.entries(r.detail||{}).filter(([k,v])=>k!=='keys'&&k!=='id'&&v!==''&&v!=null).map(([k,v])=>{
          const lbl=_L[k]||k;
          const val=(k==='cost'||k==='price') && !isNaN(Number(v)) ? locMoney(Number(v)) : String(v);
          return lbl+': '+val;
        }).join(' · ')||'—';
        return '<tr><td style="font-size:10px;color:var(--mu);white-space:nowrap">'+esc(ts)+'</td>'+
          '<td style="font-size:11px">'+esc(labelOf(r.event))+'</td>'+
          '<td style="font-size:10px;color:var(--mu);word-break:break-word">'+esc(det)+'</td></tr>';
      }).join('')+'</tbody></table>';
  }catch(e){ el.innerHTML='<div class="none">⚠ '+esc(String(e))+'</div>'; }
}

async function load2FA(){
  try{
    const d=await fetch('/api/2fa/status').then(r=>r.json());
    const st=g('twofaStatus');
    if(!st) return;
    const _btn=[...document.querySelectorAll('button')].find(b=>b.getAttribute('onclick')==='setup2FA()');
    if(!d.available){
      st.innerHTML='⚠ '+(LANG==='en'?'Enable a login password first':LANG==='ru'?'Сначала включи пароль входа':'Спочатку увімкни пароль входу');
      if(_btn){ _btn.disabled=true; _btn.style.opacity='.5'; _btn.title=(LANG==='en'?'Enable a login password first':LANG==='ru'?'Сначала включи пароль входа':'Спочатку увімкни пароль входу'); }
      if(g('twofaSetup')) g('twofaSetup').style.display='none';
      if(g('twofaEnabled')) g('twofaEnabled').style.display='none';
      return;
    }
    if(_btn){ _btn.disabled=false; _btn.style.opacity=''; _btn.title=''; }
    st.innerHTML = d.enabled
      ? '✅ '+(LANG==='en'?'2FA is enabled':LANG==='ru'?'2FA включена':'2FA увімкнена')
      : '○ '+(LANG==='en'?'2FA is not enabled':LANG==='ru'?'2FA не включена':'2FA не увімкнена');
    if(g('twofaSetup')) g('twofaSetup').style.display='none';
    if(g('twofaEnabled')) g('twofaEnabled').style.display=d.enabled?'block':'none';
    if(g('twofaRecovery')) g('twofaRecovery').style.display='none';
  }catch(e){}
}
async function setup2FA(){
  try{
    const d=await fetch('/api/2fa/setup',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    g('twofaSecret').textContent=d.secret||'';
    g('twofaUri').textContent=d.uri||'';
    g('twofaSetup').style.display='block';
    g('twofaEnabled').style.display='none';
    if(g('twofaCode')) g('twofaCode').value='';
    toast(t('twofa.secretCreated'));
  }catch(e){ toast('⚠ '+e, false); }
}
function showRecovery(codes){
  if(!codes || !codes.length) return;
  const box=g('twofaRecovery'), list=g('twofaRecoveryList');
  if(!box || !list) return;
  list.textContent=codes.join('\n');
  box.style.display='block';
}
function copyRecovery(){
  const txt=g('twofaRecoveryList')?.textContent||'';
  navigator.clipboard.writeText(txt).then(()=>toast(t('twofa.copied'))).catch(()=>toast(t('twofa.clipboardFail'), false));
}
async function enable2FA(){
  const code=(g('twofaCode')?.value||'').trim();
  try{
    const d=await fetch('/api/2fa/enable',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({code})}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    toast(t('twofa.enabledToast')); await load2FA(); showRecovery(d.recovery);
  }catch(e){ toast('⚠ '+e, false); }
}
async function regenRecovery(){
  const code=prompt(t('twofa.regenPrompt'));
  if(!code) return;
  try{
    const d=await fetch('/api/2fa/recovery',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({code})}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    showRecovery(d.recovery);
    toast(t('twofa.regenDone'));
  }catch(e){ toast('⚠ '+e, false); }
}
async function logoutAll(){
  if(!confirm(t('twofa.logoutConfirm'))) return;
  try{
    const d=await fetch('/api/logout/all',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    location.href='/login';
  }catch(e){ toast('⚠ '+e, false); }
}
async function disable2FA(){
  const code=(g('twofaDisableCode')?.value||'').trim();
  if(!confirm(LANG==='en'?'Disable 2FA?':LANG==='ru'?'Выключить 2FA?':'Вимкнути 2FA?')) return;
  try{
    const d=await fetch('/api/2fa/disable',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({code})}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    toast(t('twofa.disabledToast')); await load2FA();
  }catch(e){ toast('⚠ '+e, false); }
}

async function loadPlus(){
  const box=g('plusBody'); if(!box) return;
  try{
    const [st,set]=await Promise.all([fetch('/api/license/status').then(r=>r.json()), fetch('/api/settings').then(r=>r.json())]);
    const lic=st.license||null;
    if(g('plusStatus')) g('plusStatus').textContent = lic ? (lic.plan.toUpperCase()+' · '+lic.days_left+'d') : t('plus.free');
    const row=(k,v)=>'<div style="display:flex;justify-content:space-between;gap:12px;padding:6px 0;border-bottom:1px solid var(--brd)"><span style="color:var(--mu)">'+k+'</span><b>'+esc(String(v))+'</b></div>';
    const card=(title,price,desc)=>'<div style="background:var(--card2);border:1px solid var(--brd);border-radius:12px;padding:14px;min-width:220px;flex:1"><div style="font-weight:800">'+title+'</div><div style="font-size:22px;font-weight:800;color:var(--gr);margin:6px 0">'+price+'</div><div style="font-size:11px;color:var(--mu)">'+desc+'</div></div>';
    const pay=(id,label,val,ph)=>'<label style="font-size:11px;color:var(--mu)">'+label+'<br><input id="'+id+'" value="'+esc(val||'')+'" placeholder="'+esc(ph||'')+'" style="width:100%;margin-top:4px;font-size:12px"></label>';
    box.innerHTML =
      '<div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px">'
      + card(t('plus.solo'),'$7',t('plus.perMonth')) + card(t('plus.team'),'$29',t('plus.perMonth')) + card(t('plus.setup'),'$29',t('plus.once'))
      + '</div>'
      + '<div style="font-size:12px;color:var(--mu);margin-bottom:14px">'+t('plus.features')+'</div>'
      + '<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:12px">'
      + '<input id="licCode" placeholder="'+t('plus.codePh')+'" style="flex:1;min-width:260px;font-size:12px">'
      + '<button class="btn gr" onclick="activateLicense()">'+t('plus.activate')+'</button>'
      + (lic?'<button class="btn" onclick="deactivateLicense()">'+t('plus.deactivate')+'</button>':'')
      + '</div>'
      + (lic ? row(t('plus.plan'),lic.plan)+row(t('plus.expires'),lic.exp)+row(t('plus.days'),lic.days_left) : '<div class="al info">'+t('plus.needKey')+'</div>')
      + '<div class="ph" style="margin:18px 0 8px"><span>'+t('plus.pay')+'</span></div>'
      + '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:8px">'
      + pay('payUsdt',t('plus.usdt'),set.pay_usdt,'T... / 0x...') + pay('payBinance',t('plus.binance'),set.pay_binance,'Binance Pay ID')
      + pay('payPayoneer',t('plus.payoneer'),set.pay_payoneer,'email@payoneer') + pay('payTg',t('plus.tg'),set.pay_tg,'@ledger_os')
      + '</div>'
      + '<div style="display:flex;gap:8px;align-items:center;margin-top:10px;flex-wrap:wrap"><button class="btn" onclick="savePayDetails()">'+t('plus.save')+'</button><span style="font-size:11px;color:var(--mu)">'+t('plus.hint')+'</span></div>'
      + '<div style="font-size:11px;color:var(--mu);margin-top:10px">'+t('plus.trialNote')+'</div>'
      + '<div style="font-size:11px;color:var(--mu);margin-top:4px">'+t('plus.stars')+'</div>'
      + '<div class="ph" style="margin:18px 0 8px"><span>TEAM</span></div><div id="teamBox">⏳</div>';
    loadTeam();
  }catch(e){ box.innerHTML='<div class="al err">⚠ '+esc(String(e))+'</div>'; }
}
async function loadTeam(){
  const box=g('teamBox'); if(!box) return;
  const L=(uk,en,ru)=>LANG==='en'?en:(LANG==='ru'?ru:uk);
  try{
    const d=await fetch('/api/team').then(r=>r.json());
    if(!d.ok){ box.innerHTML='<div class="al info">'+esc(d.error||'')+'</div>'; return; }
    const rows=(d.members||[]).filter(m=>m.active).map(m=>'<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid var(--brd)"><span>'+esc(m.name)+' · <b>'+esc(m.role)+'</b></span><button class="btn" style="font-size:11px;padding:4px 8px" onclick="teamRemoveMember(\''+m.id+'\')">✕</button></div>').join('');
    const inv=(d.invites||[]).map(i=>'<div style="font-size:11px;color:var(--mu);padding:4px 0">'+esc(i.name)+' · '+esc(i.role)+' · <a style="color:var(--gr)" target="_blank" href="'+location.origin+'/join?token='+encodeURIComponent(i.token)+'">'+L('посилання','link','ссылка')+'</a></div>').join('');
    box.innerHTML='<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px"><input id="teamName" placeholder="'+L('Ім’я','Name','Имя')+'" style="flex:1;min-width:160px;font-size:12px"><select id="teamRole" style="font-size:12px;width:auto"><option value="manager">manager</option><option value="viewer">viewer</option></select><button class="btn gr" onclick="teamInvite()">'+L('Створити інвайт','Create invite','Создать инвайт')+'</button></div><div id="teamLink" style="font-size:12px;color:var(--gr);word-break:break-all;margin-bottom:6px"></div>'+(rows||'<div class="none">'+L('Немає учасників','No members','Нет участников')+'</div>')+(inv?'<div style="margin-top:8px">'+inv+'</div>':'');
  }catch(e){ box.innerHTML='<div class="al err">⚠ '+esc(String(e))+'</div>'; }
}
async function teamInvite(){
  const L=(uk,en,ru)=>LANG==='en'?en:(LANG==='ru'?ru:uk);
  try{
    const name=(g('teamName')&&g('teamName').value||'').trim();
    const role=(g('teamRole')&&g('teamRole').value)||'viewer';
    const d=await fetch('/api/team/invite',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,role,days:30})}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    if(g('teamLink')) g('teamLink').textContent=d.link;
    toast(L('Інвайт створено','Invite created','Инвайт создан'));
    loadTeam();
  }catch(e){ toast('⚠ '+e, false); }
}
async function teamRemoveMember(id){
  try{ await fetch('/api/team/remove',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id})}); loadTeam(); }catch(e){ toast('⚠ '+e, false); }
}

async function activateLicense(){
  const code=(g('licCode')&&g('licCode').value||'').trim();
  if(!code){ toast(t('plus.codePh'), false); return; }
  try{
    const d=await fetch('/api/license/activate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code})}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    toast(t('plus.activated')+' · '+d.license.plan);
    setTimeout(()=>location.reload(), 700);
  }catch(e){ toast('⚠ '+e, false); }
}
async function deactivateLicense(){
  if(!confirm(t('plus.deactivate')+'?')) return;
  try{
    await fetch('/api/license/deactivate',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
    setTimeout(()=>location.reload(), 500);
  }catch(e){ toast('⚠ '+e, false); }
}
async function savePayDetails(){
  try{
    const body={pay_usdt:(g('payUsdt')&&g('payUsdt').value)||'', pay_binance:(g('payBinance')&&g('payBinance').value)||'', pay_payoneer:(g('payPayoneer')&&g('payPayoneer').value)||'', pay_tg:(g('payTg')&&g('payTg').value)||''};
    await fetch('/api/settings/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    toast(t('plus.saved'));
  }catch(e){ toast('⚠ '+e, false); }
}

async function loadMobile(){
  const box=g('mobileBody'); if(!box) return;
  const L=(uk,en,ru)=>LANG==='en'?en:(LANG==='ru'?ru:uk);
  try{
    const d=await fetch('/api/mobile/info').then(r=>r.json());
    const items=(d.items||[]);
    if(!items.length){ box.innerHTML='<div class="al info">'+L('Посилання недоступне: застосунок слухає лише 127.0.0.1. Запусти з GT_BIND=0.0.0.0 для доступу з телефона.','No link: the app listens on 127.0.0.1 only. Start with GT_BIND=0.0.0.0 to allow phones.','Ссылка недоступна: приложение слушает только 127.0.0.1. Запусти с GT_BIND=0.0.0.0 для доступа с телефона.')+'</div>'; return; }
    window.__mobileItems=items;
    const sel=items.map((it,i)=>'<option value="'+i+'">'+esc(it.label==='lan'?L('локальна мережа','local network','локальная сеть'):L('поточне посилання','current link','текущая ссылка'))+' — '+esc(it.url)+'</option>').join('');
    box.innerHTML='<div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:10px"><select id="mobileSel" onchange="renderMobileQr()" style="flex:1;min-width:240px;font-size:12px">'+sel+'</select><button class="btn" onclick="copyMobileLink()" style="font-size:12px;padding:6px 10px">⧉ '+L('Копіювати','Copy','Копировать')+'</button></div>'
      + '<div style="display:flex;gap:14px;flex-wrap:wrap;align-items:flex-start"><img id="mobileQr" alt="QR" style="width:180px;height:180px;background:#fff;border-radius:10px;padding:6px"><div style="flex:1;min-width:220px;line-height:1.7">'+L('Відскануй QR телефоном.','Scan the QR with your phone.','Отсканируй QR телефоном.')+'<br>'+L('Якщо є пароль — введи його на телефоні.','If a password is set, enter it on the phone.','Если есть пароль — введи его на телефоне.')+(d.auth?'<br><b style="color:var(--gr)">'+L('Потрібен пароль','Password required','Нужен пароль')+'</b>':'')+'</div></div>';
    if(!d.lan_ok && /(^|\/\/)(127\.0\.0\.1|localhost)/.test(String(d.origin||''))){ box.insertAdjacentHTML('beforeend','<div class="al info" style="margin-top:8px">'+L('Телефон у тій самій Wi‑Fi мережі зможе відкрити застосунок, якщо запустити його з GT_BIND=0.0.0.0. Зараз сервер слухає лише 127.0.0.1.','A phone on the same Wi‑Fi can open the app if you start it with GT_BIND=0.0.0.0. The server currently listens on 127.0.0.1 only.','Телефон в той же Wi‑Fi сети сможет открыть приложение, если запустить его с GT_BIND=0.0.0.0. Сейчас сервер слушает только 127.0.0.1.')+'</div>'); }
    renderMobileQr();
  }catch(e){ box.innerHTML='<div class="al err">⚠ '+esc(String(e))+'</div>'; }
}
function renderMobileQr(){
  const items=window.__mobileItems||[]; const sel=g('mobileSel'); const img=g('mobileQr'); if(!img) return;
  const it=items[Number(sel&&sel.value||0)]; if(!it){ img.style.display='none'; return; }
  img.style.display='block';
  let _u=String(it.url||'');
  if(window.__mobileV) _u += (_u.includes('?')?'&':'?')+'m='+window.__mobileV;
  img.src='/api/mobile/qr?url='+encodeURIComponent(_u)+'&t='+Date.now();
}
async function copyMobileLink(){
  const items=window.__mobileItems||[]; const sel=g('mobileSel'); const it=items[Number(sel&&sel.value||0)]; if(!it) return;
  try{ await navigator.clipboard.writeText(it.url); toast('⧉ '+it.url); }catch(e){ prompt('URL', it.url); }
}

function setCompact(on){
  document.body.classList.toggle('compact-ui', !!on);
  try{ localStorage.setItem('gt_compact', on?'1':'0'); }catch(e){}
  const cb=g('compactMode'); if(cb) cb.checked=!!on;
}
try{ if(localStorage.getItem('gt_compact')==='1') document.body.classList.add('compact-ui'); }catch(e){}

async function refreshMobile(){
  const L=(uk,en,ru)=>LANG==='en'?en:(LANG==='ru'?ru:uk);
  window.__mobileV=Date.now();
  await loadMobile();
  const el=g('mobileUpdated');
  if(el) el.textContent=L('Оновлено: ','Updated: ','Обновлено: ')+new Date().toLocaleTimeString();
  toast(L('QR оновлено','QR refreshed','QR обновлён'));
}

function initDesktopPrefs(){
  const panel=g('desktopPanel'); if(!panel) return;
  if(!(window.pywebview && window.pywebview.api && window.pywebview.api.get_prefs)){ panel.style.display='none'; return; }
  try{ window.pywebview.api.get_prefs().then(p=>{ const cb=g('closeToTray'); if(cb) cb.checked = !!(p&&p.close_to_tray); const cm=g('compactMode'); if(cm) cm.checked=(localStorage.getItem('gt_compact')==='1'); panel.style.display='block'; }).catch(()=>{ panel.style.display='none'; }); }catch(e){ panel.style.display='none'; }
}
async function saveDesktopPrefs(){
  try{
    const on=!!(g('closeToTray')&&g('closeToTray').checked);
    await window.pywebview.api.set_close_to_tray(on);
    toast((on?'✅ ':'✅ ')+(LANG==='en'?'Close to tray: ':(LANG==='ru'?'Сворачивать в трей: ':'Закривати в трей: '))+(on?'ON':'OFF'));
  }catch(e){ toast('⚠ '+e, false); }
}
window.addEventListener('pywebviewready', ()=>setTimeout(initDesktopPrefs, 300));

async function loadSettings(){
  try{
    const d = await fetch('/api/settings').then(r=>r.json());
    if(d.currency) _cur = d.currency;
    _rate = parseFloat(d.usd_uah)||0;
    // Захист від старих/зіпсованих налаштувань, де курс зберігся ×100:
    // інакше Overview показував суму у 100 разів більшою за Deals.
    if((_cur==='UAH' && _rate > 200) || (_cur==='RUB' && _rate > 500)) _rate = _rate/100;
    _currencyManual = !!d.currency_manual;
    applyCurrency();
    if(g('plCur')){ g('plCur').value = _cur; }
    if(g('plFx')){ g('plFx').value = (_cur === 'USD' ? 1 : (_rate || '')); }
    if(g('rateVal')) g('rateVal').value = _rate ? _rate.toFixed(2) : '';
    if(g('rateInfo')) g('rateInfo').textContent = d.rate_ts
      ? (t('cur.updated')+' '+new Date(d.rate_ts*1000).toLocaleString(dateLocale())+' · '+(d.rate_source||''))
      : (LANG==='ru'?'курс ещё не задан':LANG==='en'?'rate not set yet':'курс ще не задано');
    if(!_rateAutoDone){
      _rateAutoDone = true;
      const _stale = !d.rate_ts || (Date.now()/1000 - Number(d.rate_ts) > 6*3600);
      if(_cur !== 'USD' && _stale) setTimeout(()=>{ try{ refreshRate(); }catch(e){} }, 400);
    }
    if(g('cloudDir')) g('cloudDir').value = d.cloud_dir || '';
    if(g('backupHours')) g('backupHours').value = d.backup_hours || 24;
    if(g('backupKeep')) g('backupKeep').value = d.backup_keep || 30;
    if(g('backupEncrypt')) g('backupEncrypt').checked = !!d.backup_encrypt;
    if(g('backupInfo')) g('backupInfo').textContent = d.backup_last_ts
      ? ('Останній бекап: '+new Date(d.backup_last_ts*1000).toLocaleString(dateLocale())+' · '+(d.backup_last_status||'')+(d.backup_last_verify?(' · перевірка: '+d.backup_last_verify):'')+(d.backup_last_restore_test?(' · restore: '+d.backup_last_restore_test):'')+(d.backup_password_protected?' · 🔐 DPAPI':''))
      : (LANG==='ru'?'Автобэкап ещё не запускался':LANG==='en'?'Auto-backup has not run yet':'Автобекап ще не запускався');
    if(g('targetPrices')) g('targetPrices').value = (d.price_targets || []).map(x => x.q + ' | ' + x.max).join('\n');
    ['g2g','gameflip','pa','zeusx','funpay','eldorado','other'].forEach(k=>{
      const el=g('pd_'+k); if(el) el.value=(d.payout_days&&d.payout_days[k]!=null)?d.payout_days[k]:3;
    });
    if(g('cloudInfo')) g('cloudInfo').innerHTML = d.cloud_effective
      ? ((LANG==='ru'?'Копирование в: ':LANG==='en'?'Copying to: ':'Копіювання у: ')+'<code>'+esc(d.cloud_effective)+'</code> '+(d.cloud_exists?'✓':(LANG==='ru'?'· папка создастся при бэкапе':LANG==='en'?'· folder will be created on backup':'· папка створиться при бекапі')))
      : (LANG==='ru'?'⚠ Облако не найдено — укажи папку вручную':LANG==='en'?'⚠ Cloud folder not found — set it manually':'⚠ Хмару не знайдено — вкажи папку вручну');
    const https = d.https||{};
    if(g('httpsEnabled')) g('httpsEnabled').checked = !!https.enabled;
    if(g('httpsCert')) g('httpsCert').value = https.cert||'';
    if(g('httpsKey')) g('httpsKey').value = https.key||'';
    if(g('httpsInfo')) g('httpsInfo').textContent = https.active
      ? (LANG==='ru'?'✅ HTTPS активен (после перезапуска)':LANG==='en'?'✅ HTTPS active (after restart)':'✅ HTTPS активний (після перезапуску)')
      : https.enabled
        ? (LANG==='ru'?'⚠ включён, но cert/key не найден — исправь и перезапусти':LANG==='en'?'⚠ enabled, but cert/key not found — fix and restart':'⚠ увімкнено, але cert/key не знайдено — виправ і перезапусти')
        : (LANG==='ru'?'HTTPS отключён · на хостинге HTTPS обычно обеспечивает прокси':LANG==='en'?'HTTPS disabled · on hosting a proxy usually provides HTTPS':'HTTPS вимкнено · на хостингу HTTPS зазвичай забезпечує проксі');
    const tg = d.tg||{};
    if(g('tgChat')) g('tgChat').value = tg.chat_id||'';
    if(typeof d.onboarded !== 'undefined') _onboarded = !!d.onboarded;
    if(d.app_name){ window._appName = d.app_name; try{ localStorage.setItem('gt_appname', d.app_name); }catch(e){} applyAppName(); }
    if(d.zeusx_tier){
      _zeusxTier = String(d.zeusx_tier);
      try{ localStorage.setItem('gt_zeusx_tier', _zeusxTier); }catch(e){}
      if(g('plPlatform')?.value === 'zeusx'){ try{ applyZeusTier(_zeusxTier, false); }catch(e){} }
    }
    if(d.fee_profiles){
      FEE_PROFILES = {
        funpay: Number(d.fee_profiles.funpay ?? FEES.funpay),
        eldorado: Number(d.fee_profiles.eldorado ?? ED_FEE),
        other: Number(d.fee_profiles.other ?? (FEES.other||0)),
        games: d.fee_profiles.games || {}
      };
      if(g('feeFunpay')) g('feeFunpay').value=(FEE_PROFILES.funpay*100).toFixed(1).replace(/\.0$/,'');
      if(g('feeEldorado')) g('feeEldorado').value=(FEE_PROFILES.eldorado*100).toFixed(1).replace(/\.0$/,'');
      if(g('feeOther')) g('feeOther').value=(FEE_PROFILES.other*100).toFixed(1).replace(/\.0$/,'');
      if(g('feeGames')){
        const lines=[];
        Object.keys(FEE_PROFILES.games||{}).forEach(name=>{
          const row=FEE_PROFILES.games[name]||{};
          Object.keys(row).forEach(plat=>lines.push(name+' | '+plat+' | '+(Number(row[plat])*100).toFixed(1).replace(/\.0$/,'')));
        });
        g('feeGames').value=lines.join('\n');
      }
      try{ applyProfileFee(); }catch(e){}
    }
  if(d.lang && d.lang !== LANG){ LANG = d.lang; try{ localStorage.setItem('gt_lang', LANG); }catch(e){} }
  applyLang();
  try{ if(g('tab-overview') && g('tab-overview').classList.contains('on')) renderOverview(); }catch(e){}
  if(!_currencyManual){
    const _autoCur = ({uk:'UAH', en:'USD', ru:'RUB'})[LANG] || _cur;
    if(_autoCur !== _cur){
      _cur = _autoCur;
      try{ fetch('/api/settings/save',{method:'POST',headers:{'Content-Type':'application/json'},
        body: JSON.stringify({currency:_cur})}); }catch(e){}
      applyCurrency();
      setTimeout(()=>{ try{ refreshRate(); }catch(e){} }, 150);
    }
  }
  try{ load2FA(); }catch(e){}
  try{ loadAudit(); }catch(e){}
  if(g('tgEnabled')) g('tgEnabled').checked = !!tg.enabled;
  if(g('autoAddOrders')){ g('autoAddOrders').checked = !!d.auto_add_orders; if(!GT_PAID){ g('autoAddOrders').disabled = true; g('autoAddOrders').parentElement.title = t('plus.needKey'); } }
  if(g('vaultEnabled')){ g('vaultEnabled').checked = !!d.vault_enabled; g('vaultEnabled').disabled = !d.vault_available; }
  const nt = d.notify || {};
  const map = {ntOrder:'order', ntMessage:'message', ntWatchdog:'watchdog', ntAgent:'agent',
               ntDigest:'digest', ntNew:'new', ntPrice:'price', ntRestock:'restock', ntDeal:'deal', ntDeadstock:'deadstock'};
  Object.keys(map).forEach(id => { if(g(id)) g(id).checked = !!nt[map[id]]; });
    if(g('tgPrice')) g('tgPrice').checked = tg.notify_price !== false;
    if(g('tgNew')) g('tgNew').checked = tg.notify_new !== false;
    if(g('tgMail')) g('tgMail').checked = tg.notify_mail !== false;
    if(g('tgStatus')) g('tgStatus').textContent = tg.configured
      ? ('✅ '+(LANG==='ru'?'настроено':LANG==='en'?'configured':'налаштовано')+(tg.enabled?(LANG==='ru'?' · включено':LANG==='en'?' · enabled':' · увімкнено'):(LANG==='ru'?' · отключено':LANG==='en'?' · disabled':' · вимкнено')))
      : (LANG==='ru'?'⚠ не настроено':LANG==='en'?'⚠ not configured':'⚠ не налаштовано');
    const gm = d.gmail || {};
    if(g('gmailUser')) g('gmailUser').value = gm.user || '';
    renderGmailInfo(gm);
    const au = d.auth || {};
    if(g('pwStatus')) g('pwStatus').textContent = d.auth_enabled ? t('pw.statusOn') : t('pw.statusOff');
    if(g('pwEnableBtn')) g('pwEnableBtn').style.display = d.auth_enabled ? 'none' : '';
    if(g('pwDisableBtn')) g('pwDisableBtn').style.display = d.auth_enabled ? '' : 'none';
    const am = g('authModeInfo');
    if(am){
      if(au.mode === 'off'){
        am.style.display='block';
        const _off = LANG==='ru'
          ? 'Доступ открыт для всех, у кого есть ссылка. Включите пароль, если приложение доступно из интернета.'
          : LANG==='en'
            ? 'Access is open to anyone with the link. Enable a password if the app is reachable from the internet.'
            : 'Доступ відкритий для всіх, хто має посилання. Увімкніть пароль, якщо застосунок доступний з інтернету.';
        am.innerHTML = '🔓 <b>'+t('pw.statusOff')+'</b>' + (au.access_required ? ' · Access header required' : '') + '. ' + _off;
      } else { am.style.display='none'; am.innerHTML=''; }
    }
    fetch('/api/tunnel').then(r=>r.json()).then(t=>{
      const el=g('tunnelInfo'); if(!el) return;
      el.innerHTML = (t && t.url)
        ? '🌐 '+(LANG==='ru'?'Туннель: ':LANG==='en'?'Tunnel: ':'Тунель: ')+'<a href="'+esc(t.url)+'" target="_blank" style="color:var(--a1)">'
          + esc(t.url.replace('https://','')) + '</a>'
        : (LANG==='ru'?'🌐 Туннель: адрес не найден (нет лога cloudflared)':LANG==='en'?'🌐 Tunnel: no address found (no cloudflared log)':'🌐 Тунель: адресу не знайдено (немає логу cloudflared)');
    }).catch(()=>{});
    if(g('statsTable') && g('tab-stats') && g('tab-stats').classList.contains('on')) renderStats();
    if(g('edList')) renderEldorado();
    // Якщо курс ще не заданий — тихо пробуємо взяти з НБУ
    if(!_rate){
      fetch('/api/rate').then(r=>r.json()).then(d=>{
        if(!d.ok) return;
        _rate = parseFloat(d.usd_uah)||0;
        if(g('rateVal')) g('rateVal').value = _rate?_rate.toFixed(2):'';
        if(g('rateInfo')) g('rateInfo').textContent = t('cur.updated')+' '+new Date((d.rate_ts||0)*1000).toLocaleString(dateLocale())+' · '+(d.source||'');
        if(g('edList')) renderEldorado();
        if(g('tab-stats') && g('tab-stats').classList.contains('on')) renderStats();
      }).catch(()=>{});
    }
    if(g('tab-setup') && g('tab-setup').classList.contains('on')) diagLoad();
  }catch(e){}
}

async function refreshRate(){
  try{
    if(_cur === 'USD'){
      _rate = 1;
      toast(t('cur.baseToast'));
      await loadSettings();
      return;
    }
    toast(t('cur.nbu'));
    const d = await fetch('/api/rate?refresh=1').then(r=>r.json());
    if(d.ok){ _rate = parseFloat(d.usd_uah)||0; toast(t('cur.refreshed')+' '+_rate.toFixed(2)+' '+curSym()); restoreMoneyText(); await loadSettings(); restoreMoneyText(); try{ convertMoneyText(document.body); }catch(e){} }
    else toast(t('cur.nbuFail'), false);
  }catch(e){ toast('⚠ '+e, false); }
}

async function saveRate(){
  const v = parseFloat(g('rateVal').value)||0;
  try{
    await fetch('/api/settings/save',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({usd_uah:v})});
    _rate = v;
    toast(t('cur.set')+': '+v.toFixed(2)+' '+curSym());
    await loadSettings(); renderStats();
  }catch(e){ toast('⚠ '+e, false); }
}

async function tgDisconnect(){
  const q = LANG==='ru' ? 'Отключить Telegram-бота?' : LANG==='en' ? 'Disconnect the Telegram bot?' : 'Відключити Telegram-бота?';
  if(!confirm(q)) return;
  try{
    const d = await fetch('/api/tg/save',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({clear:true})}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    toast(LANG==='ru'?'✅ Telegram отключён':LANG==='en'?'✅ Telegram disconnected':'✅ Telegram відключено');
    loadSettings();
  }catch(e){ toast('⚠ '+e, false); }
}
async function gmailDisconnect(){
  const q = LANG==='ru' ? 'Отключить Gmail?' : LANG==='en' ? 'Disconnect Gmail?' : 'Відключити Gmail?';
  if(!confirm(q)) return;
  try{
    const d = await fetch('/api/gmail/save',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({clear:true})}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    toast(LANG==='ru'?'✅ Gmail отключён':LANG==='en'?'✅ Gmail disconnected':'✅ Gmail відключено');
    loadSettings(); loadGmailStatus();
  }catch(e){ toast('⚠ '+e, false); }
}
async function saveTg(){
  const body = {
    token: (g('tgToken').value||'').trim(),
    chat_id: (g('tgChat').value||'').trim(),
    enabled: g('tgEnabled').checked,
    notify_mail: g('tgMail') ? g('tgMail').checked : true,
  };
  try{
    const d = await fetch('/api/tg/save',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify(body)}).then(r=>r.json());
    if(d.ok){ g('tgToken').value=''; toast('✅ Telegram збережено'); await loadSettings(); }
    else toast('⚠ '+(d.error||'помилка'), false);
  }catch(e){ toast('⚠ '+e, false); }
}

async function saveNotify(){
  const val = {
    order: !!(g('ntOrder') && g('ntOrder').checked),
    message: !!(g('ntMessage') && g('ntMessage').checked),
    watchdog: !!(g('ntWatchdog') && g('ntWatchdog').checked),
    agent: !!(g('ntAgent') && g('ntAgent').checked),
    digest: !!(g('ntDigest') && g('ntDigest').checked),
    new: !!(g('ntNew') && g('ntNew').checked),
    price: !!(g('ntPrice') && g('ntPrice').checked),
    restock: !!(g('ntRestock') && g('ntRestock').checked),
    deal: !!(g('ntDeal') && g('ntDeal').checked),
  };
  try{
    const d = await fetch('/api/settings/save',{method:'POST',headers:{'Content-Type':'application/json'},
      body: JSON.stringify({notify: val})}).then(r => r.json());
    if(!d.ok){ toast('⚠ ' + (d.error || 'помилка'), false); return; }
    const on = Object.keys(val).filter(k => val[k]).length;
    toast('✅ Сповіщення: увімкнено ' + on + ' з 9');
  }catch(e){ toast('⚠ ' + e, false); }
}

async function testTg(){
  try{
    toast('⏳ Надсилаю тест...');
    const d = await fetch('/api/tg/test',{method:'POST',headers:{'Content-Type':'application/json'},
      body:'{}'}).then(r=>r.json());
    toast(d.ok?'📨 Тест надіслано в Telegram!':'⚠ '+(d.error||'не вдалось'), !!d.ok);
  }catch(e){ toast('⚠ '+e, false); }
}

// ═══════════════════════════════════════════════
// 📧 GMAIL → TELEGRAM
// ═══════════════════════════════════════════════
function renderGmailInfo(gm){
  const el = g('gmailInfo');
  const badge = g('gmailBadge');
  if(badge) badge.textContent = gm && gm.configured
    ? ((LANG==='ru'?'проверка каждые ':LANG==='en'?'check every ':'перевірка кожні ')+Math.round((gm.interval||120)/60)+(LANG==='ru'?' мин':LANG==='en'?' min':' хв')) : '';
  if(!el) return;
  if(!gm || !gm.configured){
    el.innerHTML = LANG==='ru' ? '⚠ Gmail не настроен — уведомлений из почты не будет'
      : LANG==='en' ? '⚠ Gmail not configured — no mail notifications'
      : '⚠ Gmail не налаштовано — сповіщень з пошти не буде';
    return;
  }
  let s = '✅ ' + esc(gm.user || 'Gmail');
  if(gm.has_pass === false) s += ' · <span style="color:var(--yw)">'+(LANG==='ru'?'нет App Password':LANG==='en'?'no App Password':'немає App Password')+'</span>';
  if(gm.last_ok) s += ' · '+(LANG==='ru'?'проверено ':LANG==='en'?'checked ':'перевірено ') + new Date(gm.last_ok*1000).toLocaleString(dateLocale());
  if(gm.last_found) s += ' · '+(LANG==='ru'?'писем: ':LANG==='en'?'emails: ':'листів: ') + gm.last_found + ', '+(LANG==='ru'?'отправлено: ':LANG==='en'?'sent: ':'надіслано: ') + (gm.last_sent||0);
  if(gm.last_error) s += ' · <span style="color:var(--rd)">⚠ ' + esc(gm.last_error) + '</span>';
  el.innerHTML = s;
}

async function loadGmailStatus(){
  try{
    const d = await fetch('/api/gmail/status').then(r=>r.json());
    if(d && d.ok) renderGmailInfo(d);
  }catch(e){}
}

async function saveGmail(){
  const user = (g('gmailUser')?.value||'').trim();
  const password = (g('gmailPass')?.value||'').trim();
  if(!user){ toast('⚠ Введи Gmail-адресу', false); return; }
  try{
    toast('⏳ Перевіряю Gmail...');
    const d = await fetch('/api/gmail/save',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({user, password})}).then(r=>r.json());
    if(d.ok){
      g('gmailPass').value = '';
      toast('✅ Gmail підключено — сповіщення активні');
      loadGmailStatus();
    } else {
      let msg = d.error || '';
      if(/Gmail-адрес/i.test(msg)) msg = t('set.gmailBad');
      else if(/Нема що зберігати/i.test(msg)) msg = LANG==='ru'?'Введи адрес и пароль':LANG==='en'?'Enter the address and password':'Введи адресу і пароль';
      else if(/App Password/i.test(msg)) msg = LANG==='ru'?'Нужен App Password (16 символов)':LANG==='en'?'App Password required (16 characters)':'Потрібен App Password (16 символів)';
      toast('⚠ '+msg, false);
    }
  }catch(e){ toast('⚠ '+e, false); }
}

async function checkGmailNow(){
  try{
    toast('⏳ Перевіряю пошту...');
    const d = await fetch('/api/gmail/check',{method:'POST',headers:{'Content-Type':'application/json'},
      body:'{}'}).then(r=>r.json());
    if(d.ok) toast('📧 Листів: '+(d.found||0)+' · надіслано: '+(d.sent||0));
    else toast('⚠ '+(d.error||'помилка'), false);
    loadGmailStatus();
  }catch(e){ toast('⚠ '+e, false); }
}

async function saveCloud(){
  try{
    await fetch('/api/settings/save',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({cloud_dir:(g('cloudDir').value||'').trim()})});
    toast('✅ Папку хмари збережено');
    await loadSettings();
  }catch(e){ toast('⚠ '+e, false); }
}

async function changePassword(){
  const old = (g('pwOld').value||'');
  const n1  = (g('pwNew').value||'');
  const n2  = (g('pwNew2').value||'');
  if(n1.length < 8){ toast(t('pw.short'), false); return; }
  if(n1 !== n2){ toast(t('pw.mismatch'), false); return; }
  try{
    const d = await fetch('/api/auth/password',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({old,new:n1})}).then(r=>r.json());
    if(d.ok){
      g('pwOld').value=''; g('pwNew').value=''; g('pwNew2').value='';
      toast(t('pw.changed'));
      setTimeout(()=>location.reload(), 1100);
    } else {
      let msg = d.error || '';
      if(d.reason === 'auth_off') msg = LANG==='ru' ? 'Пароль отключён. Включите его в блоке «Пароль» выше.' : LANG==='en' ? 'Password is disabled. Enable it in the Password block above.' : 'Пароль вимкнено. Увімкніть його в блоці «Пароль» вище.';
      else if(/Невірний/i.test(msg)) msg = LANG==='ru' ? 'Неверный текущий пароль' : LANG==='en' ? 'Wrong current password' : 'Невірний поточний пароль';
      else if(/мінімум 8/i.test(msg)) msg = t('pw.short');
      toast('⚠ '+msg, false);
    }
  }catch(e){ toast('⚠ '+e, false); }
}

async function saveHttps(){
  try{
    const d = await fetch('/api/https/save',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        enabled: g('httpsEnabled').checked,
        cert: (g('httpsCert').value||'').trim(),
        key:  (g('httpsKey').value||'').trim(),
      })}).then(r=>r.json());
    if(d.ok){ toast('✅ HTTPS-налаштування збережено. Перезапусти трекер.'); await loadSettings(); }
    else toast('⚠ '+(d.error||'помилка'), false);
  }catch(e){ toast('⚠ '+e, false); }
}

async function genHttps(){
  try{
    toast(t('loading'));
    const d = await fetch('/api/https/generate',{method:'POST',headers:{'Content-Type':'application/json'},
      body:'{}'}).then(r=>r.json());
    if(d.ok){
      g('httpsCert').value = d.cert;
      g('httpsKey').value = d.key;
      toast(t('set.certCreated'));
    } else {
      const er = String(d.error || '');
      const msg = /openssl/i.test(er)
        ? (LANG==='ru'?'OpenSSL не найден. Установи OpenSSL или укажи cert/key вручную.':LANG==='en'?'OpenSSL not found. Install OpenSSL or specify cert/key manually.':'OpenSSL не знайдено. Встанови OpenSSL або вкажи cert/key вручну.')
        : (LANG==='ru'?'Не удалось создать сертификат.':LANG==='en'?'Could not create the certificate.':'Не вдалося створити сертифікат.');
      toast('⚠ '+msg, false);
    }
  }catch(e){ toast('⚠ '+e, false); }
}

function openBulkRename(){
  // Групуємо записи без назви по сумі продажу + платформа
  const noTitle = purchases.filter(p=>!(p.title||'').trim());
  if(!noTitle.length){toast(t('deal.bulkNoTitles'));return;}

  // Групуємо по ключу src+sell (округлено до цента)
  const groups = {};
  noTitle.forEach(p=>{
    const key = `${p.src||'zeusx'}|${(p.sell||0).toFixed(2)}`;
    if(!groups[key]) groups[key]={src:p.src,sell:p.sell,count:0,dates:[],ids:[]};
    groups[key].count++;
    if(groups[key].dates.length<3) groups[key].dates.push(p.date||'');
    groups[key].ids.push(p.id);
  });

  // Сортуємо по кількості (найчастіші зверху)
  const sorted = Object.entries(groups).sort((a,b)=>b[1].count-a[1].count);

  const srcIcon = s=>s==='funpay'?'🔵':'⚡';
  let html = sorted.map(([key,g])=>`
    <div style="display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:1px solid var(--brd)">
      <div style="min-width:140px;font-size:11px">
        <span style="font-family:var(--font);font-weight:700;color:var(--gr)">$${parseFloat(g.sell).toFixed(2)}</span>
        <span style="color:var(--mu);margin-left:6px">${srcIcon(g.src)} ×${g.count}</span>
        <div style="font-size:9px;color:var(--mu)">${g.dates.join(', ')}</div>
      </div>
      <input data-key="${key}" placeholder="${t('deal.bulkPlaceholder')}" style="flex:1;font-size:12px;padding:4px 8px;background:var(--card2);border:1px solid var(--brd);border-radius:5px;color:var(--tx)">
    </div>`).join('');

  g('bulkRenameList').innerHTML = html || '<div style="color:var(--mu);text-align:center;padding:20px">'+t('deal.bulkEmpty')+'</div>';
  g('bulkRenameModal').style.display = 'flex';
}

async function applyBulkRename(){
  const inputs = g('bulkRenameList').querySelectorAll('input[data-key]');
  let changed = 0;
  inputs.forEach(inp=>{
    const title = inp.value.trim();
    if(!title) return;
    const [src, sell] = inp.dataset.key.split('|');
    const sellVal = parseFloat(sell);
    purchases.forEach(p=>{
      if((p.title||'').trim()) return;
      if((p.src||'zeusx')===src && Math.abs((p.sell||0)-sellVal)<0.01){
        p.title = title;
        changed++;
      }
    });
  });
  if(changed){
    await savePL();
    renderPurchases();
    renderStats();
    g('bulkRenameModal').style.display='none';
    toast(t('deal.bulkDone').replace('%s', changed));
  } else {
    toast(t('deal.bulkNeedName'));
  }
}

function openBulkFee(){
  const list = (plFilt||[]).slice();
  if(!list.length){ toast(t('deal.bulkEmpty'), false); return; }
  const el=g('bulkFeeCount');
  if(el) el.textContent = list.length + ' ' + t('deal.bulkFeeCount');
  const inp=g('bulkFeePct'); if(inp) inp.value='';
  g('bulkFeeModal').style.display='flex';
  setTimeout(()=>{ try{ g('bulkFeePct').focus(); }catch(e){} }, 100);
}
async function applyBulkFee(){
  const pct=parseFloat(g('bulkFeePct')?.value);
  if(!Number.isFinite(pct) || pct<0 || pct>100){ toast(t('deal.bulkFeeNeed'), false); return; }
  const list=(plFilt||[]).slice();
  if(!list.length){ toast(t('deal.bulkEmpty'), false); return; }
  if(!confirm(t('deal.bulkFeeConfirm').replace('%s', pct).replace('%n', list.length))) return;
  let changed=0, edChanged=0;
  const f=pct/100;
  list.forEach(p=>{
    if(p._ed){
      const s=(edSales||[]).find(x=>String(x.id)===String(p._edId));
      if(s){
        s.fee=Math.round(Number(s.price||0)*f*100)/100;
        s.profit=Math.round((Number(s.price||0)-Number(s.fee||0)-Number(s.buy||0))*100)/100;
        edChanged++;
      }
    } else {
      p.feePct=Math.round(f*1000000)/1000000;
      p.afterFee=Math.round((Number(p.sell||0)*(1-f)-Number(p.buy||0))*10000)/10000;
      changed++;
    }
  });
  if(edChanged) await saveED();
  if(changed) await savePL();
  g('bulkFeeModal').style.display='none';
  renderPurchases();
  if(typeof renderStats==='function') renderStats();
  if(typeof renderEldorado==='function') renderEldorado();
  toast(t('deal.bulkFeeDone').replace('%s', changed+edChanged));
}

async function syncPLToServer(){
  try{
    // Явна дія користувача: відправляємо поточний стан (без «воскрешання»
    // видалених записів із localStorage — це вже одного разу губило дані)
    const resp = await fetch('/api/pl/save',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({purchases, force: purchases.length === 0})
    });
    const result = await resp.json().catch(()=>({}));
    if(resp.ok && result.ok){
      _plDirty = false;
      renderPurchases();
      toast(t('deal.synced').replace('%s', purchases.length));
    } else {
      toast('⚠ ' + (result.error||resp.status), false);
    }
  }catch(e){
    console.error('Sync error:', e);
    toast(t('deal.syncError')+' '+e, false);
  }
}

const PL_INFO = {
  zeusx:{name:'ZeusX', logo:'/logo/zeusx.png'},
  funpay:{name:'FunPay', logo:'/logo/funpay.png'},
  eldorado:{name:'Eldorado', logo:'/logo/eldorado.png'},
  other:{name:'Інше', logo:''}
};
function plPlatToggle(ev){
  if(ev) ev.stopPropagation();
  const el = g('plPlatSel'); if(!el) return;
  el.classList.toggle('open');
}
function plPlatPick(val){
  const hid = g('plPlatform'), info = PL_INFO[val] || PL_INFO.other;
  if(hid) hid.value = val;
  if(g('plPlatName')) g('plPlatName').textContent = val==='other' ? t('f.other2') : info.name;
  const lg = g('plPlatLogo');
  if(lg){
    if(info.logo){ lg.style.display=''; lg.src = info.logo; }
    else { lg.style.display='none'; }
  }
  document.querySelectorAll('#plPlatSel .psel-opt').forEach(o=>o.classList.toggle('on', o.dataset.val===val));
  const el = g('plPlatSel'); if(el) el.classList.remove('open');
  const fp = g('plFeePct');
  const zw = g('plZeusRankWrap');
  if(zw) zw.style.display = val==='zeusx' ? '' : 'none';
  if(val==='zeusx'){
    fillZeusRanks();
    const tier=zeusxTiers().find(x=>x.id===_zeusxTier) || zeusxTiers()[0];
    const sel=g('plZeusRank');
    if(sel) sel.value=tier.id;
    if(fp) fp.value=(tier.fee*100).toFixed(1).replace(/\.0$/,'');
  } else if(fp){
    fp.value=(defaultFeePct(val, g('plTitle')?.value||'')*100).toFixed(1).replace(/\.0$/,'');
  }
  try{ updateFeePreview(); }catch(e){}
}
document.addEventListener('click', (e)=>{
  const el = g('plPlatSel');
  if(el && !el.contains(e.target)) el.classList.remove('open');
});
try{ plPlatPick(g('plPlatform')?.value || 'zeusx'); }catch(e){}

async function addPLRecord(){
  const sell = parseFloat(g('plSell').value)||0;
  const buy  = parseFloat(g('plBuy').value)||0;
  if(!sell && !buy){ alert(t('deal.enterPrices')); return; }
  const plat = g('plPlatform').value;
  const feeRaw = parseFloat(g('plFeePct')?.value);
  const fee  = Number.isFinite(feeRaw) ? Math.max(0, Math.min(100, feeRaw))/100 : defaultFeePct(plat);
  const expenses = Math.max(0, parseFloat(g('plExpenses')?.value)||0);
  const dealCur = (g('plCur')?.value || 'USD').toUpperCase().slice(0,3);
  const dealFx = Math.max(0.000001, parseFloat(g('plFx')?.value) || 1);
  const buyUsd = buy / dealFx, sellUsd = sell / dealFx, expUsd = expenses / dealFx;
  const invId = _invSellId;

  if(plat === 'eldorado'){
    // Eldorado веде окремий облік — пишемо туди, щоб не було дублів
    const rec = { id: Date.now(), date: g('plDate')?.value || todayLocal(),
      title: g('plTitle')?.value.trim() || 'Eldorado', price: sellUsd, buy: buyUsd,
      fee: Math.round(sellUsd*fee*100)/100,
      profit: Math.round((sellUsd - sellUsd*fee - buyUsd)*100)/100,
      currency: dealCur, fxRate: dealFx, origPrice: sell, origBuy: buy,
      orderId: '', category: 'Eldorado' };
    edSales.unshift(rec);
    await saveED();
    if(invId) await markInvSold(invId);
    await finishMailDraft();
    g('plTitle').value=''; g('plBuy').value=''; g('plSell').value='';
    g('plExpenses').value='0';
    g('plFeePreview').textContent='$0.00';
    if(g('plNetPreview')) g('plNetPreview').textContent='$0.00';
    plPlatPick(plat);
    plPg=1; renderPurchases();
    if(typeof renderEldorado==='function') renderEldorado();
    toast(t('deal.addedED'));
    return;
  }
  const afterFee = sellUsd*(1-fee) - buyUsd;
  purchases.unshift({
    id: Date.now(),
    title: g('plTitle').value.trim(),
    src: plat,
    srcName: plat==='zeusx'?'ZeusX':plat==='funpay'?'FunPay':plat==='eldorado'?'Eldorado':t('f.other2'),
    buy: buyUsd, sell: sellUsd, feePct: Math.round(fee*1000000)/1000000,
    expenses: Math.round(expUsd*100)/100,
    afterFee: Math.round(afterFee*10000)/10000,
    currency: dealCur, fxRate: dealFx,
    origBuy: buy, origSell: sell, origExpenses: expenses,
    qty: 1,
    date: g('plDate').value || todayLocal(),
    platform: plat,
    ...(invId ? {inventoryId: invId} : {}),
  });
  await savePL();
  if(invId) await markInvSold(invId);
  await finishMailDraft();
  g('plTitle').value=''; g('plBuy').value=''; g('plSell').value='';
  g('plExpenses').value='0';
  g('plFeePreview').textContent='$0.00';
  if(g('plNetPreview')) g('plNetPreview').textContent='$0.00';
  plPlatPick(plat);
  plPg=1; renderPurchases();
  toast(t('deal.added'));
  // v4.6: без Telegram-сповіщення — це ручне внесення, користувач і так знає
}

async function delPurchase(id){
  if(!confirm(t('deal.deleteConfirm'))) return;
  purchases = purchases.filter(p=>p.id!==id);
  await savePL(); renderPurchases();
}

function edAsPL(){
  return (edSales||[]).map(s=>({
    id: 'ed:' + s.id, date: s.date, title: s.title,
    src: 'eldorado', srcName: 'Eldorado',
    buy: Number(s.buy||0), sell: Number(s.price||0),
    afterFee: Number(s.profit||0), fee: Number(s.fee||0), expenses: 0,
    feePct: Number(s.price||0)>0 ? Math.max(0, Math.min(1, Number(s.fee||0)/Number(s.price||1))) : ED_FEE,
    qty: 1, platform: 'eldorado',
    _ed: true, _edId: s.id
  }));
}

function allDeals(){
  return (purchases||[]).concat(edAsPL());
}

function renderPurchases(){
  fillMonthOptions();
  const q   = (g('purQ')?.value||'').toLowerCase();
  const sf  = g('purFilter')?.value||'';
  const df  = g('plDateFilter')?.value||'';
  const srt = g('plSortF')?.value||'date_d';
  const now = new Date();
  const todayStr = localDate(now);
  const wkStart = new Date(now); wkStart.setDate(now.getDate()-now.getDay());
  const moStart = todayStr.slice(0,7);

  plFilt = allDeals().filter(p=>{
    if(sf==='notitle') return !(p.title||'').trim();
    if(sf && p.src!==sf) return false;
    if(q && !(p.title||'').toLowerCase().includes(q) && !(p.srcName||'').toLowerCase().includes(q)) return false;
    if(df){
      const d = p.date||'';
      if(df==='today' && d!==todayStr) return false;
      if(df==='week' && d<localDate(wkStart)) return false;
      if(df==='month' && !d.startsWith(moStart)) return false;
      if(df.startsWith('m:') && !d.startsWith(df.slice(2))) return false;
      if(df==='custom'){
        const from=g('plDateFrom')?.value||'';
        const to=g('plDateTo')?.value||'';
        if(from && d<from) return false;
        if(to && d>to) return false;
      }
    }
    return true;
  });

  // Sort
  if(srt==='date_d') plFilt=[...plFilt].sort((a,b)=>(b.date||'').localeCompare(a.date||''));
  else if(srt==='date_a') plFilt=[...plFilt].sort((a,b)=>(a.date||'').localeCompare(b.date||''));
  else if(srt==='profit_d') plFilt=[...plFilt].sort((a,b)=>(b.afterFee||0)-(a.afterFee||0));
  else if(srt==='sell_d') plFilt=[...plFilt].sort((a,b)=>(b.sell||0)-(a.sell||0));

  // Stats
  const totalSell   = plFilt.reduce((s,p)=>s+(p.sell||0),0);
  const totalBuy    = plFilt.reduce((s,p)=>s+(p.buy||0),0);
  const totalExpenses = plFilt.reduce((s,p)=>s+Number(p.expenses||0),0);
  const totalProfit = plFilt.reduce((s,p)=>s+(p.afterFee||0)-Number(p.expenses||0),0);
  const totalFees   = plFilt.reduce((s,p)=>s+(p.sell||0)*feePctOf(p),0);
  const margin      = totalBuy>0?(totalProfit/totalBuy*100).toFixed(1):0;

  g('purCnt').textContent = plFilt.length;
  if(g('plProfit')){
    g('plProfit').textContent=(totalProfit>=0?'+':'-')+locMoney(Math.abs(totalProfit));
    g('plProfit').style.color=totalProfit>0?'var(--gr)':totalProfit<0?'var(--rd)':'var(--mu)';
    g('plRevenue').textContent=locMoney(totalSell);
    g('plCost').textContent=locMoney(totalBuy);
    g('plMargin').textContent=fmtPct(margin);
    g('plMargin').style.color=parseFloat(margin)>0?'var(--gr)':'var(--mu)';
    g('plCount').textContent=plFilt.length;
    g('plFees').textContent=locMoney(totalFees);
    if(g('plExpenses')) g('plExpenses').textContent=locMoney(totalExpenses);
  }

  refreshCombinedStats();

  // Render rows
  const pp=50, page=plFilt.slice((plPg-1)*pp, plPg*pp);
  const el=g('purList');
  if(!el) return;
  if(!page.length){el.innerHTML='<div class="none">Записів не знайдено</div>';g('plPag').style.display='none';return;}

  const inpStyle='width:100%;background:var(--bg2);border:1px solid var(--a1);border-radius:4px;color:var(--tx);padding:2px 4px;font-size:11px;font-family:inherit';
  el.innerHTML = '<div class="bub-wrap">' + page.map(p=>{
    const _fp=feePctOf(p);
    const fee=p._ed?Number(p.fee||0):(p.sell||0)*_fp;
    const exp=Number(p.expenses||0);
    const profit=(p.afterFee!=null?p.afterFee:((p.sell||0)*(1-_fp)-(p.buy||0)))-exp;
    const platClr=p._ed?'var(--yw)':p.src==='zeusx'?'var(--a1)':p.src==='funpay'?'var(--a3)':'var(--mu)';
    const LOGO2={zeusx:'/logo/zeusx.png',funpay:'/logo/funpay.png',eldorado:'/logo/eldorado.png'};
    const logoImg=LOGO2[p.src]?'<img src="'+LOGO2[p.src]+'" alt="" style="width:13px;height:13px;border-radius:3px;object-fit:contain;vertical-align:-2px;margin-right:4px">':'';
    if(_editId===p.id){
      return '<div class="bub" style="border-color:color-mix(in srgb, var(--a1) 55%, transparent)">'
        + '<div style="display:flex;flex-direction:column;gap:8px">'
        + '<input id="ei_date" value="'+esc(p.date||'')+'" type="date" style="'+inpStyle+'">'
        + '<input id="ei_title" value="'+esc(p.title||'')+'" placeholder="Назва" style="'+inpStyle+'">'
        + '<select id="ei_plat" style="'+inpStyle+'"><option value="zeusx"'+(p.src==='zeusx'?' selected':'')+'>⚡ ZeusX</option><option value="funpay"'+(p.src==='funpay'?' selected':'')+'>🔵 FunPay</option><option value="other"'+(p.src==='other'?' selected':'')+' data-i18n="f.other2">Інше</option></select>'
        + '<input id="ei_feePct" value="'+(feePctOf(p)*100).toFixed(2).replace(/\.?0+$/,'')+'" type="number" step="0.1" min="0" max="100" placeholder="Комісія %" style="'+inpStyle+'">'
        + '<input id="ei_expenses" value="'+Number(p.expenses||0).toFixed(2)+'" type="number" step="0.01" min="0" placeholder="Інші витрати" style="'+inpStyle+'">'
        + '<div style="display:flex;gap:8px"><input id="ei_buy" value="'+(p.buy||0).toFixed(2)+'" type="number" step="0.01" placeholder="Купив" style="'+inpStyle+';flex:1"><input id="ei_sell" value="'+(p.sell||0).toFixed(2)+'" type="number" step="0.01" placeholder="Продав" style="'+inpStyle+';flex:1"></div>'
        + '<div style="display:flex;gap:8px">'
        + '<button onclick="saveEdit('+p.id+')" style="flex:1;background:var(--gr);border:none;color:#000;padding:9px;border-radius:8px;font-size:13px;cursor:pointer;font-weight:700">✓ Зберегти</button>'
        + '<button onclick="cancelEdit()" style="flex:1;background:transparent;border:1px solid var(--brd);color:var(--mu);padding:9px;border-radius:8px;font-size:13px;cursor:pointer">✕ Скасувати</button>'
        + '</div></div></div>';
    }
    return '<div class="bub">'
      + '<div class="bub-head">'
      + '<span class="bub-date">'+esc(fmtDate(p.date))+'</span>'
      + '<span class="bub-chip" style="color:'+platClr+'">'+logoImg+esc(p.srcName||p.src)+'</span>'
      + '<span class="bub-title">'+esc(p.title||'—')+'</span>'
      + '<div class="bub-acts">'
      + (p._ed
          ? '<button class="bub-btn" onclick="editEdSale('+p._edId+')" title="Редагувати">✏</button>'
            + '<button class="bub-btn del" onclick="delEdSale('+p._edId+')" title="Видалити">🗑</button>'
          : '<button class="bub-btn" onclick="startEdit('+p.id+')" title="Редагувати">✏</button>'
            + '<button class="bub-btn del" onclick="delPurchase('+p.id+')" title="Видалити">🗑</button>')
      + '</div></div>'
      + (()=>{
          const dcur=p.currency||'USD';
          const hasOrig=p.origBuy!=null || p.origSell!=null;
          const m=v=>hasOrig ? dealMoney(v,dcur) : '$'+Number(v||0).toFixed(2);
          const dFee=hasOrig ? fee*(Number(p.fxRate)||1) : fee;
          const dExp=hasOrig ? Number(p.origExpenses!=null?p.origExpenses:exp*(Number(p.fxRate)||1)) : exp;
          const dProfit=hasOrig ? ((Number(p.afterFee)||0)-exp)*(Number(p.fxRate)||1) : profit;
          return '<div class="bub-stats">'
            + '<span class="bs">'+t('k.buy')+' <b>'+m(hasOrig?p.origBuy:p.buy)+'</b></span>'
            + '<span class="bs">'+t('k.sell')+' <b>'+m(hasOrig?p.origSell:p.sell)+'</b></span>'
            + '<span class="bs">'+t('k.fee')+' <b class="neg">-'+m(dFee)+'</b></span>'
            + (dExp>0 ? '<span class="bs">'+t('k.expenses')+' <b class="neg">-'+m(dExp)+'</b></span>' : '')
            + '<span class="bs '+(dProfit>=0?'pos':'negp')+'">'+t('k.net')+' <b>'+(dProfit>=0?'+':'')+m(dProfit)+'</b></span>'
            + '</div></div>';
        })()
  }).join('') + '</div>';

  // Pagination
  const tot=Math.ceil(plFilt.length/pp), pag=g('plPag');
  if(tot<=1){pag.style.display='none';return;}
  let h='';
  if(plPg>1)h+=`<button class="pb" onclick="plGo(${plPg-1})">←</button>`;
  const s=Math.max(1,plPg-2),en=Math.min(tot,plPg+2);
  for(let i=s;i<=en;i++)h+=`<button class="pb${i===plPg?' on':''}" onclick="plGo(${i})">${i}</button>`;
  if(plPg<tot)h+=`<button class="pb" onclick="plGo(${tot})">→</button>`;
  h+=`<span style="font-size:10px;color:var(--mu)">${plFilt.length} ${plural(plFilt.length,'records')}</span>`;
  pag.innerHTML=h; pag.style.display='flex';
}
function plGo(n){plPg=n;renderPurchases();window.scrollTo({top:0,behavior:'smooth'});}



// ═══════════════════════════════════════════════
// 📊 СТАТИСТИКА ПО ІГРАХ
// ═══════════════════════════════════════════════
let _statsChart = null;

async function loadAgentCfg(){
  if(!g('agentServer')) return;
  try{
    const d=await fetch('/api/taobao/agent-config').then(r=>r.json());
    if(!d.ok) return;
    g('agentServer').textContent=d.server||'—';
    g('agentToken').textContent=d.token||'—';
  }catch(e){}
}
async function copyAgent(id){
  const el=g(id); if(!el) return;
  const txt=el.textContent||'';
  try{ await navigator.clipboard.writeText(txt); toast('✅ Скопійовано'); }
  catch(e){ prompt('Скопіюй:', txt); }
}
let _impRows=[];
function parseCsvText(text){
  const rows=[]; let row=[], cur='', q=false;
  for(let i=0;i<text.length;i++){
    const ch=text[i];
    if(q){
      if(ch==='"' && text[i+1]==='"'){ cur+='"'; i++; }
      else if(ch==='"'){ q=false; }
      else cur+=ch;
    } else {
      if(ch==='"'){ q=true; }
      else if(ch===','){ row.push(cur); cur=''; }
      else if(ch==='\n'){ row.push(cur); rows.push(row); row=[]; cur=''; }
      else if(ch!=='\r'){ cur+=ch; }
    }
  }
  row.push(cur); if(row.some(x=>String(x).trim())) rows.push(row);
  return rows;
}
function _num(s){ return parseFloat(String(s==null?'':s).replace(/[^0-9.,-]/g,'').replace(',', '.'))||0; }
function _date(s){
  const v=String(s||'').trim();
  if(/^\d{4}-\d{2}-\d{2}/.test(v)) return v.slice(0,10);
  const m=v.match(/^(\d{1,2})[./](\d{1,2})[./](\d{2,4})/);
  if(m){ const y=m[3].length===2?'20'+m[3]:m[3]; return y+'-'+String(m[2]).padStart(2,'0')+'-'+String(m[1]).padStart(2,'0'); }
  return new Date().toISOString().slice(0,10);
}
async function importCsvFile(input){
  const f=input.files&&input.files[0]; if(!f) return;
  const text=await f.text();
  const rows=parseCsvText(text);
  if(rows.length<2){ toast('⚠ '+t('imp.emptyCsv'), false); return; }
  const hdr=rows[0].map(x=>String(x).trim().toLowerCase());
  const col=function(){ for(let i=0;i<arguments.length;i++){ const k=arguments[i]; const ix=hdr.findIndex(h=>h===k||h.includes(k)); if(ix>=0) return ix; } return -1; };
  const ci={date:col('date','created','sale date'),title:col('title','item','product','name','description'),price:col('price','amount','total','gross'),fee:col('fee','commission'),order:col('order','id')};
  if(ci.title<0||ci.price<0){ toast('⚠ '+t('imp.noColumns'), false); return; }
  const plat=g('impPlatform').value;
  const def=Number((FEE_CFG.fees||{})[plat]||0);
  _impRows=rows.slice(1).map(function(r){
    const sell=_num(r[ci.price]); if(!(sell>0)) return null;
    const feeV=ci.fee>=0?_num(r[ci.fee]):sell*def;
    const fee=Math.max(0,Math.min(sell,feeV));
    return {date:_date(ci.date>=0?r[ci.date]:''),title:String(ci.title>=0?r[ci.title]:'Import').slice(0,200),
            sell:sell,fee:fee,feePct:sell>0?fee/sell:0,order:ci.order>=0?String(r[ci.order]||''):'',platform:plat};
  }).filter(Boolean).slice(0,1000);
  if(!_impRows.length){ toast('⚠ '+t('imp.noRows'), false); return; }
  // автоматичний матчинг зі складом (перші 100 рядків, без повторного використання однієї позиції)
  const used=new Set(); let matched=0;
  for(let i=0;i<Math.min(_impRows.length,100);i++){
    const x=_impRows[i];
    try{
      const q=encodeURIComponent(x.title||'');
      if(q){
        const mm=await fetch('/api/inventory/match?title='+q).then(r=>r.json());
        const hit=(mm.matches||[]).find(z=>!used.has(String(z.id)));
        if(hit){
          used.add(String(hit.id));
          x.buy=Number(hit.cost||0); x.inventoryId=hit.id; x.matchTitle=hit.title; matched++;
        }
      }
    }catch(e){}
  }
  g('impRun').style.display='inline-flex';
  g('impInfo').textContent=f.name+' · '+_impRows.length+' · '+t('imp.foundCost')+': '+matched;
  g('impPreview').innerHTML='<div style="overflow-x:auto"><table class="sup-table"><thead><tr><th>'+t('imp.titleCol')+'</th><th>'+t('imp.name')+'</th><th>'+t('imp.price')+'</th><th>'+t('imp.fee')+'</th><th>'+t('imp.cost')+'</th><th>'+t('imp.stock')+'</th></tr></thead><tbody>'+
    _impRows.slice(0,20).map(function(x){return '<tr><td>'+esc(x.date)+'</td><td>'+esc(x.title)+'</td><td>$'+x.sell.toFixed(2)+'</td><td>$'+x.fee.toFixed(2)+'</td><td>'+(x.buy?'$'+Number(x.buy).toFixed(2):'<span style="color:var(--rd)">—</span>')+'</td><td>'+esc(x.matchTitle||'—')+'</td></tr>';}).join('')+
    '</tbody></table></div>'+( _impRows.length>20?'<div style="font-size:10px;color:var(--mu);margin-top:4px">…ще '+(_impRows.length-20)+'</div>':'');
}
async function runSalesImport(){
  if(!_impRows.length) return;
  const plat=g('impPlatform').value;
  let added=0, skipped=0;
  const newRecords=[];
  _impRows.forEach(function(x){
    if(x.order && purchases.some(p=>String(p.orderId||'')===x.order)){ skipped++; return; }
    const after=x.sell*(1-x.feePct)-(x.buy||0);
    const rec={id:Date.now()+added,title:x.title,src:plat,srcName:(FEE_CFG.marketplaces||[]).find(m=>m.id===plat)?.name||plat,
      buy:Number(x.buy||0),sell:x.sell,feePct:x.feePct,expenses:0,afterFee:after,currency:'USD',fxRate:1,
      orderId:x.order,date:x.date,platform:plat,imported:true,needsCost:!x.buy,
      ...(x.inventoryId?{inventoryId:x.inventoryId}:{})};
    purchases.unshift(rec);
    newRecords.push({id:rec.id, x, after});
    added++;
  });
  await savePL();
  let holds=0;
  if(g('impCashflow')?.checked){
    for(const rec of newRecords){
      try{
        const r=await fetch('/api/cashflow/add',{method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify({platform:plat,amount:Math.max(0,rec.after),status:'hold',date:rec.x.date,
            note:rec.x.title,saleId:'pl:'+rec.id,order:rec.x.order||''})});
        const d=await r.json().catch(()=>({}));
        if(d.ok) holds++;
      }catch(e){}
    }
  }
  for(const x of _impRows){
    if(x.inventoryId){
      try{ await fetch('/api/inventory/status',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({id:x.inventoryId,status:'sold'})}); }catch(e){}
    }
  }
  try{ loadInventory().catch(()=>{}); }catch(e){}
  renderPurchases();
  toast('✅ '+t('imp.imported')+': '+added+(skipped?' · '+t('imp.skipped')+': '+skipped:'')+(holds?' · Hold: '+holds:''));
  _impRows=[]; g('impRun').style.display='none'; g('impInfo').textContent=''; g('impPreview').innerHTML='';
  if(g('impFile')) g('impFile').value='';
}
const CF_NAMES={g2g:'G2G',gameflip:'Gameflip',pa:'PlayerAuctions',zeusx:'ZeusX',funpay:'FunPay',eldorado:'Eldorado',other:'Інше'};
async function loadCashflow(){
  const el=g('cfList'); if(!el) return;
  try{
    const d=await fetch('/api/cashflow').then(r=>r.json());
    const it=d.items||[], tot=d.totals||{};
    if(g('cfCards')) g('cfCards').innerHTML=[
      [t('cf.hold'),'hold','var(--yw)'],[t('cf.available'),'available','var(--gr)'],[t('cf.withdrawn'),'withdrawn','var(--a1)'],[t('cf.total'),'all','var(--tx)']
    ].map(function(a){var k=a[0],key=a[1],c=a[2];return '<div style="background:var(--card2);border:1px solid var(--brd);border-radius:9px;padding:8px 12px;min-width:110px"><div style="font-size:10px;color:var(--mu)">'+k+'</div><div style="font-size:17px;font-weight:800;color:'+c+'">$'+Number(key==='all'?d.all:(tot[key]||0)).toFixed(2)+'</div></div>';}).join('');
    if(!it.length){ el.innerHTML='<div class="none">'+esc(t('cf.empty'))+'</div>'; return; }
    var rows=it.slice().reverse().map(function(x){
      var id=esc(x.id);
      const _st=(x.status||'hold'); const stLbl=t('cf.'+_st)||_st;
      return '<tr><td>'+esc(x.date||'')+'</td><td>'+esc(CF_NAMES[x.platform]||x.platform||'—')+'</td><td>$'+Number(x.amount||0).toFixed(2)+'</td><td>'+esc(stLbl)+'</td><td>'+esc(x.availableDate||'—')+'</td><td>'+esc((x.note||'').substring(0,60))+'</td><td style="white-space:nowrap">'
        +'<button class="btn" style="padding:3px 7px;font-size:10px" onclick="cashflowSet(\''+id+'\',\'available\')">A</button> '
        +'<button class="btn" style="padding:3px 7px;font-size:10px" onclick="cashflowSet(\''+id+'\',\'withdrawn\')">W</button> '
        +'<button class="btn rd" style="padding:3px 7px;font-size:10px" onclick="cashflowDel(\''+id+'\')">✕</button>'
        +'</td></tr>';
    }).join('');
    el.innerHTML='<div style="overflow-x:auto"><table class="sup-table"><thead><tr><th>'+t('cf.date')+'</th><th>'+t('cf.platform')+'</th><th>'+t('cf.amount')+'</th><th>'+t('cf.status')+'</th><th>'+t('cf.availableDate')+'</th><th>'+t('cf.note')+'</th><th></th></tr></thead><tbody>'+rows+'</tbody></table></div>';
  }catch(e){ el.innerHTML='<div class="none">⚠ '+esc(String(e))+'</div>'; }
}
async function cashflowAdd(){
  const amount=Number(g('cfAmount')?.value||0);
  if(!(amount>0)){ toast('⚠ '+t('cf.amountRequired'), false); return; }
  const body={platform:g('cfPlatform')?.value||'other',amount,status:g('cfStatus')?.value||'hold',
    date:g('cfDate')?.value||new Date().toISOString().slice(0,10),note:g('cfNote')?.value||'',
    availableDate:g('cfAvailable')?.value||''};
  try{
    const d=await fetch('/api/cashflow/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    g('cfAmount').value=''; g('cfNote').value='';
    await loadCashflow();
  }catch(e){ toast('⚠ '+e, false); }
}
async function saveBackupSettings(){
  const body={backup_hours:Math.max(1,Math.min(168,parseFloat(g('backupHours')?.value||24)||24)),
              backup_keep:Math.max(1,Math.min(365,parseInt(g('backupKeep')?.value||30)||30))};
  try{
    const d=await fetch('/api/settings/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(r=>r.json());
    toast(d.ok?'✅ Розклад бекапів збережено':'⚠ '+(d.error||''), !!d.ok);
    loadSettings();
  }catch(e){ toast('⚠ '+e, false); }
}
async function saveBackupEncryption(){
  const en=!!g('backupEncrypt')?.checked;
  const pw=String(g('backupPass')?.value||'');
  if(en && !pw){ toast('⚠ Введи пароль шифрування', false); return; }
  try{
    const d=await fetch('/api/backup/encrypt',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({enabled:en,password:pw})}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    if(g('backupPass')) g('backupPass').value='';
    toast(en?'🔒 Автошифрування увімкнено':'🔓 Автошифрування вимкнено');
    loadSettings();
  }catch(e){ toast('⚠ '+e, false); }
}
async function backupVerify(){
  try{
    const d=await fetch('/api/backup/verify',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}).then(r=>r.json());
    if(d.ok) toast('✅ Бекап цілий · файлів: '+(d.files||0));
    else toast('⚠ '+(d.error||'перевірка не пройдена'), false);
    loadSettings();
  }catch(e){ toast('⚠ '+e, false); }
}
async function backupRestoreTest(){
  try{
    toast('🧪 Тестую відновлення...', true);
    const d=await fetch('/api/backup/restore-test',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}).then(r=>r.json());
    if(d.ok) toast('✅ Restore-test OK · P&L: '+((d.counts||{}).pl||0));
    else toast('⚠ '+(d.error||'restore test failed'), false);
    loadSettings();
  }catch(e){ toast('⚠ '+e, false); }
}
async function backupNow(){
  try{
    toast('⏳ Бекап...', true);
    const d=await fetch('/api/backup/run',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    toast('✅ Бекап: '+(d.files||[]).length+' файлів');
    loadSettings();
  }catch(e){ toast('⚠ '+e, false); }
}
async function savePayoutRules(){
  const days={};
  ['g2g','gameflip','pa','zeusx','funpay','eldorado','other'].forEach(k=>{
    const v=parseInt(g('pd_'+k)?.value||'3'); days[k]=Number.isFinite(v)?Math.max(0,Math.min(90,v)):3;
  });
  try{
    const d=await fetch('/api/settings/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({payout_days:days})}).then(r=>r.json());
    toast(d.ok?'✅ Правила payout збережено':'⚠ '+(d.error||''), !!d.ok);
  }catch(e){ toast('⚠ '+e, false); }
}
async function importCashflowCsv(input){
  const f=input.files&&input.files[0]; if(!f) return;
  const rows=parseCsvText(await f.text());
  if(rows.length<2){ toast('⚠ '+t('imp.emptyCsv'), false); return; }
  const hdr=rows[0].map(x=>String(x).trim().toLowerCase());
  const col=function(){ for(let i=0;i<arguments.length;i++){ const ix=hdr.findIndex(h=>h===arguments[i]||h.includes(arguments[i])); if(ix>=0) return ix; } return -1; };
  const ci={date:col('date','created'),platform:col('platform','marketplace','source'),amount:col('amount','total','payout','net'),status:col('status','state'),note:col('note','comment','description'),available:col('available','payout date','release'),order:col('order','transaction','sale','id')};
  if(ci.amount<0){ toast('⚠ Немає колонки amount', false); return; }
  let added=0, matched=0;
  let open=[];
  try{ const cur=await fetch('/api/cashflow').then(r=>r.json()); open=(cur.items||[]).filter(x=>x.status==='hold'||x.status==='available'); }catch(e){}
  for(const r of rows.slice(1)){
    const amount=_num(r[ci.amount]); if(!(amount>0)) continue;
    let plat=ci.platform>=0?String(r[ci.platform]||'').toLowerCase().trim():'other';
    if(plat.includes('g2g'))plat='g2g'; else if(plat.includes('gameflip'))plat='gameflip'; else if(plat.includes('player')||plat==='pa')plat='pa'; else if(plat.includes('zeus'))plat='zeusx'; else if(plat.includes('fun'))plat='funpay'; else if(plat.includes('eldorado'))plat='eldorado';
    const st=ci.status>=0?String(r[ci.status]||'').toLowerCase():'withdrawn';
    const order=ci.order>=0?String(r[ci.order]||'').trim():'';
    // 1) звіряємо з відкритим Hold/Available: order, потім платформа + сума
    let hit=null;
    if(order) hit=open.find(x=>String(x.order||'')===order);
    if(!hit) hit=open.find(x=>String(x.platform||'')===plat && Math.abs(Number(x.amount||0)-amount)<0.02);
    if(hit){
      try{ await fetch('/api/cashflow/status',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({id:hit.id,status:['hold','available','withdrawn'].includes(st)?st:'withdrawn'})}); matched++; }catch(e){}
      open=open.filter(x=>x.id!==hit.id);
      continue;
    }
    const body={platform:plat,amount,status:['hold','available','withdrawn'].includes(st)?st:'withdrawn',
      date:ci.date>=0?_date(r[ci.date]):new Date().toISOString().slice(0,10),
      availableDate:(ci.available>=0&&String(r[ci.available]||'').trim())?_date(r[ci.available]):'',
      note:ci.note>=0?String(r[ci.note]||'').slice(0,200):'',order};
    try{ const d=await fetch('/api/cashflow/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(r=>r.json()); if(d.ok) added++; }catch(e){}
  }
  await loadCashflow();
  toast('✅ Звірено: '+matched+' · нових: '+added);
  if(g('cfImport')) g('cfImport').value='';
}
async function cashflowSet(id,status){
  try{ const d=await fetch('/api/cashflow/status',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,status})}).then(r=>r.json()); if(d.ok) await loadCashflow(); }catch(e){}
}
async function cashflowDel(id){
  if(!confirm(t('cf.deleteConfirm'))) return;
  try{ const d=await fetch('/api/cashflow/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id})}).then(r=>r.json()); if(d.ok) await loadCashflow(); }catch(e){}
}
async function loadSupplierROI(){
  const el=g('supRoi'); if(!el) return;
  try{
    const d=await fetch('/api/supplier_roi').then(r=>r.json());
    const rows=d.suppliers||[];
    if(!rows.length){ el.innerHTML='<div class="none">'+esc(t('roi.empty'))+'</div>'; return; }
    const H=['roi.supplier','roi.items','roi.sold','roi.stock','roi.cost','roi.revenue','roi.profit','roi.roi','roi.st','roi.days'].map(k=>t(k));
    el.innerHTML='<div style="overflow-x:auto"><table class="sup-table"><thead><tr>'+
      H.map(x=>'<th>'+x+'</th>').join('')+'</tr></thead><tbody>'+
      rows.map(x=>'<tr><td><b>'+esc(x.source||'—')+'</b></td><td>'+x.items+'</td><td>'+x.sold+'</td><td>'+x.stock+
        '</td><td>$'+Number(x.cost_total||0).toFixed(2)+'</td><td>$'+Number(x.revenue||0).toFixed(2)+
        '</td><td style="color:'+(x.profit>=0?'var(--gr)':'var(--rd)')+';font-weight:700">$'+Number(x.profit||0).toFixed(2)+
        '</td><td style="color:'+(x.roi>=0?'var(--gr)':'var(--rd)')+'">'+Number(x.roi||0).toFixed(1)+'%</td><td>'+
        Number(x.sell_through||0).toFixed(1)+'%</td><td>'+(x.avg_days==null?'—':x.avg_days)+'</td></tr>').join('')+
      '</tbody></table></div>';
  }catch(e){ el.innerHTML='<div class="none">⚠ '+esc(String(e))+'</div>'; }
}

function refreshCombinedStats(){
  if(!g('plProfit')) return;
  const pl = purchases || [], ed = edSales || [];
  const plRev = pl.reduce((s,p)=>s+Number(p.sell||0),0);
  const plBuy = pl.reduce((s,p)=>s+Number(p.buy||0),0);
  const plExp = pl.reduce((s,p)=>s+Number(p.expenses||0),0);
  const plProfit = pl.reduce((s,p)=>s+Number(p.afterFee||0)-Number(p.expenses||0),0);
  const plFees = pl.reduce((s,p)=>s+Number(p.sell||0)*feePctOf(p),0);
  const edRev = ed.reduce((s,x)=>s+Number(x.price||0),0);
  const edBuy = ed.reduce((s,x)=>s+Number(x.buy||0),0);
  const edFee = ed.reduce((s,x)=>s+Number(x.fee||0),0);
  const edProfit = ed.reduce((s,x)=>s+Number(x.profit||0),0);
  const rev = plRev + edRev, cost = plBuy + edBuy;
  const profit = plProfit + edProfit;
  const margin = cost > 0 ? (profit / cost * 100) : 0;
  g('plProfit').textContent=(profit>=0?'+':'-')+locMoney(Math.abs(profit));
  g('plProfit').style.color=profit>0?'var(--gr)':profit<0?'var(--rd)':'var(--mu)';
  if(g('plRevenue')) g('plRevenue').textContent=locMoney(rev);
  if(g('plCost')) g('plCost').textContent=locMoney(cost);
  if(g('plMargin')){ g('plMargin').textContent=fmtPct(margin); g('plMargin').style.color=margin>0?'var(--gr)':'var(--mu)'; }
  if(g('plCount')) g('plCount').textContent=pl.length + ed.length;
  if(g('plFees')) g('plFees').textContent=locMoney(plFees + edFee);
  if(g('plExpenses')) g('plExpenses').textContent=locMoney(plExp);
}

function renderStats(){
  fillMonthOptions();
  const platform = g('statsPlatform')?.value || '';
  const period   = g('statsPeriod')?.value || '';
  const now      = new Date();
  const moStart  = localDate(now).slice(0,7);

  // Фільтр
  let recs = purchases.filter(p=>{
    if(platform && p.src !== platform) return false;
    if(period === 'month' && !(p.date||'').startsWith(moStart)) return false;
    if(period.startsWith('m:') && !(p.date||'').startsWith(period.slice(2))) return false;
    return true;
  });

  // Групуємо по грі (з назви лоту або srcName)
  const gameMap = {};
  recs.forEach(p=>{
    let game = (p.game || p.base_name || '').trim();
    if(!game){
      const t = (p.title||'').trim();
      if(t){
        game = t.length > 50 ? t.substring(0,50) : t;
      } else {
        // Без назви — одна група (раніше кожен запис ставав окремим рядком)
        game = '__noname__';
      }
    }
    if(!gameMap[game]) gameMap[game] = {count:0, revenue:0, profit:0, buy:0,
      displayName: game === '__noname__' ? 'Без назви' : game};
    gameMap[game].count++;
    gameMap[game].revenue += p.sell||0;
    gameMap[game].profit  += (p.afterFee||0) - Number(p.expenses||0);
    gameMap[game].buy     += p.buy||0;
  });

  const games = Object.entries(gameMap)
    .map(([key,s])=>({name: s.displayName||key, ...s, margin: s.buy>0?(s.profit/s.buy*100):0}))
    .sort((a,b)=>b.profit-a.profit);

  const top = games.slice(0,15);

  // Картки загальної статистики
  const totRev    = recs.reduce((s,p)=>s+(p.sell||0),0);
  const totProfit = recs.reduce((s,p)=>s+(p.afterFee||0)-Number(p.expenses||0),0);
  const totBuy    = recs.reduce((s,p)=>s+(p.buy||0),0);
  const avgMargin = totBuy>0?(totProfit/totBuy*100).toFixed(1):0;

  // Зведений підсумок P&L + ELDORADO (весь час)
  const plAllProfit = purchases.reduce((s,p)=>s+(p.afterFee||0)-Number(p.expenses||0),0);
  const edAllProfit = edSales.reduce((s,x)=>s+(x.profit||0),0);
  const plAllRev    = purchases.reduce((s,p)=>s+(p.sell||0),0);
  const edAllRev    = edSales.reduce((s,x)=>s+(x.price||0),0);
  const combinedAll = plAllProfit + edAllProfit;
  const combinedRev = plAllRev + edAllRev;

  const cards = g('statsCards');
  if(cards) cards.innerHTML = [
    {l:t('an.deals'),       v:recs.length,                    c:'var(--a1)'},
    {l:t('an.revenue'),     v:locMoney(totRev),           c:'var(--tx)'},
    {l:t('an.profit'),      v:(totProfit>=0?'+':'-')+locMoney(Math.abs(totProfit)), c:'var(--gr)'},
    {l:t('an.margin'),      v:fmtPct(avgMargin),              c:'var(--yw)'},
    {l:t('an.games'),       v:games.length,                    c:'var(--a3)'},
    {l:t('an.best'),        v:(top[0]?.name||'—').substring(0,18), c:'var(--gr)'},
    {l:t('an.profitED'),    v:(edAllProfit>=0?'+':'-')+locMoney(Math.abs(edAllProfit)), c:'var(--a3)'},
    {l:t('an.total'),       v:(combinedAll>=0?'+':'-')+locMoney(Math.abs(combinedAll)), c:combinedAll>=0?'var(--gr)':'var(--rd)'},
  ].concat(_rate ? [
    {l:t('an.totalIn')+' '+curSym(), v:curSym()+(combinedAll*_rate).toFixed(2), c:'var(--a1)'},
  ] : []).map(c=>`<div style="background:var(--card);border:1px solid var(--brd);border-radius:8px;padding:12px 14px">
    <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px">${c.l}</div>
    <div style="font-size:18px;font-weight:700;color:${c.c};font-family:var(--font)">${c.v}</div>
  </div>`).join('');

  // ── Порівняння місяць до місяця ──
  const cmpEl = g('statsCompare');
  if(cmpEl){
    const curKey   = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0');
    const prevDate = new Date(now.getFullYear(), now.getMonth()-1, 1);
    const prevKey  = prevDate.getFullYear()+'-'+String(prevDate.getMonth()+1).padStart(2,'0');
    const ym   = p => (p.date||'').slice(0,7);
    const plSum = (key, field) => purchases.filter(p=>ym(p)===key).reduce((s,p)=>s+(p[field]||0),0);
    const plNet = key => purchases.filter(p=>ym(p)===key).reduce((s,p)=>s+(p.afterFee||0)-Number(p.expenses||0),0);
    const edSum = (key, field) => edSales.filter(s=>ym(s)===key).reduce((s,x)=>s+(x[field]||0),0);
    const rows = [
      {l:t('an.profitPL'),   cur:plNet(curKey), prev:plNet(prevKey)},
      {l:t('an.revenuePL'),  cur:plSum(curKey,'sell'),     prev:plSum(prevKey,'sell')},
      {l:t('an.profitED'),   cur:edSum(curKey,'profit'), prev:edSum(prevKey,'profit')},
      {l:t('an.totalProfit'), cur:plNet(curKey)+edSum(curKey,'profit'),
                            prev:plNet(prevKey)+edSum(prevKey,'profit')},
    ];
    const pct = (a,b)=> b>0 ? ((a-b)/b*100) : (a>0?100:0);
    const fmtPct = (a,b)=> b>0 ? ((a-b)>=0?'+':'')+pct(a,b).toFixed(1)+'%' : (a>0?t('an.new'):'—');
    cmpEl.innerHTML = '<div style="font-size:11px;color:var(--mu);letter-spacing:1px;margin-bottom:8px">'+t('an.thisVsLast')+' ('+prevKey+' → '+curKey+')</div>'+
      '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px">'+
      rows.map(r=>{
        const good = (r.cur-r.prev) >= 0;
        return `<div style="background:var(--card);border:1px solid var(--brd);border-radius:8px;padding:12px 14px">
          <div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:4px">${r.l}</div>
          <div style="font-size:17px;font-weight:700;font-family:var(--font);color:${good?'var(--gr)':'var(--rd)'}">${r.cur>=0?'+':''}$${r.cur.toFixed(2)}</div>
          <div style="font-size:11px;color:var(--mu);margin-top:3px">${t('an.was')} $${r.prev.toFixed(2)} · <b style="color:${good?'var(--gr)':'var(--rd)'}">${fmtPct(r.cur,r.prev)}</b></div>
        </div>`;
      }).join('')+'</div>';
  }

  // ── Прибуток по платформах ──
  const platEl = g('platformStats');
  if(platEl){
    const pm = {};
    const addP = (name, rev, fee, exp, net) => {
      const a = pm[name] || (pm[name] = {n:0, rev:0, fee:0, exp:0, net:0});
      a.n++; a.rev += rev||0; a.fee += fee||0; a.exp += exp||0; a.net += net||0;
    };
    recs.forEach(p=>{
      const fee=Number(p.sell||0)*feePctOf(p);
      addP(p.srcName || p.src || '—', Number(p.sell||0), fee, Number(p.expenses||0),
           (Number(p.afterFee)||0) - Number(p.expenses||0));
    });
    if(!platform || platform==='eldorado'){
      edSales.filter(s=>{
        const d=(s.date||'').slice(0,7);
        if(period==='month' && d!==moStart) return false;
        if(period.startsWith('m:') && d!==period.slice(2)) return false;
        return true;
      }).forEach(s=>addP('Eldorado', Number(s.price||0), Number(s.fee||0), 0, Number(s.profit||0)));
    }
    const rows = Object.entries(pm).map(([name,a])=>({name,...a,
      margin: a.rev>0 ? a.net/a.rev*100 : 0
    })).sort((a,b)=>b.net-a.net);
    if(!rows.length){
      platEl.innerHTML = '<div class="none">'+t('an.noData')+'</div>';
    } else {
      platEl.innerHTML = '<div style="font-size:11px;color:var(--mu);letter-spacing:1px;margin-bottom:8px">'+t('an.platforms')+'</div>'+
        '<table class="sup-table"><thead><tr>'+
        '<th>'+t('an.platform')+'</th><th style="text-align:right">'+t('an.dealsCol')+'</th>'+
        '<th style="text-align:right">'+t('an.revenueCol')+'</th><th style="text-align:right">'+t('an.feeCol')+'</th>'+
        '<th style="text-align:right">'+t('an.expenseCol')+'</th><th style="text-align:right">'+t('an.netCol')+'</th>'+
        '<th style="text-align:right">'+t('an.netPct')+'</th></tr></thead><tbody>'+
        rows.map(r=>'<tr><td style="font-weight:600">'+esc(r.name)+'</td>'+
          '<td style="text-align:right;color:var(--mu)">'+r.n+'</td>'+
          '<td style="text-align:right;font-family:var(--font);font-size:11px">'+locMoney(r.rev)+'</td>'+
          '<td style="text-align:right;font-family:var(--font);font-size:11px;color:var(--rd)">-'+locMoney(r.fee)+'</td>'+
          '<td style="text-align:right;font-family:var(--font);font-size:11px;color:var(--yw)">-'+locMoney(r.exp)+'</td>'+
          '<td style="text-align:right;font-family:var(--font);font-size:12px;font-weight:700;color:'+(r.net>=0?'var(--gr)':'var(--rd)')+'">'+(r.net>=0?'+':'-')+locMoney(Math.abs(r.net))+'</td>'+
          '<td style="text-align:right;font-size:11px;color:var(--mu)">'+fmtPct(r.margin)+'</td></tr>').join('')+
        '</tbody></table>';
    }
  }

  // Графік
  if(_statsChart){_statsChart.destroy();_statsChart=null;}
  const ctx = g('statsChart');
  if(ctx && top.length){
    const _cm = _rate ? Number(_rate) : 1;
    const _cs = _rate ? curSym() : '$';
    _statsChart = new Chart(ctx,{
      type:'bar',
      data:{
        labels: top.map(g=>g.name.length>15?g.name.substring(0,15)+'…':g.name),
        datasets:[
          {label:t('an.profitChart'), data:top.map(g=>parseFloat((g.profit*_cm).toFixed(2))),
           backgroundColor:'rgba(16,185,129,.5)',borderColor:'rgba(16,185,129,.9)',borderWidth:1,borderRadius:4},
          {label:t('an.revenueChart'),  data:top.map(g=>parseFloat((g.revenue*_cm).toFixed(2))),
           backgroundColor:'rgba(99,102,241,.35)',borderColor:'rgba(99,102,241,.8)',borderWidth:1,borderRadius:4},
        ]
      },
      options:{
        responsive:true,maintainAspectRatio:false,
        plugins:{legend:{labels:{color:'#94a3b8',font:{size:11}}}},
        scales:{
          x:{ticks:{color:'#64748b',font:{size:9},maxRotation:35},grid:{color:'rgba(255,255,255,.04)'}},
          y:{ticks:{color:'#64748b',callback:v=>_cs+Number(v).toLocaleString(dateLocale())},grid:{color:'rgba(255,255,255,.05)'}},
        }
      }
    });
  }

  // Таблиця
  const tbl = g('statsTable');
  if(tbl){
    if(!top.length){tbl.innerHTML='<div class="none">'+t('an.noData')+'</div>';return;}
    tbl.innerHTML='<table class="sup-table"><thead><tr>'+
      '<th>#</th><th>'+t('an.game')+'</th><th style="text-align:right">'+t('an.dealsCol')+'</th>'+
      '<th style="text-align:right">'+t('an.revenueCol')+'</th><th style="text-align:right">'+t('an.profitCol')+'</th><th style="text-align:right">'+t('an.marginCol')+'</th>'+
      '</tr></thead><tbody>'+
      games.map((g2,i)=>{
        const pcls=g2.profit>0?'profit-pos':g2.profit<0?'profit-neg':'profit-neu';
        const medal=i===0?'🥇':i===1?'🥈':i===2?'🥉':'';
        return `<tr>
          <td style="color:var(--mu);font-size:11px">${medal||('#'+(i+1))}</td>
          <td style="font-weight:600;max-width:200px">${esc(g2.name)}</td>
          <td style="text-align:right;color:var(--mu)">${g2.count}</td>
          <td style="text-align:right;font-family:var(--font);font-size:11px">$${g2.revenue.toFixed(2)}</td>
          <td style="text-align:right;font-family:var(--font);font-size:12px;font-weight:700" class="${pcls}">${g2.profit>=0?'+':''}$${g2.profit.toFixed(2)}</td>
          <td style="text-align:right;font-size:11px;color:${g2.margin>50?'var(--gr)':g2.margin>20?'var(--yw)':'var(--mu)'}">${g2.margin.toFixed(0)}%</td>
        </tr>`;
      }).join('')+'</tbody></table>';
  }
}

let _editId = null;
let _invSellId = null;

function startEdit(id){ _editId=id; renderPurchases(); }
function cancelEdit(){ _editId=null; renderPurchases(); }

async function saveEdit(id){
  const p = purchases.find(x=>x.id===id);
  if(!p) return;
  const buy  = parseFloat(g('ei_buy').value)||0;
  const sell = parseFloat(g('ei_sell').value)||0;
  const plat = g('ei_plat').value;
  const feeRaw = parseFloat(g('ei_feePct')?.value);
  const fee  = Number.isFinite(feeRaw) ? Math.max(0, Math.min(100, feeRaw))/100 : defaultFeePct(plat);
  const expenses = Math.max(0, parseFloat(g('ei_expenses')?.value)||0);
  p.title    = g('ei_title').value.trim();
  p.date     = g('ei_date').value;
  p.buy      = buy;
  p.sell     = sell;
  p.src      = plat;
  p.srcName  = plat==='zeusx'?'ZeusX':plat==='funpay'?'FunPay':plat==='eldorado'?'Eldorado':t('f.other2');
  p.feePct   = Math.round(fee*1000000)/1000000;
  p.expenses = Math.round(expenses*100)/100;
  p.afterFee = Math.round((sell*(1-fee)-buy)*10000)/10000;
  p.currency = 'USD'; p.fxRate = 1;
  delete p.origBuy; delete p.origSell; delete p.origExpenses;
  _editId    = null;
  await savePL(); renderPurchases();
  toast(t('deal.updated'));
}

// Графік виторгу по днях
let _chartInst = null;
function renderRevenueChart(){
  const el = g('revenueChart');
  if(!el) return;
  // Беремо останні 30 днів
  const days = 30;
  const now = new Date();
  const labels=[], profits=[], revenues=[];
  for(let i=days-1;i>=0;i--){
    const d=new Date(now); d.setDate(d.getDate()-i);
    const ds=localDate(d);
    labels.push(ds.slice(5)); // MM-DD
    const dayRecs=purchases.filter(p=>p.date===ds);
    revenues.push(dayRecs.reduce((s,p)=>s+(p.sell||0),0));
    profits.push(dayRecs.reduce((s,p)=>s+(p.afterFee||0),0));
  }
  if(_chartInst){ _chartInst.destroy(); _chartInst=null; }
  const _cm = _rate ? Number(_rate) : 1;
  const _cs = _rate ? curSym() : '$';
  const ctx=el.getContext('2d');
  _chartInst=new Chart(ctx,{
    type:'bar',
    data:{
      labels,
      datasets:[
        {label:t('an.revenueChart'),data:revenues.map(v=>parseFloat((v*_cm).toFixed(2))),backgroundColor:'rgba(99,102,241,.35)',borderColor:'rgba(99,102,241,.8)',borderWidth:1,borderRadius:3},
        {label:t('an.profitChart'),data:profits.map(v=>parseFloat((v*_cm).toFixed(2))),backgroundColor:'rgba(16,185,129,.35)',borderColor:'rgba(16,185,129,.8)',borderWidth:1,borderRadius:3},
      ]
    },
    options:{
      responsive:true,maintainAspectRatio:false,
      plugins:{legend:{labels:{color:'#94a3b8',font:{size:11}}},
        tooltip:{callbacks:{label:ctx=>_cs+ctx.raw.toFixed(2)}}},
      scales:{
        x:{ticks:{color:'#64748b',font:{size:9},maxRotation:45},grid:{color:'rgba(255,255,255,.04)'}},
        y:{ticks:{color:'#64748b',font:{size:10},callback:v=>_cs+Number(v).toLocaleString(dateLocale())},grid:{color:'rgba(255,255,255,.06)'}}
      }
    }
  });
}

function exportCSV(){
  // CSV тільки P&L (поточний фільтр)
  const rows=[[t('th.date'),t('inv.name'),t('f.platform'),t('th.buy')+' $',t('th.sell')+' $',t('th.fee')+' $',t('k.expenses')+' $',t('an.profit')+' $']];
  plFilt.forEach(p=>{
    const _fp=feePctOf(p);
    const fee=(p.sell||0)*_fp;
    const exp=Number(p.expenses||0);
    const profit=(p.afterFee!=null?p.afterFee:((p.sell||0)*(1-_fp)-(p.buy||0)))-exp;
    rows.push([p.date||'',p.title||'',p.srcName||p.src,(p.buy||0).toFixed(2),(p.sell||0).toFixed(2),fee.toFixed(2),exp.toFixed(2),profit.toFixed(2)]);
  });
  const csv=rows.map(r=>r.map(c=>'"'+String(c).replace(/"/g,'""')+'"').join(',')).join('\n');
  const a=document.createElement('a');
  a.href='data:text/csv;charset=utf-8,\uFEFF'+encodeURIComponent(csv);
  a.download='pl_tracker_'+todayLocal()+'.csv';
  a.click();
  toast(t('deal.csvDone'));
}

async function exportFullExcel(){
  toast(t('loading'));
  if(typeof XLSX==='undefined'){
    await new Promise((res,rej)=>{
      const s=document.createElement('script');
      s.src='https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
      s.onload=res; s.onerror=rej;
      document.head.appendChild(s);
    });
  }
  const X = LANG==='ru' ? {
    date:'Дата',name:'Название',platform:'Платформа',buy:'Купил $',sell:'Продал $',fee:'Комиссия $',
    fee10:'Комиссия 10% $',expenses:'Расходы $',profit:'Прибыль $',total:'ВСЕГО:',category:'Категория',deals:'Сделок',
    rev:'Выручка $',margin:'Маржа %',noCat:'Без категории',metric:'Показатель',value:'Значение',
    totalDeals:'Всего сделок',totalRev:'Общая выручка $',totalCost:'Общие затраты $',
    totalProfit:'Общая прибыль $',totalFees:'Общие комиссии $',rate:'Курс USD→UAH',
    edProfit:'Прибыль ELDORADO $',allProfit:'ВСЕГО прибыль (P&L + ELD) $',allProfitUah:'ВСЕГО прибыль ₴',
    curMonth:'Текущий месяц',monthDeals:'Сделок за месяц',monthProfit:'Прибыль за месяц $',
    exportDate:'Дата экспорта',sheetPL:'P&L Все записи',sheetCats:'ELDORADO категории',sheetStats:'Статистика'
  } : LANG==='en' ? {
    date:'Date',name:'Name',platform:'Platform',buy:'Bought $',sell:'Sold $',fee:'Fee $',
    fee10:'Fee 10% $',expenses:'Expenses $',profit:'Profit $',total:'TOTAL:',category:'Category',deals:'Deals',
    rev:'Revenue $',margin:'Margin %',noCat:'No category',metric:'Metric',value:'Value',
    totalDeals:'Total deals',totalRev:'Total revenue $',totalCost:'Total cost $',
    totalProfit:'Total profit $',totalFees:'Total fees $',rate:'USD→UAH rate',
    edProfit:'ELDORADO profit $',allProfit:'TOTAL profit (P&L + ELD) $',allProfitUah:'TOTAL profit ₴',
    curMonth:'Current month',monthDeals:'Deals this month',monthProfit:'Profit this month $',
    exportDate:'Export date',sheetPL:'P&L All records',sheetCats:'ELDORADO categories',sheetStats:'Statistics'
  } : {
    date:'Дата',name:'Назва',platform:'Платформа',buy:'Купив $',sell:'Продав $',fee:'Комісія $',
    fee10:'Комісія 10% $',expenses:'Витрати $',profit:'Прибуток $',total:'РАЗОМ:',category:'Категорія',deals:'Угод',
    rev:'Виторг $',margin:'Маржа %',noCat:'Без категорії',metric:'Показник',value:'Значення',
    totalDeals:'Всього угод',totalRev:'Загальна виручка $',totalCost:'Загальні витрати $',
    totalProfit:'Загальний прибуток $',totalFees:'Загальні комісії $',rate:'Курс USD→UAH',
    edProfit:'Прибуток ELDORADO $',allProfit:'РАЗОМ прибуток (P&L + ELD) $',allProfitUah:'РАЗОМ прибуток ₴',
    curMonth:'Поточний місяць',monthDeals:'Угод цього місяця',monthProfit:'Прибуток цього місяця $',
    exportDate:'Дата експорту',sheetPL:'P&L Всі записи',sheetCats:'ELDORADO категорії',sheetStats:'Статистика'
  };
  const wb=XLSX.utils.book_new();

  const plRows=[[X.date,X.name,X.platform,X.buy,X.sell,X.fee,X.expenses,X.profit]];
  purchases.forEach(p=>{
    const _fp=feePctOf(p);
    const fee=(p.sell||0)*_fp;
    const exp=Number(p.expenses||0);
    const profit=(p.afterFee!=null?p.afterFee:((p.sell||0)*(1-_fp)-(p.buy||0)))-exp;
    plRows.push([p.date||'',p.title||'',p.srcName||p.src,
      parseFloat((p.buy||0).toFixed(2)),parseFloat((p.sell||0).toFixed(2)),
      parseFloat(fee.toFixed(2)),parseFloat(exp.toFixed(2)),parseFloat(profit.toFixed(2))]);
  });
  const totSell=purchases.reduce((s,p)=>s+(p.sell||0),0);
  const totBuy=purchases.reduce((s,p)=>s+(p.buy||0),0);
  const totProfit=purchases.reduce((s,p)=>s+(p.afterFee||0)-Number(p.expenses||0),0);
  const totFee=purchases.reduce((s,p)=>s+(p.sell||0)*feePctOf(p),0);
  const totExp=purchases.reduce((s,p)=>s+Number(p.expenses||0),0);
  plRows.push([]);
  plRows.push(['','',X.total,parseFloat(totBuy.toFixed(2)),parseFloat(totSell.toFixed(2)),parseFloat(totFee.toFixed(2)),parseFloat(totExp.toFixed(2)),parseFloat(totProfit.toFixed(2))]);
  const wsP=XLSX.utils.aoa_to_sheet(plRows);
  wsP['!cols']=[{wch:12},{wch:40},{wch:12},{wch:10},{wch:10},{wch:10},{wch:10},{wch:12}];
  XLSX.utils.book_append_sheet(wb,wsP,'📋 '+X.sheetPL);

  const edRows=[[X.date,X.name,X.category,X.sell,X.buy,X.fee10,X.profit,'Order ID']];
  edSales.forEach(s=>{
    edRows.push([s.date||'', s.title||'', s.category||'', parseFloat((s.price||0).toFixed(2)),
      parseFloat((s.buy||0).toFixed(2)), parseFloat((s.fee||0).toFixed(2)),
      parseFloat((s.profit||0).toFixed(2)), s.orderId||'']);
  });
  const edSell=edSales.reduce((a,s)=>a+(s.price||0),0);
  const edBuy =edSales.reduce((a,s)=>a+(s.buy||0),0);
  const edFee =edSales.reduce((a,s)=>a+(s.fee||0),0);
  const edProf=edSales.reduce((a,s)=>a+(s.profit||0),0);
  edRows.push([]);
  edRows.push(['','',X.total,parseFloat(edSell.toFixed(2)),parseFloat(edBuy.toFixed(2)),parseFloat(edFee.toFixed(2)),parseFloat(edProf.toFixed(2)),'']);
  const wsEd=XLSX.utils.aoa_to_sheet(edRows);
  wsEd['!cols']=[{wch:12},{wch:40},{wch:16},{wch:10},{wch:10},{wch:14},{wch:10},{wch:38}];
  XLSX.utils.book_append_sheet(wb,wsEd,'🟡 ELDORADO');

  const catMap = {};
  edSales.forEach(s=>{
    const k = (s.category||'').trim() || X.noCat;
    if(!catMap[k]) catMap[k] = {count:0, rev:0, buy:0, profit:0};
    catMap[k].count++;
    catMap[k].rev    += s.price||0;
    catMap[k].buy    += s.buy||0;
    catMap[k].profit += s.profit||0;
  });
  const catRows=[[X.category,X.deals,X.rev,X.buy,X.profit,X.margin]];
  Object.entries(catMap).sort((a,b)=>b[1].profit-a[1].profit).forEach(([k,v])=>{
    catRows.push([k, v.count, parseFloat(v.rev.toFixed(2)), parseFloat(v.buy.toFixed(2)),
      parseFloat(v.profit.toFixed(2)), v.buy>0?parseFloat((v.profit/v.buy*100).toFixed(1)):'—']);
  });
  const wsCat=XLSX.utils.aoa_to_sheet(catRows);
  wsCat['!cols']=[{wch:24},{wch:8},{wch:12},{wch:10},{wch:12},{wch:10}];
  XLSX.utils.book_append_sheet(wb,wsCat,'🏷 '+X.sheetCats);

  const now=new Date();
  const thisMonth=localDate(now).slice(0,7);
  const monthRecs=purchases.filter(p=>(p.date||'').startsWith(thisMonth));
  const monthProfit=monthRecs.reduce((s,p)=>s+(p.afterFee||0),0);
  const statsRows=[
    [X.metric,X.value],
    [X.totalDeals,purchases.length],
    [X.totalRev,parseFloat(totSell.toFixed(2))],
    [X.totalCost,parseFloat(totBuy.toFixed(2))],
    [X.totalProfit,parseFloat(totProfit.toFixed(2))],
    [X.totalFees,parseFloat(totFee.toFixed(2))],
    [X.margin,totBuy>0?parseFloat((totProfit/totBuy*100).toFixed(1)):0],
    [''],
    [X.rate,_rate||'—'],
    [X.edProfit,parseFloat((edProf||0).toFixed(2))],
    [X.allProfit,parseFloat(((totProfit||0)+(edProf||0)).toFixed(2))],
    [X.allProfitUah,_rate?parseFloat((((totProfit||0)+(edProf||0))*_rate).toFixed(2)):'—'],
    [''],
    [X.curMonth+' ('+thisMonth+')',''],
    [X.monthDeals,monthRecs.length],
    [X.monthProfit,parseFloat(monthProfit.toFixed(2))],
    [''],
    [X.exportDate,now.toLocaleString(dateLocale())],
  ];
  const wsSt=XLSX.utils.aoa_to_sheet(statsRows);
  wsSt['!cols']=[{wch:30},{wch:18}];
  XLSX.utils.book_append_sheet(wb,wsSt,'📊 '+X.sheetStats);

  XLSX.writeFile(wb,'game_tracker_'+localDate(now)+'.xlsx');
  toast(t('deal.excelDone')+': P&L · ELDORADO · '+X.sheetCats+' · '+X.sheetStats);
}


// ═══════════════════════════════════════════════
// 🛒 ЗАКУПІВЛЯ (постачальники)
// ═══════════════════════════════════════════════

// ===== ELDORADO (зберігається на сервері + кеш у localStorage) =====
let edSales = [];
let edLoaded = false;
let _edSaving = 0;
let _edTouched = 0;
let edFilt = [];
let edPg = 1;
let _edDirty = false;

function toggleEdRange(){
  const v = g('edDateFilter')?.value || '';
  const el = g('edCustomRange');
  if(el) el.style.display = v==='custom' ? 'flex' : 'none';
}

function suggestEdBuy(){
  const box = g('edBuy');
  if(!box || box.value) return;          // не перетираємо вже введене
  const t = (g('edTitle')?.value||'').trim().toLowerCase();
  if(t.length < 4) return;
  const hit = purchases.find(p=>{
    const pt = (p.title||'').trim().toLowerCase();
    if(!pt || pt.length < 4) return false;
    return pt === t || pt.includes(t) || t.includes(pt);
  });
  if(hit && (hit.buy||0) > 0){
    box.value = (hit.buy||0).toFixed(2);
    toast('💰 Підставлено закупівлю $'+(hit.buy||0).toFixed(2)+' з P&L');
  }
}

async function saveED(){
  _edSaving++; _edTouched = Date.now();
  try{
    const r = await fetch('/api/eldorado/save',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({sales:edSales, force: edSales.length === 0})});
    const res = await r.json().catch(()=>({}));
    if(!r.ok || res.ok === false) throw new Error(res.error || ('HTTP '+r.status));
    _edDirty = false;
  }catch(e){
    // офлайн — дані лишаються в localStorage і повторюємо запис
    _edDirty = true;
    toast('⚠ ELDORADO не збережено на сервері: '+e, false);
    setTimeout(()=>{ if(_edDirty) saveED(); }, 10000);
  } finally {
    try{ localStorage.setItem('eldorado_sales', JSON.stringify(edSales)); }catch(e2){}
    _edSaving--;
  }
}


function importEdCsv(input){
  const file = input.files[0];
  if(!file) return;
  const reader = new FileReader();
  reader.onload = async e => {
    const text = e.target.result;
    const lines = text.trim().split('\n');
    if(lines.length < 2){ alert('Порожній файл'); return; }
    // Визначаємо роздільник (tab або кома)
    const sep = lines[0].includes('\t') ? '\t' : ',';
    const headers = lines[0].split(sep).map(h=>h.trim().replace(/"/g,''));
    const idx = {
      id: headers.findIndex(h=>h.toLowerCase().includes('order id')),
      date: headers.findIndex(h=>h.toLowerCase().includes('order date')),
      title: headers.findIndex(h=>h.toLowerCase().includes('title')),
      price: headers.findIndex(h=>h.toLowerCase().includes('total order amount')),
      state: headers.findIndex(h=>h.toLowerCase().includes('order state')),
      cat: headers.findIndex(h=>['category','type','game'].includes(h.toLowerCase().trim())),
    };
    let added = 0, skipped = 0;
    const existingIds = new Set(edSales.map(s=>s.orderId));
    for(let i=1;i<lines.length;i++){
      const cols = lines[i].split(sep).map(c=>c.trim().replace(/"/g,''));
      if(cols.length < 3) continue;
      const state = idx.state>=0 ? cols[idx.state] : '';
      if(state && !['delivered','completed'].includes(state.toLowerCase())){ skipped++; continue; }
      const orderId = idx.id>=0 ? cols[idx.id] : '';
      if(orderId && existingIds.has(orderId)){ skipped++; continue; }
      const dateRaw = idx.date>=0 ? cols[idx.date] : '';
      const date = dateRaw ? dateRaw.slice(0,10) : todayLocal();
      const title = idx.title>=0 ? cols[idx.title] : 'Невідомо';
      const price = parseFloat(idx.price>=0 ? cols[idx.price] : 0) || 0;
      const category = idx.cat>=0 ? (cols[idx.cat]||'').trim() : '';
      const fee = parseFloat((price * ED_FEE).toFixed(2));
      const profit = parseFloat((price - fee).toFixed(2));
      edSales.unshift({ id: Date.now()+i, date, title, price, fee, profit, orderId, category });
      if(orderId) existingIds.add(orderId);
      added++;
    }
    await saveED();
    input.value = '';
    renderEldorado();
    alert('Імпортовано: ' + added + ' записів' + (skipped ? ', пропущено: ' + skipped : ''));
  };
  reader.readAsText(file, 'UTF-8');
}

async function loadEldorado(force=false){
  const d = g('edDate');
  if(d && !d.value) d.value = todayLocal();
  if(edLoaded && !force){ renderEldorado(); return; }
  edLoaded = true;
  let local = [];
  try{ local = JSON.parse(localStorage.getItem('eldorado_sales')||'[]') || []; }catch(e){ local = []; }
  try{
    const r = await fetch('/api/eldorado').then(x=>x.json());
    const srv = Array.isArray(r.sales) ? r.sales : [];
    if(!srv.length){
      // порожньо на сервері — значить порожньо. Кеш браузера не переносимо.
      edSales = [];
      try{ localStorage.removeItem('eldorado_sales'); }catch(e){}
    } else {
      // сервер — джерело істини, localStorage лишаємо як кеш
      edSales = srv;
      try{ localStorage.setItem('eldorado_sales', JSON.stringify(edSales)); }catch(e){}
    }
  }catch(e){
    edSales = local;   // офлайн — беремо кеш браузера
  }
  renderEldorado();
}

async function addEdorado(){
  const date = g('edDate')?.value || todayLocal();
  const title = g('edTitle')?.value.trim() || '';
  const price = parseFloat(g('edPrice')?.value) || 0;
  let buy = parseFloat(g('edBuy')?.value) || 0;
  const orderId = g('edOrderId')?.value.trim() || '';
  const category = g('edCat')?.value.trim() || '';
  if(!title || !price){ alert('Введи назву і ціну продажу'); return; }
  // Захист від дублів
  if(orderId){
    const dup = edSales.find(s=>String(s.orderId||'').toLowerCase()===orderId.toLowerCase());
    if(dup){
      alert('⚠ Запис з Order ID «'+orderId+'» вже є:\n'+dup.title+'\nДата: '+(dup.date||'—'));
      return;
    }
  }
  if(!buy){
    // автопідстановка з P&L, якщо користувач не ввів закупівлю
    const t = title.toLowerCase();
    const hit = purchases.find(p=>{
      const pt=(p.title||'').trim().toLowerCase();
      return pt.length>=4 && (pt===t || pt.includes(t) || t.includes(pt));
    });
    if(hit && (hit.buy||0)>0) buy = hit.buy;
  }
  const same = edSales.find(s=>s.title===title && s.date===date && Math.abs((s.price||0)-price)<0.01);
  if(same && !confirm('Схожий запис уже є:\n'+title+'\n'+date+' · $'+price.toFixed(2)+'\n\nДодати ще раз?')) return;
  const fee = parseFloat((price * ED_FEE).toFixed(2));
  const profit = parseFloat((price - fee - buy).toFixed(2));
  edSales.unshift({ id: Date.now(), date, title, price, buy, fee, profit, orderId, category });
  await saveED();
  g('edTitle').value = '';
  g('edPrice').value = '';
  g('edBuy').value = '';
  g('edOrderId').value = '';
  g('edCat').value = '';
  edPg = 1;
  renderEldorado();
  toast('✅ Продаж додано!');
  // v4.6: без Telegram-сповіщення — ручне внесення
}

function editEdSale(id){
  const s = edSales.find(x => x.id === id);
  if(!s) return;
  document.getElementById('edModal')?.remove();
  const d = document.createElement('div');
  d.id = 'edModal';
  d.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,.7);display:flex;align-items:center;'
    + 'justify-content:center;z-index:9999;padding:16px';
  const fld = (k, label, val, type) =>
    `<label style="display:flex;flex-direction:column;gap:4px;font-size:11px;color:var(--mu)">${label}`
    + `<input id="edM_${k}" type="${type || 'text'}" ${type === 'number' ? 'step="0.01"' : ''}`
    + ` value="${esc(String(val == null ? '' : val))}"></label>`;
  d.innerHTML = `<div style="background:var(--card);border:1px solid var(--brd);border-radius:14px;`
    + `padding:18px;max-width:580px;width:100%;max-height:90vh;overflow:auto">`
    + `<div style="font-weight:800;font-size:15px;margin-bottom:12px">✏ ${t('ed.editTitle')}</div>`
    + `<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">`
    + fld('date', t('th.date'), s.date || '', 'date')
    + fld('oid', 'Order ID', s.orderId || '')
    + `<div style="grid-column:1/-1">` + fld('title', t('inv.name'), s.title || '') + `</div>`
    + fld('cat', t('ed.category'), s.category || '')
    + fld('price', t('th.sell')+' $', s.price || 0, 'number')
    + fld('buy', t('th.buy')+' $', s.buy || 0, 'number')
    + fld('fee', t('th.fee')+' $ (10%)', s.fee || 0, 'number')
    + `</div>`
    + `<div style="font-size:11px;color:var(--mu);margin-top:8px">${t('ed.profitHint')}</div>`
    + `<div style="display:flex;gap:8px;justify-content:flex-end;margin-top:14px">`
    + `<button class="btn" onclick="document.getElementById('edModal').remove()">${t('cancel')}</button>`
    + `<button class="btn gr" onclick="saveEdEdit(${s.id})">💾 ${t('save')}</button>`
    + `</div></div>`;
  document.body.appendChild(d);
}

async function saveEdEdit(id){
  const s = edSales.find(x => x.id === id);
  if(!s) return;
  const v = k => (document.getElementById('edM_' + k) || {}).value || '';
  const num = (x, dflt) => { const n = parseFloat(String(x).replace(',', '.')); return isNaN(n) ? dflt : n; };
  if(v('date')) s.date = v('date');
  s.title = String(v('title')).trim() || s.title;
  s.category = String(v('cat')).trim();
  s.orderId = String(v('oid')).trim();
  s.price = Math.max(0, num(v('price'), 0));
  s.buy = Math.max(0, num(v('buy'), 0));
  const fch = String(v('fee')).trim();
  s.fee = fch === '' ? parseFloat((s.price * 0.1).toFixed(2)) : Math.max(0, num(fch, 0));
  s.profit = parseFloat((s.price - s.fee - s.buy).toFixed(2));
  document.getElementById('edModal')?.remove();
  await saveED();
  renderEldorado();
  toast(t('deal.updated'));
}
async function delEdSale(id){
  if(!confirm(t('ed.deleteConfirm'))) return;
  edSales = edSales.filter(s=>s.id!==id);
  await saveED();
  renderEldorado();
}

function renderEldorado(){
  const el = g('edList');
  const sum = g('edSummary');
  if(!el) return;
  refreshCombinedStats();
  const q  = (g('edQ')?.value||'').toLowerCase();
  const df = g('edDateFilter')?.value||'';
  const now = new Date();
  const todayStr = localDate(now);
  const wkStart = new Date(now); wkStart.setDate(now.getDate()-now.getDay());
  const moStart = todayStr.slice(0,7);

  edFilt = edSales.filter(s=>{
    const title = (s.title||'').toLowerCase();
    const oid   = String(s.orderId||'').toLowerCase();
    if(q && !title.includes(q) && !oid.includes(q)) return false;
    if(df){
      const d = s.date||'';
      if(df==='today' && d!==todayStr) return false;
      if(df==='week'  && d<localDate(wkStart)) return false;
      if(df==='month' && !d.startsWith(moStart)) return false;
      if(df==='custom'){
        const from = g('edFrom')?.value||'';
        const to   = g('edTo')?.value||'';
        if(from && d<from) return false;
        if(to && d>to) return false;
      }
    }
    return true;
  });

  const pp = 50;
  const tot = Math.ceil(edFilt.length/pp);
  if(edPg > tot) edPg = Math.max(1,tot);
  const page = edFilt.slice((edPg-1)*pp, edPg*pp);
  const pag = g('edPag');

  if(!edFilt.length){
    el.innerHTML = '<div class="none">'+(edSales.length?'Нічого не знайдено':'Ще немає записів')+'</div>';
    if(sum) sum.innerHTML = '';
    if(pag) pag.style.display='none';
    return;
  }

  const isMobile = window.innerWidth <= 600;
  if(isMobile){
    el.innerHTML = page.map(s=>{
      const prof = s.profit||0;
      return `<div style="background:var(--card2);border:1px solid var(--brd);border-radius:8px;padding:12px;margin-bottom:8px">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:6px">
          <div style="font-weight:700;font-size:14px;flex:1">${esc((s.title||'—').substring(0,60))}</div>
          <div class="${prof>=0?'profit-pos':'profit-neg'}" style="font-family:var(--font);font-size:14px;font-weight:700;white-space:nowrap">${prof>=0?'+':''}$${prof.toFixed(2)}</div>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
          <div style="display:flex;gap:8px;align-items:center;font-size:11px;color:var(--mu)">
            <span>${esc(s.date||'—')}</span>
            ${s.category?`<span style="background:rgba(6,182,212,.12);color:var(--a3);border:1px solid rgba(6,182,212,.3);padding:1px 6px;border-radius:3px">${esc(s.category)}</span>`:''}
            <span>↑$${(s.price||0).toFixed(2)}</span>
            <span>↓${s.buy?'$'+(s.buy||0).toFixed(2):'—'}</span>
          </div>
          <div style="display:flex;gap:6px">
            <button onclick="editEdSale(${s.id})" style="background:transparent;border:1px solid var(--brd);color:var(--a1);padding:5px 9px;border-radius:4px;font-size:12px;cursor:pointer">✏</button>
            <button onclick="delEdSale(${s.id})" style="background:transparent;border:1px solid var(--brd);color:var(--rd);padding:5px 9px;border-radius:4px;font-size:12px;cursor:pointer">🗑</button>
          </div>
        </div>
      </div>`;
    }).join('');
  } else {
    el.innerHTML = '<div class="bub-wrap">' + page.map(s => {
      const pr = Number(s.profit||0);
      return `<div class="bub">
        <div class="bub-head">
          <span class="bub-date">${esc(fmtDate(s.date))}</span>
          ${s.category?`<span class="bub-chip">${esc(s.category)}</span>`:''}
          <span class="bub-title">${esc(s.title)}</span>
          <div class="bub-acts">
            <button class="bub-btn" onclick="editEdSale(${s.id})" title="Редагувати">✏</button>
            <button class="bub-btn del" onclick="delEdSale(${s.id})" title="Видалити">🗑</button>
          </div>
        </div>
        <div class="bub-stats">
          <span class="bs">Продав <b>$${Number(s.price||0).toFixed(2)}</b></span>
          <span class="bs">Купив <b>$${Number(s.buy||0).toFixed(2)}</b></span>
          <span class="bs">Комісія <b class="neg">-$${Number(s.fee||0).toFixed(2)}</b></span>
          <span class="bs ${pr>=0?'pos':'negp'}">${t('k.profit')} <b>${pr>=0?'+':''}$${pr.toFixed(2)}</b></span>
        </div>
        ${s.orderId?`<div class="bub-id">🆔 ${esc(s.orderId)}</div>`:''}
      </div>`;
    }).join('') + '</div>';
  }

  // Підсумки по поточному фільтру
  const total       = edFilt.reduce((a,s)=>a+(s.price||0),0);
  const totalProfit = edFilt.reduce((a,s)=>a+(s.profit||0),0);
  const totalFee    = edFilt.reduce((a,s)=>a+(s.fee||0),0);
  const totalBuy    = edFilt.reduce((a,s)=>a+(s.buy||0),0);
  const plProfit    = purchases.reduce((a,p)=>a+(p.afterFee||0),0);
  const combined    = plProfit + totalProfit;
  if(sum){
    const uah = _rate ? ' <span style="color:var(--mu)">(₴'+(totalProfit*_rate).toFixed(2)+')</span>' : '';
    sum.innerHTML = `<span style="color:var(--mu)">${LANG==='uk'?'Продажів':(LANG==='ru'?'Продаж:':'Sales')}: <b style="color:var(--tx)">${edFilt.length}</b>${edFilt.length!==edSales.length?' із '+edSales.length:''}</span>`+
      `<span style="color:var(--mu)">Виторг: <b style="color:var(--tx)">$${total.toFixed(2)}</b></span>`+
      `<span style="color:var(--mu)">Купив: <b style="color:var(--mu)">$${totalBuy.toFixed(2)}</b></span>`+
      `<span style="color:var(--mu)">${LANG==='uk'?'Комісія':(LANG==='ru'?'Комиссия':'Fee')}: <b style="color:var(--rd)">-$${totalFee.toFixed(2)}</b></span>`+
      `<span style="color:var(--mu)">Прибуток: <b style="color:var(--gr)">${totalProfit>=0?'+':''}$${totalProfit.toFixed(2)}</b>${uah}</span>`+
      `<span style="border-left:1px solid var(--brd);padding-left:14px;color:var(--mu)">Разом з P&L: <b style="color:${combined>=0?'var(--gr)':'var(--rd)'}">${combined>=0?'+':''}$${combined.toFixed(2)}</b>${_rate?' <span style="color:var(--mu)">(₴'+(combined*_rate).toFixed(2)+')</span>':''}</span>`;
  }

  // Розбивка по категоріях
  renderEdBreakdown();

  // Пагінація
  if(!pag) return;
  if(tot<=1){ pag.style.display='none'; return; }
  let h='';
  if(edPg>1) h+=`<button class="pb" onclick="edGo(${edPg-1})">←</button>`;
  const s=Math.max(1,edPg-2), en=Math.min(tot,edPg+2);
  for(let i=s;i<=en;i++) h+=`<button class="pb${i===edPg?' on':''}" onclick="edGo(${i})">${i}</button>`;
  if(edPg<tot) h+=`<button class="pb" onclick="edGo(${tot})">→</button>`;
  h+=`<span style="font-size:10px;color:var(--mu)">${edFilt.length} ${plural(edFilt.length,'records')}</span>`;
  pag.innerHTML=h; pag.style.display='flex';
}
function renderEdBreakdown(){
  const el = g('edBreakdown');
  if(!el) return;
  const cats = [...new Set(edSales.map(s=>(s.category||'').trim()).filter(Boolean))].sort();
  const dl = g('edCatList');
  if(dl) dl.innerHTML = cats.map(c=>`<option value="${esc(c)}">`).join('');
  if(!edFilt.length){ el.innerHTML='<div class="none">Немає даних</div>'; return; }
  const map = {};
  edFilt.forEach(s=>{
    const k = (s.category||'').trim() || 'Без категорії';
    if(!map[k]) map[k]={count:0, rev:0, buy:0, profit:0};
    map[k].count++;
    map[k].rev    += s.price||0;
    map[k].buy    += s.buy||0;
    map[k].profit += s.profit||0;
  });
  const rows = Object.entries(map).sort((a,b)=>b[1].profit-a[1].profit);
  const max = Math.max(...rows.map(r=>Math.abs(r[1].profit)), 1);
  el.innerHTML = '<table class="sup-table"><thead><tr><th>КАТЕГОРІЯ</th><th style="text-align:right">УГОД</th><th style="text-align:right">ВИТОРГ</th><th style="text-align:right">ПРИБУТОК</th><th style="text-align:right">МАРЖА</th><th style="width:140px"></th></tr></thead><tbody>'+
    rows.map(([k,s])=>{
      const margin = s.buy>0 ? (s.profit/s.buy*100) : 0;
      const pct = Math.round(Math.abs(s.profit)/max*100);
      const color = s.profit>=0?'var(--gr)':'var(--rd)';
      return `<tr>
        <td style="font-weight:600">${esc(k)}</td>
        <td style="text-align:right;color:var(--mu)">${s.count}</td>
        <td style="text-align:right;font-family:var(--font);font-size:11px">${locMoney(s.rev)}</td>
        <td style="text-align:right;font-family:var(--font);font-weight:700;color:${color}">${s.profit>=0?'+':'-'}${locMoney(Math.abs(s.profit))}</td>
        <td style="text-align:right;font-size:11px;color:var(--mu)">${s.buy>0?margin.toFixed(0)+'%':'—'}</td>
        <td><div style="background:var(--bg2);border-radius:4px;height:8px;overflow:hidden"><div style="height:100%;width:${pct}%;background:${color};border-radius:4px"></div></div></td>
      </tr>`;
    }).join('')+'</tbody></table>';
}

function edGo(n){ edPg=n; renderEldorado(); window.scrollTo({top:0,behavior:'smooth'}); }

function exportEdCsv(){
  const rows=[['Дата','Назва','Продав $','Купив $','Комісія $',(LANG==='uk'?'Прибуток $':(LANG==='ru'?'Прибыль $':'Profit $')),'Order ID']];
  edFilt.forEach(s=>{
    rows.push([s.date||'', s.title||'', (s.price||0).toFixed(2), (s.buy||0).toFixed(2),
      (s.fee||0).toFixed(2), (s.profit||0).toFixed(2), s.orderId||'']);
  });
  const csv=rows.map(r=>r.map(c=>'"'+String(c).replace(/"/g,'""')+'"').join(',')).join('\n');
  const a=document.createElement('a');
  a.href='data:text/csv;charset=utf-8,\uFEFF'+encodeURIComponent(csv);
  a.download='eldorado_'+todayLocal()+'.csv';
  a.click();
  toast('✅ CSV ELDORADO завантажено!');
}

// ═══════════════════════════════════════════════
// 🛒 ЗАКУПІВЛЯ — посторінково із сервера
//    (раніше вкладка тягла ~970 КБ JSON; тепер 50 товарів на запит + gzip)
// ═══════════════════════════════════════════════
let supPage = {items: [], total: 0, page: 1, per: 50, counts: {}, sale: 0, gone: 0};
let _supReq = 0, _supTimer = null, _supAbort = null;

function supQuery(page){
  const p = new URLSearchParams();
  p.set('page', page||1);
  p.set('per', 50);
  const q=(g('supQ')?.value||'').trim();  if(q) p.set('q', q);
  const src=g('supSrc')?.value||'';       if(src) p.set('src', src);
  const sort=g('supSort')?.value||'';     if(sort) p.set('sort', sort);
  if(g('supAvail')?.checked) p.set('avail','1');
  if(g('supGone')?.checked) p.set('gone','1');
  if(g('supCheaper')?.checked) p.set('cheaper','1');
  return p.toString();
}

async function loadRestock(){
  const box = g('restockBox'); if(!box) return;
  try{
    const d = await fetch('/api/insights/restock').then(r=>r.json());
    if(!d.ok || !d.items || !d.items.length){ box.innerHTML=''; return; }
    const money = v => locMoney(v);
    box.innerHTML = '<div class="ph" style="margin:0 0 8px"><span>'+t('restock.title')+'</span></div>'
      + '<div style="display:flex;gap:10px;flex-wrap:wrap">'
      + d.items.map(x => '<div style="background:var(--card2);border:1px solid var(--brd);border-radius:10px;padding:10px 12px;min-width:200px">'
        + '<div style="font-weight:700;font-size:13px">'+esc(x.game)+'</div>'
        + '<div style="font-size:11px;color:var(--mu);margin-top:3px">'+t('restock.sold')+' '+x.sold+' · '+t('restock.stock')+' '+x.stock+'</div>'
        + '<div style="font-size:12px;color:'+(x.margin>=0?'var(--gr)':'var(--rd)')+';margin-top:4px">'+t('restock.margin')+' '+fmtPct(x.margin)+' · '+money(x.profit)+'</div>'
        + '<div style="font-size:10px;color:var(--yw);margin-top:3px">'+(x.stock===0?t('restock.out'):t('restock.low'))+'</div></div>').join('')
      + '</div>';
  }catch(e){ box.innerHTML=''; }
}
async function loadBuyList(force){
  const el = g('buyList'); if(!el) return;
  loadRestock();
  if(!force && el.dataset.loaded === '1') return;
  el.innerHTML = '<div class="none">'+t('rep.calculating')+'</div>';
  try{
    const d = await fetch('/api/buy-list?limit=15').then(r => r.json());
    if(!d.ok){ el.innerHTML = '<div class="al err">⚠ ' + esc(d.error || t('an.noData')) + '</div>'; return; }
    const items = d.items || [];
    if(!items.length){
      const emptyTxt = LANG==='ru' ? ('Нет прибыльных вариантов за последние '+(d.days||90)+' дней')
        : LANG==='en' ? ('No profitable options in the last '+(d.days||90)+' days')
        : ('Немає прибуткових варіантів за останні '+(d.days||90)+' днів');
      el.innerHTML = '<div class="none">'+emptyTxt+'</div>';
      return;
    }
    el.dataset.loaded = '1';
    el.innerHTML = '<div class="bub-wrap">' + items.map(x => {
      const ttl = x.url
        ? '<a href="' + esc(x.url) + '" target="_blank" rel="noopener" style="color:var(--tx)">' + esc(x.title) + '</a>'
        : esc(x.title);
      return '<div class="bub">'
        + '<div class="bub-head">'
        + '<span class="bub-chip">' + esc(x.game) + '</span>'
        + '<span class="bub-title">' + ttl + '</span>'
        + '<span class="bub-date" style="color:var(--gr)">ROI ' + Math.round((x.roi || 0) * 100) + '%</span>'
        + '</div>'
        + '<div class="bub-stats">'
        + '<span class="bs">'+t('plan.supplier')+' <b>$' + Number(x.price || 0).toFixed(2) + '</b></span>'
        + '<span class="bs">'+t('plan.yourSale')+' <b>$' + Number(x.expected || 0).toFixed(2) + '</b></span>'
        + '<span class="bs pos">'+t('plan.margin')+' <b>+$' + Number(x.margin || 0).toFixed(2) + '</b></span>'
        + '<span class="bs">'+t('plan.demand')+' <b>' + (x.demand || 0) + '</b> '+plural(x.demand||0,'sales')+'</span>'
        + (x.source ? '<span class="bs">' + esc(x.source) + '</span>' : '')
        + '</div></div>';
    }).join('') + '</div>';
  }catch(e){ el.innerHTML = '<div class="al err">⚠ ' + esc(String(e)) + '</div>'; }
}

async function loadSupply(page=1, force=false){
  loadBuyList();
  loadSupStatus();
  if(supLoaded && !force && page===1 && supPage.items.length) return;
  // Скасовуємо попередній запит: інакше пізніша відповідь може "загубитись"
  // через tag-перевірку і вкладка назавжди лишається на «Завантаження…».
  if(_supAbort){ try{ _supAbort.abort(); }catch(e){} }
  const ctrl=new AbortController(); _supAbort=ctrl;
  const tag = ++_supReq;
  g('supAl').className='al info';
  g('supAl').textContent='⏳ Завантаження...';
  try{
    const t=setTimeout(()=>ctrl.abort(),12000);
    const r = await fetch('/api/suppliers?'+supQuery(page),{signal:ctrl.signal});
    clearTimeout(t);
    if(!r.ok) throw new Error('HTTP '+r.status);
    const d = await r.json();
    if(tag !== _supReq) return;              // відповідь на старіший запит — ігнор
    supPage = {items: d.items||[], total: d.total||0, page: d.page||page,
               per: d.per||50, counts: d.counts||{}, sale: d.sale||0,
               gone: d.gone||0, cheaper: d.cheaper||0};
    supLoaded = supPage.items.length > 0;
    window._supItems = supPage.items;
    renderSupStats();
    renderSupPage();
    renderSupCards(window._supSuppliers || []);
  }catch(ex){
    if(ex && ex.name==='AbortError') return;
    if(tag !== _supReq) return;
    supLoaded=false;
    g('supAl').className='al err';
    g('supAl').textContent='❌ '+ex.message+' (натисни ↺)';
    if(g('supList')) g('supList').innerHTML='';
  }finally{
    if(_supAbort===ctrl) _supAbort=null;
  }
}

function renderSupStats(){
  const c = supPage.counts||{};
  g('supTotal').textContent = supPage.total;
  if(g('supCnt')) g('supCnt').textContent = supPage.total;
  g('supAl').className='al ok';
  g('supAl').style.display = supPage.total ? '' : 'none';
  g('supAl').textContent = '✅ '+(supPage.total)+' '+plural(supPage.total,'products')
    + (supPage.sale ? ' · 🔥 '+(LANG==='ru'?'Скидки: ':LANG==='en'?'Sale: ':'Акція: ')+supPage.sale : '')
    + (supPage.gone ? (LANG==='ru'?' · 🗑 исчезло: ':LANG==='en'?' · 🗑 gone: ':' · 🗑 зникло: ')+supPage.gone : '')
    + (supPage.cheaper ? ' · 💸 '+(LANG==='ru'?'дешевле в других: ':LANG==='en'?'cheaper elsewhere: ':'дешевше в інших: ')+supPage.cheaper : '');
}

function renderSupply(){                 // викликають фільтри/пошук
  if(_supTimer) clearTimeout(_supTimer);
  _supTimer = setTimeout(()=>{ _supTimer=null; loadSupply(1, true); }, 250);
}
function toggleCustomDateRange(){
  const df=g('plDateFilter')?.value||'';
  const el=g('plCustomRange');
  if(el) el.style.display=df==='custom'?'flex':'none';
}
const _dismissedNew = new Set(safeArray(localStorage.getItem('sup_dismissed_new')||'[]'));
const _dismissedChanged = new Set(safeArray(localStorage.getItem('sup_dismissed_changed')||'[]'));
function dismissNew(pid){
  _dismissedNew.add(pid);
  localStorage.setItem('sup_dismissed_new', JSON.stringify([..._dismissedNew]));
  renderSupPage();
}
function dismissChanged(pid){
  _dismissedChanged.add(pid);
  localStorage.setItem('sup_dismissed_changed', JSON.stringify([..._dismissedChanged]));
  renderSupPage();
}
document.addEventListener('click', e=>{
  const b=e.target.closest('.new-badge');
  if(b && b.dataset.pid) { e.stopPropagation(); dismissNew(b.dataset.pid); }
  const c=e.target.closest('.changed-badge');
  if(c && c.dataset.pid) { e.stopPropagation(); dismissChanged(c.dataset.pid); }
  // відновлення бекапу через data-атрибут (без inline-JS і екранування в рядок)
  const r=e.target.closest('button[data-restore]');
  if(r && r.dataset.restore) restoreBackup(r.dataset.restore);
  // порівняння цін
  const cmp=e.target.closest('button[data-cmp]');
  if(cmp && cmp.dataset.cmp) openCompare(cmp.dataset.cmp);
  // історія ціни
  const hst=e.target.closest('button[data-hist]');
  if(hst && hst.dataset.hist) openHistory(hst.dataset.hist);
  if(e.target === g('cmpModal')) closeCmp();
  if(e.target === g('histModal')) closeHist();
});

function supAgeBadge(p, now, DAY){
  const updAge=now-(p.updated_at||0);
  const seenAge=p.seen_at>0 ? now-p.seen_at : Infinity;
  if(p.gone) return `<span style="background:rgba(239,68,68,.12);color:var(--rd);border:1px solid rgba(239,68,68,.3);padding:1px 6px;border-radius:3px;font-size:11px;font-weight:700">🗑 ${t('sup.gone')}</span>`;
  if(seenAge<DAY*3 && !_dismissedNew.has(p.id))
    return `<span class="new-badge" data-pid="${esc(p.id)}" style="background:rgba(16,185,129,.15);color:var(--gr);border:1px solid rgba(16,185,129,.3);padding:1px 6px;border-radius:3px;font-size:11px;font-weight:700;cursor:pointer" title="Клікни щоб прибрати">🆕 ✕</span>`;
  if(p.updated_at>0 && updAge<DAY*3 && !_dismissedChanged.has(p.id))
    return `<span class="changed-badge" data-pid="${esc(p.id)}" style="background:rgba(245,158,11,.12);color:var(--yw);border:1px solid rgba(245,158,11,.3);padding:1px 6px;border-radius:3px;font-size:11px;font-weight:700;cursor:pointer" title="Клікни щоб прибрати">🔄 ✕</span>`;
  if(p.updated_at>0 && updAge<DAY*30) return `<span style="color:var(--mu);font-size:9px">${Math.floor(updAge/DAY)} ${LANG==='ru'?'дн. назад':LANG==='en'?'days ago':'дн. тому'}</span>`;
  return '';
}

function renderSupPage(){
  const page = supPage.items || [];
  if(!page.length){
    g('supList').innerHTML = '<div class="none">'+(supPage.total?t('sup.none'):t('sup.empty'))+'</div>';
    g('supPag').style.display='none';
    return;
  }
  const now=Date.now()/1000, DAY=86400;
  const isMobile = window.innerWidth <= 600;
  const cheapBadge = c => c
    ? `<span style="background:rgba(248,113,113,.12);color:var(--rd);border:1px solid rgba(248,113,113,.3);padding:1px 6px;border-radius:5px;font-size:11px;font-weight:700;white-space:nowrap" title="${esc(c.sourceName)}">💸 −$${Math.abs(c.diff).toFixed(2)}</span>`
    : '';
  if(isMobile){
    g('supList').innerHTML = page.map((p,i)=>{
      const _disc = Number(p.discount);
      const disc=p.isOnSale?`<span style="background:rgba(239,68,68,.1);color:var(--rd);border:1px solid rgba(239,68,68,.2);padding:1px 6px;border-radius:3px;font-size:11px;font-weight:700">${Number.isFinite(_disc)&&_disc>0?('-'+_disc+'%'):t('sup.sale')}</span>`:'';
      return `<div style="background:var(--card2);border:1px solid var(--brd);border-left:3px solid ${p.gone?'var(--rd)':'transparent'};border-radius:12px;padding:14px;margin-bottom:10px">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:8px">
          <a href="${esc(p.url)}" target="_blank" style="color:var(--tx);text-decoration:none;font-weight:700;font-size:15px;flex:1">${esc((p.title||'').substring(0,70))}</a>
          <span style="font-size:15px;font-weight:800;color:${p.gone?'var(--mu)':'var(--gr)'};white-space:nowrap">$${(p.price||0).toFixed(2)}</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
          <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;font-size:11px">
            <span style="display:inline-flex;padding:2px 7px;border-radius:5px;font-weight:700;border:1px solid;background:${p.sourceColor}18;color:${p.sourceColor};border-color:${p.sourceColor}38">${p.sourceEmoji} ${p.sourceName}</span>
            ${disc}
            ${cheapBadge(p.cheaper)}
            <span>${p.gone?'<span style="color:var(--mu)">—</span>':(p.available?'<span style="color:var(--gr)">✓ '+t('sup.availYes')+'</span>':'<span style="color:var(--rd)">✗ '+t('sup.availNo')+'</span>')}</span>
            ${supAgeBadge(p, now, DAY)}
          </div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;width:100%">
            <a href="${esc(p.url)}" target="_blank" class="ilnk" style="padding:6px 10px;gap:5px;display:inline-flex;align-items:center" title="Відкрити в магазині"><svg class="ic"><use href="#ic-ext"/></svg>${t('cb.shop')}</a>
            <button class="btn" style="padding:6px 10px" onclick="addTargetFromSup(_supItems[${i}])" title="Цільова ціна">🎯</button>
            <button class="btn" style="padding:6px 10px;gap:5px" data-hist="${esc(p.id)}" title="Історія ціни за 30 днів"><svg class="ic"><use href="#ic-chart"/></svg>${t('cb.history')}</button>
            <button class="btn" style="padding:6px 10px;gap:5px" data-cmp="${esc(p.id)}" title="Порівняти ціну в інших магазинах"><svg class="ic"><use href="#ic-scale"/></svg>${t('cb.compare')}</button>
            <button class="btn" style="padding:6px 10px;gap:5px;white-space:nowrap" onclick="openLotModal(_supItems[${i}])" title="Калькулятор ціни лота"><svg class="ic"><use href="#ic-calc"/></svg>${t('cb.lot')}</button>
          </div>
        </div>
      </div>`;
    }).join('');
  } else {
    g('supList').innerHTML=`<table class="sup-table"><thead><tr><th>${t('ct.name')}</th><th>${t('ct.src')}</th><th>${t('ct.price')}</th><th>${t('ct.disc')}</th><th>${t('ct.avail')}</th><th>${t('ct.date')}</th><th></th></tr></thead><tbody>`+
    page.map((p,i)=>{
      const bc=`background:${p.sourceColor}18;color:${p.sourceColor};border-color:${p.sourceColor}38`;
      const _disc = Number(p.discount);
      const disc=p.isOnSale?`<span style="background:rgba(239,68,68,.1);color:var(--rd);border:1px solid rgba(239,68,68,.2);padding:1px 5px;border-radius:3px;font-size:11px;font-weight:700">${Number.isFinite(_disc)&&_disc>0?('-'+_disc+'%'):t('sup.sale')}</span>`:'—';
      const cheap=p.cheaper?`<span style="display:block;margin-top:3px;color:var(--rd);font-size:11px">💸 −$${Math.abs(p.cheaper.diff).toFixed(2)} · ${esc(p.cheaper.sourceName)}</span>`:'';
      return`<tr${p.gone?' style="opacity:.62"':''}><td style="max-width:300px"><a href="${esc(p.url)}" target="_blank" style="text-decoration:none;font-weight:600">${esc(p.title)}</a></td>
        <td><span style="display:inline-flex;padding:2px 7px;border-radius:5px;font-size:11px;font-weight:700;border:1px solid;${bc}">${p.sourceEmoji} ${p.sourceName}</span></td>
        <td><span style="font-size:14px;font-weight:800;color:${p.gone?'var(--mu)':'var(--gr)'}">$${(p.price||0).toFixed(2)}</span>${p.comparePrice>0?`<span style="font-size:11px;color:var(--mu);text-decoration:line-through;display:block">$${p.comparePrice.toFixed(2)}</span>`:''}${cheap}</td>
        <td>${disc}</td>
        <td>${p.gone?'<span style="color:var(--mu)">—</span>':(p.available?'<span style="color:var(--gr)">✓</span>':'<span style="color:var(--rd)">✗</span>')}</td>
        <td>${supAgeBadge(p, now, DAY)}</td>
        <td style="white-space:nowrap;text-align:right"><div style="display:inline-flex;gap:5px;align-items:center;justify-content:flex-end"><a href="${esc(p.url)}" target="_blank" class="ilnk" style="padding:6px 10px;gap:5px;display:inline-flex;align-items:center" title="Відкрити в магазині"><svg class="ic"><use href="#ic-ext"/></svg>${t('cb.shop')}</a><button class="btn" style="padding:6px 10px" onclick="addTargetFromSup(_supItems[${i}])" title="Цільова ціна">🎯</button><button class="btn" style="padding:6px 10px;gap:5px" data-hist="${esc(p.id)}" title="Історія ціни за 30 днів"><svg class="ic"><use href="#ic-chart"/></svg>${t('cb.history')}</button><button class="btn" style="padding:6px 10px;gap:5px" data-cmp="${esc(p.id)}" title="Порівняти ціну в інших магазинах"><svg class="ic"><use href="#ic-scale"/></svg>${t('cb.compare')}</button><button class="btn" style="padding:6px 10px;gap:5px;white-space:nowrap" onclick="openLotModal(_supItems[${i}])" title="Калькулятор ціни лота"><svg class="ic"><use href="#ic-calc"/></svg>${t('cb.lot')}</button></div></td></tr>`;
    }).join('')+'</tbody></table>';
  }
  window._supItems=page;
  const tot=Math.ceil(supPage.total/supPage.per), pag=g('supPag');
  if(tot<=1){pag.style.display='none';return;}
  const cur=supPage.page;
  let h='';
  if(cur>1)h+=`<button class="pb" onclick="supGo(${cur-1})">←</button>`;
  const s=Math.max(1,cur-2),en=Math.min(tot,cur+2);
  for(let i=s;i<=en;i++)h+=`<button class="pb${i===cur?' on':''}" onclick="supGo(${i})">${i}</button>`;
  if(cur<tot)h+=`<button class="pb" onclick="supGo(${tot})">→</button>`;
  h+=`<span style="font-size:10px;color:var(--mu)">${supPage.total} · стор. ${cur}/${tot}</span>`;
  pag.innerHTML=h;pag.style.display='flex';
}
function supGo(n){ loadSupply(n, true); window.scrollTo({top:0,behavior:'smooth'}); }

// ── стан оновлення бази + ручне оновлення ──
function renderSupCards(list){
  const box = g('supCards'); if(!box) return;
  if(!list || !list.length){
    const cached = Number((window.supPage && supPage.total) || 0) || (window._supItems ? _supItems.length : 0);
    if(cached > 0){
      box.innerHTML = '<div class="none">'+esc(cached+' '+plural(cached,'products'))+' · '+(LANG==='ru'?'из кеша':LANG==='en'?'from cache':'з кешу')+'</div>';
    } else {
      box.innerHTML = '<div class="none">'+t('sup.noSuppliers')+'</div>';
    }
    return;
  }
  box.innerHTML = list.map(s=>
    '<div style="background:var(--card2);border:1px solid var(--brd);border-left:3px solid '+(s.color||'var(--mu)')+';border-radius:10px;padding:10px 14px;min-width:130px">'
    + '<div style="font-size:11px;color:var(--mu)">'+(s.emoji||'')+' '+esc(s.name)+'</div>'
    + '<div style="font-size:18px;font-weight:700;color:'+(s.color||'var(--tx)')+'">'+(s.count||0)+'</div></div>'
  ).join('');
  // оновимо селект
  const sel = g('supSrc');
  if(sel && sel.options.length <= 1){
    list.forEach(s=>{
      const o = document.createElement('option');
      o.value = s.key; o.textContent = (s.emoji?s.emoji+' ':'') + s.name;
      sel.appendChild(o);
    });
  }
}

// ═══════════════ ОНБОРДИНГ (3 кроки) ═══════════════
let _onbStep = 0;
const ONB = {
  uk: { t1:'Вітання в Ledger', t2:'Назва й тема', t3:'Підключення кабінетів',
        lng:'Оберіть мову інтерфейсу', nm:'Назва застосунку', th:'Тема оформлення',
        tok:'Вставте свої токени (можна пропустити й працювати вручну)',
        next:'Далі →', fin:'Готово', skip:'Пропустити' },
  en: { t1:'Welcome to Ledger', t2:'Name & theme', t3:'Connect your accounts',
        lng:'Choose interface language', nm:'App name', th:'Theme',
        tok:'Paste your tokens (or skip — manual mode works fine)',
        next:'Next →', fin:'Done', skip:'Skip' },
  ru: { t1:'Добро пожаловать в Ledger', t2:'Название и тема', t3:'Подключение кабинетов',
        lng:'Выберите язык интерфейса', nm:'Название приложения', th:'Тема оформления',
        tok:'Вставьте свои токены (можно пропустить — ручной режим работает)',
        next:'Далее →', fin:'Готово', skip:'Пропустить' }
};

let _onboarded = true;   // читаємо з сервера в loadSettings
function onbOpen(){
  if(_onboarded) return;
  g('onb').style.display = 'flex';
  onbRender();
}
function onbRender(){
  g('onbStepInfo').textContent = '';
  g('onbSkip').style.display = 'none';
  g('onbNext').style.display = 'none';
  g('onbTitle').textContent = (LANG==='uk' ? 'Оберіть мову та валюту'
                            : LANG==='ru' ? 'Выберите язык и валюту'
                            : 'Choose language and currency');
  g('onbBody').innerHTML =
      '<div class="onb-lang" style="gap:10px">'
    + '<button class="' + (LANG==='uk'?'on':'') + '" onclick="onbSetLang(\'uk\')">Українська</button>'
    + '<button class="' + (LANG==='en'?'on':'') + '" onclick="onbSetLang(\'en\')">English</button>'
    + '<button class="' + (LANG==='ru'?'on':'') + '" onclick="onbSetLang(\'ru\')">Русский</button>'
    + '</div>'
    + '<div style="margin-top:14px"><div style="font-size:10px;color:var(--mu);letter-spacing:1px;margin-bottom:5px">'+(LANG==='en'?'CURRENCY':LANG==='ru'?'ВАЛЮТА':'ВАЛЮТА')+'</div>'
    + '<select id="onbCur" onchange="onbSetCurrency(this.value)" style="width:100%;font-size:15px">'+currencyOptions(_cur)+'</select></div>'
    + '<button class="btn gr" style="width:100%;margin-top:14px;padding:12px" onclick="onbDone()">'+(LANG==='en'?'Start':LANG==='ru'?'Начать':'Почати')+'</button>'
    + '<div style="color:var(--mu);font-size:11.5px;margin-top:12px;text-align:center">'
    + t('onb.hint')+'</div>';
}
let _onbCurManual = false;
function onbSetLang(l){
  // Не setLang(): він перезавантажує сторінку й ламає вибір валюти в онбордингу.
  LANG = (l==='en') ? 'en' : (l==='ru' ? 'ru' : 'uk');
  try{ localStorage.setItem('gt_lang', LANG); }catch(e){}
  // У онбордингу мова теж не змінює валюту — її вибирають окремо.
  applyLang(); onbRender();
}
function onbSetCurrency(v){ _onbCurManual = true; _currencyManual = true; _cur = v || 'USD'; applyCurrency(); }
function onbDone(){
  _onboarded = true;
  try{ localStorage.setItem('gt_onboarded','1'); }catch(e){}
  try{ fetch('/api/settings/save',{method:'POST',headers:{'Content-Type':'application/json'},
        body: JSON.stringify({onboarded: true, lang: LANG, currency: _cur, currency_manual: _onbCurManual})})
        .then(()=>{ location.reload(); }); }catch(e){ location.reload(); }
  const el = g('onb'); if(el) el.style.display = 'none';
}
function onbSkip(){ onbDone(); }
function onbNext(){ onbDone(); }

async function loadSupStatus(){
  try{
    const d = await fetch('/api/suppliers/status').then(r=>r.json());
    const el = g('supStatus'); if(!el) return;
    const secAgo = Math.max(0, Date.now()/1000 - (d.last_ok||0));
    const next = Math.round((d.next_in||0)/60);
    window._supSuppliers = d.suppliers || [];
    renderSupCards(window._supSuppliers);
    const sc = d.scraper||{};
    const keys = sc.keys || [];
    const usable = keys.filter(k => !(k.banned > Date.now()/1000) && (k.left == null || k.left > 5)).length;
    const left = keys.reduce((a, k) => a + (Number(k.left) || 0), 0);
    const nextTxt = d.busy ? (LANG==='ru'?'сейчас обновляю…':LANG==='en'?'refreshing now…':'зараз оновлюю…')
      : (next >= 60 ? (LANG==='ru'?'следующее через ':LANG==='en'?'next in ':'наступне через ') + Math.round(next/60) + (LANG==='ru'?' ч':LANG==='en'?' h':' год')
                    : (LANG==='ru'?'следующее через ':LANG==='en'?'next in ':'наступне через ') + next + (LANG==='ru'?' мин':LANG==='en'?' min':' хв'));
    const updTxt = d.last_ok ? (secAgo < 60
      ? (LANG==='ru'?'только что':LANG==='en'?'just now':'щойно')
      : secAgo < 3600
        ? Math.round(secAgo/60) + (LANG==='ru'?' мин назад':LANG==='en'?' min ago':' хв тому')
        : secAgo < 86400
          ? Math.round(secAgo/3600) + (LANG==='ru'?' ч назад':LANG==='en'?' h ago':' год тому')
          : Math.round(secAgo/86400) + (LANG==='ru'?' дн назад':LANG==='en'?' d ago':' дн тому')) : '—';
    el.innerHTML = (LANG==='ru'?'обновлено ':LANG==='en'?'updated ':'оновлено ') + updTxt
      + ' · ' + nextTxt
      + ' · '+(LANG==='ru'?'сегодня ':LANG==='en'?'today ':'сьогодні ') + (sc.used||0) + '/' + (sc.limit||30)
      + (keys.length ? ' · '+(LANG==='ru'?'ключи ':LANG==='en'?'keys ':'ключі ') + usable + '/' + keys.length + ' ('+(LANG==='ru'?'остаток ':LANG==='en'?'left ':'залишок ') + left + ')' : '')
      + (d.news && d.news.checked ? ' · 🆕 ' + (Math.round((Date.now()/1000 - d.news.checked)/60)) + (LANG==='ru'?' мин, новых ':LANG==='en'?' min, new ':' хв, нових ') + (d.news.last_new||0) : '')
      + (d.busy ? ' · ⏳ '+(LANG==='ru'?'обновление идёт':LANG==='en'?'refresh in progress':'оновлення йде') : '');
  }catch(e){}
}

async function checkNews(){
  toast('⏳ Перевіряю новинки через sitemap...');
  try{
    const d = await fetch('/api/suppliers/news',{method:'POST'}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||'помилка'), false); return; }
    toast(d.baseline ? '🔔 Базовий список магазинів збережено'
                     : ('🆕 Нових: '+d.new+(d.notified?' — алерт у Telegram':'')));
    loadSupStatus();
  }catch(e){ toast('⚠ '+e, false); }
}

async function refreshSuppliers(){
  if(!confirm('Оновити базу постачальників зараз?\n\nЦе витратить орієнтовно 10–15 кредитів ScraperAPI.')) return;
  toast('⏳ Оновлення запущено...');
  try{ await fetch('/api/suppliers/refresh',{method:'POST'}); }catch(e){}
  for(let i=0;i<100;i++){
    await new Promise(r=>setTimeout(r,3000));
    try{
      const d = await fetch('/api/suppliers/status').then(r=>r.json());
      if(!d.busy){ toast('✅ Базу оновлено'); break; }
    }catch(e){}
  }
  loadSupStatus(); loadSupply(1,true); loadBuyList();
}

// ═══════════════════════════════════════════════
// ⚖ ПОРІВНЯННЯ ЦІН МІЖ МАГАЗИНАМИ
// ═══════════════════════════════════════════════
async function openCompare(id){
  const modal=g('cmpModal'), box=g('cmpBody');
  if(!modal||!box) return;
  modal.style.display='flex';
  box.innerHTML='<div class="none">'+t('loading')+'</div>';
  try{
    const d=await fetch('/api/suppliers/compare?id='+encodeURIComponent(id)).then(r=>r.json());
    if(!d.ok){ box.innerHTML='<div class="none">'+esc(d.error||t('sup.notFound'))+'</div>'; return; }
    const p=d.product||{}, ms=d.matches||[];
    const shopH = LANG==='ru'?'МАГАЗИН':LANG==='en'?'SHOP':'МАГАЗИН';
    const prodH = LANG==='ru'?'ТОВАР':LANG==='en'?'PRODUCT':'ТОВАР';
    const priceH = LANG==='ru'?'ЦЕНА':LANG==='en'?'PRICE':'ЦІНА';
    const diffH = LANG==='ru'?'РАЗНИЦА':LANG==='en'?'DIFF':'РІЗНИЦЯ';
    let html=`<div style="font-size:13px;font-weight:700;line-height:1.35">${esc(p.title||'')}</div>
      <div style="font-size:11px;color:var(--mu);margin:4px 0 12px">${t('sup.compareBase')}: ${esc(p.sourceName||'')} · $${(p.price||0).toFixed(2)}</div>`;
    if(!ms.length){
      html+='<div class="none">'+t('sup.compareNone')+'</div>';
    } else {
      html+='<table class="sup-table"><thead><tr><th>'+shopH+'</th><th>'+prodH+'</th><th style="text-align:right">'+priceH+'</th><th style="text-align:right">'+diffH+'</th></tr></thead><tbody>';
      ms.forEach(m=>{
        const diff=Number(m.diff||0);
        const cls=diff<0?'pr-cheaper':diff>0?'pr-expensive':'pr-same';
        html+=`<tr><td style="white-space:nowrap">${m.sourceEmoji||''} ${esc(m.sourceName||'')}</td>
          <td style="max-width:260px"><a href="${esc(m.url)}" target="_blank" style="color:var(--tx);text-decoration:none">${esc((m.title||'').substring(0,80))}</a><span style="color:var(--mu);font-size:9px"> · ${m.match}%</span></td>
          <td style="text-align:right;font-family:var(--font)">$${(m.price||0).toFixed(2)}</td>
          <td style="text-align:right" class="cmp-pr ${cls}">${diff>0?'+':''}${diff.toFixed(2)}$</td></tr>`;
      });
      html+='</tbody></table>';
      if(d.best){
        const bestTxt = LANG==='ru'?'✅ Дешевле всего:':LANG==='en'?'✅ Cheapest:':'✅ Найдешевше:';
        html+=`<div style="margin-top:12px;font-size:12px;color:var(--gr)">${bestTxt} <b>${esc(d.best.sourceName||'')}</b> — $${(d.best.price||0).toFixed(2)}</div>`;
      }
    }
    box.innerHTML=html;
  }catch(e){ box.innerHTML='<div class="none">⚠ '+esc(String(e))+'</div>'; }
}
function closeCmp(){ const m=g('cmpModal'); if(m) m.style.display='none'; }

// ═══════════════════════════════════════════════
// 📈 ІСТОРІЯ ЦІНИ
// ═══════════════════════════════════════════════
async function openHistory(id){
  const m=g('histModal'), box=g('histBody');
  if(!m||!box) return;
  m.style.display='flex';
  box.innerHTML='<div class="none">'+t('loading')+'</div>';
  try{
    const d=await fetch('/api/suppliers/history?id='+encodeURIComponent(id)).then(r=>r.json());
    if(!d.ok){ box.innerHTML='<div class="none">'+esc(d.error||t('sup.notFound'))+'</div>'; return; }
    const h=d.history||[];
    const nowTxt = LANG==='ru'?'сейчас':LANG==='en'?'now':'зараз';
    let html=`<div style="font-size:15px;font-weight:700;line-height:1.35;margin-bottom:4px">${esc(d.title||'')}</div>
      <div style="font-size:13px;color:var(--mu);margin-bottom:14px">${esc(d.sourceName||'')} · ${nowTxt} $${(d.price||0).toFixed(2)}</div>`;
    if(h.length<2){
      html+='<div class="none">'+t('sup.historyEmpty')+'</div>';
    } else {
      const vals=h.map(x=>Number(x[1]));
      const mn=Math.min(...vals), mx=Math.max(...vals);
      const W=540,H=150,pad=10,span=(mx-mn)||1;
      const pt=(x,i)=>{
        const px=pad+(W-2*pad)*(i/(h.length-1));
        const py=H-pad-(H-2*pad)*((Number(x[1])-mn)/span);
        return [px,py];
      };
      const pts=h.map(pt).map(p=>p[0].toFixed(1)+','+p[1].toFixed(1)).join(' ');
      const dots=h.map(pt).map(p=>`<circle cx="${p[0].toFixed(1)}" cy="${p[1].toFixed(1)}" r="3.2" fill="var(--a1)"/>`).join('');
      const first=Number(h[0][1]), last=Number(h[h.length-1][1]);
      const diff=last-first, pct=first?((last/first-1)*100):0;
      const color=diff<0?'var(--gr)':diff>0?'var(--rd)':'var(--mu)';
      html+=`<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto;background:var(--bg2);border:1px solid var(--brd);border-radius:12px">
        <polyline points="${pts}" fill="none" stroke="var(--a1)" stroke-width="2.5" stroke-linejoin="round"/>${dots}
      </svg>
      <div style="display:flex;justify-content:space-between;margin-top:10px;font-size:13px">
        <span style="color:var(--mu)">${LANG==='ru'?'мин':LANG==='en'?'min':'мін'} $${mn.toFixed(2)} · ${LANG==='ru'?'макс':LANG==='en'?'max':'макс'} $${mx.toFixed(2)}</span>
        <span style="color:${color};font-weight:700">${diff>=0?'+':''}${diff.toFixed(2)}$ (${pct>=0?'+':''}${pct.toFixed(1)}%)</span>
      </div>
      <div style="margin-top:8px;font-size:12px;color:var(--mu)">${LANG==='ru'?'Точек':LANG==='en'?'Points':'Точок'}: ${h.length} · ${LANG==='ru'?'последнее изменение':LANG==='en'?'last change':'остання зміна'} ${new Date(Number(h[h.length-1][0])*1000).toLocaleString(dateLocale())}</div>`;
    }
    box.innerHTML=html;
  }catch(e){ box.innerHTML='<div class="none">⚠ '+esc(String(e))+'</div>'; }
}
function closeHist(){ const m=g('histModal'); if(m) m.style.display='none'; }

// ═══════════════════════════════════════════════
// 💼 ПЛАТФОРМИ (ZeusX / FunPay)
// ═══════════════════════════════════════════════
async function loadOffers(force){
  const el = g('offersList'); if(!el) return;
  el.innerHTML = '<div class="none">⏳ Читаю лоти...</div>';
  try{
    const d = await fetch('/api/offers' + (force ? '?refresh=1' : '')).then(r => r.json());
    if(!d.ok){ el.innerHTML = '<div class="al err">⚠ ' + esc(d.error || 'немає даних') + '</div>'; return; }
    const items = d.items || [];
    if(!items.length){ el.innerHTML = '<div class="none">Активних лотів не знайдено</div>'; return; }
    el.innerHTML = '<table class="sup-table"><thead><tr><th>ЛОТ</th><th>ГРА</th><th>ЦІНА</th><th>У ПОСТАЧАЛЬНИКА</th><th>РІЗНИЦЯ</th><th>К-СТЬ</th><th></th></tr></thead><tbody>'
      + items.map(o => {
          const sup = o.supplier;
          const supTxt = sup
            ? '<b>$' + Number(sup.min).toFixed(2) + '</b><div style="font-size:11px;color:var(--mu)">медіана $' + Number(sup.median).toFixed(2) + '</div>'
            : '<span style="color:var(--mu)">—</span>';
          let diff = '<span style="color:var(--mu)">—</span>';
          if(sup && o.diff_usd != null){
            const over = o.diff_usd > 0;
            diff = '<b style="color:' + (over ? 'var(--yw)' : 'var(--gr)') + '">' + (over ? '+' : '') + '$' + Number(o.diff_usd).toFixed(2) + '</b>'
                 + '<div style="font-size:11px;color:var(--mu)">' + (over ? 'дорожче за постачальника' : 'дешевше за постачальника') + '</div>';
          }
          return '<tr>'
            + '<td style="max-width:380px">' + (o.url
                ? '<a href="' + esc(o.url) + '" target="_blank" rel="noopener" style="font-weight:600">' + esc((o.title || '').slice(0, 90)) + '</a>'
                : '<b>' + esc((o.title || '').slice(0, 90)) + '</b>') + '</td>'
            + '<td>' + esc(o.game || '—') + '</td>'
            + '<td style="color:var(--gr);font-weight:700">$' + Number(o.price || 0).toFixed(2) + '</td>'
            + '<td>' + supTxt + '</td>'
            + '<td>' + diff + '</td>'
            + '<td>' + (o.qty ?? '—') + '</td>'
            + '<td>' + (o.url ? '<a class="ilnk" href="' + esc(o.url) + '" target="_blank" rel="noopener">↗</a>' : '') + '</td>'
            + '</tr>';
        }).join('')
      + '</tbody></table>';
  }catch(e){ el.innerHTML = '<div class="al err">⚠ ' + esc(String(e)) + '</div>'; }
}

async function loadCookieStatus(){
  try{
    const d = await fetch('/api/secrets/status').then(r => r.json());
    const el = g('ckStatus'); if(!el) return d;
    const yes = LANG==='ru' ? '✅ есть' : LANG==='en' ? '✅ set' : '✅ є';
    const no  = LANG==='ru' ? '<span style="color:var(--rd)">❌ нет</span>' : LANG==='en' ? '<span style="color:var(--rd)">❌ missing</span>' : '<span style="color:var(--rd)">❌ немає</span>';
    el.innerHTML = ' · FunPay: ' + (d.funpay_cookie ? yes : no)
      + ' · ZeusX: ' + (d.zeusx_cookie ? yes : no);
    return d;
  }catch(e){ return null; }
}

async function cookieFromBrowser(){
  try{
    const before = await loadCookieStatus();
    if(before && before.funpay_cookie && before.zeusx_cookie){
      toast(LANG==='ru' ? 'Cookie уже сохранены — сначала отключите их' : LANG==='en' ? 'Cookies are already saved — disconnect them first' : 'Cookie вже збережені — спочатку відключіть їх');
      return;
    }
    await fetch('/api/secrets/request',{method:'POST',headers:{'Content-Type':'application/json'},
      body: JSON.stringify({what:'both'})});
    toast(LANG==='ru' ? '⏳ Прошу агента скопировать cookie из браузера…' : LANG==='en' ? '⏳ Asking the agent to copy cookies from the browser…' : '⏳ Прошу агента скопіювати cookie з браузера…');
    for(let i=0;i<10;i++){
      await new Promise(r=>setTimeout(r,1500));
      const st = await fetch('/api/secrets/status').then(r=>r.json());
      if(st.funpay_cookie && st.zeusx_cookie){
        toast(LANG==='ru' ? '✅ Cookie скопированы из браузера' : LANG==='en' ? '✅ Cookies copied from browser' : '✅ Cookie скопійовано з браузера');
        loadCookieStatus(); loadPlatforms(true); return;
      }
    }
    toast(LANG==='ru' ? '⚠ Не удалось: откройте funpay.com и zeusx.com в окне агента' : LANG==='en' ? '⚠ Failed: open funpay.com and zeusx.com in the agent window' : '⚠ Не вдалось: відкрийте funpay.com і zeusx.com у вікні агента', false);
  }catch(e){ toast('⚠ ' + e, false); }
}

async function clearCookies(){
  const ok = LANG==='ru' ? 'Отключить сохранённые cookie FunPay и ZeusX?' : LANG==='en' ? 'Disconnect saved FunPay and ZeusX cookies?' : 'Відключити збережені cookie FunPay і ZeusX?';
  if(!confirm(ok)) return;
  try{
    const d = await fetch('/api/secrets/save',{method:'POST',headers:{'Content-Type':'application/json'},
      body: JSON.stringify({clear:true})}).then(r => r.json());
    if(!d.ok){ toast('⚠ ' + (d.error || ''), false); return; }
    g('ckFunpay').value = ''; g('ckZeusx').value = '';
    toast(LANG==='ru' ? '✅ Cookie отключены' : LANG==='en' ? '✅ Cookies disconnected' : '✅ Cookie відключено');
    loadCookieStatus(); loadPlatforms(true);
  }catch(e){ toast('⚠ ' + e, false); }
}

async function saveCookies(){
  const fp = (g('ckFunpay') && g('ckFunpay').value || '').trim();
  const zx = (g('ckZeusx') && g('ckZeusx').value || '').trim();
  if(!fp && !zx){ toast(t('set.cookieNeed'), false); return; }
  const body = {}; if(fp) body.funpay_cookie = fp; if(zx) body.zeusx_cookie = zx;
  try{
    const d = await fetch('/api/secrets/save',{method:'POST',headers:{'Content-Type':'application/json'},
      body: JSON.stringify(body)}).then(r => r.json());
    if(!d.ok){ toast('⚠ ' + (d.error || ''), false); return; }
    g('ckFunpay').value = ''; g('ckZeusx').value = '';
    toast(LANG==='ru' ? ('✅ Cookie сохранены: '+(d.saved||[]).join(', ')) : LANG==='en' ? ('✅ Cookies saved: '+(d.saved||[]).join(', ')) : ('✅ Cookie збережено: '+(d.saved||[]).join(', ')));
    loadCookieStatus();
    loadPlatforms(true);
  }catch(e){ toast('⚠ ' + e, false); }
}

async function loadPlatforms(force){
  loadCookieStatus();
  const el=g('platList'); if(!el) return;
  el.innerHTML='<div class="none">⏳ Читаю кабінети...</div>';
  try{
    const d=await fetch(force?'/api/platforms/refresh':'/api/platforms',
      force?{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}:{})
      .then(r=>r.json());
    const z=d.zeusx||{}, f=d.funpay||{};
    const errBox=(msg)=>'<div class="al '+(String(msg||'').indexOf('не підключено')>=0?'info':'err')+'" style="margin:0">'+esc(msg||'')+'</div>';
    const card=(title,color,rows,badge)=>`<div style="flex:1;min-width:280px;background:var(--card2);border:1px solid var(--brd);border-radius:12px;padding:16px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <div style="font-size:15px;font-weight:800;color:${color}">${title}</div>
        ${badge||''}
      </div>
      ${rows}
    </div>`;
    const TR = {uk:{acc:'Акаунт',bal:'Баланс',hold:'В обробці / на холді',wd:'Виведено всього',tier:'Тіри',orders:'Замовлень',msgs:'нові повідомлення',ordsl:'Замовлень (останні)',nosrc:'немає даних'},
                en:{acc:'Account',bal:'Balance',hold:'Processing / on hold',wd:'Withdrawn total',tier:'Tiers',orders:'Orders',msgs:'new messages',ordsl:'Orders (latest)',nosrc:'no data'},
                ru:{acc:'Аккаунт',bal:'Баланс',hold:'В обработке / холд',wd:'Выведено всего',tier:'Тиры',orders:'Заказов',msgs:'новые сообщения',ordsl:'Заказов (последние)',nosrc:'нет данных'}}[LANG] || {};
    const row=(l,v)=>`<div style="display:flex;justify-content:space-between;gap:10px;padding:6px 0;border-bottom:1px solid rgba(40,48,63,.5);font-size:14px">
      <span style="color:var(--mu)">${l}</span><b style="text-align:right">${v}</b></div>`;
    const zrows = z.ok
      ? row(TR.acc,esc(z.name||'—'))+row('Email',esc(z.email||'—'))+
        row(TR.bal,locMoney(z.balance))+
        row(TR.hold,locMoney(z.on_going)+' / '+locMoney(z.on_hold))+
        row(TR.wd,locMoney(z.withdraw))+
        row(TR.tier,esc((z.seller_tier||'—')+' / '+(z.buyer_tier||'—')))+
        row(TR.orders,`${z.orders_all||0} · ✅ ${z.orders_good||0} · ⏳ ${z.orders_pending||0} · ↩ ${z.orders_refunded||0}`)+
        row(TR.msgs,(d.mail_msgs||{}).ZeusX||0)
      : `${errBox(z.error||'немає даних')}
         <div style="font-size:12px;color:var(--mu);margin-top:8px">Потрібен свіжий cookie: увійдіть на zeusx.com і оновіть токен.</div>`;
    const fl = (f.list || []).slice(0, 4);
    const frows = f.ok
      ? row(TR.ordsl,f.orders_count||0)+
        row(TR.msgs,(d.mail_msgs||{}).FunPay||0)+
        (fl.length ? fl.map(o=>`<div style="padding:7px 0;border-bottom:1px solid rgba(40,48,63,.5);font-size:13px">
            <b>${esc((o.title||'').slice(0,62))}</b>
            <div style="color:var(--mu);font-size:12px">${esc(o.status||'')} · ${locMoney(o.price)} · ${esc(o.date||'')}</div>
          </div>`).join('')
        : '<div style="font-size:12px;color:var(--mu);padding-top:6px">Замовлень у списку немає</div>')
      : `${errBox(f.error||'немає даних')}
         <div style="font-size:12px;color:var(--mu);margin-top:8px">Cookie FunPay живе недовго — увійдіть на funpay.com і оновіть.</div>`;
    const e = d.eldorado||{};
    const erows = e.ok
      ? row('Продажів усього',e.count||0)+
        row('Виторг',locMoney(e.revenue))+
        row('Прибуток',locMoney(e.profit))+
        row('Цей місяць',(e.month_count||0)+' · '+locMoney(e.month_profit))+
        row('Джерело',esc(e.source||'—'))
      : errBox(e.error||'немає даних');
    el.innerHTML='<div style="display:flex;gap:14px;flex-wrap:wrap">'
      + card('⚡ ZeusX','var(--a1)',zrows+'<div class="online-w" data-plat="zeusx"></div>',z.ok?'<span style="color:var(--gr);font-size:12px">✓ онлайн</span>':'')
      + card('🔵 FunPay','var(--a3)',frows+'<div class="online-w" data-plat="funpay"></div>',f.ok?'<span style="color:var(--gr);font-size:12px">✓ онлайн</span>':'')
      + card('🟡 Eldorado','var(--yw)',erows+'<div class="online-w" data-plat="eldorado"></div>',e.ok?'<span style="color:var(--gr);font-size:12px">✓ облік</span>':'')
      + '</div>'
      + ((d.zeusx_imported||d.funpay_imported)?`<div class="al ok" style="margin-top:14px">📥 У чергу додано нових продажів: ZeusX ${d.zeusx_imported||0} · FunPay ${d.funpay_imported||0} — відкрийте вкладку «ЗАМОВЛЕННЯ».</div>`:'')
      + `<div style="font-size:12px;color:var(--mu);margin-top:10px">Eldorado не має публічного API — дані беруться з пошти та вашого ручного обліку.</div>`;
  calcMarkets();
  loadOffers();
  loadOnline();
  }catch(e){ el.innerHTML='<div class="al err">⚠ '+esc(String(e))+'</div>'; }
}

let ONLINE = null;
const ONL_TXT = {
 uk:{always:'Завжди онлайн',from:'з',to:'до',online:'онлайн',scheduled:'за розкладом',off:'вимкнено',error:'помилка',waiting:'перевіряю…',checked:'перевірено',refresh:'Оновити',saved:'Збережено',eld:'Eldorado не має публічного API — онлайн неможливий'},
 en:{always:'Always online',from:'from',to:'to',online:'online',scheduled:'scheduled',off:'off',error:'error',waiting:'checking…',checked:'checked',refresh:'Refresh',saved:'Saved',eld:'Eldorado has no public API — online is not possible'},
 ru:{always:'Всегда онлайн',from:'с',to:'до',online:'онлайн',scheduled:'по расписанию',off:'выключено',error:'ошибка',waiting:'проверяю…',checked:'проверено',refresh:'Обновить',saved:'Сохранено',eld:'Eldorado не имеет публичного API — онлайн невозможен'}
};
function onlT(){ return ONL_TXT[LANG] || ONL_TXT.uk; }
async function loadOnline(){
  try{ const r=await fetch('/api/online'); ONLINE=await r.json(); }catch(e){ ONLINE=null; }
  renderOnline();
}
function renderOnline(){
  document.querySelectorAll('.online-w').forEach(el=>{
    const p=el.dataset.plat, T=onlT();
    const d=ONLINE && ONLINE.platforms ? ONLINE.platforms[p] : null;
    if(p==='eldorado'){
      el.innerHTML='<div class="online-box"><div class="online-title"><span class="online-dot"></span>'+T.always+'</div><div style="font-size:11px;color:var(--mu);margin-top:4px">'+T.eld+'</div></div>';
      return;
    }
    if(!d){ el.innerHTML='<div class="online-box"><div class="online-foot">'+T.waiting+'</div></div>'; return; }
    const st=d.state||'off';
    const cls = st==='online'?'on':(st==='error'?'err':(st==='scheduled'?'wait':''));
    const color = st==='online'?'var(--gr)':(st==='error'?'var(--rd)':(st==='scheduled'?'var(--yw)':'var(--mu)'));
    const label = st==='online'?T.online:(st==='scheduled'?T.scheduled:(st==='error'?T.error:(st==='off'?T.off:T.waiting)));
    const ago = d.last_ts ? Math.max(0, Math.round((Date.now()/1000-d.last_ts)/60)) : null;
    el.innerHTML='<div class="online-box">'
      +'<div class="online-head"><div class="online-title"><span class="online-dot '+cls+'"></span>'+T.always+'</div>'
      +'<label class="online-switch"><input type="checkbox" data-onl-en="'+p+'" '+(d.enabled?'checked':'')+' onchange="saveOnline(\''+p+'\')"><span class="online-slider"></span></label></div>'
      +'<div class="online-times"><span style="color:var(--mu);font-size:11px">'+T.from+'</span>'
      +'<input type="time" class="online-time" data-onl-start="'+p+'" value="'+esc(d.start||'')+'" onchange="saveOnline(\''+p+'\')">'
      +'<span style="color:var(--mu);font-size:11px">'+T.to+'</span>'
      +'<input type="time" class="online-time" data-onl-end="'+p+'" value="'+esc(d.end||'')+'" onchange="saveOnline(\''+p+'\')"></div>'
      +'<div class="online-foot"><span class="online-state" style="color:'+color+'">● '+label+'</span>'
      +(ago!==null?'<span>'+T.checked+' '+ago+' хв</span>':'')
      +(d.error?'<span style="font-size:10.5px;opacity:.8">'+esc(d.error.slice(0,70))+'</span>':'')
      +'<button class="online-refresh" onclick="saveOnline(\''+p+'\',true)">↻ '+T.refresh+'</button></div></div>';
  });
}
async function saveOnline(p, force){
  const el=document.querySelector('.online-w[data-plat="'+p+'"]');
  if(!el) return;
  const en=el.querySelector('[data-onl-en]')?.checked||false;
  const start=el.querySelector('[data-onl-start]')?.value||'';
  const end=el.querySelector('[data-onl-end]')?.value||'';
  try{
    await fetch('/api/online/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({platform:p,enabled:en,start:start,end:end,tz:-new Date().getTimezoneOffset()})});
    await loadOnline();
  }catch(e){}
}
let mailItems=[];
let _lastMailNew=null;
let _favTimer=null, _titleTimer=null, _alertCount=0, _favTick=0;
function _favFrame(phase){
  const c = phase%2 ? '%2310b981' : '%23f59e0b';
  const r = phase%2 ? 15 : 11;
  return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="%230b0c0e"/><path d="M9.4 7.5h11.3v31.9h30.6v11.3H9.4z" fill="%23f2f2f2"/><circle cx="50" cy="14" r="'+r+'" fill="'+c+'" stroke="%230b0c0e" stroke-width="3"/><circle cx="50" cy="14" r="22" fill="none" stroke="'+c+'" stroke-width="2" opacity=".5"/></svg>';
}
function _favLinks(){ return Array.from(document.querySelectorAll('link[rel~="icon"]')); }
function setDefaultFavicon(){
  const urls=['/app-icon-32.png?v=5','/app-icon.svg?v=5','/app-icon-192.png?v=5','/app-icon-180.png?v=5'];
  _favLinks().forEach((l,i)=>{ try{ l.type=(i===1?'image/svg+xml':'image/png'); l.href=urls[i]||urls[0]; }catch(e){} });
  window._origFavicons=null;
}
function _paintFavicon(phase){
  const href='data:image/svg+xml,'+_favFrame(phase);
  _favLinks().forEach(l=>{ try{ l.type='image/svg+xml'; l.href=href; }catch(e){} });
}
function setFaviconBadge(show){
  const links=_favLinks(); if(!links.length) return;
  if(!window._origFavicons) window._origFavicons=links.map(l=>({el:l,href:l.href,type:l.type}));
  if(!show){
    clearInterval(_favTimer); clearInterval(_titleTimer);
    _favTimer=null; _titleTimer=null;
    (window._origFavicons||[]).forEach(o=>{ try{ o.el.type=o.type; o.el.href=o.href; }catch(e){} });
    return;
  }
  if(_favTimer) return;
  _favTick=0; _paintFavicon(0);
  _favTimer=setInterval(()=>{ _favTick++; _paintFavicon(_favTick); }, 450);
  const nm=window._appName||'Ledger';
  _titleTimer=setInterval(()=>{
    document.title = (document.title.indexOf('🔔')>=0)
      ? '('+_alertCount+') '+nm
      : '('+_alertCount+') 🔔 '+nm;
  }, 1000);
}
let _audioCtx=null;
function _ensureAudio(){
  try{
    if(!_audioCtx) _audioCtx=new (window.AudioContext||window.webkitAudioContext)();
    if(_audioCtx.state==='suspended') _audioCtx.resume();
    return _audioCtx;
  }catch(e){ return null; }
}
function playOrderSound(){
  try{
    if(g('orderSound') && !g('orderSound').checked) return;
    const ctx=_ensureAudio(); if(!ctx) return;
    const play=()=>{
      const now=ctx.currentTime;
      [[0,660],[0.18,880],[0.36,1320]].forEach(step=>{
        const o=ctx.createOscillator(), gain=ctx.createGain();
        o.type='triangle'; o.frequency.value=step[1];
        gain.gain.setValueAtTime(0.001,now+step[0]);
        gain.gain.exponentialRampToValueAtTime(0.55,now+step[0]+0.02);
        gain.gain.exponentialRampToValueAtTime(0.001,now+step[0]+0.20);
        o.connect(gain).connect(ctx.destination); o.start(now+step[0]); o.stop(now+step[0]+0.22);
      });
    };
    if(ctx.state==='suspended') ctx.resume().then(play).catch(()=>{});
    else play();
  }catch(e){}
}
function updateOrderNotifyUI(){
  const b=g('orderNotifyBtn'); if(!b || !('Notification' in window)) return;
  if(Notification.permission==='granted'){ b.innerHTML='🔔 <span>'+t('order.enabled')+'</span>'; b.style.opacity='.85'; }
  else if(Notification.permission==='denied'){ b.innerHTML='🔕 <span>'+t('order.blocked')+'</span>'; b.style.opacity='.6'; }
  else { b.innerHTML='🔔 <span>'+t('order.notify')+'</span>'; }
}
async function enableOrderNotifications(){
  if(!('Notification' in window)){ toast('⚠ Браузер не підтримує Notification', false); return; }
  _ensureAudio();
  try{
    const p=await Notification.requestPermission();
    updateOrderNotifyUI();
    playOrderSound();
    toast(p==='granted'?('🔔 '+t('order.granted')):('⚠ '+t('order.permissionDenied')), p==='granted');
  }catch(e){ toast('⚠ '+e, false); }
}
function orderNotify(n){
  try{
    if(Notification.permission==='granted'){
      const note=new Notification('🔔 '+t('order.new'), {body:n+' · '+(window._appName||'Ledger'), icon:'/icon-192.png', tag:'ledger-orders', requireInteraction:true});
      note.onclick=()=>{ try{ window.focus(); goOrders(); note.close(); }catch(e){} };
    }
  }catch(e){}
  playOrderSound();
}
function notifyNewOrder(n){
  const mark=g('brandMark'); if(mark) mark.classList.add('order-alert');
  _alertCount=n;
  document.title='('+n+') '+(window._appName||'Ledger');
  setFaviconBadge(true);
  const b=g('orderBanner'); if(b){ b.style.display='flex'; const bt=g('orderBannerText'); if(bt) bt.textContent=t('order.new')+': '+n; }
  orderNotify(n);
  toast('🔔 '+t('order.new')+': '+n);
}
function goOrders(){
  const tab=[...document.querySelectorAll('.tab')].find(x=>String(x.getAttribute('onclick')||'').includes("'mail'"));
  if(tab) tab.click();
}
function clearOrderAlert(){
  const mark=g('brandMark'); if(mark) mark.classList.remove('order-alert');
  document.title=(window._appName||'Ledger');
  setFaviconBadge(false);
  const b=g('orderBanner'); if(b) b.style.display='none';
}
// 🏮 Taobao
let tbItems = [], tbGame = '', tbSeg = '', tbSort = 'price', tbRegion = '';

async function tbCart(href, val){
  try{
    const d = await fetch('/api/taobao/mark', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({href: href, cart: val})}).then(r => r.json());
    if(!d.ok){ toast('⚠ ' + (d.error || 'помилка'), false); return; }
    loadTaobao();
  }catch(e){ toast('⚠ ' + e, false); }
}

async function tbCartClear(){
  if(!confirm(t('tb.clearCartConfirm'))) return;
  await fetch('/api/taobao/cart-clear', {method:'POST'}).then(r => r.json());
  loadTaobao();
}

async function tbAddManual(){
  const href = prompt(t('tb.manualLink')+':', '');
  if(!href) return;
  const title = prompt(t('tb.manualTitle')+':', '') || (LANG==='ru'?'Ручной лот':LANG==='en'?'Manual lot':'Ручний лот');
  const price = prompt(t('tb.manualPrice')+':', '');
  if(price === null) return;
  const cny = parseFloat(String(price).replace(',', '.')) || 0;
  if(cny <= 0){ toast(t('tb.pricePositive'), false); return; }
  const card = confirm(t('tb.cardQuestion'));
  const opts = prompt(t('tb.optionsQuestion'), '0');
  try{
    const d = await fetch('/api/taobao/manual', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({href: href, title: title, price_cny: cny,
                            card_pay: card, options: parseInt(opts, 10) || 0})}).then(r => r.json());
    if(!d.ok){ toast('⚠ ' + (d.error || 'помилка'), false); return; }
    toast(t('tb.added'));
    loadTaobao();
  }catch(e){ toast('⚠ ' + e, false); }
}

async function tbMark(href, val){
  try{
    const d = await fetch('/api/taobao/mark', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({href: href, card_pay: val})}).then(r => r.json());
    if(!d.ok){ toast('⚠ ' + (d.error || 'помилка'), false); return; }
    toast(val ? t('tb.markedCard') : t('tb.cardRemoved'));
    loadTaobao();
  }catch(e){ toast('⚠ ' + e, false); }
}

async function tbMarkOpts(href, cur){
  const v = prompt(t('tb.optionsQuestion'), cur || '');
  if(v === null) return;
  const n = Math.max(0, parseInt(v, 10) || 0);
  try{
    const d = await fetch('/api/taobao/mark', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({href: href, options: n})}).then(r => r.json());
    if(!d.ok){ toast('⚠ ' + (d.error || 'помилка'), false); return; }
    toast(t('tb.options')+': '+n);
    loadTaobao();
  }catch(e){ toast('⚠ ' + e, false); }
}

async function tbEnrich(){
  if(!confirm(t('tb.checkConfirm'))) return;
  try{
    const d = await fetch('/api/taobao/enrich-request', {method:'POST'}).then(r => r.json());
    toast(d.ok ? '💳 Перевірка запущена — стежте за смугою прогресу' : '⚠ ' + (d.error||'помилка'), !!d.ok);
    loadTaobao();
  }catch(e){ toast('⚠ ' + e, false); }
}

async function tbSaveMin(){
  const v = parseFloat(g('tbMinCny') && g('tbMinCny').value);
  if(isNaN(v)) return;
  try{
    await fetch('/api/settings/save', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({taobao_min_cny: v})});
    toast('✅ Мінімальна ціна ¥' + v + ' — нові лоти нижче не зберігаються');
  }catch(e){ toast('⚠ ' + e, false); }
}

async function tbRequest(){
  if(!confirm(t('tb.collectConfirm'))) return;
  try{
    let d = await fetch('/api/taobao/request',{method:'POST'}).then(r=>r.json());
    if(!d.ok && d.error === 'зарано'){
      if(!confirm(t('tb.collectCooldown').replace('%s', Math.round((d.next_in||0)/60)))) return;
      d = await fetch('/api/taobao/request',{method:'POST',headers:{'Content-Type':'application/json'},
                                            body:JSON.stringify({force:true})}).then(r=>r.json());
    }
    if(d.ok) toast('⏳ ' + (d.message || 'запит надіслано'));
    else toast('⚠ ' + (d.message || d.error || 'помилка'), false);
    loadTaobao();
  }catch(e){ toast('⚠ ' + e, false); }
}

async function loadTaobao(statusOnly){
  const el = g('tbList'); if(!el) return;
  if(!statusOnly) el.innerHTML = '<div class="none">'+t('loading')+'</div>';
  try{
    const d = await fetch('/api/taobao').then(r => r.json());
    tbItems = d.items || [];
    const ci = g('tbCartInfo');
    if(ci){
      const c = d.cart || {};
      if(c.count){
        ci.innerHTML = '🛒 <b>'+t('tb.cart')+': ' + c.count + ' ' + plural(c.count,'lots') + '</b> · ¥' + Number(c.cny || 0).toFixed(2)
          + ' · $' + Number(c.usd || 0).toFixed(2)
          + ' · <span style="color:var(--yw)">' + t('tb.cardWithMiddleman') + ' $' + Number(c.landed || 0).toFixed(2) + '</span>'
          + ' <button class="btn" style="font-size:10px;padding:2px 8px" onclick="tbCartClear()">'+t('tb.clear')+'</button>';
      } else {
        ci.innerHTML = '<span style="color:var(--mu)">🛒 '+t('tb.cartEmpty')+'</span>';
      }
    }
    const ei = g('tbEnrichInfo');
    if(ei){
      const el2 = d.enrich_last || {};
      if(el2.ts){
        const mins = Math.max(0, Math.round((Date.now()/1000 - el2.ts) / 60));
        let tx = (LANG==='ru'?'💳 Проверка оплаты: ':(LANG==='en'?'💳 Payment check: ':'💳 Перевірка оплати: '))
              + (el2.checked || 0) + ' ' + (LANG==='ru'?'лотов сохранено из ':LANG==='en'?'lots saved from ':'лотів збережено з ') + (el2.requested || 0)
              + ' ' + (LANG==='ru'?'проверенных':LANG==='en'?'checked':'перевірених') + ' · ' + mins + ' ' + (LANG==='ru'?'мин назад':LANG==='en'?'min ago':'хв тому');
        if(el2.blocked > 0){
          tx += ' · <span style="color:var(--yw)">' + el2.blocked + (LANG==='ru'?' страниц требовали входа в Taobao':LANG==='en'?' pages required Taobao sign-in':' сторінок вимагали входу в Taobao') + '</span>';
        }
        ei.innerHTML = tx;
      } else {
        ei.innerHTML = '💳 '+t('tb.notChecked');
      }
    }
    if(g('tbMinCny') && d.min_cny != null && document.activeElement !== g('tbMinCny')){
      g('tbMinCny').value = d.min_cny;
    }
    const st = g('tbStatus');
    const agoTxt = d.agent_ago == null ? ''
      : (d.agent_ago < 120 ? ' · ' + d.agent_ago + (LANG==='ru'?' с назад':LANG==='en'?' s ago':' с тому') : ' · ' + Math.round(d.agent_ago/60) + (LANG==='ru'?' мин назад':LANG==='en'?' min ago':' хв тому'));
    const agentTxt = d.agent_online
      ? '<span style="color:var(--gr)">🤖 '+(LANG==='ru'?'онлайн':LANG==='en'?'online':'онлайн') + agoTxt + '</span>'
      : '<span style="color:var(--rd)">🤖 '+(LANG==='ru'?'офлайн':LANG==='en'?'offline':'офлайн') + agoTxt + '</span>';
    if(st) st.innerHTML = (tbItems.length
      ? ((LANG==='ru'?'лотов: ':LANG==='en'?'lots: ':'лотів: ') + tbItems.length + ' · '+(LANG==='ru'?'обновлено ':LANG==='en'?'updated ':'оновлено ') + (d.ts ? Math.round((Date.now()/1000 - d.ts)/60) + (LANG==='ru'?' мин назад':LANG==='en'?' min ago':' хв тому') : '—') + ' · '+(LANG==='ru'?'курс':LANG==='en'?'rate':'курс')+' ¥' + d.usd_cny + '/$')
      : (!GT_PAID
          ? (LANG==='ru'?'автоматизация доступна в платной версии':LANG==='en'?'automation is available in the paid version':'автоматизація доступна в платній версії')
          : (LANG==='ru'?'данных ещё нет — нажмите «Собрать сейчас»':LANG==='en'?'no data yet — press “Collect now”':'даних ще немає — натисніть «Зібрати зараз»')))
      + ' · ' + agentTxt
      + (d.next_in ? ' · '+(LANG==='ru'?'следующий сбор через ':LANG==='en'?'next collection in ':'наступний збір через ') + Math.round(d.next_in/60) + (LANG==='ru'?' мин':LANG==='en'?' min':' хв') : '')
      + ' · '+(LANG==='ru'?'посредник':LANG==='en'?'middleman':'посередник')+' +' + Math.round((d.landed_pct||0)*100) + '%';

    // Смуга прогресу збору
    const pg = d.progress || {};
    const box = g('tbProgress');
    if(box){
      const active = pg.total > 0 && !pg.finished;
      box.style.display = active ? 'block' : 'none';
      if(active){
        const pct = Math.min(100, Math.round((pg.done || 0) / pg.total * 100));
        const pctEl = g('tbProgPct'), bar = g('tbProgBar'), txt = g('tbProgText');
        if(pctEl) pctEl.textContent = pct + '%';
        if(bar) bar.style.width = pct + '%';
        if(txt) txt.textContent = '📥 збір: ' + (pg.done||0) + '/' + pg.total
          + (pg.current ? ' · ' + pg.current : '')
          + (pg.found ? ' · у базі ' + pg.found : '');
      }
    }

    // Поки йде збір — оновлюємо ЛИШЕ статус (без перемальовування списку)
    const pending = (d.request && d.request > (d.last_run || 0)) || (pg.total > 0 && !pg.finished);
    if(pending){
      window._tbWasPending = true;
      clearTimeout(window._tbPoll);
      window._tbPoll = setTimeout(() => { loadTaobao(true); }, 5000);
    }else if(window._tbWasPending){
      window._tbWasPending = false;
      setTimeout(() => loadTaobao(), 300);   // збір завершився — оновлюємо список один раз
    }
    if(statusOnly) return;
    const sel = g('tbGame');
    if(sel){
      const games = [...new Set(tbItems.map(x => x.game).filter(Boolean))].sort();
      const cur = sel.value;
      sel.innerHTML = '<option value="" data-i18n="ta.allGames">Всі ігри</option>' + games.map(x => '<option value="' + esc(x) + '">' + esc(x) + '</option>').join('');
      sel.value = cur || '';
    }
    const sum = g('tbSummary');
    if(sum){
      sum.innerHTML = (d.summary || []).slice(0, 6).map(r => {
        const x = (r.tb_min > 0 && r.sup_min > 0) ? (r.sup_min / r.tb_min) : 0;
        const col = x >= 3 ? 'var(--gr)' : x >= 1.5 ? 'var(--yw)' : 'var(--mu)';
        return '<div style="background:var(--card2);border:1px solid var(--brd);border-radius:10px;padding:9px 12px;min-width:190px">'
          + '<div style="font-size:12px;font-weight:700;margin-bottom:2px">' + esc(r.game) + '</div>'
          + '<div style="font-size:12px;color:var(--mu)">Taobao $' + Number(r.tb_min).toFixed(2) + ' · ' + t('tb.fromSupplier') + ' $' + Number(r.sup_min).toFixed(2) + '</div>'
          + '<div style="font-size:15px;font-weight:800;color:' + col + '">×' + (x ? x.toFixed(1) : '—') + '</div></div>';
      }).join('');
    }
    const runs = (d.runs || []).slice(0, 5);
    if(g('tbRuns')) g('tbRuns').textContent = runs.length
      ? t('tb.lastRuns') + ': ' + runs.map(r => (r.game || r.query) + ' (' + r.found + ')').join(' · ') : '';
    renderTaobao();
  }catch(e){ el.innerHTML = '<div class="al err">⚠ ' + esc(String(e)) + '</div>'; }
}

function tbSegBadge(s){
  const m = {starter: [t('s.starter'), 'var(--a3)'], developed: [t('s.developed'), 'var(--a1)'],
             endgame: [t('s.endgame'), 'var(--yw)'], other: ['—', 'var(--mu)']};
  const v = m[s] || m.other;
  return '<span style="font-size:11px;font-weight:700;color:' + v[1] + '">' + v[0] + '</span>';
}

function renderTaobao(){
  const el = g('tbList'); if(!el) return;
  let list = tbItems.slice();
  if(tbGame) list = list.filter(x => x.game === tbGame);
  if(tbSeg) list = list.filter(x => x.segment === tbSeg);
  if(tbRegion) list = list.filter(x => x.region === tbRegion);
  const q = ((g('tbQ') && g('tbQ').value) || '').toLowerCase().trim();
  if(q) list = list.filter(x => ((x.title_en || '') + ' ' + (x.title_cn || '')).toLowerCase().includes(q));
  if(tbSort === 'card') list = list.filter(x => x.card_pay);
  if(tbSort === 'variant') list = list.filter(x => (x.options || 0) > 1);
  list.sort((a, b) => {
    if(tbSort === 'variant') return (b.options || 0) - (a.options || 0);
    if(tbSort === 'card') return (b.options || 0) - (a.options || 0);
    if(tbSort === 'exp') return (b.price_cny || 0) - (a.price_cny || 0);
    return (a.price_cny || 0) - (b.price_cny || 0);
  });
  if(!list.length){ el.innerHTML = '<div class="none">'+t('sup.none')+'</div>'; return; }
  el.innerHTML = '<table class="sup-table"><thead><tr><th>'+t('tbth.lot')+'</th><th>'+t('tbth.price')+'</th><th>≈USD</th><th>'+t('tbth.withAgent')+'</th><th>'+t('tbth.atSup')+'</th><th>'+t('tbth.diff')+'</th><th>'+t('tb.type')+'</th><th></th></tr></thead><tbody>'
    + list.slice(0, 300).map(x => {
        const sup = x.sup
          ? '<b>$' + Number(x.sup.min).toFixed(2) + '</b><div style="font-size:11px;color:var(--mu)">'+(LANG==='ru'?'медиана':LANG==='en'?'median':'медіана')+' $' + Number(x.sup.median).toFixed(2) + ' · ' + x.sup.n + ' ' + (LANG==='ru'?'лотов':LANG==='en'?'lots':'лотів')+'</div>'
          : '<span style="color:var(--mu)">—</span>';
        let diff = '<span style="color:var(--mu)">—</span>';
        if(x.sup && x.diff_usd != null){
          const good = x.diff_usd > 0;
          diff = '<b style="color:' + (good ? 'var(--gr)' : 'var(--rd)') + '">' + (good ? '×' + (x.diff_x || 0).toFixed(1) : (LANG==='ru'?'дороже':LANG==='en'?'more expensive':'дорожче')) + '</b>'
               + '<div style="font-size:11px;color:' + (good ? 'var(--gr)' : 'var(--rd)') + '">' + (good ? '+' : '') + '$' + Number(x.diff_usd).toFixed(2) + '</div>';
        }
        return '<tr>'
        + '<td style="max-width:380px"><b>' + esc(x.title_en || x.title_cn || '') + '</b>'
        + '<div style="font-size:11px;color:var(--mu)">' + esc(x.title_cn || '') + '</div>'
        + '<div style="font-size:11px;color:var(--mu)">' + esc(x.game || '') + (x.sold ? ' · '+(LANG==='ru'?'продано':LANG==='en'?'sold':'продано')+' ' + esc(x.sold) : '')
        + (x.card_pay ? ' <span title="Оплата карткою" style="color:var(--gr)">💳</span>' : '')
        + ' <button class="btn" style="padding:1px 6px;font-size:10px" title="Позначити/зняти оплату карткою" onclick="tbMark(\'' + esc(x.href) + '\',' + (x.card_pay ? 'false' : 'true') + ')">💳</button>'
        + ' <button class="btn" style="padding:1px 6px;font-size:10px" title="Скільки варіантів у лоті" onclick="tbMarkOpts(\'' + esc(x.href) + '\',' + (x.options || 0) + ')">🎛</button>'
        + ' <button class="btn" style="padding:1px 6px;font-size:10px;' + (x.cart ? 'background:var(--a1);color:#000' : '') + '" title="У кошик покупок" onclick="tbCart(\'' + esc(x.href) + '\',' + (x.cart ? 'false' : 'true') + ')">🛒</button>'
        + ((x.options || 0) > 1 ? ' <span title="Варіантів у лоті" style="color:var(--a3)">🎛 ' + x.options + '</span>' : '')
        + '</div></td>'
        + '<td style="color:var(--gr);font-weight:700">¥' + Number(x.price_cny || 0).toFixed(2) + '</td>'
        + '<td>$' + Number(x.price_usd || 0).toFixed(2) + '</td>'
        + '<td style="color:var(--yw)">$' + Number(x.landed_usd || 0).toFixed(2) + '</td>'
        + '<td>' + sup + '</td>'
        + '<td>' + diff + '</td>'
        + '<td>' + tbSegBadge(x.segment) + '</td>'
        + '<td><a class="ilnk" href="' + esc(x.href) + '" target="_blank" rel="noopener">↗</a></td></tr>';
      }).join('')
    + '</tbody></table>';
}

// 📦 Склад
let invItems = [];

async function loadInventory(){
  const el = g('invList'); if(!el) return;
  el.innerHTML = '<div class="none">'+t('loading')+'</div>';
  try{
    const d = await fetch('/api/inventory').then(r => r.json());
    invItems = d.items || [];
    const card = (k, v, c) => '<div style="background:var(--card2);border:1px solid var(--brd);border-radius:10px;padding:10px 14px;min-width:130px">'
      + '<div style="font-size:11px;color:var(--mu)">' + k + '</div>'
      + '<div style="font-size:18px;font-weight:800;color:' + (c || 'var(--tx)') + '">' + v + '</div></div>';
    const _L = {uk:{a:'На складі',b:'Заморожено',c:'Продано',d:'Витрачено всього'},
                en:{a:'In stock',b:'Frozen',c:'Sold',d:'Total spent'},
                ru:{a:'На складе',b:'Заморожено',c:'Продано',d:'Потрачено всего'}}[LANG] || {a:'In stock',b:'Frozen',c:'Sold',d:'Total spent'};
    if(g('invSummary')) g('invSummary').innerHTML =
      card(_L.a, d.in_stock || 0) +
      card(_L.b, '$' + Number(d.frozen || 0).toFixed(2), 'var(--yw)') +
      card(_L.c, d.sold || 0, 'var(--gr)') +
      card(_L.d, '$' + Number(d.cost_total || 0).toFixed(2));
    if(g('invAging')){
      const ag=d.aging||{};
      const _A={uk:{a:'7+ днів',b:'30+ днів',c:'60+ днів',d:'90+ днів',e:'Частка продажів',f:'Сер. днів продажу'},
                en:{a:'7+ days',b:'30+ days',c:'60+ days',d:'90+ days',e:'Sell-through',f:'Avg days to sell'},
                ru:{a:'7+ дней',b:'30+ дней',c:'60+ дней',d:'90+ дней',e:'Доля продаж',f:'Ср. дней продажи'}}[LANG] || {a:'7+ days',b:'30+ days',c:'60+ days',d:'90+ days',e:'Sell-through',f:'Avg days to sell'};
      const cell=(k,v,c)=>'<div style="background:var(--card2);border:1px solid var(--brd);border-radius:9px;padding:8px 11px;min-width:105px"><div style="font-size:10px;color:var(--mu)">'+k+'</div><div style="font-size:15px;font-weight:800;color:'+(c||'var(--tx)')+'">'+v+'</div></div>';
      g('invAging').innerHTML =
        cell(_A.a, (ag['7']?.count||0)+' · '+locMoney(ag['7']?.value||0), 'var(--yw)') +
        cell(_A.b, (ag['30']?.count||0)+' · '+locMoney(ag['30']?.value||0), 'var(--yw)') +
        cell(_A.c, (ag['60']?.count||0)+' · '+locMoney(ag['60']?.value||0), 'var(--rd)') +
        cell(_A.d, (ag['90']?.count||0)+' · '+locMoney(ag['90']?.value||0), 'var(--rd)') +
        cell(_A.e, Number(d.sell_through||0).toFixed(1)+'%', 'var(--gr)') +
        cell(_A.f, d.avg_sold_days==null?'—':d.avg_sold_days, 'var(--mu)');
    }
    if(g('invOld')){
      if((d.old_count || 0) > 0){
        const _oldTxt = LANG==='ru'?'(куплены 30+ дней назад)':LANG==='en'?'(bought 30+ days ago)':'(куплені 30+ днів тому)';
        g('invOld').innerHTML = '🧊 <b>'+t('inv.dead')+':</b> ' + d.old_count + ' ' + locMoney(d.old_value)
          + ' ' + _oldTxt + ' · ' + t('inv.oldest') + ' ' + (d.oldest_days || 0) + ' ' + (LANG==='ru'?'дней':LANG==='en'?'days':'днів');
      } else {
        g('invOld').innerHTML = '<span style="color:var(--mu)">🧊 '+t('inv.noDead')+'</span>'
          + ((d.oldest_days || 0) ? ' · '+t('inv.oldest')+' ' + d.oldest_days + ' ' + (LANG==='ru'?'дней':LANG==='en'?'days':'днів') : '');
      }
    }
    renderInventory();
  }catch(e){ el.innerHTML = '<div class="al err">⚠ ' + esc(String(e)) + '</div>'; }
}

function renderInventory(){
  const el = g('invList'); if(!el) return;
  const f = (g('invFilter') && g('invFilter').value) || '';
  let list = invItems.slice();
  if(f) list = list.filter(x => x.status === f);
  if(!list.length){ el.innerHTML = '<div class="none">'+t('inv.empty')+'</div>'; return; }
  const badge = s => s === 'sold' ? '<span style="color:var(--gr);font-weight:700">'+t('inv.soldShort')+'</span>'
    : s === 'written_off' ? '<span style="color:var(--rd)">'+t('inv.offShort')+'</span>'
    : '<span style="color:var(--yw);font-weight:700">'+t('inv.inStockShort')+'</span>';
  el.innerHTML = '<div class="bub-wrap">' + list.slice().reverse().map(x => {
    const _ia=(d)=>'<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="'+d+'"/></svg>';
    const acts = (x.status === 'in_stock' ? '<button class="bub-btn" onclick="invSell(\'' + esc(x.id) + '\')" title="'+esc(t('inv.actSell'))+'">'+_ia('M12 3v18M16.5 7.5a3.5 3.5 0 0 0-3.5-3H11a3 3 0 0 0 0 6h2a3 3 0 0 1 0 6h-2a3.5 3.5 0 0 1-3.5-3')+'</button>' : '')
      + (x.status !== 'sold' ? '<button class="bub-btn" onclick="invStatus(\'' + esc(x.id) + '\',\'sold\')" title="'+esc(t('inv.actSold'))+'">'+_ia('M4 12l5 5L20 6')+'</button>' : '')
      + (x.status !== 'in_stock' ? '<button class="bub-btn" onclick="invStatus(\'' + esc(x.id) + '\',\'in_stock\')" title="'+esc(t('inv.actReturn'))+'">'+_ia('M9 14L4 9l5-5M4 9h12a4 4 0 0 1 0 8h-2')+'</button>' : '')
      + '<button class="bub-btn" onclick="invStatus(\'' + esc(x.id) + '\',\'written_off\')" title="'+esc(t('inv.actOff'))+'">'+_ia('M5 5l14 14M19 5L5 19')+'</button>'
      + '<button class="bub-btn del" onclick="invDelete(\'' + esc(x.id) + '\')" title="'+esc(t('inv.actDelete'))+'">'+_ia('M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3')+'</button>';
    return '<div class="bub">'
      + '<div class="bub-head">'
      + '<span class="bub-date">' + esc(fmtDate(x.date)) + '</span>'
      + (x.game ? '<span class="bub-chip">' + esc(x.game) + '</span>' : '')
      + '<span class="bub-title">' + esc(x.title || '') + '</span>'
      + '<div class="bub-acts">' + acts + '</div>'
      + '</div>'
      + '<div class="bub-stats">'
      + '<span class="bs">'+t('inv.costShort')+' <b style="color:var(--gr)">' + locMoney(x.cost) + '</b></span>'
      + '<span class="bs">'+t('inv.status')+' ' + badge(x.status) + '</span>'
      + (x.source ? '<span class="bs">'+t('inv.sourceShort')+' <b>' + esc(x.source) + '</b></span>' : '')
      + (x.has_account ? '<span class="bs">🔑 <b>' + esc(x.account_hint || 'дані') + '</b>'
          + '<button class="bub-btn" style="margin-left:8px" onclick="openInvSecret(\'' + esc(x.id) + '\')">'+t('show')+'</button></span>' : '')
      + '</div></div>';
  }).join('') + '</div>';
}

function lotsCsv(source){
  const m = (g('lotMarkup') && g('lotMarkup').value) || '30';
  window.location = '/api/lots/export?source=' + encodeURIComponent(source)
    + '&markup=' + encodeURIComponent(m) + '&limit=100';
  toast('⬇ CSV лотів (' + source + ', націнка ' + m + '%)');
}

async function invAdd(){
  const title = (g('invTitle').value || '').trim();
  const cost = Number(g('invCost').value) || 0;
  if(!title){ toast(t('inv.enterName'), false); return; }
  try{
    const d = await fetch('/api/inventory/add', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({title, game: g('invGame').value, cost,
        source: g('invSource').value,
        account: (g('invAccount') && g('invAccount').value) || ''})}).then(r => r.json());
    if(!d.ok){ toast('⚠ ' + (d.error || ''), false); return; }
    toast(t('inv.added'));
    g('invTitle').value = ''; g('invCost').value = '0';
    if(g('invGame')) g('invGame').value = '';
    if(g('invSource')) g('invSource').value = '';
    if(g('invAccount')) g('invAccount').value = '';
    loadInventory();
  }catch(e){ toast('⚠ ' + e, false); }
}

function invSell(id){
  const x = (invItems||[]).find(i=>String(i.id)===String(id));
  if(!x){ toast('⚠ ' + t('inv.empty'), false); return; }
  _invSellId = x.id;
  const tab = [...document.querySelectorAll('.tab')].find(el=>String(el.getAttribute('onclick')||'').includes("'tracker'"));
  if(tab) sw('tracker', tab);
  g('plTitle').value = x.title || '';
  g('plBuy').value = Number(x.cost||0).toFixed(2);
  g('plSell').value = '';
  g('plExpenses').value = '0';
  g('plDate').value = todayLocal();
  g('invSellText').textContent = (x.title||'') + ' · $' + Number(x.cost||0).toFixed(2);
  g('invSellBanner').style.display = 'flex';
  plPlatPick(g('plPlatform')?.value || 'zeusx');
  window.scrollTo({top:0,behavior:'smooth'});
  setTimeout(()=>{ try{ g('plSell').focus(); }catch(e){} }, 250);
}
function clearInvSell(){
  _invSellId = null;
  if(g('invSellBanner')) g('invSellBanner').style.display = 'none';
  if(g('plTitle')) g('plTitle').value = '';
  if(g('plBuy')) g('plBuy').value = '';
  if(g('plSell')) g('plSell').value = '';
  if(g('plExpenses')) g('plExpenses').value = '0';
  updateFeePreview();
}
async function markInvSold(id){
  try{
    await fetch('/api/inventory/status',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({id,status:'sold'})});
  }catch(e){}
  _invSellId = null;
  if(g('invSellBanner')) g('invSellBanner').style.display = 'none';
  if(typeof loadInventory === 'function'){ loadInventory().catch(()=>{}); }
}

async function invStatus(id, status){
  try{
    const d = await fetch('/api/inventory/status', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({id, status})}).then(r => r.json());
    if(!d.ok){ toast('⚠ ' + (d.error || ''), false); return; }
    toast(status === 'sold' ? t('inv.soldToast') : (status === 'written_off' ? t('inv.offToast') : t('inv.returnToast')));
    loadInventory();
  }catch(e){ toast('⚠ ' + e, false); }
}

let _invSecret = '';

async function openInvSecret(id){
  try{
    const d = await fetch('/api/inventory/secret?id=' + encodeURIComponent(id)).then(r => r.json());
    if(!d.ok){ toast('⚠ ' + (d.error || ''), false); return; }
    _invSecret = d.account || t('inv.noAccount');
    g('invModalTitle').textContent = (d.game || '') + ' · ' + (d.title || '');
    g('invModalText').textContent = _invSecret;
    g('invModal').style.display = 'flex';
  }catch(e){ toast('⚠ ' + e, false); }
}
function closeInvSecret(){ g('invModal').style.display = 'none'; _invSecret = ''; }
function copyInvSecret(){
  navigator.clipboard.writeText(_invSecret)
    .then(() => toast(t('lot.copied')))
    .catch(() => toast('⚠ Буфер обміну недоступний', false));
}

async function invDelete(id){
  if(!confirm(t('inv.deleteConfirm'))) return;
  try{
    const d = await fetch('/api/inventory/delete', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({id})}).then(r => r.json());
    toast(d.ok ? t('inv.deleted') : '⚠ ' + (d.error || ''), !!d.ok);
    loadInventory();
  }catch(e){ toast('⚠ ' + e, false); }
}

async function loadReport(){
  const box = g('repBox'); if(!box) return;
  const m = (g('repMonth') && g('repMonth').value) || '';
  box.innerHTML = '<div class="none">'+t('rep.calculating')+'</div>';
  try{
    const d = await fetch('/api/report' + (m ? '?month=' + m : '')).then(r => r.json());
    if(!d.ok){ box.innerHTML = '<div class="al err">⚠ ' + esc(d.error || '') + '</div>'; return; }
    if(g('repMonth') && !g('repMonth').value) g('repMonth').value = d.month;
    if(g('repCsv')) g('repCsv').href = '/api/report/export?lang=' + encodeURIComponent(LANG) + (d.month ? '&month=' + d.month : '');
    if(g('repTaxRate') && d.tax) g('repTaxRate').value = d.tax.rate;
    const card = (k, v, c) => '<div style="background:var(--card2);border:1px solid var(--brd);border-radius:10px;padding:10px 14px;min-width:140px">'
      + '<div style="font-size:11px;color:var(--mu)">' + k + '</div>'
      + '<div style="font-size:18px;font-weight:800;color:' + (c || 'var(--tx)') + '">' + v + '</div></div>';
    const s = d.sales || {};
    const sp = Number(s.profit || 0);
    box.innerHTML = '<div style="display:flex;gap:10px;flex-wrap:wrap">'
      + card(t('rep.count'), s.count || 0)
      + card(t('rep.revenue'), '$' + Number(s.revenue || 0).toFixed(2))
      + card(t('rep.fees'), '−$' + Number(s.fees || 0).toFixed(2), 'var(--rd)')
      + card(t('rep.cogs'), '$' + Number(s.cogs || 0).toFixed(2), 'var(--mu)')
      + card(t('rep.profit'), (sp>=0?'+':'') + '$' + sp.toFixed(2), sp >= 0 ? 'var(--gr)' : 'var(--rd)')
      + card(t('rep.purchases'), '$' + Number((d.purchases || {}).cost || 0).toFixed(2), 'var(--yw)')
      + card(t('rep.cash'), (s2 => (s2 >= 0 ? '' : '−') + '$' + Math.abs(s2).toFixed(2))(Number(d.cash || 0)),
             Number(d.cash || 0) >= 0 ? 'var(--gr)' : 'var(--rd)')
      + card(t('rep.stock'), '$' + Number((d.stock || {}).in_stock_value || 0).toFixed(2), 'var(--mu)')
      + '</div>'
      + '<div style="font-size:12px;color:var(--mu);margin-top:10px">'
      + t('rep.formula')
      + '</div>';
  }catch(e){ box.innerHTML = '<div class="al err">⚠ ' + esc(String(e)) + '</div>'; }
}

async function saveTaxRate(){
  try{
    const v=parseFloat(g('repTaxRate')?.value||0);
    const d=await fetch('/api/settings/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tax_rate:Math.max(0,Math.min(50,v))})}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    toast('✅ Податок: '+v+'%');
    loadReport();
  }catch(e){ toast('⚠ '+e, false); }
}

async function reportPdf(){
  const m=(g('repMonth')&&g('repMonth').value)||'';
  try{
    const d=await fetch('/api/report'+(m?'?month='+m:'')).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    const s=d.sales||{};
    const rows=[
      [t('rep.count'), s.count||0],
      [t('rep.revenue'), '$'+Number(s.revenue||0).toFixed(2)],
      [t('rep.fees'), '−$'+Number(s.fees||0).toFixed(2)],
      [t('rep.cogs'), '$'+Number(s.cogs||0).toFixed(2)],
      [t('rep.profit'), (Number(s.profit||0)>=0?'+':'')+'$'+Number(s.profit||0).toFixed(2)],
      [t('rep.purchases'), '$'+Number((d.purchases||{}).cost||0).toFixed(2)],
      [t('rep.cash'), (Number(d.cash||0)>=0?'':'−')+'$'+Math.abs(Number(d.cash||0)).toFixed(2)],
      [t('rep.stock'), '$'+Number((d.stock||{}).in_stock_value||0).toFixed(2)],
    ];
    const w=window.open('','_blank','width=900,height=700');
    if(!w){ toast('⚠ Дозволь спливаючі вікна для PDF', false); return; }
    const html='<!doctype html><html><head><meta charset="utf-8"><title>Ledger — '+esc(d.month||'')+'</title>'+
      '<style>body{font-family:Arial,sans-serif;color:#111;margin:34px}h1{font-size:22px;margin:0 0 4px}'+
      '.sub{color:#666;font-size:12px;margin-bottom:22px}table{width:100%;border-collapse:collapse;margin-top:12px}'+
      'td{border-bottom:1px solid #ddd;padding:9px 6px;font-size:13px}td:last-child{text-align:right;font-weight:700}'+
      '.note{font-size:11px;color:#666;margin-top:20px;line-height:1.5}@media print{button{display:none}}</style></head><body>'+
      '<h1>Ledger — '+esc(d.month||'')+'</h1><div class="sub">'+new Date().toLocaleString()+'</div>'+
      '<table>'+rows.map(r=>'<tr><td>'+esc(r[0])+'</td><td>'+esc(String(r[1]))+'</td></tr>').join('')+'</table>'+
      '<h2 style="font-size:15px;margin:24px 0 6px">'+esc(t('rep.cashTax'))+'</h2><table>'+
        '<tr><td>Hold</td><td>$'+Number((d.cashflow||{}).hold||0).toFixed(2)+'</td></tr>'+
        '<tr><td>Available</td><td>$'+Number((d.cashflow||{}).available||0).toFixed(2)+'</td></tr>'+
        '<tr><td>Withdrawn</td><td>$'+Number((d.cashflow||{}).withdrawn||0).toFixed(2)+'</td></tr>'+
        '<tr><td>'+esc(t('rep.taxBase'))+'</td><td>$'+Number((d.tax||{}).base||0).toFixed(2)+'</td></tr>'+
        '<tr><td>'+esc(t('rep.taxRate'))+'</td><td>'+Number((d.tax||{}).rate||0).toFixed(1)+'%</td></tr>'+
        '<tr><td>'+esc(t('rep.taxEst'))+'</td><td>$'+Number((d.tax||{}).estimate||0).toFixed(2)+'</td></tr>'+
      '</table>'+
      ((d.items&&d.items.length)?('<h2 style="font-size:15px;margin:24px 0 6px">'+esc(t('rep.deals'))+'</h2><table><thead><tr><th style="text-align:left;font-size:11px;color:#666;border-bottom:1px solid #ccc">Дата</th><th style="text-align:left;font-size:11px;color:#666;border-bottom:1px solid #ccc">Назва</th><th style="text-align:left;font-size:11px;color:#666;border-bottom:1px solid #ccc">Майданчик</th><th style="text-align:right;font-size:11px;color:#666;border-bottom:1px solid #ccc">Продаж</th><th style="text-align:right;font-size:11px;color:#666;border-bottom:1px solid #ccc">Комісія</th><th style="text-align:right;font-size:11px;color:#666;border-bottom:1px solid #ccc">Собівартість</th><th style="text-align:right;font-size:11px;color:#666;border-bottom:1px solid #ccc">Прибуток</th></tr></thead><tbody>'+d.items.slice(0,200).map(function(x){return '<tr><td>'+esc(x.date)+'</td><td>'+esc((x.title||'').substring(0,55))+'</td><td>'+esc(x.platform||'')+'</td><td style="text-align:right">$'+Number(x.sell||0).toFixed(2)+'</td><td style="text-align:right">$'+Number(x.fee||0).toFixed(2)+'</td><td style="text-align:right">$'+Number(x.buy||0).toFixed(2)+'</td><td style="text-align:right;font-weight:700">$'+Number(x.profit||0).toFixed(2)+'</td></tr>';}).join('')+'</tbody></table>'+((d.items.length>200)?'<div class="note">Показано перші 200 угод.</div>':'')):'')+
      '<div class="note">'+esc(t('rep.formula'))+'</div>'+
      '<button onclick="window.print()" style="margin-top:20px;padding:9px 14px">Друк / Зберегти PDF</button>'+
      '</body></html>';
    w.document.open(); w.document.write(html); w.document.close();
    setTimeout(()=>{ try{ w.focus(); w.print(); }catch(e){} }, 350);
  }catch(e){ toast('⚠ '+e, false); }
}

async function loadAnalytics(){
  try{
    const d = await fetch('/api/analytics').then(r => r.json());
    const gs = d.games || [], m = d.months || [];
    const total = gs.reduce((a, x) => ({n: a.n + x.n, sell: a.sell + x.sell, profit: a.profit + x.profit}), {n: 0, sell: 0, profit: 0});
    if(g('anSummary')) g('anSummary').innerHTML = [
      [t('rep.count'), total.n], [t('an.revenue'), locMoney(total.sell)], [t('an.profit'), (total.profit>=0?'+':'-')+locMoney(Math.abs(total.profit))],
      [LANG==='ru'?'Мёртвых лотов':LANG==='en'?'Dead lots':'Мертвих лотів', d.dead_total || 0]
    ].map(([k, v]) => '<div style="background:var(--card2);border:1px solid var(--brd);border-radius:10px;padding:10px 14px;min-width:130px">'
        + '<div style="font-size:11px;color:var(--mu)">' + k + '</div><div style="font-size:18px;font-weight:800">' + v + '</div></div>').join('');
    const rows = (arr, keyName) => '<table class="sup-table"><thead><tr><th>' + keyName + '</th><th>'+t('an.dealsCol')+'</th><th>'+t('an.revenueCol')+'</th><th>'+t('an.profitCol')+'</th></tr></thead><tbody>'
      + arr.map(x => '<tr><td><b>' + esc(x.game || x.month) + '</b></td><td>' + x.n + '</td>'
          + '<td>' + locMoney(x.sell) + '</td><td style="color:' + (x.profit >= 0 ? 'var(--gr)' : 'var(--rd)') + ';font-weight:700">' + (x.profit>=0?'+':'-') + locMoney(Math.abs(x.profit)) + '</td></tr>').join('')
      + '</tbody></table>';
    if(g('anGames')) g('anGames').innerHTML = rows(gs.slice(0, 12), t('an.game'));
    if(g('anMonths')) g('anMonths').innerHTML = rows(m.slice(-12).reverse(), LANG==='ru'?'МЕСЯЦ':LANG==='en'?'MONTH':'МІСЯЦЬ');
    if(g('anDead') && (d.dead || []).length){
      g('anDead').innerHTML = '<div style="font-size:12px;color:var(--mu);margin-bottom:6px">🐢 '+(LANG==='ru'?'НЕ ПРОДАВАЛИСЬ 14+ ДНЕЙ':LANG==='en'?'NOT SOLD FOR 14+ DAYS':'НЕ ПРОДАВАЛИСЬ 14+ ДНІВ')+' (' + d.dead_total + ')</div>'
        + '<div style="font-size:12px;color:var(--mu)">' + d.dead.slice(0, 8).map(x => esc(x.title) + ' · $' + x.price + ' · ' + esc(x.sourceName) + ' · ' + x.age + (LANG==='ru'?' дн.':LANG==='en'?' days':' дн.')).join('<br>') + '</div>';
    }
    const st = await fetch('/api/settings').then(r => r.json());
    if(g('stSupHours')) g('stSupHours').value = st.sup_hours || 6;
    if(g('stNewsHours')) g('stNewsHours').value = st.news_hours || 1;
    if(g('stScraperLimit')) g('stScraperLimit').value = st.scraper_limit || 30;
    if(g('stDigestHour') && st.digest_hour != null) g('stDigestHour').value = st.digest_hour;
    if(g('stDealX') && st.deal_x != null) g('stDealX').value = st.deal_x;
    if(g('targetPrices')) g('targetPrices').value = (d.price_targets || []).map(x => x.q + ' | ' + x.max).join('\n');
    ['g2g','gameflip','pa','zeusx','funpay','eldorado','other'].forEach(k=>{
      const el=g('pd_'+k); if(el) el.value=(d.payout_days&&d.payout_days[k]!=null)?d.payout_days[k]:3;
    });
    if(g('targetPrices')){
      g('targetPrices').value = (st.price_targets || []).map(x => x.q + ' | ' + x.max).join('\n');
    }
    if(g('repMonth') && !g('repMonth').value){
      const d0 = new Date(); g('repMonth').value = d0.getFullYear() + '-' + String(d0.getMonth()+1).padStart(2,'0');
    }
    loadReport();
  }catch(e){ toast('⚠ ' + e, false); }
}

async function addTargetFromSup(p){
  if(!p) return;
  const cur=Number(p.price||0);
  const dv=(cur>0?cur*0.9:10).toFixed(2);
  const v=prompt((LANG==='ru'?'Купить '+p.title+' до $':LANG==='en'?'Buy '+p.title+' up to $':'Купити '+p.title+' до $'), dv);
  if(v===null) return;
  const mx=parseFloat(String(v).replace(',','.'));
  if(!Number.isFinite(mx)||mx<=0){ toast('⚠ '+(LANG==='ru'?'Неверная цена':LANG==='en'?'Invalid price':'Некоректна ціна'), false); return; }
  try{
    const st=await fetch('/api/settings').then(r=>r.json());
    const rows=(st.price_targets||[]).filter(x=>String(x.q).toLowerCase()!==String(p.title||'').toLowerCase());
    rows.push({q:String(p.title||'').slice(0,80), max:Math.round(mx*100)/100});
    const r=await fetch('/api/settings/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({price_targets:rows})});
    const d=await r.json().catch(()=>({}));
    if(!r.ok||d.ok===false){ toast('⚠ '+(d.error||('HTTP '+r.status)), false); return; }
    toast('🎯 '+(LANG==='ru'?'Цель добавлена':LANG==='en'?'Target added':'Ціль додано')+': $'+mx.toFixed(2));
  }catch(e){ toast('⚠ '+e, false); }
}

async function savePriceTargets(){
  const rows = String(g('targetPrices')?.value || '').split(/\r?\n/).map(line => {
    const p = line.split('|').map(s => s.trim());
    if (p.length < 2) return null;
    const q = p[0].slice(0,80);
    let mx = parseFloat(String(p[1]).replace(',', '.'));
    if(!q || !Number.isFinite(mx) || mx <= 0) return null;
    return {q, max: Math.round(mx*100)/100};
  }).filter(Boolean);
  try{
    const r = await fetch('/api/settings/save',{method:'POST',headers:{'Content-Type':'application/json'},
      body: JSON.stringify({price_targets: rows})});
    const d = await r.json().catch(()=>({}));
    if(!r.ok || d.ok === false){ toast('⚠ '+(d.error||('HTTP '+r.status)), false); return; }
    toast('🎯 Цілі збережено: '+rows.length);
  }catch(e){ toast('⚠ '+e, false); }
}

async function saveSchedule(){
  const body = {
    sup_hours: Number(g('stSupHours').value) || 6,
    news_hours: Number(g('stNewsHours').value) || 1,
    scraper_limit: Number(g('stScraperLimit').value) || 30,
    digest_hour: Number(g('stDigestHour').value) || 0,
    deal_x: Number(g('stDealX').value) || 5
  };
  try{
    const d = await fetch('/api/settings/save', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)}).then(r => r.json());
    toast(d.ok ? '✅ Збережено' : ('⚠ ' + (d.error || '')), !!d.ok);
  }catch(e){ toast('⚠ ' + e, false); }
}

function calcMarkets(){
  const el = g('mpTable'); if(!el) return;
  const MP_LOCAL={
    uk:{funpay:['FunPay','залежить від розділу; для акаунтів зазвичай 10%'],ggsel:['GGsel',''],own:['Своя вітрина',''],z2u:['Z2U',''],g2g:['G2G','8% комісія продавця + виплата'],gameflip:['Gameflip','10% комісія продавця; можливі платіжні збори'],eldorado:['Eldorado','10% для акаунтів; окремі ігри 15–30%'],zeusx:['ZeusX','5–10% залежно від рангу продавця'],pa:['PlayerAuctions',''],tg:['Telegram (прямо)','']},
    en:{funpay:['FunPay','depends on section; usually 10% for accounts'],ggsel:['GGsel',''],own:['Own storefront',''],z2u:['Z2U',''],g2g:['G2G','8% seller fee + payout'],gameflip:['Gameflip','10% seller fee; payment fees may apply'],eldorado:['Eldorado','10% for accounts; some games 15–30%'],zeusx:['ZeusX','5–10% depending on seller tier'],pa:['PlayerAuctions',''],tg:['Telegram (direct)','']},
    ru:{funpay:['FunPay','зависит от раздела; для аккаунтов обычно 10%'],ggsel:['GGsel',''],own:['Свой магазин',''],z2u:['Z2U',''],g2g:['G2G','8% комиссия продавца + выплата'],gameflip:['Gameflip','10% комиссия продавца; возможны платёжные сборы'],eldorado:['Eldorado','10% для аккаунтов; отдельные игры 15–30%'],zeusx:['ZeusX','5–10% в зависимости от ранга продавца'],pa:['PlayerAuctions',''],tg:['Telegram (напрямую)','']}
  };
  const MPN=MP_LOCAL[LANG]||MP_LOCAL.en;
  const price = Number(g('mpPrice') && g('mpPrice').value) || 0;
  const cost  = Number(g('mpCost')  && g('mpCost').value)  || 0;
  const list = (FEE_CFG.marketplaces || []).map(m => {
    const total = (m.fee||0) + (m.payout||0);
    const net = price * (1 - total);
    const profit = net - cost;
    const margin = price > 0 ? (profit / price) * 100 : 0;
    return Object.assign({}, m, {net, profit, margin});
  }).sort((a,b) => b.net - a.net);
  const best = list.length && list[0].net > 0 ? list[0].id : null;
  el.innerHTML = '<table class="sup-table"><thead><tr><th>'+t('mp.marketplace')+'</th><th>'+t('mp.fee')+'</th><th>'+t('mp.net')+'</th><th>'+t('mp.profit')+'</th><th>'+t('mp.margin')+'</th></tr></thead><tbody>'
    + list.map(m => { const loc=MPN[m.id]||[m.name,m.note||'']; return '<tr' + (m.id===best?' style="background:rgba(34,197,94,.07)"':'') + '>'
        + '<td><b>' + m.emoji + ' ' + esc(loc[0]) + '</b>' + (loc[1]? '<div style="font-size:11px;color:var(--mu)">' + esc(loc[1]) + '</div>' : '') + '</td>'
        + '<td>' + ((m.fee||0)*100).toFixed(1) + '%' + (m.payout? ' + ' + (m.payout*100).toFixed(1) + '%' : '') + '</td>'
        + '<td style="color:var(--gr);font-weight:700">$' + m.net.toFixed(2) + '</td>'
        + '<td style="color:' + (m.profit>=0?'var(--gr)':'var(--rd)') + ';font-weight:700">' + (m.profit>=0?'+':'') + '$' + m.profit.toFixed(2) + '</td>'
        + '<td>' + m.margin.toFixed(1) + '%</td></tr>'; }).join('')
    + '</tbody></table>';
}

async function loadMailQueue(force){
  mailCookieHint();
  const el=g('mailList'); if(!el) return;
  try{
    const d=await fetch('/api/mail/queue' + (force?'?t='+Date.now():'')).then(r=>r.json());
    if(!d.ok) throw new Error('HTTP');
    mailItems=d.items||[];
    renderMailQueue();
    const badge=g('mailBadge'), n=d.new||0;
    const first=_lastMailNew===null;
    if(!first && n>_lastMailNew && !document.querySelector('#tab-mail.on')) notifyNewOrder(n);
    if(n===0) clearOrderAlert();
    _lastMailNew=n;
    if(badge) badge.innerHTML = n ? ` <span style="background:var(--a2);color:#1a0a05;border-radius:20px;padding:0 7px;font-size:11px;font-weight:800">${n}</span>` : '';
    if(g('mailStat')) g('mailStat').textContent = mailItems.length ? `${mailItems.length} ${plural(mailItems.length,'emails')} · ${LANG==='ru'?'новых':LANG==='en'?'new':'нових'} ${n}` : '';
  }catch(e){ el.innerHTML='<div class="none">⚠ '+esc(String(e))+'</div>'; }
}

async function saveVault(){
  const on = !!(g('vaultEnabled') && g('vaultEnabled').checked);
  try{
    const d = await fetch('/api/settings/save',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({vault_enabled:on})}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    toast(on ? t('vault.on') : t('vault.off'));
    setTimeout(()=>{ try{ loadInventory(); }catch(e){} }, 400);
  }catch(e){ toast('⚠ '+e, false); }
}
async function saveAutoAddOrders(){
  if(!GT_PAID){ toast(t('plus.needKey'), false); try{ if(g('autoAddOrders')) g('autoAddOrders').checked=false; }catch(e){} return; }
  const on = !!(g('autoAddOrders') && g('autoAddOrders').checked);
  try{
    await fetch('/api/settings/save',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({auto_add_orders:on})});
    toast(on ? t('order.autoOn') : t('order.autoOff'));
  }catch(e){ toast('⚠ '+e, false); }
}
async function createDemoOrder(){
  try{
    _ensureAudio();
    playOrderSound();
    if('Notification' in window && Notification.permission==='default'){
      try{ Notification.requestPermission().then(updateOrderNotifyUI).catch(()=>{}); }catch(e){}
    }
    const d=await fetch('/api/mail/demo',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({lang:LANG})}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||''), false); return; }
    await loadMailQueue(true);
    notifyNewOrder(1);
    toast('🧪 '+t('order.demoCreated'));
  }catch(e){ toast('⚠ '+e, false); }
}
async function mailCookieHint(){
  const box = g('mailHint'); if(!box) return;
  try{
    const st = await fetch('/api/secrets/status').then(r => r.json());
    box.innerHTML = st.funpay_cookie ? '' :
      '<div class="al warn" style="margin-bottom:12px">⚠ <b>FunPay:</b> ' + (LANG==='uk'?'cookie не задано — замовлення з FunPay сюди не надходять.':(LANG==='ru'?'cookie не задан — заказы с FunPay сюда не поступают.':'cookie is not set — FunPay orders do not arrive here.')) + ' <button class="btn" style="font-size:11px;padding:3px 9px" '
      + 'onclick="openCookiePanel()">' + (LANG==='uk'?'Вставити cookie':(LANG==='ru'?'Вставить cookie':'Paste cookie')) + '</button></div>';
  }catch(e){}
}

function renderMailQueue(){
  const el=g('mailList'); if(!el) return;
  if(!mailItems.length){
    el.innerHTML='<div class="none">'+t('mail.empty')+'</div>';
    return;
  }
  const order=mailItems.slice().reverse();
  el.innerHTML = order.map(m=>{
    const isOrder=m.kind==='order';
    const clr={'ZeusX':'var(--a1)','FunPay':'var(--a3)','Eldorado':'var(--yw)'}[m.platform]||'var(--mu)';
    const bits=[];
    if(m.orderId) bits.push('🆔 '+esc(m.orderId));
    if(m.price!=null) bits.push('💵 $'+Number(m.price).toFixed(2));
    if(m.game) bits.push('🎮 '+esc(m.game));
    if(m.category) bits.push('📁 '+esc(m.category));
    const when=m.ts ? new Date(m.ts*1000).toLocaleString(dateLocale()) : '';
    const status = (m.status==='added' || m.status==='auto_added')
      ? `<span style="color:var(--gr);font-size:12px;font-weight:700">${m.status==='auto_added'?'🤖 ':'✓ '}${LANG==='ru'?'добавлено в':LANG==='en'?'added to':'додано в'} ${esc(m.added_to||'')}</span>`
      : m.status==='ignored'
        ? '<span style="color:var(--mu);font-size:12px">✕ '+(LANG==='ru'?'проигнорировано':LANG==='en'?'ignored':'проігноровано')+'</span>' : '';
    const canAdd = m.status !== 'added' && m.status !== 'auto_added';
    const plat = m.platform || '';
    const canEd = canAdd && plat === 'Eldorado';
    const canPl = canAdd && plat !== 'Eldorado';
    return `<div style="background:var(--card2);border:1px solid var(--brd);border-radius:12px;padding:14px;margin-bottom:10px">
      <div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;flex-wrap:wrap">
        <div style="flex:1;min-width:240px">
          <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:7px">
            <span style="font-size:12px;font-weight:700;color:${clr};background:${clr}18;border:1px solid ${clr}38;padding:2px 8px;border-radius:6px">${esc(m.platform||'')}</span>
            <span style="font-size:13px;font-weight:700">${isOrder?(LANG==='ru'?'💰 заказ':LANG==='en'?'💰 order':'💰 замовлення'):(LANG==='ru'?'💬 сообщение':LANG==='en'?'💬 message':'💬 повідомлення')}</span>
            <span style="font-size:12px;color:var(--mu)">${when}</span>
          </div>
          <div style="font-weight:700;font-size:14px;margin-bottom:5px">${esc(m.subject||(LANG==='ru'?'(без темы)':LANG==='en'?'(no subject)':'(без теми)'))}</div>
          ${bits.length?`<div style="font-size:13px;margin-bottom:6px">${bits.join(' · ')}</div>`:''}
          <div style="font-size:12px;color:var(--mu);white-space:pre-wrap;max-height:76px;overflow:hidden">${esc((m.body||'').substring(0,240))}</div>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
          ${status}
          ${canEd?`<button class="btn gr" onclick="mailAct('${esc(m.id)}','add_ed')">➕ ELDORADO</button>`:''}
          ${canPl?`<button class="btn" onclick="mailAct('${esc(m.id)}','add_pl')">➕ P&amp;L</button>`:''}
          ${isOrder?`<button class="btn" onclick="openReplyGenerator('${esc(m.id)}')">💬 ${LANG==='ru'?'Ответ':LANG==='en'?'Reply':'Відповідь'}</button>`:''}
          ${isOrder?`<button class="btn" onclick="mailDraft('${esc(m.id)}')">📝 ${LANG==='ru'?'Черновик':LANG==='en'?'Draft':'Чернетка'}</button>`:''}
          ${m.status==='new'?`<button class="btn" onclick="mailAct('${esc(m.id)}','ignore')">✕</button>`:''}
          <button class="btn rd" onclick="mailAct('${esc(m.id)}','remove')">🗑</button>
        </div>
      </div>
    </div>`;
  }).join('');
}

async function clearMailQueue(){
  if(!confirm(t('mail.clearConfirm'))) return;
  try{
    const d = await fetch('/api/mail/clear',{method:'POST'}).then(r=>r.json());
    toast(d.ok ? (t('mail.cleared')+' '+(d.removed||0)) : ('⚠ '+(d.error||'')), !!d.ok);
    loadMailQueue();
  }catch(e){ toast(String(e), false); }
}

async function mailDraft(id){
  const item=(mailItems||[]).find(x=>x.id===id);
  if(!item){ toast('⚠ замовлення не знайдено', false); return; }
  window._mailDraftId=id;
  const platTxt=String(item.platform||'').toLowerCase();
  const plat=platTxt.includes('zeus')?'zeusx':platTxt.includes('fun')?'funpay':platTxt.includes('eldorado')?'eldorado':'other';
  const tab=[...document.querySelectorAll('.tabs .tab')].find(x=>String(x.getAttribute('onclick')||'').includes("'tracker'"));
  if(tab) sw('tracker',tab);
  plPlatPick(plat);
  g('plTitle').value=(item.subject||item.game||'').trim();
  g('plSell').value=item.price!=null?String(item.price):'';
  g('plDate').value=todayLocal();
  g('plExpenses').value='0';
  g('plCur').value=_cur;
  g('plFx').value=(_cur==='USD'?1:(_rate||''));
  if(item.game) g('plTitle').value=String(item.game)+' · '+g('plTitle').value;
  try{
    const q=encodeURIComponent(((item.subject||'')+' '+(item.game||'')).trim());
    if(q){
      const mm=await fetch('/api/inventory/match?title='+q).then(r=>r.json());
      const match=(mm.matches||[])[0];
      if(match){
        _invSellId=match.id;
        g('plBuy').value=Number(match.cost||0).toFixed(2);
        g('invSellText').textContent=match.title+' · '+Number(match.cost||0).toFixed(2);
        g('invSellBanner').style.display='flex';
      }
    }
  }catch(e){}
  updateFeePreview();
  toast(LANG==='ru'?'📝 Черновик создан — проверь и сохрани':LANG==='en'?'📝 Draft created — review and save':'📝 Чернетку створено — перевір і збережи');
}
let _replyItemId=null, _replyRound=0, _replyCache={};
function _replyHash(s){ let h=0; for(let i=0;i<String(s).length;i++){ h=(h*31+String(s).charCodeAt(i))|0; } return Math.abs(h); }
function _replyData(item){
  const title=String(item.subject||item.game||'').trim() || (LANG==='ru'?'ваш заказ':LANG==='en'?'your order':'ваше замовлення');
  const platform=String(item.platform||'').trim() || 'marketplace';
  const h=_replyHash(String(item.id||'')+title+platform);
  const pick=a=>a[(h+_replyRound)%a.length];
  const fill=s=>s.replace('{title}',title);
  return {
    uk: fill(pick([
      'Добрий день! Дякую за замовлення «{title}». Замовлення прийнято в роботу. Найближчим часом підготую акаунт і надішлю дані для входу. Якщо потрібна допомога — напишіть у цей чат.',
      'Привіт! Замовлення «{title}» прийнято. Вже займаюся підготовкою — дані для входу надішлю сюди найближчим часом.',
      'Вітаю! Ваше замовлення «{title}» вже в обробці. Я підготую все найближчим часом і надішлю дані сюди. Дякую за покупку!',
      'Дякую за замовлення «{title}»! Все прийнято. Очікуйте, будь ласка, повідомлення з даними для входу. Якщо виникнуть питання — я на зв’язку.',
      'Вітаю! Почав підготовку замовлення «{title}». Щойно все буде готово — надішлю дані для входу. Дякую за очікування!',
      'Добрий день! «{title}» в роботі. Намагаюся підготувати якнайшвидше; дані для входу прийдуть у цей чат.',
      'Дякую за покупку «{title}»! Замовлення підтверджено. Будь ласка, зачекайте трохи — скоро надішлю всі дані для входу.',
      'Привіт! Все гаразд, замовлення «{title}» прийнято. Вже готую акаунт; якщо є побажання — напишіть, врахую.',
      'Ваше замовлення «{title}» в черзі на підготовку. Я повідомлю вас тут, щойно з’являться дані для входу. Дякую!',
      'Добрий день! Дякую за «{title}». Замовлення прийнято; найближчим часом надішлю логін і пароль. Гарного дня!'
    ])),
    en: fill(pick([
      'Hi! Thanks for ordering "{title}". Your order is now in progress. I’ll prepare the account and send the login details shortly. If you need anything, just reply here.',
      'Hello! Your order for "{title}" is being processed. I’ll send the account details here as soon as it’s ready. Thanks for your purchase!',
      'Thank you for your order "{title}"! It’s confirmed and in progress. Please wait for the login details — I’ll message you here shortly.',
      'Hi! I’ve started preparing "{title}". I’ll send the login details here as soon as everything is ready. Thanks for your patience!',
      'Hello! Your order "{title}" is in the queue. I’ll message you here with the account details shortly.',
      'Thanks for buying "{title}"! The order is confirmed. Please give me a little time — I’ll send the login details soon.',
      'Hi! Everything is fine — "{title}" is accepted and being prepared. If you have any preferences, just let me know.',
      'Your order "{title}" is being prepared. I’ll update you here as soon as the login details are ready. Thank you!',
      'Hello! Thank you for "{title}". The order is accepted; I’ll send the login and password shortly. Have a great day!',
      'Hi! Just confirming: "{title}" is in progress. I’ll send the account details here as soon as it’s ready.'
    ])),
    ru: fill(pick([
      'Здравствуйте! Спасибо за заказ «{title}». Заказ принят в работу. Скоро подготовлю аккаунт и отправлю данные для входа. Если нужна помощь — напишите в этот чат.',
      'Привет! Заказ «{title}» принят. Уже занимаюсь подготовкой — данные для входа пришлю сюда в ближайшее время.',
      'Здравствуйте! Ваш заказ «{title}» уже в обработке. Я всё подготовлю в ближайшее время и пришлю данные сюда. Спасибо за покупку!',
      'Спасибо за заказ «{title}»! Всё принято. Пожалуйста, ожидайте сообщение с данными для входа. Если появятся вопросы — я на связи.',
      'Здравствуйте! Начал подготовку заказа «{title}». Как только всё будет готово — пришлю данные для входа. Спасибо за ожидание!',
      'Добрый день! «{title}» в работе. Стараюсь подготовить как можно быстрее; данные для входа придут в этот чат.',
      'Спасибо за покупку «{title}»! Заказ подтверждён. Пожалуйста, подождите немного — скоро пришлю все данные для входа.',
      'Привет! Всё в порядке, заказ «{title}» принят. Уже готовлю аккаунт; если есть пожелания — напишите, учту.',
      'Ваш заказ «{title}» в очереди на подготовку. Я сообщу здесь, как только появятся данные для входа. Спасибо!',
      'Добрый день! Спасибо за «{title}». Заказ принят; в ближайшее время пришлю логин и пароль. Хорошего дня!'
    ]))
  };
}
function openReplyGenerator(id){
  const item=(mailItems||[]).find(x=>x.id===id);
  if(!item){ toast('⚠ '+t('reply.notFound'), false); return; }
  _replyItemId=id; _replyRound=0;
  const modal=g('replyModal'); if(modal) modal.style.display='flex';
  renderReplyGenerator();
}
function renderReplyGenerator(){
  const item=(mailItems||[]).find(x=>x.id===_replyItemId); if(!item) return;
  _replyCache=_replyData(item);
  const title=g('replyTitle'), hint=g('replyHint'), body=g('replyBody'), regen=g('replyRegen');
  if(title) title.textContent='💬 '+t('reply.title');
  if(hint) hint.textContent=t('reply.hint');
  if(regen) regen.textContent='↻ '+t('reply.regen');
  if(!body) return;
  const langs=[['uk','УКРАЇНСЬКА'],['en','ENGLISH'],['ru','РУССКИЙ']];
  body.innerHTML=langs.map(([code,label])=>'<div style="background:var(--card2);border:1px solid var(--brd);border-radius:10px;padding:10px">'+
    '<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:7px"><b style="font-size:11px;letter-spacing:.08em;color:var(--mu)">'+label+'</b>'+
    '<button class="btn gr" style="font-size:10px;padding:3px 9px" onclick="copyReply(\''+code+'\',this)">📋 '+esc(t('reply.copy'))+'</button></div>'+
    '<div style="font-size:12px;line-height:1.55;white-space:pre-wrap">'+esc(_replyCache[code])+'</div></div>').join('');
}
function regenReply(){ _replyRound++; renderReplyGenerator(); }
function closeReplyGenerator(){ const m=g('replyModal'); if(m) m.style.display='none'; }
async function copyReply(code,btn){
  const txt=_replyCache[code]||'';
  try{ await navigator.clipboard.writeText(txt); toast('📋 '+t('reply.copied')); }
  catch(e){
    const ta=document.createElement('textarea'); ta.value=txt; document.body.appendChild(ta); ta.select();
    try{ document.execCommand('copy'); toast('📋 '+t('reply.copied')); }catch(_){ toast('⚠ '+t('reply.copyFail'), false); }
    ta.remove();
  }
}
async function finishMailDraft(){
  const id=window._mailDraftId;
  if(!id) return;
  window._mailDraftId=null;
  try{ await fetch('/api/mail/action',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({id,action:'remove'})}); }catch(e){}
  try{ loadMailQueue(); }catch(e){}
}
async function mailAct(id, action){
  try{
    let buy = 0, match = null, amount = null, game = '';
    if(action==='add_pl' || action==='add_ed'){
      const item = (mailItems || []).find(x => x.id === id) || {};
      if(item.price == null || Number(item.price) <= 0){
        const pv = prompt(t('mail.amountPrompt'), '');
        if(pv === null) return;
        amount = Math.max(0, parseFloat(String(pv).replace(',', '.')) || 0);
        if(amount <= 0){ toast(t('mail.amountPositive'), false); return; }
      }
      try{
        const q = encodeURIComponent(((item.subject || '') + ' ' + (item.game || '')).trim());
        if(q){
          const mm = await fetch('/api/inventory/match?title=' + q).then(r => r.json());
          match = (mm.matches || [])[0] || null;
        }
      }catch(e){}
      game = (item.game || '').trim();
      if(!game || game === 'Other'){
        const gv = prompt(t('mail.gamePrompt'), '');
        if(gv === null) return;
        game = gv.trim();
      }
      const msg = match
        ? t('mail.inStock').replace('%s', match.title).replace('%s', Number(match.cost).toFixed(2))
        : t('mail.costPrompt');
      const v = prompt(msg, match ? String(match.cost) : '0');
      if(v === null) return;
      buy = Math.max(0, parseFloat(String(v).replace(',', '.')) || 0);
    }
    const d=await fetch('/api/mail/action',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({id, action, buy, price: amount, game: (game||'')})}).then(r=>r.json());
    if(!d.ok){ toast('⚠ '+(d.error||'помилка'), false); return; }
    if(action==='add_ed' || action==='add_pl'){
      toast(t('mail.added')+' '+(action==='add_ed'?'ELDORADO':'P&L') + (match ? ' '+t('mail.fromStock') : ''));
      if(match){
        try{
          await fetch('/api/inventory/status', {method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({id: match.id, status: 'sold', sale_id: id})});
        }catch(e){}
      }
      try{
        if(action==='add_ed'){
          const r=await fetch('/api/eldorado').then(x=>x.json());
          edSales = Array.isArray(r.sales)?r.sales:[]; edLoaded=true;
          try{ localStorage.setItem('eldorado_sales', JSON.stringify(edSales)); }catch(e){}
          renderEldorado();
        } else {
          const r=await fetch('/api/pl').then(x=>x.json());
          purchases = Array.isArray(r.purchases)?r.purchases:[];
          renderPurchases(); renderRevenueChart();
        }
      }catch(e){}
    } else if(action==='ignore'){ toast(t('mail.ignored')); }
    else { toast(t('mail.removed')); }
    loadMailQueue(true);
  }catch(e){ toast('⚠ '+e, false); }
}
document.addEventListener('keydown', e=>{ if(e.key==='Escape'){ closeCmp(); closeHist(); } });

// ═══════════════════════════════════════════════
// 💰 КАЛЬКУЛЯТОР ЦІНИ (тільки розрахунок, без API)
// ═══════════════════════════════════════════════
// PLATFORM_FEES (майданчик + вивід) визначено у блоці STATE з конфігу Python
let _lotPlatform = 'zeusx';
let _lotSupplierUrl = '';

function openLotModal(p){
  const item = p || {};
  _lotSupplierUrl = item.url || '';
  _lotPlatform = 'zeusx';
  g('lmBtnZX').classList.add('on'); g('lmBtnFP').classList.remove('on');
  g('lmTitle').value = item.title || '';
  g('lmGame').value = item.sourceName || '';
  g('lmBuyPrice').value = parseFloat(item.price || 0).toFixed(2);
  g('lmMarkup').value = '30';
  g('lmDesc').value = item.title || '';
  calcLotPrice();
  g('lmResult').textContent = '';
  g('lotModal').style.display = 'flex';
}

function closeLotModal(){ g('lotModal').style.display='none'; }

function setLotPlatform(p){
  _lotPlatform = p;
  g('lmBtnZX').classList.toggle('on', p==='zeusx');
  g('lmBtnFP').classList.toggle('on', p==='funpay');
  calcLotPrice();
}

function calcLotPrice(){
  const buy = parseFloat(g('lmBuyPrice').value)||0;
  const markup = parseFloat(g('lmMarkup').value)||0;
  const sell = buy*(1+markup/100);
  g('lmSellPrice').value = sell.toFixed(2);
  if(buy>0){
    const fee = PLATFORM_FEES[_lotPlatform]||0;
    const afterFee = sell*(1-fee);
    const profit = afterFee-buy;
    g('lmSummary').style.display='block';
    g('lmProfit').textContent=(profit>=0?'+':'')+profit.toFixed(2)+'$';
    g('lmProfit').style.color=profit>=0?'var(--gr)':'var(--rd)';
    g('lmAfterFee').textContent=afterFee.toFixed(2)+'$';
  } else {
    g('lmSummary').style.display='none';
  }
}

function copyLotLink(){
  const title=g('lmTitle').value.trim();
  const sell=parseFloat(g('lmSellPrice').value)||0;
  const game=g('lmGame').value.trim();
  const desc=g('lmDesc').value.trim();
  if(!title){ g('lmResult').innerHTML='<span style="color:var(--rd)">⚠️ '+t('lot.enterName')+'</span>'; return; }
  const priceWord = LANG==='ru'?'Цена':LANG==='en'?'Price':'Ціна';
  const srcWord = LANG==='ru'?'Источник':LANG==='en'?'Source':'Джерело';
  const text=title+(game?' ['+game+']':'')+'\n'+priceWord+': $'+sell.toFixed(2)
    +(desc?'\n\n'+desc:'')+(_lotSupplierUrl?'\n\n'+srcWord+': '+_lotSupplierUrl:'');
  navigator.clipboard.writeText(text)
    .then(()=>{ toast(t('lot.copied')); g('lmResult').textContent=''; })
    .catch(()=>{ g('lmResult').innerHTML='<span style="color:var(--rd)">❌ '+t('lot.clipboard')+'</span>'; });
}

g('lotModal').addEventListener('click', e=>{ if(e.target===g('lotModal')) closeLotModal(); });

;(async()=>{
  // Завантажуємо P&L з сервера (синхронізується між пристроями)
  let serverOk = false, plBroken = false;
  try{
    const r = await fetch('/api/pl');
    const plResp = await r.json();
    if(!r.ok || plResp.ok === false){
      // файл пошкоджено / не читається — НЕ перезаписуємо його і не сіємо демо
      plBroken = true;
      purchases = [];
      toast('⚠ P&L не прочитано: '+(plResp.error||('HTTP '+r.status)), false);
    } else {
      purchases = Array.isArray(plResp.purchases) ? plResp.purchases : [];
      serverOk = true;
    }
  }catch(e){
    // сервер недоступний — працюємо з локальною копією, нічого не перезаписуємо
    purchases = safeParse(localStorage.getItem(PKEY)||'[]', []);
    toast('⚠ Сервер недоступний — показано локальну копію', false);
  }
  // Міграція: сервер порожній, але в браузері є записи → переносимо їх.
  // Демо-дані (IMPORTED_DATA) більше не підставляються ніколи.
  // Сервер — єдине джерело істини. Дані з браузера на сервер НЕ переносимо,
  // інакше старі тестові записи з localStorage повертаються в чистий застосунок.
  try{ localStorage.removeItem(PKEY); }catch(e){}
  loadTheme();
  applyFs();
  applyLang();
  renderOverview();
  // перший запуск: вікно мови показуємо лише якщо на сервері ще не обрано
  loadSettings().then(()=>{ if(!_onboarded) setTimeout(onbOpen, 250); });
  try{
    new MutationObserver(translateAll).observe(document.body, {childList:true, subtree:true});
    translateAll();
  }catch(e){}
  renderPurchases();
  setTimeout(renderRevenueChart, 300);
  loadEldorado();   // серверні продажі ELDORADO + міграція з localStorage
  loadSettings();   // курс, Telegram, хмара + зведена статистика
  loadMailQueue();  // бейдж нових замовлень у вкладці
  loadSupStatus();
  setInterval(loadSupStatus, 60000);
  setInterval(()=>{ try{ loadMailQueue(); }catch(e){} }, 45000);
  try{ updateOrderNotifyUI(); }catch(e){}

  // PWA: встановлення застосунку
  let _pwaPrompt=null;
  window.addEventListener('beforeinstallprompt', e=>{
    e.preventDefault(); _pwaPrompt=e; window.__pwaEarly=e;
    const s=g('pwaStatus'); if(s) s.textContent='✅ '+(LANG==='ru'?'Готово к установке':LANG==='en'?'Ready to install':'Готово до встановлення');
  });
  window.addEventListener('appinstalled', ()=>{
    _pwaPrompt=null; window.__pwaEarly=null;
    const s=g('pwaStatus'); if(s) s.textContent='✅ '+(LANG==='ru'?'Установлено':LANG==='en'?'Installed':'Встановлено');
  });
  function pwaInstall(){
    if(window.matchMedia('(display-mode: standalone)').matches){
      toast(LANG==='ru'?'Уже открыто как приложение':LANG==='en'?'Already running as an app':'Вже відкрито як застосунок'); return;
    }
    if(!window.isSecureContext){
      const _h=location.hostname;
      const secure=(_h==='70-34-243-50.sslip.io'||/^[0-9.]+$/.test(_h))?'https://ledger.70-34-243-50.sslip.io/':('https://'+_h+'/');
      const s=g('pwaStatus');
      if(s) s.textContent=LANG==='ru'?'🔒 Нужен HTTPS — открываю защищённую версию…':LANG==='en'?'🔒 HTTPS required — opening the secure version…':'🔒 Потрібен HTTPS — відкриваю захищену версію…';
      if(confirm(LANG==='ru'?'Установка приложения работает только по HTTPS. Открыть защищённую версию?':LANG==='en'?'App installation only works over HTTPS. Open the secure version?':'Встановлення застосунку працює лише через HTTPS. Відкрити захищену версію?')){
        location.href=secure;
      }
      return;
    }
    const ua=navigator.userAgent||'';
    const isOpera=/OPR\/|Opera/i.test(ua);
    if(isOpera){ openPwaHelp('opera'); return; }
    const _pp=_pwaPrompt||window.__pwaEarly;
    if(_pp){
      try{
        _pp.prompt();
        _pp.userChoice.then(c=>{
          if(c && c.outcome==='accepted') toast('✅ '+(LANG==='ru'?'Установлено':LANG==='en'?'Installed':'Встановлено'));
          _pwaPrompt=null; window.__pwaEarly=null;
        }).catch(()=>{ openPwaHelp('manual'); });
      }catch(e){ openPwaHelp('manual'); }
      return;
    }
    const ios=/iphone|ipad|ipod/i.test(ua);
    openPwaHelp(ios?'ios':'manual');
  }
  function closePwaHelp(){
    const m=g('pwaHelpModal');
    if(m){ m.style.display='none'; m.setAttribute('aria-hidden','true'); }
  }
  window.closePwaHelp=closePwaHelp;
  window.pwaCopyLink=pwaCopyLink;
  window.pwaDownloadShortcut=pwaDownloadShortcut;
  document.addEventListener('keydown',function(e){ if(e.key==='Escape'){ try{ closePwaHelp(); }catch(_){} } });
  function pwaCopyLink(){
    const u=location.origin+'/';
    (navigator.clipboard?navigator.clipboard.writeText(u):Promise.reject()).then(()=>toast('📋 '+(LANG==='ru'?'Ссылка скопирована':LANG==='en'?'Link copied':'Посилання скопійовано'))).catch(()=>{ prompt('URL',u); });
  }
  function pwaDownloadShortcut(){
    const u=location.origin+'/';
    const ico=location.origin+'/app-icon-192.png';
    const body='[InternetShortcut]\r\nURL='+u+'\r\nIconFile='+ico+'\r\n';
    const a=document.createElement('a');
    a.href=URL.createObjectURL(new Blob([body],{type:'application/internet-shortcut'}));
    a.download='Ledger.url'; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(()=>URL.revokeObjectURL(a.href),1000);
  }
  function openPwaHelp(reason){
    const m=g('pwaHelpModal'); if(!m) return;
    const ru=LANG==='ru', en=LANG==='en';
    const title=g('pwaHelpTitle'), body=g('pwaHelpBody');
    const short=reason==='opera'?(ru?'Opera на компьютере не поддерживает установку PWA. Открой эту же ссылку в Chrome или Edge — там кнопка работает. На Android в Opera: меню → «Добавить на главный экран».':en?'Opera on desktop does not support PWA installation. Open this link in Chrome or Edge — the button works there. On Opera Android: menu → “Add to Home screen”.':'Opera на комп’ютері не підтримує встановлення PWA. Відкрий це саме посилання в Chrome або Edge — там кнопка працює. На Android в Opera: меню → «Додати на головний екран».')
      : reason==='ios'?(ru?'Safari → «Поделиться» → «На экран Домой».':en?'Safari → Share → Add to Home Screen.':'Safari → «Поділитися» → «На екран Домівки».')
      : (ru?'Браузер не показал окно установки. Попробуй меню ⋮ → «Установить приложение». Если пункта нет — открой в Chrome или Edge.':en?'The browser did not show the install prompt. Try menu ⋮ → Install app. If that item is missing, open in Chrome or Edge.':'Браузер не показав вікно встановлення. Спробуй меню ⋮ → «Встановити застосунок». Якщо пункту немає — відкрий у Chrome або Edge.');
    if(title) title.textContent='⬇ '+(ru?'Установка приложения':en?'Install app':'Встановлення застосунку');
    if(body) body.innerHTML='<div style="margin-bottom:8px">'+esc(short)+'</div><div style="font-size:11px;word-break:break-all"><code>'+esc(location.origin+'/')+'</code></div>';
    const sb=g('pwaShortcutBtn'), cb=g('pwaCopyBtn'), xb=g('pwaCloseBtn');
    if(sb) sb.textContent='⬇ '+(ru?'Скачать ярлык':en?'Download shortcut':'Скачати ярлик');
    if(cb) cb.textContent='📋 '+(ru?'Копировать ссылку':en?'Copy link':'Скопіювати посилання');
    if(xb) xb.textContent=(ru?'Закрыть':en?'Close':'Закрити');
    m.style.display='flex';
  }
  window.pwaInstall = pwaInstall;
  try{
    const s=g('pwaStatus');
    if(s && window.matchMedia('(display-mode: standalone)').matches) s.textContent='✅ '+(LANG==='ru'?'Установлено':LANG==='en'?'Installed':'Встановлено');
    else if(s && !window.isSecureContext) s.textContent='🔒 '+(LANG==='ru'?'Для установки открой по HTTPS':LANG==='en'?'Open over HTTPS to install':'Для встановлення відкрий через HTTPS');
  }catch(e){}

  // Paid Ledger: без продажної сторінки Taobao, тільки робочий інтерфейс
  function applyPaidMode(){
    const hero=g('tbHero'), work=g('tbWorkPanel'), bar=g('tbPaidBar');
    const paid=(typeof GT_PAID!=='undefined' && GT_PAID);
    try{ applyAppName(); }catch(e){}
    document.querySelectorAll('[data-paid-only]').forEach(el=>{ el.style.display=paid?'':'none'; });
    document.querySelectorAll('[data-free-only]').forEach(el=>{ el.style.display=paid?'none':''; });
    if(!paid){
      if(hero) hero.style.display='block';
      if(work) work.style.display='none';
      return;
    }
    if(hero) hero.style.display='none';
    if(work) work.style.display='block';
    if(bar){
      bar.style.display='block';
      ['tbStatus','tbProgress'].forEach(id=>{
        const el=g(id); if(el){ bar.appendChild(el); }
      });
    }
  }
  try{ applyPaidMode(); }catch(e){}

  // PWA: реєструємо service worker (без кешу — тільки для встановлення застосунку)
  if('serviceWorker' in navigator){
    navigator.serviceWorker.register('/sw.js').catch(()=>{});
  }

  // Перемальовуємо таблиці при зміні ширини (мобільні картки ↔ таблиця)
  let _rsz = null;
  window.addEventListener('resize', ()=>{
    clearTimeout(_rsz);
    _rsz = setTimeout(()=>{ renderPurchases(); renderEldorado(); if(g('supList')) renderSupPage(); }, 250);
  });

  // Авто-синхронізація P&L з сервера кожні 60 сек (ПК ↔ телефон)
  setInterval(async ()=>{
    try{
      if(_plSaving || _plDirty) return;   // є незбережені зміни → не перетираємо їх
      const r = await fetch('/api/pl');
      const d = await r.json();
      if(!r.ok || d.ok === false || !Array.isArray(d.purchases)) return;
      const srv = d.purchases;
      if(JSON.stringify(srv) !== JSON.stringify(purchases)){
        purchases = srv;
        renderPurchases();
        renderRevenueChart();
        console.log('P&L авто-оновлено:', srv.length, 'записів');
      }
    }catch(e){}
  }, 60000);

  // Авто-синхронізація ELDORADO між пристроями
  setInterval(async ()=>{
    try{
      if(_edSaving || _edDirty || Date.now()-_edTouched < 7000) return;
      const r = await fetch('/api/eldorado');
      const d = await r.json();
      if(!r.ok || d.ok === false || !Array.isArray(d.sales)) return;
      const srv = d.sales;
      if(JSON.stringify(srv) !== JSON.stringify(edSales)){
        edSales = srv;
        try{ localStorage.setItem('eldorado_sales', JSON.stringify(edSales)); }catch(e){}
        renderEldorado();
        console.log('ELDORADO авто-оновлено:', srv.length, 'записів');
      }
    }catch(e){}
  }, 60000);
})();
</script>
<script>
Object.assign(I18N.uk, {'tk.check':'Перевірити токени','tk.checking':'Перевіряю токени…','fs.title':'Розмір шрифту','fs.reset':'Скинути'});
Object.assign(I18N.en, {'fs.title':'Font size','fs.reset':'Reset'});
Object.assign(I18N.ru, {'fs.title':'Размер шрифта','fs.reset':'Сбросить'});
Object.assign(I18N.uk, {
 'plus.stars':'Telegram Stars: команда /buy у боті Ledger — ключ прийде автоматично.',
 'nav.plus':'Ledger+','plus.free':'Безкоштовна версія','plus.solo':'Ledger+ Solo','plus.team':'Ledger+ Team','plus.setup':'Налаштування під ключ','plus.perMonth':'/міс','plus.once':'разово','plus.features':'Хостинг, Taobao-агент, автододавання замовлень, бекапи, оновлення, підтримка.','plus.activate':'Активувати ключ','plus.deactivate':'Деактивувати','plus.codePh':'LDG… або TRIAL…','plus.plan':'Тариф','plus.expires':'Діє до','plus.days':'Днів залишилось','plus.needKey':'Автододавання та Taobao доступні з ключем Ledger+.','plus.pay':'ОПЛАТА','plus.usdt':'USDT (TRC20 / BEP20)','plus.binance':'Binance Pay ID','plus.payoneer':'Payoneer email','plus.tg':'Telegram','plus.save':'Зберегти реквізити','plus.saved':'Реквізити збережено','plus.hint':'Після оплати надішли скрін + email у Telegram — отримаєш ключ.','plus.trialNote':'Тестові ключі — за запитом у Telegram @ledger_os. Можливі розіграші.','plus.activated':'Ключ активовано',
 'restock.title':'ЩО ДОКУПИТИ','restock.sold':'продано за 30 днів:','restock.stock':'на складі:','restock.margin':'маржа','restock.out':'немає на складі','restock.low':'залишився 1 шт',
 'vault.label':'Шифрувати дані акаунтів','vault.hint':'Ключ у .gt_secrets.json; список показує лише маску, повний логін — по кнопці «Показати».','vault.on':'Шифрування акаунтів увімкнено','vault.off':'Шифрування акаунтів вимкнено',
 'order.autoAdd':'авто в P&L','order.autoOn':'Автододавання увімкнено — нові замовлення з сумою потраплятимуть у P&L','order.autoOff':'Автододавання вимкнено',
 'inv.actSell':'Продати','inv.actSold':'Продано','inv.actReturn':'Повернути на склад','inv.actOff':'Списати','inv.actDelete':'Видалити',
 'twofa.code':'КОД 6 ЦИФР','twofa.recovery':'Recovery-коди','twofa.logoutAll':'Вийти на всіх пристроях',
 'twofa.keepCodes':'Збережи ці коди. Кожен працює один раз.','twofa.copy':'Копіювати',
 'twofa.secretCreated':'🔐 Секрет створено — додай його в Authenticator',
 'twofa.copied':'📋 Recovery-коди скопійовано','twofa.clipboardFail':'⚠ Буфер недоступний',
 'twofa.enabledToast':'✅ 2FA увімкнено','twofa.regenPrompt':'Введи поточний 6-значний код 2FA',
 'twofa.regenDone':'🔑 Нові recovery-коди створено',
 'twofa.logoutConfirm':'Вийти на всіх пристроях? Потрібно буде увійти заново.',
 'twofa.disabledToast':'2FA вимкнено',
 'inv.cost':'Собівартість, USD',
 'diag.title':'ДАНІ Й ДІАГНОСТИКА','diag.press':'натисніть ↻ Оновити',
 'upd.checking':'⏳ Перевіряю GitHub…','upd.fail':'⚠ Не вдалося перевірити',
 'upd.current':'Поточна','upd.latest':'Остання на GitHub',
 'upd.same':'✅ У тебе остання версія','upd.newer':'⬆ Доступна новіша версія','upd.open':'Відкрити release'
});
Object.assign(I18N.en, {
 'plus.stars':'Telegram Stars: /buy in the Ledger bot — the key arrives automatically.',
 'nav.plus':'Ledger+','plus.free':'Free version','plus.solo':'Ledger+ Solo','plus.team':'Ledger+ Team','plus.setup':'Done-for-you setup','plus.perMonth':'/mo','plus.once':'one-time','plus.features':'Hosting, Taobao agent, automatic order import, backups, updates, support.','plus.activate':'Activate key','plus.deactivate':'Deactivate','plus.codePh':'LDG… or TRIAL…','plus.plan':'Plan','plus.expires':'Valid until','plus.days':'Days left','plus.needKey':'Automatic orders and Taobao require a Ledger+ key.','plus.pay':'PAYMENT','plus.usdt':'USDT (TRC20 / BEP20)','plus.binance':'Binance Pay ID','plus.payoneer':'Payoneer email','plus.tg':'Telegram','plus.save':'Save payment details','plus.saved':'Payment details saved','plus.hint':'After payment send a screenshot and your email in Telegram to get the key.','plus.trialNote':'Trial keys on request in Telegram @ledger_os. Giveaways are possible.','plus.activated':'Key activated',
 'restock.title':'RESTOCK SUGGESTIONS','restock.sold':'sold in 30 days:','restock.stock':'in stock:','restock.margin':'margin','restock.out':'out of stock','restock.low':'only 1 left',
 'vault.label':'Encrypt account credentials','vault.hint':'Key lives in .gt_secrets.json; the list shows only a mask, the full login is behind Show.','vault.on':'Credential encryption enabled','vault.off':'Credential encryption disabled',
 'order.autoAdd':'auto to P&L','order.autoOn':'Auto-add enabled — new orders with a price go straight to P&L','order.autoOff':'Auto-add disabled',
 'inv.actSell':'Sell','inv.actSold':'Sold','inv.actReturn':'Return to stock','inv.actOff':'Write off','inv.actDelete':'Delete',
 'twofa.code':'6-DIGIT CODE','twofa.recovery':'Recovery codes','twofa.logoutAll':'Sign out everywhere',
 'twofa.keepCodes':'Save these codes. Each works once.','twofa.copy':'Copy',
 'twofa.secretCreated':'🔐 Secret created — add it to your authenticator',
 'twofa.copied':'📋 Recovery codes copied','twofa.clipboardFail':'⚠ Clipboard unavailable',
 'twofa.enabledToast':'✅ 2FA enabled','twofa.regenPrompt':'Enter the current 6-digit 2FA code',
 'twofa.regenDone':'🔑 New recovery codes created',
 'twofa.logoutConfirm':'Sign out everywhere? You will need to sign in again.',
 'twofa.disabledToast':'2FA disabled',
 'inv.cost':'Cost, USD',
 'diag.title':'DATA & DIAGNOSTICS','diag.press':'click ↻ Refresh',
 'upd.checking':'⏳ Checking GitHub…','upd.fail':'⚠ Could not check',
 'upd.current':'Current','upd.latest':'Latest on GitHub',
 'upd.same':'✅ You are up to date','upd.newer':'⬆ A newer version is available','upd.open':'Open release'
});
Object.assign(I18N.ru, {
 'plus.stars':'Telegram Stars: команда /buy в боте Ledger — ключ придёт автоматически.',
 'nav.plus':'Ledger+','plus.free':'Бесплатная версия','plus.solo':'Ledger+ Solo','plus.team':'Ledger+ Team','plus.setup':'Настройка под ключ','plus.perMonth':'/мес','plus.once':'разово','plus.features':'Хостинг, Taobao-агент, автодобавление заказов, бэкапы, обновления, поддержка.','plus.activate':'Активировать ключ','plus.deactivate':'Деактивировать','plus.codePh':'LDG… или TRIAL…','plus.plan':'Тариф','plus.expires':'Действует до','plus.days':'Осталось дней','plus.needKey':'Автодобавление и Taobao доступны с ключом Ledger+.','plus.pay':'ОПЛАТА','plus.usdt':'USDT (TRC20 / BEP20)','plus.binance':'Binance Pay ID','plus.payoneer':'Payoneer email','plus.tg':'Telegram','plus.save':'Сохранить реквизиты','plus.saved':'Реквизиты сохранены','plus.hint':'После оплаты пришли скрин + email в Telegram — получишь ключ.','plus.trialNote':'Тестовые ключи — по запросу в Telegram @ledger_os. Возможны розыгрыши.','plus.activated':'Ключ активирован',
 'restock.title':'ЧТО ДОКУПИТЬ','restock.sold':'продано за 30 дней:','restock.stock':'на складе:','restock.margin':'маржа','restock.out':'нет на складе','restock.low':'осталась 1 шт',
 'vault.label':'Шифровать данные аккаунтов','vault.hint':'Ключ в .gt_secrets.json; список показывает только маску, полный логин — по кнопке «Показать».','vault.on':'Шифрование аккаунтов включено','vault.off':'Шифрование аккаунтов выключено',
 'order.autoAdd':'авто в P&L','order.autoOn':'Автодобавление включено — новые заказы с суммой попадут в P&L','order.autoOff':'Автодобавление выключено',
 'inv.actSell':'Продать','inv.actSold':'Продано','inv.actReturn':'Вернуть на склад','inv.actOff':'Списать','inv.actDelete':'Удалить',
 'twofa.code':'КОД 6 ЦИФР','twofa.recovery':'Recovery-коды','twofa.logoutAll':'Выйти на всех устройствах',
 'twofa.keepCodes':'Сохрани эти коды. Каждый работает один раз.','twofa.copy':'Копировать',
 'twofa.secretCreated':'🔐 Секрет создан — добавь его в Authenticator',
 'twofa.copied':'📋 Recovery-коды скопированы','twofa.clipboardFail':'⚠ Буфер недоступен',
 'twofa.enabledToast':'✅ 2FA включена','twofa.regenPrompt':'Введи текущий 6-значный код 2FA',
 'twofa.regenDone':'🔑 Новые recovery-коды созданы',
 'twofa.logoutConfirm':'Выйти на всех устройствах? Нужно будет войти заново.',
 'twofa.disabledToast':'2FA выключена',
 'inv.cost':'Себестоимость, USD',
 'diag.title':'ДАННЫЕ И ДИАГНОСТИКА','diag.press':'нажмите ↻ Обновить',
 'upd.checking':'⏳ Проверяю GitHub…','upd.fail':'⚠ Не удалось проверить',
 'upd.current':'Текущая','upd.latest':'Последняя на GitHub',
 'upd.same':'✅ У тебя последняя версия','upd.newer':'⬆ Доступна более новая версия','upd.open':'Открыть release'
});
Object.assign(I18N.en, {'tk.check':'Check tokens','tk.checking':'Checking tokens…'});
Object.assign(I18N.ru, {'tk.check':'Проверить токены','tk.checking':'Проверяю токены…'});

const TR_EN = {
  "збереженими": "saved", "хвилини": "minutes", "хвилин": "minutes", "хвилину": "minute",

  "Канал": "Channel", "новий": "new",

  "у": "in", "і": "and", "У": "In", "І": "And", "з": "with",

  // ── канали / пошта ──
  "Cookie кабінетів": "Account cookies", "є": "set", "немає": "missing",
  "Берегти cookie": "Save cookies", "Взяти з браузера": "Take from browser",
  "Зберегти cookie": "Save cookies",
  "Спостерігаю": "Monitoring", "Спостерігаю…": "Monitoring…",
  "Баланси": "Balances", "Eldorado — продажі": "Eldorado — sales",
  "Спостерігаю за кабінетами": "Watching accounts",
  "Акаунт": "Account", "Email": "Email", "Баланс": "Balance",
  "В обробці / на холді": "Processing / on hold", "Виведено всього": "Withdrawn total",
  "Тіри": "Tiers", "Замовлень": "Orders", "Замовлень (останні)": "Orders (latest)",
  "нові повідомлення": "new messages", "нових повідомлень": "new messages",
  "Замовлень у списку немає": "No orders in the list",
  "Потрібен свіжий cookie: увійдіть на zeusx.com і оновіть токен.":
    "A fresh cookie is required: sign in to zeusx.com and update the token.",
  "Cookie FunPay живе недовго — увійдіть на funpay.com і оновіть.":
    "FunPay cookie is short-lived — sign in to funpay.com and refresh it.",
  "Продажів усього": "Total sales", "Виторг": "Revenue", "Прибуток": "Profit",
  "Цей місяць": "This month", "Джерело": "Source", "пошта + ручний облік": "mail + manual entry",
  "Немає даних": "No data", "немає даних": "no data",
  "Eldorado не має публічного API — дані беруться з пошти та вашого ручного обліку.":
    "Eldorado has no public API — data comes from mail and your manual entry.",
  "Де вигідніше продавати": "Where it is more profitable to sell",
  "Ціна продажу, $": "Sale price, $", "Собівартість, $": "Cost, $", "Ціна продажу, USD": "Sale price, USD", "Собівартість, USD": "Cost, USD",
  "Комісії орієнтовні — уточнюйте тарифи майданчика":
    "Fees are approximate — confirm the marketplace rates",
  "МАЙДАНЧИК": "MARKETPLACE", "КОМІСІЯ": "FEE", "НА РУКИ": "NET", "МАРЖА": "MARGIN",
  "Telegram (прямо)": "Telegram (direct)", "Своя вітрина": "Own storefront",
  "Мої лоти на ZeusX": "My lots on ZeusX",
  // ── пошта ──
  "Очистити всі": "Clear all", "Очистити": "Clear",
  "Листи від FunPay / ZeusX / Eldorado, які трекер уже розпізнав. Нічого не додається автоматично: перенесіть одним кліком у ELDORADO або P&L, або ігноруйте.":
    "Emails from FunPay / ZeusX / Eldorado that the tracker recognised. Nothing is added automatically: move it to ELDORADO or P&L with one click, or ignore it.",
  "FunPay: cookie не задано — замовлення з FunPay сюди не надходять.":
    "FunPay: cookie is not set — FunPay orders do not arrive here.",
  "Вставити cookie": "Paste cookie",
  // ── каталог ──
  "Новинки": "New", "Оновити зараз": "Refresh now",
  "База порожня — натисни ↺ або зачекай оновлення":
    "Database is empty — press ↺ or wait for a refresh",
  "Нічого не знайдено": "Nothing found", "ВСЬОГО": "TOTAL", "всього": "total",
  "Ще немає постачальників — додайте у ⚙ → Постачальники":
    "No suppliers yet — add one in ⚙ → Suppliers",
  "Пошук...": "Search...", "Без сорт.": "No sorting", "Нові першими": "Newest first",
  "Оновлені першими": "Recently updated", "Ціна ↑": "Price ↑", "Ціна ↓": "Price ↓",
  "Sale першими": "On sale first", "є в наявності": "in stock", "зниклі": "gone",
  "дешевше": "cheaper",
  // ── склад ──
  "На складі": "In stock", "Заморожено": "Frozen", "Продано": "Sold",
  "Витрачено всього": "Total spent", "Всі": "All", "Продані": "Sold", "Списані": "Written off",
  "Мертвого складу немає": "No dead stock", "Порожньо — додайте першу закупівлю":
    "Empty — add your first purchase",
  "Назва": "Name", "Гра": "Game", "Додати": "Add", "＋ Додати": "＋ Add",
  "Дані акаунта (логін / пароль / пошта)": "Account data (login / password / mail)",
  // ── налаштування ──
  "ДАНІ Й ДІАГНОСТИКА": "DATA & DIAGNOSTICS", "натисніть ↻ Оновити": "press ↻ Refresh",
  "Завантажити демо-дані": "Load demo data", "Стерти дані": "Erase data",
  "Експорт усіх даних": "Export all data", "Імпорт CSV": "Import CSV",
  "Мій постачальник (Shopify)": "My supplier (Shopify)", "Назва магазину": "Shop name",
  "Працює для Shopify-магазинів (/products.json).":
    "Works for Shopify stores (/products.json).",
  "ПОТРІБНА АВТОМАТИЗАЦІЯ?": "NEED AUTOMATION?",
  "Хочете таку саму автоматизацію: збір Taobao, FunPay/ZeusX, проходження капчі, авто-імпорт замовлень — напишіть у Telegram.":
    "Want the same automation: Taobao collection, FunPay/ZeusX, captcha handling, order auto-import — message me on Telegram.",
  "ТЕМА ІНТЕРФЕЙСУ": "INTERFACE THEME", "Світла": "Light",
  "Розмір шрифту — кнопки A- / A+ у шапці сторінки (запам'ятовується).":
    "Font size — A- / A+ buttons in the page header (remembered).",
  "БЕКАП P&L": "P&L BACKUP", "Зробити зараз": "Run now", "БЕЗПЕКА": "SECURITY",
  "Ledger — лаконічна, без градієнтів": "Ledger — minimal, no gradients",
  "Slate — попередня тема": "Slate — previous theme",
  "Nord — холодний синьо-сірий": "Nord — cool blue-grey",
  "Carbon — теплий графіт": "Carbon — warm graphite",
  // ── аналітика ──
  "ЗВЕДЕНО — ВСІ ЦИФРИ В ОДНОМУ МІСЦІ": "SUMMARY — ALL NUMBERS IN ONE PLACE",
  "ПРИБУТОК": "PROFIT", "ВИРУЧКА": "REVENUE", "ВКЛАДЕНО": "INVESTED",
  "УГОД": "DEALS", "КОМІСІЇ": "FEES", "ВИТОРГ ПО ДНЯХ (30 днів)": "REVENUE BY DAY (30 days)",
  "Виторг $": "Revenue $", "Прибуток $": "Profit $", "АНАЛІТИКА": "ANALYTICS",
  "ПО ІГРАХ": "BY GAME", "ПО МІСЯЦЯХ": "BY MONTH", "Розклад і ліміти": "Schedule & limits",
  "Оновлення баз. год": "Base refresh, h", "Новинки, год": "News, h",
  "Кредити/день": "Credits/day", "Дайджест год": "Digest, h", "Алерт Taobao, ×": "Taobao alert, ×",
  "Зберегти": "Save", "Місячний звіт": "Monthly report", "Показати": "Show",
  "Вибрати місяць": "Pick a month",
  // ── Taobao ──
  "TAOBAO — ціни з Китаю": "TAOBAO — prices from China",
  "Пошук по назві...": "Search by name...", "мін. ціна ¥": "min price ¥",
  "Всі ігри": "All games", "Всі типи": "All types", "Всі регіони": "All regions",
  "Дешевші спершу": "Cheapest first", "Кошик порожній — натисніть 🛒 біля лота, щоб додати":
    "Cart is empty — press 🛒 next to a lot to add it",
  "Нічого не знайдено": "Nothing found",

  // ── додатково (з автоматичного скану) ──
  "Без назви": "Untitled", "Без назви ": "Untitled ", "Весь час": "All time",
  "Дата": "Date", "Прибуток": "Profit", "Записів не знайдено": "No records found",
  "Очистити": "Clear", "Вставити": "Paste", "Поки порожньо": "Empty for now",
  "Листи від": "Emails from", "Нічого не додається автоматично": "nothing is added automatically",
  "Оновити": "Refresh", "Без ": "Without ", "Взяти з браузера": "Take from browser",
  "Виторг": "Revenue", "Дані читаються з ваших кабінетів за збереженими cookie":
    "Data is read from your accounts using saved cookies",
  "Де вигідніше продавати": "Where it is more profitable to sell",
  "База порожня": "Database is empty", "Постачальники": "Suppliers",
  "Ще немає постачальників": "No suppliers yet",
  "Немає прибуткових варіантів за останні": "No profitable options in the last",
  "днів": "days", "Агент працює у фоні": "Agent runs in background",
  "Більше варіантів": "More options", "Всі регіони": "All regions", "Всі типи": "All types",
  "Всі ігри": "All games", "Дешевші спершу": "Cheapest first",
  "Мертвого складу немає": "No dead stock", "Порожньо": "Empty",
  "додайте першу закупівлю": "add your first purchase",
  "АНАЛІТИКА": "ANALYTICS", "Алерт": "Alert", "ВИРУЧКА": "REVENUE",
  "ВИТОРГ ПО ДНЯХ": "REVENUE BY DAY", "ВКЛАДЕНО": "INVESTED",
  "ВСІ ЦИФРИ В ОДНОМУ МІСЦІ": "ALL NUMBERS IN ONE PLACE",
  "Імпорт": "Import", "Авто-бекап раз на день у папку": "Auto-backup once a day to folder",
  "БЕКАП": "BACKUP", "Бот відповідає на команди": "Bot answers commands",
  "Бот пише лише про те": "Bot writes only about", "Вигідні лоти": "Profitable lots",
  "Ціль": "Goal", "ціль": "goal", "Місяць": "Month", "Тиждень": "Week",
  "Сьогодні": "Today", "Вчора": "Yesterday", "За місяць": "This month",
  "Платформа": "Platform", "Платформа ": "Platform ", "Записів": "Records",
  "Редагувати": "Edit", "Видалити": "Delete", "Зберегти ": "Save ",
  "Скасувати": "Cancel", "Готово": "Done", "Назад": "Back", "Далі": "Next",
  "Купив": "Bought", "Продав": "Sold", "Комісія": "Fee", "Кількість": "Qty",
  "Назва гри": "Game name", "Дата ": "Date ", "Замовлення": "Orders",
  "Повідомлення": "Messages", "Нове": "New", "Нові": "New",
  "Налаштування": "Settings", "Мова": "Language", "Тема": "Theme",
  "Профіль": "Profile", "Вихід": "Log out", "Увійти": "Sign in",


  "Продаж": "Sale", "Продаж ": "Sale ", "Свій період": "Custom range",
  "Цей тиждень": "This week", "всі дані": "all data", "Цей місяць": "This month",
  "Сюди потрапляють нові замовлення й повідомлення": "New orders and messages land here",
  "проігноруйте": "ignore", "Підключення": "Connections", "вставте": "insert",
  "з кабінетів": "from accounts", "Ще": "Yet", "Дорожчі спершу": "Most expensive first",
  "Ендгейм": "Endgame", "Збира": "Gath", "Зібрати зараз": "Collect now",
  "Капчу проходите ви": "You pass the captcha", "Лоти": "Lots",
  "Виберіть місяць": "Pick a month", "Виручка": "Revenue",
  "ДЕТАЛЬНА ТАБЛИЦЯ": "DETAIL TABLE", "Дайджест": "Digest", "Кредитів": "Credits",
  "Маржа": "Margin", "Відновити": "Restore", "Згенерувати": "Generate",
  "Зберігаються останні": "Keep latest", "Доступ контролю": "Access control",
  "оновлюю": "refreshing", "наступне через": "next in", "сьогодні": "today",
  "нових": "new", "товарів": "products", "год": "h", "хв": "min",
  "Всього": "Total", "Разом": "Total", "Сума": "Amount",
  "Закрити": "Close", "Відкрити": "Open", "Копіювати": "Copy", "Скопійовано": "Copied",
  "Завантаження": "Loading", "Завантажити": "Download", "Завантажено": "Downloaded",
  "Помилка": "Error", "Успішно": "Success", "Невірний": "Wrong",
  "Спробуйте ще раз": "Try again", "Немає": "No", "Так": "Yes", "Ні": "No",
  "Оберіть": "Choose", "Вибрати": "Choose", "Введіть": "Enter",
  "Мінімум": "Minimum", "Максимум": "Maximum", "Середнє": "Average",
  "Період": "Period", "Діапазон": "Range", "Застосувати": "Apply",


  "Нічого не додається автоматично": "Nothing is added automatically",
  "перенесіть одним кліком у": "move it with one click to",
  "сюди не надходять": "do not arrive here",
  "не задано": "not set", "не підключено": "not connected",
  "Зберігається лише на сервері": "Stored on the server only",
  "Оновлюється не частіше ніж раз на": "Refreshed at most once every",
  "облік": "entry", "Збирається колектором на вашому ПК": "Collected by the agent on your PC",
  "Мітки": "Marks", "Натисніть": "Press", "Оплата": "Payment",
  "Перевірити оплату": "Check payment", "Розвинені": "Developed",
  "Найкраща": "Best", "Оновлення бази": "Base refresh", "РАЗОМ": "TOTAL",
  "Різних ігор": "Different games", "СТАТИСТИКА": "STATISTICS",
  "ТОП ІГРИ ПО ПРИБУТКУ": "TOP GAMES BY PROFIT",
  "Доступ контролює": "Access is controlled by",
  "Зміна пароля діє одразу": "Password change applies immediately",
  "Змінити пароль": "Change password", "КУРС": "RATE", "Копіювання у": "Copying to",
  "Пароль": "Password", "Пароля": "Password", "Логін": "Login",
  "Безпека": "Security", "Ключ": "Key", "Ключі": "Keys",
  "Сервер": "Server", "Клієнт": "Client", "Помилки": "Errors", "Логи": "Logs",
  "Версія": "Version", "Розмір": "Size", "Файли": "Files", "Записів у базі": "Records in DB",
  "Токени": "Tokens", "Канали": "Channels", "Склад": "Stock", "Замовлення з пошти": "Orders from mail",

  "Нічого не додається автоматично": "Nothing is added automatically",
  "замовлення з": "orders from", "не надходять": "do not arrive",
  "які трекер знайшов у пошті": "that the tracker found in mail",
  "які трекер уже розпізнав": "that the tracker already recognised",
  "прибуток за місяць": "profit this month", "продажів": "sales",
  "скопіюйте значення": "copy the value", "сторінка замовлень": "orders page",
  "Стартові": "Starter", "Тільки з оплатою карткою": "Card payment only",
  "Ціни в юанях": "Prices in CNY", "автозапуск при вході в": "autostart on sign-in to",
  "біля лота": "next to a lot", "вони вже відфільтровані": "they are already filtered out",
  "Угод": "Deals", "ЦЕЙ МІСЯЦЬ ПРОТИ МИНУЛОГО": "THIS MONTH VS LAST", "було": "was",
  "день": "day", "прибуток": "profit", "продажі": "sales",
  "Копія бекапів у": "Backup copy to", "НОВИЙ ПАРОЛЬ": "NEW PASSWORD", "ПАПКА": "FOLDER",
  "ПОВТОРИ": "REPEAT", "ПОТОЧНИЙ ПАРОЛЬ": "CURRENT PASSWORD",
  "Відновити ": "Restore ", "Місячний": "Monthly", "Загальний": "Overall",

  "Нічого не додається": "Nothing is added", "або": "or", "хвилини": "minutes",
  "даних ще": "no data yet", "картка": "card", "ключі": "keys",
  "колектор чекає": "agent waits", "лотів": "lots", "найнадійніше": "most reliable",
  "трекер закупівель": "purchasing tracker", "пише лише про те": "writes only about",
  "Падіння цін": "Price drops", "Перевірити зараз": "Check now",
  "Порожнє поле": "Empty field", "Потрібен": "Required", "Пошта": "Mail",
  "Замовлення": "Orders", "Повідомлення": "Messages", "Ціна": "Price",
  "Кількість": "Quantity", "Дата": "Date", "Час": "Time", "Статус": "Status",

  "автоматично": "automatically", "натисніть": "press", "не перевіряли": "not checked yet",
  "не продавець": "not a seller", "не підходять під таку оплату": "do not support this payment",
  "нижче": "below", "орієнтовний долар": "approximate USD",
  "Бот пише лише про те": "Bot writes only about", "Продажі": "Sales",
  "Ресток": "Restock", "Ручне внесення продажу в таблицю не спові":
    "Manual sale entry does not notify",
  "Створи бота у": "Create a bot in", "ТОКЕН БОТА": "BOT TOKEN",
  "ціна": "price", "гри": "games", "гра": "game", "дата": "date",

  "офлайн": "offline", "платформа": "platform", "поповнення балансу": "balance top-up",
  "посередник": "middleman", "потрібен вхід у": "sign-in required in",
  "скільки варіантів акаунтів": "how many account variants",
  "Бот пише лише про те, що": "Bot writes only about what",
  "Ручне внесення продажу в таблицю не сповіщає": "Manual sale entry does not notify",
  "Тест": "Test", "Трекер читає пошту": "Tracker reads mail", "Тунель": "Tunnel",
  "Увімкнено": "Enabled", "Вимкнено": "Disabled", "Перевірити": "Check",
  "Налаштування": "Settings", "Зберегти": "Save", "Скасувати": "Cancel",

  "телефон": "phone", "тому ручна мітка": "so the manual mark", "у вікні браузера": "in the browser window",
  "часто блокує автоматичне читання сторінок": "often blocks automatic page reading",
  "через": "because of", "якщо його": "if it", "Бот пише лише про те": "Bot writes only about",
  "Ручне внесення продажу в таблицю не сповіщає": "Manual sale entry does not notify",
  "Ручне внесення продажу в таблицю не спові": "Manual sale entry does not notify",
  "Форма зміни пароля не діє": "The password change form is inactive",
  "Що надсилати в": "What to send to", "авто": "auto", "агента": "agent",
  "Застосувати": "Apply", "Скинути": "Reset", "Оновити зараз": "Refresh now",

  "якщо там оплата карткою": "if card payment is available there",
  "і сам відкриває вікно браузера": "and opens the browser window itself",
  "адресу не знайдено": "address not found", "акаунти": "accounts", "баланс": "balance",
  "браузер попросить його після перезавантаження":
    "the browser will ask for it after a reload",
  "Бот пише лише про те, що": "Bot writes only about what",
  "Ручне внесення продажу": "Manual sale entry",
  "в таблицю не сповіщає": "into the table does not notify",

  "і сам відкриває вікно браузера": "and opens the browser window itself",
  "будь-яка папка": "any folder", "в таблицю не сповіщає": "into the table does not notify",
  "вимкнено": "disabled", "встав токен і свій": "insert the token and your",
  "для прямого доступу": "for direct access", "Бот пише лише про те": "Bot writes only about",
  "сам відкриває вікно": "opens the window itself", "вікно браузера": "browser window",

  "браузера": "browser", "Бот пише лише про те": "Bot writes only about",
  "в таблицю не сповіщає": "into the table does not notify",
  "дізнатись у": "find it in", "з НБУ": "from NBU", "зазвичай забезпечує проксі":
    "usually provides a proxy", "дізнатись": "find out",

  "показує не кабінет": "does not show the account", "прострочений": "expired",
  "зараз": "now", "оновлення йде": "refresh in progress", "замовлення": "order",
  "запам'ятовується": "remembered", "й за місяць": "and for the month",
  "Бот пише лише про те, що": "Bot writes only about what",
  "в таблицю не сповіщає": "into the table does not notify",

  "Бот пише лише про те, що": "Bot writes only about what",
  "в таблицю не сповіщає": "into the table does not notify",
  "й повідомлення": "and messages", "кнопки": "buttons",
  "кожен тип окремо": "each type separately", "за ": "for ",

  // ── ⚙ Налаштування: повні речення (перебивають переклад слів) ──
  "Розмір шрифту — кнопки": "Font size —",
  "у шапці сторінки (запам'ятовується).": "buttons in the page header (remembered).",
  "Авто-бекап раз на день у папку": "Auto-backup once a day into",
  "поруч з трекером. Зберігаються останні 30 файлів (P&L, ELDORADO, ціль).":
    "next to the tracker. The latest 30 files are kept (P&L, ELDORADO, goal).",
  "Бот пише": "The bot writes",
  "лише про те, що прийшло з пошти": "only about what came from mail",
  "(нові замовлення й повідомлення FunPay / ZeusX / Eldorado) та про досягнення цілі.":
    "(new orders and messages from FunPay / ZeusX / Eldorado) and about reaching the goal.",
  "Ручне внесення продажу в таблицю": "A manual sale entry into the table",
  "сповіщає. Створи бота у": "does not notify. Create a bot in",
  "встав токен і свій chat_id (дізнатись у": "insert the token and your chat_id (find it in",
  "якщо його немає. Капчу проходите ви — колектор чекає.":
    "if you do not have one. You pass the captcha — the agent waits.",
  "💬 Повідомлення покупців": "💬 Buyer messages",
  "⚠️ Watchdog сайту": "⚠️ Site watchdog",
  "⚠️ Watchdog агента Taobao": "⚠️ Taobao agent watchdog",
  "📊 Дайджест (20:00)": "📊 Digest (20:00)",
  "💾 Зберегти сповіщення": "💾 Save notifications",
  "Бот відповідає на команди": "Bot answers commands",
  "(тільки ваш чат):": "(your chat only):",
  "продажі сьогодні й за місяць": "sales today and for the month",
  "баланс ZeusX / FunPay / Eldorado": "ZeusX / FunPay / Eldorado balance",
  "— останні замовлення": "— latest orders",
  "— топ вигідних лотів": "— top profitable lots",
  "📧 Пошта": "📧 Mail",
  "⚠ не налаштовано": "⚠ not configured",
  "✅ налаштовано": "✅ configured",
  "· увімкнено": "· enabled", "· вимкнено": "· disabled",
  "Трекер читає пошту (IMAP) і надсилає в Telegram нові":
    "The tracker reads mail (IMAP) and sends new",
  "FunPay / ZeusX / Eldorado. Потрібен": "FunPay / ZeusX / Eldorado to Telegram. Required:",
  "(не звичайний пароль):": "(not a regular password):",
  "та": "and", "повідомлення": "messages", "замовлення": "orders",
  "увімкнений IMAP у Gmail.": "IMAP enabled in Gmail.",
  "⚠ Gmail не налаштовано — сповіщень з пошти не буде":
    "⚠ Gmail not configured — no mail notifications",
  "немає App Password": "no App Password",
  "перевірено": "checked",
  "Зміна пароля діє одразу (браузер попросить його після перезавантаження). HTTPS — для прямого доступу; на хостингу зазвичай уже є проксі з HTTPS.":
    "Password change applies immediately (the browser will ask for it after a reload). HTTPS is for direct access; on hosting a proxy with HTTPS is usually already in place.",
  "HTTPS вимкнено · на хостингу HTTPS зазвичай забезпечує проксі":
    "HTTPS disabled · on hosting a proxy usually provides HTTPS",
  "⚠ увімкнено, але cert/key не знайдено — виправ і перезапусти":
    "⚠ enabled but cert/key not found — fix it and restart",
  "🌐 Тунель: адресу не знайдено (немає логу cloudflared)":
    "🌐 Tunnel: address not found (no cloudflared log)",
  "боти": "bots", "Сповіщення": "Notifications",

  "не": "", " Не": "", "бо": "because", "це": "this",

  "Місяці": "Months", "CSV (фільтр)": "CSV (filter)", "фільтр": "filter",
  "Price купівлі": "Purchase price", "Price продажу": "Sale price",
  "Order ID (необов'язково)": "Order ID (optional)",
  "Категорія (необов'язково)": "Category (optional)",
  "необов'язково": "optional",
  "логін: user@mail.com": "login: user@mail.com", "пароль: 12345": "password: 12345",
  "пошта: user@mail.com": "mail: user@mail.com", "логін": "login", "пароль": "password",
  "пошта": "mail", "КУРС": "RATE", "Оновити з НБУ": "Refresh from NBU",
  "КУРС USD → UAH": "CURRENCY · USD → UAH", "КУРС (₴ за $1)": "RATE (₴ per $1)",
  "Зберегти": "Save", "Оновити": "Refresh", "Місяць": "Month",
  // ── інше ──
  "Імпорт CSV": "Import CSV", "Інвентар": "Inventory", "Аналітика": "Analytics",
  "Весь час": "All time", "Записи": "Records", "Пошук...": "Search...",
  "P&L + ELDORADO + ціль + налаштування · без паролів і токенів · sha256-перевірка":
    "P&L + ELDORADO + goal + settings · no passwords or tokens · sha256 check",
  "Джерело": "Source", "Більший шрифт": "Larger font",
};

const TR_RU = {
  "збереженими": "сохранёнными", "збережений": "сохранённый", "збережено": "сохранено",
  "хвилини": "минуты", "хвилин": "минут", "хвилину": "минуту", "хв": "мин",

  "Взяти з браузера": "Взять из браузера", "Берегти cookie": "Сохранить cookie",

  "Канал": "Канал", "новий": "новый", "Каналы": "Каналы",

  "APP PASSWORD": "ПАРОЛЬ ПРИЛОЖЕНИЯ", "App Password": "App Password",

  "продажі сьогодні й за місяць": "продажи сегодня и за месяц",
  "баланс ZeusX / FunPay / Eldorado": "баланс ZeusX / FunPay / Eldorado",
  "останні замовлення": "последние заказы", "топ вигідних лотів": "топ выгодных лотов",
  "налаштовано": "настроено", "сповіщень з пошти не буде": "уведомлений из почты не будет",
  "не сповіщає": "не уведомляет", "сповіщення": "уведомления",
  "Замовлення сюди": "Заказы сюда", "поки порожньо": "пока пусто",

  "лише про те, що прийшло з пошти": "только о том, что пришло из почты",
  "(нові замовлення й повідомлення FunPay / ZeusX / Eldorado) та про досягнення цілі.":
    "(новые заказы и сообщения FunPay / ZeusX / Eldorado) и о достижении цели.",
  "Ручне внесення продажу в таблицю": "Ручное внесение продажи в таблицу",
  "Створи бота у": "Создай бота в", "встав токен і свій chat_id (дізнатись у": "вставь токен и свой chat_id (узнать в",
  "Трекер читає пошту (IMAP) і надсилає в Telegram нові": "Трекер читает почту (IMAP) и отправляет в Telegram новые",
  "FunPay / ZeusX / Eldorado. Потрібен": "FunPay / ZeusX / Eldorado. Нужен",
  "(не звичайний пароль):": "(не обычный пароль):",
  "увімкнений IMAP у Gmail.": "включённый IMAP в Gmail.",
  "Авто-бекап раз на день у папку": "Авто-бэкап раз в день в папку",
  "поруч з трекером. Зберігаються останні 30 файлів (P&L, ELDORADO, ціль).":
    "рядом с трекером. Хранятся последние 30 файлов (P&L, ELDORADO, цель).",
  "Завантаження...": "Загрузка...", "без паролів і токенів": "без паролей и токенов",
  "P&L + ELDORADO + ціль + налаштування · без паролів і токенів · sha256-перевірка":
    "P&L + ELDORADO + цель + настройки · без паролей и токенов · sha256-проверка",
  "Зберегти сповіщення": "Сохранить уведомления", "Тест": "Тест",
  "Увімкнено": "Включено", "Вимкнено": "Отключено",
  "Пошта": "Почта", "Перевірити": "Проверить",

  "Пароль вимкнено": "Пароль отключён", "Доступ контролює Cloudflare Access": "Доступ контролирует Cloudflare Access",
  "Форма зміни пароля не діє.": "Форма смены пароля не действует.",
  "заголовок Access обов’язковий": "заголовок Access обязателен",
  "Зміна пароля діє одразу (браузер попросить його після перезавантаження). HTTPS — для прямого доступу; на хостингу зазвичай уже є проксі з HTTPS.":
    "Смена пароля действует сразу (браузер попросит его после перезагрузки). HTTPS — для прямого доступа; на хостинге обычно уже есть прокси с HTTPS.",
  "ПОТОЧНИЙ ПАРОЛЬ": "ТЕКУЩИЙ ПАРОЛЬ", "НОВИЙ ПАРОЛЬ": "НОВЫЙ ПАРОЛЬ", "ПОВТОРИ": "ПОВТОРИТЕ",
  "мін. 6 символів": "мин. 6 символов", "Змінити пароль": "Сменить пароль",
  "Згенерувати self-signed": "Сгенерировать self-signed",
  "HTTPS вимкнено · на хостингу HTTPS зазвичай забезпечує проксі":
    "HTTPS отключён · на хостинге HTTPS обычно обеспечивает прокси",
  "увімкнено, але cert/key не знайдено — виправ і перезапусти":
    "включён, но cert/key не найден — исправь и перезапусти",
  "Тунель: адресу не знайдено (немає логу cloudflared)":
    "Туннель: адрес не найден (нет лога cloudflared)",
  "Пароль вимкнено (GT_AUTH=off)": "Пароль отключён (GT_AUTH=off)",

  "Taobao часто блокує автоматичне читання сторінок": "Taobao часто блокирует автоматическое чтение страниц",
  "якщо там оплата карткою": "если там оплата картой",
  "і сам відкриває вікно браузера": "и сам открывает окно браузера",
  "Зберегти сповіщення": "Сохранить уведомления",
  "замовлення та повідомлення": "заказы и сообщения",
  "у шапці сторінки (запам'ятовується).": "в шапке страницы (запоминается).",
  "і 🎛": "и 🎛", "Бот": "Бот",

  "Нічого не додається": "Ничего не добавляется", "оплата карткою": "оплата картой",
  "орієнтовний долар": "ориентировочный доллар", "читання сторінок лотів": "чтение страниц лотов",
  "Сохранить сповіщення": "Сохранить уведомления", "зазвичай забезпечує проксі": "обычно обеспечивает прокси",
  "замовлення та повідомлення": "заказы и сообщения", "Бот пише": "Бот пишет",
  "скільки варіантів акаунтів": "сколько вариантов аккаунтов", "тому ручна мітка": "поэтому ручная метка",
  "не підходять під таку оплату": "не поддерживают такую оплату",

  "Потрібен": "Нужен", "Розмір шрифту": "Размер шрифта", "кнопки": "кнопки",
  "у шапці сторінки": "в шапке страницы", "Сохранить сповіщення": "Сохранить уведомления",

  "Нічого не додається автоматично": "Ничего не добавляется автоматически",
  "сторінка замовлень": "страница заказов", "ключі": "ключи",
  "колектор чекає": "коллектор ждёт", "найнадійніше": "надёжнее всего",
  "натисніть": "нажмите", "Падіння цін": "Падение цен",
  "Перевірити зараз": "Проверить сейчас", "Повідомлення покупців": "Сообщения покупателей",
  "Порожнє поле": "Пустое поле", "Завантаження": "Загрузка",

  "Нічого не додається автоматично": "Ничего не добавляется автоматически",
  "які трекер уже розпізнав": "которые трекер уже распознал",
  "кабінетів": "кабинетов", "облік": "учёт", "прибуток за місяць": "прибыль за месяц",
  "скопіюйте значення": "скопируйте значение",
  "Тільки з оплатою карткою": "Только с оплатой картой",
  "автозапуск при вході в": "автозапуск при входе в",
  "біля лота": "у лота", "вони вже відфільтровані": "они уже отфильтрованы",
  "трекер закупівель": "трекер закупок",
  "Зміна пароля діє одразу": "Смена пароля действует сразу",
  "Змінити пароль": "Сменить пароль", "Копія бекапів у": "Копия бэкапов в",
  "Нові акаунти": "Новые аккаунты",

  "Свій період": "Свой период", "Сьогодні": "Сегодня", "всі дані": "все данные",
  "Листи від": "Письма от", "Нічого не додається автоматично": "Ничего не добавляется автоматически",
  "або проігноруйте": "или игнорируйте", "перенесіть одним кліком у": "перенесите одним кликом в",
  "Дані читаються з ваших кабінетів": "Данные читаются из ваших кабинетов",
  "Зберігається лише на сервері": "Хранится только на сервере",
  "Оновлюється не частіше ніж раз на": "Обновляется не чаще раза в",
  "Ще немає продажів": "Пока нет продаж", "Агент працює у фоні": "Агент работает в фоне",
  "Більше варіантів": "Больше вариантов", "Дорожчі спершу": "Дороже сначала",
  "Збирається колектором на вашому ПК": "Собирается коллектором на вашем ПК",
  "Виберіть місяць": "Выберите месяц", "Кредитів": "Кредитов",
  "ТОП ІГРИ ПО ПРИБУТКУ": "ТОП ИГРЫ ПО ПРИБЫЛИ", "продажі": "продажи",
  "Імпорт": "Импорт", "Бот відповідає на команди": "Бот отвечает на команды",
  "Вигідні лоти": "Выгодные лоты", "Зберігаються останні": "Хранятся последние",
  "Пароль входу": "Пароль входа", "Без пароля": "Без пароля",
  "Потрібна автоматизація": "Нужна автоматизация", "Зберегти": "Сохранить",

  "Записів не знайдено": "Записей не найдено", "Підключення": "Подключение",
  "не підключено": "не подключено", "немає": "нет", "Натисніть": "Нажмите",
  "потрібен вхід у": "нужен вход в", "у вікні браузера": "в окне браузера",
  "Немає даних": "Нет данных", "Різних ігор": "Разных игр",
  "ЦЕЙ МІСЯЦЬ ПРОТИ МИНУЛОГО": "ЭТОТ МЕСЯЦ ПРОТИВ ПРОШЛОГО",
  "Відновити": "Восстановить", "Доступ контролює": "Доступ контролирует",
  "Копіювання у": "Копирование в", "Форма зміни пароля не діє": "Форма смены пароля не действует",
  "Замовлення з пошти": "Заказы из почты", "Дані й діагностика": "Данные и диагностика",
  "Спостерігаю": "Наблюдаю", "Виторг": "Выручка", "Продажі": "Продажи",
  "Трекер читає пошту": "Трекер читает почту", "Пошта": "Почта", "Готово": "Готово",
  "Застосувати": "Применить", "Скинути": "Сбросить", "Назад": "Назад", "Далі": "Далее",
  "Налаштування": "Настройки", "Мова": "Язык", "Тема": "Тема", "Вийти": "Выйти",

  // ── навігація / заголовки ──
  "Огляд": "Обзор", "Угоди": "Сделки", "Замовлення": "Заказы", "Канали": "Каналы",
  "Каталог": "Каталог", "План": "План", "Інвентар": "Инвентарь", "Аналітика": "Аналитика",
  "ЗАМОВЛЕННЯ З ПОШТИ": "ЗАКАЗЫ ИЗ ПОЧТЫ", "Канали ": "Каналы ",
  "Все канали — останні продажі": "Все каналы — последние продажи",
  "Все канали": "Все каналы", "Баланси": "Балансы", "Оновити": "Обновить",
  "Оновити зараз": "Обновить сейчас", "Оновити з кабінетів": "Обновить из кабинетов",
  // ── пошта ──
  "Очистити всі": "Очистить все", "Очистити": "Очистить",
  "Листи від FunPay / ZeusX / Eldorado, які трекер уже розпізнав. Нічого не додається автоматично: перенесіть одним кліком у ELDORADO або P&L, або ігноруйте.":
    "Письма от FunPay / ZeusX / Eldorado, которые трекер уже распознал. Ничего не добавляется автоматически: перенесите одним кликом в ELDORADO или P&L, либо игнорируйте.",
  "FunPay: cookie не задано — замовлення з FunPay сюди не надходять.":
    "FunPay: cookie не задан — заказы с FunPay сюда не поступают.",
  "Вставити cookie": "Вставить cookie", "Вставити": "Вставить",
  "Поки порожньо. Сюди потрапляють нові замовлення й повідомлення, які трекер знайшов у пошті.":
    "Пока пусто. Сюда попадают новые заказы и сообщения, которые трекер нашёл в почте.",
  // ── канали ──
  "Акаунт": "Аккаунт", "Баланс": "Баланс", "В обробці / на холді": "В обработке / холд",
  "Виведено всього": "Выведено всего", "Тіри": "Тиры", "Замовлень": "Заказов",
  "Замовлень (останні)": "Заказов (последние)", "нові повідомлення": "новые сообщения",
  "Продажів усього": "Продаж всего", "Виторг": "Выручка", "Прибуток": "Прибыль",
  "Цей місяць": "Этот месяц", "Джерело": "Источник", "пошта + ручний облік": "почта + ручной учёт",
  "Замовлень у списку немає": "Заказов в списке нет",
  "Потрібен свіжий cookie: увійдіть на zeusx.com і оновіть токен.":
    "Нужен свежий cookie: войдите на zeusx.com и обновите токен.",
  "Cookie FunPay живе недовго — увійдіть на funpay.com і оновіть.":
    "Cookie FunPay живёт недолго — войдите на funpay.com и обновите.",
  "Eldorado не має публічного API — дані беруться з пошти та вашого ручного обліку.":
    "У Eldorado нет публичного API — данные берутся из почты и вашего ручного учёта.",
  "Де вигідніше продавати": "Где выгоднее продавать",
  "Ціна продажу, $": "Цена продажи, $", "Собівартість, $": "Себестоимость, $", "Ціна продажу, USD": "Цена продажи, USD", "Собівартість, USD": "Себестоимость, USD",
  "Комісії орієнтовні — уточнюйте тарифи майданчика":
    "Комиссии ориентировочные — уточняйте тарифы площадки",
  "МАЙДАНЧИК": "ПЛОЩАДКА", "КОМІСІЯ": "КОМИССИЯ", "НА РУКИ": "НА РУКИ",
  "МАРЖА": "МАРЖА", "Telegram (прямо)": "Telegram (напрямую)",
  "Своя вітрина": "Своя витрина",
  "Мої лоти на ZeusX": "Мои лоты на ZeusX",
  "Дані читаються з ваших кабінетів за збереженими cookie (ZeusX — API, FunPay — сторінка замовлень). Оновлюється не частіше ніж раз на 2 хвилини.":
    "Данные читаются из ваших кабинетов по сохранённым cookie (ZeusX — API, FunPay — страница заказов). Обновляется не чаще раза в 2 минуты.",
  // ── каталог ──
  "ТОВАРИ": "ТОВАРЫ", "Пошук...": "Поиск...", "Без сорт.": "Без сорт.",
  "Нові першими": "Новые первыми", "Оновлені першими": "Обновлённые",
  "Ціна ↑": "Цена ↑", "Ціна ↓": "Цена ↓", "Sale першими": "Sale первыми",
  "є в наявності": "в наличии", "зниклі": "исчезли", "дешевше": "дешевле",
  "Новинки": "Новинки", "Ще немає постачальників — додайте у ⚙ → Постачальники":
    "Пока нет поставщиков — добавьте в ⚙ → Поставщики",
  "База порожня — натисни ↺ або зачекай оновлення":
    "База пуста — нажми ↺ или подожди обновления",
  "Нічого не знайдено": "Ничего не найдено", "ВСЬОГО": "ВСЕГО", "всього": "всего",
  "оновлено": "обновлено", "наступне через": "следующее через",
  "сьогодні": "сегодня", "товарів": "товаров", "нових": "новых", "год": "ч", "хв": "мин",
  // ── склад ──
  "На складі": "На складе", "Заморожено": "Заморожено", "Продано": "Продано",
  "Витрачено всього": "Потрачено всего", "Всі": "Все", "Продані": "Проданные",
  "Списані": "Списанные", "Мертвого складу немає": "Мёртвого склада нет",
  "Порожньо — додайте першу закупівлю": "Пусто — добавьте первую закупку",
  "Назва": "Название", "Гра": "Игра", "Додати": "Добавить",
  "Дані акаунта (логін / пароль / пошта)": "Данные аккаунта (логин / пароль / почта)",
  "Тут куплені акаунти: скільки коштували, у кого, і чи продані. Дає реальну маржу й показує, скільки грошей «заморожено».":
    "Здесь купленные аккаунты: сколько стоили, у кого и проданы ли. Даёт реальную маржу и показывает, сколько денег «заморожено».",
  // ── плани / таобао ──
  "ЧТО КУПИТЬ СЕГОДНЯ": "ЧТО КУПИТЬ СЕГОДНЯ",
  "Немає прибуткових варіантів за останні": "Нет прибыльных вариантов за последние",
  "днів": "дней", "Пошук по назві...": "Поиск по названию...",
  "мін. ціна ¥": "мин. цена ¥", "Всі ігри": "Все игры", "Всі типи": "Все типы",
  "Всі регіони": "Все регионы", "Дешевші спершу": "Дешевле сначала",
  "Кошик порожній — натисніть 🛒 біля лота, щоб додати":
    "Корзина пуста — нажмите 🛒 у лота, чтобы добавить",
  "Ще не перевіряли": "Ещё не проверяли", "Мітки": "Метки", "Оплата": "Оплата",
  "даних ще немає": "данных ещё нет", "офлайн": "офлайн", "посередник": "посредник",
  "Перевірити оплату": "Проверить оплату", "Зібрати зараз": "Собрать сейчас",
  "Лот": "Лот", "Стартові": "Стартовые", "Розвинені": "Развитые",
  "Ціни в юанях": "Цены в юанях",
  // ── ⚙ ──
  "ДАНІ Й ДІАГНОСТИКА": "ДАННЫЕ И ДИАГНОСТИКА", "натисніть ↻ Оновити": "нажмите ↻ Обновить",
  "Завантажити демо-дані": "Загрузить демо-данные", "Стерти дані": "Стереть данные",
  "Експорт усіх даних": "Экспорт всех данных", "Імпорт CSV": "Импорт CSV",
  "Мій постачальник (Shopify)": "Мой поставщик (Shopify)",
  "Назва магазину": "Название магазина",
  "Працює для Shopify-магазинів (/products.json).": "Работает для Shopify-магазинов (/products.json).",
  "ПОТРІБНА АВТОМАТИЗАЦІЯ?": "НУЖНА АВТОМАТИЗАЦИЯ?",
  "Хочете таку саму автоматизацію: збір Taobao, FunPay/ZeusX, проходження капчі, авто-імпорт замовлень — напишіть у Telegram.":
    "Хотите такую же автоматизацию: сбор Taobao, FunPay/ZeusX, прохождение капчи, авто-импорт заказов — напишите в Telegram.",
  "ТЕМА ІНТЕРФЕЙСУ": "ТЕМА ИНТЕРФЕЙСА", "Світла": "Светлая", "Ledger": "Ledger",
  "Розмір шрифту — кнопки A- / A+ у шапці сторінки (запам'ятовується).":
    "Размер шрифта — кнопки A- / A+ в шапке страницы (запоминается).",
  "БЕКАП P&L": "БЭКАП P&L", "Зробити зараз": "Сделать сейчас",
  "БЕЗПЕКА": "БЕЗОПАСНОСТЬ", "Пароль": "Пароль",
  "ПОТРІБНА АВТОМАТИЗАЦІЯ": "НУЖНА АВТОМАТИЗАЦИЯ",
  // ── аналітика ──
  "ЗВЕДЕНО — ВСІ ЦИФРИ В ОДНОМУ МІСЦІ": "СВЕДЕНО — ВСЕ ЦИФРЫ В ОДНОМ МЕСТЕ",
  "ПРИБУТОК": "ПРИБЫЛЬ", "ВИРУЧКА": "ВЫРУЧКА", "ВКЛАДЕНО": "ВЛОЖЕНО",
  "УГОД": "СДЕЛОК", "КОМІСІЇ": "КОМИССИИ", "ВИТОРГ ПО ДНЯХ (30 днів)": "ВЫРУЧКА ПО ДНЯМ (30 дней)",
  "Виторг $": "Выручка $", "Прибуток $": "Прибыль $", "АНАЛІТИКА": "АНАЛИТИКА",
  "ПО ІГРАХ": "ПО ИГРАМ", "ПО МІСЯЦЯХ": "ПО МЕСЯЦАМ",
  "Розклад і ліміти": "Расписание и лимиты", "Оновлення баз. год": "Обновление базы, ч",
  "Новинки, год": "Новинки, ч", "Кредити/день": "Кредиты/день", "Дайджест год": "Дайджест, ч",
  "Алерт Taobao, ×": "Алерт Taobao, ×", "Зберегти": "Сохранить",
  "Місячний звіт": "Месячный отчёт", "Показати": "Показать", "Вибрати місяць": "Выбрать месяц",
};

const EN2RU = {
  "GMAIL → TELEGRAM": "GMAIL → TELEGRAM",

  "Refresh": "Обновить", "Save": "Сохранить", "from": "из", "the": "the",

  "Clear": "Очистить", "Cookies": "Cookie", "Nothing": "Ничего",
  "already": "уже", "This": "Этот", "this": "этот", "your": "ваш", "the": "the",
  "Save": "Сохранить", "Total": "Всего", "Search...": "Поиск...",

  "Clear all": "Очистить всё", "Refresh": "Обновить", "Refresh now": "Обновить сейчас",
  "Save cookies": "Сохранить cookie", "Take from browser": "Взять из браузера",
  "Account cookies": "Cookie кабинетов", "Refresh from accounts": "Обновить из кабинетов",
  "My lots on ZeusX": "Мои лоты на ZeusX", "Yet missing sales": "Пока нет продаж",
  "Eldorado — sales": "Eldorado — продажи", "All channels — recent sales": "Все каналы — последние продажи",
  "New": "Новые", "TOTAL": "ВСЕГО", "All": "Все", "Refresh rate": "Обновить курс",
  "Save": "Сохранить", "CURRENCY": "ВАЛЮТА", "RATE": "КУРС",
  "Collected by the agent on your PC. Agent runs in background (autostart on sign-in to Windows) i opens the window itself browser, if you do not have one. You pass the captcha — the agent waits. Prices in CNY below — approximate USD.":
    "Собирается агентом на вашем ПК. Агент работает в фоне (автозапуск при входе в Windows) и сам открывает окно браузера, если его нет. Капчу проходите вы — агент ждёт. Цены в юанях, ниже — примерный доллар.",
  "Marks: press": "Метки: нажмите", "next to a lot, if card payment is available there,": "у лота, если там оплата картой,",
  " — how many account variants. Taobao often blocks automatic page reading lots («访问异常»), so the manual mark — most reliable.":
    " — сколько вариантов аккаунтов. Taobao часто блокирует автоматическое чтение страниц («访问异常»), поэтому ручная метка — надёжнее.",
  "Payment: card / Apple Pay because of Alipay International (platform, not a seller). Lots «代充 / 充值 / 话费» (balance top-up, phone, keys) do not support this payment — they are already filtered out.":
    "Оплата: карта / Apple Pay через Alipay International (площадка, не продавец). Лоты «代充 / 充值 / 话费» (пополнение баланса, телефон, ключи) не поддерживают эту оплату — они уже отфильтрованы.",
  "PASSWORD (OPTIONAL)": "ПАРОЛЬ (ОПЦИОНАЛЬНО)", "Enable password": "Включить пароль",
  "Disable password": "Отключить пароль", "New password (min 8)": "Новый пароль (мин. 8)",
  "DATA & DIAGNOSTICS": "ДАННЫЕ И ДИАГНОСТИКА", "Load demo data": "Загрузить демо-данные",
  "Erase data": "Стереть данные", "Export all data": "Экспорт всех данных",
  "Import CSV": "Импорт CSV", "My supplier (Shopify)": "Мой поставщик (Shopify)",
  "Shop name": "Название магазина", "Add": "Добавить", "NEED AUTOMATION?": "НУЖНА АВТОМАТИЗАЦИЯ?",
  "INTERFACE THEME": "ТЕМА ИНТЕРФЕЙСА", "P&L BACKUP": "БЭКАП P&L", "Run now": "Сделать сейчас",
  "SECURITY": "БЕЗОПАСНОСТЬ", "TELEGRAM NOTIFICATIONS": "TELEGRAM-УВЕДОМЛЕНИЯ",
  "GMAIL → TELEGRAM": "GMAIL → TELEGRAM", "CLOUD BACKUP": "ОБЛАЧНЫЙ БЭКАП",
  "Mail": "Почта", "Orders": "Заказы", "Deals": "Сделки", "Channels": "Каналы",
  "Catalog": "Каталог", "Plan": "План", "Taobao": "Taobao", "Inventory": "Инвентарь",
  "Analytics": "Аналитика", "Overview": "Обзор",
};

const TR_PATTERNS = [
  [/^оновлено (.*)$/, "updated $1"],
  [/^оновлено — /, "updated — "],
  [/^наступне через (\d+) год$/, "next in $1 h"],
  [/^наступне через (\d+) хв$/, "next in $1 min"],
  [/^зараз оновлюю…$/, "refreshing now…"],
  [/^оновлення йде$/, "refresh in progress"],
  [/^сьогодні (\d+)\/(\d+)$/, "today $1/$2"],
  [/^ключі (\d+)\/(\d+) \(залишок (\d+)\)$/, "keys $1/$2 (left $3)"],
  [/^(\d+) хв, нових (\d+)$/, "$1 min, new $2"],
  [/^(\d+) товарів$/, "$1 products"],
  [/^(\d+) товарів · /, "$1 products · "],
  [/· товарів$/, "· products"],
  [/^Продажів усього$/, "Total sales"],
  [/^(\d+) · стор\. (\d+)\/(\d+)$/, "$1 · page $2/$3"],
  [/^(\d+) записів$/, "$1 records"],
  [/^(\d+) продажів$/, "$1 sales"],
  [/^(\d+) лотів$/, "$1 lots"],
  [/^(\d+) листів$/, "$1 emails"]
];

const TR_PATTERNS_RU = [
  [/^оновлено — /, "обновлено — "],
  [/^оновлено (.*)$/, "обновлено $1"],
  [/^наступне через (\d+) год$/, "следующее через $1 ч"],
  [/^наступне через (\d+) хв$/, "следующее через $1 мин"],
  [/^зараз оновлюю…$/, "сейчас обновляю…"],
  [/^оновлення йде$/, "обновление идёт"],
  [/^сьогодні (\d+)\/(\d+)$/, "сегодня $1/$2"],
  [/^ключі (\d+)\/(\d+) \(залишок (\d+)\)$/, "ключи $1/$2 (остаток $3)"],
  [/^(\d+) хв, нових (\d+)$/, "$1 мин, новых $2"],
  [/^(\d+) товарів$/, "$1 товаров"],
  [/^(\d+) товарів · /, "$1 товаров · "],
  [/· товарів$/, "· товаров"],
  [/^Продажів усього$/, "Всего продаж"],
  [/^(\d+) · стор\. (\d+)\/(\d+)$/, "$1 · стр. $2/$3"],
  [/^(\d+) записів$/, "$1 записей"],
  [/^(\d+) продажів$/, "$1 продаж"],
  [/^(\d+) лотів$/, "$1 лотов"],
  [/^(\d+) листів$/, "$1 писем"]
];

Object.assign(TR_EN, {
  '📊 Excel (всі дані)':'📊 Excel (all data)',
  '🗑 Очистити':'🗑 Clear',
  '↺ Оновити з кабінетів':'↺ Refresh from accounts',
  '⏳ Завантаження...':'⏳ Loading...',
  '🏦 Де вигідніше продавати':'🏦 Where it pays to sell',
  '🏷 Мої лоти на ZeusX':'🏷 My lots on ZeusX',
  '↻ Оновити':'↻ Refresh',
  '⏳ Завантаження постачальників...':'⏳ Loading suppliers...',
  '🆕 Новинки':'🆕 New items',
  '↻ Оновити зараз':'↻ Refresh now',
  '⏳ Рахую...':'⏳ Calculating...',
  '⚙ Налаштування Taobao-агента':'⚙ Taobao agent settings',
  'Сервер:':'Server:',
  'Токен:':'Token:',
  'Копіювати':'Copy',
  'На ПК: запусти':'On PC: run',
  'з папки Ledger, встав ці два значення, дочекайся Chromium. Потім один раз увійди в Taobao через QR.':'from the Ledger folder, paste these two values, wait for Chromium. Then sign in to Taobao once via QR.',
  '⬇ P&L у CSV':'⬇ P&L to CSV',
  '⬇ ELDORADO у CSV':'⬇ ELDORADO to CSV',
  '📊 СТАТИСТИКА ПО ІГРАХ':'📊 STATS BY GAME',
  '✓ Змінити пароль':'✓ Change password',
  '✓ Зберегти':'✓ Save',
  '🔑 Згенерувати self-signed':'🔑 Generate self-signed'
});

Object.assign(TR_RU, {
  '📊 Excel (всі дані)':'📊 Excel (все данные)',
  '🗑 Очистити':'🗑 Очистить',
  'Eldorado — продажі':'Eldorado — продажи',
  '↺ Оновити з кабінетів':'↺ Обновить из кабинетов',
  'Cookie кабінетів':'Cookie кабинетов',
  'Зберегти cookie':'Сохранить cookie',
  '⏳ Завантаження...':'⏳ Загрузка...',
  '🏦 Де вигідніше продавати':'🏦 Где выгоднее продавать',
  '🏷 Мої лоти на ZeusX':'🏷 Мои лоты на ZeusX',
  '↻ Оновити':'↻ Обновить',
  '⏳ Завантаження постачальників...':'⏳ Загрузка поставщиков...',
  '↻ Оновити зараз':'↻ Обновить сейчас',
  '⏳ Рахую...':'⏳ Считаю...',
  'TAOBAO — ціни з Китаю':'TAOBAO — цены из Китая',
  '⚙ Налаштування Taobao-агента':'⚙ Настройки Taobao-агента',
  'Копіювати':'Копировать',
  'На ПК: запусти':'На ПК: запусти',
  'з папки Ledger, встав ці два значення, дочекайся Chromium. Потім один раз увійди в Taobao через QR.':'из папки Ledger, вставь эти два значения, дождись Chromium. Потом один раз войди в Taobao через QR.',
  '⬇ P&L у CSV':'⬇ P&L в CSV',
  '⬇ ELDORADO у CSV':'⬇ ELDORADO в CSV',
  '📊 СТАТИСТИКА ПО ІГРАХ':'📊 СТАТИСТИКА ПО ИГРАМ',
  '✓ Змінити пароль':'✓ Изменить пароль',
  '✓ Зберегти':'✓ Сохранить',
  '🔑 Згенерувати self-signed':'🔑 Сгенерировать self-signed'
});

Object.assign(TR_RU, {
  "у":"в",
  "і":"и",
  "У":"В",
  "І":"И",
  "з":"с",
  "є":"есть",
  "Спостерігаю…":"Наблюдаю…",
  "Спостерігаю за кабінетами":"Наблюдаю за кабинетами",
  "Email":"Email",
  "нових повідомлень":"новых сообщений",
  "немає даних":"нет данных",
  "＋ Додати":"＋ Добавить",
  "Ledger — лаконічна, без градієнтів":"Ledger — лаконичная, без градиентов",
  "Slate — попередня тема":"Slate — предыдущая тема",
  "Nord — холодний синьо-сірий":"Nord — холодный сине-серый",
  "Carbon — теплий графіт":"Carbon — тёплый графит",
  "Без назви":"Без названия",
  "Без назви ":"Без названия ",
  "Весь час":"Всё время",
  "Дата":"Дата",
  "Поки порожньо":"Пока пусто",
  "Без ":"Без ",
  "Дані читаються з ваших кабінетів за збереженими cookie":"Данные читаются из ваших кабинетов по сохранённым cookie",
  "База порожня":"База пуста",
  "Постачальники":"Поставщики",
  "Ще немає постачальників":"Поставщиков пока нет",
  "Порожньо":"Пусто",
  "додайте першу закупівлю":"добавьте первую закупку",
  "Алерт":"Алерт",
  "ВИТОРГ ПО ДНЯХ":"ВЫРУЧКА ПО ДНЯМ",
  "ВСІ ЦИФРИ В ОДНОМУ МІСЦІ":"ВСЕ ЦИФРЫ В ОДНОМ МЕСТЕ",
  "БЕКАП":"БЭКАП",
  "Бот пише лише про те":"Бот пишет только о том",
  "Ціль":"Цель",
  "ціль":"цель",
  "Місяць":"Месяц",
  "Тиждень":"Неделя",
  "Вчора":"Вчера",
  "За місяць":"За месяц",
  "Платформа":"Платформа",
  "Платформа ":"Платформа ",
  "Записів":"Записей",
  "Редагувати":"Редактировать",
  "Видалити":"Удалить",
  "Зберегти ":"Сохранить ",
  "Скасувати":"Отмена",
  "Купив":"Купил",
  "Продав":"Продал",
  "Комісія":"Комиссия",
  "Кількість":"Количество",
  "Назва гри":"Название игры",
  "Дата ":"Дата ",
  "Повідомлення":"Сообщения",
  "Нове":"Новое",
  "Нові":"Новые",
  "Профіль":"Профиль",
  "Вихід":"Выход",
  "Увійти":"Войти",
  "Продаж":"Продажа",
  "Продаж ":"Продажа ",
  "Цей тиждень":"Эта неделя",
  "Сюди потрапляють нові замовлення й повідомлення":"Сюда попадают новые заказы и сообщения",
  "проігноруйте":"проигнорируйте",
  "вставте":"вставьте",
  "з кабінетів":"из кабинетов",
  "Ще":"Ещё",
  "Ендгейм":"Эндгейм",
  "Збира":"Собир",
  "Капчу проходите ви":"Капчу проходите вы",
  "Лоти":"Лоты",
  "Виручка":"Выручка",
  "ДЕТАЛЬНА ТАБЛИЦЯ":"ДЕТАЛЬНАЯ ТАБЛИЦА",
  "Дайджест":"Дайджест",
  "Маржа":"Маржа",
  "Згенерувати":"Сгенерировать",
  "Доступ контролю":"Доступ контролирует",
  "оновлюю":"обновляю",
  "Всього":"Всего",
  "Разом":"Итого",
  "Сума":"Сумма",
  "Закрити":"Закрыть",
  "Відкрити":"Открыть",
  "Скопійовано":"Скопировано",
  "Завантажити":"Скачать",
  "Завантажено":"Загружено",
  "Помилка":"Ошибка",
  "Успішно":"Успешно",
  "Невірний":"Неверный",
  "Спробуйте ще раз":"Попробуйте ещё раз",
  "Немає":"Нет",
  "Так":"Да",
  "Ні":"Нет",
  "Оберіть":"Выберите",
  "Вибрати":"Выбрать",
  "Введіть":"Введите",
  "Мінімум":"Минимум",
  "Максимум":"Максимум",
  "Середнє":"Среднее",
  "Період":"Период",
  "Діапазон":"Диапазон",
  "сюди не надходять":"сюда не поступают",
  "не задано":"не задано",
  "Найкраща":"Лучшая",
  "Оновлення бази":"Обновление базы",
  "РАЗОМ":"ИТОГО",
  "СТАТИСТИКА":"СТАТИСТИКА",
  "КУРС":"КУРС",
  "Пароля":"Пароля",
  "Логін":"Логин",
  "Безпека":"Безопасность",
  "Ключ":"Ключ",
  "Ключі":"Ключи",
  "Сервер":"Сервер",
  "Клієнт":"Клиент",
  "Помилки":"Ошибки",
  "Логи":"Логи",
  "Версія":"Версия",
  "Розмір":"Размер",
  "Файли":"Файлы",
  "Записів у базі":"Записей в базе",
  "Токени":"Токены",
  "Склад":"Склад",
  "замовлення з":"заказы из",
  "не надходять":"не поступают",
  "які трекер знайшов у пошті":"которые трекер нашёл в почте",
  "продажів":"продаж",
  "Угод":"Сделок",
  "було":"было",
  "день":"день",
  "прибуток":"прибыль",
  "ПАПКА":"ПАПКА",
  "Відновити ":"Восстановить ",
  "Місячний":"Месячный",
  "Загальний":"Общий",
  "або":"или",
  "даних ще":"данных ещё",
  "картка":"карта",
  "лотів":"лотов",
  "пише лише про те":"пишет только о том",
  "Ціна":"Цена",
  "Час":"Время",
  "Статус":"Статус",
  "автоматично":"автоматически",
  "не перевіряли":"не проверяли",
  "не продавець":"не продавец",
  "нижче":"ниже",
  "Ресток":"Ресток",
  "Ручне внесення продажу в таблицю не спові":"Ручное внесение продажи в таблицу не уведом",
  "ТОКЕН БОТА":"ТОКЕН БОТА",
  "ціна":"цена",
  "гри":"игры",
  "гра":"игра",
  "дата":"дата",
  "платформа":"платформа",
  "поповнення балансу":"пополнение баланса",
  "Бот пише лише про те, що":"Бот пишет только о том, что",
  "Ручне внесення продажу в таблицю не сповіщає":"Ручное внесение продажи в таблицу не уведомляет",
  "Тунель":"Туннель",
  "телефон":"телефон",
  "часто блокує автоматичне читання сторінок":"часто блокирует автоматическое чтение страниц",
  "через":"из-за",
  "якщо його":"если его",
  "Що надсилати в":"Что отправлять в",
  "авто":"авто",
  "агента":"агента",
  "адресу не знайдено":"адрес не найден",
  "акаунти":"аккаунты",
  "баланс":"баланс",
  "браузер попросить його після перезавантаження":"браузер попросит его после перезагрузки",
  "Ручне внесення продажу":"Ручное внесение продажи",
  "в таблицю не сповіщає":"в таблицу не уведомляет",
  "будь-яка папка":"любая папка",
  "вимкнено":"отключено",
  "встав токен і свій":"вставь токен и свой",
  "для прямого доступу":"для прямого доступа",
  "сам відкриває вікно":"сам открывает окно",
  "вікно браузера":"окно браузера",
  "браузера":"браузера",
  "дізнатись у":"узнать в",
  "з НБУ":"из НБУ",
  "дізнатись":"узнать",
  "показує не кабінет":"показывает не кабинет",
  "прострочений":"просрочен",
  "зараз":"сейчас",
  "оновлення йде":"обновление идёт",
  "замовлення":"заказы",
  "запам'ятовується":"запоминается",
  "й за місяць":"и за месяц",
  "й повідомлення":"и сообщения",
  "кожен тип окремо":"каждый тип отдельно",
  "за  ":"за  ",
  "Розмір шрифту — кнопки":"Размер шрифта — кнопки",
  "сповіщає. Створи бота у":"уведомляет. Создай бота в",
  "якщо його немає. Капчу проходите ви — колектор чекає.":"если его нет. Капчу проходите вы — коллектор ждёт.",
  "💬 Повідомлення покупців":"💬 Сообщения покупателей",
  "⚠️ Watchdog сайту":"⚠️ Watchdog сайта",
  "⚠️ Watchdog агента Taobao":"⚠️ Watchdog агента Taobao",
  "📊 Дайджест (20:00)":"📊 Дайджест (20:00)",
  "💾 Зберегти сповіщення":"💾 Сохранить уведомления",
  "(тільки ваш чат):":"(только ваш чат):",
  "— останні замовлення":"— последние заказы",
  "— топ вигідних лотів":"— топ выгодных лотов",
  "📧 Пошта":"📧 Почта",
  "⚠ не налаштовано":"⚠ не настроено",
  "✅ налаштовано":"✅ настроено",
  "· увімкнено":"· включено",
  "· вимкнено":"· отключено",
  "та":"и",
  "повідомлення":"сообщения",
  "⚠ Gmail не налаштовано — сповіщень з пошти не буде":"⚠ Gmail не настроен — уведомлений с почты не будет",
  "немає App Password":"нет App Password",
  "перевірено":"проверено",
  "⚠ увімкнено, але cert/key не знайдено — виправ і перезапусти":"⚠ включено, но cert/key не найдены — исправь и перезапусти",
  "🌐 Тунель: адресу не знайдено (немає логу cloudflared)":"🌐 Туннель: адрес не найден (нет лога cloudflared)",
  "боти":"боты",
  "Сповіщення":"Уведомления",
  "не":"не",
  " Не":" Не",
  "бо":"т.к.",
  "це":"это",
  "Місяці":"Месяцы",
  "CSV (фільтр)":"CSV (фильтр)",
  "фільтр":"фильтр",
  "Price купівлі":"Цена покупки",
  "Price продажу":"Цена продажи",
  "Order ID (необов'язково)":"Order ID (необязательно)",
  "Категорія (необов'язково)":"Категория (необязательно)",
  "необов'язково":"необязательно",
  "логін: user@mail.com":"логин: user@mail.com",
  "пароль: 12345":"пароль: 12345",
  "пошта: user@mail.com":"почта: user@mail.com",
  "логін":"логин",
  "пароль":"пароль",
  "пошта":"почта",
  "Оновити з НБУ":"Обновить из НБУ",
  "КУРС USD → UAH":"КУРС · USD → UAH",
  "КУРС (₴ за $1)":"КУРС (₴ за $1)",
  "Записи":"Записи",
  "Більший шрифт":"Крупнее шрифт",
  "🆕 Новинки":"🆕 Новинки",
  "Сервер:":"Сервер:",
  "Токен:":"Токен:",
  "Ще немає записів":"Записей пока нет",
  "➕ Додати":"➕ Добавить",
  "📥 Імпорт CSV":"📥 Импорт CSV",
  "Завантаження…":"Загрузка…",
  "Українська":"Украинский",
  "Оновити сторінку":"Обновить страницу",
  "🔍 Пошук...":"🔍 Поиск...",
  "🔍 Пошук по назві...":"🔍 Поиск по названию...",
  "Товари, які зникли з полиць магазинів за останні 14 днів":"Товары, которые исчезли с полок магазинов за последние 14 дней",
  "Товари, які в іншому магазині дешевші":"Товары, которые в другом магазине дешевле",
  "Швидка перевірка новинок через sitemap (безкоштовно)":"Быстрая проверка новинок через sitemap (бесплатно)",
  "Повне оновлення бази (витрачає кредити ScraperAPI)":"Полное обновление базы (тратит кредиты ScraperAPI)",
  "Прочитати cookie з відкритого вікна браузера (FunPay/ZeusX)":"Прочитать cookie из открытого окна браузера (FunPay/ZeusX)",
  "CSV лотів зі складу (ціна = собівартість × 1.3)":"CSV лотов со склада (цена = себестоимость × 1.3)",
  "CSV лотів із каталогу постачальників (ціна = закупівля × 1.3)":"CSV лотов из каталога поставщиков (цена = закупка × 1.3)",
  "Доступно з (Hold → Available)":"Доступно с (Hold → Available)",
  "Світла тема (день)":"Светлая тема (день)",
  "Назва...":"Название...",
  "✅ Комісії збережено":"✅ Комиссии сохранены",
  "Пароль для зашифрованого бекапу (мін. 4 символи)":"Пароль для зашифрованного бэкапа (мин. 4 символа)",
  "⚠ Пароль закороткий":"⚠ Пароль слишком короткий",
  "🔒 Шифрую бекап…":"🔒 Шифрую бэкап…",
  "✅ Зашифрований бекап завантажено":"✅ Зашифрованный бэкап загружен",
  "Пароль від зашифрованого бекапу":"Пароль от зашифрованного бэкапа",
  "⏳ Надсилаю тест...":"⏳ Отправляю тест...",
  "📨 Тест надіслано в Telegram!":"📨 Тест отправлен в Telegram!",
  "⏳ Перевіряю Gmail...":"⏳ Проверяю Gmail...",
  "⏳ Перевіряю пошту...":"⏳ Проверяю почту...",
  "✅ Скопійовано":"✅ Скопировано",
  "Скопіюй:":"Скопируй:",
  "✅ Розклад бекапів збережено":"✅ Расписание бэкапов сохранено",
  "⚠ Введи пароль шифрування":"⚠ Введи пароль шифрования",
  "🔒 Автошифрування увімкнено":"🔒 Автошифрование включено",
  "🔓 Автошифрування вимкнено":"🔓 Автошифрование отключено",
  "🧪 Тестую відновлення...":"🧪 Тестирую восстановление...",
  "⏳ Бекап...":"⏳ Бэкап...",
  "✅ Правила payout збережено":"✅ Правила payout сохранены",
  "⚠ Немає колонки amount":"⚠ Нет колонки amount",
  "Порожній файл":"Пустой файл",
  "Введи назву і ціну продажу":"Введи название и цену продажи",
  "✅ Продаж додано!":"✅ Продажа добавлена!",
  "⏳ Перевіряю новинки через sitemap...":"⏳ Проверяю новинки через sitemap...",
  "🔔 Базовий список магазинів збережено":"🔔 Базовый список магазинов сохранён",
  "⏳ Оновлення запущено...":"⏳ Обновление запущено...",
  "✅ Базу оновлено":"✅ База обновлена",
  "⚠ Браузер не підтримує Notification":"⚠ Браузер не поддерживает Notification",
  "💳 Перевірка запущена — стежте за смугою прогресу":"💳 Проверка запущена — следите за полосой прогресса",
  "⚠ Буфер обміну недоступний":"⚠ Буфер обмена недоступен",
  "⚠ Дозволь спливаючі вікна для PDF":"⚠ Разреши всплывающие окна для PDF",
  "⚠ замовлення не знайдено":"⚠ заказ не найден",
  "⚠ Сервер недоступний — показано локальну копію":"⚠ Сервер недоступен — показана локальная копия",
  "за ":"за "
});

let _trSorted = null;
function _trBuildSorted(){
  const keys = Object.keys(TR_EN).filter(k => k && /[А-Яа-яІіЇїЄє]/.test(k));
  keys.sort((a, b) => b.length - a.length);
  _trSorted = keys;
}
const _CYR = '[А-Яа-яІіЇїЄє]';

// Точний переклад цілого рядка (без послівної підміни — саме вона давала
// «because of», «with папки», «Done к установке»).
function _trLookup(map, txt){
  const s = String(txt);
  const k = s.trim();
  if(!k) return null;
  if(Object.prototype.hasOwnProperty.call(map, k)) return s.replace(k, map[k]);
  return null;
}

function _trText(txt){
  if(LANG === 'uk') return txt;
  const map = (LANG === 'ru') ? TR_RU : TR_EN;
  const exact = _trLookup(map, txt);
  if(exact !== null) return exact;
  let out = String(txt);
  const pats = (LANG === 'ru') ? TR_PATTERNS_RU : TR_PATTERNS;
  for(const [re, rep] of pats){ out = out.replace(re, rep); }
  return out;
}

function _trWalk(root){
  if(!root) return;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
  const nodes = [];
  let n;
  while((n = walker.nextNode())) nodes.push(n);
  for(const node of nodes){
    const parent = node.parentElement;
    if(!parent) continue;
    const tag = parent.tagName;
    if(tag === 'SCRIPT' || tag === 'STYLE' || tag === 'TEXTAREA') continue;
    if(parent.closest && parent.closest('#replyBody,[data-no-i18n]')) continue;
    // зберігаємо оригінал ОДИН раз — далі завжди перекладаємо з нього
    if(typeof node.__o === 'undefined') node.__o = node.nodeValue;
    if(LANG === 'uk'){ node.nodeValue = node.__o; continue; }
    const tr = _trText(node.__o);
    if(node.nodeValue !== tr) node.nodeValue = tr;
  }
  root.querySelectorAll && root.querySelectorAll('[placeholder],[title]').forEach(el => {
    if(el.dataset && el.dataset.i18nPh) return;   // керується applyLang
    for(const attr of ['placeholder','title']){
      const okey = '__o_' + attr;
      const cur = el.getAttribute(attr);
      if(cur === null) continue;
      if(typeof el[okey] === 'undefined') el[okey] = cur;
      const want = (LANG === 'uk') ? el[okey] : _trText(el[okey]);
      if(el.getAttribute(attr) !== want) el.setAttribute(attr, want);
    }
  });
}

let _trTimer = null;
const CMDK_ITEMS=[
 ['overview','Огляд','Overview','Обзор'],['tracker','Угоди','Deals','Сделки'],['mail','Замовлення','Orders','Заказы'],
 ['channels','Канали','Channels','Каналы'],['supply','Каталог','Catalog','Каталог'],['buy','План','Plan','План'],
 ['taobao','Taobao','Taobao','Taobao'],['inventory','Інвентар','Inventory','Инвентарь'],
 ['stats','Аналітика','Analytics','Аналитика'],['setup','Налаштування','Settings','Настройки'],['plus','Ledger+','Ledger+','Ledger+']
];
function _cmdkLabel(x){ return LANG==='en'?x[2]:(LANG==='ru'?x[3]:x[1]); }
function openCmdk(){ const m=g('cmdk'); if(!m) return; m.style.display='flex'; const i=g('cmdkInput'); if(i){ i.value=''; i.focus(); } renderCmdk(''); }
function closeCmdk(){ const m=g('cmdk'); if(m) m.style.display='none'; }
function renderCmdk(q){
  const box=g('cmdkList'); if(!box) return;
  const s=String(q||'').toLowerCase();
  const items=CMDK_ITEMS.filter(x=>!s||_cmdkLabel(x).toLowerCase().includes(s)||x[0].includes(s));
  box.innerHTML=items.map(x=>'<button class="cmdk-item" data-tab="'+x[0]+'" onclick="runCmdk(\''+x[0]+'\')" style="display:block;width:100%;text-align:left;background:transparent;border:0;color:var(--fg);padding:9px 10px;border-radius:8px;font-size:13px;cursor:pointer">'+_cmdkLabel(x)+'</button>').join('');
}
function runCmdk(tab){
  closeCmdk();
  const el=[...document.querySelectorAll('.tab')].find(x=>String(x.getAttribute('onclick')||'').includes("'"+tab+"'"));
  if(el) el.click();
}
document.addEventListener('keydown',e=>{ if((e.ctrlKey||e.metaKey)&&String(e.key).toLowerCase()==='k'){ e.preventDefault(); const m=g('cmdk'); if(m&&m.style.display==='flex') closeCmdk(); else openCmdk(); } else if(e.key==='Escape'){ closeCmdk(); } });

function translateAll(){
  clearTimeout(_trTimer);
  _trTimer = setTimeout(()=>{ _trWalk(document.body); }, 60);
}

</script>
<div id="cmdk" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:12000;align-items:flex-start;justify-content:center;padding-top:14vh" onclick="if(event.target===this)closeCmdk()">
  <div style="width:min(560px,94vw);background:var(--card);border:1px solid var(--brd);border-radius:14px;padding:12px;box-shadow:0 20px 60px rgba(0,0,0,.5)">
    <input id="cmdkInput" placeholder="Ctrl+K — пошук дії" oninput="renderCmdk(this.value)" onkeydown="if(event.key==='Escape')closeCmdk();if(event.key==='Enter'){const b=document.querySelector('#cmdkList .cmdk-item');if(b)b.click();}" style="width:100%;font-size:15px;padding:10px 12px;margin-bottom:8px">
    <div id="cmdkList"></div>
  </div>
</div>
</body>
</html>"""


def render_html(fee_cfg_json, paid=False, lang="en"):
    """HTML з підставленими комісіями, мовою та режимом без продажної сторінки."""
    lang = lang if lang in ("uk", "en", "ru") else "en"
    return (HTML.replace("__FEE_CONFIG__", fee_cfg_json)
                .replace("__PAID_MODE__", "true" if paid else "false")
                .replace("__GT_LANG_VALUE__", lang))
