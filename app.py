import streamlit as st
import pandas as pd
import sqlite3

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="KYK Intelligence System", layout="wide")
st.title("🏆 KYK Intelligence System")

# =========================================================
# LOGIN
# =========================================================
USERS = {
    "admin": {"password": "Kakashisensei90", "role": "admin"},
    "Membre": {"password": "SubaeleagueAR", "role": "viewer"}
}

if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.role = None

user = st.sidebar.text_input("User")
pwd = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if user in USERS and USERS[user]["password"] == pwd:
        st.session_state.auth = True
        st.session_state.role = USERS[user]["role"]
    else:
        st.error("Erreur login")

if not st.session_state.auth:
    st.stop()

is_admin = st.session_state.role == "admin"

# =========================================================
# DB
# =========================================================
conn = sqlite3.connect("subae.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS resultats (
id INTEGER PRIMARY KEY AUTOINCREMENT,
date TEXT,
semaine INTEGER,
kuyok TEXT,
field INTEGER,
fruit INTEGER,
autres INTEGER,
presence INTEGER,
taggui INTEGER,
bb_ind INTEGER,
bb_group INTEGER,
ct INTEGER,
ot INTEGER
)
""")

conn.commit()

df = pd.read_sql_query("SELECT * FROM resultats", conn)

# =========================================================
# KYK LIST
# =========================================================
all_kyk = [f"KYK{i}" for i in range(1, 19)]

# =========================================================
# CLEAN + POINTS
# =========================================================
if not df.empty:
    for c in ["field","fruit","autres","presence","taggui","bb_ind","bb_group","ct","ot"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["points"] = (
        df["field"] * 1 +
        df["fruit"] * 5 +
        df["presence"] * 10 +
        df["taggui"] * 20 +
        df["bb_group"] * 100 +
        df["ct"] * 200 +
        df["ot"] * 500
    )
else:
    df["points"] = 0

# =========================================================
# NAVIGATION
# =========================================================
page = st.sidebar.radio("Menu", [
    "📊 Dashboard",
    "🧠 KYK Analyzer",
    "🚨 Alertes",
    "🩺 Santé KYK",
    "📈 Funnel",
    "🎯 Objectifs",
    "📅 Historique",
    "⚔️ Comparaison",
    "📂 Données",
    "⚙️ Admin"
])

# =========================================================
# BASE RANKING (GLOBAL)
# =========================================================
base = pd.DataFrame({"kuyok": all_kyk})

ranking = df.groupby("kuyok")["points"].sum().reset_index()
ranking = base.merge(ranking, on="kuyok", how="left").fillna(0)

# =========================================================
# 📊 DASHBOARD
# =========================================================
if page == "📊 Dashboard":

    st.header("📊 Vue globale")

    st.bar_chart(ranking.set_index("kuyok"))

    st.dataframe(ranking)

# =========================================================
# 🧠 KYK ANALYZER
# =========================================================
elif page == "🧠 KYK Analyzer":

    k = st.selectbox("KYK", all_kyk)
    sub = df[df["kuyok"] == k]

    st.subheader(k)

    if sub.empty:
        st.info("Aucune donnée")
    else:
        st.write(sub.sum(numeric_only=True))

# =========================================================
# 🚨 ALERTES
# =========================================================
elif page == "🚨 Alertes":

    st.subheader("Alertes intelligentes")

    alerts = []

    for k in all_kyk:
        sub = df[df["kuyok"] == k]

        if sub.empty:
            alerts.append((k, "😴 Aucun activité"))
        elif sub["taggui"].sum() < 3:
            alerts.append((k, "⚠️ faible consolidation"))
        elif sub["field"].sum() > 20 and sub["taggui"].sum() < 5:
            alerts.append((k, "⚠️ inefficacité field"))
        else:
            alerts.append((k, "🟢 OK"))

    st.table(pd.DataFrame(alerts, columns=["KYK","Status"]))

# =========================================================
# 🩺 SANTÉ KYK
# =========================================================
elif page == "🩺 Santé KYK":

    st.subheader("Santé des KYK")

    health = []

    for k in all_kyk:
        sub = df[df["kuyok"] == k]

        if sub.empty:
            state = "🔴 Inactif"
        elif sub["points"].sum() > 500:
            state = "🟢 Excellent"
        elif sub["points"].sum() > 200:
            state = "🟠 Moyen"
        else:
            state = "🔴 Faible"

        health.append((k, state))

    st.table(pd.DataFrame(health, columns=["KYK","Etat"]))

# =========================================================
# 📈 FUNNEL
# =========================================================
elif page == "📈 Funnel":

    st.subheader("Pipeline évangélisation")

    st.write("""
    Field ↓
    Fruit ↓
    Présence ↓
    Taggui ↓
    BB ↓
    CT ↓
    OT
    """)

# =========================================================
# 🎯 OBJECTIFS
# =========================================================
elif page == "🎯 Objectifs":

    st.subheader("Objectifs KYK")

    st.write("À développer KPI par KPI")

# =========================================================
# 📅 HISTORIQUE
# =========================================================
elif page == "📅 Historique":

    st.subheader("Évolution")

    st.line_chart(ranking.set_index("kuyok"))

# =========================================================
# ⚔️ COMPARAISON
# =========================================================
elif page == "⚔️ Comparaison":

    a = st.selectbox("KYK A", all_kyk)
    b = st.selectbox("KYK B", all_kyk)

    st.write(ranking[ranking["kuyok"].isin([a,b])])

# =========================================================
# 📂 DONNÉES
# =========================================================
elif page == "📂 Données":

    st.dataframe(df)

# =========================================================
# ⚙️ ADMIN
# =========================================================
elif page == "⚙️ Admin":

    if not is_admin:
        st.error("Accès refusé")

    else:

        st.subheader("Ajout données")

        with st.form("add"):

            date = st.date_input("Date")
            semaine = st.number_input("Semaine", step=1)
            k = st.selectbox("KYK", all_kyk)

            field = st.number_input("Field", step=1)
            fruit = st.number_input("Fruit", step=1)
            presence = st.number_input("Presence", step=1)
            taggui = st.number_input("Taggui", step=1)

            submit = st.form_submit_button("Ajouter")

        if submit:
            cursor.execute("""
            INSERT INTO resultats (date,semaine,kuyok,field,fruit,presence,taggui,bb_ind,bb_group,ct,ot)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (str(date),semaine,k,field,fruit,presence,taggui,0,0,0,0))

            conn.commit()

            st.success("Ajouté")
