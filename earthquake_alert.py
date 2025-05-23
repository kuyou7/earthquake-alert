# -*- coding: utf-8 -*-
import requests
import xml.etree.ElementTree as ET
from gtts import gTTS
import streamlit as st
import time

# メッセージ辞書
messages = {
    'ja': {
        'title': "地震速報アプリ",
        'description': "ここに地震情報を表示します",
        'notify_button': "通知を許可",
        'notify_enabled': "通知が有効になりました！",
        'next_action': "次の行動",
        'actions': {
            1: "安全を確保してください。テーブルや丈夫な物の下に隠れてください。",
            2: "揺れが収まったら、避難ルートを確認し、落下物に注意してください。",
            3: "必要に応じて避難を開始してください。周囲の安全を確認してください。また、ガス栓を締め、必要であればブレーカーを落としてください。",
        },
        'all_actions_done': "全ての行動指示が完了しました。",
        'no_new_alert': "新しい地震速報なし",
        'fetch_error': "地震情報を取得できませんでした",
        'excluded_alert': "取得しましたが対象外: ",
        'toggle_button': "English / 日本語切替",
        'no_action': "行動指示がありません。"
    },
    'en': {
        'title': "Earthquake Alert App",
        'description': "Earthquake information will be displayed here.",
        'notify_button': "Allow Notifications",
        'notify_enabled': "Notifications have been enabled!",
        'next_action': "Next Action",
        'actions': {
            1: "Ensure your safety. Take cover under a sturdy table or object.",
            2: "After shaking stops, check evacuation routes and beware of falling objects.",
            3: "Evacuate if necessary. Confirm safety around you. Also, turn off gas valves and breakers if needed.",
        },
        'all_actions_done': "All actions completed.",
        'no_new_alert': "No new earthquake alerts",
        'fetch_error': "Could not fetch earthquake information",
        'excluded_alert': "Fetched but excluded: ",
        'toggle_button': "English / 日本語 Toggle",
        'no_action': "No action instructions."
    }
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

msg = messages[st.session_state.lang]
actions = msg['actions']

# 言語切替関数（再読み込みは関数外で）
def toggle_language():
    st.session_state.lang = 'en' if st.session_state.lang == 'ja' else 'ja'
    st.session_state.current_step = 1
    st.session_state.last_earthquake_title = ""

# 地震情報取得URL
JMA_EARTHQUAKE_FEED_URL = "https://www.data.jma.go.jp/developer/xml/feed/eqvol.xml"

def fetch_latest_earthquake_info():
    try:
        response = requests.get(JMA_EARTHQUAKE_FEED_URL, timeout=5)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        first_entry = root.find('channel/item')
        if first_entry is None:
            return None, None, None, None
        title = first_entry.find('title').text if first_entry.find('title') is not None else None
        link = first_entry.find('link').text if first_entry.find('link') is not None else None
        pubDate = first_entry.find('pubDate').text if first_entry.find('pubDate') is not None else None
        description = first_entry.find('description').text if first_entry.find('description') is not None else None
        return title, link, pubDate, description
    except Exception as e:
        print(f"地震情報取得失敗: {e}")
        return None, None, None, None

def next_step():
    if st.session_state.current_step < 3:
        st.session_state.current_step += 1
    else:
        st.info(msg['all_actions_done'])

def speak_text(text):
    try:
        lang_code = 'en' if st.session_state.lang == 'en' else 'ja'
        tts = gTTS(text=text, lang=lang_code)
        tts.save("action.mp3")
        st.audio("action.mp3", autoplay=True)
    except Exception as e:
        st.error(f"音声再生に失敗しました: {e}")

# UI表示

st.title(msg['title'])
st.write(msg['description'])

# 言語切替ボタン
if st.button(msg['toggle_button']):
    toggle_language()
    st.experimental_rerun()

# 通知許可ボタン（今はダミー）
if st.button(msg['notify_button']):
    st.success(msg['notify_enabled'])

# 5秒ごとに地震情報を更新
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
                action_message = actions.get(st.session_state.current_step, msg['no_action'])

                st.markdown(f"### ⚡ {title}")
                st.write(description)
                st.write(f"[詳細リンク]({link})")
                st.write(f"**{action_message}**")
                speak_text(action_message)

                if st.button(msg['next_action']):
                    next_step()
                    action_message = actions.get(st.session_state.current_step, msg['no_action'])
                    speak_text(action_message)
                    st.write(action_message)
            else:
                st.info(msg['excluded_alert'] + title)
        else:
            st.info(msg['no_new_alert'])
else:
    # 5秒経ってなければ前の情報だけ表示
    if st.session_state.last_earthquake_title:
        st.markdown(f"### ⚡ {st.session_state.last_earthquake_title}")
        st.write("最新の地震情報を監視中...")
    else:
        st.write(msg['description'])
