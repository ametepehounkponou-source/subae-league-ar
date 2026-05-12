import streamlit as st
import pandas as pd

st.set_page_config(page_title="Subae League AR")

st.title("🏆 Subae League AR")

# -----------------------
# CHARGEMENT CSV
# -----------------------
matchs = pd.read_csv("matchs.csv")
resultats = pd.read_csv("resultats.csv")

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
# DEBUG IMPORTANT (voir les données réelles)
# -----------------------
st.subheader("🔍 DEBUG - données brutes")
st.dataframe(resultats)

# -----------------------
# NETTOYAGE DES COLONNES
# -----------------------
for col in points_map.keys():
    if col in resultats.columns:
        resultats[col] = pd.to_numeric(resultats[col], errors="coerce").fillna(0)
    else:
        resultats[col] = 0  # si colonne manquante → 0

# -----------------------
# CALCUL POINTS
# -----------------------
def calc(row):
    total = 0
    for k, v in points_map.items():
        val = float(row.get(k, 0))
        total += val * v
    return total

resultats["points"] = resultats.apply(calc, axis=1)

# -----------------------
# CLASSEMENT
# -----------------------
classement = resultats.groupby("kuyok")["points"].sum().reset_index()
classement = classement.sort_values("points", ascending=False)

st.subheader("🏆 Classement général")
st.dataframe(classement)

# -----------------------
# DEBUG PAR LIGNE
# -----------------------
st.subheader("🧮 DEBUG - calcul ligne par ligne")
for _, row in resultats.iterrows():
    st.write(row["kuyok"], "→", row["points"], "points")
