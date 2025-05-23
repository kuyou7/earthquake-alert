import streamlit as st

def toggle_language():
    st.session_state.lang = 'en' if st.session_state.lang == 'ja' else 'ja'

if 'lang' not in st.session_state:
    st.session_state.lang = 'ja'

st.write(f"Current language: {st.session_state.lang}")

if st.button("Toggle Language"):
    toggle_language()
    st.experimental_rerun()


