import streamlit as st
import pandas as pd

st.set_page_config(page_title="Subae League AR")

st.title("🏆 Subae League AR")

# chargement
matchs = pd.read_csv("matchs.csv")
resultats = pd.read_csv("resultats.csv")

st.subheader("📅 Journée 1")
st.dataframe(matchs)

# barème
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

# calcul score
def calcul_points(row):
    total = 0
    for k, v in points_map.items():
        total += row.get(k, 0) * v
    return total

if not resultats.empty:
    resultats["points"] = resultats.apply(calcul_points, axis=1)

    classement = resultats.groupby("kuyok")["points"].sum().reset_index()
    classement = classement.sort_values("points", ascending=False)

    st.subheader("🏆 Classement")
    st.dataframe(classement)
else:
    st.info("Aucun résultat pour le moment")
