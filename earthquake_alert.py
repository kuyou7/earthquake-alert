# -*- coding: utf-8 -*-
import requests
import xml.etree.ElementTree as ET
from gtts import gTTS
import streamlit as st
import time

messages = {
    'ja': { ... },  # （省略。あなたの元コードのmessagesをそのまま使う）
    'en': { ... }
}

# 初期化
if 'lang' not in st.session_state:
    st.session_state.lang = 'ja'
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'last_earthquake_title' not in st.session_state:
    st.session_state.last_earthquake_title = ""
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = 0
if 'simulated_quake' not in st.session_state:
    st.session_state.simulated_quake = False

msg = messages[st.session_state.lang]
acts = msg['actions']

# --- 以下、共通関数群（fetch_latest_earthquake_info, speak_text, play_alert_sound, is_significant_earthquake, toggle_language）をここにコピー ---

# --- ページ切り替えメニュー ---
page = st.sidebar.selectbox("メニュー / Menu", ["地震情報", "模擬地震 / Simulation"])

# 言語切替ボタン
if st.sidebar.button(msg['toggle_button']):
    toggle_language()

if page == "地震情報":
    st.title(msg['title'])

    # 行動ステップ表示
    if st.session_state.current_step <= 3:
        step_msg = acts.get(st.session_state.current_step, msg['no_action'])
        st.subheader(f"🧭 {msg['action_step_label']} {st.session_state.current_step}")
        st.write(step_msg)
        speak_text(step_msg)

        if st.button(msg['next_action']):
            st.session_state.current_step += 1
            st.experimental_rerun()
        elif st.button(msg['reset_action']):
            st.session_state.current_step = 1
            st.experimental_rerun()

    # 地震情報監視（5秒ごと）
    quake_displayed = False
    current_time = time.time()
    if current_time - st.session_state.last_update_time > 5:
        st.session_state.last_update_time = current_time
        title, link, pubDate, description = fetch_latest_earthquake_info()
        if title is None:
            st.warning(msg['fetch_error'])
        else:
            if title != st.session_state.last_earthquake_title:
                if "震度速報" in title or "震源情報" in title:
                    st.session_state.last_earthquake_title = title
                    st.markdown(f"### ⚡ {title}")
                    st.write(description)
                    st.write(f"[詳細リンク]({link})")
                    if is_significant_earthquake(title):
                        play_alert_sound()
                    quake_displayed = True
                else:
                    st.info(msg['excluded_alert'] + title)
            else:
                st.info(msg['no_new_alert'])

    if not quake_displayed and st.session_state.last_earthquake_title:
        st.write("最新の地震情報を監視中...")
    elif not quake_displayed:
        st.write(msg['no_quake'])

elif page == "模擬地震 / Simulation":
    st.title("模擬地震発生 (Simulation)")

    if st.button(msg['simulate_quake']):
        st.session_state.simulated_quake = True
        st.session_state.last_earthquake_title = "震度5弱：訓練地震"
        play_alert_sound()
        st.experimental_rerun()

    if st.session_state.simulated_quake:
        st.markdown("### ⚡ 訓練用地震発生！")
        st.write("これは訓練です。震度5弱の揺れを想定しています。")
        st.write("適切な避難行動を取ってください。")
        st.session_state.simulated_quake = False
