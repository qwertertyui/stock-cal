import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="DCF法 理論株価計算機", layout="centered")

# タイトル
st.title("📈 理論株価 計算アプリ (DCF法)")
st.markdown("企業の「将来の稼ぐ力」から、本来あるべき株価を算出します。")

# --- サイドバー：入力フォーム ---
st.sidebar.header("財務データ入力")

current_fcf = st.sidebar.number_input("現在のFCF (億円)", value=100.0, step=10.0)
growth_rate = st.sidebar.number_input("今後数年の成長率 (%)", value=5.0, step=0.5) / 100
forecast_years = st.sidebar.number_input("高成長が続く期間 (年)", value=5, step=1)
discount_rate = st.sidebar.number_input("割引率/期待収益率 (%)", value=8.0, step=0.5) / 100
terminal_growth = st.sidebar.number_input("永久成長率 (通常0-2%)", value=1.0, step=0.1) / 100
shares_outstanding = st.sidebar.number_input("発行済株式数 (億株)", value=1.0, step=0.1)

# --- 計算ボタン ---
if st.sidebar.button("計算する"):
    
    # エラーチェック
    if discount_rate <= terminal_growth:
        st.error("エラー: 割引率は永久成長率より高く設定してください。（分母がマイナスになります）")
    else:
        # --- DCF計算ロジック ---
        future_cash_flows = []
        present_values = []
        
        # 1. 予測期間の計算
        temp_fcf = current_fcf
        for i in range(1, int(forecast_years) + 1):
            temp_fcf = temp_fcf * (1 + growth_rate)
            pv = temp_fcf / ((1 + discount_rate) ** i)
            future_cash_flows.append(temp_fcf)
            present_values.append(pv)

        sum_pv_explicit = sum(present_values)

        # 2. ターミナルバリューの計算
        fcf_n_plus_1 = future_cash_flows[-1] * (1 + terminal_growth)
        terminal_value = fcf_n_plus_1 / (discount_rate - terminal_growth)
        terminal_value_pv = terminal_value / ((1 + discount_rate) ** forecast_years)

        # 3. 企業価値と株価
        total_enterprise_value = sum_pv_explicit + terminal_value_pv
        stock_price = total_enterprise_value / shares_outstanding

        # --- 結果表示 ---
        st.success("計算完了")
        
        # メインの数字を大きく表示
        st.metric(label="理論株価", value=f"{stock_price:,.0f} 円")

        # 詳細データの表示
        st.subheader("計算内訳")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**予測期間({forecast_years}年)の価値**\n\n{sum_pv_explicit:,.1f} 億円")
        with col2:
            st.info(f"**それ以降の永続価値**\n\n{terminal_value_pv:,.1f} 億円")
        
        st.write(f"企業価値合計: **{total_enterprise_value:,.1f} 億円**")
        
        # 将来キャッシュフローの推移グラフ
        st.subheader("将来キャッシュフローの推移予想")
        chart_data = pd.DataFrame({
            "年数": list(range(1, int(forecast_years) + 1)),
            "FCF予測 (億円)": future_cash_flows
        })
        st.bar_chart(chart_data, x="年数", y="FCF予測 (億円)")
 
