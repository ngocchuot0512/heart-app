"""Màn hình 01: Đăng nhập, Đăng ký, Quên mật khẩu."""
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
        tab_in, tab_up, tab_reset = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký", "🔄 Quên mật khẩu"])
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

        with tab_reset:
            with st.form("reset_pw"):
                r_email = st.text_input("Nhập email đã đăng ký")
                if st.form_submit_button("Gửi liên kết đặt lại mật khẩu", use_container_width=True):
                    if not r_email.strip():
                        st.warning("Vui lòng nhập địa chỉ email.")
                    else:
                        c = database.get_client()
                        if c is None:
                            st.error(database.NOT_CONFIGURED)
                        else:
                            try:
                                c.auth.reset_password_for_email(r_email.strip())
                                st.success("Đã gửi hướng dẫn đặt lại mật khẩu. Vui lòng kiểm tra hộp thư email.")
                            except Exception as e:
                                st.error(f"Không thể gửi yêu cầu: {e}")

        disclaimer()