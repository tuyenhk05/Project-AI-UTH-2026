import streamlit as st
import joblib
import pandas as pd
from feature_extractor import PhishingFeatureExtractor

# ===============================
# CONFIG
# ===============================
st.set_page_config(page_title="PhishGuard", layout="wide")

# ===============================
# CSS (GIỮ NGUYÊN GIAO DIỆN CYBER CỦA BẠN)
# ===============================
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stApp {
    background: linear-gradient(135deg, #0f172a, #0d9488);
    color: white;
}
.title {
    font-size: 64px;
    font-weight: 800;
}
.desc {
    color: #cbd5f5;
    margin-top: 20px;
    font-size: 18px;
}
.badge {
    background: rgba(16,185,129,0.2);
    color: #34d399;
    padding: 8px 14px;
    border-radius: 20px;
    display: inline-block;
    margin-bottom: 20px;
}
.block-container .stColumn > div {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    padding: 20px;
    border-radius: 12px;
}
.stButton button {
    background: linear-gradient(135deg, #14b8a6, #0d9488) !important;
    color: white !important;
    border-radius: 10px !important;
    height: 45px;
    font-weight: bold;
    border: none !important;
    transition: 0.3s;
}
.stButton button:hover {
    background: linear-gradient(135deg, #0d9488, #0f766e) !important;
    transform: scale(1.03);
}
.guide-text {
    padding: 12px;
    background: rgba(0,0,0,0.2);
    border-radius: 12px;
    color: #cbd5f5;
}
.footer {
    text-align:center;
    margin-top:40px;
    color:#cbd5f5;
    font-size:14px;
}

/* THIẾT KẾ CYBER SECURITY DASHBOARD */
.cyber-verdict {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    background: rgba(0, 0, 0, 0.4);
    border: 2px solid;
    border-radius: 20px;
    padding: 30px;
    margin: 30px 0;
    backdrop-filter: blur(10px);
}

.verdict-safe {
    border-color: #10b981;
    box-shadow: 0 0 20px rgba(16,185,129,0.2);
}

.verdict-danger {
    border-color: #ef4444;
    box-shadow: 0 0 20px rgba(239,68,68,0.2);
}

.verdict-neutral {
    border-color: #f59e0b;
    box-shadow: 0 0 20px rgba(245,158,11,0.2);
}

.verdict-main {
    flex: 1 1 300px;
}

.verdict-icon {
    font-size: 48px;
    margin-bottom: 10px;
}

.verdict-title {
    font-size: 32px;
    font-weight: 900;
    letter-spacing: 1px;
    margin-bottom: 5px;
}

.verdict-subtitle {
    font-size: 15px;
    color: #94a3b8;
}

.verdict-stats {
    display: flex;
    gap: 15px;
    flex: 1 1 300px;
    justify-content: flex-end;
}

.stat-box {
    background: rgba(255,255,255,0.05);
    padding: 15px 20px;
    border-radius: 12px;
    text-align: center;
    min-width: 110px;
    border: 1px solid rgba(255,255,255,0.1);
}

.stat-val {
    font-size: 26px;
    font-weight: 800;
}

.stat-label {
    font-size: 11px;
    text-transform: uppercase;
    color: #cbd5e1;
    margin-top: 5px;
}

.section-title {
    font-size: 24px;
    font-weight: 700;
    margin: 30px 0 15px 0;
    color: #f8fafc;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 16px;
}

.feature-box {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 15px;
    background: rgba(0, 0, 0, 0.25);
    border-radius: 12px;
    border-left: 5px solid;
}

.fb-safe {
    border-left-color: #10b981;
}

.fb-danger {
    border-left-color: #ef4444;
}

.fb-neutral {
    border-left-color: #f59e0b;
}

.fb-icon-wrapper {
    width: 35px;
    height: 35px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255,255,255,0.05);
}

.fb-content {
    flex: 1;
}

.fb-title {
    font-size: 13px;
    color: #e2e8f0;
    font-weight: 500;
}

.fb-status {
    font-size: 11px;
    margin-top: 4px;
    font-weight: 700;
}

.txt-safe {
    color: #10b981;
}

.txt-danger {
    color: #ef4444;
}

.txt-neutral {
    color: #f59e0b;
}

.divider {
    margin: 30px 0;
    border-top: 1px dashed rgba(255,255,255,0.2);
}
</style>
""", unsafe_allow_html=True)

# ===============================
# LOAD MODEL
# ===============================
@st.cache_resource
def load_models():
    try:
        m = joblib.load("models/rf_phishing.pkl")
        f = joblib.load("models/feature_order.pkl")
        return m, f
    except Exception as e:
        st.error(f"❌ Chưa có model hoặc lỗi tải: {e}. Hãy chạy train_model.py trước!")
        st.stop()

model, feature_order = load_models()

# ===============================
# FEATURE DESCRIPTION
# ===============================
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

feature_map = {}

for item in danh_sach:
    name = item.split("(")[-1].replace(").", "")
    desc = item.split("(")[0].strip()
    feature_map[name] = desc

# ===============================
# HERO
# ===============================
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="badge">Công nghệ Machine Learning</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="title">Phát Hiện Website Lừa Đảo <br> Ngay Lập Tức</div>
    <div class="desc">Bảo vệ bạn khỏi các mối đe dọa trực tuyến với hệ thống phân tích redirect và AI chuyên sâu.</div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="text-align:center;">
        <div style="width:280px;height:280px;border-radius:50%;background: rgba(16,185,129,0.1);
        display:flex;align-items:center;justify-content:center;margin:auto;">
            <div style="width:160px;height:160px;border-radius:50%;background: rgba(16,185,129,0.2);
            display:flex;align-items:center;justify-content:center;font-size:60px;">
            🛡️
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ===============================
# INPUT
# ===============================
st.subheader("Kiểm tra URL website")

col_in1, col_in2 = st.columns([4, 1])

with col_in1:
    url = st.text_input("Nhập URL", placeholder="https://example.com", label_visibility="collapsed")

with col_in2:
    if st.button("Phân tích", use_container_width=True):
        st.session_state.analyze_clicked = True

if "analyze_clicked" not in st.session_state:
    st.session_state.analyze_clicked = False

st.markdown(
    '<div class="guide-text"><b>Cách sử dụng</b>: Nhập URL và nhấn Phân tích để bắt đầu quét AI đa tầng.</div>',
    unsafe_allow_html=True
)

# ===============================
# PREDICT LOGIC
# ===============================
if st.session_state.analyze_clicked:

    if url.strip() == "":
        st.warning("Vui lòng nhập URL")
    else:
        try:
            with st.spinner("Đang thực hiện quét bảo mật..."):

                extractor = PhishingFeatureExtractor(url)
                features_dict = extractor.extract_all_features()

                ordered_features = [
                    features_dict.get(name, 0) for name in feature_order
                ]

                df = pd.DataFrame([ordered_features], columns=feature_order)

                pred = model.predict(df)[0]

                try:
                    prob = model.predict_proba(df)[0]
                    confidence = round(max(prob) * 100, 2)
                except:
                    confidence = 50

                st.session_state.analyze_clicked = False

                safe_signals = sum(1 for v in features_dict.values() if v == 1)
                suspicious_signals = sum(1 for v in features_dict.values() if v == -1)

                if pred == 0 or suspicious_signals >= 8:
                    st_title, st_sub = "CẢNH BÁO LỪA ĐẢO!", f"Hệ thống xác định mức độ rủi ro cực cao tại: {extractor.domain}"
                    v_class, m_color, m_icon = "verdict-danger", "#ef4444", "🚨"

                elif suspicious_signals >= 4 or suspicious_signals >= safe_signals:
                    st_title, st_sub = "CẦN THẬN TRỌNG", "Mô hình AI nghi ngờ một số yếu tố bất thường trên trang."
                    v_class, m_color, m_icon = "verdict-neutral", "#f59e0b", "⚠️"

                else:
                    st_title, st_sub = "TRANG WEB AN TOÀN", f"Kết quả phân tích domain: {extractor.domain}"
                    v_class, m_color, m_icon = "verdict-safe", "#10b981", "✅"

                overview_html = f"""<div class="cyber-verdict {v_class}">
<div class="verdict-main">
<div class="verdict-title" style="color:{m_color};">{st_title}</div>
<div class="verdict-subtitle">{st_sub}</div>
</div>
<div class="verdict-stats">
<div class="stat-box">
<div class="stat-val" style="color:{m_color};">{confidence}%</div>
<div class="stat-label">Tin cậy</div>
</div>
<div class="stat-box">
<div class="stat-val" style="color:#ef4444;">{suspicious_signals}</div>
<div class="stat-label">Rủi ro</div>
</div>
<div class="stat-box">
<div class="stat-val" style="color:#10b981;">{safe_signals}</div>
<div class="stat-label">An toàn</div>
</div>
</div>
</div>"""

                st.markdown(overview_html, unsafe_allow_html=True)

                if v_class == "verdict-danger":
                    st.error(f"⚠️ **CẢNH BÁO:** Hệ thống phát hiện URL này thực chất dẫn đến: {extractor.redirected_url}.")

                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

                st.markdown('<div class="section-title">🔍 Chi tiết kỹ thuật hệ thống quét được</div>', unsafe_allow_html=True)

                grid_html = '<div class="feature-grid">'

                for name in feature_order:
                    value = features_dict.get(name, 0)
                    desc = feature_map.get(name, name)

                    if value == -1:
                        fb_c, txt_c, icon, txt = "fb-danger", "txt-danger", "⚠️", "RỦI RO"
                    elif value == 1:
                        fb_c, txt_c, icon, txt = "fb-safe", "txt-safe", "🛡️", "AN TOÀN"
                    else:
                        fb_c, txt_c, icon, txt = "fb-neutral", "txt-neutral", "ℹ️", "CẢNH BÁO"

                    grid_html += f"""<div class="feature-box {fb_c}">
<div class="fb-icon-wrapper">{icon}</div>
<div class="fb-content">
<div class="fb-title">{desc}</div>
<div class="fb-status {txt_c}">{txt}</div>
</div>
</div>"""

                grid_html += "</div>"

                st.markdown(grid_html, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Lỗi phân tích: {e}")

# ===============================
# FOOTER
# ===============================
st.markdown(
    '<div class="footer">PhishGuard © 2026 | Bảo vệ không gian mạng Việt Nam</div>',
    unsafe_allow_html=True
)