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
    "admin": {
        "password": "Kakashisensei90",
        "role": "admin"
    },
    "Membre": {
        "password": "SubaeleagueAR",
        "role": "viewer"
    }
}

if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.role = None

user = st.sidebar.text_input("User")

pwd = st.sidebar.text_input(
    "Password",
    type="password"
)

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
conn = sqlite3.connect(
    "subae.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS resultats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    semaine INTEGER,
    kuyok TEXT,
    field INTEGER DEFAULT 0,
    fruit INTEGER DEFAULT 0,
    autres INTEGER DEFAULT 0,
    presence INTEGER DEFAULT 0,
    taggui INTEGER DEFAULT 0,
    bb_ind INTEGER DEFAULT 0,
    bb_group INTEGER DEFAULT 0,
    ct INTEGER DEFAULT 0,
    ot INTEGER DEFAULT 0
)
""")

conn.commit()

# =========================================================
# LOAD DATA
# =========================================================
df = pd.read_sql_query(
    "SELECT * FROM resultats",
    conn
)

# =========================================================
# KYK LIST
# =========================================================
all_kyk = [f"KYK{i}" for i in range(1, 19)]

# =========================================================
# CLEAN DATA
# =========================================================
numeric_cols = [
    "field",
    "fruit",
    "autres",
    "presence",
    "taggui",
    "bb_ind",
    "bb_group",
    "ct",
    "ot"
]

if not df.empty:

    for c in numeric_cols:

        if c not in df.columns:
            df[c] = 0

        df[c] = pd.to_numeric(
            df[c],
            errors="coerce"
        ).fillna(0)

    # =====================================================
    # CALCUL POINTS
    # =====================================================
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
    "Menu",
    [
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
    ]
)

# =========================================================
# RANKING GLOBAL
# =========================================================
base = pd.DataFrame({
    "kuyok": all_kyk
})

ranking = (
    df.groupby("kuyok")["points"]
    .sum()
    .reset_index()
)

ranking = base.merge(
    ranking,
    on="kuyok",
    how="left"
).fillna(0)

ranking = ranking.sort_values(
    by="points",
    ascending=False
)

# =========================================================
# 📊 DASHBOARD
# =========================================================
if page == "📊 Dashboard":

    st.header("📊 Vue globale")

    st.bar_chart(
        ranking.set_index("kuyok")
    )

    st.dataframe(
        ranking,
        use_container_width=True
    )

# =========================================================
# 🧠 KYK ANALYZER
# =========================================================
elif page == "🧠 KYK Analyzer":

    k = st.selectbox(
        "KYK",
        all_kyk
    )

    sub = df[df["kuyok"] == k]

    st.subheader(k)

    if sub.empty:

        st.info("Aucune donnée")

    else:

        total_points = sub["points"].sum()

        st.metric(
            "Total Points",
            int(total_points)
        )

        st.write("### Activités cumulées")

        st.write(
            sub[numeric_cols].sum()
        )

        st.write("### Historique")

        st.dataframe(
            sub,
            use_container_width=True
        )

# =========================================================
# 🚨 ALERTES
# =========================================================
elif page == "🚨 Alertes":

    st.subheader("Alertes intelligentes")

    alerts = []

    for k in all_kyk:

        sub = df[df["kuyok"] == k]

        if sub.empty:

            alerts.append((
                k,
                "😴 Aucun activité"
            ))

        elif sub["taggui"].sum() < 3:

            alerts.append((
                k,
                "⚠️ Faible consolidation"
            ))

        elif (
            sub["field"].sum() > 20 and
            sub["taggui"].sum() < 5
        ):

            alerts.append((
                k,
                "⚠️ Inefficacité field"
            ))

        else:

            alerts.append((
                k,
                "🟢 OK"
            ))

    st.table(
        pd.DataFrame(
            alerts,
            columns=["KYK", "Status"]
        )
    )

# =========================================================
# 🩺 SANTÉ KYK
# =========================================================
elif page == "🩺 Santé KYK":

    st.subheader("Santé des KYK")

    health = []

    for k in all_kyk:

        sub = df[df["kuyok"] == k]

        total = sub["points"].sum()

        if sub.empty:

            state = "🔴 Inactif"

        elif total >= 500:

            state = "🟢 Excellent"

        elif total >= 200:

            state = "🟠 Moyen"

        else:

            state = "🔴 Faible"

        health.append((
            k,
            state,
            int(total)
        ))

    st.table(
        pd.DataFrame(
            health,
            columns=[
                "KYK",
                "Etat",
                "Points"
            ]
        )
    )

# =========================================================
# 📈 FUNNEL
# =========================================================
elif page == "📈 Funnel":

    st.subheader("Pipeline évangélisation")

    funnel = {
        "Field": int(df["field"].sum()),
        "Fruit Mannam": int(df["fruit"].sum()),
        "Autres Fruits": int(df["autres"].sum()),
        "Présence": int(df["presence"].sum()),
        "Taggui": int(df["taggui"].sum()),
        "BB Individuel": int(df["bb_ind"].sum()),
        "BB Groupe": int(df["bb_group"].sum()),
        "CT": int(df["ct"].sum()),
        "OT": int(df["ot"].sum())
    }

    funnel_df = pd.DataFrame(
        funnel.items(),
        columns=["Étape", "Total"]
    )

    st.dataframe(
        funnel_df,
        use_container_width=True
    )

    st.bar_chart(
        funnel_df.set_index("Étape")
    )

# =========================================================
# 🎯 OBJECTIFS
# =========================================================
elif page == "🎯 Objectifs":

    st.subheader("Objectifs KYK")

    st.info(
        "Module KPI évolutif à développer"
    )

# =========================================================
# 📅 HISTORIQUE
# =========================================================
elif page == "📅 Historique":

    st.subheader(
        "Historique des performances"
    )

    history = (
        df.groupby("semaine")["points"]
        .sum()
    )

    st.line_chart(history)

# =========================================================
# ⚔️ COMPARAISON
# =========================================================
elif page == "⚔️ Comparaison":

    a = st.selectbox(
        "KYK A",
        all_kyk
    )

    b = st.selectbox(
        "KYK B",
        all_kyk
    )

    compare = ranking[
        ranking["kuyok"].isin([a, b])
    ]

    st.dataframe(
        compare,
        use_container_width=True
    )

# =========================================================
# 📂 DONNÉES
# =========================================================
elif page == "📂 Données":

    st.subheader("Base de données")

    st.dataframe(
        df,
        use_container_width=True
    )

# =========================================================
# ⚙️ ADMIN
# =========================================================
elif page == "⚙️ Admin":

    if not is_admin:

        st.error("Accès refusé")

    else:

        st.subheader("Ajout données KYK")

        with st.form("add"):

            # =============================================
            # INFOS
            # =============================================
            date = st.date_input("Date")

            semaine = st.number_input(
                "Semaine",
                min_value=1,
                step=1
            )

            k = st.selectbox(
                "KYK",
                all_kyk
            )

            st.markdown("## Activités")

            # =============================================
            # INPUTS QUANTITÉS
            # =============================================
            field = st.number_input(
                "Passages sur le Field",
                min_value=0,
                step=1
            )

            fruit = st.number_input(
                "Fruit Mannam",
                min_value=0,
                step=1
            )

            autres = st.number_input(
                "Autres Fruits (NTF, EM...)",
                min_value=0,
                step=1
            )

            presence = st.number_input(
                "Mannam Présence",
                min_value=0,
                step=1
            )

            taggui = st.number_input(
                "Mannam Taggui",
                min_value=0,
                step=1
            )

            bb_ind = st.number_input(
                "BB Individuel",
                min_value=0,
                step=1
            )

            bb_group = st.number_input(
                "BB Groupe",
                min_value=0,
                step=1
            )

            ct = st.number_input(
                "CT",
                min_value=0,
                step=1
            )

            ot = st.number_input(
                "Participation OT",
                min_value=0,
                step=1
            )

            # =============================================
            # CALCUL DES POINTS
            # =============================================
            points = (
                field * 1 +
                fruit * 5 +
                autres * 2 +
                presence * 10 +
                taggui * 20 +
                bb_ind * 50 +
                bb_group * 100 +
                ct * 200 +
                ot * 500
            )

            st.markdown("## 🏆 Calcul automatique")

            st.write(
                f"Field : {field} × 1 = {field * 1}"
            )

            st.write(
                f"Fruit Mannam : {fruit} × 5 = {fruit * 5}"
            )

            st.write(
                f"Autres Fruits : {autres} × 2 = {autres * 2}"
            )

            st.write(
                f"Présence : {presence} × 10 = {presence * 10}"
            )

            st.write(
                f"Taggui : {taggui} × 20 = {taggui * 20}"
            )

            st.write(
                f"BB Individuel : {bb_ind} × 50 = {bb_ind * 50}"
            )

            st.write(
                f"BB Groupe : {bb_group} × 100 = {bb_group * 100}"
            )

            st.write(
                f"CT : {ct} × 200 = {ct * 200}"
            )

            st.write(
                f"OT : {ot} × 500 = {ot * 500}"
            )

            st.success(
                f"🏆 TOTAL POINTS = {points}"
            )

            submit = st.form_submit_button(
                "Ajouter"
            )

        # =================================================
        # INSERT DB
        # =================================================
        if submit:

            cursor.execute("""
            INSERT INTO resultats (
                date,
                semaine,
                kuyok,
                field,
                fruit,
                autres,
                presence,
                taggui,
                bb_ind,
                bb_group,
                ct,
                ot
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                str(date),
                int(semaine),
                k,
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

            st.success(
                f"✅ Données ajoutées pour {k} | Points : {points}"
            )

            st.rerun()
