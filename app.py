import streamlit as st
import pandas as pd

st.set_page_config(page_title="Subae League AR")

st.title("🏆 Subae League AR")

st.write("Dashboard en ligne ✔️")

# chargement des matchs
matchs = pd.read_csv("matchs.csv")

st.subheader("📅 Journée 1")
st.dataframe(matchs)
