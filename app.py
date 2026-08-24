import streamlit as st

st.set_page_config(page_title="Hannes Kø", layout="centered")


# Delt minne på tvers av alle brukere
@st.cache_resource
def get_shared_state():
    return {
        "ko": [],
        "now_serving": 0,
        "lapp_nr": 0
    }


state = get_shared_state()
minutter_per_person = 5

st.title("🪪 Hannes Køsystem")

# Valg i sidemenyen for å skille Hanne og kollegaer
visning = st.sidebar.radio("Velg visning:", ["Kølapp (Kollega)", "Hannes Kontrollpanel"])

if visning == "Kølapp (Kollega)":
    st.markdown(
        f"<h1 style='text-align: center; color: red; font-size: 3.5rem;'>NOW SERVING: #{state['now_serving']}</h1>",
        unsafe_allow_html=True)

    estimert_tid = len(state["ko"]) * minutter_per_person
    st.info(f"⏱️ Estimert ventetid til Hanne er ledig: **{estimert_tid} minutter** ({len(state['ko'])} i kø)")

    st.divider()
    st.subheader("Trekk en kølapp")

    with st.form("trekk_lapp_form", clear_on_submit=True):
        navn = st.text_input("Ditt navn")
        emne = st.text_area("Hva lurer du på? (Vær presis!)")
        innsendt = st.form_submit_button("Trekk lapp 🎟️")

        if innsendt:
            if navn and emne:
                state["lapp_nr"] += 1
                state["ko"].append({
                    "nr": state["lapp_nr"],
                    "navn": navn,
                    "emne": emne
                })
                st.success(f"Du har fått kølapp **#{state['lapp_nr']}**!")
            else:
                st.error("Vennligst fyll ut både navn og hva du lurer på.")

elif visning == "Hannes Kontrollpanel":
    st.header("👩‍💼 Hannes Dashboard")
    st.caption("Her kan du se sakene og velge hvem som skal ropes opp.")

    if not state["ko"]:
        st.success("Køen er tom! Nyt kaffen ☕")
    else:
        for person in list(state["ko"]):
            with st.container(border=True):
                st.markdown(f"**Lapp #{person['nr']} — {person['navn']}**")
                st.write(f"_{person['emne']}_")
                if st.button("Rop opp denne!", key=f"btn_{person['nr']}"):
                    state["now_serving"] = person["nr"]
                    state["ko"] = [p for p in state["ko"] if p["nr"] != person["nr"]]
                    st.rerun()