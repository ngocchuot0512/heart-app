"""Màn hình 02: Trang chủ (Dashboard tổng quan sức khỏe, nút đánh giá nổi bật, nhắc nhở, kiến thức)."""
import streamlit as st

from db import database
from services import importer
from ui.pages.knowledge import ARTICLES
from ui.pages.assess import CP
from ui.theme import LEVEL_COLOR, card, hero_banner, level_pill


def _go(nav: str, view: str | None = None):
    st.session_state["goto"] = nav
    if view:
        st.session_state["diag_view"] = view


def _quick_start():
    bp = int(st.session_state["q_bp"])
    st.session_state["prefill"] = {
        "age": int(st.session_state["q_age"]),
        "trestbps": bp,
        "thalach": int(st.session_state["q_hr"]),
        "cp": int(st.session_state["q_cp"]),
        "_systolic": bp,
    }
    st.session_state["assess_step"] = 1
    _go("Đánh giá", "form")


def _apply_import():
    st.session_state["prefill"] = st.session_state.pop("import_values")
    st.session_state["assess_step"] = 1
    _go("Đánh giá", "form")


def _last(rows: list, key: str):
    for r in reversed(rows):
        if r.get(key) is not None:
            return r[key]
    return None


def render(bundle: dict):
    user = st.session_state["user"]
    prof = st.session_state.get("user_profile") or {}
    name = prof.get("full_name") or user.email.split("@")[0]

    hero_banner(
        "Bảng điều khiển sức khỏe",
        f"Xin chào, {name}",
        "Theo dõi các chỉ số tim mạch quan trọng và thực hiện sàng lọc nguy cơ bằng AI chỉ trong 4 bước đơn giản.",
    )

    # Nút hành động chính nổi bật ngay đầu trang
    cta1, cta2 = st.columns([2.2, 1], gap="medium")
    with cta1:
        st.button("🩺 BẮT ĐẦU ĐÁNH GIÁ NGUY CƠ TIM MẠCH MỚI", type="primary", use_container_width=True,
                  on_click=_go, args=("Đánh giá", "form"))
    with cta2:
        st.button("📚 Kiến thức tim mạch", use_container_width=True, on_click=_go, args=("Kiến thức",))

    st.write("")

    # Dữ liệu tổng quan từ lịch sử
    rows, _ = database.fetch_history()
    rows = rows or []
    sys_ = _last(rows, "systolic") or _last(rows, "trestbps")
    dia_ = _last(rows, "diastolic")
    bp_txt = f"{int(sys_)}/{int(dia_)} mmHg" if sys_ and dia_ else (f"{int(sys_)} mmHg" if sys_ else "Chưa có")
    hr = _last(rows, "thalach")
    chol = _last(rows, "chol")
    prob = _last(rows, "risk_probability")
    lvl = _last(rows, "risk_level")

    # 4 thẻ chỉ số quan trọng
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        lvl_key = {"Thấp": "low", "Trung bình": "mid", "Cao": "high"}.get(lvl, "low")
        badge = level_pill(lvl, LEVEL_COLOR[lvl_key]) if lvl else "Chưa đánh giá"
        st.markdown(
            f'<div class="med-card"><div class="k">Kết quả gần nhất</div>'
            f'<div class="v">{f"{float(prob):.0f}%" if prob is not None else "—"}</div>'
            f'<div class="s">{badge}</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        card("Huyết áp gần nhất", bp_txt, "Mục tiêu < 120/80 mmHg")
    with c3:
        card("Cholesterol", f"{int(chol)} mg/dL" if chol else "Chưa có", "Mức mong muốn < 200")
    with c4:
        card("Nhịp tim tối đa", f"{int(hr)} bpm" if hr else "Chưa có", "Ghi nhận khi gắng sức")

    st.write("")

    # Nhập nhanh hoặc Tải CSV xét nghiệm
    with st.expander("⚡ Nhập nhanh vài chỉ số hoặc tải file xét nghiệm (CSV)", expanded=False):
        q1, q2, q3, q4, q5 = st.columns([0.9, 1.1, 1.2, 1.6, 1.2], vertical_alignment="bottom")
        q1.number_input("Tuổi", 18, 100, 55, key="q_age")
        q2.number_input("Huyết áp (mmHg)", 80, 220, 130, key="q_bp")
        q3.number_input("Nhịp tim tối đa", 60, 220, 150, key="q_hr")
        q4.selectbox("Đau ngực", list(CP), format_func=CP.get, key="q_cp")
        q5.button("Điền vào biểu mẫu", type="primary", use_container_width=True, on_click=_quick_start)

        up = st.file_uploader("Tải file CSV kết quả xét nghiệm (lấy dòng mới nhất)", type=["csv"], key="lab_csv")
        if up is not None:
            vals, warns = importer.parse_lab_csv(up)
            for w in warns:
                st.warning(w)
            if vals:
                st.session_state["import_values"] = vals
                st.success(f"Đã đọc thành công {len(vals)}/13 chỉ số từ file CSV.")
                st.button("Chuyển sang biểu mẫu 4 bước", on_click=_apply_import)

    st.write("")

    # Cột trái: Nhắc nhở chăm sóc sức khỏe | Cột phải: Kiến thức sức khỏe nổi bật
    left, right = st.columns([1, 1.25], gap="large")
    with left:
        st.subheader("⏰ Nhắc nhở hôm nay")
        reminders = st.session_state.get("reminders", [])
        active_rems = [r for r in reminders if r.get("enabled")]
        if not active_rems:
            st.info("Bạn chưa bật nhắc nhở nào. Vào mục **Cá nhân** để thiết lập lịch nhắc.")
        else:
            for r in active_rems:
                st.markdown(
                    f'<div class="med-card" style="margin-bottom:0.65rem;padding:0.9rem 1.1rem;">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                    f'<b>{r["title"]}</b><span class="top-badge">{r["time"]}</span></div>'
                    f'<div class="s" style="margin-top:0.2rem;">Tần suất: {r["freq"]}</div></div>',
                    unsafe_allow_html=True,
                )
        st.button("Quản lý lịch nhắc nhở", on_click=_go, args=("Cá nhân",))

    with right:
        st.subheader("📚 Kiến thức tim mạch nổi bật")
        for art in ARTICLES[:2]:
            st.markdown(
                f'<div class="med-card" style="margin-bottom:0.65rem;padding:0.95rem 1.15rem;">'
                f'<div class="k">{art["category"]} · {art["read_time"]}</div>'
                f'<div style="font-weight:700;color:#0F294A;margin:0.2rem 0;">{art["title"]}</div>'
                f'<div class="s">{art["summary"]}</div></div>',
                unsafe_allow_html=True,
            )
        st.button("Đọc thêm tại Thư viện kiến thức", on_click=_go, args=("Kiến thức",))