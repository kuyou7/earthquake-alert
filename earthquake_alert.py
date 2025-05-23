# -*- coding: utf-8 -*-
import requests
import xml.etree.ElementTree as ET
from gtts import gTTS
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# 言語ごとのメッセージ辞書
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
        'toggle_button': "English / 日本語切替"
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
        'toggle_button': "English / 日本語 Toggle"
    }
}

# 気象庁 地震速報フィードURL
JMA_EARTHQUAKE_FEED_URL = "https://www.data.jma.go.jp/developer/xml/feed/eqvol.xml"

# セッションステート初期化
if 'lang' not in st.session_state:
    st.session_state.lang = 'ja'

if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

if 'last_earthquake_title' not in st.session_state:
    st.session_state.last_earthquake_title = ""

# 言語切替関数
def toggle_language():
    st.session_state.lang = 'en' if st.session_state.lang == 'ja' else 'ja'

# 自動更新設定（5秒ごと）
st_autorefresh(interval=5 * 1000, key="earthquake_refresh")

msg = messages[st.session_state.lang]
actions = msg['actions']

# 言語切替ボタン
if st.button(msg['toggle_button'], key='toggle_lang'):
    toggle_language()
    st.experimental_rerun()  # 言語切替時に即時更新

# ページ表示
st.title(msg['title'])
st.write(msg['description'])

# 通知許可ボタン
if st.button(msg['notify_button'], key='notify_button'):
    st.write(msg['notify_enabled'])

def fetch_latest_earthquake_info():
    try:
        response = requests.get(JMA_EARTHQUAKE_FEED_URL)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        first_entry = root.find('channel/item')
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
        st.write(msg['all_actions_done'])

    action_message = actions.get(st.session_state.current_step, "No action instructions." if st.session_state.lang == 'en' else "行動指示がありません。")

    tts = gTTS(text=action_message, lang='en' if st.session_state.lang == 'en' else 'ja')
    tts.save("action.mp3")

    st.audio("action.mp3", autoplay=True)
    st.write(action_message)

def alert_user(title, link, description):
    action_message = actions.get(st.session_state.current_step, "No action instructions." if st.session_state.lang == 'en' else "行動指示がありません。")

    tts = gTTS(text=action_message, lang='en' if st.session_state.lang == 'en' else 'ja')
    tts.save("earthquake_alert.mp3")

    st.audio("earthquake_alert.mp3", autoplay=True)

    st.write(f"⚡ {title}")
    st.write(description)
    st.write(link)
    st.write(action_message)

    if st.button(msg['next_action'], key='next_action'):
        next_step()

# 地震速報1回取得
title, link, pubDate, description = fetch_latest_earthquake_info()

if title:
    if title != st.session_state.last_earthquake_title:
        if "震度速報" in title or "震源情報" in title:
            alert_user(title, link, description)
            st.session_state.last_earthquake_title = title
        else:
            st.write(msg['excluded_alert'] + title)
    else:
        st.write(msg['no_new_alert'])
else:
    st.write(msg['fetch_error'])
