"""Kiểm tra dữ liệu đầu vào: trả về danh sách lỗi (rỗng nghĩa là hợp lệ)."""

# (min, max, nhãn) – giới hạn sinh lý hợp lý, chặn dữ liệu vô lý trước khi vào mô hình.
LIMITS = {
    "age": (18, 100, "Tuổi"),
    "trestbps": (80, 220, "Huyết áp lúc nghỉ"),
    "chol": (100, 600, "Cholesterol"),
    "thalach": (60, 220, "Nhịp tim tối đa"),
    "oldpeak": (0.0, 7.0, "Oldpeak"),
}
CHOICES = {"sex": {0, 1}, "cp": {0, 1, 2, 3}, "fbs": {0, 1}, "restecg": {0, 1, 2},
           "exang": {0, 1}, "slope": {0, 1, 2}, "ca": {0, 1, 2, 3, 4}, "thal": {0, 1, 2, 3}}
REQUIRED = list(LIMITS) + list(CHOICES)


def validate_clinical(values: dict) -> list[str]:
    errors = []
    for key in REQUIRED:
        if values.get(key) is None:
            errors.append(f"Thiếu thông tin: {key}")
    if errors:
        return errors
    for key, (lo, hi, label) in LIMITS.items():
        v = values[key]
        if not (lo <= v <= hi):
            errors.append(f"{label} phải nằm trong khoảng {lo}–{hi} (đang nhập {v}).")
    for key, allowed in CHOICES.items():
        if values[key] not in allowed:
            errors.append(f"Giá trị không hợp lệ cho {key}.")
    return errors


def validate_lifestyle(height_cm, weight_kg, systolic, diastolic) -> list[str]:
    errors = []
    if not 120 <= height_cm <= 220:
        errors.append("Chiều cao phải trong khoảng 120–220 cm.")
    if not 30 <= weight_kg <= 250:
        errors.append("Cân nặng phải trong khoảng 30–250 kg.")
    if not 70 <= systolic <= 250:
        errors.append("Huyết áp tâm thu phải trong khoảng 70–250 mmHg.")
    if not 40 <= diastolic <= 150:
        errors.append("Huyết áp tâm trương phải trong khoảng 40–150 mmHg.")
    if diastolic >= systolic:
        errors.append("Huyết áp tâm trương phải thấp hơn tâm thu.")
    return errors


def bmi(height_cm: float, weight_kg: float) -> float:
    return round(weight_kg / (height_cm / 100) ** 2, 1)
