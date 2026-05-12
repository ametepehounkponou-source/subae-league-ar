import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Subae League AR",
    page_icon="🏆",
    layout="wide"
)

st.title("🏆 Subae League AR - Pro Dashboard")

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

st.sidebar.subheader("🔐 Connexion")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):

    if username in USERS and USERS[username]["password"] == password:

        st.session_state.auth = True
        st.session_state.role = USERS[username]["role"]

        st.success(f"Bienvenue {username}")

    else:
        st.error("Identifiants incorrects")

if not st.session_state.auth:
    st.stop()

is_admin = st.session_state.role == "admin"

# =========================================================
# FILE
# =========================================================
FILE = "resultats.csv"

# =========================================================
# LOAD DATA
# =========================================================
if os.path.exists(FILE):

    df = pd.read_csv(FILE)

else:

    df = pd.DataFrame(columns=[
        "date",
        "semaine",
        "kuyok",
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

# =========================================================
# SETTINGS
# =========================================================
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
# CLEAN DATA
# =========================================================
if not df.empty:

    df["date"] = pd.to_datetime(df["date"])

    for c in weights:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

# =========================================================
# CALCUL POINTS
# =========================================================
def calc_points(row):

    return sum(
        float(row.get(k, 0)) * v
        for k, v in weights.items()
    )

if not df.empty:
    df["points"] = df.apply(calc_points, axis=1)
else:
    df["points"] = 0

# =========================================================
# PRIORITY SCORE
# =========================================================
def priority_score(group):

    return (
        group["Mannam Taggui"].sum() * 1000000 +
        group["Mannam présence"].sum() * 10000 +
        group["Fruit Mannam fixé"].sum() * 100 +
        group["Passage sur le field"].sum()
    )

# =========================================================
# RANKING
# =========================================================
base = pd.DataFrame({"kuyok": all_kyk})

ranking = (
    df.groupby("kuyok")["points"]
    .sum()
    .reset_index()
)

ranking = (
    base.merge(ranking, on="kuyok", how="left")
    .fillna(0)
    .sort_values("points", ascending=False)
)

# =========================================================
# SIDEBAR NAVIGATION
# =========================================================
page = st.sidebar.radio(
    "📂 Navigation",
    [
        "📊 Dashboard",
        "🧠 Analyse KYK",
        "⚔️ Comparaison",
        "📊 Données",
        "⚙️ Admin"
    ]
)

# =========================================================
# DASHBOARD
# =========================================================
if page == "📊 Dashboard":

    st.header("📊 Dashboard Global")

    # =====================================================
    # KPI
    # =====================================================
    c1, c2, c3, c4 = st.columns(4)

    top_kyk = ranking.iloc[0]["kuyok"]
    top_points = ranking.iloc[0]["points"]

    total_points = ranking["points"].sum()

    total_kyk = len(df["kuyok"].unique()) if not df.empty else 0

    current_week = int(df["semaine"].max()) if not df.empty else 0

    c1.metric("🏆 Top KYK", top_kyk)
    c2.metric("🔥 Points Top", f"{top_points:.0f}")
    c3.metric("📈 Total Points", f"{total_points:.0f}")
    c4.metric("📅 Semaine actuelle", current_week)

    # =====================================================
    # DISTINCTIONS
    # =====================================================
    with st.expander("🏅 Distinctions", expanded=True):

        if not df.empty:

            # =========================
            # KYK SEMAINE
            # =========================
            week_df = df[df["semaine"] == current_week]

            week_scores = (
                week_df.groupby("kuyok")
                .apply(priority_score)
                .reset_index(name="score")
                .sort_values("score", ascending=False)
            )

            best_week = week_scores.iloc[0]["kuyok"]
            worst_week = week_scores.iloc[-1]["kuyok"]

            # =========================
            # KYK MOIS
            # =========================
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

            # =========================
            # PROGRESSION
            # =========================
            progressions = []

            for kyk in all_kyk:

                sub = df[df["kuyok"] == kyk]

                weeks = sorted(sub["semaine"].unique())

                if len(weeks) >= 2:

                    current_w = weeks[-1]
                    previous_w = weeks[-2]

                    current_pts = (
                        sub[sub["semaine"] == current_w]["points"]
                        .sum()
                    )

                    previous_pts = (
                        sub[sub["semaine"] == previous_w]["points"]
                        .sum()
                    )

                    if previous_pts > 0:

                        variation = (
                            (current_pts - previous_pts)
                            / previous_pts
                        ) * 100

                        progressions.append({
                            "kuyok": kyk,
                            "variation": variation
                        })

            prog_df = pd.DataFrame(progressions)

            if not prog_df.empty:

                best_progression = (
                    prog_df.sort_values(
                        "variation",
                        ascending=False
                    ).iloc[0]
                )

                worst_regression = (
                    prog_df.sort_values(
                        "variation",
                        ascending=True
                    ).iloc[0]
                )

                bp = best_progression["kuyok"]
                bpv = best_progression["variation"]

                wr = worst_regression["kuyok"]
                wrv = worst_regression["variation"]

            else:

                bp = "N/A"
                bpv = 0

                wr = "N/A"
                wrv = 0

            d1, d2, d3 = st.columns(3)

            d1.success(f"""
            🥇 KYK de la semaine :
            {best_week}
            """)

            d2.success(f"""
            🏆 KYK du mois :
            {best_month}
            """)

            d3.success(f"""
            📈 Plus forte progression :
            {bp}
            ({bpv:.1f}%)
            """)

            d1.error(f"""
            📉 Plus faible semaine :
            {worst_week}
            """)

            d2.error(f"""
            ⚠️ Plus faible mois :
            {worst_month}
            """)

            d3.error(f"""
            🔻 Plus forte régression :
            {wr}
            ({wrv:.1f}%)
            """)

    # =====================================================
    # CLASSEMENT
    # =====================================================
    with st.expander("🏆 Classement général"):

        st.dataframe(
            ranking,
            use_container_width=True,
            hide_index=True
        )

    # =====================================================
    # GRAPHE
    # =====================================================
    with st.expander("📊 Forces globales"):

        st.bar_chart(
            ranking.set_index("kuyok")["points"]
        )

    # =====================================================
    # EVOLUTION
    # =====================================================
    with st.expander("📈 Evolution générale"):

        if not df.empty:

            evo = (
                df.groupby(["semaine", "kuyok"])["points"]
                .sum()
                .reset_index()
            )

            pivot = (
                evo.pivot(
                    index="semaine",
                    columns="kuyok",
                    values="points"
                )
                .fillna(0)
            )

            st.line_chart(pivot)

# =========================================================
# ANALYSE KYK
# =========================================================
elif page == "🧠 Analyse KYK":

    st.header("🧠 Analyse KYK")

    selected_kyk = st.selectbox(
        "Choisir un KYK",
        all_kyk
    )

    sub = df[df["kuyok"] == selected_kyk]

    stats = {c: 0 for c in weights}

    if not sub.empty:
        stats = {c: sub[c].sum() for c in weights}

    total_points = ranking[
        ranking["kuyok"] == selected_kyk
    ]["points"].values[0]

    # =====================================================
    # KPI
    # =====================================================
    k1, k2, k3, k4 = st.columns(4)

    k1.metric("🏆 Points", f"{total_points:.0f}")
    k2.metric("🔥 Taggui", int(stats["Mannam Taggui"]))
    k3.metric("👥 Présence", int(stats["Mannam présence"]))
    k4.metric("🎯 OT", int(stats["Participation OT"]))

    # =====================================================
    # CONVERSIONS
    # =====================================================
    with st.expander("🔄 Conversions", expanded=True):

        field_to_presence = (
            stats["Mannam présence"]
            / stats["Passage sur le field"] * 100
            if stats["Passage sur le field"] > 0 else 0
        )

        presence_to_tag = (
            stats["Mannam Taggui"]
            / stats["Mannam présence"] * 100
            if stats["Mannam présence"] > 0 else 0
        )

        tag_to_bb = (
            stats["BB individuel"]
            / stats["Mannam Taggui"] * 100
            if stats["Mannam Taggui"] > 0 else 0
        )

        ct_to_ot = (
            stats["Participation OT"]
            / stats["CT"] * 100
            if stats["CT"] > 0 else 0
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Field → Présence",
            f"{field_to_presence:.1f}%"
        )

        c2.metric(
            "Présence → Taggui",
            f"{presence_to_tag:.1f}%"
        )

        c3.metric(
            "Taggui → BB",
            f"{tag_to_bb:.1f}%"
        )

        c4.metric(
            "CT → OT",
            f"{ct_to_ot:.1f}%"
        )

    # =====================================================
    # ALERTES
    # =====================================================
    with st.expander("🚨 Alertes & amélioration", expanded=True):

        alerts = []

        if field_to_presence < 20:
            alerts.append(
                "⚠️ Le field ne se transforme pas suffisamment en présence."
            )

        if presence_to_tag < 20:
            alerts.append(
                "⚠️ Les présences deviennent rarement des Taggui."
            )

        if stats["Participation OT"] == 0:
            alerts.append(
                "⚠️ Aucune participation OT."
            )

        if stats["Mannam Taggui"] == 0:
            alerts.append(
                "⚠️ Aucun Mannam Taggui enregistré."
            )

        weeks = sorted(sub["semaine"].unique())

        if len(weeks) >= 2:

            current_w = weeks[-1]
            previous_w = weeks[-2]

            current_pts = (
                sub[sub["semaine"] == current_w]["points"]
                .sum()
            )

            previous_pts = (
                sub[sub["semaine"] == previous_w]["points"]
                .sum()
            )

            if previous_pts > 0:

                variation = (
                    (current_pts - previous_pts)
                    / previous_pts
                ) * 100

                if variation < -25:
                    alerts.append(
                        f"🔻 Forte régression ({variation:.1f}%)"
                    )

                elif variation > 25:
                    alerts.append(
                        f"🔥 Forte progression ({variation:.1f}%)"
                    )

        if len(alerts) == 0:
            st.success("✅ Aucun signal négatif détecté.")

        else:
            for a in alerts:
                st.warning(a)

    # =====================================================
    # SYNTHÈSE
    # =====================================================
    with st.expander("🧠 Synthèse automatique", expanded=True):

        synthesis = []

        if stats["Passage sur le field"] > 20:
            synthesis.append(
                "Le KYK montre une bonne activité terrain."
            )

        if field_to_presence < 20:
            synthesis.append(
                "Le principal point faible est la conversion field → présence."
            )

        if presence_to_tag > 40:
            synthesis.append(
                "Très bonne consolidation des présences."
            )

        if stats["Participation OT"] > 0:
            synthesis.append(
                "Le KYK participe activement aux OT."
            )

        if stats["Mannam Taggui"] == 0:
            synthesis.append(
                "Aucun Mannam Taggui enregistré."
            )

        if len(synthesis) == 0:
            synthesis.append(
                "Le KYK reste stable mais manque encore de données significatives."
            )

        st.info(" ".join(synthesis))

    # =====================================================
    # RADAR
    # =====================================================
    with st.expander("🎮 Radar", expanded=True):

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
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# =========================================================
# COMPARAISON
# =========================================================
elif page == "⚔️ Comparaison":

    st.header("⚔️ Comparaison")

    col1, col2 = st.columns(2)

    with col1:
        kyk1 = st.selectbox(
            "Premier KYK",
            all_kyk
        )

    with col2:
        kyk2 = st.selectbox(
            "Deuxième KYK",
            all_kyk,
            index=1
        )

    sub1 = df[df["kuyok"] == kyk1]
    sub2 = df[df["kuyok"] == kyk2]

    stats1 = {c: 0 for c in weights}
    stats2 = {c: 0 for c in weights}

    if not sub1.empty:
        stats1 = {c: sub1[c].sum() for c in weights}

    if not sub2.empty:
        stats2 = {c: sub2[c].sum() for c in weights}

    compare_df = pd.DataFrame({
        kyk1: stats1,
        kyk2: stats2
    })

    st.dataframe(compare_df)

    categories = [
        "Field",
        "Présence",
        "Taggui",
        "BB",
        "CT",
        "OT"
    ]

    values1 = [
        stats1["Passage sur le field"],
        stats1["Mannam présence"],
        stats1["Mannam Taggui"],
        stats1["BB groupe"] + stats1["BB individuel"],
        stats1["CT"],
        stats1["Participation OT"]
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

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values1,
        theta=categories,
        fill='toself',
        name=kyk1
    ))

    fig.add_trace(go.Scatterpolar(
        r=values2,
        theta=categories,
        fill='toself',
        name=kyk2
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        )
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# DATA
# =========================================================
elif page == "📊 Données":

    st.header("📊 Données brutes")

    st.dataframe(
        df,
        use_container_width=True
    )

# =========================================================
# ADMIN
# =========================================================
elif page == "⚙️ Admin":

    if not is_admin:

        st.error("Accès refusé.")

    else:

        st.header("⚙️ Administration")

        # =================================================
        # AJOUT
        # =================================================
        with st.expander("➕ Ajouter un résultat", expanded=True):

            with st.form("add"):

                date = st.date_input("Date")

                semaine = st.number_input(
                    "Semaine",
                    step=1
                )

                kuyok = st.selectbox(
                    "KYK",
                    all_kyk
                )

                field = st.number_input(
                    "Passage sur le field",
                    step=1
                )

                fruit = st.number_input(
                    "Fruit Mannam fixé",
                    step=1
                )

                autres = st.number_input(
                    "Autres fruits",
                    step=1
                )

                presence = st.number_input(
                    "Mannam présence",
                    step=1
                )

                taggui = st.number_input(
                    "Mannam Taggui",
                    step=1
                )

                bb_ind = st.number_input(
                    "BB individuel",
                    step=1
                )

                bb_group = st.number_input(
                    "BB groupe",
                    step=1
                )

                ct = st.number_input(
                    "CT",
                    step=1
                )

                ot = st.number_input(
                    "Participation OT",
                    step=1
                )

                submit = st.form_submit_button(
                    "Ajouter"
                )

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

                df = pd.concat(
                    [df, pd.DataFrame([new])],
                    ignore_index=True
                )

                df.to_csv(FILE, index=False)

                st.success("Ajouté ✔️")

        # =================================================
        # EDIT
        # =================================================
        with st.expander("✏️ Modifier une ligne"):

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

                    save = st.form_submit_button(
                        "Sauvegarder"
                    )

                if save:

                    df.to_csv(FILE, index=False)

                    st.success("Modifié ✔️")
