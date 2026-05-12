import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Subae League AR", layout="wide")

st.title("🏆 Subae League AR - Pro Dashboard (SQLite)")

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

st.sidebar.subheader("🔐 Connexion")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if username in USERS and USERS[username]["password"] == password:
        st.session_state.auth = True
        st.session_state.role = USERS[username]["role"]
        st.success(f"Connecté en tant que {username}")
    else:
        st.error("Identifiants incorrects")

if not st.session_state.auth:
    st.stop()

is_admin = st.session_state.role == "admin"

# =========================================================
# SQLITE CONNECTION
# =========================================================
def get_conn():
    return sqlite3.connect("subae.db", check_same_thread=False)

conn = get_conn()
cursor = conn.cursor()

# =========================================================
# CREATE TABLE AUTO
# =========================================================
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

# =========================================================
# SETTINGS
# =========================================================
all_kyk = [f"KYK{i}" for i in range(1, 19)]

weights = {
    "field": 1,
    "fruit": 5,
    "autres": 2,
    "presence": 10,
    "taggui": 20,
    "bb_ind": 50,
    "bb_group": 100,
    "ct": 200,
    "ot": 500
}

# =========================================================
# LOAD DATA
# =========================================================
df = pd.read_sql_query("SELECT * FROM resultats", conn)

# =========================================================
# CALCUL POINTS
# =========================================================
if not df.empty:
    for c in weights:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["points"] = sum(df[c] * w for c, w in weights.items())
else:
    df["points"] = 0

# =========================================================
# PRIORITY SCORE
# =========================================================
def priority_score(group):
    return (
        group["taggui"].sum() * 1000000 +
        group["presence"].sum() * 10000 +
        group["fruit"].sum() * 100 +
        group["field"].sum()
    )

# =========================================================
# RANKING
# =========================================================
base = pd.DataFrame({"kuyok": all_kyk})

ranking = df.groupby("kuyok")["points"].sum().reset_index()

ranking = base.merge(ranking, on="kuyok", how="left").fillna(0)
ranking = ranking.sort_values("points", ascending=False)

# =========================================================
# NAVIGATION
# =========================================================
page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "🧠 Analyse KYK", "⚔️ Comparaison", "📂 Données", "⚙️ Admin"]
)

# =========================================================
# DASHBOARD
# =========================================================
if page == "📊 Dashboard":

    st.header("📊 Dashboard Global")

    c1, c2, c3 = st.columns(3)

    c1.metric("🏆 Top KYK", ranking.iloc[0]["kuyok"] if not df.empty else "-")
    c2.metric("📈 Total points", int(ranking["points"].sum()))
    c3.metric("👥 KYK actifs", len(df["kuyok"].unique()))

    with st.expander("🏆 Classement"):
        st.dataframe(ranking, use_container_width=True)

    with st.expander("📊 Graph"):
        st.bar_chart(ranking.set_index("kuyok")["points"])

    with st.expander("📈 Evolution"):
        if not df.empty:
            evo = df.groupby(["semaine", "kuyok"])["points"].sum().reset_index()
            pivot = evo.pivot(index="semaine", columns="kuyok", values="points").fillna(0)
            st.line_chart(pivot)

    # =====================================================
    # DISTINCTIONS
    # =====================================================
    with st.expander("🏅 Distinctions"):

        if not df.empty:

            week = int(df["semaine"].max())

            week_df = df[df["semaine"] == week]

            week_scores = week_df.groupby("kuyok").apply(priority_score).reset_index(name="score")

            best_week = week_scores.sort_values("score", ascending=False).iloc[0]["kuyok"]
            worst_week = week_scores.sort_values("score", ascending=True).iloc[0]["kuyok"]

            month_df = df[df["date"].str[:7] == df["date"].max()[:7]]

            month_scores = month_df.groupby("kuyok").apply(priority_score).reset_index(name="score")

            best_month = month_scores.sort_values("score", ascending=False).iloc[0]["kuyok"]
            worst_month = month_scores.sort_values("score", ascending=True).iloc[0]["kuyok"]

            st.success(f"🥇 Semaine : {best_week}")
            st.success(f"🏆 Mois : {best_month}")

            st.error(f"📉 Semaine : {worst_week}")
            st.error(f"⚠️ Mois : {worst_month}")

# =========================================================
# ANALYSE KYK
# =========================================================
elif page == "🧠 Analyse KYK":

    kyk = st.selectbox("Choisir KYK", all_kyk)

    sub = df[df["kuyok"] == kyk]

    stats = {c: sub[c].sum() for c in weights} if not sub.empty else {c: 0 for c in weights}

    st.subheader(f"🧠 Analyse {kyk}")

    st.metric("Points", int(sub["points"].sum()) if not sub.empty else 0)

    st.write(stats)

# =========================================================
# COMPARAISON
# =========================================================
elif page == "⚔️ Comparaison":

    k1 = st.selectbox("KYK 1", all_kyk)
    k2 = st.selectbox("KYK 2", all_kyk, index=1)

    s1 = df[df["kuyok"] == k1]
    s2 = df[df["kuyok"] == k2]

    st.subheader("Comparaison")

    col1, col2 = st.columns(2)

    with col1:
        st.write(k1)
        st.write(s1.sum(numeric_only=True))

    with col2:
        st.write(k2)
        st.write(s2.sum(numeric_only=True))

# =========================================================
# DONNÉES
# =========================================================
elif page == "📂 Données":

    st.dataframe(df, use_container_width=True)

# =========================================================
# ADMIN
# =========================================================
elif page == "⚙️ Admin":

    if not is_admin:
        st.error("Accès refusé")
    else:

        st.subheader("➕ Ajouter un résultat")

        with st.form("add"):

            date = st.date_input("Date")
            semaine = st.number_input("Semaine")
            kuyok = st.selectbox("KYK", all_kyk)

            field = st.number_input("Field")
            fruit = st.number_input("Fruit")
            autres = st.number_input("Autres")
            presence = st.number_input("Présence")
            taggui = st.number_input("Taggui")
            bb_ind = st.number_input("BB ind")
            bb_group = st.number_input("BB group")
            ct = st.number_input("CT")
            ot = st.number_input("OT")

            submit = st.form_submit_button("Ajouter")

        if submit:

            cursor.execute("""
            INSERT INTO resultats (
                date, semaine, kuyok,
                field, fruit, autres,
                presence, taggui,
                bb_ind, bb_group,
                ct, ot
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(date), semaine, kuyok,
                field, fruit, autres,
                presence, taggui,
                bb_ind, bb_group,
                ct, ot
            ))

            conn.commit()

            st.success("Ajouté ✔️")
