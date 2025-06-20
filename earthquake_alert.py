# -*- coding: utf-8 -*-
import requests
import xml.etree.ElementTree as ET
from gtts import gTTS
import streamlit as st
import time

# メッセージ辞書（多言語対応）
messages = {
    'ja': {
        'title': "地震速報アプリ",
        'description': "ここに地震情報を表示します",
        'no_quake': "地震は確認されませんでした。",
        'notify_button': "通知を許可",
        'notify_enabled': "通知が有効になりました！",
        'next_action': "次の行動",
        'reset_action': "最初からやり直す",
        'simulate_quake': "🔁 模擬地震を発生させる",
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
        'no_action': "行動指示がありません。",
        'action_step_label': "行動ステップ"
    },
    'en': {
        'title': "Earthquake Alert App",
        'description': "Earthquake information will be displayed here.",
        'no_quake': "No earthquake was detected.",
        'notify_button': "Allow Notifications",
        'notify_enabled': "Notifications have been enabled!",
        'next_action': "Next Action",
        'reset_action': "Restart",
        'simulate_quake': "🔁 Simulate Earthquake",
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
        'no_action': "No action instructions.",
        'action_step_label': "Action Step"
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
if 'simulated_quake' not in st.session_state:
    st.session_state.simulated_quake = False

msg = messages[st.session_state.lang]
acts = msg['actions']

JMA_EARTHQUAKE_FEED_URL = "https://www.data.jma.go.jp/developer/xml/feed/eqvol.xml"

# 地震情報取得関数
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

# 音声読み上げ
def speak_text(text):
    try:
        lang_code = 'en' if st.session_state.lang == 'en' else 'ja'
        tts = gTTS(text=text, lang=lang_code)
        tts.save("action.mp3")
        st.audio("action.mp3", autoplay=True)
    except Exception as e:
        st.error(f"音声再生に失敗しました: {e}")

# 警報音再生
def play_alert_sound():
    try:
        st.audio("alert.mp3", autoplay=True)
    except Exception as e:
        st.error(f"警報音の再生に失敗しました: {e}")

# 震度4以上の判定
def is_significant_earthquake(title):
    keywords = ["震度4", "震度5", "震度6", "震度7"]
    return any(level in title for level in keywords)

# 言語切替
def toggle_language():
    st.session_state.lang = 'en' if st.session_state.lang == 'ja' else 'ja'
    st.rerun()

# ---------------- UI ----------------

st.title(msg['title'])

# 言語切替ボタン
if st.button(msg['toggle_button']):
    toggle_language()

# 行動ステップ表示
if st.session_state.current_step <= 3:
    step_msg = acts.get(st.session_state.current_step, msg['no_action'])
    st.subheader(f"🧭 {msg['action_step_label']} {st.session_state.current_step}")
    st.write(step_msg)
    speak_text(step_msg)

    if st.button(msg['next_action']):
        st.session_state.current_step += 1
        st.rerun()
elif st.button(msg['reset_action']):
    st.session_state.current_step = 1
    st.rerun()

# 模擬地震ボタン（訓練用）
if st.button(msg['simulate_quake']):
    st.session_state.simulated_quake = True
    st.session_state.last_earthquake_title = "震度5弱：訓練地震"
    play_alert_sound()
    st.rerun()

# 地震情報の監視と表示（5秒おき）
quake_displayed = False
current_time = time.time()

if current_time - st.session_state.last_update_time > 5:
    st.session_state.last_update_time = current_time

    if st.session_state.simulated_quake:
        st.markdown("### ⚡ 訓練用地震発生！")
        st.write("これは訓練です。震度5弱の揺れを想定しています。")
        st.write("適切な避難行動を取ってください。")
        st.session_state.simulated_quake = False
        quake_displayed = True
    else:
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

# 前回の地震情報の再表示
if not quake_displayed and st.session_state.last_earthquake_title:
    st.write("最新の地震情報を監視中...")
elif not quake_displayed:
    st.write(msg['no_quake'])
