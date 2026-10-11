"""
Demo Day Voting — застосунок для голосування в номінаціях
Курс «Інноваційні технології», заняття 12 (модуль «AI Startup Sprint»).

Зібраний з того, що ми вивчили на курсі: Streamlit (заняття 1-2), JSON і Pandas
(заняття 8), Plotly (заняття 8), Secrets (заняття 11).

Як користуватися:
  1. Впиши назви проєктів групи у список PROJECTS нижче.
  2. Опублікуй застосунок на Streamlit Cloud і дай студентам посилання або QR-код.
     Тут спільний JSON-файл на сервері — саме те, що потрібно: усі голоси в одному місці.
     (Файл зникне після перезапуску застосунку — для одного заняття цього достатньо.)
  3. Після виступів відкрий вкладку «Результати» і введи код викладача.
Запасний варіант без інтернету — паперовий «Бюлетень голосування».
"""

import json
import os

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECTS = [
    "Horse Help",
    "LuxChange",
    "MathBOT",
    "GameMatch",
    "AI - Lingo"
]

NOMINATIONS = [
    "Найкращий UX",
    "Найсильніша AI-функція",
    "Найкреативніша ідея",
    "Найкращий MVP",
]

DATA_FILE = "votes.json"
TEACHER_CODE = st.secrets["TEACHER_CODE"]


def load_data() -> list:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(records: list) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Streamlit-інтерфейс
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Demo Day Voting", page_icon="🏆")
st.title("🏆 Demo Day — голосування")

tab_vote, tab_results = st.tabs(["Голосувати", "Результати"])

with tab_vote:
    st.info("Обери по одному проєкту в кожній номінації. За власний проєкт не голосуємо.")

    with st.form("vote"):
        voter = st.text_input("Твоє ім'я та прізвище")
        own = st.selectbox("Твій власний проєкт", ["— я гість —"] + PROJECTS)
        choices = {}
        for nomination in NOMINATIONS:
            choices[nomination] = st.selectbox(nomination, ["— обери —"] + PROJECTS)
        submitted = st.form_submit_button("✅ Проголосувати", type="primary")

    if submitted:
        records = load_data()
        name = voter.strip()
        if not name:
            st.warning("Впиши своє ім'я — так ми рахуємо один голос від людини.")
        elif any(r["voter"].lower() == name.lower() for r in records):
            st.warning("Голос від цього імені вже зараховано.")
        elif "— обери —" in choices.values():
            st.warning("Обери проєкт у кожній із чотирьох номінацій.")
        elif own in choices.values():
            st.warning("За власний проєкт не голосуємо — зміни вибір.")
        else:
            records.append({"voter": name, **choices})
            save_data(records)
            st.success("Дякуємо! Твій голос зараховано.")
            st.balloons()

with tab_results:
    code = st.text_input("Код викладача", type="password")
    if code != TEACHER_CODE:
        st.caption("Результати відкриває викладач після завершення голосування.")
    else:
        records = load_data()
        st.metric("Проголосувало", len(records))
        if not records:
            st.info("Голосів поки немає.")
        else:
            df = pd.DataFrame(records)
            for nomination in NOMINATIONS:
                counts = df[nomination].value_counts().reset_index()
                counts.columns = ["Проєкт", "Голоси"]
                winner = counts.iloc[0]
                st.subheader(f"{nomination}: {winner['Проєкт']}")
                fig = px.bar(counts, x="Проєкт", y="Голоси")
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{nomination}")
            if st.button("🗑️ Очистити всі голоси"):
                save_data([])
                st.rerun()
