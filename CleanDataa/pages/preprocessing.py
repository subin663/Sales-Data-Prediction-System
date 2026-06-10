import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


st.markdown("""
    <div style="margin-bottom: 25px;">
        <h1 style="color: #F8FAFC; font-weight: 800; font-size: 2.2rem;">⚙️ TIỀN XỬ LÝ DỮ LIỆU & ĐẶC TRƯNG</h1>
        <p style="color: #94A3B8; font-size: 1.05rem;">Phân tích trực quan quá trình làm sạch dữ liệu ngoại lai và cấu hình các đặc trưng chuỗi thời gian động.</p>
    </div>
""", unsafe_allow_html=True)

# Tải dữ liệu thô phục vụ tiền xử lý trực tuyến
@st.cache_data
def load_raw_data():
    try:
        df = pd.read_csv('data/test.csv', encoding='latin1')
        df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
        df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
        # Loại bỏ các dòng trống ở các trường dữ liệu cốt lõi
        df_clean = df.dropna(subset=['Order Date', 'Product Name', 'Sales'])
        df_clean = df_clean[df_clean['Sales'] > 0]
        return df_clean
    except Exception as e:
        st.error(f"Lỗi tải dữ liệu thô: {e}")
        return pd.DataFrame()

df_raw = load_raw_data()

if df_raw.empty:
    st.warning("Không thể tải tập dữ liệu thô 'data/test.csv'. Vui lòng kiểm tra lại đường dẫn!")
    st.stop()

# Khởi tạo 2 Tab tương tác
tab1, tab2 = st.tabs(["🧹 Làm sạch & Loại bỏ Outliers", "🧠 Kỹ nghệ Đặc trưng (Feature Engineering)"])

# ----------------- TAB 1: OUTLIERS -----------------
with tab1:
    st.markdown("<h3 style='color: #F8FAFC; font-size: 1.3rem; margin-bottom: 15px;'>🔍 Loại bỏ giá trị ngoại lai (Outliers Detection)</h3>", unsafe_allow_html=True)
    
    col_ctrl1, col_ctrl2 = st.columns([1, 1])
    with col_ctrl1:
        method = st.selectbox(
            "Phương pháp phát hiện ngoại lai",
            options=["Phương pháp Z-Score (Theo từng sản phẩm)", "Phương pháp IQR (Theo từng sản phẩm)"]
        )
    with col_ctrl2:
        if "Z-Score" in method:
            threshold = st.slider("Ngưỡng Z-Score (|Z| >= threshold)", min_value=2.0, max_value=4.0, value=3.0, step=0.1)
        else:
            threshold = st.slider("Hệ số k của khoảng IQR (Q3 + k*IQR)", min_value=1.0, max_value=3.0, value=1.5, step=0.1)

    # Thực thi tính toán Outlier theo nhóm sản phẩm để sát thực tế notebook
    df_cleaned = df_raw.copy()
    
    if "Z-Score" in method:
        # Tính z-score theo từng nhóm sản phẩm
        z_scores = df_raw.groupby('Product Name')['Sales'].transform(lambda x: ((x - x.mean()) / x.std()).abs() if x.std() > 0 else 0).fillna(0)
        outlier_mask = z_scores >= threshold
    else:
        # Tính IQR theo từng nhóm sản phẩm
        Q1 = df_raw.groupby('Product Name')['Sales'].transform(lambda x: x.quantile(0.25))
        Q3 = df_raw.groupby('Product Name')['Sales'].transform(lambda x: x.quantile(0.75))
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        outlier_mask = (df_raw['Sales'] < lower_bound) | (df_raw['Sales'] > upper_bound)
        
    df_cleaned = df_raw[~outlier_mask]
    num_outliers = outlier_mask.sum()
    pct_outliers = (num_outliers / len(df_raw)) * 100

    # Hiển thị số liệu kết quả bằng Glassmorphism
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        st.markdown(f"""
            <div class="glass-card">
                <div class="glass-card-title">Dòng dữ liệu ban đầu</div>
                <div class="glass-card-value">{len(df_raw):,}</div>
                <div class="glass-card-desc">Giao dịch thô đã làm sạch null</div>
            </div>
        """, unsafe_allow_html=True)
    with col_kpi2:
        st.markdown(f"""
            <div class="glass-card" style="border-color: rgba(244, 63, 94, 0.3) !important;">
                <div class="glass-card-title" style="color: #F43F5E;">Số Ngoại Lai Bị Loại Bỏ</div>
                <div class="glass-card-value" style="color: #F43F5E;">{num_outliers:,}</div>
                <div class="glass-card-desc">Tỷ lệ loại bỏ: {pct_outliers:.2f}%</div>
            </div>
        """, unsafe_allow_html=True)
    with col_kpi3:
        st.markdown(f"""
            <div class="glass-card" style="border-color: rgba(52, 211, 153, 0.3) !important;">
                <div class="glass-card-title" style="color: #34D399;">Dữ Liệu Sạch Còn Lại</div>
                <div class="glass-card-value" style="color: #34D399;">{len(df_cleaned):,}</div>
                <div class="glass-card-desc">Được đưa vào tổng hợp tuần</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>---<br/>", unsafe_allow_html=True)
    st.subheader("📊 So sánh phân bố doanh số trước và sau khi lọc ngoại lai (Boxplot)")

    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("<p style='text-align: center; color: #F43F5E; font-weight: bold;'>Trước khi lọc ngoại lai (Raw Sales)</p>", unsafe_allow_html=True)
        fig_b, ax_b = plt.subplots(figsize=(6, 4.2), facecolor='#0F172A')
        ax_b.set_facecolor('#0F172A')
        
        # Vẽ boxplot của dữ liệu thô
        sns.boxplot(y=df_raw['Sales'], ax=ax_b, color='#F43F5E', width=0.4)
        ax_b.tick_params(colors='#94A3B8', labelsize=9)
        ax_b.set_ylabel('Giá trị giao dịch ($)', color='#94A3B8')
        ax_b.grid(True, linestyle='--', color='#1E293B', alpha=0.5)
        for spine in ['top', 'right', 'left', 'bottom']:
            ax_b.spines[spine].set_visible(False)
        ax_b.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}$".format(int(x))))
        st.pyplot(fig_b)
        
    with col_g2:
        st.markdown("<p style='text-align: center; color: #34D399; font-weight: bold;'>Sau khi lọc ngoại lai (Cleaned Sales)</p>", unsafe_allow_html=True)
        fig_a, ax_a = plt.subplots(figsize=(6, 4.2), facecolor='#0F172A')
        ax_a.set_facecolor('#0F172A')
        
        # Vẽ boxplot của dữ liệu sạch
        sns.boxplot(y=df_cleaned['Sales'], ax=ax_a, color='#34D399', width=0.4)
        ax_a.tick_params(colors='#94A3B8', labelsize=9)
        ax_a.set_ylabel('Giá trị giao dịch ($)', color='#94A3B8')
        ax_a.grid(True, linestyle='--', color='#1E293B', alpha=0.5)
        for spine in ['top', 'right', 'left', 'bottom']:
            ax_a.spines[spine].set_visible(False)
        ax_a.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}$".format(int(x))))
        st.pyplot(fig_a)

# ----------------- TAB 2: FEATURE ENGINEERING -----------------
with tab2:
    st.markdown("<h3 style='color: #F8FAFC; font-size: 1.3rem; margin-bottom: 15px;'>⚙️ Xây dựng các đặc trưng chuỗi thời gian tuần</h3>", unsafe_allow_html=True)
    st.info("Để chuyển đổi chuỗi thời gian đơn biến thành bài toán học máy có giám sát (Supervised Learning), chúng tôi xây dựng Lag Features (biến trễ) và Rolling Mean (trung bình trượt) động dựa trên dữ liệu doanh thu tuần đã làm sạch.")

    col_fe1, col_fe2 = st.columns(2)
    with col_fe1:
        num_lags = st.slider("Số lượng biến trễ để tạo (Lag Features)", min_value=1, max_value=5, value=3, step=1)
    with col_fe2:
        rolling_window = st.slider("Độ rộng cửa sổ trung bình trượt (Rolling Mean Window)", min_value=2, max_value=8, value=4, step=1)

    # 1. Gom nhóm tuần dữ liệu đã làm sạch ở Tab 1
    df_weekly = df_cleaned.resample('W', on='Order Date')['Sales'].sum().reset_index()
    df_weekly.columns = ['sale_date', 'revenue']
    df_weekly = df_weekly.sort_values('sale_date')

    # 2. Tạo đặc trưng động
    df_features = df_weekly.copy()
    
    # Tạo Lag Features
    for i in range(1, num_lags + 1):
        df_features[f'Lag_{i}'] = df_features['revenue'].shift(i)
        
    # Tạo Rolling Mean
    df_features[f'Rolling_Mean_{rolling_window}W'] = df_features['revenue'].rolling(window=rolling_window).mean()

    st.markdown("<h4 style='color: #F8FAFC;'>📋 Xem trước Bảng dữ liệu đặc trưng sau khi xử lý (15 dòng đầu tiên)</h4>", unsafe_allow_html=True)
    
    # Định dạng hiển thị ngày và tiền tệ (Làm tròn đến 2 chữ số thập phân)
    df_features_display = df_features.round(0)
    df_features_display['sale_date'] = df_features['sale_date'].dt.strftime('%d-%m-%Y')
    
    # Hiển thị dataframe
    st.dataframe(
        df_features_display.head(15).style.format({
            col: "${:,.0f}" for col in df_features_display.columns if col != 'sale_date'
        }),
        use_container_width=True
    )
    
    # Nút bấm đẩy dữ liệu vào CSV
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("💾 LƯU DỮ LIỆU ĐÃ XỬ LÝ XUỐNG CSV (processed_data.csv)"):
        # Tính toán chính xác các cột như yêu cầu của người dùng (làm tròn đến 2 chữ số thập phân)
        df_db = df_weekly.copy()
        df_db['revenue'] = df_db['revenue'].round(0)
        df_db['lag_1'] = df_db['revenue'].shift(1).round(0)
        df_db['lag_2'] = df_db['revenue'].shift(2).round(0)
        df_db['lag_4'] = df_db['revenue'].shift(4).round(0)
        df_db['rolling_mean_4'] = df_db['revenue'].rolling(window=4).mean().round(0)
        df_db['month_num'] = df_db['sale_date'].dt.month
        df_db['week_of_year'] = df_db['sale_date'].dt.isocalendar().week
        
        status_db = st.status("🔄 Đang ghi dữ liệu đặc trưng xuống tệp CSV...", expanded=True)
        try:
            # Tạo bản ghi lưu trữ
            df_db['created_at'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            df_db.to_csv('data/processed_data.csv', index=False, encoding='utf-8')
            status_db.update(state="complete", label="🎉 Lưu dữ liệu vào data/processed_data.csv thành công!")
            st.success(f"🎉 **Thành công!** Đã lưu toàn bộ {len(df_db)} dòng dữ liệu đặc trưng vào tệp **data/processed_data.csv** cục bộ.")
        except Exception as ex:
            status_db.update(state="error", label="❌ Lỗi khi lưu tệp CSV!")
            st.error(f"Chi tiết lỗi: {ex}")
            
    st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.3); border: 1px solid rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 10px; margin-top: 15px;">
            <p style="color: #94A3B8; margin: 0; font-size: 0.85rem;">
                <b>Lưu ý cấu trúc dữ liệu học máy:</b><br/>
                - <b>Các cột Lag_1, Lag_2, ...</b> đóng vai trò là các đặc trưng đầu vào (Features) để dự báo.<br/>
                - <b>Các dòng đầu tiên</b> xuất hiện giá trị <code>NaN</code> (None) do không có đủ dữ liệu lịch sử phía trước để dịch chuyển hoặc tính trung bình trượt. Các giá trị này sẽ tự động được loại bỏ trước khi đưa vào huấn luyện mô hình.
            </p>
        </div>
    """, unsafe_allow_html=True)
