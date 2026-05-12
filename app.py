import streamlit as st
import pandas as pd

st.set_page_config(page_title="Subae League AR")

st.title("🏆 Subae League AR")

# -----------------------
# CHARGEMENT
# -----------------------
matchs = pd.read_csv("matchs.csv")

try:
    resultats = pd.read_csv("resultats.csv")
except:
    resultats = pd.DataFrame()

st.subheader("📅 Journée 1")
st.dataframe(matchs)

# -----------------------
# BARÈME OFFICIEL
# -----------------------
points_map = {
    "Passage sur le field": 1,
    "Fruit Mannam fixé": 5,
    "Autres fruits (NTF, EM, etc.)": 2,
    "Mannam présence": 10,
    "Mannam Taggui": 20,
    "BB individuel": 50,
    "BB groupe": 100,
    "CT": 200,
    "Participation OT": 500
}

# -----------------------
# CALCUL POINTS
# -----------------------
def calc(row):
    total = 0
    for k, v in points_map.items():
        total += float(row.get(k, 0)) * v
    return total

# -----------------------
# CLASSEMENT (MODE PROPRE)
# -----------------------
if not resultats.empty:

    # conversion sécurité
    for col in points_map.keys():
        if col in resultats.columns:
            resultats[col] = pd.to_numeric(resultats[col], errors="coerce").fillna(0)

    # calcul des points par équipe
    resultats["points"] = resultats.apply(calc, axis=1)

    classement = resultats.groupby("kuyok")["points"].sum().reset_index()
    classement = classement.sort_values("points", ascending=False)

    st.subheader("🏆 Classement général")
    st.dataframe(classement)

else:
    st.warning("Aucun résultat encore")
