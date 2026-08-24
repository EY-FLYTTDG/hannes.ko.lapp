import streamlit as st
import time

# ==========================================
# 1. OPPSETT OG DELT MINNE
# ==========================================
st.set_page_config(page_title="Hannes Kø", layout="centered")


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
# 3. FORSIDE FOR KOLLEGAER (MED AUTO-OPPDATERING)
# ==========================================
if visning == "Kølapp (Kollega)":
    st.markdown(
        f"<h1 style='text-align: center; color: red; font-size: 3.5rem;'>NOW SERVING: #{state['now_serving']}</h1>",
        unsafe_allow_html=True)

    estimert_tid = len(state["ko"]) * minutter_per_person
    st.info(f"⏱️ Estimert ventetid til Hanne er ledig: **{estimert_tid} minutter** ({len(state['ko'])} i kø)+- 1t ")

    st.divider()

    # Sjekk om brukeren allerede har en lapp som fortsatt står i køen
    min_aktive_lapp = next((p for p in state["ko"] if p["nr"] == st.session_state["min_lapp_nr"]), None)

    if min_aktive_lapp:
        st.warning(
            f"✋ Du har allerede trukket lapp **#{min_aktive_lapp['nr']}**! Vennligst vent på tur (eller til Hanne sletter deg).")
    else:
        st.subheader("Trekk en kølapp")
        with st.form("trekk_lapp_form"):
            navn = st.text_input("Ditt navn")
            kategori = st.selectbox("Hva gjelder det?", ["Ensom","viktig jobb", "Swada"])
            emne = st.text_area("Utdyp kort (valgfritt)")
            innsendt = st.form_submit_button("Trekk lapp 🎟️")

            if innsendt:
                if navn:
                    state["lapp_nr"] += 1
                    st.session_state["min_lapp_nr"] = state["lapp_nr"]

                    state["ko"].append({
                        "nr": state["lapp_nr"],
                        "navn": navn,
                        "kategori": kategori,
                        "emne": emne
                    })
                    st.success(f"Du har fått kølapp **#{state['lapp_nr']}**!")
                    st.rerun()
                else:
                    st.error("Vennligst fyll ut navnet ditt.")

    # ==========================================
    # 4. SKAMMEKROKEN (AVVISTE SAKER)
    # ==========================================
    if state["skipped"]:
        st.divider()
        st.subheader("🗑️ Nådeløst avvist av Hanne")
        for avvist in reversed(state["skipped"]):
            st.error(f"~~Lapp #{avvist['nr']} — {avvist['navn']} ({avvist['kategori']})~~")

    # AUTO-OPPDATERING KUN PÅ FORSIDEN: Venter 5 sekunder og oppdaterer skiltet
    time.sleep(5)
    st.rerun()


# ==========================================
# 5. HANNES KONTROLLPANEL
# ==========================================
elif visning == "Hannes Kontrollpanel":
    st.header("👩‍💼 Hannes Dashboard")
    passord = st.text_input("Skriv inn passord for å åpne", type="password")

    # Bytt ut "hanne123" med det passordet dere ønsker
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

                    kol1, kol2 = st.columns(2)

                    if kol1.button("✅ Rop opp denne!", key=f"rop_{person['nr']}", use_container_width=True):
                        state["now_serving"] = person["nr"]
                        state["ko"] = [p for p in state["ko"] if p["nr"] != person["nr"]]
                        st.rerun()

                    if kol2.button("🚫 Avvis", key=f"slett_{person['nr']}", use_container_width=True):
                        state["ko"] = [p for p in state["ko"] if p["nr"] != person["nr"]]
                        state["skipped"].append(person)
                        st.rerun()

    elif passord:
        st.error("Feil passord! Tilbake til pulten din.")