import streamlit as st
import joblib
import pandas as pd
from feature_extractor import PhishingFeatureExtractor

# ===============================
# CONFIG
# ===============================
st.set_page_config(page_title="PhishGuard", layout="wide")

# ===============================
# CSS
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

/* HERO */
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

/* CARD */
.block-container .stColumn > div {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    padding: 20px;
    border-radius: 12px;
}

/* BUTTON FIX */
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

/* RESULT */
.result-card {
    margin-top: 25px;
    padding: 24px;
    border-radius: 20px;
    background: rgba(255,255,255,0.08);
}
.metric-card {
    background: rgba(0,0,0,0.3);
    border-radius: 12px;
    padding: 10px;
    margin-bottom: 10px;
}
.feature-item {
    background: rgba(0,0,0,0.25);
    padding: 8px 12px;
    border-radius: 10px;
    margin-bottom: 6px;
    font-size: 14px;
}
.divider {
    margin: 20px 0;
    border-top: 1px solid rgba(255,255,255,0.1);
}
.guide-text {
    padding: 12px;
    background: rgba(0,0,0,0.2);
    border-radius: 12px;
    color: #cbd5f5;
}

/* FOOTER */
.footer {
    text-align:center;
    margin-top:40px;
    color:#cbd5f5;
    font-size:14px;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# LOAD MODEL
# ===============================
try:
    model = joblib.load("models/rf_phishing.pkl")
    feature_order = joblib.load("models/feature_order.pkl")
except:
    st.error("❌ Chưa có model. Hãy chạy train_model.py trước!")
    st.stop()

# ===============================
# HERO (GIỮ NGUYÊN ICON CỦA M)
# ===============================
col1, col2 = st.columns([2,1])

with col1:
    st.markdown('<div class="badge">🛡️ Machine Learning Powered</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="title">
        Detect Phishing <br>
        Websites Instantly
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="desc">
        Protect yourself from online threats with our ML-based phishing detection system.
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="text-align:center;">
        <div style="
            width:320px;
            height:320px;
            border-radius:50%;
            background: rgba(16,185,129,0.1);
            display:flex;
            align-items:center;
            justify-content:center;
            margin:auto;
        ">
            <div style="
                width:180px;
                height:180px;
                border-radius:50%;
                background: rgba(16,185,129,0.2);
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:70px;
            ">
                🛡️
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ===============================
# INPUT
# ===============================
st.subheader("🔍 Check a Website URL")

col1, col2 = st.columns([4,1])
with col1:
    url = st.text_input("", placeholder="https://example.com", label_visibility="collapsed")
with col2:
    analyze = st.button("🚀 Analyze", use_container_width=True)

st.markdown("""
<div class="guide-text">
📘 <b>How to use</b><br>
- Enter URL<br>
- Click Analyze<br>
- Get result instantly
</div>
""", unsafe_allow_html=True)

# ===============================
# PREDICT
# ===============================
if analyze:
    if url.strip() == "":
        st.warning("⚠️ Please enter a URL")
    else:
        try:
            with st.spinner("Analyzing..."):
                extractor = PhishingFeatureExtractor(url)
                features = extractor.extract_all_features()

                df = pd.DataFrame([features], columns=feature_order)

                pred = model.predict(df)[0]

                try:
                    prob = model.predict_proba(df)[0]
                    confidence = round(max(prob) * 100, 2)
                except:
                    confidence = 50

            if pred == 1:
                status = "SAFE WEBSITE ✅"
                color = "#22c55e"
                risk = 100 - confidence
            else:
                status = "PHISHING WEBSITE ⚠️"
                color = "#ef4444"
                risk = confidence

            # FEATURE ANALYSIS
            feature_analysis = []
            safe_signals = 0
            suspicious_signals = 0

            for name, value in zip(feature_order, features):
                if value == -1:
                    feature_analysis.append(f"⚠️ {name}")
                    suspicious_signals += 1
                elif value == 1:
                    safe_signals += 1

            feature_analysis = feature_analysis[:6]

            # RECOMMENDATION
            if pred == 0:
                recommendation = """
                ⚠️ Do not enter personal information<br>
                🔍 Check domain carefully<br>
                🚫 Avoid clicking unknown links
                """
            else:
                recommendation = """
                ✅ Website appears safe<br>
                🔒 Always check HTTPS<br>
                ⚠️ Stay cautious
                """

            # RESULT UI
            st.markdown(f"""
            <div class="result-card">

            <h2 style="color:{color}">{status}</h2>

            <div class="metric-card">
                <b>Confidence:</b> {confidence}%<br>
                <b>Risk Score:</b> {round(risk,2)}%
            </div>

            <div class="divider"></div>

            <b>🔬 Key Findings</b>
            {"".join([f"<div class='feature-item'>{f}</div>" for f in feature_analysis])}

            <div class="divider"></div>

            <b>📊 Analysis Summary</b>
            <div class="feature-item">⚠️ Suspicious: {suspicious_signals}</div>
            <div class="feature-item">✅ Safe: {safe_signals}</div>

            <div class="divider"></div>

            <b>💡 Recommendation</b>
            <div class="guide-text">{recommendation}</div>

            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Lỗi: {e}")

# ===============================
# FOOTER
# ===============================
st.markdown("""
<div class="footer">
    🛡️ PhishGuard © 2026
</div>
""", unsafe_allow_html=True)