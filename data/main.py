import pandas as pd
from scipy.io import arff
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# đọc dataset
data, meta = arff.loadarff("dataset.arff")
df = pd.DataFrame(data)

# chuyển dữ liệu sang số
df = df.apply(lambda col: col.astype(int))

# tách feature và label
X = df.drop("Result", axis=1)
y = df["Result"]

# chia dữ liệu
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# mô hình Random Forest
model = RandomForestClassifier()

# train
model.fit(X_train, y_train)

# dự đoán
y_pred = model.predict(X_test)

# accuracy
accuracy = accuracy_score(y_test, y_pred)

print("Accuracy:", accuracy)