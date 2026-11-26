"""Nghiệp vụ đánh giá nguy cơ: nạp mô hình, dự đoán, phân mức, giải thích."""
from pathlib import Path
import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent.parent / "ml" / "pipeline.pkl"

# Ngưỡng phân mức dựa trên xác suất của mô hình (quy ước của ứng dụng, KHÔNG phải ngưỡng lâm sàng).
LOW_MAX, MID_MAX = 0.35, 0.65

FEATURE_LABELS = {
    "age": "Tuổi", "sex": "Giới tính", "cp": "Loại đau ngực",
    "trestbps": "Huyết áp lúc nghỉ", "chol": "Cholesterol", "fbs": "Đường huyết đói",
    "restecg": "Điện tâm đồ", "thalach": "Nhịp tim tối đa", "exang": "Đau ngực khi gắng sức",
    "oldpeak": "Chênh đoạn ST (oldpeak)", "slope": "Độ dốc đoạn ST",
    "ca": "Số mạch chính (CA)", "thal": "Thal",
}


def load_bundle(path: Path = MODEL_PATH) -> dict:
    """Nạp bundle {pipeline, columns, reference, importance, ...}. Gọi qua st.cache_resource ở UI."""
    if not path.exists():
        raise FileNotFoundError("Chưa có ml/pipeline.pkl. Hãy chạy: python ml/train.py")
    return joblib.load(path)


def risk_level(p: float) -> tuple[str, str]:
    """(nhãn, khóa màu) theo xác suất nhóm 1."""
    if p < LOW_MAX:
        return "Thấp", "low"
    if p < MID_MAX:
        return "Trung bình", "mid"
    return "Cao", "high"


def predict(bundle: dict, values: dict) -> dict:
    cols = bundle["columns"]
    X = pd.DataFrame([{c: values[c] for c in cols}])[cols]  # đúng thứ tự cột lúc huấn luyện
    pipe = bundle["pipeline"]
    p1 = float(pipe.predict_proba(X)[0][list(pipe.classes_).index(1)])
    label, key = risk_level(p1)
    return {"p1": p1, "p0": 1 - p1, "label": int(p1 >= 0.5), "level": label, "level_key": key,
            "contrib": explain(bundle, X)}


def explain(bundle: dict, X: pd.DataFrame) -> list[dict]:
    """Giải thích cục bộ: thay từng chỉ số bằng giá trị tham chiếu (trung vị tập huấn luyện) và
    đo mức thay đổi xác suất. delta > 0: chỉ số này đang ĐẨY nguy cơ lên so với mức tham chiếu."""
    pipe, ref = bundle["pipeline"], bundle["reference"]
    base = pipe.predict_proba(X)[0][1]
    out = []
    for c in bundle["columns"]:
        Xr = X.copy()
        Xr[c] = ref[c]
        delta = float(base - pipe.predict_proba(Xr)[0][1])
        out.append({"feature": c, "label": FEATURE_LABELS[c], "value": float(X[c].iloc[0]), "delta": delta})
    return sorted(out, key=lambda d: -abs(d["delta"]))


def recommendations(level_key: str) -> list[str]:
    """Khuyến nghị chung, không mang tính kê đơn."""
    base = ["Duy trì vận động vừa phải đều đặn (khoảng 150 phút/tuần nếu bác sĩ cho phép).",
            "Ăn nhiều rau quả, hạn chế muối, chất béo bão hòa và đồ chế biến sẵn.",
            "Không hút thuốc; hạn chế rượu bia; ngủ đủ giấc."]
    if level_key == "low":
        return base + ["Kiểm tra sức khỏe định kỳ hằng năm."]
    if level_key == "mid":
        return ["Nên đặt lịch khám tim mạch để được đánh giá đầy đủ."] + base
    return ["Hãy đến cơ sở y tế để được thăm khám sớm; ứng dụng này không thay thế chẩn đoán.",
            "Nếu đau ngực, khó thở, choáng váng đột ngột: gọi cấp cứu (115) ngay."] + base
