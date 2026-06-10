import streamlit as st
import pandas as pd
import hashlib
import os

def get_db_connection():
    # Deprecated: Connection to SQL Server is no longer needed since system uses local CSV files.
    # Return None to maintain backward compatibility without crashing old references.
    return None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_products_csv():
    import re
    
    products_path = 'data/data_products.csv'
    sql_path = 'import_data.sql'
    sales_path = 'data/data_sales.csv'
    
    if not os.path.exists(products_path):
        return
        
    try:
        df_prod = pd.read_csv(products_path)
        modified = False
        
        if 'price' not in df_prod.columns:
            prices = {}
            # 1. Parse from SQL file
            if os.path.exists(sql_path):
                try:
                    with open(sql_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    matches = re.findall(r"INSERT\s+INTO\s+Products\s*\(product_name,\s*category_id,\s*price\)\s*SELECT\s*'(.*?)',\s*category_id,\s*([\d.]+)", content, re.IGNORECASE)
                    for name, price_str in matches:
                        clean_name = name.replace("''", "'")
                        prices[clean_name] = float(price_str)
                except Exception as e:
                    print(f"Error parsing SQL prices: {e}")
            
            # 2. Supplement from sales
            if os.path.exists(sales_path):
                try:
                    df_sales = pd.read_csv(sales_path)
                    df_sales['calc_price'] = df_sales['revenue'] / df_sales['quantity']
                    sales_prices = df_sales.groupby('product_name')['calc_price'].median().to_dict()
                    for k, v in sales_prices.items():
                        if k not in prices or pd.isna(prices[k]):
                            prices[k] = v
                except Exception as e:
                    print(f"Error calculating prices from sales: {e}")
            
            df_prod['price'] = df_prod['product_name'].map(prices)
            median_price = df_prod['price'].median()
            if pd.isna(median_price) or median_price <= 0:
                median_price = 15.0
            df_prod['price'] = df_prod['price'].fillna(median_price)
            modified = True
            print("Successfully initialized products price column!")
            
        if 'sub_category_name' not in df_prod.columns:
            raw_path = 'data/cleaned_data.csv' if os.path.exists('data/cleaned_data.csv') else 'data/test.csv'
            if os.path.exists(raw_path):
                try:
                    df_raw = pd.read_csv(raw_path, encoding='latin1')
                except Exception:
                    df_raw = pd.read_csv(raw_path, encoding='utf-8')
                mapping = df_raw.groupby('Product Name')['Sub-Category'].first().to_dict()
                df_prod['sub_category_name'] = df_prod['product_name'].map(mapping).fillna('Binders')
                modified = True
                print("Successfully mapped subcategory names to data_products!")
                
        if modified:
            df_prod.to_csv(products_path, index=False, encoding='utf-8')
            
    except Exception as e:
        print(f"Error in init_products_csv: {e}")

@st.cache_data(ttl=1)
def load_base_data():
    # Tự động loại bỏ dữ liệu mô phỏng thừa để khôi phục dữ liệu gốc
    sales_path = 'data/data_sales.csv'
    if os.path.exists(sales_path):
        try:
            df_s = pd.read_csv(sales_path)
            df_s['parsed_date'] = pd.to_datetime(df_s['sale_date'], format='mixed', errors='coerce')
            df_original = df_s[df_s['parsed_date'] <= pd.Timestamp('2018-12-30')]
            if len(df_original) < len(df_s):
                df_original.drop(columns=['parsed_date']).to_csv(sales_path, index=False, encoding='utf-8')
                # Xóa các file kết quả cũ để kích hoạt tính toán huấn luyện lại tự động
                for f in ['data/forecasts.csv', 'data/test_predictions.csv', 'data/evaluations.csv']:
                    if os.path.exists(f):
                        try:
                            os.remove(f)
                        except Exception:
                            pass
                st.cache_data.clear()
                st.rerun()
        except Exception as e:
            pass

    # Đọc dữ liệu từ các file CSV cục bộ thay vì SQL Server
    df_sales = pd.read_csv('data/data_sales.csv')
    df_products = pd.read_csv('data/data_products.csv')
    
    # Tạo dữ liệu cơ bản (sale_date, revenue)
    df = df_sales[['sale_date', 'revenue']].copy()
    try:
        df['sale_date'] = pd.to_datetime(df['sale_date'], format='mixed')
    except Exception:
        df['sale_date'] = pd.to_datetime(df['sale_date'], errors='coerce')
    df = df.dropna(subset=['sale_date'])
    df = df.sort_values('sale_date')
    
    # Kết hợp doanh số với danh mục sản phẩm (denormalize)
    df_merged = df_sales.merge(df_products, on='product_name', how='left')
    
    try:
        order_dates = pd.to_datetime(df_merged['sale_date'], format='mixed')
    except Exception:
        order_dates = pd.to_datetime(df_merged['sale_date'], errors='coerce')
        
    df_clean = pd.DataFrame({
        'order_date': order_dates,
        'sales': pd.to_numeric(df_merged['revenue']),
        'category': df_merged['category_name'].fillna('Office Supplies'),
        'sub_category': df_merged['sub_category_name'].fillna('Binders'),
        'product_name': df_merged['product_name'],
        'segment': 'All Segments'
    })
    df_clean = df_clean.dropna(subset=['order_date'])
    
    # Gom nhóm theo tuần
    monthly_data = df.resample('W', on='sale_date')['revenue'].sum().reset_index()
    monthly_data.columns = ['sale_date', 'revenue']
    monthly_data = monthly_data.sort_values('sale_date')
    
    return monthly_data, df_clean

def generate_simulated_sale():
    import random
    from datetime import datetime, timedelta
    
    try:
        df_prod = pd.read_csv('data/data_products.csv')
        if df_prod.empty:
            return None
        
        random_row = df_prod.sample(n=1).iloc[0]
        product_name = random_row['product_name']
        price = float(random_row['price'])
        
        df_sales = pd.read_csv('data/data_sales.csv')
        if df_sales.empty:
            sale_date = datetime(2018, 12, 30).date()
        else:
            try:
                df_sales['sale_date'] = pd.to_datetime(df_sales['sale_date'], format='mixed')
            except Exception:
                df_sales['sale_date'] = pd.to_datetime(df_sales['sale_date'], errors='coerce')
            df_sales = df_sales.dropna(subset=['sale_date'])
            sale_date = df_sales['sale_date'].max().date()
                
        new_date = sale_date + timedelta(days=random.randint(1, 3))
        quantity = random.randint(1, 5)
        revenue = price * quantity
        
        # Thêm bản ghi mới
        new_row = pd.DataFrame([{
            'product_name': product_name,
            'quantity': quantity,
            'sale_date': new_date.strftime('%Y-%m-%d'),
            'revenue': revenue
        }])
        
        df_sales = pd.concat([df_sales, new_row], ignore_index=True)
        df_sales.to_csv('data/data_sales.csv', index=False, encoding='utf-8')
        
        return {
            'product_name': product_name,
            'quantity': quantity,
            'revenue': revenue,
            'sale_date': new_date
        }
    except Exception as e:
        print(f"Error in generate_simulated_sale: {e}")
        return None

def authenticate(username, password):
    if not os.path.exists('data/users.csv'):
        return None
    try:
        df_users = pd.read_csv('data/users.csv')
        user_row = df_users[df_users['username'] == username]
        if user_row.empty:
            return None
        user_row = user_row.iloc[0]
        hashed = hash_password(password)
        if user_row['password_hash'] == hashed:
            return (user_row['role'], user_row['status'])
    except Exception as e:
        print(f"Error in authenticate: {e}")
    return None

def forecast_recursive(model, df_feat, num_steps=12):
    import pandas as pd
    import numpy as np
    history = list(df_feat['revenue'].values)
    last_date = df_feat['sale_date'].max()
    predictions = []
    feature_cols = ['lag_1', 'lag_2', 'lag_4', 'rolling_mean_4', 'month_num', 'week_of_year']
    for i in range(num_steps):
        next_date = last_date + pd.Timedelta(weeks=i+1)
        month_num = next_date.month
        week_of_year = int(next_date.isocalendar()[1])
        l1 = history[-1]
        l2 = history[-2]
        l4 = history[-4]
        rm4 = np.mean(history[-4:])
        X_next = pd.DataFrame([{
            'lag_1': l1,
            'lag_2': l2,
            'lag_4': l4,
            'rolling_mean_4': rm4,
            'month_num': month_num,
            'week_of_year': week_of_year
        }])
        X_next = X_next[feature_cols]
        pred = max(0.0, float(model.predict(X_next)[0]))
        predictions.append(pred)
        history.append(pred)
    return np.array(predictions)

def run_retraining(status_box=None):
    import numpy as np
    import pandas as pd
    from datetime import datetime
    import warnings
    warnings.filterwarnings('ignore')
    
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    from xgboost import XGBRegressor
    from statsmodels.tsa.arima.model import ARIMA
    from sklearn.preprocessing import MinMaxScaler
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM as KerasLSTM, Dense

    def log(msg):
        if status_box:
            status_box.write(msg)
        else:
            print(msg)
            
    log("📥 Đang tải dữ liệu và tạo đặc trưng trễ...")
    # Load data
    weekly_data, df_clean = load_base_data()
    
    # Tạo các đặc trưng trễ động từ dữ liệu tuần (ĐÃ FIX DATA LEAKAGE)
    df_feat = weekly_data.copy()
    df_feat['lag_1'] = df_feat['revenue'].shift(1)
    df_feat['lag_2'] = df_feat['revenue'].shift(2)
    df_feat['lag_4'] = df_feat['revenue'].shift(4)
    df_feat['rolling_mean_4'] = df_feat['revenue'].shift(1).rolling(window=4).mean()
    df_feat['month_num'] = df_feat['sale_date'].dt.month
    df_feat['week_of_year'] = df_feat['sale_date'].dt.isocalendar().week.astype(int)
    
    # Bỏ qua các dòng đầu bị NaN do shift/rolling
    df_feat_clean = df_feat.dropna().reset_index(drop=True)
    feature_cols = ['lag_1', 'lag_2', 'lag_4', 'rolling_mean_4', 'month_num', 'week_of_year']
    
    y_all = df_feat_clean['revenue'].values
    X_all = df_feat_clean[feature_cols]
    dates_all = df_feat_clean['sale_date'].values
    
    N = len(y_all)
    test_len = 42
    train_len = N - test_len
    
    y_train = y_all[:train_len]
    y_test = y_all[train_len:]
    X_train = X_all.iloc[:train_len]
    X_test = X_all.iloc[train_len:]
    dates_test = dates_all[train_len:]
    
    log(f"📊 Tập huấn luyện: {train_len} tuần | Tập đánh giá: {test_len} tuần.")
    
    # --- MODEL 1: Linear Regression ---
    log("🧠 1. Đang huấn luyện Linear Regression...")
    lr_eval = LinearRegression().fit(X_train, y_train)
    lr_pred = lr_eval.predict(X_test)
    lr_mae = mean_absolute_error(y_test, lr_pred)
    lr_rmse = np.sqrt(mean_squared_error(y_test, lr_pred))
    
    lr_full = LinearRegression().fit(X_all, y_all)
    lr_forecast = forecast_recursive(lr_full, df_feat_clean, 12)
    
    # --- MODEL 2: Random Forest ---
    log("🌲 2. Đang huấn luyện Random Forest...")
    rf_eval = RandomForestRegressor(n_estimators=100, random_state=42).fit(X_train, y_train)
    rf_pred = rf_eval.predict(X_test)
    rf_mae = mean_absolute_error(y_test, rf_pred)
    rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred))
    
    rf_full = RandomForestRegressor(n_estimators=100, random_state=42).fit(X_all, y_all)
    rf_forecast = forecast_recursive(rf_full, df_feat_clean, 12)
    
    # --- MODEL 3: XGBoost ---
    log("⚡ 3. Đang huấn luyện XGBoost...")
    xgb_eval = XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=5, random_state=42).fit(X_train, y_train)
    xgb_pred = xgb_eval.predict(X_test)
    xgb_mae = mean_absolute_error(y_test, xgb_pred)
    xgb_rmse = np.sqrt(mean_squared_error(y_test, xgb_pred))
    
    xgb_full = XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=5, random_state=42).fit(X_all, y_all)
    xgb_forecast = forecast_recursive(xgb_full, df_feat_clean, 12)
    
    # --- MODEL 4: ARIMA ---
    log("📈 4. Đang huấn luyện ARIMA...")
    history = list(y_train)
    arima_pred_list = []
    for t in range(test_len):
        model = ARIMA(history, order=(1, 1, 1))
        model_fit = model.fit()
        output = model_fit.forecast()
        arima_pred_list.append(output[0])
        history.append(y_test[t])
    arima_pred = np.array(arima_pred_list)
    
    arima_mae = mean_absolute_error(y_test, arima_pred)
    arima_rmse = np.sqrt(mean_squared_error(y_test, arima_pred))
    
    arima_full = ARIMA(y_all, order=(1, 1, 1)).fit()
    arima_forecast = np.maximum(0, arima_full.forecast(steps=12))
    
    # --- MODEL 5: LSTM ---
    log("🤖 5. Đang huấn luyện Deep Learning LSTM...")
    scaler = MinMaxScaler(feature_range=(0, 1))
    y_train_scaled = scaler.fit_transform(y_train.reshape(-1, 1)).flatten()
    y_test_scaled = scaler.transform(y_test.reshape(-1, 1)).flatten()
    
    seq_length = 3
    X_train_lstm, y_train_lstm = [], []
    for i in range(len(y_train_scaled) - seq_length):
        X_train_lstm.append(y_train_scaled[i:i+seq_length])
        y_train_lstm.append(y_train_scaled[i+seq_length])
    X_train_lstm, y_train_lstm = np.array(X_train_lstm), np.array(y_train_lstm)
    
    y_test_seq_input = np.concatenate([y_train_scaled[-seq_length:], y_test_scaled])
    X_test_lstm = []
    for i in range(len(y_test_seq_input) - seq_length):
        X_test_lstm.append(y_test_seq_input[i:i+seq_length])
    X_test_lstm = np.array(X_test_lstm)
    
    lstm_model = Sequential()
    lstm_model.add(KerasLSTM(50, activation='relu', input_shape=(seq_length, 1)))
    lstm_model.add(Dense(1))
    lstm_model.compile(optimizer='adam', loss='mse')
    lstm_model.fit(X_train_lstm.reshape(-1, seq_length, 1), y_train_lstm, epochs=50, verbose=0)
    
    lstm_pred_scaled = lstm_model.predict(X_test_lstm.reshape(-1, seq_length, 1), verbose=0)
    lstm_pred = scaler.inverse_transform(lstm_pred_scaled).flatten()
    lstm_mae = mean_absolute_error(y_test, lstm_pred)
    lstm_rmse = np.sqrt(mean_squared_error(y_test, lstm_pred))
    
    # Huấn luyện mô hình Full LSTM trên 100% dữ liệu
    scaler_full = MinMaxScaler(feature_range=(0, 1))
    y_all_scaled = scaler_full.fit_transform(y_all.reshape(-1, 1)).flatten()
    
    X_all_lstm, y_all_lstm = [], []
    for i in range(len(y_all_scaled) - seq_length):
        X_all_lstm.append(y_all_scaled[i:i+seq_length])
        y_all_lstm.append(y_all_scaled[i+seq_length])
    X_all_lstm, y_all_lstm = np.array(X_all_lstm), np.array(y_all_lstm)
    
    lstm_full = Sequential()
    lstm_full.add(KerasLSTM(50, activation='relu', input_shape=(seq_length, 1)))
    lstm_full.add(Dense(1))
    lstm_full.compile(optimizer='adam', loss='mse')
    lstm_full.fit(X_all_lstm.reshape(-1, seq_length, 1), y_all_lstm, epochs=50, verbose=0)
    
    last_seq = y_all_scaled[-seq_length:].reshape(1, seq_length, 1)
    lstm_pred_list = []
    for _ in range(12):
        next_scaled = lstm_full.predict(last_seq, verbose=0)
        lstm_pred_list.append(next_scaled[0][0])
        last_seq = np.append(last_seq[:, 1:, :], next_scaled.reshape(1, 1, 1), axis=1)
        
    lstm_forecast = scaler_full.inverse_transform(np.array(lstm_pred_list).reshape(-1, 1)).flatten()
    lstm_forecast = np.maximum(0, lstm_forecast)
    
    # --- 6. CẬP NHẬT KẾT QUẢ VÀO FILE CSV ---
    log("💾 Đang ghi đè kết quả huấn luyện mới vào các tệp CSV...")
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Lưu evaluations (làm tròn đến 2 chữ số thập phân)
    eval_rows = [
        {'model_name': 'Linear Regression', 'mae': float(round(lr_mae, 2)), 'rmse': float(round(lr_rmse, 2)), 'created_at': now_str},
        {'model_name': 'Random Forest', 'mae': float(round(rf_mae, 2)), 'rmse': float(round(rf_rmse, 2)), 'created_at': now_str},
        {'model_name': 'XGBoost', 'mae': float(round(xgb_mae, 2)), 'rmse': float(round(xgb_rmse, 2)), 'created_at': now_str},
        {'model_name': 'ARIMA', 'mae': float(round(arima_mae, 2)), 'rmse': float(round(arima_rmse, 2)), 'created_at': now_str},
        {'model_name': 'LSTM', 'mae': float(round(lstm_mae, 2)), 'rmse': float(round(lstm_rmse, 2)), 'created_at': now_str}
    ]
    pd.DataFrame(eval_rows).to_csv('data/evaluations.csv', index=False, encoding='utf-8')
    
    # Lưu forecasts (12 tuần tương lai, làm tròn đến 2 chữ số thập phân)
    last_date = pd.to_datetime(weekly_data['sale_date'].max())
    forecasts_data = {
        'Linear Regression': lr_forecast,
        'Random Forest': rf_forecast,
        'XGBoost': xgb_forecast,
        'ARIMA': arima_forecast,
        'LSTM': lstm_forecast
    }
    forecast_rows = []
    for name, forecast_vals in forecasts_data.items():
        for i, val in enumerate(forecast_vals):
            forecast_date = last_date + pd.Timedelta(weeks=i+1)
            forecast_rows.append({
                'product_id': 1,
                'forecast_date': forecast_date.strftime('%Y-%m-%d'),
                'predicted_revenue': float(round(val, 2)),
                'model_name': name,
                'created_at': now_str
            })
    pd.DataFrame(forecast_rows).to_csv('data/forecasts.csv', index=False, encoding='utf-8')
    
    # Lưu test predictions (làm tròn đến 2 chữ số thập phân)
    df_test_preds = pd.DataFrame({
        'sale_date': pd.to_datetime(dates_test).strftime('%Y-%m-%d'),
        'actual_revenue': np.round(y_test, 2),
        'Linear Regression': np.round(lr_pred, 2),
        'Random Forest': np.round(rf_pred, 2),
        'XGBoost': np.round(xgb_pred, 2),
        'ARIMA': np.round(arima_pred, 2),
        'LSTM': np.round(lstm_pred, 2)
    })
    df_test_preds.to_csv('data/test_predictions.csv', index=False, encoding='utf-8')
    log("🎉 Đã hoàn thành cập nhật tất cả tệp CSV!")


