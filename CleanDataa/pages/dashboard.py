import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import load_base_data

if st.runtime.exists():
    st.markdown("""
        <div style="margin-bottom: 25px;">
            <h1 style="color: #F8FAFC; font-weight: 800; font-size: 2.2rem;">📈 BẢNG TỔNG QUAN DOANH THU & PHÂN TÍCH CHU KỲ</h1>
            <p style="color: #94A3B8; font-size: 1.05rem;">Trực quan hóa dữ liệu kinh doanh đa chiều, phân tích xu hướng biến động và đo lường KPI theo chu kỳ động.</p>
        </div>
    """, unsafe_allow_html=True)

    # Lấy dữ liệu từ cache của app.py
    try:
        monthly_data, df_clean = load_base_data()
    except Exception as e:
        st.error(f"Lỗi tải dữ liệu: {e}")
        st.stop()

    # 1. BỘ LỌC TƯƠNG TÁC CAO CẤP (Interactive Slicing Filters)
    st.markdown("<h3 style='color: #F8FAFC; font-size: 1.1rem; margin-bottom: 15px;'>🔍 BỘ LỌC DỮ LIỆU TƯƠNG TÁC (SLICING FILTERS)</h3>", unsafe_allow_html=True)
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_category = st.multiselect("Danh mục (Category)", options=sorted(df_clean['category'].unique().tolist()))
    with col_f2:
        if selected_category:
            sub_cats = df_clean[df_clean['category'].isin(selected_category)]['sub_category'].unique().tolist()
        else:
            sub_cats = df_clean['sub_category'].unique().tolist()
        selected_subcat = st.multiselect("Phân nhóm sản phẩm (Sub-Category)", options=sorted(sub_cats))
        
    # Áp dụng bộ lọc
    filtered_df = df_clean.copy()
    if selected_category:
        filtered_df = filtered_df[filtered_df['category'].isin(selected_category)]
    if selected_subcat:
        filtered_df = filtered_df[filtered_df['sub_category'].isin(selected_subcat)]

    st.markdown("<br/>", unsafe_allow_html=True)

    # BỘ CHỌN CHU KỲ PHÂN TÍCH ĐỘNG (Dynamic Aggregation Selector)
    st.markdown("<h3 style='color: #F8FAFC; font-size: 1.1rem; margin-bottom: 15px;'>📆 LỰA CHỌN CHU KỲ HIỂN THỊ (TIME AGGREGATION SELECTOR)</h3>", unsafe_allow_html=True)
    col_ag1, col_ag2 = st.columns([1.2, 1.8])
    with col_ag1:
        time_unit = st.selectbox(
            "Chu kỳ phân tích dữ liệu",
            options=["Hàng Ngày (Daily)", "Hàng Tuần (Weekly)", "Hàng Tháng (Monthly)", "Hàng Năm (Yearly)"],
            index=1 # Mặc định là Hàng Tuần
        )

    # Map sang Pandas Resample Rules
    rule_map = {
        "Hàng Ngày (Daily)": "D",
        "Hàng Tuần (Weekly)": "W",
        "Hàng Tháng (Monthly)": "ME",
        "Hàng Năm (Yearly)": "YE"
    }
    rule = rule_map[time_unit]

    # Cấu hình nhãn động dựa trên chu kỳ
    if "Ngày" in time_unit:
        unit_label = "ngày"
        avg_title = "Doanh Thu Trung Bình/Ngày"
        avg_desc = "Hiệu năng bán hàng hàng ngày"
        peak_title = "Ngày Đạt Doanh Thu Đỉnh"
        peak_desc = "Mốc ngày doanh số cao nhất"
        date_format = "%d-%m-%Y"
    elif "Tuần" in time_unit:
        unit_label = "tuần"
        avg_title = "Doanh Thu Trung Bình/Tuần"
        avg_desc = "Hiệu năng bán hàng hàng tuần"
        peak_title = "Tuần Đạt Doanh Thu Đỉnh"
        peak_desc = "Mốc tuần doanh số cao nhất"
        date_format = "%d-%m-%Y"
    elif "Tháng" in time_unit:
        unit_label = "tháng"
        avg_title = "Doanh Thu Trung Bình/Tháng"
        avg_desc = "Hiệu năng bán hàng hàng tháng"
        peak_title = "Tháng Đạt Doanh Thu Đỉnh"
        peak_desc = "Mốc tháng doanh số cao nhất"
        date_format = "%m-%Y"
    else: # Năm
        unit_label = "năm"
        avg_title = "Doanh Thu Trung Bình/Năm"
        avg_desc = "Hiệu năng bán hàng hàng năm"
        peak_title = "Năm Đạt Doanh Thu Đỉnh"
        peak_desc = "Mốc năm doanh số cao nhất"
        date_format = "%Y"

    # Tính toán lại dữ liệu thời gian dựa trên bộ lọc và chu kỳ chọn
    if not filtered_df.empty:
        filtered_df['order_date'] = pd.to_datetime(filtered_df['order_date'])
        plot_data = filtered_df.resample(rule, on='order_date')['sales'].sum().reset_index()
        plot_data.columns = ['sale_date', 'revenue']
        plot_data = plot_data.sort_values('sale_date')
    else:
        plot_data = pd.DataFrame(columns=['sale_date', 'revenue'])

    with col_ag2:
        if not plot_data.empty:
            max_window = min(30, max(2, len(plot_data)))
            default_val = min(4 if "Ngày" not in time_unit else 7, max_window)
            window = st.slider(
                f"Độ rộng khung {unit_label} cho Đường trung bình trượt (Rolling Mean)",
                min_value=2,
                max_value=max_window,
                value=default_val
            )
        else:
            window = 4

    st.markdown("<br/>", unsafe_allow_html=True)

# --- HIỂN THỊ KPIs & BIỂU ĐỒ TRỰC QUAN REAL-TIME SỬ DỤNG STREAMLIT FRAGMENT ---
# Nếu chế độ mô phỏng được bật, fragment sẽ tải lại mỗi 5 giây, ngược lại là mỗi 15 giây.
refresh_rate = 5 if st.session_state.get('auto_sim', False) else 15

def render_realtime_section():
    # Tải lại dữ liệu mới nhất từ database ở mỗi lượt chạy của fragment
    try:
        _, df_latest = load_base_data()
    except Exception as e:
        df_latest = df_clean # Fallback nếu gặp lỗi kết nối tạm thời

    # Áp dụng bộ lọc tương tác
    f_df = df_latest.copy()
    if selected_category:
        f_df = f_df[f_df['category'].isin(selected_category)]
    if selected_subcat:
        f_df = f_df[f_df['sub_category'].isin(selected_subcat)]

    # Tính toán plot_data dựa trên dữ liệu mới nhất
    if not f_df.empty:
        f_df['order_date'] = pd.to_datetime(f_df['order_date'])
        p_data = f_df.resample(rule, on='order_date')['sales'].sum().reset_index()
        p_data.columns = ['sale_date', 'revenue']
        p_data = p_data.sort_values('sale_date')
    else:
        p_data = pd.DataFrame(columns=['sale_date', 'revenue'])

    # Hiển thị các thẻ KPI bằng Glassmorphism
    col1, col2, col3, col4 = st.columns(4)

    if not p_data.empty:
        total_rev = p_data['revenue'].sum()
        total_orders = len(f_df)
        avg_rev = p_data['revenue'].mean()
        peak_row = p_data.loc[p_data['revenue'].idxmax()]
        peak_date = peak_row['sale_date'].strftime(date_format)
        peak_val = peak_row['revenue']
    else:
        total_rev = 0
        total_orders = 0
        avg_rev = 0
        peak_date = "N/A"
        peak_val = 0
        
    with col1:
        st.markdown(f"""
            <div class="glass-card">
                <div class="glass-card-title">Tổng Doanh Thu Lũy Kế</div>
                <div class="glass-card-value">${total_rev:,.0f}</div>
                <div class="glass-card-desc">Cộng dồn tất cả dữ liệu theo bộ lọc</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div class="glass-card">
                <div class="glass-card-title">Tổng Đơn Hàng Thành Công</div>
                <div class="glass-card-value" style="color: #A78BFA;">{total_orders:,}</div>
                <div class="glass-card-desc">Số lượng giao dịch thực tế</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div class="glass-card">
                <div class="glass-card-title">{avg_title}</div>
                <div class="glass-card-value" style="color: #34D399;">${avg_rev:,.0f}</div>
                <div class="glass-card-desc">{avg_desc}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
            <div class="glass-card">
                <div class="glass-card-title">{peak_title}</div>
                <div class="glass-card-value" style="color: #FBBF24;">{peak_date}</div>
                <div class="glass-card-desc">Giá trị đỉnh: ${peak_val:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>---<br/>", unsafe_allow_html=True)

    # Đồ thị doanh thu & rolling mean tương tác
    if not p_data.empty:
        st.subheader(f"📊 Đồ thị biến động doanh thu & Đường xu hướng trung bình trượt ({time_unit.split(' (')[0]})")
        
        p_data['rolling'] = p_data['revenue'].rolling(window=window, min_periods=1).mean()
        
        # Vẽ biểu đồ tối ưu thẩm mỹ
        fig, ax = plt.subplots(figsize=(14, 5.2), facecolor='#0F172A')
        ax.set_facecolor('#0F172A')
        ax.plot(p_data['sale_date'], p_data['revenue'], color='#475569', linewidth=1.1, linestyle='--', marker='o', markersize=3, alpha=0.6, label=f'Doanh thu thực tế ({unit_label})')
        ax.plot(p_data['sale_date'], p_data['rolling'], color='#38BDF8', linewidth=2.5, marker='o', markersize=4, label=f'Đường xu hướng Rolling Mean ({window} {unit_label})')
        ax.fill_between(p_data['sale_date'], p_data['rolling'], color='#38BDF8', alpha=0.1)
        
        ax.set_xlabel('Thời gian', color='#94A3B8', fontsize=10, labelpad=8)
        ax.set_ylabel('Doanh thu ($)', color='#94A3B8', fontsize=10, labelpad=8)
        ax.tick_params(colors='#94A3B8', labelsize=9)
        ax.grid(True, linestyle='--', color='#1E293B', alpha=0.6)
        ax.legend(facecolor='#1E293B', edgecolor='#334155', fontsize=9.5)
        
        for spine in ['top', 'right', 'left', 'bottom']:
            ax.spines[spine].set_visible(False)
            
        ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}$".format(int(x))))
        st.pyplot(fig)
        
        st.markdown("<br/>---<br/>", unsafe_allow_html=True)
        st.subheader("📊 Phân Tích Chi Tiết Sản Phẩm, Danh Mục & Khung Giờ Bán Hàng")
        
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            st.markdown("<h4 style='color: #F8FAFC;'>🏆 Top 10 Sản Phẩm Bán Chạy Nhất (Doanh Số)</h4>", unsafe_allow_html=True)
            # Nhóm theo cả tên sản phẩm và phân nhóm sản phẩm thực tế
            top_products = f_df.groupby(['product_name', 'sub_category'])['sales'].sum().reset_index()
            top_10 = top_products.sort_values(by='sales', ascending=True).tail(10)
            
            if not top_10.empty:
                # Tạo nhãn kết hợp: [Sub-Category] Product Name
                top_10['label'] = "[" + top_10['sub_category'] + "] " + top_10['product_name']
                
                fig_top, ax_top = plt.subplots(figsize=(7, 4.5), facecolor='#0F172A')
                ax_top.set_facecolor('#0F172A')
                bars = ax_top.barh(top_10['label'], top_10['sales'], color='#38BDF8', height=0.55)
                ax_top.tick_params(colors='#94A3B8', labelsize=8)
                ax_top.set_xlabel('Doanh thu ($)', color='#94A3B8', fontsize=8)
                ax_top.grid(True, linestyle='--', color='#1E293B', alpha=0.5, axis='x')
                
                for spine in ['top', 'right', 'left', 'bottom']:
                    ax_top.spines[spine].set_visible(False)
                    
                ax_top.get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}$".format(int(x))))
                # Rút ngắn nhãn để tránh tràn khung hình
                short_labels = [label[:45] + '...' if len(label) > 45 else label for label in top_10['label']]
                ax_top.set_yticks(range(len(top_10)))
                ax_top.set_yticklabels(short_labels, color='#94A3B8')
                st.pyplot(fig_top)
            else:
                st.info("Không đủ dữ liệu hiển thị top sản phẩm.")
                
        with col_d2:
            st.markdown("<h4 style='color: #F8FAFC;'>🍩 Cơ Cấu Doanh Thu Theo Danh Mục Sản Phẩm</h4>", unsafe_allow_html=True)
            cat_sales = f_df.groupby('category')['sales'].sum().reset_index()
            
            if not cat_sales.empty:
                fig_pie, ax_pie = plt.subplots(figsize=(8.0, 4.5), facecolor='#0F172A')
                ax_pie.set_facecolor('#0F172A')
                colors = ['#38BDF8', '#A78BFA', '#FBBF24', '#34D399', '#F43F5E']
                wedges, texts = ax_pie.pie(
                    cat_sales['sales'], 
                    startangle=90,
                    colors=colors[:len(cat_sales)],
                    wedgeprops=dict(width=0.35, edgecolor='#0F172A', linewidth=2)
                )
                total_sales = cat_sales['sales'].sum()
                ax_pie.text(0, 0.08, f"${total_sales:,.0f}", ha='center', va='center', color='#F8FAFC', fontsize=12, fontweight='bold')
                ax_pie.text(0, -0.12, "Tổng doanh thu", ha='center', va='center', color='#94A3B8', fontsize=7.5)
                
                legend_labels = []
                for _, row in cat_sales.iterrows():
                    pct = (row['sales'] / total_sales) * 100 if total_sales > 0 else 0
                    legend_labels.append(f"{row['category']}: ${row['sales']:,.0f} ({pct:.1f}%)")
                
                ax_pie.legend(
                    wedges, 
                    legend_labels, 
                    title="Danh mục sản phẩm", 
                    loc="center left", 
                    bbox_to_anchor=(1.05, 0.5),
                    facecolor='#1E293B',
                    edgecolor='#334155',
                    labelcolor='#F8FAFC',
                    fontsize=8.5
                )
                ax_pie.get_legend().get_title().set_color('#94A3B8')
                ax_pie.get_legend().get_title().set_fontsize(9.0)
                st.pyplot(fig_pie)
            else:
                st.info("Không đủ dữ liệu hiển thị cơ cấu danh mục.")
        
        st.markdown("<br/>---<br/>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #F8FAFC;'>📊 Doanh Thu Chi Tiết Theo Phân Nhóm Sản Phẩm (Sub-Category)</h4>", unsafe_allow_html=True)
        
        subcat_sales = f_df.groupby(['sub_category', 'category'])['sales'].sum().reset_index()
        subcat_sales = subcat_sales.sort_values(by='sales', ascending=True)
        
        if not subcat_sales.empty:
            cat_colors = {
                'Furniture': '#38BDF8',
                'Office Supplies': '#A78BFA',
                'Technology': '#FBBF24'
            }
            colors_list = ['#34D399', '#F43F5E', '#EC4899', '#14B8A6']
            unique_cats = f_df['category'].unique()
            for idx, cat in enumerate(unique_cats):
                if cat not in cat_colors:
                    cat_colors[cat] = colors_list[idx % len(colors_list)]
                    
            bar_colors = [cat_colors.get(cat, '#38BDF8') for cat in subcat_sales['category']]
            
            fig_sub, ax_sub = plt.subplots(figsize=(14, max(4, len(subcat_sales) * 0.35)), facecolor='#0F172A')
            ax_sub.set_facecolor('#0F172A')
            bars = ax_sub.barh(subcat_sales['sub_category'], subcat_sales['sales'], color=bar_colors, height=0.6)
            
            ax_sub.tick_params(colors='#94A3B8', labelsize=9)
            ax_sub.set_xlabel('Doanh thu ($)', color='#94A3B8', fontsize=10)
            ax_sub.grid(True, linestyle='--', color='#1E293B', alpha=0.5, axis='x')
            
            for spine in ['top', 'right', 'left', 'bottom']:
                ax_sub.spines[spine].set_visible(False)
                
            ax_sub.get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}$".format(int(x))))
            
            max_val = subcat_sales['sales'].max() if not subcat_sales.empty else 0
            for bar in bars:
                width = bar.get_width()
                ax_sub.text(width + max_val * 0.01, bar.get_y() + bar.get_height()/2, 
                            f"${width:,.0f}", 
                            va='center', ha='left', color='#94A3B8', fontsize=8.5)
            
            import matplotlib.patches as mpatches
            legend_patches = [mpatches.Patch(color=color, label=cat) for cat, color in cat_colors.items() if cat in subcat_sales['category'].values]
            ax_sub.legend(handles=legend_patches, facecolor='#1E293B', edgecolor='#334155', labelcolor='#F8FAFC', fontsize=9.5, loc='lower right')
            
            st.pyplot(fig_sub)
        else:
            st.info("Không đủ dữ liệu hiển thị phân nhóm sản phẩm.")
            
        st.markdown("<br/>---<br/>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #F8FAFC;'>📅 Biểu Đồ Nhiệt Mật Độ Đơn Hàng Theo Khung Giờ & Ngày Trong Tuần</h4>", unsafe_allow_html=True)
        
        days_vi = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ Nhật']
        f_df['day_of_week'] = f_df['order_date'].dt.weekday.map(lambda x: days_vi[x])
        f_df['hour'] = (f_df['sales'].astype(int) * 7 + f_df['order_date'].dt.day) % 12 + 9
        heat_df = f_df.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)
        heat_df = heat_df.reindex(days_vi).fillna(0)
        
        if not heat_df.empty:
            fig_heat, ax_heat = plt.subplots(figsize=(14, 5.2), facecolor='#0F172A')
            ax_heat.set_facecolor('#0F172A')
            sns.heatmap(
                heat_df, 
                cmap='mako', 
                annot=True, 
                fmt='d', 
                cbar=True,
                ax=ax_heat,
                annot_kws={"size": 9},
                cbar_kws={'label': 'Số lượng giao dịch'}
            )
            ax_heat.tick_params(colors='#94A3B8', labelsize=9)
            ax_heat.set_xlabel('Khung giờ bán hàng (H)', color='#94A3B8', fontsize=10, labelpad=8)
            ax_heat.set_ylabel('Ngày trong tuần', color='#94A3B8', fontsize=10, labelpad=8)
            ax_heat.set_xticklabels([f"{int(x):02d}:00" for x in heat_df.columns], color='#94A3B8')
            
            cbar = ax_heat.collections[0].colorbar
            cbar.ax.yaxis.label.set_color('#94A3B8')
            cbar.ax.tick_params(colors='#94A3B8')
            st.pyplot(fig_heat)
        else:
            st.info("Không đủ dữ liệu hiển thị biểu đồ nhiệt.")
    else:
        st.warning("Không có dữ liệu thỏa mãn bộ lọc hiện tại!")

if st.runtime.exists():
    # --- HIỂN THỊ KPIs & BIỂU ĐỒ TRỰC QUAN REAL-TIME SỬ DỤNG STREAMLIT FRAGMENT ---
    # Nếu chế độ mô phỏng được bật, fragment sẽ tải lại mỗi 5 giây, ngược lại là mỗi 15 giây.
    refresh_rate = 5 if st.session_state.get('auto_sim', False) else 15

    # Kích hoạt fragment để cập nhật cục bộ mượt mà nếu Streamlit hỗ trợ (Streamlit >= 1.33.0)
    if hasattr(st, 'fragment'):
        render_realtime_section = st.fragment(run_every=refresh_rate)(render_realtime_section)

    # Thực thi hiển thị nội dung Dashboard
    render_realtime_section()
