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

        # 1. Rullegardinmeny for emne
        kategori = st.selectbox("Hva gjelder det?", ["viktig jobb", "ensom", "swada"])

        # Et lite tekstfelt hvis de vil utdype (valgfritt)
        emne = st.text_area("Utdyp kort (valgfritt)")

        innsendt = st.form_submit_button("Trekk lapp 🎟️")

        if innsendt:
            if navn:
                state["lapp_nr"] += 1
                state["ko"].append({
                    "nr": state["lapp_nr"],
                    "navn": navn,
                    "kategori": kategori,
                    "emne": emne
                })
                st.success(f"Du har fått kølapp **#{state['lapp_nr']}**!")
            else:
                st.error("Vennligst fyll ut navnet ditt.")

elif visning == "Hannes Kontrollpanel":
    st.header("👩‍💼 Hannes Dashboard")

    # 2. Passordbeskyttelse for å åpne panelet
    passord = st.text_input("Skriv inn passord for å åpne", type="password")

    # Bytt ut "hanne123" med det passordet dere ønsker
    if passord == "hanne123":
        st.success("Passord godkjent!")
        st.caption("Her kan du se sakene og velge hvem som skal ropes opp.")

        if not state["ko"]:
            st.info("Køen er tom! Nyt kaffen ☕")
        else:
            for person in list(state["ko"]):
                with st.container(border=True):
                    # Fargekode basert på hva de valgte i rullegardinen
                    farge = "🔴" if person["kategori"] == "swada" else "🟡" if person["kategori"] == "ensom" else "🟢"

                    st.markdown(f"**Lapp #{person['nr']} — {person['navn']}** {farge} ({person['kategori'].upper()})")

                    if person["emne"]:
                        st.write(f"_{person['emne']}_")

                    if st.button("Rop opp denne!", key=f"btn_{person['nr']}"):
                        state["now_serving"] = person["nr"]
                        state["ko"] = [p for p in state["ko"] if p["nr"] != person["nr"]]
                        st.rerun()
    elif passord:
        # Vises hvis de skriver feil passord
        st.error("Feil passord! Tilbake til pulten din.")