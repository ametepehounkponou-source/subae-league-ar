import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Subae League AR")

st.title("🏆 Subae League AR")

FILE = "resultats.csv"

# -----------------------
# CHARGEMENT
# -----------------------
if os.path.exists(FILE):
    resultats = pd.read_csv(FILE)
else:
    resultats = pd.DataFrame(columns=[
        "date","semaine","kuyok",
        "Passage sur le field",
        "Fruit Mannam fixé",
        "Autres fruits (NTF, EM, etc.)",
        "Mannam présence",
        "Mannam Taggui",
        "BB individuel",
        "BB groupe",
        "CT",
        "Participation OT"
    ])

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

all_kyk = [f"KYK{i}" for i in range(1, 19)]

# -----------------------
# CALCUL POINTS
# -----------------------
def calc(row):
    total = 0
    for k, v in points_map.items():
        total += float(row.get(k, 0)) * v
    return total

# -----------------------
# PREPARATION DATA
# -----------------------
if not resultats.empty:
    for col in points_map.keys():
        if col in resultats.columns:
            resultats[col] = pd.to_numeric(resultats[col], errors="coerce").fillna(0)
        else:
            resultats[col] = 0

    resultats["points"] = resultats.apply(calc, axis=1)

    classement = resultats.groupby("kuyok")["points"].sum().reset_index()
else:
    classement = pd.DataFrame(columns=["kuyok", "points"])

base = pd.DataFrame({"kuyok": all_kyk})
classement = base.merge(classement, on="kuyok", how="left").fillna(0)

classement = classement.sort_values("points", ascending=False)

# -----------------------
# 🏆 TOP 3 VISUEL
# -----------------------
st.subheader("🥇 Top 3 du championnat")

top3 = classement.head(3).copy()
top3["position"] = ["🥇", "🥈", "🥉"]

st.dataframe(top3[["position", "kuyok", "points"]], hide_index=True)

# -----------------------
# 🏆 CLASSEMENT COMPLET
# -----------------------
st.subheader("🏆 Classement général (tous les KYK)")
st.dataframe(classement, hide_index=True)

# -----------------------
# 📊 GRAPHIQUE GLOBAL
# -----------------------
st.subheader("📈 Graphique des points")

chart_data = classement.set_index("kuyok")["points"]
st.bar_chart(chart_data)

# -----------------------
# 📊 ÉVOLUTION SI DONNÉES
# -----------------------
if not resultats.empty:
    st.subheader("📊 Évolution des performances")

    evo = resultats.groupby(["semaine", "kuyok"])["points"].sum().reset_index()
    pivot = evo.pivot(index="semaine", columns="kuyok", values="points").fillna(0)

    st.line_chart(pivot)

# -----------------------
# DONNÉES BRUTES
# -----------------------
st.subheader("📊 Résultats bruts")
st.dataframe(resultats)
