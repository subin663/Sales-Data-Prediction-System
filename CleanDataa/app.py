import streamlit as st
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

# Import shared database and ML data loading helpers to break circular dependencies
from utils import hash_password, load_base_data, authenticate, init_products_csv


# Cấu hình trang (Phải là lệnh Streamlit đầu tiên)
st.set_page_config(
    page_title="Hệ Thống Dự Báo Doanh Thu Bán Hàng - SAS",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PHONG CÁCH THIẾT KẾ PREMIUM (GLASSMORPHISM & SLATE DARK THEME) ---
# Được nhúng một lần ở app.py và áp dụng cho toàn bộ các trang con
st.markdown("""
<style>
    /* Nền chính và màu chữ */
    .stApp {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
    }
    
    /* Đồng bộ hóa thanh header trên cùng với Slate Dark Theme */
    [data-testid="stHeader"], header {
        background-color: #0F172A !important;
        background: #0F172A !important;
        border-bottom: 1px solid #1E293B !important;
    }
    
    /* Giao diện Sidebar trái */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B !important;
    }
    
    /* Chữ màu trắng cho menu điều hướng sidebar */
    [data-testid="stSidebar"] a span, 
    [data-testid="stSidebarNavItems"] span,
    [data-testid="stSidebarNav"] span {
        color: #F8FAFC !important;
        font-weight: 500 !important;
    }
    
    /* Chữ màu trắng cho tiêu đề st.expander trong sidebar */
    [data-testid="stSidebar"] details summary p,
    [data-testid="stSidebar"] details summary span,
    [data-testid="stSidebar"] details summary {
        color: #F8FAFC !important;
    }
    
    /* Tiêu đề sidebar */
    .sidebar-header {
        text-align: center;
        padding: 15px 10px;
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.1), rgba(139, 92, 246, 0.1));
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid rgba(56, 189, 248, 0.2);
    }
    
    /* Thiết kế Glassmorphism cho thẻ Metric */
    .glass-card {
        background: rgba(30, 41, 59, 0.45) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        padding: 22px !important;
        text-align: center !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
        height: 165px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        align-items: center !important;
    }
    
    .glass-card:hover {
        transform: translateY(-6px) !important;
        border-color: rgba(56, 189, 248, 0.4) !important;
        box-shadow: 0 12px 40px 0 rgba(56, 189, 248, 0.18) !important;
    }
    
    .glass-card-title {
        font-size: 0.85rem !important;
        color: #94A3B8 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.07em !important;
        margin-bottom: 10px !important;
        font-weight: 600 !important;
    }
    
    .glass-card-value {
        font-size: 1.9rem !important;
        font-weight: 700 !important;
        color: #38BDF8 !important;
        margin-bottom: 6px !important;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
    }
    
    .glass-card-desc {
        font-size: 0.75rem !important;
        color: #64748B !important;
    }
    
    /* Thiết kế Leaderboard Card */
    .leaderboard-card {
        background: rgba(30, 41, 59, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        margin-bottom: 12px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        transition: all 0.2s ease !important;
    }
    
    .leaderboard-card:hover {
        background: rgba(30, 41, 59, 0.5) !important;
        border-color: rgba(139, 92, 246, 0.3) !important;
    }
    
    /* Nút bấm (Buttons) */
    .stButton>button {
        background: linear-gradient(135deg, #0284C7, #0369A1) !important;
        color: #F8FAFC !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.2) !important;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #38BDF8, #0284C7) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.4) !important;
    }
    
    /* Thu nhỏ nút bấm trong sidebar */
    section[data-testid="stSidebar"] .stButton>button {
        padding: 6px 10px !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        border-radius: 6px !important;
        box-shadow: none !important;
    }
    
    section[data-testid="stSidebar"] .stButton>button:hover {
        transform: none !important;
        box-shadow: none !important;
    }
    
    /* Form đăng nhập */
    div[data-testid="stForm"] {
        background: rgba(30, 41, 59, 0.45) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 30px !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4) !important;
    }
    
    /* Thiết kế riêng cho nút Xác Thực đăng nhập (Màu xanh Emerald nổi bật) */
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #10B981, #059669) !important;
        color: #F8FAFC !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25) !important;
    }
    
    div[data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(135deg, #34D399, #10B981) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(52, 211, 153, 0.4) !important;
    }
    
    /* Đảm bảo chữ bên trong nút Đăng nhập luôn hiển thị màu trắng */
    div[data-testid="stFormSubmitButton"] button p {
        display: block !important;
        color: #F8FAFC !important;
        font-weight: 700 !important;
    }
    
    /* Chỉ ẩn dòng chữ hướng dẫn "Press Enter to submit" nằm bên ngoài nút */
    div[data-testid="stFormSubmitButton"] > p {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Hàm tạo tài khoản Admin và cấu trúc bảng NguoiDung mẫu nếu chưa tồn tại
def init_user_db():
    import os
    users_path = 'data/users.csv'
    if not os.path.exists(users_path):
        df_users = pd.DataFrame(columns=['username', 'password_hash', 'email', 'role', 'status', 'created_at'])
        hashed = hash_password("admin123")
        now_str = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        admin_row = pd.DataFrame([{
            'username': 'admin',
            'password_hash': hashed,
            'email': 'admin@sas.com',
            'role': 'Admin',
            'status': 'Active',
            'created_at': now_str
        }])
        df_users = pd.concat([df_users, admin_row], ignore_index=True)
        df_users.to_csv(users_path, index=False, encoding='utf-8')

# Khởi tạo DB User và Sản Phẩm
init_user_db()
init_products_csv()

# --- QUẢN LÝ TRẠNG THÁI ĐĂNG NHẬP ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'role' not in st.session_state:
    st.session_state['role'] = ""

# --- ĐỊNH NGHĨA CÁC TRANG (st.Page) ---
login_page = st.Page("login.py", title="Đăng Nhập", icon="🔒")
intro_page = st.Page("pages/introduction.py", title="Giới Thiệu Đề Tài", icon="📖")
dashboard_page = st.Page("pages/dashboard.py", title="Dashboard Tổng Quan", icon="📈")
preprocessing_page = st.Page("pages/preprocessing.py", title="Tiền Xử Lý & Đặc Trưng", icon="⚙️")
forecast_page = st.Page("pages/forecast.py", title="Dự Báo Doanh Thu", icon="🔮")
evaluation_page = st.Page("pages/evaluation.py", title="Đánh Giá & Huấn Luyện", icon="🏆")

# --- ĐIỀU HƯỚNG DỰA TRÊN ĐĂNG NHẬP ---
if st.session_state['logged_in']:
    # Tự động tạo đơn hàng nếu chế độ mô phỏng tự động đang bật
    if st.session_state.get('auto_sim', False):
        from utils import generate_simulated_sale
        res = generate_simulated_sale()
        if res:
            st.toast(f"⚡ Đơn mới: {res['quantity']}x {res['product_name'][:20]}... - ${res['revenue']:,.0f}", icon="🛒")
            st.cache_data.clear()

    # Hiển thị sidebar thông tin tài khoản ở app.py
    st.sidebar.markdown(f"""
        <div class="sidebar-header">
            <h3 style="color: #38BDF8; margin: 0; font-size: 1.4rem;">📊 HỆ THỐNG SAS</h3>
            <p style="color: #94A3B8; margin: 5px 0 10px 0; font-size: 0.9rem;">Tài khoản: <b>{st.session_state['username']}</b></p>
            <span style="background-color: #38BDF8; color: #0F172A; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; letter-spacing: 0.05em;">{st.session_state['role']}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Bảng điều khiển mô phỏng Real-time trong sidebar
    with st.sidebar:
        with st.expander("⚡ MÔ PHỎNG REAL-TIME", expanded=False):
            auto_sim = st.toggle("Tự động phát sinh đơn (5s)", value=st.session_state.get('auto_sim', False), key='auto_sim_toggle')
            st.session_state['auto_sim'] = auto_sim
            
            if st.button("➕ Tạo nhanh 1 đơn hàng", use_container_width=True):
                from utils import generate_simulated_sale
                res = generate_simulated_sale()
                if res:
                    st.toast(f"🛒 Đơn mới: {res['quantity']}x {res['product_name'][:20]}... - ${res['revenue']:,.0f}", icon="⚡")
                    st.success("Đã thêm 1 giao dịch!")
                    st.cache_data.clear()
                    st.rerun()
        st.markdown("---")

    # Hiển thị các trang chức năng (Đặt intro_page lên đầu làm trang chủ mặc định)
    pg = st.navigation([intro_page, dashboard_page, preprocessing_page, forecast_page, evaluation_page])
    
    # Nút làm mới dữ liệu và nút đăng xuất trong sidebar
    st.sidebar.markdown("<br/>", unsafe_allow_html=True)
    with st.sidebar:
        col_sb1, col_sb2 = st.columns(2)
        with col_sb1:
            if st.button("🔄 Làm mới", key="manual_refresh_btn"):
                st.cache_data.clear()
                st.rerun()
        with col_sb2:
            if st.button("🔓 Đăng Xuất"):
                st.session_state['logged_in'] = False
                st.session_state['username'] = ""
                st.session_state['role'] = ""
                st.rerun()
else:
    # Ẩn hoàn toàn các trang khác nếu chưa đăng nhập
    pg = st.navigation([login_page])

# Khởi chạy trang tương ứng
pg.run()

# --- TỰ ĐỘNG TẢI LẠI DỮ LIỆU KHÔNG BẰNG BLOCKING SLEEP (NON-BLOCKING AUTO-REFRESH) ---
if st.session_state['logged_in']:
    # Nếu đang bật mô phỏng, tải lại sau mỗi 5 giây, ngược lại sau mỗi 30 giây
    refresh_interval = 5000 if st.session_state.get('auto_sim', False) else 30000
    st.components.v1.html(
        f"""
        <script>
            setTimeout(function() {{
                const buttons = window.parent.document.querySelectorAll('button');
                for (const btn of buttons) {{
                    if (btn.innerText.includes('Làm mới') || btn.textContent.includes('Làm mới')) {{
                        btn.click();
                        break;
                    }}
                }}
            }}, {refresh_interval});
        </script>
        """,
        height=0
    )








