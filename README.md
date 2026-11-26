# CardioScreen – Hỗ trợ sàng lọc nguy cơ tim mạch (Streamlit + SVM + Supabase)

## Chạy (cần Streamlit >= 1.39)
1. `pip install -r requirements.txt`
2. Chạy `db/schema.sql` trong Supabase SQL Editor (bảng + RLS).
3. Sao chép `.streamlit/secrets.toml.example` thành `.streamlit/secrets.toml`, điền URL và publishable key.
4. (Tùy chọn) huấn luyện lại: `python ml/train.py` – đã có sẵn `ml/pipeline.pkl` (scikit-learn 1.9.1).
5. `streamlit run app.py`

## Cấu trúc
- `ui/` giao diện (theme, biểu đồ, 5 màn hình + đăng nhập) · `services/` nghiệp vụ & kiểm tra dữ liệu
- `ml/` huấn luyện, pipeline, báo cáo · `db/` Supabase + schema · `data/` heart.csv, dữ liệu mẫu
