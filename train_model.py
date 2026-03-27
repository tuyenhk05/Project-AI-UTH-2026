import pandas as pd
from scipy.io import arff
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
import os

print("--- BẮT ĐẦU KIỂM TRA ---")
file_path = "data/dataset_15.arff"
print(f"1. Đang đọc dữ liệu từ {file_path} ...")
data, meta = arff.loadarff(file_path)
df = pd.DataFrame(data)

df = df.apply(lambda col: col.astype(int))

X = df.drop("Result", axis=1) # X lấy 15 cột đề bài
y = df["Result"]              # y lấy cột kết quả cuối cùng

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("2. Đang truyền cho Random Forest...")
model = RandomForestClassifier(n_estimators=100, random_state=42)

model.fit(X_train, y_train)

print("3. Đang cho AI kiểm tra trên tập dữ liệu...")
y_pred = model.predict(X_test)


accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, pos_label=-1) 
recall = recall_score(y_test, y_pred, pos_label=-1)

print("\n========== BẢNG VÀNG THÀNH TÍCH ==========")
print(f"Độ chính xác (Accuracy)  : {accuracy * 100:.2f}%")
print(f"Độ tin cậy   (Precision) : {precision * 100:.2f}%")
print(f"Độ nhạy      (Recall)    : {recall * 100:.2f}%")
print("==========================================\n")

# # 7. Đóng gói 
# print("4. Đang đóng gói trí tuệ nhân tạo thành file...")
# if not os.path.exists('models'):
#     os.makedirs('models') # Tạo thư mục models nếu chưa tạo
    
# joblib.dump(model, 'models/random_forest_15.pkl') # Lưu tên file có số 15 để phân biệt
# print("=> ĐẠI CÔNG CÁO THÀNH! Đã lưu mô hình tại: models/random_forest_15.pkl")