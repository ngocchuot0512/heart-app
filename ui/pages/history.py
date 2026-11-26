"""Màn hình 08 & 09: Lịch sử đánh giá, so sánh thay đổi và biểu đồ theo dõi xu hướng."""
import pandas as pd
import streamlit as st

from db import database
from ui import charts
from ui.theme import card, disclaimer

@st.cache_data(show_spinner=False)
def _trend_fig(dates: tuple, vals: tuple, label: str):
    return charts.trend(list(dates), {label: list(vals)})

def render(bundle: dict):
    c_title, c_ref = st.columns([4, 1], vertical_alignment="bottom")
    c_title.title("📈 Lịch sử & Xu hướng sức khỏe")
    c_ref.button("🔄 Làm mới", use_container_width=True)

    rows, err = database.fetch_history()
    if err:
        st.error(err)
        st.caption("Vui lòng kiểm tra cấu hình bảng `diagnosis_history` và chính sách RLS trong `db/schema.sql`.")
        return
    if not rows:
        st.info("Bạn chưa có bản ghi đánh giá nào. Hãy thực hiện một lần ở mục **Đánh giá**.")
        return

    df = pd.DataFrame(rows)
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True).dt.tz_convert("Asia/Ho_Chi_Minh")
    df = df.sort_values("created_at").reset_index(drop=True)
    last = df.iloc[-1]

    c1, c2, c3 = st.columns(3)
    with c1:
        card("Tổng số lần đánh giá", str(len(df)), "Lưu riêng tư trên tài khoản")
    with c2:
        card("Lần đánh giá gần nhất", last["created_at"].strftime("%d/%m/%Y"), last["created_at"].strftime("Lúc %H:%M"))
    with c3:
        delta = "Lần đầu tiên"
        if len(df) > 1:
            d = float(last["risk_probability"]) - float(df.iloc[-2]["risk_probability"])
            delta = f"{d:+.1f} điểm % so với lần trước"
        card("Điểm dự đoán gần nhất", f'{float(last["risk_probability"]):.1f}%', delta)

    st.subheader("Biểu đồ thay đổi chỉ số theo thời gian")
    t1, t2 = st.columns(2)
    with t1:
        with st.container(border=True):
            st.markdown("**Xu hướng điểm dự đoán nhóm 1 (%)**")
            fig1 = _trend_fig(tuple(df["created_at"]), tuple(df["risk_probability"].astype(float)), "Xác suất")
            st.pyplot(fig1, use_container_width=True)
    with t2:
        with st.container(border=True):
            st.markdown("**Theo dõi chỉ số sinh tồn**")
            opts = {"Huyết áp lúc nghỉ (mmHg)": "trestbps", "Cholesterol (mg/dL)": "chol", "Chỉ số BMI": "bmi"}
            avail = [k for k, v in opts.items() if v in df and df[v].notna().any()]
            pick = st.selectbox("Chọn chỉ số", avail, label_visibility="collapsed")
            col = opts[pick]
            sub = df[df[col].notna()]
            fig2 = _trend_fig(tuple(sub["created_at"]), tuple(sub[col].astype(float)), pick)
            st.pyplot(fig2, use_container_width=True)

    st.subheader("Bảng so sánh chi tiết các lần đánh giá")
    show = pd.DataFrame({
        "Thời gian": df["created_at"].dt.strftime("%d/%m/%Y %H:%M"),
        "Hồ sơ": df["patient_name"],
        "Mức đánh giá": df.get("risk_level"),
        "Điểm dự đoán (%)": df["risk_probability"].astype(float).round(1),
        "Chênh lệch (điểm %)": df["risk_probability"].astype(float).diff().round(1),
        "Huyết áp": df["trestbps"],
        "Cholesterol": df["chol"],
        "BMI": df.get("bmi"),
    }).iloc[::-1]
    st.dataframe(show, hide_index=True, use_container_width=True)

    st.download_button(
        "⬇ Xuất dữ liệu lịch sử (CSV)",
        show.to_csv(index=False).encode("utf-8-sig"),
        "lich_su_tim_mach.csv",
        "text/csv",
    )
    st.caption("Lưu ý: Biểu đồ giúp bạn nhận biết xu hướng thay đổi của các chỉ số theo thời gian, không tự kết luận bệnh đã khỏi hay nặng lên chỉ từ điểm số AI.")
    disclaimer()