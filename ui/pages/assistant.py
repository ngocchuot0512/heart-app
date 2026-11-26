"""Màn hình 10 & 11: Trợ lý AI tư vấn sức khỏe tim mạch (có kiểm soát an toàn) & Thư viện kiến thức."""
import streamlit as st

from db import database
from ui.pages.knowledge import ARTICLES, METRIC_GUIDE
from ui.theme import disclaimer

SUGGESTED_QUESTIONS = [
    "Làm thế nào để kiểm soát huyết áp tại nhà?",
    "Người có cholesterol cao nên ăn gì và kiêng gì?",
    "Nhịp tim bình thường là bao nhiêu?",
    "Những dấu hiệu nào cảnh báo nhồi máu cơ tim?",
    "Nên tập thể dục bao nhiêu phút mỗi ngày?",
    "Phân tích giúp tôi kết quả đánh giá gần nhất của tôi",
]

EMERGENCY_KEYWORDS = ["đau ngực dữ dội", "khó thở", "ngất", "nhồi máu", "bóp nghẹt ngực", "vã mồ hôi lạnh"]


def _generate_safe_reply(prompt: str, use_profile: bool) -> str:
    """Trả lời dựa trên kho kiến thức y khoa đã chuẩn hóa, nhận diện tình huống khẩn cấp và không kê đơn."""
    q = prompt.lower().strip()

    # 1. Nhận diện khẩn cấp 115
    if any(kw in q for kw in EMERGENCY_KEYWORDS):
        return (
            "🚨 **CẢNH BÁO KHẨN CẤP:** Các triệu chứng bạn vừa mô tả có thể liên quan đến tình trạng tim mạch cấp tính.\n\n"
            "- Hãy **gọi ngay Cấp cứu 115** hoặc nhờ người thân đưa tới bệnh viện gần nhất ngay lập tức.\n"
            "- Ngồi nghỉ yên tại chỗ, nới lỏng quần áo, không tự lái xe."
        )

    # 2. Tham khảo hồ sơ nếu người dùng cho phép
    context_note = ""
    if use_profile:
        rows, _ = database.fetch_history()
        if rows:
            last = rows[-1]
            context_note = (
                f"\n\n📋 *Dựa trên lần đánh giá gần nhất của bạn ({last.get('patient_name', 'Hồ sơ')}):* "
                f"Huyết áp lúc nghỉ **{last.get('trestbps')} mmHg**, Cholesterol **{last.get('chol')} mg/dL**, "
                f"Điểm dự đoán AI **{last.get('risk_probability')}%** (Mức: **{last.get('risk_level')}**)."
            )

    # 3. Đối chiếu nội dung chuẩn hóa
    if "huyết áp" in q:
        g = METRIC_GUIDE["trestbps"]
        return (
            f"**Kiểm soát huyết áp hiệu quả:**\n"
            f"- **Mốc tham chiếu:** {g['reference']}\n"
            f"- **Cách cải thiện tự nhiên:** Giảm ăn mặn (< 5g muối/ngày), duy trì cân nặng hợp lý, đi bộ nhanh 30 phút/ngày, hạn chế rượu bia và ngủ đủ giấc.\n"
            f"- **Lưu ý:** {g['when_doctor']}" + context_note
        )
    if "cholesterol" in q or "mỡ máu" in q or "ăn gì" in q:
        g = METRIC_GUIDE["chol"]
        return (
            f"**Chế độ dinh dưỡng cho người có Cholesterol cao:**\n"
            f"- **Mốc tham chiếu:** {g['reference']}\n"
            f"- **Nên ăn:** Rau xanh, trái cây tươi, yến mạch, các loại đậu, cá béo (cá hồi, cá thu), dầu ô-liu.\n"
            f"- **Nên hạn chế:** Mỡ động vật, nội tạng, da gia cầm, đồ chiên rán ngập dầu và thực phẩm chế biến sẵn.\n"
            f"- **Khi nào đi khám:** {g['when_doctor']}" + context_note
        )
    if "nhịp tim" in q:
        return (
            "**Nhịp tim bình thường ở người trưởng thành:**\n"
            "- **Lúc nghỉ ngơi:** Thường dao động từ **60 – 100 nhịp/phút (bpm)**.\n"
            "- **Khi gắng sức tối đa:** Ước tính theo công thức `220 − Tuổi`.\n"
            "- Nếu nhịp tim lúc nghỉ thường xuyên trên 100 bpm hoặc dưới 50 bpm kèm chóng mặt, hồi hộp, bạn nên đi khám chuyên khoa tim mạch." + context_note
        )
    if "tập thể dục" in q or "vận động" in q:
        return (
            "**Khuyến nghị vận động cho sức khỏe tim mạch:**\n"
            "- Duy trì tối thiểu **150 phút/tuần** vận động cường độ vừa (khoảng **30 phút/ngày**, 5 ngày/tuần) như đi bộ nhanh, đạp xe, bơi lội.\n"
            "- Luôn khởi động 5–10 phút và dừng tập ngay nếu thấy tức ngực hoặc hụt hơi bất thường." + context_note
        )
    if "gần nhất" in q or "kết quả" in q or "hồ sơ" in q:
        if not use_profile:
            return "Bạn đang tắt quyền truy cập dữ liệu cá nhân cho Trợ lý AI. Hãy bật công tắc **Cho phép tham khảo hồ sơ sức khỏe** ở phía trên để tôi xem giúp bạn nhé."
        if context_note:
            return (
                "**Tổng hợp nhanh hồ sơ gần nhất của bạn:**" + context_note +
                "\n\nBạn nên duy trì theo dõi huyết áp định kỳ, ăn nhạt, vận động đều đặn và mang theo phiếu báo cáo khi đi khám bác sĩ."
            )
        return "Bạn chưa có dữ liệu đánh giá nào trong lịch sử. Hãy vào mục **Đánh giá** để thực hiện lần kiểm tra đầu tiên."

    return (
        "Cảm ơn câu hỏi của bạn! Hiện tại tôi hỗ trợ giải đáp dựa trên nguồn kiến thức tim mạch chuẩn hóa về: "
        "**huyết áp, cholesterol, đường huyết, nhịp tim, chế độ ăn uống, vận động và dấu hiệu cảnh báo**.\n\n"
        "Bạn có thể chọn một trong các câu hỏi gợi ý bên dưới hoặc đặt câu hỏi cụ thể hơn. "
        "*(Lưu ý: Tôi không kê đơn thuốc hay thay thế tư vấn trực tiếp của bác sĩ)*." + context_note
    )


def render(bundle: dict):
    st.title("💬 Trợ lý AI & Kiến thức tim mạch")

    tab_chat, tab_lib, tab_metrics = st.tabs([
        "🤖 Trợ lý tư vấn AI",
        "📚 Thư viện bài viết tim mạch",
        "📖 Từ điển 11 chỉ số y khoa",
    ])

    # ==================== TAB 1: TRỢ LÝ AI ====================
    with tab_chat:
        use_prof = st.toggle(
            "Cho phép Trợ lý AI tham khảo chỉ số gần nhất trong hồ sơ của tôi",
            value=True,
        )
        st.session_state.setdefault("chat_messages", [
            {
                "role": "assistant",
                "content": "Xin chào! Tôi là **Trợ lý sức khỏe CardioScreen**. Tôi có thể giúp bạn giải thích chỉ số tim mạch, tư vấn lối sống lành mạnh hoặc tổng hợp hồ sơ gần nhất. Bạn muốn hỏi về vấn đề gì?",
            }
        ])

        # Hiển thị lịch sử trò chuyện
        for msg in st.session_state["chat_messages"]:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble-ai">{msg["content"]}</div>', unsafe_allow_html=True)

        # Câu hỏi gợi ý nhanh
        st.caption("💡 Câu hỏi gợi ý nhanh:")
        g_cols = st.columns(3)
        for idx, q in enumerate(SUGGESTED_QUESTIONS):
            if g_cols[idx % 3].button(q, key=f"sug_{idx}", use_container_width=True):
                st.session_state["chat_messages"].append({"role": "user", "content": q})
                reply = _generate_safe_reply(q, use_prof)
                st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
                st.rerun()

        # Ô nhập tin nhắn
        with st.form("chat_form", clear_on_submit=True):
            c_in, c_btn = st.columns([4.5, 1], vertical_alignment="bottom")
            user_q = c_in.text_input("Nhập câu hỏi của bạn...", label_visibility="collapsed",
                                     placeholder="Ví dụ: Huyết áp 140/90 mmHg có cao không?")
            if c_btn.form_submit_button("Gửi", type="primary", use_container_width=True) and user_q.strip():
                st.session_state["chat_messages"].append({"role": "user", "content": user_q.strip()})
                reply = _generate_safe_reply(user_q.strip(), use_prof)
                st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
                st.rerun()

        disclaimer()

    # ==================== TAB 2: THƯ VIỆN BÀI VIẾT ====================
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

    # ==================== TAB 3: TỪ ĐIỂN CHỈ SỐ ====================
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