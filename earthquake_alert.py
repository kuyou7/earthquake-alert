# -*- coding: utf-8 -*-
import streamlit as st
from gtts import gTTS

# メッセージ辞書
messages = {
    'ja': {
        'title': "地震速報アプリ",
        'description': "行動指示を順に表示していきます",
        'next_action': "次の行動へ",
        'actions': {
            1: "安全を確保してください。テーブルや丈夫な物の下に隠れてください。",
            2: "揺れが収まったら、避難ルートを確認し、落下物に注意してください。",
            3: "必要に応じて避難を開始してください。周囲の安全を確認してください。また、ガス栓を締め、必要であればブレーカーを落としてください。",
        },
        'all_actions_done': "全ての行動指示が完了しました。",
        'toggle_button': "English / 日本語切替",
        'no_action': "行動指示がありません。"
    },
    'en': {
        'title': "Earthquake Alert App",
        'description': "Action instructions will be shown step by step.",
        'next_action': "Next Action",
        'actions': {
            1: "Ensure your safety. Take cover under a sturdy table or object.",
            2: "After shaking stops, check evacuation routes and beware of falling objects.",
            3: "Evacuate if necessary. Confirm safety around you. Also, turn off gas valves and breakers if needed.",
        },
        'all_actions_done': "All actions completed.",
        'toggle_button': "English / 日本語 Toggle",
        'no_action': "No action instructions."
    }
}

# セッション初期化
if 'lang' not in st.session_state:
    st.session_state.lang = 'ja'
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# メッセージ選択
msg = messages[st.session_state.lang]
actions = msg['actions']

# 言語切替
def toggle_language():
    st.session_state.lang = 'en' if st.session_state.lang == 'ja' else 'ja'
    st.session_state.current_step = 1

# 音声読み上げ
def speak_text(text):
    try:
        lang_code = 'en' if st.session_state.lang == 'en' else 'ja'
        tts = gTTS(text=text, lang=lang_code)
        tts.save("step.mp3")
        st.audio("step.mp3", autoplay=True)
    except Exception as e:
        st.error(f"音声再生に失敗しました: {e}")

# 次のステップへ
def next_step():
    if st.session_state.current_step < 3:
        st.session_state.current_step += 1
    else:
        st.info(msg['all_actions_done'])

# タイトルと説明
st.title(msg['title'])
st.write(msg['description'])

# 言語切替ボタン
if st.button(msg['toggle_button']):
    toggle_language()
    st.rerun()

# 現在の行動ステップ表示
action_message = actions.get(st.session_state.current_step, msg['no_action'])
st.markdown(f"### 🧭 行動ステップ {st.session_state.current_step}")
st.write(f"**{action_message}**")

# 次へボタンと音声再生
if st.button(msg['next_action']):
    next_step()
    action_message = actions.get(st.session_state.current_step, msg['no_action'])
    st.markdown(f"### 🧭 行動ステップ {st.session_state.current_step}")
    st.write(f"**{action_message}**")
    speak_text(action_message)
