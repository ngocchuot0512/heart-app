"""Màn hình Cá nhân & Cài đặt: Hồ sơ sức khỏe, Nhắc nhở chăm sóc, Bảo mật & Dữ liệu."""
from datetime import datetime, time
import streamlit as st

from db import database

SEXES = ["", "Nam", "Nữ", "Khác"]
SMOKE_OPTS = ["Không hút", "Đã bỏ", "Đang hút"]
ALCOHOL_OPTS = ["Không uống", "Thỉnh thoảng", "Thường xuyên"]
HIST_OPTS = ["Không", "Có (bản thân)", "Có (gia đình)"]


def render(bundle: dict):
    user = st.session_state["user"]
    st.title("👤 Cá nhân & Cài đặt")

    prof, err = database.get_profile()
    if err:
        st.warning(err + " (Cần chạy `db/schema.sql` trong Supabase SQL Editor để tạo bảng `profiles`.)")
        prof = {}

    tab_prof, tab_rem, tab_sec = st.tabs([
        "📋 Hồ sơ sức khỏe",
        "⏰ Cài đặt nhắc nhở",
        "🔒 Bảo mật & Dữ liệu",
    ])

    # ================= TAB 1: HỒ SƠ SỨC KHỎE =================
    with tab_prof:
        st.markdown(f"**Tài khoản đăng nhập:** `{user.email}`")
        st.caption("Thông tin lưu tại đây sẽ tự động điền sẵn vào biểu mẫu Đánh giá nguy cơ để bạn không phải nhập lại nhiều lần.")
        with st.form("profile_form"):
            name = st.text_input("Họ và tên", value=prof.get("full_name") or "")
            c1, c2 = st.columns(2)
            year = c1.number_input("Năm sinh", 1920, datetime.now().year, value=int(prof.get("birth_year") or 1985))
            sex_val = prof.get("sex") or ""
            sex = c2.selectbox("Giới tính", SEXES, index=SEXES.index(sex_val) if sex_val in SEXES else 0)

            c3, c4 = st.columns(2)
            height = c3.number_input("Chiều cao (cm)", 120, 220, value=int(st.session_state.get("prof_height", 168)))
            weight = c4.number_input("Cân nặng (kg)", 30, 250, value=int(st.session_state.get("prof_weight", 65)))

            c5, c6, c7 = st.columns(3)
            smoke = c5.selectbox("Thói quen hút thuốc", SMOKE_OPTS,
                                 index=SMOKE_OPTS.index(st.session_state.get("prof_smoke", SMOKE_OPTS[0])))
            alcohol = c6.selectbox("Uống rượu bia", ALCOHOL_OPTS,
                                   index=ALCOHOL_OPTS.index(st.session_state.get("prof_alcohol", ALCOHOL_OPTS[0])))
            hist = c7.selectbox("Tiền sử bệnh tim mạch", HIST_OPTS,
                                index=HIST_OPTS.index(st.session_state.get("prof_hist", HIST_OPTS[0])))

            if st.form_submit_button("💾 Lưu hồ sơ sức khỏe", type="primary", use_container_width=True):
                ok, msg = database.upsert_profile({
                    "full_name": name.strip(),
                    "birth_year": int(year),
                    "sex": sex,
                })
                # Lưu thêm các chỉ số mở rộng vào session để tự điền vào form Đánh giá
                st.session_state["profile_name"] = name.strip()
                st.session_state["prof_birth_year"] = int(year)
                st.session_state["prof_sex"] = 1 if sex == "Nam" else (0 if sex == "Nữ" else 1)
                st.session_state["prof_height"] = int(height)
                st.session_state["prof_weight"] = int(weight)
                st.session_state["prof_smoke"] = smoke
                st.session_state["prof_alcohol"] = alcohol
                st.session_state["prof_hist"] = hist
                (st.success if ok else st.error)(msg)

    
    # ================= TAB 2: CÀI ĐẶT NHẮC NHỞ =================
    with tab_rem:
        st.subheader("Lịch nhắc nhở chăm sóc tim mạch")
        st.caption("Thiết lập lịch nhắc đo huyết áp, vận động, uống thuốc và tái khám định kỳ. Các nhắc nhở đang bật sẽ hiển thị ngay trên Trang chủ.")

        default_reminders = [
            {"label": "Đo huyết áp buổi sáng", "time": time(7, 30), "on": True},
            {"label": "Uống thuốc theo đơn bác sĩ", "time": time(8, 0), "on": False},
            {"label": "Vận động thể chất (30 phút đi bộ)", "time": time(17, 30), "on": True},
            {"label": "Kiểm tra sức khỏe tim mạch định kỳ (6 tháng/lần)", "time": time(9, 0), "on": True},
        ]
        if "reminders" not in st.session_state or not isinstance(st.session_state["reminders"], list):
            st.session_state["reminders"] = default_reminders

        rem_list = st.session_state["reminders"]

        with st.form("reminder_form"):
            for idx, item in enumerate(rem_list):
                label_txt = item.get("label") or item.get("title") or f"Nhắc nhở #{idx + 1}"
                is_on = bool(item.get("on", item.get("active", True)))
                t_val = item.get("time", time(8, 0))
                if isinstance(t_val, str):
                    try:
                        h, m = map(int, t_val.split(":")[:2])
                        t_val = time(h, m)
                    except Exception:
                        t_val = time(8, 0)

                col_a, col_b = st.columns([3, 1.2], vertical_alignment="center")
                new_on = col_a.toggle(label_txt, value=is_on, key=f"rem_on_{idx}")
                new_time = col_b.time_input("Giờ nhắc", value=t_val, key=f"rem_t_{idx}", label_visibility="collapsed")

                # Cập nhật đồng bộ cả key chuẩn của home.py và profile.py
                item["label"] = item["title"] = label_txt
                item["on"] = item["active"] = new_on
                item["time"] = new_time

            if st.form_submit_button("✅ Lưu lịch nhắc nhở", type="primary"):
                st.success("Đã cập nhật lịch nhắc nhở chăm sóc sức khỏe.")

    # ================= TAB 3: BẢO MẬT & DỮ LIỆU =================
    with tab_sec:
        st.subheader("Đổi mật khẩu")
        with st.form("change_pw_form"):
            new_pw = st.text_input("Mật khẩu mới (tối thiểu 6 ký tự)", type="password")
            new_pw2 = st.text_input("Nhập lại mật khẩu mới", type="password")
            if st.form_submit_button("Cập nhật mật khẩu"):
                if len(new_pw) < 6:
                    st.warning("Mật khẩu mới phải có ít nhất 6 ký tự.")
                elif new_pw != new_pw2:
                    st.error("Mật khẩu xác nhận không khớp.")
                else:
                    try:
                        c = database.get_client()
                        if c:
                            c.auth.update_user({"password": new_pw})
                            st.success("Đã đổi mật khẩu thành công!")
                    except Exception as e:
                        st.error(f"Không thể đổi mật khẩu: {e}")

        st.divider()
        st.subheader("Quyền riêng tư & Quản lý dữ liệu")
        with st.expander("📄 Chính sách sử dụng dữ liệu & Bảo mật"):
            st.markdown(
                "- Dữ liệu sức khỏe của bạn được bảo vệ bằng **Row Level Security (RLS)** trên Supabase — chỉ tài khoản của bạn mới có quyền xem và xóa.\n"
                "- Ứng dụng chỉ phục vụ mục đích sàng lọc tham khảo, không chia sẻ dữ liệu y tế cho bên thứ ba."
            )

        confirm = st.checkbox("Tôi hiểu rằng việc xóa toàn bộ lịch sử đánh giá không thể hoàn tác")
        if st.button("🗑 Xóa toàn bộ lịch sử đánh giá", disabled=not confirm):
            ok, msg = database.delete_all_history()
            (st.success if ok else st.error)(msg)

        st.divider()
        if st.button("🚪 Đăng xuất tài khoản", type="primary"):
            database.sign_out()
            st.rerun()