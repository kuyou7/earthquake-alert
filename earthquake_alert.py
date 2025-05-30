# -*- coding: utf-8 -*-
import requests
import xml.etree.ElementTree as ET
from gtts import gTTS
import streamlit as st
import time

# --- 多言語メッセージ辞書 ---
messages = {
    'ja': {
        'title': "地震速報アプリ",
        'description': "ここに地震情報と行動指示を表示します",
        'no_quake': "地震は確認されませんでした。",
        'next_action': "次の行動",
        'reset': "リセット",
        'actions': {
            1: "安全を確保してください。テーブルや丈夫な物の下に隠れてください。",
            2: "揺れが収まったら、避難ルートを確認し、落下物に注意してください。",
            3: "必要に応じて避難を開始してください。周囲の安全を確認してください。また、ガス栓を締め、必要であればブレーカーを落としてください。",
        },
        'all_actions_done': "全ての行動指示が完了しました。",
        'no_action': "行動指示がありません。",
        'new_quake': "⚡ 地震速報を検知しました！",
    }
}

# --- 初期化 ---
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'last_earthquake_title' not in st.session_state:
    st.session_state.last_earthquake_title = ""

msg = messages['ja']
actions = msg['actions']

# --- 地震情報取得 ---
def fetch_latest_earthquake_info():
    FEED_URL = "https://www.data.jma.go.jp/developer/xml/feed/eqvol.xml"
    try:
        response = requests.get(FEED_URL, timeout=5)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        first_entry = root.find('channel/item')
        if first_entry is None:
            return None, None, None
        title = first_entry.find('title').text
        description = first_entry.find('description').text
        link = first_entry.find('link').text
        return title, description, link
    except Exception as e:
        return None, None, None

# --- 音声出力 ---
def speak(text):
    tts = gTTS(text=text, lang='ja')
    tts.save("action.mp3")
    st.audio("action.mp3", autoplay=True)

# --- UI ---
st.title(msg['title'])
st.write(msg['description'])

# --- 地震情報取得と表示 ---
title, description, link = fetch_latest_earthquake_info()
if title and title != st.session_state.last_earthquake_title and ("震度速報" in title or "震源情報" in title):
    st.session_state.last_earthquake_title = title
    st.session_state.current_step = 1  # 新しい地震検知でステップ1から開始
    st.success(f"{msg['new_quake']} {title}")
    st.write(description)
    st.write(f"[詳細はこちら]({link})")

# --- 行動指示表示 ---
placeholder = st.empty()

if st.session_state.current_step > 0 and st.session_state.current_step <= 3:
    with placeholder.container():
        st.markdown(f"### 行動ステップ {st.session_state.current_step}")
        st.write(actions[st.session_state.current_step])
        speak(actions[st.session_state.current_step])
        if st.button(msg['next_action']):
            st.session_state.current_step += 1
            st.rerun()
elif st.session_state.current_step > 3:
    with placeholder.container():
        st.success(msg['all_actions_done'])
        if st.button(msg['reset']):
            st.session_state.current_step = 0
            st.rerun()
else:
    st.write(msg['no_quake'])
