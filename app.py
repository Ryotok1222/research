import streamlit as st
import sys
import os

# ページ設定
st.set_page_config(
    page_title="ヘルスケアアプリ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# セッション状態の初期化（login.pyをインポートする前に実行）
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'login_time' not in st.session_state:
    st.session_state.login_time = 0
if 'session_id' not in st.session_state:
    st.session_state.session_id = ""

# ログイン機能をインポート
from login import check_login, show_user_info, get_username

# ログイン状態をチェック
check_login()

# サイドバーでページ選択
st.sidebar.title("ヘルスケアアプリ")
st.sidebar.markdown("---")

# ユーザー情報とログアウト
show_user_info()

# ページ選択
page = st.sidebar.selectbox(
    "ページを選択してください",
    ["ホーム", "アプリ１", "アプリ２"]
)

# ページルーティング
if page == "ホーム":
    # ホーム画面
    st.title("ヘルスケアアプリ")
    st.markdown(f"**ようこそ、{get_username()}さん！**")
    st.markdown("---")
    
    # メインコンテンツ
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("アプリの概要")
        st.markdown("""
        このアプリは、あなたの健康状態に基づいて最適なトレーニングメニューを提案し、
        高度な動的計画法による最適化分析を提供します。
        
        ### 主な機能
        - **アプリ１**: 基本的なトレーニングメニュー提案と効果予測
        - **アプリ２**: 初心者スキルレベル別のトレーニングメニュー提案と効果予測
        - **スキルレベル別分析**: 初心者・中級者・上級者別の遷移確率
        - **コスト効率分析**: 限られたリソースで最大の効果を得る
        - **最適ポリシー**: 状態・コスト・期間別の最適行動の可視化
        """)
        
elif page == "アプリ１":

    import subprocess
    import sys
    

    try:
        exec(open('dev.py').read())
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        st.info("dev.pyファイルが見つからないか、実行中にエラーが発生しました。")

elif page == "アプリ２":
    try:
        exec(open('mydev.py').read())
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        st.info("mydev.pyファイルが見つからないか、実行中にエラーが発生しました。")



