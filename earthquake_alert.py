# -*- coding: utf-8 -*-
import requests, time
import xml.etree.ElementTree as ET
from gtts import gTTS
import streamlit as st
from datetime import datetime

# ──────────────────────────  設定  ────────────────────────── #
JMA_FEED = "https://www.data.jma.go.jp/developer/xml/feed/eqvol.xml"
ALERT_MP3 = "alert.mp3"          # ← 警報音ファイル
STEP_MP3  = "action.mp3"         # ← 行動読み上げ一時ファイル
CHECK_INTERVAL = 5               # フィード取得間隔 (秒)
ALERT_LEVELS  = ["震度4", "震度5", "震度6", "震度7"]  # 警報音対象
# ─────────────────────────────────────────────────────────── #

# ─── 多言語メッセージ ─── #
messages = {
    'ja': { 'title':"地震速報アプリ",'description':"ここに地震情報を表示します",
            'no_quake':"地震は確認されませんでした。",'next':"次の行動",
            'reset':"最初からやり直す",'toggle':"English / 日本語切替",
            'step_label':"行動ステップ",
            'actions':{1:"安全を確保してください。テーブルや丈夫な物の下に隠れてください。",
                       2:"揺れが収まったら、避難ルートを確認し、落下物に注意してください。",
                       3:"必要に応じて避難を開始してください。周囲の安全を確認してください。また、ガス栓を締め、必要であればブレーカーを落としてください。"}},
    'en': { 'title':"Earthquake Alert App",'description':"Earthquake information will be displayed here.",
            'no_quake':"No earthquake was detected.",'next':"Next Action",
            'reset':"Restart",'toggle':"English / 日本語 Toggle",
            'step_label':"Action Step",
            'actions':{1:"Ensure your safety. Take cover under a sturdy table or object.",
                       2:"After shaking stops, check evacuation routes and beware of falling objects.",
                       3:"Evacuate if necessary. Confirm safety around you. Also, turn off gas valves and breakers if needed."}}
}

# ─── Session State 初期化 ─── #
for key, default in [('lang','ja'),('step',1),('last_title',''),('last_time',0)]:
    if key not in st.session_state: st.session_state[key]=default

msg   = messages[st.session_state.lang]
acts  = msg['actions']

# ─── ユーティリティ ─── #
def tts_play(text):
    lang = 'en' if st.session_state.lang=='en' else 'ja'
    gTTS(text=text, lang=lang).save(STEP_MP3)
    st.audio(STEP_MP3, autoplay=True)

def play_alert():     # 警報音
    st.audio(ALERT_MP3, autoplay=True)

def is_significant(title):       # 震度4 以上判定
    return any(k in title for k in ALERT_LEVELS)

def fetch_quake():
    try:
        xml = requests.get(JMA_FEED,timeout=5); xml.raise_for_status()
        root = ET.fromstring(xml.content)
        item = root.find('channel/item')
        if item is None: return None
        return {'title':item.findtext('title'),
                'link' :item.findtext('link'),
                'desc' :item.findtext('description')}
    except Exception as e:
        print("fetch error:",e); return None

# ─── UI ─── #
st.title(msg['title'])
st.write(msg['description'])

if st.button(msg['toggle']):
    st.session_state.lang = 'en' if st.session_state.lang=='ja' else 'ja'
    st.rerun()

# --- 訓練モード (Simulate) ------------------------------ #
with st.expander("🚧 訓練モード / Simulation"):
    level   = st.selectbox("震度 (Intensity)", ["震度4","震度5弱","震度5強","震度6弱","震度6強","震度7"])
    sim_desc= st.text_input("説明 / Description", "これは訓練です。")
    if st.button("訓練開始 / Trigger Drill"):
        sim_title = f"{datetime.now().strftime('%m月%d日%H:%M')} {level} 訓練"
        st.session_state.last_title = ""          # 強制的に新規扱い
        st.session_state.sim_quake  = {'title':sim_title,'link':'#','desc':sim_desc}
        st.session_state.step = 1                 # ステップをリセット
        st.experimental_rerun()
# -------------------------------------------------------- #

# --- 地震フィード取得 (インターバル制御) -------------- #
quake = None
if time.time()-st.session_state.last_time > CHECK_INTERVAL:
    st.session_state.last_time = time.time()
    quake = fetch_quake()
    # 訓練モード優先
    if 'sim_quake' in st.session_state:
        quake = st.session_state.pop('sim_quake')
else:
    quake = None

# --- 地震情報処理 ------------------------------------ #
if quake and quake['title']:
    if quake['title'] != st.session_state.last_title:
        st.session_state.last_title = quake['title']
        st.markdown(f"### ⚡ {quake['title']}")
        st.write(quake['desc'])
        st.write(f"[詳細リンク]({quake['link']})")
        # 警報条件
        if is_significant(quake['title']): play_alert()
else:
    if st.session_state.last_title:
        st.write("最新の地震情報を監視中...")

# --- 行動ステップ表示 -------------------------------- #
if st.session_state.step <= 3:
    step_msg = acts.get(st.session_state.step, msg['no_action'])
    st.subheader(f"🧭 {msg['step_label']} {st.session_state.step}")
    st.write(step_msg)
    tts_play(step_msg)
    if st.button(msg['next']):
        st.session_state.step +=1
        st.rerun()
elif st.button(msg['reset']):
    st.session_state.step = 1
    st.rerun()
