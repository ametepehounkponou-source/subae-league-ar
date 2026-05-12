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
# CALCUL
# -----------------------
def calc(row):
    total = 0
    for k, v in points_map.items():
        total += float(row.get(k, 0)) * v
    return total

# -----------------------
# PREP DATA
# -----------------------
if not resultats.empty:
    for col in points_map.keys():
        if col in resultats.columns:
            resultats[col] = pd.to_numeric(resultats[col], errors="coerce").fillna(0)
        else:
            resultats[col] = 0

    resultats["points"] = resultats.apply(calc, axis=1)
else:
    resultats["points"] = 0

# -----------------------
# CLASSEMENT GLOBAL
# -----------------------
base = pd.DataFrame({"kuyok": all_kyk})

classement = resultats.groupby("kuyok")["points"].sum().reset_index()
classement = base.merge(classement, on="kuyok", how="left").fillna(0)
classement = classement.sort_values("points", ascending=False)

st.subheader("🏆 Classement général")
st.dataframe(classement, hide_index=True)

# -----------------------
# 🥇 TOP 3
# -----------------------
st.subheader("🥇 Top 3")
top3 = classement.head(3).copy()
top3["rank"] = ["🥇", "🥈", "🥉"]
st.dataframe(top3[["rank", "kuyok", "points"]], hide_index=True)

# -----------------------
# 📊 BAR CHART GLOBAL
# -----------------------
st.subheader("📊 Forces globales")
st.bar_chart(classement.set_index("kuyok")["points"])

# -----------------------
# 🧠 ANALYSE PAR KYK (FORCES / FAIBLESSES)
# -----------------------
st.subheader("🧠 Analyse des forces et faiblesses")

for kyk in all_kyk:
    df = resultats[resultats["kuyok"] == kyk]

    st.markdown(f"### {kyk}")

    if df.empty:
        st.info("Aucune donnée")
        continue

    stats = {}
    for k in points_map.keys():
        stats[k] = df[k].sum()

    stat_df = pd.DataFrame.from_dict(stats, orient="index", columns=["points"])
    stat_df = stat_df.sort_values("points", ascending=False)

    # point fort / faible
    strong = stat_df.index[0]
    weak = stat_df.index[-1]

    st.write(f"🔥 Point fort : **{strong}**")
    st.write(f"❄️ Point faible : **{weak}**")

    st.bar_chart(stat_df)

# -----------------------
# DONNÉES BRUTES
# -----------------------
st.subheader("📊 Données brutes")
st.dataframe(resultats)
