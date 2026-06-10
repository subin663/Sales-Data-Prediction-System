import streamlit as st
from utils import authenticate

st.markdown("""
    <div style="text-align: center; margin-top: 50px; margin-bottom: 25px;">
        <h1 style="color: #38BDF8; font-weight: 800; font-size: 2.6rem; letter-spacing: -0.02em;">📊 HỆ THỐNG DỰ BÁO DOANH THU SAS</h1>
        <p style="color: #94A3B8; font-size: 1.15rem; font-weight: 400;">Hệ thống phân tích kinh doanh tích hợp Trí tuệ nhân tạo (AI-BI Platform)</p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1.1, 1.8, 1.1])
with col2:
    with st.form("login_form"):
        st.markdown("<h3 style='text-align: center; margin-bottom: 20px; color: #F8FAFC;'>🔑 ĐĂNG NHẬP HỆ THỐNG</h3>", unsafe_allow_html=True)
        username_input = st.text_input("Tài khoản (Username)", placeholder="Nhập tên tài khoản của bạn...")
        password_input = st.text_input("Mật khẩu (Password)", type="password", placeholder="Nhập mật khẩu...")
        submit_button = st.form_submit_button("Đăng Nhập (Login)")
        
        if submit_button:
            user_info = authenticate(username_input, password_input)
            if user_info:
                role, status = user_info
                if status == 'Active':
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username_input
                    st.session_state['role'] = role
                    st.success(f"Chào mừng {username_input}! Đang tải trang điều khiển...")
                    st.rerun()
                else:
                    st.error("Tài khoản của bạn hiện đang bị khóa tạm thời!")
            else:
                st.error("Sai tên đăng nhập hoặc mật khẩu!")
    
