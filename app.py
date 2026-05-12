import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

st.set_page_config(page_title="Subae League AR")

st.title("🏆 Subae League AR - Pro Dashboard")

# -----------------------
# USERS (LOGIN SYSTEM)
# -----------------------
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "viewer": {"password": "viewer123", "role": "viewer"}
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
        st.success(f"Connecté en tant que {username} ({st.session_state.role})")
    else:
        st.error("Login incorrect")

if not st.session_state.auth:
    st.stop()

is_admin = st.session_state.role == "admin"

# -----------------------
# DATA
# -----------------------
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

# -----------------------
# ADD RESULT (ADMIN ONLY)
# -----------------------
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

# -----------------------
# CALCUL POINTS
# -----------------------
def calc(row):
    return sum(float(row.get(k, 0)) * v for k, v in weights.items())

if not df.empty:
    for c in weights.keys():
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
# GLOBAL GRAPH
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
# RADAR (FIFA STYLE)
# -----------------------
st.subheader("🎮 Radar KYK")

kyk = st.selectbox("Choisir KYK", all_kyk)

sub = df[df["kuyok"] == kyk]

stats = {c: 0 for c in weights}

if not sub.empty:
    stats = {c: sub[c].sum() for c in weights}

categories = ["Field","Mannam","Taggui","BB","CT","OT"]
values = [
    stats["Passage sur le field"],
    stats["Mannam présence"],
    stats["Mannam Taggui"],
    stats["BB groupe"] + stats["BB individuel"],
    stats["CT"],
    stats["Participation OT"]
]

maxv = max(values) if max(values) > 0 else 1
values = [v/maxv*100 for v in values]

fig = go.Figure()
fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself'))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])))

st.plotly_chart(fig)

# -----------------------
# PORTRAIT KYK + CONVERSIONS
# -----------------------
st.subheader("🧠 Portrait KYK")

for k in all_kyk:
    sub = df[df["kuyok"] == k]

    st.markdown(f"### {k}")

    stats = {c: 0 for c in weights}
    if not sub.empty:
        stats = {c: sub[c].sum() for c in weights}

    total = ranking[ranking["kuyok"] == k]["points"].values[0] if k in ranking["kuyok"].values else 0

    ot_rate = (stats["Participation OT"] / stats["Fruit Mannam fixé"] * 100) if stats["Fruit Mannam fixé"] > 0 else 0

    field_to_presence = (stats["Mannam présence"] / stats["Passage sur le field"] * 100) if stats["Passage sur le field"] > 0 else 0
    presence_to_tag = (stats["Mannam Taggui"] / stats["Mannam présence"] * 100) if stats["Mannam présence"] > 0 else 0
    tag_to_bb = (stats["BB individuel"] / stats["Mannam Taggui"] * 100) if stats["Mannam Taggui"] > 0 else 0
    bb_to_ct = (stats["CT"] / stats["BB groupe"] * 100) if stats["BB groupe"] > 0 else 0
    ct_to_ot = (stats["Participation OT"] / stats["CT"] * 100) if stats["CT"] > 0 else 0

    st.write(f"Total points : {total:.0f}")
    st.write(f"Type analyse basé sur performance")

    st.write("🔄 Conversions")
    st.write(f"Field → Presence : {field_to_presence:.1f}%")
    st.write(f"Presence → Taggui : {presence_to_tag:.1f}%")
    st.write(f"Taggui → BB : {tag_to_bb:.1f}%")
    st.write(f"BB → CT : {bb_to_ct:.1f}%")
    st.write(f"CT → OT : {ct_to_ot:.1f}%")
    st.write(f"Mannam → OT : {ot_rate:.1f}%")

    st.bar_chart(pd.DataFrame.from_dict(stats, orient="index"))

# -----------------------
# DATA
# -----------------------
st.subheader("📊 Données brutes")
st.dataframe(df)

# -----------------------
# EDIT (ADMIN ONLY)
# -----------------------
if is_admin:
    st.subheader("✏️ Modifier une ligne")

    if not df.empty:
        i = st.number_input("Index", 0, len(df)-1, 0)
        row = df.iloc[i]

        with st.form("edit"):
            for c in weights:
                df.at[i, c] = st.number_input(c, value=float(row[c]))

            save = st.form_submit_button("Sauvegarder")

        if save:
            df.to_csv(FILE, index=False)
            st.success("Modifié ✔️")
