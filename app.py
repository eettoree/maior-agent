import streamlit as st
import json
import time
from groq import Groq

# --- CONFIGURAZIONE GLOBALE ---
# Nota: Su Streamlit Cloud, imposta GROQ_API_KEY nei 'Secrets'
try:
    GROQ_KEY = st.secrets["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"]
except:
    GROQ_KEY = "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"

WHATSAPP_NUMBER = "390789604545"
B_GOLD = "#C8A96E"
B_DARK = "#0A0D12"

st.set_page_config(
    page_title="Maior Capital AI Advisor",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- LUXURY UI/UX CUSTOM (GEMINI PRO STYLE) ---
def apply_bespoke_design():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
        
        /* Reset & Mobile Optimization */
        .stApp {{ background-color: {B_DARK}; color: #E6EDF3; font-family: 'Inter', sans-serif; }}
        [data-testid="stHeader"], [data-testid="stToolbar"] {{ display: none; }}
        
        /* Chat Container & Bubbles */
        .stChatMessage {{ 
            border-radius: 28px; 
            padding: 20px 25px; 
            margin-bottom: 18px; 
            border: 1px solid rgba(255,255,255,0.06) !important;
            background-color: transparent !important;
        }}
        .stChatMessage[data-testid="stChatMessageAssistant"] {{ 
            background-color: #111419 !important; 
            border-left: 4px solid {B_GOLD} !important; 
        }}

        /* Skeleton UI Animation */
        @keyframes shimmer {{ 0% {{ opacity: 0.3; }} 50% {{ opacity: 0.6; }} 100% {{ opacity: 0.3; }} }}
        .skeleton {{ height: 16px; background: #1E232B; border-radius: 8px; margin: 12px 0; animation: shimmer 2s infinite; }}

        /* Chat Input Arrotondato */
        div[data-testid="stChatInput"] {{
            border-radius: 35px !important;
            border: 1px solid rgba(200, 169, 110, 0.2) !important;
            background-color: #161B22 !important;
            padding: 10px !important;
        }}

        /* Luxury Property Cards */
        .luxury-card {{
            background: #181C23; 
            border: 1px solid rgba(200, 169, 110, 0.15);
            border-radius: 22px; 
            overflow: hidden; 
            transition: all 0.4s ease;
            margin-bottom: 25px;
        }}
        .luxury-card:hover {{ border-color: {B_GOLD}; transform: translateY(-6px); box-shadow: 0 12px 40px rgba(0,0,0,0.6); }}
        .card-img {{ width: 100%; height: 190px; object-fit: cover; }}
        .card-body {{ padding: 22px; }}
        .card-price {{ color: {B_GOLD}; font-size: 22px; font-weight: 700; }}
        .card-meta {{ color: #888; font-size: 11px; text-transform: uppercase; letter-spacing: 1.2px; margin-top: 4px; }}
        .card-title {{ font-size: 15px; font-weight: 500; margin: 12px 0; color: white; height: 44px; overflow: hidden; }}
        
        /* Buttons Grid */
        .btn-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 18px; }}
        .btn-web {{ text-align: center; background: transparent; border: 1px solid {B_GOLD}; color: {B_GOLD} !important; text-decoration: none; padding: 10px; border-radius: 14px; font-size: 12px; font-weight: 600; transition: 0.2s; }}
        .btn-web:hover {{ background: rgba(200, 169, 110, 0.1); }}
        .btn-wa {{ text-align: center; background: #25D366; color: white !important; text-decoration: none; padding: 10px; border-radius: 14px; font-size: 12px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 7px; }}
        
        /* Mobile adjustment */
        @media (max-width: 640px) {{
            .btn-grid {{ grid-template-columns: 1fr; }}
        }}
        </style>
    """, unsafe_allow_html=True)

# --- LOGICA DATI ---
@st.cache_data
def load_db():
    try:
        with open('immobili_full.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def get_recommendations(query, budget=None):
    db = load_db()
    if not db: return []
    
    results = []
    q = query.lower()
    
    for p in db:
        score = 0
        # Corrispondenza località e tipologia
        if p.get('l', '').lower() in q: score += 20
        if p.get('tp', '').lower() in q: score += 10
        
        # Logica Budget
        if budget and p.get('p_val', 0) > 0:
            if p['p_val'] <= budget: score += 30
            elif p['p_val'] <= budget * 1.2: score += 10
            else: score -= 40
            
        if score > 0:
            results.append((p, score))
    
    return [x[0] for x in sorted(results, key=lambda x: x[1], reverse=True)[:3]]

# --- LOGICA AI ---
client = Groq(api_key=GROQ_KEY)

def call_ai(messages):
    try:
        with open("istruzioni.txt", "r", encoding="utf-8") as f:
            system_prompt = f.read()
            
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}] + messages,
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Mi scusi, ho difficoltà a connettermi ai nostri sistemi. Può contattare Maior Capital direttamente al +39 0789 604545."

# --- MAIN APP ---
apply_bespoke_design()

if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome = "Benvenuto in **Maior Capital**. Sono il suo assistente virtuale dedicato alla ricerca immobiliare di lusso in Sardegna.\n\nMi indichi le sue preferenze: **zona**, **budget** o **tipologia di immobile** (villa, appartamento, terreno)."
    st.session_state.messages.append({"role": "assistant", "content": welcome})

# Render Storia
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Input
if prompt := st.chat_input("Cerco una villa con piscina a Budoni..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Skeleton UI
        placeholder = st.empty()
        placeholder.markdown('<div class="skeleton"></div><div class="skeleton" style="width:75%"></div>', unsafe_allow_html=True)
        
        # Analisi Budget rapida
        found_nums = [int(s.replace('.','')) for s in prompt.split() if s.replace('.','').isdigit() and int(s.replace('.','')) > 10000]
        budget = max(found_nums) if found_nums else None

        # AI Response
        response = call_ai(st.session_state.messages)
        placeholder.empty()

        # Typing Effect parola per parola
        typed_content = ""
        type_area = st.empty()
        for word in response.split():
            typed_content += word + " "
            type_area.markdown(typed_content + "▌")
            time.sleep(0.03)
        type_area.markdown(response)

        # Cards Logic
        matches = get_recommendations(prompt, budget)
        if matches:
            st.markdown("### 💎 Proprietà Consigliate")
            cols = st.columns(len(matches))
            for i, p in enumerate(matches):
                with cols[i]:
                    price = f"€ {p['p_val']:,}".replace(',', '.') if p.get('p_val', 0) > 0 else "Trattativa Riservata"
                    wa_msg = f"Interessato a: {p['t']} ({p['u']})".replace(" ", "%20")
                    wa_link = f"https://wa.me/{WHATSAPP_NUMBER}?text={wa_msg}"
                    
                    st.markdown(f"""
                        <div class="luxury-card">
                            <img src="{p.get('img', '')}" class="card-img">
                            <div class="card-body">
                                <div class="card-price">{price}</div>
                                <div class="card-meta">{p.get('l', 'Sardegna')} | {p.get('mq', '---')} MQ</div>
                                <div class="card-title">{p['t'][:50]}...</div>
                                <div class="btn-grid">
                                    <a href="{p['u']}" target="_blank" class="btn-web">DETTAGLI</a>
                                    <a href="{wa_link}" target="_blank" class="btn-wa">WHATSAPP</a>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})