import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="Shadow Network Investigator", page_icon="🕵️", layout="wide")

st.title("🕵️ Shadow Network Investigator")
st.markdown("Search for individuals, companies, or keywords across global registries.")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Investigation Scope")
search_mode = st.sidebar.selectbox("Search Mode", ["Target Search (Global)", "Jurisdiction Audit (By Country)"])

if search_mode == "Target Search (Global)":
    query = st.sidebar.text_input("Enter Name/Keyword", placeholder="e.g., Alex Singer or Sahara Foundation")
    country_code = None
else:
    country_code = st.sidebar.text_input("Country Code", value="KY").upper()
    query = None

num_records = st.sidebar.slider("Records to Fetch", 5, 100, 20)

# --- API LOGIC ---
@st.cache_data(ttl=3600)
def fetch_lei_data(search_query=None, country=None, limit=20):
    base_url = "https://api.gleif.org/api/v1/lei-records"
    params = {'page[size]': limit}
    
    if search_query:
        params['filter[fulltext]'] = search_query
    if country:
        params['filter[entity.legalAddress.country]'] = country
        
    response = requests.get(base_url, params=params)
    return response.json().get('data', []) if response.status_code == 200 else None

def get_exception_reason(p_data):
    exception_url = p_data.get('links', {}).get('reporting-exception')
    if not exception_url: return "DISCLOSED"
    try:
        ex_res = requests.get(exception_url).json()
        return ex_res['data']['attributes'].get('exceptionReason', "UNKNOWN")
    except: return "LOOKUP_ERROR"

# --- EXECUTION ---
if st.sidebar.button("🔍 Run Search"):
    with st.spinner("Accessing Global LEI Index..."):
        data = fetch_lei_data(search_query=query, country=country_code, limit=num_records)
        
        if data:
            results = []
            for record in data:
                attr = record['attributes']
                rel = record.get('relationships', {})
                
                results.append({
                    "Entity Name": attr['entity']['legalName']['name'],
                    "Jurisdiction": attr['entity']['legalAddress']['country'],
                    "Direct Parent": get_exception_reason(rel.get('direct-parent', {})),
                    "Ultimate Parent": get_exception_reason(rel.get('ultimate-parent', {})),
                    "LEI": record['id']
                })
            
            df = pd.DataFrame(results)
            
            # --- DISPLAY ---
            st.subheader(f"Results for: {query or country_code}")
            st.dataframe(df, use_container_width=True)
            
            # Pie Chart of Secrecy Reasons
            fig = px.pie(df, names='Direct Parent', title="Ownership Transparency Breakdown", hole=0.4)
            st.plotly_chart(fig)
        else:
            st.error("No matches found. Try broadening your search term.")
