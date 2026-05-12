import streamlit as st
import pandas as pd

st.set_page_config(page_title="Subae League AR")

st.title("🏆 Subae League AR")

st.write("🚀 App démarrée avec succès")

# test tableau simple
df = pd.DataFrame({
    "Kuyok": ["KYK1", "KYK2", "KYK3"],
    "Points": [10, 20, 15]
})

st.dataframe(df)
