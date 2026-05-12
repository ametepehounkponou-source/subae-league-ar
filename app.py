import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Subae League AR")

st.title("🏆 Subae League AR")

FILE = "resultats.csv"

# -----------------------
# CHARGEMENT SIMPLE
# -----------------------
if os.path.exists(FILE):
    resultats = pd.read_csv(FILE)
else:
    resultats = pd.DataFrame()

st.subheader("📊 Résultats bruts")
st.dataframe(resultats)

# -----------------------
# BARÈME
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
# CALCUL SIMPLE
# -----------------------
def calc(row):
    total = 0
    for k, v in points_map.items():
        total += float(row.get(k, 0)) * v
    return total

if not resultats.empty:
    for col in points_map.keys():
        if col in resultats.columns:
            resultats[col] = pd.to_numeric(resultats[col], errors="coerce").fillna(0)
        else:
            resultats[col] = 0

    resultats["points"] = resultats.apply(calc, axis=1)

    classement = resultats.groupby("kuyok")["points"].sum().reset_index()
    classement = classement.sort_values("points", ascending=False)

    st.subheader("🏆 Classement général")
    st.dataframe(classement)

# -----------------------
# CLASSEMENT COMPLET (TOUS KYK)
# -----------------------
all_kyk = [f"KYK{i}" for i in range(1, 19)]
base = pd.DataFrame({"kuyok": all_kyk})

if not resultats.empty:
    classement = resultats.groupby("kuyok")["points"].sum().reset_index()
    classement = base.merge(classement, on="kuyok", how="left").fillna(0)
else:
    classement = base
    classement["points"] = 0

classement = classement.sort_values("points", ascending=False)

st.subheader("🏆 Classement (stable)")
st.dataframe(classement)
