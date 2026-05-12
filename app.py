import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Subae League AR")

st.title("🏆 Subae League AR")

FILE = "resultats.csv"

# -----------------------
# LOAD DATA
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
# PREP DATA
# -----------------------
if not resultats.empty:
    for col in points_map.keys():
        if col in resultats.columns:
            resultats[col] = pd.to_numeric(resultats[col], errors="coerce").fillna(0)
        else:
            resultats[col] = 0

    resultats["points"] = resultats.apply(calc, axis=1)

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
# 📈 PROGRESSION HEBDO
# -----------------------
st.subheader("📊 Progression semaine")

if not resultats.empty:

    weekly = resultats.groupby(["semaine", "kuyok"])["points"].sum().reset_index()
    pivot = weekly.pivot(index="kuyok", columns="semaine", values="points").fillna(0)

    st.dataframe(pivot)

    # -----------------------
    # 🧠 PROGRESSION / RÉGRESSION
    # -----------------------
    st.subheader("📈 Meilleure progression / 📉 plus grosse régression")

    if pivot.shape[1] >= 2:
        last_week = pivot.columns.max()
        prev_week = last_week - 1

        pivot["diff"] = pivot[last_week] - pivot[prev_week]

        best = pivot["diff"].idxmax()
        worst = pivot["diff"].idxmin()

        st.success(f"🔥 Meilleure progression : {best} (+{pivot['diff'].max()})")
        st.error(f"📉 Plus grosse régression : {worst} ({pivot['diff'].min()})")

# -----------------------
# TOP 3
# -----------------------
st.subheader("🥇 Top 3")
top3 = classement.head(3).copy()
top3["rank"] = ["🥇", "🥈", "🥉"]
st.dataframe(top3[["rank", "kuyok", "points"]], hide_index=True)

# -----------------------
# GRAPH GLOBAL
# -----------------------
st.subheader("📊 Forces globales")
st.bar_chart(classement.set_index("kuyok")["points"])

# -----------------------
# ANALYSE PAR KYK
# -----------------------
st.subheader("🧠 Analyse des forces")

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

    st.bar_chart(stat_df)

# -----------------------
# DATA
# -----------------------
st.subheader("📊 Résultats bruts")
st.dataframe(resultats)
