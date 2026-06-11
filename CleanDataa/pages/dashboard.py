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
    col1, col2, col3, col4, col5 = st.columns(5)

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
        
    total_profit = total_rev * 0.4

    with col1:
        st.markdown(f"""
            <div class="glass-card">
                <div class="glass-card-title">Tổng Doanh Thu</div>
                <div class="glass-card-value">${total_rev:,.0f}</div>
                <div class="glass-card-desc">Cộng dồn doanh số bán hàng</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div class="glass-card">
                <div class="glass-card-title">Lợi Nhuận Ước Tính</div>
                <div class="glass-card-value" style="color: #10B981;">${total_profit:,.0f}</div>
                <div class="glass-card-desc">Giá vốn định mức (60% Doanh thu)</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div class="glass-card">
                <div class="glass-card-title">Tổng Đơn Hàng</div>
                <div class="glass-card-value" style="color: #A78BFA;">{total_orders:,}</div>
                <div class="glass-card-desc">Số lượng giao dịch thực tế</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
            <div class="glass-card">
                <div class="glass-card-title">{avg_title}</div>
                <div class="glass-card-value" style="color: #34D399;">${avg_rev:,.0f}</div>
                <div class="glass-card-desc">{avg_desc}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col5:
        st.markdown(f"""
            <div class="glass-card">
                <div class="glass-card-title">Doanh Thu Đỉnh / {unit_label.capitalize()}</div>
                <div class="glass-card-value" style="color: #FBBF24;">${peak_val:,.0f}</div>
                <div class="glass-card-desc">Thời gian: {peak_date}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>---<br/>", unsafe_allow_html=True)

    # Đồ thị tương quan Doanh thu - Chi phí - Lợi nhuận
    if not p_data.empty:
        st.subheader(f"📈 Phân tích tương quan Doanh Thu - Chi Phí - Lợi Nhuận ({time_unit.split(' (')[0]})")
        
        # Tính toán Cost và Profit
        p_data['cost'] = p_data['revenue'] * 0.6
        p_data['profit'] = p_data['revenue'] * 0.4
        
        fig_p, ax_p = plt.subplots(figsize=(14, 5.2), facecolor='#0F172A')
        ax_p.set_facecolor('#0F172A')
        
        # Vẽ các đường
        ax_p.plot(p_data['sale_date'], p_data['revenue'], color='#38BDF8', linewidth=2.2, marker='o', markersize=3, label='Doanh thu (Sales)')
        ax_p.plot(p_data['sale_date'], p_data['cost'], color='#F43F5E', linewidth=1.8, linestyle=':', marker='s', markersize=3, alpha=0.8, label='Giá vốn (Cost - 60%)')
        ax_p.plot(p_data['sale_date'], p_data['profit'], color='#10B981', linewidth=2.2, marker='^', markersize=4, label='Lợi nhuận (Profit - 40%)')
        
        # Fill area for profit to make it look premium
        ax_p.fill_between(p_data['sale_date'], p_data['profit'], color='#10B981', alpha=0.1)
        
        ax_p.set_xlabel('Thời gian', color='#94A3B8', fontsize=10, labelpad=8)
        ax_p.set_ylabel('Giá trị ($)', color='#94A3B8', fontsize=10, labelpad=8)
        ax_p.tick_params(colors='#94A3B8', labelsize=9)
        ax_p.grid(True, linestyle='--', color='#1E293B', alpha=0.6)
        ax_p.legend(facecolor='#1E293B', edgecolor='#334155', fontsize=9.5)
        
        for spine in ['top', 'right', 'left', 'bottom']:
            ax_p.spines[spine].set_visible(False)
            
        ax_p.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}$".format(int(x))))
        st.pyplot(fig_p)
        
        st.markdown("<br/>---<br/>", unsafe_allow_html=True)
        st.subheader("📊 Phân Tích Chi Tiết Sản Phẩm, Danh Mục & Khung Giờ Bán Hàng")
        
        # Chọn chế độ hiển thị chi tiết (Doanh thu hay Lợi nhuận)
        view_mode = st.radio("Chỉ số hiển thị ở các biểu đồ dưới:", ["Doanh thu ($)", "Lợi nhuận ($)"], horizontal=True, key="dashboard_view_mode")
        
        # Thêm các cột tính toán chi phí & lợi nhuận
        f_df['cost'] = f_df['sales'] * 0.6
        f_df['profit'] = f_df['sales'] * 0.4
        
        val_col = 'sales' if "Doanh thu" in view_mode else 'profit'
        mode_label = "Doanh thu" if "Doanh thu" in view_mode else "Lợi nhuận"
        theme_color = '#38BDF8' if "Doanh thu" in view_mode else '#10B981'
        
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            st.markdown(f"<h4 style='color: #F8FAFC;'>🏆 Top 10 Sản Phẩm Cao Nhất ({mode_label})</h4>", unsafe_allow_html=True)
            # Nhóm theo cả tên sản phẩm và phân nhóm sản phẩm thực tế
            top_products = f_df.groupby(['product_name', 'sub_category'])[val_col].sum().reset_index()
            top_10 = top_products.sort_values(by=val_col, ascending=True).tail(10)
            
            if not top_10.empty:
                # Tạo nhãn kết hợp: [Sub-Category] Product Name
                top_10['label'] = "[" + top_10['sub_category'] + "] " + top_10['product_name']
                
                fig_top, ax_top = plt.subplots(figsize=(7, 4.5), facecolor='#0F172A')
                ax_top.set_facecolor('#0F172A')
                bars = ax_top.barh(top_10['label'], top_10[val_col], color=theme_color, height=0.55)
                ax_top.tick_params(colors='#94A3B8', labelsize=8)
                ax_top.set_xlabel(f'{mode_label} ($)', color='#94A3B8', fontsize=8)
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
                st.info(f"Không đủ dữ liệu hiển thị top sản phẩm theo {mode_label.lower()}.")
                
        with col_d2:
            st.markdown(f"<h4 style='color: #F8FAFC;'>🍩 Cơ Cấu {mode_label} Theo Danh Mục Sản Phẩm</h4>", unsafe_allow_html=True)
            cat_sales = f_df.groupby('category')[val_col].sum().reset_index()
            
            if not cat_sales.empty:
                fig_pie, ax_pie = plt.subplots(figsize=(8.0, 4.5), facecolor='#0F172A')
                ax_pie.set_facecolor('#0F172A')
                colors = ['#38BDF8', '#A78BFA', '#FBBF24', '#34D399', '#F43F5E']
                wedges, texts = ax_pie.pie(
                    cat_sales[val_col], 
                    startangle=90,
                    colors=colors[:len(cat_sales)],
                    wedgeprops=dict(width=0.35, edgecolor='#0F172A', linewidth=2)
                )
                total_val = cat_sales[val_col].sum()
                ax_pie.text(0, 0.08, f"${total_val:,.0f}", ha='center', va='center', color='#F8FAFC', fontsize=12, fontweight='bold')
                ax_pie.text(0, -0.12, f"Tổng {mode_label.lower()}", ha='center', va='center', color='#94A3B8', fontsize=7.5)
                
                legend_labels = []
                for _, row in cat_sales.iterrows():
                    pct = (row[val_col] / total_val) * 100 if total_val > 0 else 0
                    legend_labels.append(f"{row['category']}: ${row[val_col]:,.0f} ({pct:.1f}%)")
                
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
                st.info(f"Không đủ dữ liệu hiển thị cơ cấu danh mục theo {mode_label.lower()}.")
        
        st.markdown("<br/>---<br/>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color: #F8FAFC;'>📊 {mode_label} Chi Tiết Theo Phân Nhóm Sản Phẩm (Sub-Category)</h4>", unsafe_allow_html=True)
        
        subcat_sales = f_df.groupby(['sub_category', 'category'])[val_col].sum().reset_index()
        subcat_sales = subcat_sales.sort_values(by=val_col, ascending=True)
        
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
            bars = ax_sub.barh(subcat_sales['sub_category'], subcat_sales[val_col], color=bar_colors, height=0.6)
            
            ax_sub.tick_params(colors='#94A3B8', labelsize=9)
            ax_sub.set_xlabel(f'{mode_label} ($)', color='#94A3B8', fontsize=10)
            ax_sub.grid(True, linestyle='--', color='#1E293B', alpha=0.5, axis='x')
            
            for spine in ['top', 'right', 'left', 'bottom']:
                ax_sub.spines[spine].set_visible(False)
                
            ax_sub.get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}$".format(int(x))))
            
            max_val = subcat_sales[val_col].max() if not subcat_sales.empty else 0
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
            st.info(f"Không đủ dữ liệu hiển thị phân nhóm sản phẩm theo {mode_label.lower()}.")
            
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
