import streamlit as st

# ==========================================
# 1. OPPSETT OG DELT MINNE
# ==========================================
st.set_page_config(page_title="Hannes Kø", layout="centered")


# Delt minne på tvers av alle brukere
@st.cache_resource
def get_shared_state():
    return {
        "ko": [],
        "now_serving": 0,
        "lapp_nr": 0,
        "skipped": []  # Liste for henvendelser Hanne har slettet
    }


state = get_shared_state()
minutter_per_person = 5

# ==========================================
# 2. ANTI-SPAM (LOKALT MINNE)
# ==========================================
# Husker brukeren i deres egen nettleser for å hindre at de trekker flere lapper
if "min_lapp_nr" not in st.session_state:
    st.session_state["min_lapp_nr"] = None

st.title("🪪 Hannes Køsystem")

# Valg i sidemenyen for å skille visningene
visning = st.sidebar.radio("Velg visning:", ["Kølapp (Kollega)", "Hannes Kontrollpanel"])

# ==========================================
# 3. FORSIDE FOR KOLLEGAER
# ==========================================
if visning == "Kølapp (Kollega)":
    st.markdown(
        f"<h1 style='text-align: center; color: red; font-size: 3.5rem;'>NOW SERVING: #{state['now_serving']}</h1>",
        unsafe_allow_html=True)

    estimert_tid = len(state["ko"]) * minutter_per_person
    st.info(f"⏱️ Estimert ventetid til Hanne er ledig: **{estimert_tid} minutter** ({len(state['ko'])} i kø)")

    st.divider()

    # Sjekk om brukeren allerede har en lapp som fortsatt står i køen
    min_aktive_lapp = next((p for p in state["ko"] if p["nr"] == st.session_state["min_lapp_nr"]), None)

    if min_aktive_lapp:
        # Hvis de har en lapp, får de ikke trekke ny
        st.warning(
            f"✋ Du har allerede trukket lapp **#{min_aktive_lapp['nr']}**! Vennligst vent på tur (eller til Hanne sletter deg).")
    else:
        # Hvis de ikke har en aktiv lapp, kan de trekke en
        st.subheader("Trekk en kølapp")
        with st.form("trekk_lapp_form"):
            navn = st.text_input("Ditt navn")
            kategori = st.selectbox("Hva gjelder det?", ["viktig jobb", "ensom", "swada"])
            emne = st.text_area("Utdyp kort (valgfritt)")
            innsendt = st.form_submit_button("Trekk lapp 🎟️")

            if innsendt:
                if navn:
                    state["lapp_nr"] += 1
                    # Lagrer nummeret i brukerens personlige nettleserminne
                    st.session_state["min_lapp_nr"] = state["lapp_nr"]

                    state["ko"].append({
                        "nr": state["lapp_nr"],
                        "navn": navn,
                        "kategori": kategori,
                        "emne": emne
                    })
                    st.success(f"Du har fått kølapp **#{state['lapp_nr']}**!")
                    st.rerun()  # Oppdaterer siden for å skjule skjemaet
                else:
                    st.error("Vennligst fyll ut navnet ditt.")

    # ==========================================
    # 4. SKAMMEKROKEN (AVVISTE SAKER)
    # ==========================================
    # Viser listen over henvendelser som er slettet/hoppet over
    if state["skipped"]:
        st.divider()
        st.subheader("🗑️ Nådeløst avvist av Hanne")
        for avvist in reversed(state["skipped"]):  # Viser de sist avviste øverst
            st.error(f"~~Lapp #{avvist['nr']} — {avvist['navn']} ({avvist['kategori']})~~")


# ==========================================
# 5. HANNES KONTROLLPANEL
# ==========================================
elif visning == "Hannes Kontrollpanel":
    st.header("👩‍💼 Hannes Dashboard")
    passord = st.text_input("Skriv inn passord for å åpne", type="password")

    if passord == "hanne123":
        st.success("Passord godkjent!")
        st.caption("Her kan du lese hva folk lurer på og bedømme hvor viktig det er.")

        if not state["ko"]:
            st.info("Køen er tom! Nyt kaffen ☕")
        else:
            for person in list(state["ko"]):
                with st.container(border=True):
                    farge = "🔴" if person["kategori"] == "swada" else "🟡" if person["kategori"] == "ensom" else "🟢"
                    st.markdown(f"**Lapp #{person['nr']} — {person['navn']}** {farge} ({person['kategori'].upper()})")

                    if person["emne"]:
                        st.write(f"_{person['emne']}_")

                    # Deler knappene i to kolonner
                    kol1, kol2 = st.columns(2)

                    # Knapp 1: Rop opp
                    if kol1.button("✅ Rop opp denne!", key=f"rop_{person['nr']}", use_container_width=True):
                        state["now_serving"] = person["nr"]
                        state["ko"] = [p for p in state["ko"] if p["nr"] != person["nr"]]
                        st.rerun()

                    # Knapp 2: Hopp over / Slett
                    if kol2.button("🚫 Avvis", key=f"slett_{person['nr']}", use_container_width=True):
                        # Fjerner fra køen og legger i 'skipped'-listen
                        state["ko"] = [p for p in state["ko"] if p["nr"] != person["nr"]]
                        state["skipped"].append(person)
                        st.rerun()

    elif passord:
        st.error("Feil passord! Tilbake til pulten din.")