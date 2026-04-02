import pandas as pd
from scipy.io import arff
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os

# ===============================
# LOAD DATA
# ===============================
data_path = 'data/dataset_15.arff'
data, meta = arff.loadarff(data_path)
df = pd.DataFrame(data)

# Decode bytes → int
for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].apply(lambda x: int(x.decode()) if isinstance(x, bytes) else int(x))

# Fix tên cột (tránh lỗi dấu cách / dấu chấm)
df.columns = df.columns.str.strip()

print("Columns in dataset:")
print(df.columns.tolist())

# ===============================
# AUTO FIX FEATURE ORDER
# ===============================
TARGET = 'Result'

# Lấy toàn bộ feature có thật trong dataset
FEATURE_ORDER = [col for col in df.columns if col != TARGET]

print("\nUsing features:", FEATURE_ORDER)

X = df[FEATURE_ORDER]
y = df[TARGET]

print("\nDataset shape:", X.shape)

# ===============================
# SPLIT
# ===============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ===============================
# GRID SEARCH
# ===============================
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2]
}

rf = RandomForestClassifier(
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)

grid = GridSearchCV(
    rf,
    param_grid,
    cv=3,
    scoring='accuracy',
    n_jobs=-1,
    verbose=1
)

grid.fit(X_train, y_train)

best_model = grid.best_estimator_

print("\nBest Params:", grid.best_params_)

# ===============================
# EVALUATION
# ===============================
y_pred = best_model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# ===============================
# CROSS VALIDATION
# ===============================
cv_score = cross_val_score(best_model, X, y, cv=5)
print("\nCross-validation Accuracy:", cv_score.mean())

# ===============================
# FEATURE IMPORTANCE
# ===============================
importances = best_model.feature_importances_

feature_importance = pd.DataFrame({
    'Feature': FEATURE_ORDER,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

print("\nFeature Importance:\n", feature_importance)

# ===============================
# SAVE MODEL
# ===============================
os.makedirs('models', exist_ok=True)

joblib.dump(best_model, 'models/rf_phishing.pkl')
joblib.dump(FEATURE_ORDER, 'models/feature_order.pkl')

print("\nModel saved SUCCESSFULLY 🚀")