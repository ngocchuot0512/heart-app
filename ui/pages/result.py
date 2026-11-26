"""Màn hình Kết quả đánh giá: Biểu đồ trung tâm, giải thích yếu tố ảnh hưởng, khuyến nghị & xuất báo cáo."""
from datetime import datetime
import pandas as pd
import streamlit as st

from services import risk_service
from ui.theme import LEVEL_COLOR, card, contributions_html, disclaimer, gauge_html, level_pill


def _notables(last: dict) -> list[tuple[str, str, str]]:
    v, ex = last["values"], last["extra"]
    out = []
    if ex["systolic"] >= 140 or ex["diastolic"] >= 90:
        out.append(("Huyết áp", f'{ex["systolic"]}/{ex["diastolic"]} mmHg', "Cao hơn mốc tham khảo 140/90 mmHg"))
    if v["chol"] >= 240:
        out.append(("Cholesterol", f'{v["chol"]} mg/dL', "Từ 240 mg/dL trở lên được xem là cao"))
    elif v["chol"] >= 200:
        out.append(("Cholesterol", f'{v["chol"]} mg/dL', "Mức giới hạn cao (200–239 mg/dL)"))
    if last["bmi"] >= 25:
        out.append(("BMI", f"{last['bmi']} kg/m²", "Từ 25 trở lên là thừa cân (mốc phổ biến)"))
    elif last["bmi"] < 18.5:
        out.append(("BMI", f"{last['bmi']} kg/m²", "Dưới 18,5 là thiếu cân"))
    if v["fbs"] == 1:
        out.append(("Đường huyết đói", "> 120 mg/dL", "Cao hơn ngưỡng bình thường, nên kiểm tra thêm"))
    if v["exang"] == 1:
        out.append(("Đau ngực khi gắng sức", "Có", "Triệu chứng tim mạch cần lưu ý"))
    if v["oldpeak"] >= 2.0:
        out.append(("Chênh đoạn ST (oldpeak)", f'{v["oldpeak"]} mm', "Chênh xuống đáng kể khi gắng sức"))
    if ex["smoking"] == "Đang hút":
        out.append(("Hút thuốc", "Đang hút", "Yếu tố nguy cơ tim mạch quan trọng"))
    if ex["activity"] == "Ít vận động":
        out.append(("Vận động", "Ít", "Nên tăng dần thời lượng vận động mỗi ngày"))
    return out


def _plain_explanation(level_key: str) -> str:
    if level_key == "low":
        return (
            "Các thông số lâm sàng bạn nhập hiện đang gần với nhóm ít có dấu hiệu nguy cơ tim mạch trong dữ liệu mô hình. "
            "Tuy nhiên, bạn vẫn nên duy trì lối sống lành mạnh và kiểm tra sức khỏe định kỳ."
        )
    if level_key == "mid":
        return (
            "Một số chỉ số đầu vào của bạn nằm ở vùng cần theo dõi. Mô hình ghi nhận mức nguy cơ trung bình — "
            "bạn nên chủ động theo dõi huyết áp, mỡ máu và trao đổi thêm với bác sĩ để được tư vấn cụ thể."
        )
    return (
        "Nhiều thông số đầu vào của bạn tương đồng với nhóm có nguy cơ cao trong tập dữ liệu huấn luyện. "
        "Bạn nên sắp xếp đến cơ sở y tế chuyên khoa tim mạch để được bác sĩ thăm khám và làm xét nghiệm chuyên sâu."
    )


def _build_report_html(last: dict) -> str:
    r = last["result"]
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    tips_html = "".join(f"<li>{t}</li>" for t in risk_service.recommendations(r["level_key"]))
    return f"""<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8"><title>Báo cáo sàng lọc CardioScreen</title>
<style>
  body {{ font-family: Arial, sans-serif; color: #0F2942; max-width: 760px; margin: 24px auto; line-height: 1.5; }}
  .hdr {{ border-bottom: 3px solid #0D9488; padding-bottom: 12px; margin-bottom: 20px; }}
  .box {{ background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 10px; padding: 16px; margin-bottom: 16px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
  td, th {{ border: 1px solid #E2E8F0; padding: 8px; text-align: left; }}
  .warn {{ background: #FEF2F2; border-left: 4px solid #DC2626; padding: 12px; font-size: 13px; }}
</style></head><body>
<div class="hdr"><h2>BÁO CÁO KẾT QUẢ SÀNG LỌC NGUY CƠ TIM MẠCH (AI)</h2>
<p>Hồ sơ: <b>{last['name']}</b> · Ngày xuất báo cáo: {now_str}</p></div>
<div class="box"><h3>Kết quả dự đoán từ mô hình SVM</h3>
<p>Điểm xác suất nhóm 1: <b>{r['p1']*100:.1f}%</b> · Mức phân loại ứng dụng: <b>{r['level']}</b></p>
<p>{_plain_explanation(r['level_key'])}</p></div>
<h3>Thông số lâm sàng đã nhập</h3>
<table><tr><th>Chỉ số</th><th>Giá trị</th><th>Chỉ số</th><th>Giá trị</th></tr>
<tr><td>Tuổi</td><td>{last['values']['age']}</td><td>Huyết áp lúc nghỉ</td><td>{last['values']['trestbps']} mmHg</td></tr>
<tr><td>Cholesterol</td><td>{last['values']['chol']} mg/dL</td><td>Nhịp tim tối đa</td><td>{last['values']['thalach']} bpm</td></tr>
<tr><td>Oldpeak</td><td>{last['values']['oldpeak']} mm</td><td>BMI</td><td>{last['bmi']} kg/m²</td></tr></table>
<h3>Khuyến nghị chăm sóc sức khỏe</h3><ul>{tips_html}</ul>
<div class="warn"><b>Tuyên bố miễn trừ trách nhiệm:</b> Đây là kết quả dự đoán hỗ trợ sàng lọc từ mô hình học máy,
<b>KHÔNG phải kết luận chẩn đoán y khoa của bác sĩ</b>. Vui lòng mang theo các chỉ số xét nghiệm gốc khi đi khám.</div>
</body></html>"""


def render(bundle: dict):
    last = st.session_state.get("last_result")
    st.title("📊 Kết quả đánh giá nguy cơ")
    if not last:
        st.info("Chưa có kết quả. Hãy thực hiện một lần đánh giá ở mục **Đánh giá**.")
        return

    status = st.session_state.pop("save_status", None)
    if status:
        (st.toast if status[0] else st.warning)(status[1])

    r = last["result"]
    color = LEVEL_COLOR[r["level_key"]]
    st.markdown(
        f"Hồ sơ: **{last['name']}** · Mức nguy cơ theo mô hình: {level_pill(r['level'], color)}",
        unsafe_allow_html=True,
    )
    st.write("")

    left, right = st.columns([1, 1.25], gap="large")
    with left:
        st.markdown(gauge_html(r["p1"], color), unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            card("Điểm dự đoán (Nhóm 1)", f'{r["p1"]*100:.1f}%', "xác suất từ mô hình SVM")
        with c2:
            card("Mức đánh giá", r["level"], "theo ngưỡng quy ước ứng dụng")

        st.info(f"**Nhận xét từ hệ thống:** {_plain_explanation(r['level_key'])}")
        st.caption(
            f"Quy ước phân mức: Thấp < {risk_service.LOW_MAX:.0%}, Trung bình {risk_service.LOW_MAX:.0%}–"
            f"{risk_service.MID_MAX:.0%}, Cao ≥ {risk_service.MID_MAX:.0%}. "
            "Xác suất này là đầu ra của mô hình học máy trên tập dữ liệu mẫu, không phải xác suất mắc bệnh lâm sàng."
        )

    with right:
        st.subheader("Yếu tố ảnh hưởng nhiều nhất")
        st.markdown(contributions_html(r["contrib"]), unsafe_allow_html=True)
        st.caption(
            "Cách tính: thay từng chỉ số bằng giá trị trung vị của tập huấn luyện để đo mức thay đổi điểm dự đoán. "
            "Thanh đỏ/cam: đẩy nguy cơ lên; thanh xanh teal: kéo nguy cơ xuống."
        )

    st.subheader("Chỉ số đầu vào đáng chú ý")
    notes = _notables(last)
    if notes:
        st.dataframe(pd.DataFrame(notes, columns=["Chỉ số", "Giá trị", "Ghi chú tham khảo"]),
                     hide_index=True, use_container_width=True)
    else:
        st.success("Không có chỉ số nào vượt các mốc tham khảo phổ biến trong dữ liệu bạn nhập.")

    st.subheader("Đề xuất hành động & Khuyến nghị")
    for tip in risk_service.recommendations(r["level_key"]):
        st.markdown(f"- {tip}")

    m = bundle["test_metrics"]
    with st.expander("🔍 Xem chi tiết độ tin cậy & Giới hạn của mô hình AI"):
        st.markdown(
            f"- Thuật toán sử dụng: **Support Vector Machine (SVM - RBF)**, huấn luyện trên **{bundle['n_samples']}** mẫu duy nhất.\n"
            f"- Hiệu năng kiểm thử ({bundle['n_test']} mẫu): Accuracy **{m['Accuracy (%)']}%**, "
            f"Recall **{m['Recall (%)']}%**, ROC-AUC **{m['ROC-AUC']}**.\n"
            "- **Giới hạn:** Dữ liệu huấn luyện lấy từ bộ Heart Disease (UCI/Kaggle), chưa được hiệu chuẩn lâm sàng trên người Việt Nam."
        )

    disclaimer()
    st.write("")

    # Các nút điều hướng & xuất báo cáo theo mục 2.5 docx
    b1, b2, b3 = st.columns(3)
    b1.button("🔄 Đánh giá mới", type="primary", use_container_width=True,
              on_click=lambda: st.session_state.update(diag_view="form", assess_step=1))
    b2.button("📈 Xem lịch sử theo dõi", use_container_width=True,
              on_click=lambda: st.session_state.update(goto="Lịch sử"))
    b3.download_button(
        "📄 Tải báo cáo (Mở in PDF)",
        data=_build_report_html(last).encode("utf-8"),
        file_name=f"bao_cao_tim_mach_{last['name'].replace(' ', '_')}.html",
        mime="text/html",
        use_container_width=True,
    )