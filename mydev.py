import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="ヘルスケアアプリ", layout="wide")
st.title("ヘルスケアアプリ")
st.write("常に最高のコンディション保持のために")

# --- UI ---
with st.form("sim_form"):
    choice = st.radio("あなたの状態は？", ["良い", "普通", "悪い"], horizontal=True)
    skill_level = st.radio("今のあなたのトレーニングレベルは", ["初心者", "中級者", "上級者"], horizontal=True)
    T = st.radio("期間は？(最大30日間まで選択可能)", list(range(1, 31)), horizontal=True, index=11)  
    L = st.number_input("トレーニングに対するモチベーション", min_value=1, max_value=6, value=6, step=1)
    submitted = st.form_submit_button("計算する")

if not submitted:
    st.stop()

# --- パラメータ設定 ---
S = 3  # 状態数
A = 4  # アクション数
# コスト設定（固定）
costs = [3, 2, 1, 0]

# 初期状態ベクトルを選択に応じて作成
init_idx = {"良い": 0, "普通": 1, "悪い": 2}[choice]
state_vec = np.zeros(3)
state_vec[init_idx] = 1.0  # 例: 良い→[1,0,0]

# スキルレベルに応じて期間分割を決定
if skill_level == "初心者":
    # 3分割（余りは初心者期間に追加）
    base_period = T // 3
    remainder = T % 3
    beginner_period = base_period + remainder
    intermediate_period = base_period
    advanced_period = base_period
elif skill_level == "中級者":
    # 2分割（余りは中級者期間に追加）
    base_period = T // 2
    remainder = T % 2
    beginner_period = 0  # 初心者期間なし
    intermediate_period = base_period + remainder
    advanced_period = base_period
else:  # 上級者
    # 分割なし（ずっと上級者用）
    beginner_period = 0
    intermediate_period = 0
    advanced_period = T
# 遷移確率：Pr(sk | si, aj)
# shape: (S, A, S)
#初心者用
P = np.zeros((S, A, S))
P[0, 0] = [0.7, 0.2, 0.1]
P[1, 0] = [0.4, 0.35, 0.25]
P[2, 0] = [0.3, 0.5, 0.2]
#ここからは行動a2を選択した場合
P[0, 1] = [0.55, 0.32, 0.2]
P[1, 1] = [0.3, 0.42, 0.28]
P[2, 1] = [0.2, 0.3, 0.5]
#ここからは行動a3を選択した場合
P[0, 2] = [0.45, 0.35, 0.2]
P[1, 2] = [0.2, 0.5, 0.3]
P[2, 2] = [0.1, 0.2, 0.7]
#ここからは行動a4を選択した場合
P[0, 3] = [0.3,0.4,0.3]
P[1, 3] = [0.15,0.52,0.33]
P[2, 3] = [0.05,0.15,0.8]
#中級者用
P2 = np.zeros((S, A, S))
P2[0, 0] = [0.8, 0.15, 0.05]
P2[1, 0] = [0.5, 0.3, 0.2]
P2[2, 0] = [0.2, 0.65, 0.15]
#ここからは行動a2を選択した場合
P2[0, 1] = [0.6, 0.25, 0.15]
P2[1, 1] = [0.4, 0.35, 0.25]
P2[2, 1] = [0.15, 0.5, 0.35]
#ここからは行動a3を選択した場合
P2[0, 2] = [0.5, 0.3, 0.2]
P2[1, 2] = [0.35, 0.45, 0.2]
P2[2, 2] = [0.1, 0.4, 0.5]
#ここからは行動a4を選択した場合
P2[0, 3] =[0.4, 0.35, 0.25]
P2[1, 3] =[0.1,0.6,0.3]
P2[2, 3] =[0.03,0.15,0.82]
#上級者用
P3 = np.zeros((S, A, S))
P3[0, 0] = [0.9, 0.1, 0.0]
P3[1, 0] = [0.6, 0.25, 0.15]
P3[2, 0] = [0.3, 0.5, 0.2]
#ここからは行動a2を選択した場合
P3[0, 1] = [0.6, 0.25, 0.15]
P3[1, 1] = [0.5, 0.3, 0.2]
P3[2, 1] = [0.2, 0.3, 0.5]
#ここからは行動a3を選択した場合
P3[0, 2] = [0.7, 0.2, 0.1]
P3[1, 2] = [0.4, 0.35, 0.25]
P3[2, 2] = [0.1, 0.2, 0.7]
#ここからは行動a4を選択した場合
P3[0, 3] = [0.6, 0.25, 0.15]
P3[1, 3] = [0.05, 0.6, 0.35]
P3[2, 3] = [0.05, 0.15, 0.8]
# 利得：目標状態s1（index 0）のみ1
reward = np.array([1, 0, 0])
# DPテーブル：V[state][cost][time]
V = np.zeros((S, L + 1, T + 1))
policy = np.full((S, L + 1, T), -1)  # 最適行動の記録
# DP後ろから計算
for t in reversed(range(1, T + 1)):
    # スキルレベルと期間に応じて遷移確率を決定
    if skill_level == "初心者":
        if t <= beginner_period:
            P_t = P  # 初心者
        elif t <= beginner_period + intermediate_period:
            P_t = P2  # 中級者
        else:
            P_t = P3  # 上級者
    elif skill_level == "中級者":
        if t <= intermediate_period:
            P_t = P2  # 中級者
        else:
            P_t = P3  # 上級者
    else:  # 上級者
        P_t = P3  # ずっと上級者
    for s in range(S):
        for l in range(L + 1):
            best = -1
            best_action = -1
            for a in range(A):
                if costs[a] > l:
                    continue
                expected = 0
                for next_s in range(S):
                    r = reward[next_s]
                    next_l = L if costs[a] == 0 else l - costs[a]
                    next_v = V[next_s][next_l][t] if t < T else 0
                    expected += P_t[s, a, next_s] * (r + next_v)
                if expected > best:
                    best = expected
                    best_action = a
            V[s][l][t - 1] = best
            policy[s][l][t - 1] = best_action  # :左矢印: 最適行動を記録
# --- 結果表示 ---
# 選択された初期状態での結果を計算
initial_state_prob = V[init_idx][L][0] / T
final_state_prob = V[init_idx][L][0]

col1, col2, col3 = st.columns(3)
if choice == "良い":
    col1.metric("最終時点の確率", f"{final_state_prob:.3f}")
    col2.metric("平均確率（各期）", f"{initial_state_prob:.3f}")
    col3.metric("最終モチベーション", f"{L}")
elif choice == "普通":
    col1.metric("最終時点の確率", f"{final_state_prob:.3f}")
    col2.metric("平均確率（各期）", f"{initial_state_prob:.3f}")
    col3.metric("最終モチベーション", f"{L}")
else:  # 悪い
    col1.metric("最終時点の確率", f"{final_state_prob:.3f}")
    col2.metric("平均確率（各期）", f"{initial_state_prob:.3f}")
    col3.metric("最終モチベーション", f"{L}")

st.subheader("トレーニングメニューのおすすめ")

# 最適ポリシーから実際のトレーニングメニューを生成
def generate_training_plan(initial_state, initial_cost, policy, V, costs, T, beginner_period, intermediate_period):
    """最適ポリシーに基づいてトレーニングメニューを生成"""
    rows = []
    current_state = initial_state
    current_cost = initial_cost
    
    for t in range(1, T + 1):
        if current_cost < 0:
            break
            
        # 最適行動を取得
        best_action = policy[current_state][current_cost][t-1]
        
        if best_action == -1:
            rows.append({
                "期": t, 
                "行動": "なし(予算不足)", 
                "モチベーション": current_cost,
                "s1": 0, "s2": 0, "s3": 0
            })
            break
        
        # スキルレベルと期間に応じて遷移確率を選択
        if skill_level == "初心者":
            if t <= beginner_period:
                P_t = P  # 初心者
            elif t <= beginner_period + intermediate_period:
                P_t = P2  # 中級者
            else:
                P_t = P3  # 上級者
        elif skill_level == "中級者":
            if t <= intermediate_period:
                P_t = P2  # 中級者
            else:
                P_t = P3  # 上級者
        else:  # 上級者
            P_t = P3  # ずっと上級者
        
        # 次の状態を計算
        next_state_probs = P_t[current_state, best_action, :]
        next_state = np.argmax(next_state_probs)  # 最も確率の高い状態を選択
        
        # コストを更新（コスト0の場合は初期値Lに戻る）
        new_cost = L if costs[best_action] == 0 else current_cost - costs[best_action]
        
        # 行動名を変換
        action_names = ["行動1", "行動2", "行動3", "行動4"]
        action_name = action_names[best_action]
        
        rows.append({
            "期": t,
            "行動": action_name,
            "モチベーション": current_cost,
            "s1": next_state_probs[0],
            "s2": next_state_probs[1], 
            "s3": next_state_probs[2]
        })
        
        current_state = next_state
        current_cost = new_cost
    
    return rows

# スキルレベル判定関数
def get_skill_level_for_period(period, skill_level, beginner_period, intermediate_period):
    """期間に応じたスキルレベルを返す"""
    if skill_level == "初心者":
        if period <= beginner_period:
            return "初心者"
        elif period <= beginner_period + intermediate_period:
            return "中級者"
        else:
            return "上級者"
    elif skill_level == "中級者":
        if period <= intermediate_period:
            return "中級者"
        else:
            return "上級者"
    else:  # 上級者
        return "上級者"

# トレーニングメニューを生成
training_plan = generate_training_plan(init_idx, L, policy, V, costs, T, beginner_period, intermediate_period)
df_plan = pd.DataFrame(training_plan)
if choice == "良い":
    st.dataframe(df_plan[["期", "行動", "モチベーション", "s1"]].style.format({"s1": "{:.3f}"}), use_container_width=True)
elif choice == "普通":
    st.dataframe(df_plan[["期", "行動", "モチベーション", "s2"]].style.format({"s2": "{:.3f}"}), use_container_width=True)
else:  # 悪い
    st.dataframe(df_plan[["期", "行動", "モチベーション", "s3"]].style.format({"s3": "{:.3f}"}), use_container_width=True)

st.caption("※ 高度動的計画法により、スキルレベル別の最適行動を計算しています。")

# --- 結果保存機能 ---
st.subheader("結果保存")

# 保存用データの準備
save_data = {
    "設定": {
        "初期状態": choice,
        "トレーニングレベル": skill_level,
        "期間": T,
        "総コスト制限": L,
        "初心者期間": f"1-{beginner_period}期" if beginner_period > 0 else "なし",
        "中級者期間": f"{beginner_period + 1}-{beginner_period + intermediate_period}期" if intermediate_period > 0 else "なし",
        "上級者期間": f"{beginner_period + intermediate_period + 1}-{T}期" if advanced_period > 0 else "なし"
    },
    "結果": {
        "最終時点のs1確率": f"{final_state_prob:.3f}",
        "平均s1確率": f"{initial_state_prob:.3f}",
        "最終残コスト": L
    }
}

# CSVダウンロード用のデータフレーム作成
download_data = []
for i, row in enumerate(training_plan):
    download_data.append({
        "期": row["期"],
        "行動": row["行動"],
        "モチベーション": row["モチベーション"],
        "s1確率": f"{row['s1']:.3f}",
        "s2確率": f"{row['s2']:.3f}",
        "s3確率": f"{row['s3']:.3f}",
        "スキルレベル": get_skill_level_for_period(row["期"], skill_level, beginner_period, intermediate_period)
    })

download_df = pd.DataFrame(download_data)

# ダウンロードボタン
col1, col2, col3 = st.columns(3)

with col1:
    # トレーニングメニューのCSVダウンロード
    csv = download_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="トレーニングメニューをCSVで保存",
        data=csv,
        file_name=f"training_plan_{choice}_{T}days.csv",
        mime="text/csv"
    )

with col2:
    # 設定情報のJSONダウンロード
    import json
    settings_json = json.dumps(save_data, ensure_ascii=False, indent=2)
    st.download_button(
        label="設定をJSONで保存",
        data=settings_json,
        file_name=f"settings_{choice}_{T}days.json",
        mime="application/json"
    )

with col3:
    # 結果サマリーのテキストダウンロード
    summary_text = f"""
ヘルスケアアプリ - 計算結果サマリー
=====================================

【設定】
- 初期状態: {choice}
- トレーニングレベル: {skill_level}
- 期間: {T}日
- 総コスト制限: {L}
- 初心者期間: {f"1-{beginner_period}期" if beginner_period > 0 else "なし"}
- 中級者期間: {f"{beginner_period + 1}-{beginner_period + intermediate_period}期" if intermediate_period > 0 else "なし"}
- 上級者期間: {f"{beginner_period + intermediate_period + 1}-{T}期" if advanced_period > 0 else "なし"}

【結果】
- 最終時点のs1確率: {final_state_prob:.3f}
- 平均s1確率: {initial_state_prob:.3f}
- 最終残コスト: {L}

【推奨トレーニングメニュー】
{download_df.to_string(index=False)}
    """
    st.download_button(
        label="結果サマリーをTXTで保存",
        data=summary_text,
        file_name=f"summary_{choice}_{T}days.txt",
        mime="text/plain"
    )

# 結果の表示
st.subheader("保存用データプレビュー")
st.write("**設定情報:**")
st.json(save_data)

st.write("**トレーニングメニュー詳細**")
st.dataframe(download_df, use_container_width=True)

st.markdown("---")
st.info("""
**研究背景について**

スポーツ選手は成長具合に応じてトレーニングの効果が変わってくるので、トレーニングモデルを変化させてモデル化をした
""")







