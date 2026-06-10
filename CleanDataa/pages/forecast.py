import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from utils import load_base_data

st.markdown("""
    <div style="margin-bottom: 25px;">
        <h1 style="color: #F8FAFC; font-weight: 800; font-size: 2.2rem;">🔮 DỰ BÁO DOANH THU TƯƠNG LAI & SO SÁNH</h1>
        <p style="color: #94A3B8; font-size: 1.05rem;">So sánh hiệu năng dự báo của 5 mô hình trên tập Test và hiển thị dự báo 12 tuần tiếp theo.</p>
    </div>
""", unsafe_allow_html=True)

# Tải dữ liệu từ cache
try:
    monthly_data, df_clean = load_base_data()
except Exception as e:
    st.error(f"Lỗi tải dữ liệu: {e}")
    st.stop()

# Đọc dữ liệu từ file CSV cục bộ thay vì SQL Server
if not os.path.exists("data/forecasts.csv") or not os.path.exists("data/test_predictions.csv") or not os.path.exists("data/evaluations.csv"):
    with st.spinner("⏳ Hệ thống đang tự động khôi phục và huấn luyện lại mô hình trên dữ liệu gốc..."):
        from utils import run_retraining
        run_retraining(status_box=None)

if os.path.exists("data/forecasts.csv"):
    df_forecast = pd.read_csv("data/forecasts.csv")
else:
    df_forecast = pd.DataFrame(columns=['product_id', 'forecast_date', 'predicted_revenue', 'model_name', 'created_at'])

if df_forecast.empty:
    st.warning("Chưa có dữ liệu dự báo nào trong tệp CSV. Vui lòng chuyển sang tab Đánh giá & Huấn luyện để chạy mô hình lần đầu!")
else:
    df_forecast['forecast_date'] = pd.to_datetime(df_forecast['forecast_date'])
    
    # Loại bỏ dữ liệu dự báo trùng lặp (giữ lại bản ghi được tạo mới nhất 'created_at')
    df_forecast = df_forecast.sort_values('created_at').drop_duplicates(subset=['forecast_date', 'model_name'], keep='last')
    
    # Hiển thị thông tin mô tả đầy đủ
    st.info("💡 **Thông tin về mốc dự báo**: Mốc thời gian dự báo tương lai bắt đầu ngay từ tuần tiếp theo sau ngày bán hàng cuối cùng có trong cơ sở dữ liệu. Kết quả này được trích xuất trực tiếp từ tệp CSV phục vụ lập kế hoạch tồn kho.")
    
    # Bảng dữ liệu chiếm 100% chiều rộng giao diện và tăng chiều cao hiển thị để đọc rõ ràng
    st.markdown("<h4 style='color: #F8FAFC;'>📋 Bảng Dự Báo 12 Tuần Tương Lai Lưu Trong Tệp CSV</h4>", unsafe_allow_html=True)
    pivot_forecast = df_forecast.pivot(index='forecast_date', columns='model_name', values='predicted_revenue').round(0)
    pivot_forecast.index = pivot_forecast.index.strftime('%d-%m-%Y')
    st.dataframe(pivot_forecast.style.format("{:,.0f}$"), use_container_width=True, height=460)
        
    st.markdown("<br/>---<br/>", unsafe_allow_html=True)
    
    # Vẽ biểu đồ so sánh 5 mô hình trên tập Test
    st.subheader("📈 So sánh độ chính xác của các thuật toán trên 42 tuần tập Test")
    
    # Tạo các đặc trưng trễ động từ monthly_data (dữ liệu tuần)
    df_feat = monthly_data.copy()
    df_feat['lag_1'] = df_feat['revenue'].shift(1)
    df_feat['lag_2'] = df_feat['revenue'].shift(2)
    df_feat['lag_4'] = df_feat['revenue'].shift(4)
    df_feat['rolling_mean_4'] = df_feat['revenue'].shift(1).rolling(window=4).mean()
    df_feat['month_num'] = df_feat['sale_date'].dt.month
    df_feat['week_of_year'] = df_feat['sale_date'].dt.isocalendar().week.astype(int)
    
    df_feat_clean = df_feat.dropna().reset_index(drop=True)
    
    y_all = df_feat_clean['revenue'].values
    dates_all = df_feat_clean['sale_date'].values
    
    # 1. Đọc kết quả dự báo tập Test từ CSV để tối ưu hóa hiệu năng
    test_pred_path = 'data/test_predictions.csv'
    if not os.path.exists(test_pred_path):
        from utils import run_retraining
        run_retraining(status_box=None)
        
    df_test_preds = pd.read_csv(test_pred_path)
    df_test_preds['sale_date'] = pd.to_datetime(df_test_preds['sale_date'])
    
    dates_test = df_test_preds['sale_date']
    y_test_orig = df_test_preds['actual_revenue']
    lr_test = df_test_preds['Linear Regression']
    rf_test = df_test_preds['Random Forest']
    xgb_test = df_test_preds['XGBoost']
    arima_test = df_test_preds['ARIMA']
    lstm_test = df_test_preds['LSTM']
    
    fig2, ax2 = plt.subplots(figsize=(14, 6), facecolor='#0F172A')
    ax2.set_facecolor('#0F172A')
    
    # Vẽ Thực tế
    ax2.plot(dates_test, y_test_orig, color='#38BDF8', linewidth=3.5, marker='o', markersize=6, label='Thực tế (Actual)')
    
    # Vẽ các đường dự báo kiểm thử (mặc định hiển thị đầy đủ)
    ax2.plot(dates_test, lr_test, color='#F59E0B', linewidth=1.8, linestyle='-.', marker='s', markersize=4, label='Linear Regression')
    ax2.plot(dates_test, rf_test, color='#10B981', linewidth=1.8, linestyle=':', marker='^', markersize=4, label='Random Forest')
    ax2.plot(dates_test, xgb_test, color='#14B8A6', linewidth=1.8, linestyle='-', marker='p', markersize=4, label='XGBoost')
    ax2.plot(dates_test, arima_test, color='#A855F7', linewidth=1.8, linestyle='--', marker='d', markersize=4, label='ARIMA')
    ax2.plot(dates_test, lstm_test, color='#EC4899', linewidth=1.8, linestyle='-', marker='o', markersize=4, label='LSTM')
    
    ax2.set_xlabel('Thời gian', color='#94A3B8', fontsize=10, labelpad=8)
    ax2.set_ylabel('Doanh thu ($)', color='#94A3B8', fontsize=10, labelpad=8)
    ax2.tick_params(colors='#94A3B8', labelsize=9)
    ax2.grid(True, linestyle='--', color='#1E293B', alpha=0.5)
    ax2.legend(facecolor='#1E293B', edgecolor='#334155', fontsize=9.5)
    
    for spine in ['top', 'right', 'left', 'bottom']:
        ax2.spines[spine].set_visible(False)
        
    ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}$".format(int(x))))
    
    import matplotlib.dates as mdates
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    fig2.autofmt_xdate()
    
    st.pyplot(fig2)
    
    st.markdown("<br/>---<br/>", unsafe_allow_html=True)
    
    # Vẽ biểu đồ dự báo tương lai nối tiếp thực tế
    st.subheader("🔮 Đường dự báo 12 tuần tương lai nối tiếp dữ liệu lịch sử thực tế")
    st.info("Biểu đồ dưới đây kết hợp 20 tuần dữ liệu lịch sử thực tế cuối cùng và đường dự báo 12 tuần tiếp theo của các mô hình, giúp dễ dàng nhận diện xu hướng tăng/giảm doanh số trong tương lai.")
    
    # Lấy 20 tuần lịch sử cuối cùng
    hist_len = min(20, len(y_all))
    hist_dates = dates_all[-hist_len:]
    hist_revenue = y_all[-hist_len:]
    
    fig3, ax3 = plt.subplots(figsize=(14, 6.2), facecolor='#0F172A')
    ax3.set_facecolor('#0F172A')
    
    # 1. Vẽ dữ liệu lịch sử thực tế dưới dạng đường nét liền dày màu xanh da trời đặc trưng
    ax3.plot(hist_dates, hist_revenue, color='#38BDF8', linewidth=3.5, marker='o', markersize=6, label='Lịch sử (Actual Sales)')
    
    # 2. Vẽ dự báo của từng mô hình nối tiếp mốc lịch sử cuối cùng
    colors_map = {
        'Linear Regression': '#F59E0B',
        'Random Forest': '#10B981',
        'XGBoost': '#14B8A6',
        'ARIMA': '#A855F7',
        'LSTM': '#EC4899'
    }
    markers_map = {
        'Linear Regression': 's',
        'Random Forest': '^',
        'XGBoost': 'p',
        'ARIMA': 'd',
        'LSTM': 'o'
    }
    
    models_to_plot = ["Linear Regression", "Random Forest", "XGBoost", "ARIMA", "LSTM"]
    
    for m_name in models_to_plot:
        model_df = df_forecast[df_forecast['model_name'] == m_name].sort_values('forecast_date')
        if not model_df.empty:
            m_dates = model_df['forecast_date'].values
            m_preds = model_df['predicted_revenue'].values
            
            # Kết nối điểm lịch sử cuối cùng với điểm dự báo đầu tiên
            conn_dates = np.concatenate([[hist_dates[-1]], m_dates])
            conn_preds = np.concatenate([[hist_revenue[-1]], m_preds])
            
            # Vẽ đường nét đứt biểu diễn tương lai
            ax3.plot(
                conn_dates, 
                conn_preds, 
                color=colors_map.get(m_name, '#94A3B8'), 
                linewidth=2.0, 
                linestyle='--', 
                marker=markers_map.get(m_name, 'o'), 
                markersize=5, 
                label=f'Dự báo {m_name}'
            )
            
    ax3.set_xlabel('Thời gian', color='#94A3B8', fontsize=10, labelpad=8)
    ax3.set_ylabel('Doanh thu ($)', color='#94A3B8', fontsize=10, labelpad=8)
    ax3.tick_params(colors='#94A3B8', labelsize=9)
    ax3.grid(True, linestyle='--', color='#1E293B', alpha=0.5)
    ax3.legend(facecolor='#1E293B', edgecolor='#334155', fontsize=9.5)
    
    for spine in ['top', 'right', 'left', 'bottom']:
        ax3.spines[spine].set_visible(False)
        
    ax3.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}$".format(int(x))))
    
    # Định dạng hiển thị ngày trên trục hoành
    import matplotlib.dates as mdates
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    fig3.autofmt_xdate()
    
    st.pyplot(fig3)
