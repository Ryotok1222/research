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
    ["ホーム", "従来研究", "本研究"]
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
        - **従来研究**: 基本的なトレーニングメニュー提案と効果予測
        - **本研究**: 初心者スキルレベル別のトレーニングメニュー提案と効果予測
        - **スキルレベル別分析**: 初心者・中級者・上級者別の遷移確率
        - **コスト効率分析**: 限られたリソースで最大の効果を得る
        - **最適ポリシー**: 状態・コスト・期間別の最適行動の可視化
        """)
        
        st.header("使い方")
        st.markdown("""
        ####  従来研究ページ
        1. 左のサイドバーから「従来研究」を選択
        2. 現在の状態を選択（良い・普通・悪い）
        3. トレーニング期間を設定（1-30日）
        4. モチベーションレベルを設定（1-6）
        5. 「計算する」ボタンをクリック
        
        #### 本研究ページ
        1. 左のサイドバーから「本研究」を選択
        2. 基本パラメータ（期間T、トレーニングに対するモチベーションL）を設定
        3. 各行動のコストを調整
        4. スキルレベル期間を設定
        5. 「計算実行」ボタンをクリック
        """)
    
    with col2:
        st.header("アプリ統計")
        st.metric("従来研究ページ", "基本機能")
        st.metric("本研究ページ", "高度機能")
        st.metric("スキルレベル", "3段階")
        st.metric("行動選択肢", "4種類")
        st.metric("状態数", "3状態")
        
    
        st.header("ヒント")
        st.info("""
        **従来研究**: 基本的なトレーニングメニュー提案
        
        **本研究**: 高度な動的計画法による最適戦略分析
        
        """)

elif page == "従来研究":

    import subprocess
    import sys
    

    try:
        exec(open('dev.py').read())
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        st.info("dev.pyファイルが見つからないか、実行中にエラーが発生しました。")

elif page == "本研究":
    try:
        exec(open('mydev.py').read())
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        st.info("mydev.pyファイルが見つからないか、実行中にエラーが発生しました。")

# サイドバーの追加情報
st.sidebar.markdown("---")
st.sidebar.markdown("### アプリ情報")
st.sidebar.info("""
**バージョン**: 1.0.0  
**最終更新**: 2025年  
""")


