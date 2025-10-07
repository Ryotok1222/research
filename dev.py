import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="ヘルスケアアプリ", layout="wide")
st.title("ヘルスケアアプリ")
st.write("常に最高のコンディション保持のために")

# --- UI ---
with st.form("sim_form"):
    choice = st.radio("あなたの状態は？", ["良い", "普通", "悪い"], horizontal=True)
    T = st.radio("期間は？(最大31日間まで選択可能)", list(range(1, 31)), horizontal=True, index=2)  
    L = st.number_input("トレーニングに対するモチベーション", min_value=1, max_value=6, value=6, step=1)
    submitted = st.form_submit_button("計算する")

if not submitted:
    st.stop()

# --- MDPの設定 ---
states = {"s1": 0, "s2": 1, "s3": 2}
actions = ["a1", "a2", "a3"]
action_cost = {"a1": 2, "a2": 1, "a3": 0}

# 遷移確率行列（行=現在状態 s1/s2/s3, 列=次状態 s1/s2/s3）
transition_matrices = {
    "a1": np.array([[0.9, 0.1, 0.0],
                    [0.6, 0.35, 0.05],
                    [0.2, 0.7, 0.1]]),
    "a2": np.array([[0.7, 0.25, 0.05],
                    [0.25, 0.55, 0.2],
                    [0.0, 0.5, 0.5]]),
    "a3": np.array([[0.5, 0.3, 0.2],
                    [0.0, 0.5, 0.5],
                    [0.0, 0.0, 1.0]]),
}

# 初期状態ベクトルを選択に応じて作成
init_idx = {"良い": 0, "普通": 1, "悪い": 2}[choice]
state_vec = np.zeros(3)
state_vec[init_idx] = 1.0  # 例: 良い→[1,0,0]

def best_action_under_budget(state_vec: np.ndarray, budget: int):
    """
    予算内で選べる行動のうち、次期の s1 確率を最大化する行動を返す。
    返り値: (action, next_state_vec) 予算内で何も選べなければ (None, None)
    """
    candidates = [a for a in actions if action_cost[a] <= budget]
    if not candidates:
        return None, None

    scored = []
    for a in candidates:
        next_vec = state_vec @ transition_matrices[a]  # 行ベクトル×遷移行列
        p_s1 = next_vec[states["s1"]]
        scored.append((a, p_s1, next_vec))

    # s1確率が最大、同点なら低コスト優先
    a_best, _, next_best = max(scored, key=lambda x: (x[1], -action_cost[x[0]]))
    return a_best, next_best

# --- シミュレーション ---
rows = []
remain = int(L)
cur = state_vec.copy()

for t in range(1, int(T) + 1):
    act, nxt = best_action_under_budget(cur, remain)
    if act is None:
        rows.append({"期": t, "行動": "なし(予算不足)", "残りコスト(前)": remain,
                     "s1": cur[0], "s2": cur[1], "s3": cur[2]})
        break

    rows.append({"期": t, "行動": act, "残りコスト(前)": remain,
                 "s1": nxt[0], "s2": nxt[1], "s3": nxt[2]})
    remain -= action_cost[act]
    cur = nxt

df = pd.DataFrame(rows)
# df を作った後、表示する前に置換
df["行動"] = df["行動"].replace({"a1": "高強度", "a2": "中強度", "a3": "低強度"})

col1, col2, col3 = st.columns(3)
col1.metric("最終時点の確率", f"{cur[0]:.3f}")
col2.metric("平均確率（各期）", f"{df['s1'].mean():.3f}")
col3.metric("最終モチベーション", f"{remain}")

st.subheader("トレーニングメニューのおすすめ")
st.dataframe(df.style.format({"s1": "{:.3f}", "s2": "{:.3f}", "s3": "{:.3f}"}), use_container_width=True)

st.caption("※ 方策は貪欲（各期で次期の s1 確率が最大の行動を予算内で選択）。行列やコストはコード上部で変更できます。")

# --- 結果保存機能 ---
st.subheader("結果保存")

# 保存用データの準備
save_data = {
    "設定": {
        "初期状態": choice,
        "期間": T,
        "モチベーション": L,
        "行動コスト": {
            "高強度(a1)": action_cost["a1"],
            "中強度(a2)": action_cost["a2"],
            "低強度(a3)": action_cost["a3"]
        }
    },
    "結果": {
        "最終時点のs1確率": f"{cur[0]:.3f}",
        "平均s1確率": f"{df['s1'].mean():.3f}",
        "最終残コスト": remain
    }
}

# CSVダウンロード用のデータフレーム作成
download_data = []
for i, row in df.iterrows():
    download_data.append({
        "期": row["期"],
        "行動": row["行動"],
        "残りコスト": row["残りコスト(前)"],
        "s1確率": f"{row['s1']:.3f}",
        "s2確率": f"{row['s2']:.3f}",
        "s3確率": f"{row['s3']:.3f}"
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
ヘルスケアアプリ（従来研究） - 計算結果サマリー
===============================================

【設定】
- 初期状態: {choice}
- 期間: {T}日
- モチベーション: {L}
- 高強度コスト: {action_cost['a1']}
- 中強度コスト: {action_cost['a2']}
- 低強度コスト: {action_cost['a3']}

【結果】
- 最終時点のs1確率: {cur[0]:.3f}
- 平均s1確率: {df['s1'].mean():.3f}
- 最終残コスト: {remain}

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