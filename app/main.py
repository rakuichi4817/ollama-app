"""一旦langhainを使わずに実装"""
from collections import namedtuple

import requests
import streamlit as st

# チャットの保存形式
Chat = namedtuple("Chat", ["role", "content"])

# ページ設定
page_title = "Ollamaデモチャットアプリ"
page_icon = "🐏"
st.set_page_config(page_title=page_title, page_icon=page_icon)

# 表示
st.write(f"# {page_icon}{page_title}")
st.write("初回メッセージ送信時、時間がかかります")

# モデルダウンロード
if "model_download" not in st.session_state:
    with st.spinner("モデル準備中"):
        requests.post(
            "http://ollama:11434/api/pull", json={"name": "llama2", "stream": False}
        )
        # 2回目以降ダウンロードしないように
        st.session_state.model_download = True

# セッション初期化
if "chat_logs" not in st.session_state:
    st.session_state.chat_logs = []


def write_chat_log(chat: Chat | None = None):
    """単一のチャットを出力するか、セッションすべてを表示する

    Notes
    -----
    引数がなければチャットログを表示

    Parameters
    ----------
    chat : Chat | None, optional
        表示するチャット, by default None
    """
    if chat:
        with st.chat_message(chat.role):
            st.write(chat.content)
    else:
        for chat_log in st.session_state.chat_logs:
            with st.chat_message(chat_log.role):
                st.write(chat_log.content)


# ユーザインプット
prompt = st.chat_input()
# セッションリセットボタン
if st.button("新規セッションの開始", type="primary", use_container_width=True):
    st.session_state.chat_logs = []

if prompt:
    # ユーザメッセージの形式変換とセッションステートへの追加
    user_chat = Chat("user", prompt)
    st.session_state.chat_logs.append(user_chat)
    # 新規ユーザチャット含むセッション内のすべてを表示
    write_chat_log()

    # ollama側に投げる
    messages = [chat_log._asdict() for chat_log in st.session_state.chat_logs]
    with st.spinner("🤖考え中"):
        response = requests.post(
            "http://ollama:11434/api/chat",
            json={"model": "llama2", "messages": messages, "stream": False},
        )
        # レスポンスの取得
        if response.status_code != 200:
            system_chat = Chat("system", "error")
        else:
            response_json = response.json()
            system_chat = Chat(
                response_json["message"]["role"], response_json["message"]["content"]
            )
    # ステートへの追加
    st.session_state.chat_logs.append(system_chat)
    # システムチャットを表示
    write_chat_log(system_chat)
