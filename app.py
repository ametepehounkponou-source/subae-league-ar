import streamlit as st
import pandas as pd

st.title("🏆 Subae League AR")

st.success("App connectée et fonctionnelle")

st.write("Dashboard en cours de construction...")

# test tableau
df = pd.DataFrame({
    "Kuyok": ["KYK1", "KYK2", "KYK3"],
    "Points": [10, 20, 15]
})

st.dataframe(df)
