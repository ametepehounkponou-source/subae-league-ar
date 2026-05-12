import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Subae League AR")

st.title("🏆 Subae League AR")

# -----------------------
# FICHIERS
# -----------------------
FILE = "resultats.csv"

if os.path.exists(FILE):
    resultats = pd.read_csv(FILE)
else:
    resultats = pd.DataFrame(columns=[
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
# BARÈME
# -----------------------
points_map = {
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
# FORMULAIRE D'AJOUT
# -----------------------
st.subheader("➕ Ajouter un résultat")

with st.form("form"):
    date = st.text_input("Date (YYYY-MM-DD)")
    semaine = st.number_input("Semaine", step=1)

    kuyok = st.text_input("Kuyok (ex: KYK2)")

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
        new_row = {
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

        resultats = pd.concat([resultats, pd.DataFrame([new_row])], ignore_index=True)
        resultats.to_csv(FILE, index=False)
        st.success("Résultat ajouté ✔️")

# -----------------------
# CALCUL POINTS
# -----------------------
def calc(row):
    total = 0
    for k, v in points_map.items():
        total += float(row.get(k, 0)) * v
    return total

if not resultats.empty:
    for col in points_map.keys():
        resultats[col] = pd.to_numeric(resultats[col], errors="coerce").fillna(0)

    resultats["points"] = resultats.apply(calc, axis=1)

    classement = resultats.groupby("kuyok")["points"].sum().reset_index()
    classement = classement.sort_values("points", ascending=False)

    st.subheader("🏆 Classement général")
    st.dataframe(classement)

# -----------------------
# DONNÉES BRUTES
# -----------------------
st.subheader("📊 Résultats enregistrés")
st.dataframe(resultats)
