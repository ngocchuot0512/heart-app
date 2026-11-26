"""Màn hình 11: Thư viện kiến thức & Từ điển chỉ số tim mạch."""
import streamlit as st

from ui.pages.knowledge import ARTICLES, METRIC_GUIDE
from ui.theme import disclaimer


def render(bundle: dict):
    st.title("📚 Kiến thức tim mạch")

    tab_lib, tab_metrics = st.tabs([
        "📚 Thư viện bài viết tim mạch",
        "📖 Từ điển 11 chỉ số y khoa",
    ])

    # ==================== THƯ VIỆN BÀI VIẾT ====================
    with tab_lib:
        st.subheader("Kiến thức chăm sóc & phòng ngừa bệnh tim mạch")
        cats = ["Tất cả"] + sorted(list({a["category"] for a in ARTICLES}))
        sel_cat = st.selectbox("Lọc theo chủ đề", cats)
        for art in ARTICLES:
            if sel_cat != "Tất cả" and art["category"] != sel_cat:
                continue
            with st.expander(f"📄 [{art['category']}] {art['title']} ({art['read_time']})"):
                st.info(art["summary"])
                st.markdown(art["content"])
        disclaimer()

    # ==================== TỪ ĐIỂN CHỈ SỐ ====================
    with tab_metrics:
        st.subheader("Giải thích chi tiết các chỉ số lâm sàng trong ứng dụng")
        for key, info in METRIC_GUIDE.items():
            with st.expander(f"🩺 {info['name']}"):
                st.markdown(
                    f"- **Là gì:** {info['what']}\n"
                    f"- **Ý nghĩa lâm sàng:** {info['meaning']}\n"
                    f"- **Khoảng tham chiếu:** {info['reference']}\n"
                    f"- **Yếu tố ảnh hưởng:** {info['factors']}\n"
                    f"- **Khi nào cần đi khám:** {info['when_doctor']}"
                )
        disclaimer()