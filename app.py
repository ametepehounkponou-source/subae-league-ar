import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Subae League AR")

st.title("🏆 Subae League AR")

FILE = "resultats.csv"

# -----------------------
# LOAD DATA
# -----------------------
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
# AJOUT RESULTAT (FORMULAIRE 1)
# -----------------------
st.subheader("➕ Ajouter un résultat")

with st.form("form_add"):
    date = st.text_input("Date")
    semaine = st.number_input("Semaine", step=1)
    kuyok = st.text_input("Kuyok")

    field = st.number_input("Passage sur le field", step=1)
    fruit = st.number_input("Fruit Mannam fixé", step=1)
    autres = st.number_input("Autres fruits", step=1)
    presence = st.number_input("Mannam présence", step=1)
    taggui = st.number_input("Mannam Taggui", step=1)
    bb_ind = st.number_input("BB individuel", step=1)
    bb_group = st.number_input("BB groupe", step=1)
    ct = st.number_input("CT", step=1)
    ot = st.number_input("Participation OT", step=1)

    submit_add = st.form_submit_button("Ajouter")

if submit_add:
    new = {
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

    resultats = pd.concat([resultats, pd.DataFrame([new])], ignore_index=True)
    resultats.to_csv(FILE, index=False)
    st.success("Résultat ajouté ✔️")

# -----------------------
# EDIT RESULT (FORMULAIRE 2)
# -----------------------
st.subheader("✏️ Modifier un résultat")

if not resultats.empty:
    index = st.number_input("Index à modifier", 0, len(resultats)-1, 0)

    row = resultats.iloc[index]

    with st.form("form_edit"):
        field = st.number_input("Field", value=int(row["Passage sur le field"]))
        fruit = st.number_input("Fruit", value=int(row["Fruit Mannam fixé"]))
        autres = st.number_input("Autres", value=int(row["Autres fruits (NTF, EM, etc.)"]))
        presence = st.number_input("Présence", value=int(row["Mannam présence"]))
        taggui = st.number_input("Taggui", value=int(row["Mannam Taggui"]))
        bb_ind = st.number_input("BB indiv", value=int(row["BB individuel"]))
        bb_group = st.number_input("BB groupe", value=int(row["BB groupe"]))
        ct = st.number_input("CT", value=int(row["CT"]))
        ot = st.number_input("OT", value=int(row["Participation OT"]))

        submit_edit = st.form_submit_button("Modifier")

    if submit_edit:
        resultats.at[index, "Passage sur le field"] = field
        resultats.at[index, "Fruit Mannam fixé"] = fruit
        resultats.at[index, "Autres fruits (NTF, EM, etc.)"] = autres
        resultats.at[index, "Mannam présence"] = presence
        resultats.at[index, "Mannam Taggui"] = taggui
        resultats.at[index, "BB individuel"] = bb_ind
        resultats.at[index, "BB groupe"] = bb_group
        resultats.at[index, "CT"] = ct
        resultats.at[index, "Participation OT"] = ot

        resultats.to_csv(FILE, index=False)
        st.success("Résultat modifié ✔️")

# -----------------------
# CALCUL
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

# -----------------------
# CLASSEMENT COMPLET
# -----------------------
all_kyk = [f"KYK{i}" for i in range(1, 19)]
base = pd.DataFrame({"kuyok": all_kyk})

if not resultats.empty:
    classement = resultats.groupby("kuyok")["points"].sum().reset_index()
    classement = base.merge(classement, on="kuyok", how="left").fillna(0)
else:
    classement = base
    classement["points"] = 0

classement = classement.sort_values("points", ascending=False)

st.subheader("🏆 Classement général")
st.dataframe(classement)

st.subheader("📊 Résultats")
st.dataframe(resultats)
