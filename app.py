import warnings
import joblib

warnings.filterwarnings("ignore", message="X does not have valid feature names")

danh_sach = [
    "Dùng địa chỉ IP thay cho tên miền (having_IP_Address).",
    "Đường dẫn URL quá dài, có dấu hiệu ẩn giấu (URL_Length).",
    "Sử dụng dịch vụ rút gọn link để che mắt (Shortining_Service).",
    "Có chứa ký tự @ đáng ngờ trong đường dẫn (having_At_Symbol).",
    "Chuyển hướng người dùng bằng dấu // (double_slash_redirecting).",
    "Tên miền có chứa dấu gạch ngang - (Prefix_Suffix).",
    "Sử dụng quá nhiều tên miền phụ (having_Sub_Domain).",
    "Chứng chỉ bảo mật SSL không hợp lệ hoặc không có (SSLfinal_State).",
    "Thời gian đăng ký tên miền quá ngắn (Domain_registeration_length).",
    "URL yêu cầu tải tài nguyên từ trang web khác (Request_URL).",
    "Đường dẫn neo (Anchor) trỏ sang trang lạ (URL_of_Anchor).",
    "Các thẻ Meta/Script chứa liên kết ẩn (Links_in_tags).",
    "Biểu mẫu (Form) gửi dữ liệu đi nơi khác (SFH).",
    "Lưu lượng truy cập web thấp hoặc không xác định (web_traffic).",
    "Trang web không được Google lập chỉ mục (Google_Index)."
]

# 1. Gọi AI
ai_da_tot_nghiep = joblib.load('models/random_forest_15.pkl')

# 2. Khách hàng nhập link
#link test
link_khach_nhap = "http://web-nhan-qua-shopee-gia-mao.com"

# 3. Tính toán ra mảng 15 đặc trưng (Gọi từ feature_extractor của đệ)
mang_15_dac_trung = [[-1, 1, 1, 1, -1, -1, -1, -1, -1, 1, -1, 1, -1, -1, 1]] 

# 4. AI kiểm tra
ket_qua = ai_da_tot_nghiep.predict(mang_15_dac_trung)

# 5. XỬ LÝ ĐẦU RA 
if ket_qua[0] == -1:
    print(f"❌ CẢNH BÁO: {link_khach_nhap} là WEB LỪA ĐẢO!")
    print("🔎 LÝ DO :")
    
    cac_con_so = mang_15_dac_trung[0]
    for vi_tri in range(len(cac_con_so)):
        if cac_con_so[vi_tri] == -1:
            print(f"  - {danh_sach[vi_tri]}")
else:
    print(f"✅ AN TOÀN: {link_khach_nhap} là web sạch!")