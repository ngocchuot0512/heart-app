"""Màn hình Đánh giá nguy cơ: Sàng lọc khẩn cấp 115, Form 4 bước có thanh tiến trình và giải thích chỉ số."""
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st

from services import risk_service, validators
from db import database
from ui.theme import disclaimer

SAMPLES = Path(__file__).resolve().parents[2] / "data" / "sample_patients.csv"

CP = {0: "Đau thắt ngực điển hình", 1: "Đau ngực không điển hình",
      2: "Đau ngực không do tim", 3: "Không triệu chứng"}
ECG = {0: "Bình thường", 1: "Bất thường sóng ST-T", 2: "Phì đại thất trái"}
SLOPE = {0: "Dốc lên (tốt)", 1: "Đi ngang", 2: "Dốc xuống"}
THAL = {0: "Không xác định", 1: "Khuyết tật cố định", 2: "Bình thường", 3: "Khuyết tật có thể phục hồi"}
SEX = {1: "Nam", 0: "Nữ"}
YN = {0: "Không", 1: "Có"}
SMOKE = ["Không hút", "Đã bỏ", "Đang hút"]
ACTIVITY = ["Ít vận động", "Vừa phải", "Thường xuyên"]
HISTORY = ["Không", "Có (bản thân)", "Có (gia đình)"]

# Kho dữ liệu giải thích chi tiết từng chỉ số theo yêu cầu mục 1.4 trong docx
METRIC_GUIDE = {
    "Huyết áp lúc nghỉ (trestbps)": {
        "what": "Áp lực máu tác động lên thành động mạch khi cơ thể ở trạng thái nghỉ ngơi (đơn vị: mmHg).",
        "ref": "Bình thường: < 120/80 mmHg · Tiền tăng huyết áp: 120–139 mmHg · Tăng huyết áp: ≥ 140 mmHg.",
        "factors": "Căng thẳng, ăn mặn, ít vận động, tuổi tác, hút thuốc hoặc bệnh lý thận.",
        "doctor": "Nên đi khám sớm nếu huyết áp lúc nghỉ thường xuyên ≥ 140/90 mmHg hoặc kèm đau đầu, chóng mặt.",
    },
    "Cholesterol toàn phần (chol)": {
        "what": "Tổng lượng mỡ cholesterol lưu hành trong máu (đơn vị: mg/dL).",
        "ref": "Mức mong muốn: < 200 mg/dL · Giới hạn cao: 200–239 mg/dL · Cao: ≥ 240 mg/dL.",
        "factors": "Chế độ ăn nhiều chất béo bão hòa, đồ chiên rán, thừa cân, di truyền.",
        "doctor": "Nên kiểm tra bộ mỡ máu chuyên sâu (LDL, HDL, Triglyceride) khi chỉ số ≥ 200 mg/dL.",
    },
    "Đường huyết lúc đói (fbs)": {
        "what": "Nồng độ đường glucose trong máu sau khi nhịn ăn ít nhất 8 giờ.",
        "ref": "Bình thường: < 100 mg/dL · Ngưỡng đánh dấu trong mô hình: > 120 mg/dL.",
        "factors": "Chế độ ăn nhiều tinh bột/đường, kháng insulin, ít vận động.",
        "doctor": "Đường huyết đói > 120–126 mg/dL cần khám nội tiết để tầm soát tiền đái tháo đường hoặc đái tháo đường.",
    },
    "Nhịp tim tối đa (thalach)": {
        "what": "Số nhịp tim cao nhất đạt được trong bài kiểm tra gắng sức (đơn vị: nhịp/phút - bpm).",
        "ref": "Ước tính tham khảo theo tuổi: khoảng (220 − Tuổi) bpm.",
        "factors": "Tuổi tác, thể lực, thuốc điều trị tim mạch (như thuốc chẹn beta).",
        "doctor": "Nhịp tim tăng quá chậm khi gắng sức hoặc kèm khó thở, choáng váng cần được bác sĩ tim mạch đánh giá.",
    },
    "Chênh đoạn ST (oldpeak) & Độ dốc ST (slope)": {
        "what": "Mức độ chênh xuống của đoạn ST trên điện tâm đồ khi gắng sức so với lúc nghỉ (đơn vị: mm).",
        "ref": "Bình thường: 0.0 – 1.0 mm, độ dốc hướng lên.",
        "factors": "Thiếu máu cơ tim cục bộ khi tim phải làm việc cường độ cao.",
        "doctor": "Oldpeak ≥ 2.0 mm hoặc đoạn ST dốc xuống là dấu hiệu quan trọng cần khám chuyên khoa tim mạch.",
    },
}

DEFAULTS = {
    "f_name": "Hồ sơ của tôi", "f_age": 55, "f_sex": 1, "f_height": 168, "f_weight": 65,
    "f_sys": 130, "f_dia": 80, "f_smoke": SMOKE[0], "f_act": ACTIVITY[1], "f_hist": HISTORY[0],
    "f_cp": 0, "f_trestbps": 130, "f_chol": 220, "f_fbs": 0, "f_restecg": 0, "f_thalach": 150,
    "f_exang": 0, "f_oldpeak": 0.0, "f_slope": 1, "f_ca": 0, "f_thal": 2,
}

FIELD_KEYS = {
    "age": "f_age", "sex": "f_sex", "cp": "f_cp", "trestbps": "f_trestbps", "chol": "f_chol",
    "fbs": "f_fbs", "restecg": "f_restecg", "thalach": "f_thalach", "exang": "f_exang",
    "oldpeak": "f_oldpeak", "slope": "f_slope", "ca": "f_ca", "thal": "f_thal",
}


def _persist(key: str):
    """Khóa chặt giá trị vào kho bền vững ngay khi người dùng thay đổi ô nhập."""
    if key in st.session_state:
        st.session_state["assess_data"][key] = st.session_state[key]


def _set_all_fields(updates: dict):
    """Cập nhật đồng bộ cả kho bền vững lẫn widget state."""
    st.session_state.setdefault("assess_data", dict(DEFAULTS))
    for k, v in updates.items():
        st.session_state["assess_data"][k] = v
        st.session_state[k] = v


def _sync_from_profile():
    """Tự động điền thông tin từ tab Hồ sơ sức khỏe nếu người dùng đã lưu."""
    updates = {}
    if st.session_state.get("profile_name"):
        updates["f_name"] = st.session_state["profile_name"]
    if "prof_birth_year" in st.session_state:
        updates["f_age"] = max(18, min(100, datetime.now().year - st.session_state["prof_birth_year"]))
    for src, dst in [("prof_sex", "f_sex"), ("prof_height", "f_height"), ("prof_weight", "f_weight"),
                     ("prof_smoke", "f_smoke"), ("prof_hist", "f_hist")]:
        if src in st.session_state:
            updates[dst] = st.session_state[src]
    _set_all_fields(updates)


def _load_sample():
    name = st.session_state.get("sample_pick")
    df = pd.read_csv(SAMPLES)
    row = df[df["name"] == name].iloc[0]
    m = {"f_name": "name", "f_age": "age", "f_sex": "sex", "f_height": "height_cm", "f_weight": "weight_kg",
         "f_sys": "systolic", "f_dia": "diastolic", "f_smoke": "smoking", "f_act": "activity",
         "f_hist": "cardio_history", "f_cp": "cp", "f_trestbps": "trestbps", "f_chol": "chol",
         "f_fbs": "fbs", "f_restecg": "restecg", "f_thalach": "thalach", "f_exang": "exang",
         "f_oldpeak": "oldpeak", "f_slope": "slope", "f_ca": "ca", "f_thal": "thal"}
    updates = {}
    for k, col in m.items():
        v = row[col]
        updates[k] = v if isinstance(v, str) else (float(v) if k == "f_oldpeak" else int(v))
    _set_all_fields(updates)


def render(bundle: dict):
    if "assess_data" not in st.session_state:
        st.session_state["assess_data"] = dict(DEFAULTS)
    data = st.session_state["assess_data"]

    for k in DEFAULTS:
        if k in st.session_state:
            data[k] = st.session_state[k]
        st.session_state[k] = data[k]

    st.session_state.setdefault("assess_step", 1)

    pre = st.session_state.pop("prefill", None)
    if pre:
        updates = {}
        if "_systolic" in pre:
            updates["f_sys"] = int(pre.pop("_systolic"))
            updates["f_trestbps"] = updates["f_sys"]
        for key, val in pre.items():
            updates[FIELD_KEYS[key]] = float(val) if key == "oldpeak" else int(val)
        _set_all_fields(updates)
        st.session_state["assess_step"] = 2

    st.title("🩺 Đánh giá nguy cơ tim mạch")

    # ---- BẮT BUỘC THEO MỤC 3 DOCX: SÀNG LỌC KHẨN CẤP 115 ----
    with st.expander("🚨 CẢNH BÁO KHẨN CẤP — Đọc trước khi nhập liệu", expanded=False):
        st.error(
            "**Nếu bạn hoặc người thân đang có một trong các dấu hiệu sau:**\n"
            "- Đau thắt ngực dữ dội, cảm giác bóp nghẹt hoặc đè nặng sau xương ức kéo dài > 5 phút\n"
            "- Khó thở đột ngột, vã mồ hôi lạnh, choáng váng hoặc ngất xỉu\n"
            "- Đau lan lên cổ, hàm, vai hoặc cánh tay trái\n\n"
            "👉 **KHÔNG tiếp tục điền biểu mẫu này. Hãy gọi ngay Cấp cứu 115 (Việt Nam) hoặc đến cơ sở y tế gần nhất!**"
        )

    # Thanh công cụ nạp nhanh dữ liệu mẫu / đồng bộ hồ sơ
    if SAMPLES.exists():
        names = pd.read_csv(SAMPLES)["name"].tolist()
        c1, c2, c3 = st.columns([2.4, 1, 1.2], vertical_alignment="bottom")
        c1.selectbox("Nạp bệnh nhân mẫu để kiểm thử nhanh", names, key="sample_pick")
        c2.button("Nạp mẫu", on_click=_load_sample, use_container_width=True)
        c3.button("Lấy từ Hồ sơ cá nhân", on_click=_sync_from_profile, use_container_width=True)

    # ---- THANH TIẾN TRÌNH 4 BƯỚC ----
    step = st.session_state["assess_step"]
    steps_title = [
        "Bước 1/4: Thông tin cơ bản",
        "Bước 2/4: Chỉ số sinh tồn & Xét nghiệm",
        "Bước 3/4: Triệu chứng & Thăm dò tim mạch",
        "Bước 4/4: Xác nhận dữ liệu & Phân tích",
    ]
    pct = int(step * 25)
    st.progress(step / 4, text=f"**{steps_title[step - 1]}** — Hoàn thành {pct}%")

    # ==================== BƯỚC 1: THÔNG TIN CƠ BẢN ====================
    if step == 1:
        with st.container(border=True):
            st.subheader("👤 Bước 1: Thông tin cơ bản & Thể trạng")
            c1, c2, c3 = st.columns(3)
            c1.text_input("Tên / mã hồ sơ *", key="f_name")
            c1.caption("Dùng để phân biệt các lần đo trong lịch sử.")
            c2.number_input("Tuổi (năm) *", 18, 100, key="f_age")
            c2.caption("Khoảng hợp lệ: 18 – 100 tuổi.")
            c3.selectbox("Giới tính sinh học *", list(SEX), format_func=SEX.get, key="f_sex")
            c3.caption("Yếu tố nền tảng trong mô hình dự đoán.")

            c4, c5, c6 = st.columns(3)
            c4.number_input("Chiều cao (cm) *", 120, 220, key="f_height")
            c4.caption("Đơn vị: centimet (120 – 220 cm).")
            c5.number_input("Cân nặng (kg) *", 30, 250, key="f_weight")
            c5.caption("Đơn vị: kilogram (30 – 250 kg).")
            bmi_now = validators.bmi(st.session_state["f_height"], st.session_state["f_weight"])
            c6.metric("Chỉ số BMI tạm tính", f"{bmi_now} kg/m²")

            st.markdown("##### Lối sống & Tiền sử (lưu theo dõi)")
            l1, l2, l3 = st.columns(3)
            l1.selectbox("Thói quen hút thuốc", SMOKE, key="f_smoke")
            l2.selectbox("Mức độ vận động", ACTIVITY, key="f_act")
            l3.selectbox("Tiền sử bệnh tim mạch", HISTORY, key="f_hist")

        _, col_next = st.columns([4, 1.2])
        if col_next.button("Tiếp tục ➔", type="primary", use_container_width=True):
            if not st.session_state["f_name"].strip():
                st.error("Vui lòng nhập Tên / mã hồ sơ trước khi tiếp tục.")
            else:
                st.session_state["assess_step"] = 2
                st.rerun()

    # ==================== BƯỚC 2: CHỈ SỐ SỨC KHỎE ====================
    elif step == 2:
        with st.container(border=True):
            st.subheader("❤️ Bước 2: Huyết áp & Chỉ số xét nghiệm máu")
            g, h, i = st.columns(3)
            g.number_input("Huyết áp tâm thu (mmHg)", 70, 250, key="f_sys", on_change=_persist, args=("f_sys",))
            g.caption("Số trên khi đo huyết áp (ví dụ: 120 mmHg).")
            h.number_input("Huyết áp tâm trương (mmHg)", 40, 150, key="f_dia", on_change=_persist, args=("f_dia",))
            h.caption("Số dưới khi đo huyết áp (ví dụ: 80 mmHg).")
            i.number_input("Huyết áp lúc nghỉ - trestbps (mmHg) *", 80, 220, key="f_trestbps", on_change=_persist, args=("f_trestbps",))
            i.caption("Đưa vào mô hình AI (thường bằng huyết áp tâm thu).")

            j, k, l = st.columns(3)
            j.number_input("Cholesterol toàn phần (mg/dL) *", 100, 600, key="f_chol", on_change=_persist, args=("f_chol",))
            j.caption("Bình thường < 200 mg/dL (giới hạn: 100–600).")
            k.selectbox("Đường huyết lúc đói > 120 mg/dL *", list(YN), format_func=YN.get, key="f_fbs", on_change=_persist, args=("f_fbs",))
            k.caption("Chọn 'Có' nếu đường huyết đói > 120 mg/dL.")
            l.number_input("Nhịp tim tối đa (bpm) *", 60, 220, key="f_thalach", on_change=_persist, args=("f_thalach",))
            l.caption("Nhịp tim cao nhất đạt được khi gắng sức.")

        # Hộp giải thích chi tiết từng chỉ số ngay trong trang nhập liệu (mục 1.4 docx)
        with st.expander("📖 Giải thích ý nghĩa các chỉ số & Khoảng tham chiếu"):
            topic = st.selectbox("Chọn chỉ số muốn tìm hiểu:", list(METRIC_GUIDE.keys()))
            info = METRIC_GUIDE[topic]
            st.markdown(
                f"- **Chỉ số này là gì?** {info['what']}\n"
                f"- **Khoảng tham chiếu:** {info['ref']}\n"
                f"- **Yếu tố ảnh hưởng:** {info['factors']}\n"
                f"- **Khi nào nên đi khám?** {info['doctor']}"
            )

        col_back, _, col_next = st.columns([1.2, 2.8, 1.2])
        if col_back.button("⬅ Quay lại", use_container_width=True):
            st.session_state["assess_step"] = 1
            st.rerun()
        if col_next.button("Tiếp tục ➔", type="primary", use_container_width=True):
            errs = validators.validate_lifestyle(
                st.session_state["f_height"], st.session_state["f_weight"],
                st.session_state["f_sys"], st.session_state["f_dia"]
            )
            if errs:
                for er in errs:
                    st.error(er)
            else:
                st.session_state["assess_step"] = 3
                st.rerun()

    # ==================== BƯỚC 3: TRIỆU CHỨNG & THĂM DÒ ====================
    elif step == 3:
        with st.container(border=True):
            st.subheader("🩺 Bước 3: Triệu chứng & Kết quả thăm dò chuyên khoa")
            m_, n_, o_ = st.columns(3)
            m_.selectbox("Loại đau ngực (cp) *", list(CP), format_func=CP.get, key="f_cp")
            m_.caption("Mô tả cảm giác đau/tức vùng ngực.")
            n_.selectbox("Điện tâm đồ lúc nghỉ (restecg) *", list(ECG), format_func=ECG.get, key="f_restecg")
            n_.caption("Kết quả đo ECG khi nghỉ ngơi.")
            o_.selectbox("Đau ngực khi gắng sức (exang) *", list(YN), format_func=YN.get, key="f_exang")
            o_.caption("Có xuất hiện đau thắt ngực khi vận động mạnh không.")

            p_, q_, r_ = st.columns(3)
            p_.number_input("Chênh đoạn ST - oldpeak (mm) *", 0.0, 7.0, step=0.1, format="%.1f", key="f_oldpeak")
            p_.caption("Mức chênh xuống đoạn ST khi gắng sức (0.0 – 7.0).")
            q_.selectbox("Độ dốc đoạn ST (slope) *", list(SLOPE), format_func=SLOPE.get, key="f_slope")
            q_.caption("Hướng của đoạn ST ở đỉnh gắng sức.")
            r_.selectbox("Số mạch chính nhuộm màu (ca) *", [0, 1, 2, 3, 4], key="f_ca")
            r_.caption("Số mạch vành chính thấy trên chụp huỳnh quang (0–4).")

            s_, _, _ = st.columns(3)
            s_.selectbox("Chỉ số Thalassemia (thal) *", list(THAL), format_func=THAL.get, key="f_thal")
            s_.caption("Kết quả xạ hình tưới máu cơ tim.")

        col_back, _, col_next = st.columns([1.2, 2.8, 1.2])
        if col_back.button("⬅ Quay lại", use_container_width=True):
            st.session_state["assess_step"] = 2
            st.rerun()
        if col_next.button("Xem lại & Xác nhận ➔", type="primary", use_container_width=True):
            st.session_state["assess_step"] = 4
            st.rerun()

    # ==================== BƯỚC 4: XÁC NHẬN DỮ LIỆU ====================
    else:
        with st.container(border=True):
            st.subheader("✅ Bước 4: Kiểm tra & Xác nhận thông tin trước khi phân tích")
            st.caption("Vui lòng rà soát lại các thông số bên dưới. Bạn có thể bấm 'Quay lại' để chỉnh sửa bất kỳ mục nào.")

            bmi_val = validators.bmi(st.session_state["f_height"], st.session_state["f_weight"])
            summary_rows = [
                ("Hồ sơ / Tuổi / Giới tính", f"{st.session_state['f_name']} · {st.session_state['f_age']} tuổi · {SEX[st.session_state['f_sex']]}"),
                ("Chiều cao / Cân nặng / BMI", f"{st.session_state['f_height']} cm · {st.session_state['f_weight']} kg · BMI {bmi_val}"),
                ("Huyết áp tâm thu / tâm trương", f"{st.session_state['f_sys']}/{st.session_state['f_dia']} mmHg (Lúc nghỉ: {st.session_state['f_trestbps']} mmHg)"),
                ("Cholesterol / Đường huyết đói", f"{st.session_state['f_chol']} mg/dL · Đường huyết > 120: {YN[st.session_state['f_fbs']]}"),
                ("Nhịp tim tối đa / Đau ngực gắng sức", f"{st.session_state['f_thalach']} bpm · Đau ngực gắng sức: {YN[st.session_state['f_exang']]}"),
                ("Loại đau ngực / Điện tâm đồ", f"{CP[st.session_state['f_cp']]} · {ECG[st.session_state['f_restecg']]}"),
                ("Oldpeak / Độ dốc ST / CA / Thal", f"{st.session_state['f_oldpeak']} mm · {SLOPE[st.session_state['f_slope']]} · CA={st.session_state['f_ca']} · {THAL[st.session_state['f_thal']]}"),
            ]
            st.dataframe(pd.DataFrame(summary_rows, columns=["Nhóm thông tin", "Giá trị đã nhập"]),
                         hide_index=True, use_container_width=True)

        col_back, _, col_submit = st.columns([1.2, 2.2, 1.8])
        if col_back.button("⬅ Quay lại chỉnh sửa", use_container_width=True):
            st.session_state["assess_step"] = 3
            st.rerun()

        if col_submit.button("🔎 Xác nhận & Đánh giá nguy cơ", type="primary", use_container_width=True):
            values = {
                "age": st.session_state["f_age"], "sex": st.session_state["f_sex"],
                "cp": st.session_state["f_cp"], "trestbps": st.session_state["f_trestbps"],
                "chol": st.session_state["f_chol"], "fbs": st.session_state["f_fbs"],
                "restecg": st.session_state["f_restecg"], "thalach": st.session_state["f_thalach"],
                "exang": st.session_state["f_exang"], "oldpeak": float(st.session_state["f_oldpeak"]),
                "slope": st.session_state["f_slope"], "ca": st.session_state["f_ca"],
                "thal": st.session_state["f_thal"],
            }
            errors = validators.validate_clinical(values) + validators.validate_lifestyle(
                st.session_state["f_height"], st.session_state["f_weight"],
                st.session_state["f_sys"], st.session_state["f_dia"]
            )
            if errors:
                for er in errors:
                    st.error(er)
                return

            with st.spinner("Mô hình SVM đang phân tích 13 chỉ số lâm sàng..."):
                result = risk_service.predict(bundle, values)
                bmi = validators.bmi(st.session_state["f_height"], st.session_state["f_weight"])
                st.session_state["last_result"] = {
                    "name": st.session_state["f_name"].strip(),
                    "values": values,
                    "result": result,
                    "bmi": bmi,
                    "extra": {
                        "height_cm": st.session_state["f_height"],
                        "weight_kg": st.session_state["f_weight"],
                        "systolic": st.session_state["f_sys"],
                        "diastolic": st.session_state["f_dia"],
                        "smoking": st.session_state["f_smoke"],
                        "activity": st.session_state["f_act"],
                        "cardio_history": st.session_state["f_hist"],
                    },
                }
                record = {
                    "patient_name": st.session_state["f_name"].strip(),
                    "age": int(values["age"]), "sex": SEX[values["sex"]],
                    "trestbps": int(values["trestbps"]), "chol": int(values["chol"]),
                    "thalach": int(values["thalach"]), "oldpeak": float(values["oldpeak"]),
                    "prediction_result": "Nhóm 1 - Có nguy cơ bệnh tim" if result["label"] else "Nhóm 0 - Không có nguy cơ",
                    "risk_probability": round(result["p1"] * 100, 2),
                    "risk_level": result["level"],
                    "height_cm": st.session_state["f_height"], "weight_kg": st.session_state["f_weight"],
                    "bmi": bmi, "systolic": st.session_state["f_sys"], "diastolic": st.session_state["f_dia"],
                    "smoking": st.session_state["f_smoke"], "activity": st.session_state["f_act"],
                    "cardio_history": st.session_state["f_hist"],
                    "inputs": {k: (float(v) if k == "oldpeak" else int(v)) for k, v in values.items()},
                }
                ok, msg = database.save_assessment(record)
                st.session_state["save_status"] = (ok, msg)
                st.session_state["assess_step"] = 1
                st.session_state["goto"] = "Đánh giá"
                st.session_state["diag_view"] = "result"
                st.rerun()

    disclaimer()