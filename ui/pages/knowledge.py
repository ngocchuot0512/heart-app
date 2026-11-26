"""Kho giải thích chi tiết các chỉ số sức khỏe và thư viện kiến thức tim mạch chuẩn hóa."""

METRIC_GUIDE = {
    "trestbps": {
        "name": "Huyết áp lúc nghỉ (mmHg)",
        "what": "Là áp lực của dòng máu tác động lên thành động mạch khi tim bơm máu đi và khi tim nghỉ ngơi ở trạng thái thư giãn.",
        "meaning": "Huyết áp cao kéo dài làm tăng gánh nặng cho tim và gây tổn thương nội mạc mạch máu, thúc đẩy xơ vữa động mạch.",
        "reference": "Bình thường: < 120/80 mmHg · Tiền tăng huyết áp: 120–139 / 80–89 mmHg · Tăng huyết áp: ≥ 140/90 mmHg.",
        "factors": "Căng thẳng, ăn mặn, thiếu ngủ, hút thuốc lá, uống cà phê/rượu bia ngay trước khi đo.",
        "when_doctor": "Khi huyết áp đo nhiều lần ≥ 140/90 mmHg hoặc tăng vọt ≥ 180/120 mmHg kèm đau đầu, mờ mắt, đau ngực.",
    },
    "chol": {
        "name": "Cholesterol toàn phần (mg/dL)",
        "what": "Tổng lượng cholesterol (bao gồm LDL 'xấu', HDL 'tốt' và một phần triglyceride) lưu hành trong máu.",
        "meaning": "Cholesterol dư thừa lắng đọng trên thành động mạch vành tạo thành mảng xơ vữa, làm hẹp lòng mạch nuôi tim.",
        "reference": "Mong muốn: < 200 mg/dL · Giới hạn cao: 200–239 mg/dL · Cao: ≥ 240 mg/dL.",
        "factors": "Chế độ ăn nhiều mỡ bão hòa, nội tạng động vật, ít vận động, yếu tố di truyền gia đình.",
        "when_doctor": "Khi chỉ số ≥ 200 mg/dL, nên làm xét nghiệm bộ mỡ máu đầy đủ (LDL-C, HDL-C, Triglyceride) để bác sĩ tư vấn.",
    },
    "fbs": {
        "name": "Đường huyết lúc đói (> 120 mg/dL)",
        "what": "Nồng độ đường (glucose) trong máu sau khi nhịn ăn ít nhất 8 giờ.",
        "meaning": "Đường huyết cao mạn tính làm tổn thương mạch máu nhỏ và lớn, tăng gấp đôi nguy cơ bệnh mạch vành.",
        "reference": "Bình thường: < 100 mg/dL · Tiền đái tháo đường: 100–125 mg/dL · Nghi ngờ đái tháo đường: ≥ 126 mg/dL.",
        "factors": "Ăn uống trước giờ lấy máu, chế độ ăn nhiều tinh bột/đường, thừa cân, căng thẳng.",
        "when_doctor": "Khi đường huyết đói thường xuyên > 120–126 mg/dL hoặc kèm khát nước nhiều, tiểu nhiều, sụt cân.",
    },
    "thalach": {
        "name": "Nhịp tim tối đa khi gắng sức (bpm)",
        "what": "Số nhịp tim cao nhất đạt được trong bài kiểm tra gắng sức (chạy thảm lăn hoặc đạp xe).",
        "meaning": "Phản ánh khả năng đáp ứng của tim khi cơ thể cần nhiều oxy. Không đạt được nhịp tim mục tiêu có thể gợi ý suy giảm chức năng tim.",
        "reference": "Ước tính nhịp tim tối đa theo tuổi ≈ 220 − Tuổi (ví dụ: 50 tuổi khoảng 170 bpm).",
        "factors": "Tuổi tác, mức độ rèn luyện thể lực, thuốc chẹn beta đang sử dụng.",
        "when_doctor": "Khi tim đập quá nhanh bất thường, loạn nhịp hoặc hụt hơi sớm khi mới vận động nhẹ.",
    },
    "cp": {
        "name": "Loại đau ngực",
        "what": "Phân loại tính chất cơn đau vùng ngực dựa trên triệu chứng lâm sàng.",
        "meaning": "Đau thắt ngực điển hình (cảm giác bóp nghẹt sau xương ức, tăng khi gắng sức, giảm khi nghỉ) là dấu hiệu đặc trưng của thiếu máu cơ tim.",
        "reference": "0: Đau thắt ngực điển hình · 1: Đau ngực không điển hình · 2: Đau ngực không do tim · 3: Không triệu chứng.",
        "factors": "Vận động mạnh, xúc động mạnh, thời tiết lạnh, hoặc các bệnh lý dạ dày – cơ xương khớp vùng ngực.",
        "when_doctor": "Khám ngay nếu đau ngực xuất hiện khi gắng sức; gọi cấp cứu 115 nếu đau dữ dội lan lên hàm, vai hoặc tay trái.",
    },
    "restecg": {
        "name": "Điện tâm đồ lúc nghỉ (ECG)",
        "what": "Ghi lại hoạt động điện học của tim khi bạn nằm nghỉ yên.",
        "meaning": "Giúp phát hiện dày thành cơ tim (phì đại thất trái) hoặc dấu hiệu thiếu máu cơ tim thầm lặng qua sóng ST-T.",
        "reference": "0: Bình thường · 1: Bất thường sóng ST-T · 2: Phì đại thất trái.",
        "factors": "Tăng huyết áp lâu năm, rối loạn điện giải, bệnh van tim.",
        "when_doctor": "Bất kỳ kết quả điện tâm đồ bất thường nào cũng cần bác sĩ tim mạch đọc trực tiếp trên bản ghi ECG.",
    },
    "exang": {
        "name": "Đau ngực khi gắng sức",
        "what": "Tình trạng xuất hiện cơn đau hoặc tức nặng ngực khi đi bộ nhanh, leo cầu thang hoặc làm việc nặng.",
        "meaning": "Khi gắng sức, cơ tim cần nhiều máu hơn; nếu động mạch vành bị hẹp, cơ tim bị thiếu oxy gây đau.",
        "reference": "0: Không đau · 1: Có đau ngực khi gắng sức.",
        "factors": "Cường độ vận động, mức độ hẹp mạch vành.",
        "when_doctor": "Nên đi khám chuyên khoa tim mạch sớm để làm nghiệm pháp gắng sức hoặc chụp mạch kiểm tra.",
    },
    "oldpeak": {
        "name": "Oldpeak – Độ chênh xuống đoạn ST",
        "what": "Mức độ đoạn ST trên điện tâm đồ hạ thấp xuống (tính bằng mm) khi gắng sức so với lúc nghỉ.",
        "meaning": "Đoạn ST chênh xuống càng sâu thì mức độ thiếu máu cơ tim khi gắng sức càng đáng kể.",
        "reference": "Bình thường: 0.0 – 0.5 mm · Đáng lưu ý: ≥ 1.0 – 2.0 mm.",
        "factors": "Lấy trực tiếp từ phiếu kết quả nghiệm pháp gắng sức tại bệnh viện.",
        "when_doctor": "Khi giá trị từ 1.0 mm trở lên kèm theo đau ngực hoặc mệt mỏi khi gắng sức.",
    },
    "slope": {
        "name": "Độ dốc đoạn ST đỉnh gắng sức",
        "what": "Hình dạng hướng đi của đoạn ST trên điện tâm đồ tại thời điểm gắng sức cao nhất.",
        "meaning": "Đoạn ST đi ngang hoặc dốc xuống thường liên quan chặt chẽ hơn tới thiếu máu cục bộ cơ tim.",
        "reference": "0: Dốc lên (thường lành tính) · 1: Đi ngang · 2: Dốc xuống.",
        "factors": "Được xác định bởi bác sĩ tim mạch khi đọc nghiệm pháp gắng sức.",
        "when_doctor": "Khi kết quả ghi nhận đoạn ST đi ngang hoặc dốc xuống.",
    },
    "ca": {
        "name": "Số mạch máu chính (CA: 0–4)",
        "what": "Số lượng nhánh động mạch vành lớn quan sát thấy trên phim chụp mạch huỳnh quang.",
        "meaning": "Là chỉ số hình ảnh chuyên sâu phản ánh tình trạng tưới máu mạch vành.",
        "reference": "Giá trị từ 0 đến 4 theo kết quả chẩn đoán hình ảnh.",
        "factors": "Chỉ có được khi người bệnh đã thực hiện thủ thuật chụp mạch tại cơ sở y tế.",
        "when_doctor": "Luôn trao đổi trực tiếp với bác sĩ tim mạch can thiệp nếu bạn có phim chụp mạch vành.",
    },
    "thal": {
        "name": "Xạ hình tưới máu cơ tim (Thal)",
        "what": "Kết quả đánh giá lưu lượng máu tới cơ tim thông qua kỹ thuật chuyên sâu.",
        "meaning": "Giúp phân biệt vùng cơ tim tưới máu bình thường, vùng thiếu máu hồi phục được hay vùng sẹo nhồi máu cũ.",
        "reference": "1: Khuyết tật cố định · 2: Bình thường · 3: Khuyết tật có thể phục hồi.",
        "factors": "Tiền sử nhồi máu cơ tim hoặc hẹp động mạch vành.",
        "when_doctor": "Khi kết quả ghi nhận khuyết tật tưới máu (mức 1 hoặc 3).",
    },
}

ARTICLES = [
    {
        "category": "Phòng ngừa & Đo lường",
        "title": "Hướng dẫn đo huyết áp tại nhà đúng chuẩn y khoa",
        "read_time": "3 phút đọc",
        "summary": "Đo sai tư thế hoặc đo ngay sau khi uống cà phê có thể làm huyết áp tăng giả tạo 10–20 mmHg.",
        "content": """
**1. Chuẩn bị trước khi đo 30 phút:**
- Không hút thuốc lá, không uống cà phê, trà đặc hoặc rượu bia.
- Không vận động mạnh; đi vệ sinh trước khi đo (bàng quang đầy làm tăng huyết áp).

**2. Tư thế ngồi chuẩn:**
- Ngồi tựa lưng thẳng vào ghế, hai bàn chân đặt phẳng trên sàn nhà (không vắt chéo chân).
- Nghỉ ngơi yên tĩnh ít nhất **5 phút** trước khi bấm máy.
- Đặt cánh tay lên bàn sao cho vòng bít ngang mức với tim.

**3. Cách ghi nhận kết quả:**
- Đo 2 lần cách nhau 1–2 phút và lấy giá trị trung bình.
- Nên đo vào cùng một khung giờ mỗi ngày (buổi sáng sau khi thức dậy và buổi tối trước khi ngủ).
        """,
    },
    {
        "category": "Dinh dưỡng tim mạch",
        "title": "Chế độ ăn DASH & Địa Trung Hải bảo vệ thành mạch",
        "read_time": "4 phút đọc",
        "summary": "Giảm muối xuống dưới 5g/ngày và ưu tiên chất béo không bão hòa giúp hạ huyết áp tự nhiên.",
        "content": """
**Nguyên tắc vàng cho trái tim khỏe:**
- **Giảm muối (Natri):** Hạn chế nước mắm, đồ kho mặn, thực phẩm đóng hộp, mì ăn liền. Mục tiêu < 5g muối/ngày (khoảng 1 thìa cà phê gạt).
- **Tăng chất xơ hòa tan:** Ăn nhiều rau xanh, trái cây tươi, yến mạch, các loại đậu giúp giảm hấp thu cholesterol xấu (LDL).
- **Chọn chất béo tốt:** Ưu tiên cá béo (cá hồi, cá thu, cá trích) 2 bữa/tuần, dầu ô-liu, quả bơ, các loại hạt; hạn chế mỡ động vật và đồ chiên rán ngập dầu.
- **Hạn chế đường tinh luyện:** Tránh nước ngọt có ga và bánh kẹo công nghiệp.
        """,
    },
    {
        "category": "Dấu hiệu cảnh báo",
        "title": "Nhận biết sớm cơn đau thắt ngực và khi nào cần gọi 115",
        "read_time": "3 phút đọc",
        "summary": "Phân biệt đau ngực do tim với đau cơ xương khớp và quy tắc 'thời gian vàng' cấp cứu.",
        "content": """
**Dấu hiệu cảnh báo nhồi máu cơ tim cấp:**
- Cảm giác đè nặng, thắt chặt, bóp nghẹt hoặc nóng rát ở vùng giữa ngực kéo dài trên vài phút.
- Cơn đau có thể lan lên cổ, hàm dưới, vai trái hoặc mặt trong cánh tay trái.
- Kèm theo khó thở, vã mồ hôi lạnh, buồn nôn, choáng váng hoặc muốn ngất.

**Hành động khẩn cấp:**
- **Gọi ngay Cấp cứu 115** hoặc nhờ người thân đưa đến cơ sở y tế gần nhất có khả năng can thiệp tim mạch.
- Ngừng mọi hoạt động, ngồi hoặc nằm ở tư thế nửa nằm nửa ngồi dễ thở nhất, nới lỏng quần áo.
- Tuyệt đối không tự lái xe đến bệnh viện.
        """,
    },
    {
        "category": "Vận động thể chất",
        "title": "Tập thể dục bao nhiêu là đủ và an toàn cho người có nguy cơ?",
        "read_time": "4 phút đọc",
        "summary": "Khuyến nghị 150 phút vận động cường độ vừa mỗi tuần theo Tổ chức Y tế Thế giới (WHO).",
        "content": """
**Mức vận động khuyến nghị:**
- Tối thiểu **150 phút/tuần** vận động nhịp điệu cường độ vừa (đi bộ nhanh, đạp xe chậm, bơi lội) — tương đương 30 phút/ngày, 5 ngày/tuần.
- Kết hợp 2 buổi tập tăng cường sức mạnh cơ bắp nhẹ nhàng.

**Quy tắc an toàn:**
- Luôn khởi động 5–10 phút trước khi tập và thả lỏng sau khi tập.
- **Dừng tập ngay lập tức** nếu thấy tức ngực, chóng mặt, hụt hơi quá mức hoặc tim đập loạn nhịp.
- Nếu bạn từng có bệnh tim hoặc huyết áp cao chưa kiểm soát, hãy hỏi ý kiến bác sĩ trước khi bắt đầu bài tập mới.
        """,
    },
]