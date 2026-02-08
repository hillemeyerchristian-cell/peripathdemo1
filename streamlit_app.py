import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime

st.set_page_config(
    page_title="Peripath - Deine KI-Begleiterin",
    page_icon="🌸",
    layout="centered"
)

# Custom CSS
st.markdown('''
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0 2rem 0;
        border-bottom: 2px solid #FFF4F9;
        margin-bottom: 2rem;
    }
    .disclaimer {
        background-color: #FFF9E6;
        border-left: 4px solid #FFB800;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
</style>
''', unsafe_allow_html=True)

PERIPATH_SYSTEM_PROMPT = '''Du bist Peripath, eine KI-gestützte Begleiterin für Frauen durch die Perimenopause. 

Du bietest wissenschaftlich fundierte Information basierend auf:
- Peer-reviewed Studien aus PubMed, Cochrane Database
- Klinischen Leitlinien von IMS, NAMS, EMAS, DMG, S3-Leitlinie Peri- und Postmenopause

WICHTIG:
- ❌ Du stellst keine Diagnosen
- ❌ Du ersetzt keine ärztliche Beratung
- ✅ Du informierst, ordnest ein, erklärst Zusammenhänge
- ✅ Bei ernsthaften Symptomen empfiehlst du ärztliche Abklärung

Ton: Empathisch, verständlich, auf Augenhöhe, wissenschaftlich fundiert, ermutigend.

Struktur deiner Antworten:
1. Direkte Antwort (2-4 Sätze)
2. Erklärung & Kontext
3. Handlungsoptionen (wenn relevant)
4. Quellenangaben am Ende: 
   📚 Quellen: [Name, Jahr]
5. Optional: Follow-up-Vorschlag

Kernthemen:
- Perimenopause Definition, Symptome (Hitzewallungen, Schlaf, Stimmung, Gewicht)
- Hormontherapie (HRT): Nutzen, Risiken
- Lifestyle: Ernährung, Bewegung
- Psychische Gesundheit
- Wo finde ich Hilfe?'''

def initialize_gemini():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        api_key = st.secrets.get("GOOGLE_API_KEY")
    
    if not api_key:
        st.error("⚠️ GOOGLE_API_KEY nicht gefunden!")
        st.info("Bitte setze deinen API-Key in den Streamlit Secrets.")
        st.stop()
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=PERIPATH_SYSTEM_PROMPT
    )

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": '''👋 Hallo! Ich bin **Peripath**, deine KI-gestützte Begleiterin durch die Perimenopause.

Ich kann dir wissenschaftlich fundierte Informationen geben zu:
• **Symptomen** (Hitzewallungen, Schlafstörungen, Stimmung, Gewicht)
• **Behandlungsmöglichkeiten** (Hormontherapie und Alternativen)
• **Lifestyle-Tipps** (Ernährung, Bewegung)

Was möchtest du wissen? 💚'''
    }]

if "model" not in st.session_state:
    st.session_state.model = initialize_gemini()

# Header
st.markdown('<div class="main-header"><h1>🌸 Peripath</h1><p>Deine KI-gestützte Begleiterin durch die Perimenopause</p></div>', unsafe_allow_html=True)

# Disclaimer
st.markdown('<div class="disclaimer">⚠️ <strong>Medizinischer Hinweis:</strong> Peripath ersetzt keine ärztliche Beratung und stellt keine Diagnosen.</div>', unsafe_allow_html=True)

# Chat Historie
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Stelle deine Frage..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            chat_history = []
            for msg in st.session_state.messages[1:]:
                role = "user" if msg["role"] == "user" else "model"
                chat_history.append({"role": role, "parts": [msg["content"]]})
            
            chat = st.session_state.model.start_chat(history=chat_history[:-1])
            response = chat.send_message(prompt)
            full_response = response.text
            
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"❌ Fehler: {str(e)}")

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Über Peripath")
    st.markdown("Basiert auf wissenschaftlichen Quellen: DMG, S3-Leitlinie, NAMS, IMS")
    
    if st.button("🗑️ Chat zurücksetzen"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📞 Hilfe")
    st.markdown("[Deutsche Menopause Gesellschaft](https://www.menopause-gesellschaft.de/)")
    st.caption(f"Peripath v1.0 | {datetime.now().year}")
