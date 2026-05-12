import streamlit as st
import pandas as pd
import sqlite3

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="KYK Intelligence System",
    layout="wide"
)

st.title("🏆 KYK Intelligence System")

# =========================================================
# LOGIN SYSTEM
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

user = st.sidebar.text_input("👤 User")

pwd = st.sidebar.text_input(
    "🔒 Password",
    type="password"
)

if st.sidebar.button("Login"):

    if user in USERS and USERS[user]["password"] == pwd:

        st.session_state.auth = True
        st.session_state.role = USERS[user]["role"]

        st.sidebar.success("✅ Connexion réussie")

    else:
        st.sidebar.error("❌ Erreur login")

if not st.session_state.auth:
    st.stop()

is_admin = st.session_state.role == "admin"

# =========================================================
# LOGOUT
# =========================================================
if st.sidebar.button("Logout"):

    st.session_state.auth = False
    st.session_state.role = None

    st.rerun()

# =========================================================
# DATABASE
# =========================================================
conn = sqlite3.connect(
    "subae.db",
    check_same_thread=False
)

cursor = conn.cursor()

# =========================================================
# CREATE TABLE
# =========================================================
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
# NUMERIC COLUMNS
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

# =========================================================
# CLEAN + POINTS
# =========================================================
if not df.empty:

    for c in numeric_cols:

        if c not in df.columns:
            df[c] = 0

        df[c] = pd.to_numeric(
            df[c],
            errors="coerce"
        ).fillna(0)

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
# LABEL FOR EDIT / DELETE
# =========================================================
if not df.empty:

    df["label"] = (
        df["kuyok"]
        + " - "
        + df["date"].astype(str)
        + " (ID "
        + df["id"].astype(str)
        + ")"
    )

# =========================================================
# SIDEBAR MENU
# =========================================================
page = st.sidebar.radio(
    "📂 Menu",
    [
        "📊 Dashboard",
        "🧠 KYK Analyzer",
        "🚨 Alertes",
        "🩺 Santé KYK",
        "📈 Funnel",
        "📅 Historique",
        "⚔️ Comparaison",
        "📂 Données",
        "⚙️ Admin"
    ]
)

# =========================================================
# GLOBAL RANKING
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
# DASHBOARD
# =========================================================
if page == "📊 Dashboard":

    st.header("📊 Classement Général")

    st.bar_chart(
        ranking.set_index("kuyok")
    )

    st.dataframe(
        ranking,
        use_container_width=True
    )

    st.success(
        f"🏆 Total global : {int(df['points'].sum())} points"
    )

# =========================================================
# ANALYZER
# =========================================================
elif page == "🧠 KYK Analyzer":

    k = st.selectbox(
        "Choisir KYK",
        all_kyk
    )

    sub = df[df["kuyok"] == k]

    st.subheader(f"🧠 Analyse de {k}")

    if sub.empty:

        st.warning("Aucune donnée disponible")

    else:

        st.metric(
            "🏆 Total Points",
            int(sub["points"].sum())
        )

        st.write("### Totaux activités")

        st.dataframe(
            sub[numeric_cols].sum().to_frame("Total"),
            use_container_width=True
        )

        st.write("### Historique")

        st.dataframe(
            sub,
            use_container_width=True
        )

# =========================================================
# ALERTS
# =========================================================
elif page == "🚨 Alertes":

    st.subheader("🚨 Alertes intelligentes")

    alerts = []

    for k in all_kyk:

        sub = df[df["kuyok"] == k]

        if sub.empty:

            alerts.append((k, "😴 Inactif"))

        elif sub["taggui"].sum() < 3:

            alerts.append((k, "⚠️ Faible consolidation"))

        elif (
            sub["field"].sum() > 20 and
            sub["taggui"].sum() < 5
        ):

            alerts.append((k, "⚠️ Inefficacité field"))

        else:

            alerts.append((k, "🟢 Stable"))

    st.table(
        pd.DataFrame(
            alerts,
            columns=["KYK", "Status"]
        )
    )

# =========================================================
# HEALTH
# =========================================================
elif page == "🩺 Santé KYK":

    st.subheader("🩺 Santé des KYK")

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
# FUNNEL
# =========================================================
elif page == "📈 Funnel":

    st.subheader("📈 Funnel Global")

    funnel = {
        "Field": int(df["field"].sum()),
        "Fruit": int(df["fruit"].sum()),
        "Autres": int(df["autres"].sum()),
        "Présence": int(df["presence"].sum()),
        "Taggui": int(df["taggui"].sum()),
        "BB Individuel": int(df["bb_ind"].sum()),
        "BB Groupe": int(df["bb_group"].sum()),
        "CT": int(df["ct"].sum()),
        "OT": int(df["ot"].sum())
    }

    funnel_df = pd.DataFrame(
        funnel.items(),
        columns=["Étape", "Valeur"]
    )

    st.dataframe(
        funnel_df,
        use_container_width=True
    )

    st.bar_chart(
        funnel_df.set_index("Étape")
    )

# =========================================================
# HISTORY
# =========================================================
elif page == "📅 Historique":

    st.subheader("📅 Historique")

    history = (
        df.groupby("semaine")["points"]
        .sum()
    )

    st.line_chart(history)

# =========================================================
# COMPARISON
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
# DATA
# =========================================================
elif page == "📂 Données":

    st.subheader("📂 Base de données")

    st.dataframe(
        df,
        use_container_width=True
    )

# =========================================================
# ADMIN
# =========================================================
elif page == "⚙️ Admin":

    if not is_admin:

        st.error("⛔ Accès refusé")

    else:

        st.header("⚙️ Administration")

        tabs = st.tabs([
            "➕ Ajouter",
            "✏️ Modifier",
            "🗑️ Supprimer"
        ])

        # =================================================
        # ADD
        # =================================================
        with tabs[0]:

            st.subheader("➕ Ajouter des données")

            with st.form("add_form"):

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

                field = st.number_input("Field", min_value=0)
                fruit = st.number_input("Fruit Mannam", min_value=0)
                autres = st.number_input("Autres Fruits", min_value=0)
                presence = st.number_input("Présence", min_value=0)
                taggui = st.number_input("Taggui", min_value=0)
                bb_ind = st.number_input("BB Individuel", min_value=0)
                bb_group = st.number_input("BB Groupe", min_value=0)
                ct = st.number_input("CT", min_value=0)
                ot = st.number_input("OT", min_value=0)

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

                st.info(f"""
                👤 KYK : {k}

                📅 Date : {date}

                🏆 Points : {points}
                """)

                confirm_add = st.checkbox(
                    "✅ Je confirme l'ajout"
                )

                submit = st.form_submit_button(
                    "Ajouter"
                )

            if submit:

                if points == 0:

                    st.error(
                        "❌ Impossible d'ajouter une entrée vide"
                    )

                elif not confirm_add:

                    st.error(
                        "❌ Veuillez confirmer l'ajout"
                    )

                else:

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

                    st.success(f"""
                    ✅ Données ajoutées avec succès !

                    👤 KYK : {k}

                    🏆 Points enregistrés : {points}
                    """)

                    st.balloons()

                    st.rerun()

        # =================================================
        # UPDATE
        # =================================================
        with tabs[1]:

            st.subheader("✏️ Modifier une entrée")

            if df.empty:

                st.warning("Aucune donnée")

            else:

                selected_label = st.selectbox(
                    "Choisir une entrée",
                    df["label"]
                )

                row = df[
                    df["label"] == selected_label
                ].iloc[0]

                selected_id = row["id"]

                with st.form("edit_form"):

                    edit_date = st.text_input(
                        "Date",
                        value=row["date"]
                    )

                    edit_semaine = st.number_input(
                        "Semaine",
                        value=int(row["semaine"])
                    )

                    edit_k = st.selectbox(
                        "KYK",
                        all_kyk,
                        index=all_kyk.index(row["kuyok"])
                    )

                    edit_field = st.number_input(
                        "Field",
                        value=int(row["field"])
                    )

                    edit_fruit = st.number_input(
                        "Fruit",
                        value=int(row["fruit"])
                    )

                    edit_autres = st.number_input(
                        "Autres",
                        value=int(row["autres"])
                    )

                    edit_presence = st.number_input(
                        "Présence",
                        value=int(row["presence"])
                    )

                    edit_taggui = st.number_input(
                        "Taggui",
                        value=int(row["taggui"])
                    )

                    edit_bb_ind = st.number_input(
                        "BB Individuel",
                        value=int(row["bb_ind"])
                    )

                    edit_bb_group = st.number_input(
                        "BB Groupe",
                        value=int(row["bb_group"])
                    )

                    edit_ct = st.number_input(
                        "CT",
                        value=int(row["ct"])
                    )

                    edit_ot = st.number_input(
                        "OT",
                        value=int(row["ot"])
                    )

                    edit_points = (
                        edit_field * 1 +
                        edit_fruit * 5 +
                        edit_autres * 2 +
                        edit_presence * 10 +
                        edit_taggui * 20 +
                        edit_bb_ind * 50 +
                        edit_bb_group * 100 +
                        edit_ct * 200 +
                        edit_ot * 500
                    )

                    st.info(f"""
                    🏆 Nouveau total : {edit_points} points
                    """)

                    confirm_update = st.checkbox(
                        "✅ Je confirme la modification"
                    )

                    update_btn = st.form_submit_button(
                        "💾 Sauvegarder"
                    )

                if update_btn:

                    if not confirm_update:

                        st.error(
                            "❌ Veuillez confirmer la modification"
                        )

                    else:

                        cursor.execute("""
                        UPDATE resultats
                        SET
                            date=?,
                            semaine=?,
                            kuyok=?,
                            field=?,
                            fruit=?,
                            autres=?,
                            presence=?,
                            taggui=?,
                            bb_ind=?,
                            bb_group=?,
                            ct=?,
                            ot=?
                        WHERE id=?
                        """, (
                            edit_date,
                            int(edit_semaine),
                            edit_k,
                            int(edit_field),
                            int(edit_fruit),
                            int(edit_autres),
                            int(edit_presence),
                            int(edit_taggui),
                            int(edit_bb_ind),
                            int(edit_bb_group),
                            int(edit_ct),
                            int(edit_ot),
                            int(selected_id)
                        ))

                        conn.commit()

                        st.success("""
                        ✅ Modification enregistrée avec succès
                        """)

                        st.balloons()

                        st.rerun()

        # =================================================
        # DELETE
        # =================================================
        with tabs[2]:

            st.subheader("🗑️ Supprimer une entrée")

            if df.empty:

                st.warning("Aucune donnée")

            else:

                delete_label = st.selectbox(
                    "Choisir une entrée",
                    df["label"],
                    key="delete_select"
                )

                row_delete = df[
                    df["label"] == delete_label
                ]

                delete_id = row_delete.iloc[0]["id"]

                st.dataframe(
                    row_delete,
                    use_container_width=True
                )

                confirm_delete = st.checkbox(
                    "⚠️ Je confirme la suppression"
                )

                delete_btn = st.button(
                    "❌ Supprimer définitivement"
                )

                if delete_btn:

                    if not confirm_delete:

                        st.error(
                            "❌ Veuillez confirmer la suppression"
                        )

                    else:

                        cursor.execute("""
                        DELETE FROM resultats
                        WHERE id=?
                        """, (
                            int(delete_id),
                        ))

                        conn.commit()

                        st.success(f"""
                        ✅ Entrée supprimée avec succès !

                        🗑️ {delete_label}
                        """)

                        st.balloons()

                        st.rerun()
