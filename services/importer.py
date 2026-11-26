"""Nhập dữ liệu xét nghiệm từ file CSV để điền sẵn form chẩn đoán.

Chấp nhận tên cột của bộ heart.csv (age, sex, cp, trestbps, ...) hoặc vài tên tiếng Việt phổ biến.
Chỉ lấy dòng cuối cùng của file. Không phân tích ảnh/PDF điện tâm đồ (chưa có mô hình kiểm định cho việc này).
"""
import pandas as pd

from services import validators

SYNONYMS = {
    "age": ["age", "tuoi", "tuổi"],
    "sex": ["sex", "gioi_tinh", "giới tính", "gender"],
    "cp": ["cp", "chest_pain", "loai_dau_nguc"],
    "trestbps": ["trestbps", "resting_bp", "huyet_ap", "huyết áp", "systolic"],
    "chol": ["chol", "cholesterol"],
    "fbs": ["fbs", "fasting_blood_sugar", "duong_huyet_doi"],
    "restecg": ["restecg", "resting_ecg"],
    "thalach": ["thalach", "max_heart_rate", "nhip_tim_toi_da", "nhịp tim tối đa"],
    "exang": ["exang", "exercise_angina"],
    "oldpeak": ["oldpeak"],
    "slope": ["slope"],
    "ca": ["ca"],
    "thal": ["thal"],
}
SEX_TEXT = {"nam": 1, "male": 1, "m": 1, "nữ": 0, "nu": 0, "female": 0, "f": 0}


def parse_lab_csv(file_obj) -> tuple[dict, list[str]]:
    """Trả về (giá trị nhận được, danh sách cảnh báo)."""
    warnings: list[str] = []
    try:
        df = pd.read_csv(file_obj)
    except Exception as e:
        return {}, [f"Không đọc được file CSV: {e}"]
    if df.empty:
        return {}, ["File CSV không có dòng dữ liệu nào."]
    row = df.iloc[-1]
    lower = {str(c).strip().lower(): c for c in df.columns}
    found: dict = {}
    for key, names in SYNONYMS.items():
        col = next((lower[n] for n in names if n in lower), None)
        if col is None:
            continue
        raw = row[col]
        if key == "sex" and isinstance(raw, str):
            raw = SEX_TEXT.get(raw.strip().lower(), raw)
        try:
            found[key] = float(raw) if key == "oldpeak" else int(float(raw))
        except (TypeError, ValueError):
            warnings.append(f"Bỏ qua cột '{col}': giá trị '{raw}' không phải số hợp lệ.")
    if not found:
        return {}, ["Không nhận ra cột nào. Dùng tên cột như age, trestbps, chol, thalach, oldpeak, ..."]
    # Bỏ các giá trị ngoài giới hạn để người dùng nhập lại thay vì đưa dữ liệu vô lý vào form.
    for key, (lo, hi, label) in validators.LIMITS.items():
        if key in found and not (lo <= found[key] <= hi):
            warnings.append(f"{label} = {found[key]} ngoài khoảng {lo}–{hi}, đã bỏ qua.")
            found.pop(key)
    for key, allowed in validators.CHOICES.items():
        if key in found and found[key] not in allowed:
            warnings.append(f"Giá trị '{key}' = {found[key]} không hợp lệ, đã bỏ qua.")
            found.pop(key)
    return found, warnings
