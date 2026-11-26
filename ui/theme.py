"""Hệ thống giao diện Healthcare Technology: Xanh Navy (#0F294A) chủ đạo, Xanh Teal (#0D9488) nhấn,
nền xám sáng (#F4F7FA), thanh điều hướng cố định dưới màn hình 5 mục."""
import math
import streamlit as st

NAVY = "#0F294A"
NAVY_LIGHT = "#1E3A5F"
TEAL = "#0D9488"
TEAL_SOFT = "#E6F4F1"
INK = "#1E293B"
MUTED = "#64748B"
BG = "#F4F7FA"
GREEN = "#10B981"
AMBER = "#F59E0B"
RED = "#DC2626"

LEVEL_COLOR = {"low": TEAL, "mid": AMBER, "high": RED}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');

:root {
  --navy: #0F294A;
  --navy-2: #1E3A5F;
  --teal: #0D9488;
  --teal-soft: #E6F4F1;
  --ink: #1E293B;
  --muted: #64748B;
  --bg: #F4F7FA;
  --amber: #F59E0B;
  --red: #DC2626;
  --shadow: 0 4px 20px rgba(15, 41, 74, 0.06);
  --radius: 18px;
}

html, body, [class*="css"], .stApp {
  font-family: 'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, sans-serif;
  color: var(--ink);
  background-color: var(--bg);
}

/* Ẩn thanh mặc định của Streamlit */
header[data-testid="stHeader"], section[data-testid="stSidebar"],
[data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] {
  display: none !important;
}

.block-container {
  max-width: 1100px;
  padding: 1.2rem 1.4rem 6.5rem 1.4rem; /* chừa khoảng trống cho bottom nav */
}

h1, h2, h3 {
  color: var(--navy);
  font-weight: 700;
  letter-spacing: -0.02em;
}

/* ---------- Top Header gọn ---------- */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #FFFFFF;
  padding: 0.75rem 1.25rem;
  border-radius: 16px;
  box-shadow: var(--shadow);
  border: 1px solid #E2E8F0;
  margin-bottom: 1.2rem;
}
.top-brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-weight: 800;
  font-size: 1.15rem;
  color: var(--navy);
}
.top-badge {
  background: var(--teal-soft);
  color: var(--teal);
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
}
.top-user {
  font-size: 0.88rem;
  color: var(--muted);
  font-weight: 500;
}

/* ---------- Bottom Navigation cố định dưới đáy ---------- */
.st-key-bottomnav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(14px);
  border-top: 1px solid #CBD5E1;
  box-shadow: 0 -4px 20px rgba(15, 41, 74, 0.08);
  padding: 0.45rem 0.5rem;
}
.st-key-bottomnav [role="radiogroup"] {
  display: flex;
  justify-content: space-around;
  max-width: 780px;
  margin: 0 auto;
  gap: 0.25rem;
}
.st-key-bottomnav [role="radiogroup"] label {
  flex: 1;
  text-align: center;
  justify-content: center;
  padding: 0.55rem 0.4rem;
  border-radius: 12px;
  cursor: pointer;
  margin: 0;
  transition: all 0.2s ease;
}
.st-key-bottomnav [role="radiogroup"] label > div:first-child {
  display: none;
}
.st-key-bottomnav [role="radiogroup"] label p {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--muted);
  margin: 0;
}
.st-key-bottomnav [role="radiogroup"] label:hover {
  background: #F1F5F9;
}
.st-key-bottomnav [role="radiogroup"] label:has(input:checked) {
  background: var(--navy);
}
.st-key-bottomnav [role="radiogroup"] label:has(input:checked) p {
  color: #FFFFFF;
}

/* ---------- Hero Banner Navy/Teal ---------- */
.hero-banner {
  background: linear-gradient(135deg, #0F294A 0%, #173F6E 60%, #0D9488 100%);
  color: #FFFFFF;
  border-radius: 22px;
  padding: 1.8rem 2rem;
  box-shadow: 0 10px 28px rgba(15, 41, 74, 0.16);
  margin-bottom: 1.2rem;
}
.hero-banner .eyebrow {
  font-size: 0.85rem;
  font-weight: 600;
  color: #99F6E4;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.hero-banner h1 {
  color: #FFFFFF !important;
  font-size: 1.85rem;
  margin: 0.35rem 0 0.5rem 0;
}
.hero-banner p {
  color: #E2E8F0;
  font-size: 0.96rem;
  margin: 0;
  max-width: 680px;
  line-height: 1.55;
}

/* ---------- Thẻ thống kê & Bento ---------- */
.med-card {
  background: #FFFFFF;
  border-radius: var(--radius);
  padding: 1.25rem 1.4rem;
  box-shadow: var(--shadow);
  border: 1px solid #E2E8F0;
  height: 100%;
}
.med-card .k {
  color: var(--muted);
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.med-card .v {
  color: var(--navy);
  font-size: 1.95rem;
  font-weight: 800;
  margin: 0.25rem 0;
}
.med-card .s {
  color: var(--muted);
  font-size: 0.85rem;
}

/* ---------- Thanh tiến trình nhiều bước ---------- */
.stepper {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.6rem;
  margin: 0.8rem 0 1.2rem 0;
}
.step-item {
  background: #FFFFFF;
  border: 1.5px solid #CBD5E1;
  border-radius: 12px;
  padding: 0.65rem 0.8rem;
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--muted);
  text-align: center;
}
.step-item.active {
  border-color: var(--teal);
  background: var(--teal-soft);
  color: var(--navy);
}
.step-item.done {
  border-color: var(--navy);
  background: var(--navy);
  color: #FFFFFF;
}

/* ---------- Cảnh báo khẩn cấp 115 ---------- */
.emergency-box {
  background: #FEF2F2;
  border: 2px solid #DC2626;
  border-radius: 16px;
  padding: 1.2rem 1.4rem;
  margin-bottom: 1rem;
}
.emergency-box h3 {
  color: #991B1B !important;
  margin: 0 0 0.4rem 0;
  font-size: 1.15rem;
}
.emergency-box p {
  color: #7F1D1D;
  margin: 0;
  font-size: 0.94rem;
  line-height: 1.5;
}

/* ---------- Nút bấm chuẩn y tế ---------- */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
  border-radius: 12px;
  font-weight: 600;
  padding: 0.55rem 1.25rem;
  border: 1.5px solid #CBD5E1;
  background: #FFFFFF;
  color: var(--navy);
  transition: all 0.2s ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
  border-color: var(--teal);
  color: var(--teal);
}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
  background: var(--teal);
  color: #FFFFFF !important;
  border: none;
  box-shadow: 0 4px 14px rgba(13, 148, 136, 0.28);
}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {
  background: #0F766E;
}

/* ---------- Kết quả: Pill, Đồng hồ SVG, Thanh đóng góp ---------- */
.pill {
  display: inline-block;
  padding: 0.28rem 0.9rem;
  border-radius: 999px;
  font-weight: 700;
  color: #FFFFFF;
  font-size: 0.88rem;
}
.gauge {
  width: 100%;
  max-width: 340px;
  margin: 0 auto;
}
.gnum {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 800;
  margin-top: -2.2rem;
}
.bars .row {
  display: grid;
  grid-template-columns: 165px 1fr 56px;
  align-items: center;
  gap: 0.65rem;
  margin: 0.5rem 0;
  font-size: 0.88rem;
}
.bars .track {
  position: relative;
  height: 11px;
  background: #E2E8F0;
  border-radius: 6px;
  overflow: hidden;
}
.bars .track::after {
  content: "";
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #94A3B8;
}
.bars .fill {
  position: absolute;
  top: 0;
  bottom: 0;
  border-radius: 6px;
}
.bars .fill.pos {
  left: 50%;
  background: #DC2626;
}
.bars .fill.neg {
  right: 50%;
  background: #0D9488;
}
.bars .val {
  font-weight: 700;
  text-align: right;
}

.disclaimer {
  background: #FFFFFF;
  border-radius: 14px;
  padding: 0.9rem 1.15rem;
  color: var(--muted);
  font-size: 0.86rem;
  border: 1px solid #E2E8F0;
  border-left: 4px solid var(--amber);
  margin-top: 1rem;
}
.info-note {
  background: var(--teal-soft);
  border-radius: 12px;
  padding: 0.7rem 1rem;
  color: var(--navy);
  font-size: 0.88rem;
  margin-bottom: 0.8rem;
}

@media (max-width: 768px) {
  .stepper { grid-template-columns: repeat(2, 1fr); }
  .st-key-bottomnav [role="radiogroup"] label p { font-size: 0.78rem; }
}
</style>
"""


def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)


def top_header_html(user_name: str) -> str:
    return (
        f'<div class="top-bar">'
        f'<div class="top-brand">🫀 CardioScreen <span class="top-badge">AI Sàng lọc Tim mạch</span></div>'
        f'<div class="top-user">Xin chào, <b>{user_name}</b></div>'
        f'</div>'
    )


def hero_banner(eyebrow: str, title: str, sub: str):
    st.markdown(
        f'<div class="hero-banner"><div class="eyebrow">{eyebrow}</div>'
        f'<h1>{title}</h1><p>{sub}</p></div>',
        unsafe_allow_html=True,
    )


def card(label: str, value: str, sub: str = "", *args, **kwargs):
    st.markdown(
        f'<div class="med-card"><div class="k">{label}</div>'
        f'<div class="v">{value}</div><div class="s">{sub}</div></div>',
        unsafe_allow_html=True,
    )


def level_pill(label: str, color: str) -> str:
    return f'<span class="pill" style="background:{color}">{label}</span>'


def gauge_html(p: float, color: str) -> str:
    r = 115
    length = math.pi * r
    off = length * (1 - p)
    rot = -90 + 180 * p
    arc = f"M35 145 A{r} {r} 0 0 1 265 145"
    return (
        f'<div class="gauge"><svg viewBox="0 0 300 175">'
        f'<path d="{arc}" fill="none" stroke="#E2E8F0" stroke-width="20" stroke-linecap="round"/>'
        f'<path d="{arc}" fill="none" stroke="{color}" stroke-width="20" stroke-linecap="round" '
        f'stroke-dasharray="{length:.1f}" stroke-dashoffset="{off:.1f}"/>'
        f'<g transform="rotate({rot:.1f} 150 145)">'
        f'<line x1="150" y1="145" x2="150" y2="52" stroke="{NAVY}" stroke-width="4" stroke-linecap="round"/></g>'
        f'<circle cx="150" cy="145" r="9" fill="{NAVY}"/></svg>'
        f'<div class="gnum" style="color:{color}">{round(p * 100)}%</div></div>'
    )


def contributions_html(contrib: list, top: int = 8) -> str:
    items = contrib[:top]
    scale = max(abs(d["delta"]) for d in items) or 1
    rows = []
    for d in items:
        w = abs(d["delta"]) / scale * 50
        cls = "pos" if d["delta"] > 0 else "neg"
        val = d["delta"] * 100 if abs(d["delta"]) >= 0.0005 else 0
        c_txt = RED if d["delta"] > 0 else TEAL
        rows.append(
            f'<div class="row"><span>{d["label"]}</span>'
            f'<div class="track"><div class="fill {cls}" style="width:{w:.1f}%"></div></div>'
            f'<span class="val" style="color:{c_txt}">{val:+.1f}</span></div>'
        )
    return '<div class="bars">' + "".join(rows) + "</div>"


def disclaimer():
    st.markdown(
        '<div class="disclaimer"><b>⚠️ Lưu ý y khoa quan trọng:</b> Ứng dụng sử dụng mô hình học máy để hỗ trợ '
        '<b>sàng lọc và tham khảo</b>, <b>không thay thế</b> chẩn đoán của bác sĩ hay xét nghiệm lâm sàng. '
        'Nếu có dấu hiệu đau ngực dữ dội, khó thở hoặc ngất, hãy gọi ngay <b>Cấp cứu 115</b>.</div>',
        unsafe_allow_html=True,
    )