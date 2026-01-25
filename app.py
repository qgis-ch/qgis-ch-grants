import streamlit as st
import json
import sqlite3
import pandas as pd
import os

# --- KONFIGURATION ---
CONFIG_FILE = 'projekte.json'
DB_FILE = 'data/votes.db'
TOKENS_FILE = 'tokens.txt'
LOGO_FILE = 'logo.png'

def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

# --- DATENBANK & MIGRATION ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Tabelle erstellen (falls nicht existiert)
    c.execute('''CREATE TABLE IF NOT EXISTS votes
                 (token TEXT PRIMARY KEY, 
                  email TEXT, 
                  selected_projects TEXT, 
                  total_cost INTEGER, 
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # MIGRATION: Prüfen, ob Spalte 'email' schon existiert (für Update von alter Version)
    c.execute("PRAGMA table_info(votes)")
    columns = [info[1] for info in c.fetchall()]
    if 'email' not in columns:
        c.execute("ALTER TABLE votes ADD COLUMN email TEXT")
        
    conn.commit()
    conn.close()

def check_token_status(token):
    if not os.path.exists(TOKENS_FILE):
        return "ERROR_NO_TOKEN_FILE"
    
    with open(TOKENS_FILE, 'r') as f:
        valid_tokens = [line.strip() for line in f if line.strip()]
    
    if token not in valid_tokens:
        return "INVALID"
        
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM votes WHERE token=?", (token,))
    exists = c.fetchone()
    conn.close()
    
    if exists:
        return "USED"
    return "OK"

def save_vote(token, email, selected_ids, total_cost):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    ids_str = ",".join(selected_ids)
    try:
        c.execute("INSERT INTO votes (token, email, selected_projects, total_cost) VALUES (?, ?, ?, ?)", 
                  (token, email, ids_str, total_cost))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# --- GUI LOGIK ---
st.set_page_config(page_title=config['titel'], page_icon="📊")

# Logo anzeigen falls vorhanden
if os.path.exists(LOGO_FILE):
    st.image(LOGO_FILE, width=200)

init_db()

if 'user_type' not in st.session_state:
    st.session_state.user_type = None

# --- SIDEBAR ---
with st.sidebar:
    st.header("Login")
    mode = st.radio("Modus", ["Abstimmung", "Admin-Bereich"])
    
    if mode == "Abstimmung":
        token_input = st.text_input("Zugangscode", type="password")
        if st.button("Starten"):
            status = check_token_status(token_input)
            if status == "OK":
                st.session_state.user_type = 'voter'
                st.session_state.token = token_input
                st.rerun()
            elif status == "USED":
                st.error("Code bereits verwendet.")
            else:
                st.error("Ungültiger Code.")
                
    elif mode == "Admin-Bereich":
        admin_pw = st.text_input("Admin Passwort", type="password")
        if st.button("Login"):
            if admin_pw == config['admin_password']:
                st.session_state.user_type = 'admin'
                st.success("Eingeloggt")
                st.rerun()
            else:
                st.error("Falsches Passwort")

# --- VOTER VIEW ---
if st.session_state.user_type == 'voter':
    st.title(config['titel'])
    
    # E-Mail Abfrage
    email = st.text_input("Deine offizielle QGIS-Mitglieder-E-Mail Adresse (Pflichtfeld). - Ton adresse oficielle de membre QGIS-CH.", placeholder="name@beispiel.ch")
    
    st.write("---")
    st.write("Wähle deine Favoriten aus. - Choisis tes favorits:")

    limit = config['budget_limit']
    currency = config['waehrung']
    
    selected_projects = []
    current_total = 0
    
    # Checkboxen für Projekte
    for p in config['projekte']:
        label = f"**{p['name']}**"
        if p.get('beschreibung'):
            label += f" - _{p['beschreibung']}_"
            
        is_selected = st.checkbox(f"{label}  \n💰 {p['kosten']} {currency}", key=p['id'])
        
        if is_selected:
            current_total += p['kosten']
            selected_projects.append(p['id'])

    st.write("---")
    
    # Budget Status Check
    remaining = limit - current_total
    over_budget = current_total > limit

    # Submit Button
    if over_budget:
        st.error(f"⚠️ Budget exceeded by **{abs(remaining)} {currency}**!")
        st.button("Abstimmen - Voter", disabled=True)
    elif not email or "@" not in email:
        st.warning("Bitte gib eine gültige E-Mail Adresse ein. Veuillez fournir une adresse e-mail valide.")
        st.button("Abstimmen - Voter", disabled=True)
    else:
        if st.button("✅ Send", type="primary", use_container_width=True):
            if len(selected_projects) > 0:
                if save_vote(st.session_state.token, email, selected_projects, current_total):
                    st.balloons()
                    st.success("Stimme gespeichert! Vielen Dank. - Vote enregistrée! Merci beaucoup.")
                    del st.session_state['token']
                    st.session_state.user_type = None
                    st.button("Fertig! Zurück zum Start. Fini! Retour au début.")
                else:
                    st.error("Fehler beim Speichern. - Erreur lors de l'enregistrement.")
            else:
                st.warning("Bitte mindestens ein Projekt auswählen. - Veuillez choisir au moins un projet.")
    
    # SIDEBAR Budget-Anzeige (Live-Update)
    with st.sidebar:
        st.write("---")
        st.subheader("💰 Budget-Status")
        
        if over_budget:
            st.error(f"**Überschritten!**  \n{abs(remaining):,} {currency} zu viel")
        elif current_total == 0:
            st.info(f"**Verfügbar:**  \n{limit:,} {currency}")
        else:
            st.success(f"**Verbleibend:**  \n{remaining:,} {currency}")
            st.caption(f"Ausgewählt: {current_total:,} {currency}")


# --- ADMIN VIEW ---
elif st.session_state.user_type == 'admin':
    st.title("Admin Dashboard 🔒")
    
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM votes", conn)
    conn.close()
    
    st.metric("Abgegebene Stimmen", len(df))
    
    if not df.empty:
        # 1. Rangliste berechnen
        all_votes = []
        for ids_str in df['selected_projects']:
            if ids_str:
                all_votes.extend(ids_str.split(','))
            
        counts = pd.Series(all_votes).value_counts().reset_index()
        counts.columns = ['id', 'stimmen']
        
        # Mapping erstellen: ID -> Name & Kosten
        proj_map = {p['id']: p for p in config['projekte']}
        
        counts['Projekt Name'] = counts['id'].apply(lambda x: proj_map.get(x, {}).get('name', 'Unbekannt'))
        counts['Kosten'] = counts['id'].apply(lambda x: proj_map.get(x, {}).get('kosten', 0))
        counts['Volumen (Stimmen * Kosten)'] = counts['stimmen'] * counts['Kosten']
        
        st.subheader("Rangliste")
        st.dataframe(counts[['Projekt Name', 'stimmen', 'Kosten', 'Volumen (Stimmen * Kosten)']], use_container_width=True)

        # 2. Detaillierter CSV Export für Admins
        st.subheader("Daten Export")
        
        # Wir bauen den DataFrame um, damit er lesbarer ist
        export_data = []
        for index, row in df.iterrows():
            sel_ids = row['selected_projects'].split(',') if row['selected_projects'] else []
            
            # Klarnamen und Preise auflisten
            details = []
            for pid in sel_ids:
                p = proj_map.get(pid, {})
                details.append(f"{p.get('name', pid)} ({p.get('kosten', 0)})")
            
            export_data.append({
                "Token": row['token'],
                "Email": row.get('email', '-'), # Fallback für alte Daten
                "Zeitstempel": row['timestamp'],
                "Gesamtkosten": row['total_cost'],
                "Gewählte Projekte (Details)": "; ".join(details),
                "Projekt IDs": row['selected_projects']
            })
            
        export_df = pd.DataFrame(export_data)
        csv = export_df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            "Detaillierte CSV Herunterladen", 
            data=csv, 
            file_name="budget_abstimmung_detail.csv", 
            mime="text/csv"
        )
    else:
        st.info("Noch keine Daten.")

else:
    st.info("👈 Bitte einloggen.")
