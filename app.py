"""Điểm vào ứng dụng CardioScreen: cấu hình, xác thực, thanh điều hướng cố định dưới đáy 5 mục."""
import streamlit as st

st.set_page_config(
    page_title="CardioScreen – Sàng lọc nguy cơ tim mạch",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from db import database
from services import risk_service
from ui.theme import apply_theme, top_header_html
from ui.pages import assess, assistant, auth, history, home, profile, result

apply_theme()

NAV = ["Trang chủ", "Đánh giá", "Lịch sử", "Kiến thức", "Cá nhân"]


@st.cache_resource
def _bundle():
    return risk_service.load_bundle()


if "user" not in st.session_state:
    auth.render()
    st.stop()

try:
    bundle = _bundle()
except Exception as e:
    st.error(f"Không thể nạp mô hình AI: {e}")
    st.stop()

# Nạp hồ sơ người dùng 1 lần mỗi phiên để tự động điền thông tin cá nhân vào form chẩn đoán
if "user_profile" not in st.session_state:
    prof, _ = database.get_profile()
    st.session_state["user_profile"] = prof or {}

# Khởi tạo danh sách nhắc nhở mặc định trong phiên làm việc
st.session_state.setdefault("reminders", [
    {"id": "bp", "title": "Đo huyết áp buổi sáng", "time": "07:30", "freq": "Hằng ngày", "enabled": True},
    {"id": "med", "title": "Uống thuốc / thực phẩm hỗ trợ theo chỉ định", "time": "08:00", "freq": "Hằng ngày", "enabled": False},
    {"id": "walk", "title": "Đi bộ nhanh / vận động thể chất 30 phút", "time": "17:30", "freq": "Thứ 2, 4, 6", "enabled": True},
    {"id": "checkup", "title": "Kiểm tra mỡ máu & khám tim mạch định kỳ", "time": "09:00", "freq": "Mỗi 6 tháng", "enabled": True},
])

# Xử lý điều hướng lập trình trước khi khởi tạo widget radio
if "goto" in st.session_state:
    target = st.session_state.pop("goto")
    if target in NAV:
        st.session_state["nav"] = target

st.session_state.setdefault("nav", NAV[0])
st.session_state.setdefault("diag_view", "form")

# Thanh tiêu đề gọn phía trên
user_email = st.session_state["user"].email
prof_name = (st.session_state.get("user_profile") or {}).get("full_name") or user_email.split("@")[0]
st.markdown(top_header_html(prof_name), unsafe_allow_html=True)

# Điều hướng nội dung chính
page = st.session_state["nav"]
if page == "Trang chủ":
    home.render(bundle)
elif page == "Đánh giá":
    if st.session_state["diag_view"] == "result" and st.session_state.get("last_result"):
        result.render(bundle)
    else:
        assess.render(bundle)
elif page == "Lịch sử":
    history.render(bundle)
elif page == "Kiến thức":
    assistant.render(bundle)
else:
    profile.render(bundle)

# Thanh điều hướng cố định dưới cùng (Bottom Navigation Bar - 5 mục)
with st.container(key="bottomnav"):
    st.radio("Điều hướng chính", NAV, key="nav", horizontal=True, label_visibility="collapsed")