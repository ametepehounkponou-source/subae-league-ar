import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Subae League AR",
    layout="wide"
)

st.title("🏆 Subae League AR - Pro Dashboard")

# =========================================================
# LOGIN SYSTEM
# =========================================================
USERS = {
    "admin": {"password": "Kakashisensei90", "role": "admin"},
    "Membre": {"password": "SubaeleagueAR", "role": "viewer"}
}

if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.role = None

st.sidebar.subheader("🔐 Login")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if username in USERS and USERS[username]["password"] == password:
        st.session_state.auth = True
        st.session_state.role = USERS[username]["role"]
        st.success(f"Connecté en tant que {username}")
    else:
        st.error("Login incorrect")

if not st.session_state.auth:
    st.stop()

is_admin = st.session_state.role == "admin"

# =========================================================
# DATA
# =========================================================
FILE = "resultats.csv"

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

# =========================================================
# ADD RESULT
# =========================================================
if is_admin:

    st.subheader("➕ Ajouter un résultat")

    with st.form("add"):

        date = st.date_input("Date")
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
            "date": str(date),
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

# =========================================================
# CLEAN DATA
# =========================================================
if not df.empty:

    df["date"] = pd.to_datetime(df["date"])

    for c in weights.keys():
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

# =========================================================
# CALCUL POINTS
# =========================================================
def calc(row):
    return sum(float(row.get(k, 0)) * v for k, v in weights.items())

if not df.empty:
    df["points"] = df.apply(calc, axis=1)
else:
    df["points"] = 0

# =========================================================
# RANKING
# =========================================================
base = pd.DataFrame({"kuyok": all_kyk})

ranking = df.groupby("kuyok")["points"].sum().reset_index()

ranking = (
    base.merge(ranking, on="kuyok", how="left")
    .fillna(0)
    .sort_values("points", ascending=False)
)

# =========================================================
# GLOBAL KPI
# =========================================================
st.subheader("📊 Vue globale")

c1, c2, c3, c4 = st.columns(4)

top_kyk = ranking.iloc[0]["kuyok"]
top_points = ranking.iloc[0]["points"]

total_points = ranking["points"].sum()

active_kyk = len(df["kuyok"].unique()) if not df.empty else 0

last_week = int(df["semaine"].max()) if not df.empty else 0

c1.metric("🏆 Top KYK", top_kyk)
c2.metric("🔥 Points Top", f"{top_points:.0f}")
c3.metric("📈 Total Points", f"{total_points:.0f}")
c4.metric("📅 Dernière semaine", last_week)

# =========================================================
# CLASSEMENT
# =========================================================
st.subheader("🏆 Classement général")

st.dataframe(
    ranking,
    use_container_width=True,
    hide_index=True
)

# =========================================================
# DISTINCTIONS
# =========================================================
st.subheader("🏅 Distinctions")

def priority_score(group):

    return (
        group["Mannam Taggui"].sum() * 1000000 +
        group["Mannam présence"].sum() * 10000 +
        group["Fruit Mannam fixé"].sum() * 100 +
        group["Passage sur le field"].sum()
    )

if not df.empty:

    # WEEK
    week_df = df[df["semaine"] == last_week]

    week_scores = (
        week_df.groupby("kuyok")
        .apply(priority_score)
        .reset_index(name="score")
        .sort_values("score", ascending=False)
    )

    best_week = week_scores.iloc[0]["kuyok"]
    worst_week = week_scores.iloc[-1]["kuyok"]

    # MONTH
    current_month = df["date"].dt.month.max()
    current_year = df["date"].dt.year.max()

    month_df = df[
        (df["date"].dt.month == current_month)
        & (df["date"].dt.year == current_year)
    ]

    month_scores = (
        month_df.groupby("kuyok")
        .apply(priority_score)
        .reset_index(name="score")
        .sort_values("score", ascending=False)
    )

    best_month = month_scores.iloc[0]["kuyok"]
    worst_month = month_scores.iloc[-1]["kuyok"]

    a1, a2, a3, a4 = st.columns(4)

    a1.success(f"🥇 Semaine : {best_week}")
    a2.error(f"📉 Semaine : {worst_week}")

    a3.success(f"🏆 Mois : {best_month}")
    a4.error(f"⚠️ Mois : {worst_month}")

# =========================================================
# GLOBAL GRAPH
# =========================================================
st.subheader("📊 Forces globales")

st.bar_chart(ranking.set_index("kuyok")["points"])

# =========================================================
# EVOLUTION
# =========================================================
st.subheader("📈 Evolution générale")

if not df.empty:

    evo = (
        df.groupby(["semaine", "kuyok"])["points"]
        .sum()
        .reset_index()
    )

    pivot = (
        evo.pivot(index="semaine", columns="kuyok", values="points")
        .fillna(0)
    )

    st.line_chart(pivot)

# =========================================================
# KYK ANALYSIS
# =========================================================
st.subheader("🧠 Analyse KYK")

selected_kyk = st.selectbox(
    "Choisir un KYK",
    all_kyk
)

sub = df[df["kuyok"] == selected_kyk]

# =========================================================
# KYK STATS
# =========================================================
stats = {c: 0 for c in weights}

if not sub.empty:
    stats = {c: sub[c].sum() for c in weights}

total = ranking[ranking["kuyok"] == selected_kyk]["points"].values[0]

# =========================================================
# KPI KYK
# =========================================================
k1, k2, k3, k4 = st.columns(4)

k1.metric("🏆 Points", f"{total:.0f}")
k2.metric("🔥 Taggui", int(stats["Mannam Taggui"]))
k3.metric("👥 Présence", int(stats["Mannam présence"]))
k4.metric("🎯 OT", int(stats["Participation OT"]))

# =========================================================
# CONVERSIONS
# =========================================================
st.subheader("🔄 Conversions")

field_to_presence = (
    stats["Mannam présence"] /
    stats["Passage sur le field"] * 100
    if stats["Passage sur le field"] > 0 else 0
)

presence_to_tag = (
    stats["Mannam Taggui"] /
    stats["Mannam présence"] * 100
    if stats["Mannam présence"] > 0 else 0
)

tag_to_bb = (
    stats["BB individuel"] /
    stats["Mannam Taggui"] * 100
    if stats["Mannam Taggui"] > 0 else 0
)

ct_to_ot = (
    stats["Participation OT"] /
    stats["CT"] * 100
    if stats["CT"] > 0 else 0
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Field → Présence", f"{field_to_presence:.1f}%")
c2.metric("Présence → Taggui", f"{presence_to_tag:.1f}%")
c3.metric("Taggui → BB", f"{tag_to_bb:.1f}%")
c4.metric("CT → OT", f"{ct_to_ot:.1f}%")

# =========================================================
# ALERTS
# =========================================================
st.subheader("🚨 Alertes & Points d'amélioration")

alerts = []

if field_to_presence < 20:
    alerts.append(
        "⚠️ Beaucoup de field mais faible transformation en présence."
    )

if presence_to_tag < 20:
    alerts.append(
        "⚠️ Les présences passent peu en Taggui."
    )

if stats["Participation OT"] == 0:
    alerts.append(
        "⚠️ Aucune participation OT enregistrée."
    )

if stats["Mannam Taggui"] == 0:
    alerts.append(
        "⚠️ Aucun Taggui enregistré."
    )

# REGRESSION
if not sub.empty:

    weeks = sorted(sub["semaine"].unique())

    if len(weeks) >= 2:

        current_week = weeks[-1]
        previous_week = weeks[-2]

        current_pts = (
            sub[sub["semaine"] == current_week]["points"]
            .sum()
        )

        previous_pts = (
            sub[sub["semaine"] == previous_week]["points"]
            .sum()
        )

        if previous_pts > 0:

            variation = (
                (current_pts - previous_pts)
                / previous_pts
            ) * 100

            if variation < -25:
                alerts.append(
                    f"🔻 Régression importante ({variation:.1f}%)."
                )

            elif variation > 25:
                alerts.append(
                    f"🔥 Forte progression ({variation:.1f}%)."
                )

if len(alerts) == 0:
    st.success("✅ Aucun signal négatif détecté.")
else:
    for a in alerts:
        st.warning(a)

# =========================================================
# SYNTHESIS IA
# =========================================================
st.subheader("🧠 Synthèse automatique")

synthesis = []

if stats["Passage sur le field"] > 20:
    synthesis.append(
        "Le KYK montre une bonne activité terrain."
    )

if field_to_presence < 20:
    synthesis.append(
        "Le principal point d'amélioration semble être la transformation du field en présence."
    )

if presence_to_tag > 40:
    synthesis.append(
        "Très bon travail de consolidation après les présences."
    )

if stats["Participation OT"] > 0:
    synthesis.append(
        "Le KYK participe activement aux OT."
    )

if stats["Mannam Taggui"] == 0:
    synthesis.append(
        "Aucun Mannam Taggui enregistré pour le moment."
    )

if len(synthesis) == 0:
    synthesis.append(
        "Le KYK reste stable mais manque encore de données significatives."
    )

st.info(" ".join(synthesis))

# =========================================================
# RADAR
# =========================================================
st.subheader("🎮 Radar")

categories = [
    "Field",
    "Présence",
    "Taggui",
    "BB",
    "CT",
    "OT"
]

values = [
    stats["Passage sur le field"],
    stats["Mannam présence"],
    stats["Mannam Taggui"],
    stats["BB groupe"] + stats["BB individuel"],
    stats["CT"],
    stats["Participation OT"]
]

maxv = max(values) if max(values) > 0 else 1

values = [v / maxv * 100 for v in values]

fig = go.Figure()

fig.add_trace(
    go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=selected_kyk
    )
)

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100]
        )
    ),
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

# =========================================================
# COMPARISON
# =========================================================
st.subheader("⚔️ Comparer deux KYK")

compare_kyk = st.selectbox(
    "Comparer avec",
    all_kyk,
    index=1
)

sub2 = df[df["kuyok"] == compare_kyk]

stats2 = {c: 0 for c in weights}

if not sub2.empty:
    stats2 = {c: sub2[c].sum() for c in weights}

compare_df = pd.DataFrame({
    selected_kyk: stats,
    compare_kyk: stats2
})

st.dataframe(compare_df)

# =========================================================
# COMPARISON RADAR
# =========================================================
values1 = [
    stats["Passage sur le field"],
    stats["Mannam présence"],
    stats["Mannam Taggui"],
    stats["BB groupe"] + stats["BB individuel"],
    stats["CT"],
    stats["Participation OT"]
]

values2 = [
    stats2["Passage sur le field"],
    stats2["Mannam présence"],
    stats2["Mannam Taggui"],
    stats2["BB groupe"] + stats2["BB individuel"],
    stats2["CT"],
    stats2["Participation OT"]
]

maxv = max(values1 + values2)

if maxv == 0:
    maxv = 1

values1 = [v / maxv * 100 for v in values1]
values2 = [v / maxv * 100 for v in values2]

fig2 = go.Figure()

fig2.add_trace(go.Scatterpolar(
    r=values1,
    theta=categories,
    fill='toself',
    name=selected_kyk
))

fig2.add_trace(go.Scatterpolar(
    r=values2,
    theta=categories,
    fill='toself',
    name=compare_kyk
))

fig2.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100]
        )
    )
)

st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# RAW DATA
# =========================================================
st.subheader("📊 Données brutes")

st.dataframe(
    df,
    use_container_width=True
)

# =========================================================
# EDIT
# =========================================================
if is_admin:

    st.subheader("✏️ Modifier une ligne")

    if not df.empty:

        i = st.number_input(
            "Index",
            0,
            len(df) - 1,
            0
        )

        row = df.iloc[i]

        with st.form("edit"):

            for c in weights:
                df.at[i, c] = st.number_input(
                    c,
                    value=float(row[c])
                )

            save = st.form_submit_button("Sauvegarder")

        if save:

            df.to_csv(FILE, index=False)

            st.success("Modifié ✔️")
