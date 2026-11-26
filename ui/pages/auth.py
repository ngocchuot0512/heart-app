"""Màn hình 01: Đăng nhập, Đăng ký."""
import streamlit as st

from db import database
from ui.theme import disclaimer, hero_banner


def render():
    hero_banner(
        "CardioScreen · Healthcare AI",
        "Sàng lọc nguy cơ tim mạch thông minh",
        "Phân tích 13 chỉ số lâm sàng bằng mô hình Machine Learning, giải thích minh bạch từng yếu tố và theo dõi sức khỏe riêng tư.",
    )
    _, mid, _ = st.columns([1, 1.35, 1])
    with mid:
        # ==================== GIAO DIỆN 2 TAB CHÍNH ====================
        tab_in, tab_up = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký"])
        with tab_in:
            with st.form("login"):
                email = st.text_input("Email")
                pw = st.text_input("Mật khẩu", type="password")
                if st.form_submit_button("Đăng nhập", type="primary", use_container_width=True):
                    if not email or not pw:
                        st.warning("Vui lòng nhập đầy đủ email và mật khẩu.")
                    else:
                        with st.spinner("Đang xác thực..."):
                            ok, msg = database.sign_in(email.strip(), pw)
                        if ok:
                            st.rerun()
                        st.error(msg)

        with tab_up:
            with st.form("register"):
                email = st.text_input("Email đăng ký")
                pw = st.text_input("Mật khẩu (tối thiểu 6 ký tự)", type="password")
                pw2 = st.text_input("Xác nhận mật khẩu", type="password")
                if st.form_submit_button("Tạo tài khoản", type="primary", use_container_width=True):
                    if not email or not pw:
                        st.warning("Vui lòng điền đầy đủ thông tin.")
                    elif len(pw) < 6:
                        st.warning("Mật khẩu phải có ít nhất 6 ký tự.")
                    elif pw != pw2:
                        st.error("Mật khẩu xác nhận không khớp.")
                    else:
                        with st.spinner("Đang tạo tài khoản..."):
                            ok, msg = database.sign_up(email.strip(), pw)
                        (st.success if ok else st.error)(msg)

        disclaimer()