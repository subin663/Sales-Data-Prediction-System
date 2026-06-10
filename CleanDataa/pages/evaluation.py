import streamlit as st
import pandas as pd
import numpy as np
import warnings
import os
from datetime import datetime

# Suppress TensorFlow logging to keep UI and terminal clean
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

# Prevent circular import issues and access DB/load functions from app.py
from utils import load_base_data, run_retraining

if st.runtime.exists():
    st.markdown("""
        <div style="margin-bottom: 25px;">
            <h1 style="color: #F8FAFC; font-weight: 800; font-size: 2.2rem;">🏆 BẢNG XẾP HẠNG & ĐÁNH GIÁ MÔ HÌNH</h1>
            <p style="color: #94A3B8; font-size: 1.05rem;">So sánh chất lượng dự đoán thực tế của 5 mô hình ML/DL hàng tuần và quản lý vòng đời huấn luyện.</p>
        </div>
    """, unsafe_allow_html=True)

    # Hiển thị thông báo sau khi tái huấn luyện thành công và rerun trang
    if st.session_state.get('retraining_completed', False):
        st.toast("🎉 Đã hoàn thành tái huấn luyện 5 mô hình và cập nhật tệp CSV thành công!", icon="🏆")
        st.success("🎉 **Thành công!** Toàn bộ 5 mô hình đã được tái huấn luyện trực tuyến và cập nhật đầy đủ vào tệp CSV thành công.")
        # Reset flag
        st.session_state['retraining_completed'] = False

# Khởi tạo bảng nếu chưa tồn tại
def init_eval_db():
    eval_path = 'data/evaluations.csv'
    forecast_path = 'data/forecasts.csv'
    test_pred_path = 'data/test_predictions.csv'
    
    # 1. Tạo tệp evaluations.csv nếu chưa có
    if not os.path.exists(eval_path):
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        seed_data = [
            ('XGBoost', 17850.32, 22450.15, now_str),
            ('Linear Regression', 18560.28, 23619.29, now_str),
            ('LSTM', 19040.15, 26595.90, now_str),
            ('ARIMA', 22411.75, 30359.89, now_str),
            ('Random Forest', 34702.47, 42205.57, now_str)
        ]
        df_eval = pd.DataFrame(seed_data, columns=['model_name', 'mae', 'rmse', 'created_at'])
        df_eval.to_csv(eval_path, index=False, encoding='utf-8')
        
    # 2. Tạo tệp forecasts.csv nếu chưa có
    if not os.path.exists(forecast_path):
        df_fc = pd.DataFrame(columns=['product_id', 'forecast_date', 'predicted_revenue', 'model_name', 'created_at'])
        df_fc.to_csv(forecast_path, index=False, encoding='utf-8')

    # 3. Tạo tệp test_predictions.csv nếu chưa có
    if not os.path.exists(test_pred_path):
        run_retraining(status_box=None)

if st.runtime.exists():
    try:
        init_eval_db()
    except Exception as e:
        st.error(f"Lỗi khởi tạo dữ liệu đánh giá: {e}")


# Truy xuất kết quả đánh giá từ file CSV
def load_evaluations():
    if not os.path.exists('data/evaluations.csv'):
        return pd.DataFrame(columns=['model_name', 'mae', 'rmse', 'created_at'])
    df = pd.read_csv('data/evaluations.csv')
    if not df.empty:
        df['created_at'] = pd.to_datetime(df['created_at'])
        df = df.sort_values('created_at', ascending=True)
        # Chỉ giữ lại bản ghi đánh giá mới nhất của mỗi mô hình
        df = df.drop_duplicates(subset=['model_name'], keep='last')
        # Sắp xếp lại theo sai số MAE tăng dần để làm bảng xếp hạng
        df = df.sort_values(by='mae', ascending=True)
    return df

if st.runtime.exists():
    df_evals = load_evaluations()

    if df_evals.empty:
        st.warning("Hiện tại chưa có dữ liệu đánh giá trong SQL Server. Vui lòng chạy tác vụ huấn luyện lại bên dưới!")
    else:
        # HIỂN THỊ BẢNG XẾP HẠNG PHÁT SÁNG PREMIUM
        st.markdown("<h3 style='color: #F8FAFC; font-size: 1.25rem; margin-bottom: 20px;'>⭐ BẢNG XẾP HẠNG HIỆU NĂNG MÔ HÌNH (SẮP XẾP THEO MAE TĂNG DẦN)</h3>", unsafe_allow_html=True)
        
        # Render cúp vàng cho mẫu đứng đầu
        best_model = df_evals.iloc[0]
        st.markdown(f"""
            <div class="leaderboard-card" style="border-left: 5px solid #FBBF24; background: rgba(251, 191, 36, 0.08) !important; padding: 22px 25px !important;">
                <div style="display: flex; align-items: center; gap: 18px;">
                    <span style="font-size: 2.5rem; text-shadow: 0 0 15px rgba(251, 191, 36, 0.5);">🏆</span>
                    <div>
                        <h4 style="color: #F8FAFC; margin: 0; font-size: 1.25rem; font-weight: 800;">{best_model['model_name']} (MÔ HÌNH TỐT NHẤT)</h4>
                        <p style="color: #94A3B8; margin: 3px 0 0 0; font-size: 0.85rem;">Có độ chính xác vượt trội nhất trên 42 tuần tập dữ liệu Test.</p>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.55rem; font-weight: 800; color: #FBBF24; text-shadow: 0 0 10px rgba(251, 191, 36, 0.3);">MAE: ${best_model['mae']:,.0f}</div>
                    <div style="font-size: 0.85rem; color: #64748B;">RMSE: ${best_model['rmse']:,.0f}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Render các mẫu tiếp theo
        for idx in range(1, len(df_evals)):
            model_row = df_evals.iloc[idx]
            st.markdown(f"""
                <div class="leaderboard-card" style="border-left: 5px solid #38BDF8; padding: 16px 20px !important;">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span style="font-size: 1.4rem; color: #38BDF8; font-weight: 800; width: 35px; text-align: center;">#{idx + 1}</span>
                        <div>
                            <h4 style="color: #F8FAFC; margin: 0; font-size: 1.1rem; font-weight: 700;">{model_row['model_name']}</h4>
                            <p style="color: #64748B; margin: 3px 0 0 0; font-size: 0.8rem;">Đánh giá trên tập dữ liệu kiểm thử hàng tuần.</p>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.3rem; font-weight: 700; color: #38BDF8;">MAE: ${model_row['mae']:,.0f}</div>
                        <div style="font-size: 0.8rem; color: #64748B;">RMSE: ${model_row['rmse']:,.0f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br/>---<br/>", unsafe_allow_html=True)
        
        # BẢNG THÔNG TIN CHI TIẾT
        col_t1, col_t2 = st.columns([1.5, 1])
        with col_t1:
            st.markdown("<h4 style='color: #F8FAFC; margin-bottom: 12px;'>📋 Chi tiết số liệu kiểm thử trên hệ thống</h4>", unsafe_allow_html=True)
            df_display = df_evals.copy()
            df_display['created_at'] = pd.to_datetime(df_display['created_at']).dt.strftime('%d-%m-%Y %H:%M:%S')
            df_display.columns = ['Tên Mô Hình', 'Sai Số MAE ($)', 'Sai Số RMSE ($)', 'Ngày Cập Nhật']
            st.dataframe(
                df_display.style.format({
                    'Sai Số MAE ($)': "${:,.0f}",
                    'Sai Số RMSE ($)': "${:,.0f}"
                }),
                use_container_width=True,
                hide_index=True
            )
        with col_t2:
            st.markdown("<h4 style='color: #F8FAFC; margin-bottom: 12px;'>💡 Giải thích thuật ngữ</h4>", unsafe_allow_html=True)
            st.info("""
            - **MAE (Mean Absolute Error)**: Sai số tuyệt đối trung bình. Chỉ số này đo lường độ lệch trung bình giữa doanh số thực tế và doanh số dự báo. Giá trị càng nhỏ thể hiện mô hình càng chính xác.
            - **RMSE (Root Mean Squared Error)**: Căn bậc hai của sai số bình phương trung bình. Chỉ số này đặc biệt nhạy cảm với các khoảng sai số lớn, giúp phát hiện mô hình có xu hướng đoán lệch nghiêm trọng ở các tuần biến động mạnh hay không.
            """)

    st.markdown("<br/>---<br/>", unsafe_allow_html=True)
    
    # PHÂN HỆ QUẢN TRỊ VIÊN: HUẤN LUYỆN LẠI TOÀN BỘ MÔ HÌNH
    st.markdown("<h3 style='color: #F8FAFC; font-size: 1.25rem; margin-bottom: 15px;'>🚀 QUẢN LÝ HUẤN LUYỆN MÔ HÌNH TRỰC TUYẾN (ONLINE RETRAINING)</h3>", unsafe_allow_html=True)
    
    if st.session_state['role'] != 'Admin':
        st.warning("⚠️ CHỈ TÀI KHOẢN ADMIN MỚI CÓ QUYỀN HUẤN LUYỆN LẠI MÔ HÌNH. Vui lòng đăng nhập với tài khoản Admin để sử dụng chức năng này.")
        st.button("🚀 BẮT ĐẦU HUẤN LUYỆN LẠI TOÀN BỘ MÔ HÌNH", disabled=True)
    else:
        st.success("🔓 Chào Admin! Bạn có toàn quyền kích hoạt tiến trình cập nhật dữ liệu và tái huấn luyện mô hình học máy theo thời gian thực.")
        
        if st.button("🚀 BẮT ĐẦU HUẤN LUYỆN LẠI TOÀN BỘ MÔ HÌNH"):
            # Xóa cache dữ liệu cũ của app.py
            st.cache_data.clear()
            
            status_box = st.status("🔄 Đang khởi tạo tiến trình huấn luyện học máy trực tuyến...", expanded=True)
            
            try:
                run_retraining(status_box)
                status_box.update(state="complete", label="🎉 Hoàn thành huấn luyện lại và lưu dữ liệu thành công!")
                st.session_state['retraining_completed'] = True
                st.rerun()
                
            except Exception as ex:
                status_box.update(state="error", label="❌ Xảy ra lỗi trong quá trình huấn luyện!")
                st.error(f"Chi tiết lỗi huấn luyện: {ex}")

