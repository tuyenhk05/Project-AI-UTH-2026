# interface.py
import streamlit as st
import joblib
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from feature_extractor import PhishingFeatureExtractor

# -------------------- CẤU HÌNH --------------------
st.set_page_config(
    page_title="PhishGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------- CSS (ĐẸP, KHÔNG DƯ THỪA) --------------------
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    /* Nền chính */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #0a0f1f, #05070f);
    }
    /* Ẩn header mặc định */
    header { display: none; }
    /* Container chính */
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 1.5rem;
    }
    /* Grid 2 cột */
    .two-columns {
        display: grid;
        grid-template-columns: 1.5fr 1fr;
        gap: 1.5rem;
        margin-bottom: 1.5rem;
    }
    /* Card */
    .glass-card {
        background: rgba(15, 25, 45, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 1.5rem;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        transition: 0.2s;
    }
    .glass-card:hover {
        background: rgba(20, 30, 55, 0.7);
        border-color: rgba(59,130,246,0.3);
    }
    /* Tiêu đề */
    h1 {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #fff, #60a5fa);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }
    /* Input */
    .stTextInput > div > div > input {
        background: rgba(0,0,0,0.4);
        border: 1px solid #2d3a5e;
        border-radius: 2rem;
        color: white;
        padding: 0.7rem 1rem;
    }
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59,130,246,0.2);
    }
    /* Button */
    .stButton button {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        border: none;
        border-radius: 2rem;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        color: white;
        width: 100%;
        transition: 0.2s;
    }
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 20px rgba(59,130,246,0.3);
    }
    /* Kết quả */
    .result-box {
        margin-top: 1rem;
        border-radius: 1rem;
        padding: 1rem;
        text-align: center;
    }
    .safe {
        background: rgba(16,185,129,0.2);
        border: 1px solid #10b981;
    }
    .phish {
        background: rgba(239,68,68,0.2);
        border: 1px solid #ef4444;
    }
    .safe h2 { color: #10b981; }
    .phish h2 { color: #ef4444; }
    .result-box p { color: #cbd5e1; margin-top: 0.3rem; }
    /* Metric */
    .metric {
        text-align: center;
        padding: 0.8rem;
        background: rgba(0,0,0,0.3);
        border-radius: 1rem;
        margin-top: 0.5rem;
    }
    .metric-label { font-size: 0.8rem; color: #94a3b8; }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: white; }
    /* Badge */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 2rem;
        font-size: 0.7rem;
        font-weight: 600;
    }
    .badge-safe { background: rgba(16,185,129,0.2); color: #10b981; }
    .badge-phish { background: rgba(239,68,68,0.2); color: #ef4444; }
    .badge-susp { background: rgba(245,158,11,0.2); color: #f59e0b; }
    /* History */
    .history-item {
        background: rgba(0,0,0,0.3);
        border-radius: 0.8rem;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
    }
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.05);
        border-radius: 2rem;
        color: white;
    }
    /* Table */
    .dataframe {
        background: transparent !important;
        color: #e2e8f0 !important;
    }
    .dataframe th {
        background: rgba(255,255,255,0.1) !important;
    }
    .dataframe td {
        background: rgba(0,0,0,0.3) !important;
    }
    /* Footer */
    .footer {
        text-align: center;
        color: #475569;
        font-size: 0.7rem;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.05);
    }
</style>
""", unsafe_allow_html=True)

# -------------------- STATE --------------------
if 'history' not in st.session_state:
    st.session_state.history = []

def add_to_history(url, result, confidence):
    st.session_state.history.append({
        'url': url,
        'result': result,
        'confidence': confidence,
        'time': time.strftime("%H:%M:%S")
    })
    if len(st.session_state.history) > 10:
        st.session_state.history.pop(0)

# -------------------- LOAD MODEL --------------------
@st.cache_resource
def load_model():
    try:
        model = joblib.load('models/random_forest_15.pkl')
        feature_names = joblib.load('models/feature_names.pkl')
        importance = None
        if hasattr(model, 'feature_importances_'):
            importance = dict(zip(feature_names, model.feature_importances_))
        return model, feature_names, importance
    except Exception as e:
        st.error(f"Lỗi load model: {e}")
        return None, None, None

model, feature_names, feature_importance = load_model()

# -------------------- LAYOUT --------------------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown("<h1>🛡️ PhishGuard AI</h1>", unsafe_allow_html=True)
st.markdown('<div class="subtitle">Phát hiện trang web lừa đảo bằng Machine Learning | Random Forest</div>', unsafe_allow_html=True)

# Hai cột
st.markdown('<div class="two-columns">', unsafe_allow_html=True)

# Cột trái: nhập URL và kết quả
with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🔗 URL cần kiểm tra")
    url = st.text_input("", placeholder="https://example.com", label_visibility="collapsed")
    analyze = st.button("Phân tích", type="primary", use_container_width=True)
    
    if analyze and url:
        if not model:
            st.error("Mô hình chưa sẵn sàng.")
        else:
            with st.spinner("Đang phân tích..."):
                try:
                    extractor = PhishingFeatureExtractor(url)
                    features = extractor.extract_all_features()
                    X = pd.DataFrame([features], columns=feature_names)
                    pred = model.predict(X)[0]
                    proba = model.predict_proba(X)[0]
                    
                    # Xác suất phishing
                    if pred == -1:
                        prob_phish = proba[0]
                    else:
                        prob_phish = proba[1]
                    confidence = prob_phish * 100 if pred == -1 else (1 - prob_phish) * 100
                    
                    add_to_history(url, pred, confidence)
                    
                    # Hiển thị kết quả
                    if pred == -1:
                        st.markdown("""
                        <div class="result-box phish">
                            <h2>⚠️ CẢNH BÁO LỪA ĐẢO</h2>
                            <p>Trang web có dấu hiệu lừa đảo.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="result-box safe">
                            <h2>✅ AN TOÀN</h2>
                            <p>Trang web hợp lệ.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="metric">
                        <div class="metric-label">ĐỘ TIN CẬY</div>
                        <div class="metric-value">{confidence:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(confidence/100)
                    
                    # Chi tiết đặc trưng
                    with st.expander("🔍 Xem chi tiết đặc trưng"):
                        feature_details = {
                            'having_IP_Address': 'Địa chỉ IP', 'URL_Length': 'Độ dài URL',
                            'Shortining_Service': 'Rút gọn URL', 'having_At_Symbol': 'Ký tự @',
                            'double_slash_redirecting': 'Dấu //', 'Prefix_Suffix': 'Dấu -',
                            'having_Sub_Domain': 'Subdomain', 'SSLfinal_State': 'SSL',
                            'Domain_registeration_length': 'Tuổi domain', 'Request_URL': 'Request ngoại',
                            'URL_of_Anchor': 'Anchor ngoại', 'Links_in_tags': 'Links ngoại',
                            'SFH': 'Form handler', 'web_traffic': 'Traffic', 'Google_Index': 'Google index'
                        }
                        df_feat = pd.DataFrame({
                            "STT": range(1,16),
                            "Đặc trưng": feature_names,
                            "Giá trị": features,
                            "Phân loại": ["<span class='badge badge-safe'>Hợp lệ</span>" if v==1 else ("<span class='badge badge-phish'>Lừa đảo</span>" if v==-1 else "<span class='badge badge-susp'>Đáng ngờ</span>") for v in features],
                            "Giải thích": [feature_details.get(f, "") for f in feature_names]
                        })
                        st.write(df_feat.to_html(escape=False, index=False), unsafe_allow_html=True)
                    
                    # Biểu đồ
                    with st.expander("📈 Biểu đồ đặc trưng"):
                        fig, ax = plt.subplots(figsize=(10, 5))
                        colors = ['#ef4444' if v==-1 else ('#f59e0b' if v==0 else '#10b981') for v in features]
                        ax.barh(feature_names, features, color=colors)
                        ax.axvline(0, color='gray', linestyle='--')
                        ax.set_xlabel("Giá trị")
                        ax.set_facecolor('none')
                        fig.patch.set_facecolor('none')
                        ax.tick_params(colors='white')
                        st.pyplot(fig)
                    
                    # Tải báo cáo
                    report = f"URL: {url}\nKết quả: {'LỪA ĐẢO' if pred==-1 else 'AN TOÀN'}\nĐộ tin cậy: {confidence:.1f}%\n\nĐặc trưng:\n"
                    for f, v in zip(feature_names, features):
                        report += f"{f}: {v}\n"
                    st.download_button("📥 Tải báo cáo", report, "phishguard_report.txt", "text/plain")
                    
                except Exception as e:
                    st.error(f"Lỗi: {e}")
    elif analyze and not url:
        st.warning("Nhập URL.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Cột phải: lịch sử + thông tin model
with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🕒 Lịch sử gần đây")
    if st.session_state.history:
        for item in reversed(st.session_state.history[-5:]):
            icon = "✅" if item['result'] == 1 else "⚠️"
            st.markdown(f"""
            <div class="history-item">
                {icon} <strong>{item['url'][:35]}</strong><br>
                <span style="font-size:0.7rem; color:#94a3b8;">{item['time']} - {item['confidence']:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Chưa có phân tích.")
    
    st.markdown("---")
    st.markdown("### 🧠 Mô hình")
    st.markdown("**Random Forest** – 100 cây – 15 đặc trưng")
    st.markdown("Độ chính xác: **95.2%**")
    
    if feature_importance:
        st.markdown("#### 🔥 Đặc trưng quan trọng nhất")
        imp_df = pd.DataFrame(feature_importance.items(), columns=["Đặc trưng", "Độ quan trọng"])
        imp_df = imp_df.sort_values("Độ quan trọng", ascending=False).head(5)
        for _, row in imp_df.iterrows():
            st.markdown(f"• {row['Đặc trưng']}: {row['Độ quan trọng']:.3f}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # đóng two-columns

# Tab hướng dẫn (nhỏ gọn)
tab1, tab2 = st.tabs(["📖 Hướng dẫn", "📊 Chi tiết mô hình"])
with tab1:
    st.markdown("""
    **Cách dùng:** Nhập URL đầy đủ (http://hoặc https://) → Nhấn **Phân tích** → Xem kết quả và độ tin cậy.
    - Mở rộng các mục để xem chi tiết đặc trưng, biểu đồ.
    - Tải báo cáo để lưu kết quả.
    - Lịch sử hiển thị 5 URL gần nhất.
    """)
with tab2:
    if feature_importance:
        st.markdown("### 📊 Độ quan trọng đặc trưng (toàn bộ)")
        imp_df = pd.DataFrame(feature_importance.items(), columns=["Đặc trưng", "Độ quan trọng"])
        imp_df = imp_df.sort_values("Độ quan trọng", ascending=False)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(imp_df["Đặc trưng"], imp_df["Độ quan trọng"], color='#3b82f6')
        ax.set_xlabel("Độ quan trọng")
        ax.set_facecolor('none')
        fig.patch.set_facecolor('none')
        ax.tick_params(colors='white')
        st.pyplot(fig)
    else:
        st.info("Không có dữ liệu feature importance.")

# Footer
st.markdown("""
<div class="footer">
    PhishGuard AI © 2026 | Machine Learning | UCI Phishing Dataset
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)