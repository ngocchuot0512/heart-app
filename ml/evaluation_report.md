# Báo cáo đánh giá mô hình

**Dữ liệu:** 1025 dòng gốc, 302 dòng duy nhất sau khi bỏ trùng (723 dòng trùng bị loại).
Chia train/test 80/20 (stratify, seed=42) *sau khi* bỏ trùng; test = 61 mẫu.

**Tham số SVM tối ưu (GridSearchCV, 5-fold, scoring ROC-AUC):** `{'clf__C': 10, 'clf__gamma': 0.01, 'clf__kernel': 'rbf'}`

## Kết quả trên tập test
| Mô hình             |   Accuracy (%) |   Precision (%) |   Recall (%) |   F1-Score (%) |   ROC-AUC |
|:--------------------|---------------:|----------------:|-------------:|---------------:|----------:|
| SVM (tối ưu)        |          80.33 |           80    |        84.85 |          82.35 |    0.8582 |
| Logistic Regression |          80.33 |           80    |        84.85 |          82.35 |    0.8712 |
| Random Forest       |          75.41 |           76.47 |        78.79 |          77.61 |    0.868  |
| KNN (k=5)           |          78.69 |           77.78 |        84.85 |          81.16 |    0.8377 |

## Cross-validation 5 lần trên toàn bộ dữ liệu duy nhất
| Mô hình             | CV Accuracy (%)   | CV Recall (%)   | CV ROC-AUC    |
|:--------------------|:------------------|:----------------|:--------------|
| SVM (tối ưu)        | 84.1 ± 4.1        | 90.8 ± 8.6      | 0.908 ± 0.018 |
| Logistic Regression | 83.1 ± 2.8        | 86.6 ± 9.9      | 0.905 ± 0.018 |
| Random Forest       | 81.5 ± 4.0        | 84.1 ± 8.4      | 0.908 ± 0.013 |
| KNN (k=5)           | 80.8 ± 2.7        | 86.0 ± 4.1      | 0.884 ± 0.020 |

## Ma trận nhầm lẫn SVM (hàng = thực tế, cột = dự đoán)
|  | Dự đoán 0 | Dự đoán 1 |
|---|---|---|
| Thực tế 0 | 21 | 7 |
| Thực tế 1 | 5 | 28 |

## Độ quan trọng đặc trưng (permutation, giảm ROC-AUC khi xáo trộn)
- ca: 0.0459
- thal: 0.0305
- oldpeak: 0.0298
- sex: 0.0227
- slope: 0.0155
- thalach: 0.0127
- cp: 0.0057
- exang: 0.0056
- trestbps: -0.0041
- chol: -0.0053
- restecg: -0.0070
- fbs: -0.0084
- age: -0.0188

## Giới hạn và lưu ý
- Tập test chỉ có 61 mẫu nên khoảng tin cậy rộng; nên ưu tiên số liệu cross-validation.
- Đây là kết quả trên dữ liệu thử nghiệm (bộ Heart Disease, nguồn UCI/Kaggle), **chưa** được kiểm chứng lâm sàng
  hay trên quần thể khác. Không dùng để chẩn đoán.
- Nhãn 0/1 và mã hóa đặc trưng theo bộ dữ liệu; cần đối chiếu mô tả gốc trước khi công bố.
