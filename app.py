import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Subae League AR")

st.title("🏆 Subae League AR - Analytics Dashboard")

FILE = "resultats.csv"

# -----------------------
# LOAD DATA
# -----------------------
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=[
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
# KYK LIST
# -----------------------
all_kyk = [f"KYK{i}" for i in range(1, 19)]

# -----------------------
# BARÈME
# -----------------------
weights = {
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
# ADD RESULT
# -----------------------
st.subheader("➕ Ajouter un résultat")

with st.form("add"):
    date = st.text_input("Date")
    semaine = st.number_input("Semaine", step=1)
    kuyok = st.selectbox("KYK", all_kyk)

    field = st.number_input("Passage sur le field", step=1)
    fruit = st.number_input("Fruit Mannam fixé", step=1)
    autres = st.number_input("Autres fruits", step=1)
    presence = st.number_input("Mannam présence", step=1)
    taggui = st.number_input("Mannam Taggui", step=1)
    bb_ind = st.number_input("BB individuel", step=1)
    bb_group = st.number_input("BB groupe", step=1)
    ct = st.number_input("CT", step=1)
    ot = st.number_input("Participation OT", step=1)

    submit = st.form_submit_button("Ajouter")

if submit:
    new = {
        "date": date,
        "semaine": semaine,
        "kuyok": kuyok,
        "Passage sur le field": field,
        "Fruit Mannam fixé": fruit,
        "Autres fruits (NTF, EM, etc.)": autres,
        "Mannam présence": presence,
        "Mannam Taggui": taggui,
        "BB individuel": bb_ind,
        "BB groupe": bb_group,
        "CT": ct,
        "Participation OT": ot
    }

    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    df.to_csv(FILE, index=False)
    st.success("Ajouté ✔️")

# -----------------------
# CALC POINTS
# -----------------------
def calc(row):
    total = 0
    for k, v in weights.items():
        total += float(row.get(k, 0)) * v
    return total

if not df.empty:
    for c in weights.keys():
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["points"] = df.apply(calc, axis=1)
else:
    df["points"] = 0

# -----------------------
# CLASSEMENT GLOBAL
# -----------------------
base = pd.DataFrame({"kuyok": all_kyk})

ranking = df.groupby("kuyok")["points"].sum().reset_index()
ranking = base.merge(ranking, on="kuyok", how="left").fillna(0)
ranking = ranking.sort_values("points", ascending=False)

st.subheader("🏆 Classement général")
st.dataframe(ranking, hide_index=True)

# -----------------------
# TOP 3
# -----------------------
st.subheader("🥇 Top 3")
top3 = ranking.head(3).copy()
top3["rank"] = ["🥇","🥈","🥉"]
st.dataframe(top3[["rank","kuyok","points"]], hide_index=True)

# -----------------------
# GLOBAL CHART
# -----------------------
st.subheader("📊 Forces globales")
st.bar_chart(ranking.set_index("kuyok")["points"])

# -----------------------
# EVOLUTION
# -----------------------
st.subheader("📈 Evolution semaine")

if not df.empty:
    evo = df.groupby(["semaine","kuyok"])["points"].sum().reset_index()
    pivot = evo.pivot(index="semaine", columns="kuyok", values="points").fillna(0)
    st.line_chart(pivot)

# -----------------------
# PORTRAIT KYK
# -----------------------
st.subheader("🧠 Portrait KYK")

for k in all_kyk:
    sub = df[df["kuyok"] == k]

    st.markdown(f"### {k}")

    if sub.empty:
        st.info("Aucune donnée")
        continue

    stats = {c: sub[c].sum() for c in weights.keys()}

    total = sum(stats.values())
    ot_rate = (stats["Participation OT"] / stats["Fruit Mannam fixé"] * 100) if stats["Fruit Mannam fixé"] > 0 else 0

    # TYPE KYK
    if stats["CT"] > stats["BB groupe"] and stats["CT"] > stats["Mannam présence"]:
        typ = "🧠 KYK impact"
    elif stats["Passage sur le field"] + stats["Mannam présence"] > stats["BB individuel"]:
        typ = "🧱 KYK terrain"
    else:
        typ = "⚡ KYK équilibré"

    st.write(f"Type : {typ}")
    st.write(f"Total points : {ranking[ranking['kuyok']==k]['points'].values[0] if k in ranking['kuyok'].values else 0:.0f}")
    st.write(f"Taux conversion Mannam → OT : {ot_rate:.1f}%")

    st.bar_chart(pd.DataFrame.from_dict(stats, orient="index"))

# -----------------------
# RAW DATA
# -----------------------
st.subheader("📊 Données brutes")
st.dataframe(df)
