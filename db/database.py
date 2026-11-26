"""Lớp truy cập Supabase (Auth + PostgreSQL). Không chứa khóa ghi cứng:
khóa lấy từ .streamlit/secrets.toml hoặc biến môi trường SUPABASE_URL / SUPABASE_KEY."""
import os
import streamlit as st
from supabase import create_client, Client


def _credentials():
    try:
        if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
            return st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    except Exception:
        pass
    return os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY")


def get_client() -> Client | None:
    """Tái sử dụng client trong phiên làm việc để tránh gọi lại set_session() qua mạng mỗi lần chuyển trang."""
    url, key = _credentials()
    if not url or not key:
        return None
    if "_sb_client" in st.session_state:
        return st.session_state["_sb_client"]

    client = create_client(url, key)
    if "access_token" in st.session_state and "refresh_token" in st.session_state:
        try:
            res = client.auth.set_session(st.session_state["access_token"],
                                          st.session_state["refresh_token"])
            if res and res.session:
                st.session_state["access_token"] = res.session.access_token
                st.session_state["refresh_token"] = res.session.refresh_token
        except Exception:
            pass
    st.session_state["_sb_client"] = client
    return client

@st.cache_data(ttl=60, show_spinner=False)
def _cached_history(user_id: str, access_token: str):
    c = get_client()
    r = c.table("diagnosis_history").select("*").order("created_at", desc=False).execute()
    return r.data


def fetch_history():
    c = get_client()
    if c is None or "user" not in st.session_state:
        return None, "Vui lòng đăng nhập để xem lịch sử."
    try:
        data = _cached_history(st.session_state["user"].id, st.session_state.get("access_token", ""))
        return data, None
    except Exception as e:
        return None, f"Không thể đọc dữ liệu: {e}"


@st.cache_data(ttl=120, show_spinner=False)
def _cached_profile(user_id: str, access_token: str):
    c = get_client()
    r = c.table("profiles").select("*").eq("user_id", user_id).execute()
    return r.data[0] if r.data else {}


def get_profile():
    c = get_client()
    if c is None or "user" not in st.session_state:
        return None, "Vui lòng đăng nhập."
    try:
        data = _cached_profile(st.session_state["user"].id, st.session_state.get("access_token", ""))
        return data, None
    except Exception as e:
        return None, f"Không thể đọc hồ sơ: {e}"


NOT_CONFIGURED = "Chưa cấu hình Supabase (thiếu SUPABASE_URL / SUPABASE_KEY trong secrets)."


# ---------------- Xác thực ----------------
def sign_up(email: str, password: str):
    c = get_client()
    if c is None:
        return False, NOT_CONFIGURED
    try:
        res = c.auth.sign_up({"email": email, "password": password})
        if res.user:
            return True, "Đăng ký thành công! Nếu dự án bật xác nhận email, hãy kiểm tra hộp thư rồi đăng nhập."
        return False, "Không thể tạo tài khoản."
    except Exception as e:
        return False, f"Lỗi đăng ký: {e}"


def sign_in(email: str, password: str):
    c = get_client()
    if c is None:
        return False, NOT_CONFIGURED
    try:
        res = c.auth.sign_in_with_password({"email": email, "password": password})
        if res.session and res.user:
            st.session_state["user"] = res.user
            st.session_state["access_token"] = res.session.access_token
            st.session_state["refresh_token"] = res.session.refresh_token
            return True, "Đăng nhập thành công!"
        return False, "Sai email hoặc mật khẩu."
    except Exception as e:
        return False, f"Lỗi đăng nhập: {e}"


def sign_out():
    try:
        c = get_client()
        if c:
            c.auth.sign_out()
    except Exception:
        pass
    for k in list(st.session_state.keys()):
        del st.session_state[k]


# ---------------- Lịch sử đánh giá ----------------
def save_assessment(record: dict):
    c = get_client()
    if c is None or "user" not in st.session_state:
        return False, "Vui lòng đăng nhập để lưu dữ liệu."
    try:
        record = {**record, "user_id": st.session_state["user"].id}
        c.table("diagnosis_history").insert(record).execute()
        return True, "Đã lưu lần đánh giá vào lịch sử."
    except Exception as e:
        return False, f"Lỗi khi lưu dữ liệu: {e}"


def fetch_history():
    """RLS đảm bảo chỉ trả về bản ghi của người dùng hiện tại."""
    c = get_client()
    if c is None or "user" not in st.session_state:
        return None, "Vui lòng đăng nhập để xem lịch sử."
    try:
        r = c.table("diagnosis_history").select("*").order("created_at", desc=False).execute()
        return r.data, None
    except Exception as e:
        return None, f"Không thể đọc dữ liệu: {e}"


def delete_all_history():
    c = get_client()
    if c is None or "user" not in st.session_state:
        return False, "Vui lòng đăng nhập."
    try:
        c.table("diagnosis_history").delete().eq("user_id", st.session_state["user"].id).execute()
        return True, "Đã xóa toàn bộ lịch sử đánh giá của bạn."
    except Exception as e:
        return False, f"Không thể xóa: {e}"


# ---------------- Hồ sơ cá nhân ----------------
def get_profile():
    c = get_client()
    if c is None or "user" not in st.session_state:
        return None, "Vui lòng đăng nhập."
    try:
        r = c.table("profiles").select("*").eq("user_id", st.session_state["user"].id).execute()
        return (r.data[0] if r.data else {}), None
    except Exception as e:
        return None, f"Không thể đọc hồ sơ: {e}"


def upsert_profile(data: dict):
    c = get_client()
    if c is None or "user" not in st.session_state:
        return False, "Vui lòng đăng nhập."
    try:
        c.table("profiles").upsert({**data, "user_id": st.session_state["user"].id}).execute()
        return True, "Đã cập nhật hồ sơ."
    except Exception as e:
        return False, f"Không thể lưu hồ sơ: {e}"
