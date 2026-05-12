import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

st.set_page_config(page_title="Subae League AR")

st.title("🏆 Subae League AR - FIFA Radar Edition")

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
# CALCUL GLOBAL
# -----------------------
def calc(row):
    return sum(float(row.get(k,0))*v for k,v in weights.items())

if not df.empty:
    for c in weights:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["points"] = df.apply(calc, axis=1)
else:
    df["points"] = 0

# -----------------------
# CLASSEMENT
# -----------------------
base = pd.DataFrame({"kuyok": all_kyk})
ranking = df.groupby("kuyok")["points"].sum().reset_index()
ranking = base.merge(ranking, on="kuyok", how="left").fillna(0)

st.subheader("🏆 Classement")
st.dataframe(ranking.sort_values("points", ascending=False), hide_index=True)

# -----------------------
# 🔥 RADAR FIFA
# -----------------------
st.subheader("🎮 Radar FIFA des KYK")

kyk = st.selectbox("Choisir un KYK", all_kyk)

sub = df[df["kuyok"] == kyk]

if sub.empty:
    st.info("Aucune donnée pour ce KYK")
else:
    stats = {
        "Field": sub["Passage sur le field"].sum(),
        "Mannam": sub["Mannam présence"].sum(),
        "Taggui": sub["Mannam Taggui"].sum(),
        "BB": sub["BB groupe"].sum() + sub["BB individuel"].sum(),
        "CT": sub["CT"].sum(),
        "OT": sub["Participation OT"].sum()
    }

    categories = list(stats.keys())
    values = list(stats.values())

    # normalisation (0-100 pour radar propre)
    max_val = max(values) if max(values) > 0 else 1
    values_norm = [v/max_val*100 for v in values]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_norm,
        theta=categories,
        fill='toself',
        name=kyk
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0,100])
        ),
        showlegend=False
    )

    st.plotly_chart(fig)

# -----------------------
# GLOBAL DATA
# -----------------------
st.subheader("📊 Données brutes")
st.dataframe(df)
