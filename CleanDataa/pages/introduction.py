import streamlit as st

# Custom styling specifically for the Introduction page to isolate from app.py card heights
st.markdown("""
<style>
    /* Custom profile card to avoid inheritance of 165px metric height */
    .profile-card {
        background: rgba(30, 41, 59, 0.45) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .profile-card:hover {
        border-color: rgba(56, 189, 248, 0.4) !important;
        box-shadow: 0 12px 40px 0 rgba(56, 189, 248, 0.15) !important;
    }

    /* Custom intro card for step process flow with comfortable 270px height */
    .intro-card {
        background: rgba(30, 41, 59, 0.45) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        padding: 22px !important;
        text-align: center !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
        height: 270px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        align-items: center !important;
    }
    
    .intro-card:hover {
        transform: translateY(-6px) !important;
        border-color: rgba(56, 189, 248, 0.4) !important;
        box-shadow: 0 12px 40px 0 rgba(56, 189, 248, 0.18) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style="margin-bottom: 30px; text-align: center;">
        <h1 style="color: #38BDF8; font-weight: 800; font-size: 2.5rem; letter-spacing: -0.01em; text-shadow: 0 0 20px rgba(56, 189, 248, 0.25);">
            📚 HỆ THỐNG PHÂN TÍCH VÀ DỰ BÁO NHU CẦU BÁN HÀNG
        </h1>
        <p style="color: #94A3B8; font-size: 1.2rem; font-weight: 400; margin-top: 5px;">
            Đồ Án Tốt Nghiệp Hệ Thống Thông Tin Quản Lý - AI & BI Forecasting Platform
        </p>
    </div>
""", unsafe_allow_html=True)

# 1. THẺ PROFILE SINH VIÊN THỰC HIỆN
st.markdown("""
    <div class="profile-card" style="max-width: 100%; margin: 0 auto 35px auto; padding: 45px 50px !important; min-height: 250px; display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 20px; border-left: 5px solid #38BDF8;">
        <h3 style="color: #F8FAFC; font-size: 1.35rem; font-weight: 700; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 12px; text-align: center; width: 100%;">
            👤 THÔNG TIN TÁC GIẢ ĐỀ TÀI
        </h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; row-gap: 30px; column-gap: 25px; text-align: center; width: 100%;">
            <div>
                <p style="color: #94A3B8; margin: 0; font-size: 0.9rem;">Sinh viên thực hiện:</p>
                <p style="color: #F8FAFC; margin: 4px 0 0 0; font-size: 1.15rem; font-weight: bold;">Lê Tấn Vinh</p>
            </div>
            <div>
                <p style="color: #94A3B8; margin: 0; font-size: 0.9rem;">Mã số sinh viên (MSSV):</p>
                <p style="color: #F8FAFC; margin: 4px 0 0 0; font-size: 1.15rem; font-weight: bold; color: #38BDF8;">64139010</p>
            </div>
            <div>
                <p style="color: #94A3B8; margin: 0; font-size: 0.9rem;">Lớp học phần:</p>
                <p style="color: #F8FAFC; margin: 4px 0 0 0; font-size: 1.15rem; font-weight: bold;">64.HTTT</p>
            </div>
            <div>
                <p style="color: #94A3B8; margin: 0; font-size: 0.9rem;">Chuyên ngành:</p>
                <p style="color: #F8FAFC; margin: 4px 0 0 0; font-size: 1.15rem; font-weight: bold;">Hệ thống thông tin quản lý</p>
            </div>
        </div>
        <!-- 
        <div style="margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 15px; text-align: left;">
            <p style="color: #94A3B8; margin: 0; font-size: 0.9rem;">Giảng viên hướng dẫn:</p>
            <p style="color: #FBBF24; margin: 4px 0 0 0; font-size: 1.15rem; font-weight: bold;">ThS. Nguyễn Thị Hương Lý</p>
        </div>
        -->
    </div>
""", unsafe_allow_html=True)

st.markdown("<h3 style='color: #F8FAFC; font-size: 1.35rem; margin-bottom: 20px;'>⚙️ KIẾN TRÚC & LUỒNG HOẠT ĐỘNG HỆ THỐNG (AI-BI PIPELINE)</h3>", unsafe_allow_html=True)

# 2. SƠ ĐỒ LUỒNG HOẠT ĐỘNG THÔNG MINH (4 bước với class intro-card)
col_l1, col_l2, col_l3, col_l4 = st.columns(4)

with col_l1:
    st.markdown("""
        <div class="intro-card">
            <div style="font-size: 1.8rem; margin-bottom: 10px; text-shadow: 0 0 10px rgba(56, 189, 248, 0.25);">📂 Bước 1</div>
            <div class="glass-card-title" style="color: #38BDF8 !important;">Dữ Liệu CSV</div>
            <div class="glass-card-desc" style="font-size: 0.8rem; text-align: left;">
                Tải và hợp nhất dữ liệu từ các tệp tin CSV cục bộ (<b>data_sales.csv</b>, <b>data_products.csv</b>) thay vì sử dụng máy chủ cơ sở dữ liệu.
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_l2:
    st.markdown("""
        <div class="intro-card" style="border-top: 1px solid rgba(167, 139, 250, 0.3) !important;">
            <div style="font-size: 1.8rem; margin-bottom: 10px; color: #A78BFA; text-shadow: 0 0 10px rgba(167, 139, 250, 0.2);">📊 Bước 2</div>
            <div class="glass-card-title" style="color: #A78BFA !important;">Tiền Xử Lý</div>
            <div class="glass-card-desc" style="font-size: 0.8rem; text-align: left;">
                Tự động làm sạch dữ liệu giao dịch và tổng hợp theo chu kỳ <b>Tuần (Weekly)</b> tối ưu, loại bỏ nhiễu ngẫu nhiên để tránh quá khớp.
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_l3:
    st.markdown("""
        <div class="intro-card" style="border-top: 1px solid rgba(245, 158, 11, 0.3) !important;">
            <div style="font-size: 1.8rem; margin-bottom: 10px; color: #F59E0B; text-shadow: 0 0 10px rgba(245, 158, 11, 0.2);">🧠 Bước 3</div>
            <div class="glass-card-title" style="color: #F59E0B !important;">AI Forecasting</div>
            <div class="glass-card-desc" style="font-size: 0.8rem; text-align: left;">
                Huấn luyện song song 5 mô hình: <b>Linear Reg, Random Forest, XGBoost, ARIMA</b> và <b>Deep Learning LSTM</b> để đưa ra dự báo 6 tuần tiếp theo.
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_l4:
    st.markdown("""
        <div class="intro-card" style="border-top: 1px solid rgba(52, 211, 153, 0.3) !important;">
            <div style="font-size: 1.8rem; margin-bottom: 10px; color: #34D399; text-shadow: 0 0 10px rgba(52, 211, 153, 0.2);">📈 Bước 4</div>
            <div class="glass-card-title" style="color: #34D399 !important;">BI Analytics</div>
            <div class="glass-card-desc" style="font-size: 0.8rem; text-align: left;">
                Trực quan hóa Dashboard cao cấp cho phép tương tác lọc đa chiều và thay đổi linh hoạt chu kỳ Ngày/Tuần/Tháng/Năm.
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>---<br/>", unsafe_allow_html=True)

# 3. HỆ SINH THÁI CÔNG NGHỆ (TECHNOLOGY STACK BADGES)
st.markdown("<h3 style='color: #F8FAFC; font-size: 1.35rem; margin-bottom: 20px;'>🛠️ HỆ SINH THÁI CÔNG NGHỆ CỐT LÕI (TECHNOLOGY STACK)</h3>", unsafe_allow_html=True)

st.markdown("""
    <div style="display: flex; flex-wrap: wrap; gap: 15px; align-items: center; justify-content: center; margin-bottom: 40px;">
        <span style="background: rgba(56, 189, 248, 0.12); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.25); padding: 8px 18px; border-radius: 30px; font-size: 0.9rem; font-weight: 600;">🐍 Python 3.13</span>
        <span style="background: rgba(251, 191, 36, 0.12); color: #FBBF24; border: 1px solid rgba(251, 191, 36, 0.25); padding: 8px 18px; border-radius: 30px; font-size: 0.9rem; font-weight: 600;">📁 Local CSV Data Store</span>
        <span style="background: rgba(239, 68, 68, 0.12); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.25); padding: 8px 18px; border-radius: 30px; font-size: 0.9rem; font-weight: 600;">🔴 Streamlit Framework</span>
        <span style="background: rgba(167, 139, 250, 0.12); color: #A78BFA; border: 1px solid rgba(167, 139, 250, 0.25); padding: 8px 18px; border-radius: 30px; font-size: 0.9rem; font-weight: 600;">🤖 TensorFlow (LSTM)</span>
        <span style="background: rgba(52, 211, 153, 0.12); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.25); padding: 8px 18px; border-radius: 30px; font-size: 0.9rem; font-weight: 600;">⚡ XGBoost Regressor</span>
        <span style="background: rgba(244, 63, 94, 0.12); color: #F43F5E; border: 1px solid rgba(244, 63, 94, 0.25); padding: 8px 18px; border-radius: 30px; font-size: 0.9rem; font-weight: 600;">⚙️ Scikit-Learn</span>
        <span style="background: rgba(14, 165, 233, 0.12); color: #0EA5E9; border: 1px solid rgba(14, 165, 233, 0.25); padding: 8px 18px; border-radius: 30px; font-size: 0.9rem; font-weight: 600;">📈 Statsmodels (ARIMA)</span>
        <span style="background: rgba(100, 116, 139, 0.12); color: #94A3B8; border: 1px solid rgba(100, 116, 139, 0.25); padding: 8px 18px; border-radius: 30px; font-size: 0.9rem; font-weight: 600;">🐼 Pandas & Numpy</span>
    </div>
""", unsafe_allow_html=True)
