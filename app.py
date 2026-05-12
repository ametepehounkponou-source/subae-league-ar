import streamlit as st
import pandas as pd
import sqlite3

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Subae League AR", layout="wide")
st.title("🏆 Subae League AR - KYK Intelligence System")

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
        st.success("Connexion réussie")
    else:
        st.error("Identifiants incorrects")

if not st.session_state.auth:
    st.stop()

is_admin = st.session_state.role == "admin"

# =========================================================
# SQLITE
# =========================================================
def get_conn():
    return sqlite3.connect("subae.db", check_same_thread=False)

conn = get_conn()
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

# =========================================================
# LOAD DATA
# =========================================================
df = pd.read_sql_query("SELECT * FROM resultats", conn)

# =========================================================
# KYK LIST (TOUJOURS COMPLET)
# =========================================================
all_kyk = [f"KYK{i}" for i in range(1, 19)]

# =========================================================
# SAFE INIT
# =========================================================
if df.empty:
    df = pd.DataFrame(columns=[
        "id","date","semaine","kuyok",
        "field","fruit","autres","presence",
        "taggui","bb_ind","bb_group","ct","ot","points"
    ])

# =========================================================
# CLEAN + POINTS CALCULATION
# =========================================================
if not df.empty:

    for col in ["field","fruit","autres","presence","taggui","bb_ind","bb_group","ct","ot"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["points"] = (
        df["field"] * 1 +
        df["fruit"] * 5 +
        df["autres"] * 2 +
        df["presence"] * 10 +
        df["taggui"] * 20 +
        df["bb_ind"] * 50 +
        df["bb_group"] * 100 +
        df["ct"] * 200 +
        df["ot"] * 500
    )
else:
    df["points"] = 0

# =========================================================
# NAVIGATION
# =========================================================
page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "🧠 Analyse KYK", "⚔️ Comparaison", "📂 Données", "⚙️ Admin"]
)

# =========================================================
# 📊 DASHBOARD
# =========================================================
if page == "📊 Dashboard":

    st.header("📊 Dashboard Global")

    if df.empty:
        st.warning("Aucune donnée enregistrée.")
    else:

        # 🔥 FORCER TOUS LES KYK
        base = pd.DataFrame({"kuyok": all_kyk})

        ranking = df.groupby("kuyok")["points"].sum().reset_index()

        ranking = base.merge(ranking, on="kuyok", how="left").fillna(0)

        ranking = ranking.sort_values("points", ascending=False)

        c1, c2, c3 = st.columns(3)

        c1.metric("🏆 Top KYK", ranking.iloc[0]["kuyok"])
        c2.metric("📈 Total points", int(ranking["points"].sum()))
        c3.metric("👥 KYK actifs", df["kuyok"].nunique())

        st.subheader("🏆 Classement complet")
        st.dataframe(ranking, use_container_width=True)

        st.subheader("📊 Performance")
        st.bar_chart(ranking.set_index("kuyok"))

# =========================================================
# 🧠 ANALYSE KYK
# =========================================================
elif page == "🧠 Analyse KYK":

    kyk = st.selectbox("Choisir KYK", all_kyk)

    sub = df[df["kuyok"] == kyk].copy()

    st.subheader(f"🧠 Analyse {kyk}")

    if sub.empty:
        st.info("Aucune donnée pour ce KYK")
    else:
        st.metric("Points", int(sub["points"].sum()))
        st.write(sub.sum(numeric_only=True))

# =========================================================
# ⚔️ COMPARAISON
# =========================================================
elif page == "⚔️ Comparaison":

    k1 = st.selectbox("KYK 1", all_kyk)
    k2 = st.selectbox("KYK 2", all_kyk, index=1)

    s1 = df[df["kuyok"] == k1].sum(numeric_only=True)
    s2 = df[df["kuyok"] == k2].sum(numeric_only=True)

    st.subheader("⚔️ Comparaison")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"### {k1}")
        st.write(s1)

    with col2:
        st.write(f"### {k2}")
        st.write(s2)

# =========================================================
# 📂 DONNÉES
# =========================================================
elif page == "📂 Données":

    st.subheader("📂 Données brutes")
    st.dataframe(df, use_container_width=True)

# =========================================================
# ⚙️ ADMIN
# =========================================================
elif page == "⚙️ Admin":

    if not is_admin:
        st.error("Accès refusé")
    else:

        st.subheader("➕ Ajouter un résultat")

        with st.form("add"):

            date = st.date_input("Date")

            semaine = st.number_input("Semaine", step=1, format="%d")

            kuyok = st.selectbox("KYK", all_kyk)

            field = st.number_input("Field", step=1, format="%d")
            fruit = st.number_input("Fruit", step=1, format="%d")
            autres = st.number_input("Autres", step=1, format="%d")
            presence = st.number_input("Présence", step=1, format="%d")
            taggui = st.number_input("Taggui", step=1, format="%d")
            bb_ind = st.number_input("BB individuel", step=1, format="%d")
            bb_group = st.number_input("BB groupe", step=1, format="%d")
            ct = st.number_input("CT", step=1, format="%d")
            ot = st.number_input("OT", step=1, format="%d")

            submit = st.form_submit_button("Ajouter")

        if submit:

            cursor.execute("""
            INSERT INTO resultats (
                date, semaine, kuyok,
                field, fruit, autres,
                presence, taggui,
                bb_ind, bb_group,
                ct, ot
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(date),
                int(semaine),
                kuyok,
                int(field),
                int(fruit),
                int(autres),
                int(presence),
                int(taggui),
                int(bb_ind),
                int(bb_group),
                int(ct),
                int(ot)
            ))

            conn.commit()

            st.success("Ajouté ✔️")
