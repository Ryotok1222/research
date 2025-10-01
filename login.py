import streamlit as st
import hashlib
import time
import json
import base64

# 簡単なユーザー認証（実際のアプリではデータベースを使用）
USERS = {
    "user": "123456",
}

def generate_session_id(username):
    """セッションIDを生成"""
    timestamp = str(int(time.time()))
    data = f"{username}_{timestamp}"
    return hashlib.md5(data.encode()).hexdigest()

def save_auth_to_session(username, session_id):
    """認証情報をセッションに保存"""
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.login_time = time.time()
    st.session_state.session_id = session_id

def check_persistent_auth():
    """永続的な認証をチェック"""
    # URLパラメータから認証情報を取得
    query_params = st.query_params
    
    if 'user' in query_params and 'session' in query_params:
        try:
            username = query_params['user']
            session_id = query_params['session']
            login_time = float(query_params.get('time', 0))
            
            # セッション有効性をチェック（24時間）
            current_time = time.time()
            if current_time - login_time < 86400:  # 24時間
                save_auth_to_session(username, session_id)
                return True
        except:
            pass
    
    return False

def set_auth_params(username, session_id):
    """認証パラメータをURLに設定"""
    current_time = time.time()
    st.query_params.user = username
    st.query_params.session = session_id
    st.query_params.time = str(current_time)

def is_session_valid():
    """セッションが有効かチェック（24時間）"""
    if not st.session_state.logged_in:
        return False
    
    current_time = time.time()
    session_duration = current_time - st.session_state.login_time
    
    # 24時間（86400秒）でセッション期限切れ
    return session_duration < 86400

def login(username, password):
    """ログイン認証"""
    if username in USERS and USERS[username] == password:
        session_id = generate_session_id(username)
        save_auth_to_session(username, session_id)
        set_auth_params(username, session_id)
        return True
    return False

def logout():
    """ログアウト"""
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.login_time = 0
    st.session_state.session_id = ""
    
    # URLパラメータをクリア
    st.query_params.clear()

def show_login_page():
    """ログイン画面を表示"""
    st.title("ヘルスケアアプリ - ログイン")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("ログイン")
        
        with st.form("login_form"):
            username = st.text_input("ユーザー名", placeholder="ユーザー名を入力")
            password = st.text_input("パスワード", type="password", placeholder="パスワードを入力")
            submitted = st.form_submit_button("ログイン")
            
            if submitted:
                if login(username, password):
                    st.success(f"ようこそ、{username}さん！")
                    st.rerun()
                else:
                    st.error("ユーザー名またはパスワードが正しくありません。")
        
        st.markdown("---")
        st.info("""
        - ユーザー名: `user` / パスワード: `123456`
        """)
    
    st.stop()

def check_login():
    """ログイン状態をチェックし、未ログインの場合はログイン画面を表示"""
    # まず永続的な認証をチェック
    if not st.session_state.logged_in:
        if check_persistent_auth():
            return
    
    # セッション有効性をチェック
    if not st.session_state.logged_in or not is_session_valid():
        if st.session_state.logged_in and not is_session_valid():
            st.warning("セッションが期限切れです。再度ログインしてください。")
            logout()
        show_login_page()

def show_user_info():
    """サイドバーにユーザー情報とログアウトボタンを表示"""
    if is_session_valid():
        # セッション残り時間を計算
        current_time = time.time()
        remaining_time = 86400 - (current_time - st.session_state.login_time)
        remaining_hours = int(remaining_time // 3600)
        remaining_minutes = int((remaining_time % 3600) // 60)
        
        st.sidebar.success(f"ログイン中: {st.session_state.username}")
    
        
        if st.sidebar.button(" ログアウト"):
            logout()
            st.rerun()
    else:
        st.sidebar.error("セッションが無効です")
        if st.sidebar.button("再ログイン"):
            logout()
            st.rerun()
    
    st.sidebar.markdown("---")

def get_username():
    """現在のユーザー名を取得"""
    return st.session_state.username
