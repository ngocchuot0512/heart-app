"""Huấn luyện mô hình SVM đánh giá nguy cơ tim mạch.

Khác bản cũ:
  * Loại bỏ dòng trùng lặp TRƯỚC khi chia train/test (heart.csv có 723/1025 dòng trùng
    -> bản cũ bị rò rỉ dữ liệu, số liệu 98-100% không đáng tin).
  * Dùng sklearn Pipeline(StandardScaler + SVC) lưu thành MỘT file -> app không thể
    tiền xử lý sai khác với lúc huấn luyện.
  * Báo cáo thêm cross-validation 5 lần trên toàn bộ dữ liệu.

Chạy:  python ml/train.py   (từ thư mục gốc dự án)
"""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import (GridSearchCV, StratifiedKFold,
                                     cross_validate, train_test_split)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

ROOT = Path(__file__).resolve().parent.parent
SEED = 42


def make_pipe(clf):
    return Pipeline([("scaler", StandardScaler()), ("clf", clf)])


def metrics(y_true, y_pred, y_prob):
    return {
        "Accuracy (%)": round(accuracy_score(y_true, y_pred) * 100, 2),
        "Precision (%)": round(precision_score(y_true, y_pred) * 100, 2),
        "Recall (%)": round(recall_score(y_true, y_pred) * 100, 2),
        "F1-Score (%)": round(f1_score(y_true, y_pred) * 100, 2),
        "ROC-AUC": round(roc_auc_score(y_true, y_prob), 4),
    }


def main():
    raw = pd.read_csv(ROOT / "data" / "heart.csv")
    df = raw.drop_duplicates().reset_index(drop=True)
    print(f"Dữ liệu gốc: {len(raw)} dòng -> sau bỏ trùng: {len(df)} dòng")

    X, y = df.drop(columns="target"), df["target"]
    cols = list(X.columns)
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=SEED, stratify=y)

    # --- Tối ưu SVM (chọn tham số bằng CV trên tập train, scaler nằm TRONG CV) ---
    grid = GridSearchCV(
        make_pipe(SVC(probability=True, random_state=SEED)),
        {"clf__C": [0.1, 1, 10], "clf__gamma": ["scale", 0.1, 0.01],
         "clf__kernel": ["rbf", "linear"]},
        cv=StratifiedKFold(5, shuffle=True, random_state=SEED),
        scoring="roc_auc", n_jobs=-1)
    grid.fit(X_tr, y_tr)
    svm = grid.best_estimator_
    print("Tham số SVM tối ưu:", grid.best_params_)

    models = {
        "SVM (tối ưu)": svm,
        "Logistic Regression": make_pipe(LogisticRegression(max_iter=1000, random_state=SEED)),
        "Random Forest": make_pipe(RandomForestClassifier(n_estimators=200, random_state=SEED)),
        "KNN (k=5)": make_pipe(KNeighborsClassifier(n_neighbors=5)),
    }
    rows, cv_rows = [], []
    skf = StratifiedKFold(5, shuffle=True, random_state=SEED)
    for name, m in models.items():
        if name != "SVM (tối ưu)":
            m.fit(X_tr, y_tr)
        rows.append({"Mô hình": name, **metrics(y_te, m.predict(X_te), m.predict_proba(X_te)[:, 1])})
        cv = cross_validate(m, X, y, cv=skf, scoring=["accuracy", "recall", "roc_auc"])
        cv_rows.append({
            "Mô hình": name,
            "CV Accuracy (%)": f"{cv['test_accuracy'].mean()*100:.1f} ± {cv['test_accuracy'].std()*100:.1f}",
            "CV Recall (%)": f"{cv['test_recall'].mean()*100:.1f} ± {cv['test_recall'].std()*100:.1f}",
            "CV ROC-AUC": f"{cv['test_roc_auc'].mean():.3f} ± {cv['test_roc_auc'].std():.3f}",
        })
    res, cvres = pd.DataFrame(rows), pd.DataFrame(cv_rows)
    cm = confusion_matrix(y_te, svm.predict(X_te))

    # --- Độ quan trọng toàn cục (permutation importance trên tập test) ---
    pi = permutation_importance(svm, X_te, y_te, n_repeats=30, random_state=SEED,
                                scoring="roc_auc")
    importance = dict(sorted(zip(cols, pi.importances_mean.round(4).tolist()),
                             key=lambda kv: -kv[1]))

    # --- Giá trị tham chiếu dùng cho giải thích cục bộ ---
    reference = {c: float(X_tr[c].median()) for c in cols}

    bundle = {
        "pipeline": svm,
        "columns": cols,
        "reference": reference,
        "importance": importance,
        "test_metrics": res.set_index("Mô hình").loc["SVM (tối ưu)"].to_dict(),
        "n_samples": int(len(df)), "n_test": int(len(X_te)),
        "sklearn_version": sklearn.__version__,
    }
    joblib.dump(bundle, ROOT / "ml" / "pipeline.pkl")

    report = f"""# Báo cáo đánh giá mô hình

**Dữ liệu:** {len(raw)} dòng gốc, {len(df)} dòng duy nhất sau khi bỏ trùng ({len(raw)-len(df)} dòng trùng bị loại).
Chia train/test 80/20 (stratify, seed={SEED}) *sau khi* bỏ trùng; test = {len(X_te)} mẫu.

**Tham số SVM tối ưu (GridSearchCV, 5-fold, scoring ROC-AUC):** `{grid.best_params_}`

## Kết quả trên tập test
{res.to_markdown(index=False)}

## Cross-validation 5 lần trên toàn bộ dữ liệu duy nhất
{cvres.to_markdown(index=False)}

## Ma trận nhầm lẫn SVM (hàng = thực tế, cột = dự đoán)
|  | Dự đoán 0 | Dự đoán 1 |
|---|---|---|
| Thực tế 0 | {cm[0,0]} | {cm[0,1]} |
| Thực tế 1 | {cm[1,0]} | {cm[1,1]} |

## Độ quan trọng đặc trưng (permutation, giảm ROC-AUC khi xáo trộn)
{chr(10).join(f"- {k}: {v:.4f}" for k, v in importance.items())}

## Giới hạn và lưu ý
- Tập test chỉ có {len(X_te)} mẫu nên khoảng tin cậy rộng; nên ưu tiên số liệu cross-validation.
- Đây là kết quả trên dữ liệu thử nghiệm (bộ Heart Disease, nguồn UCI/Kaggle), **chưa** được kiểm chứng lâm sàng
  hay trên quần thể khác. Không dùng để chẩn đoán.
- Nhãn 0/1 và mã hóa đặc trưng theo bộ dữ liệu; cần đối chiếu mô tả gốc trước khi công bố.
"""
    (ROOT / "ml" / "evaluation_report.md").write_text(report, encoding="utf-8")
    (ROOT / "ml" / "metrics.json").write_text(
        json.dumps({"test": res.to_dict("records"), "cv": cv_rows}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(res.to_string(index=False))
    print(cvres.to_string(index=False))
    print("Đã lưu ml/pipeline.pkl và ml/evaluation_report.md")


if __name__ == "__main__":
    main()
