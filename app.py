import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Deep Link MVP", page_icon="🕵️", layout="wide")
st.title("🕵️ The Deep Link MVP")

# Get a free API key at opensanctions.org
API_KEY = st.sidebar.text_input("OpenSanctions API Key", type="password")
search_term = st.text_input("Target Name (Person or Company)", "Jamie Dimon")

def get_links(entity_id):
    """Fetch adjacent entities (the spiderweb)."""
    url = f"https://api.opensanctions.org/entities/{entity_id}/adjacent"
    res = requests.get(url, headers={"Authorization": f"ApiKey {API_KEY}"})
    return res.json().get('entities', []) if res.status_code == 200 else []

if st.button("🔍 Map Connections") and API_KEY:
    # 1. Search for the core target
    search_url = "https://api.opensanctions.org/search/default"
    s_res = requests.get(search_url, params={"q": search_term}, headers={"Authorization": f"ApiKey {API_KEY}"})
    
    if s_res.status_code == 200:
        results = s_res.json().get('results', [])
        if results:
            target = results[0] # Take the top match
            target_id = target['id']
            st.subheader(f"Target: {target['caption']} ({target['schema']})")
            
            # 2. Find the spiderweb
            adjacent = get_links(target_id)
            
            links_list = []
            for adj in adjacent:
                links_list.append({
                    "Linked To": adj['caption'],
                    "Type": adj['schema'],
                    "Reason": adj.get('referents', ["Assumed Relationship"])[0],
                    "Country": adj.get('properties', {}).get('country', ['??'])[0]
                })
            
            df = pd.DataFrame(links_list)
            st.table(df)
            
            st.success(f"Successfully mapped {len(df)} direct connections.")
        else:
            st.error("No target found.")
