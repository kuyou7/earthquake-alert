# --- 省略（上部はあなたのまま） ---

# UI表示
st.title(msg['title'])
st.write(msg['description'])

# 言語切替用フラグ初期化
if 'toggle_clicked' not in st.session_state:
    st.session_state.toggle_clicked = False

def toggle_language():
    st.session_state.lang = 'en' if st.session_state.lang == 'ja' else 'ja'
    st.session_state.current_step = 1
    st.session_state.last_earthquake_title = ""
    st.session_state.toggle_clicked = True

if st.button(msg['toggle_button']):
    toggle_language()

if st.session_state.toggle_clicked:
    st.session_state.toggle_clicked = False
    st.experimental_rerun()

# 通知許可ボタン（ダミー表示）
if st.button(msg['notify_button']):
    st.success(msg['notify_enabled'])

# --- 以降、あなたのコード通りの地震情報取得＆表示処理 ---

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
    if st.session_state.last_earthquake_title:
        st.markdown(f"### ⚡ {st.session_state.last_earthquake_title}")
        st.write("最新の地震情報を監視中...")
    else:
        st.write(msg['description'])
