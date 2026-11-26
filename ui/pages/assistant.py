"""Màn hình 10 & 11: Trợ lý AI tư vấn sức khỏe tim mạch (có kiểm soát an toàn) & Thư viện kiến thức."""
import streamlit as st
from google import genai
from google.genai import types

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

SYSTEM_PROMPT = """Bạn là Trợ lý Sức khỏe Tim mạch của ứng dụng CardioScreen.
Nhiệm vụ của bạn là giải thích các chỉ số y khoa (huyết áp, cholesterol, nhịp tim, ECG, ST depression...), tư vấn lối sống lành mạnh và hỗ trợ người dùng hiểu kết quả sàng lọc.
Quy tắc bắt buộc:
- Trả lời bằng tiếng Việt rõ ràng, súc tích, dễ hiểu, có gạch đầu dòng khoa học.
- Không chẩn đoán bệnh thay bác sĩ, không kê đơn thuốc cụ thể.
- Luôn giữ giọng điệu hỗ trợ, khách quan, chuẩn y khoa."""


def _fallback_rule_reply(q: str, context_note: str, use_profile: bool) -> str:
    """Dự phòng trả lời theo luật khi chưa cấu hình API Key hoặc lỗi mạng."""
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
        "Cảm ơn câu hỏi của bạn! Hiện tại tôi chưa kết nối được với khóa API AI nên đang trả lời theo chế độ chuẩn hóa. "
        "Bạn có thể hỏi về: **huyết áp, cholesterol, đường huyết, nhịp tim, chế độ ăn uống, vận động** hoặc chọn các gợi ý bên dưới." + context_note
    )


def _generate_safe_reply(prompt: str, use_profile: bool, history: list[dict]) -> str:
    """Kiểm soát an toàn 115 -> Gắn ngữ cảnh hồ sơ -> Gọi Gemini API (có dự phòng)."""
    q = prompt.lower().strip()

    # 1. Nhận diện khẩn cấp 115 trước khi gọi API
    if any(kw in q for kw in EMERGENCY_KEYWORDS):
        return (
            "🚨 **CẢNH BÁO KHẨN CẤP:** Các triệu chứng bạn vừa mô tả có thể liên quan đến tình trạng tim mạch cấp tính.\n\n"
            "- Hãy **gọi ngay Cấp cứu 115** hoặc nhờ người thân đưa tới bệnh viện gần nhất ngay lập tức.\n"
            "- Ngồi nghỉ yên tại chỗ, nới lỏng quần áo, không tự lái xe."
        )

    # 2. Lấy dữ liệu hồ sơ gần nhất nếu người dùng bật công tắc
    context_note = ""
    raw_context = "Người dùng không chia sẻ hồ sơ cá nhân."
    if use_profile:
        rows, _ = database.fetch_history()
        if rows:
            last = rows[-1]
            context_note = (
                f"\n\n📋 *Dựa trên lần đánh giá gần nhất của bạn ({last.get('patient_name', 'Hồ sơ')}):* "
                f"Huyết áp lúc nghỉ **{last.get('trestbps')} mmHg**, Cholesterol **{last.get('chol')} mg/dL**, "
                f"Điểm dự đoán AI **{last.get('risk_probability')}%** (Mức: **{last.get('risk_level')}**)."
            )
            raw_context = (
                f"Hồ sơ gần nhất ({last.get('patient_name', 'Hồ sơ')}): Tuổi {last.get('age')}, "
                f"Huyết áp nghỉ {last.get('trestbps')} mmHg, Cholesterol {last.get('chol')} mg/dL, "
                f"Nhịp tim tối đa {last.get('thalach')} bpm, Xác suất nguy cơ AI {last.get('risk_probability')}% ({last.get('risk_level')})."
            )
        else:
            raw_context = "Người dùng đã bật chia sẻ nhưng chưa có bản ghi đánh giá nào trong lịch sử."

    # 3. Gọi Gemini API bằng khóa trong .streamlit/secrets.toml
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return _fallback_rule_reply(q, context_note, use_profile)

    try:
        client = genai.Client(api_key=api_key)
        contents = []
        for m in history[-8:]:
            role = "user" if m["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

        res = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=f"{SYSTEM_PROMPT}\n\nDữ liệu người dùng: {raw_context}",
                temperature=0.4,
                max_output_tokens=800,
            ),
        )
        if res and res.text:
            return res.text
    except Exception:
        pass

    return _fallback_rule_reply(q, context_note, use_profile)


def render(bundle: dict):
    st.title("💬 Trợ lý AI & Kiến thức tim mạch")

    tab_chat, tab_lib, tab_metrics = st.tabs([
        "🤖 Trợ lý tư vấn AI",
        "📚 Thư viện bài viết tim mạch",
        "📖 Từ điển 11 chỉ số y khoa",
    ])

    # ==================== TAB 1: TRỢ LÝ AI ====================
    with tab_chat:
        c_tog, c_clr = st.columns([4, 1], vertical_alignment="center")
        use_prof = c_tog.toggle(
            "Cho phép Trợ lý AI tham khảo chỉ số gần nhất trong hồ sơ của tôi",
            value=True,
        )
        if c_clr.button("🗑️ Xóa chat", use_container_width=True):
            st.session_state.pop("chat_messages", None)
            st.rerun()

        st.session_state.setdefault("chat_messages", [
            {
                "role": "assistant",
                "content": "Xin chào! Tôi là **Trợ lý sức khỏe CardioScreen**. Tôi có thể giúp bạn giải thích chỉ số tim mạch, tư vấn lối sống lành mạnh hoặc tổng hợp hồ sơ gần nhất. Bạn muốn hỏi về vấn đề gì?",
            }
        ])

        # Hiển thị lịch sử trò chuyện
        for msg in st.session_state["chat_messages"]:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-bubble-