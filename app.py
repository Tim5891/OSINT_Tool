import streamlit as st
import requests
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="Corporate Spiderweb", page_icon="🕸️", layout="wide")

st.title("🕸️ Corporate Spiderweb Investigator")
st.markdown("Trace global ownership chains and unmask parent companies.")

# --- DATA: ISO COUNTRY CODES (Abbreviated List) ---
COUNTRIES = {"Any": None, "Cayman Islands": "KY", "Luxembourg": "LU", "British Virgin Islands": "VG", "USA": "US", "UK": "GB", "Panama": "PA"}

# --- SIDEBAR: ADVANCED SEARCH ---
st.sidebar.header("🔍 Search Parameters")
search_term = st.sidebar.text_input("Entity Name or Alias", placeholder="e.g., Nicholas Gold")
selected_country = st.sidebar.selectbox("Filter by Country (Optional)", list(COUNTRIES.keys()))
deep_scan = st.sidebar.checkbox("Deep Scan (Follow Parent Chains)", value=True)

# --- API HELPERS ---
def get_entity_name_by_lei(lei):
    """Quick lookup to turn an LEI into a human-readable name."""
    if not lei: return "Unknown"
    url = f"https://api.gleif.org/api/v1/lei-records/{lei}"
    try:
        res = requests.get(url).json()
        return res['data']['attributes']['entity']['legalName']['name']
    except:
        return lei # Fallback to LEI if lookup fails

def get_secrecy_reason(p_data):
    """Extract why a parent is hidden."""
    exception_url = p_data.get('links', {}).get('reporting-exception')
    if not exception_url: return None
    try:
        ex_res = requests.get(exception_url).json()
        return ex_res['data']['attributes'].get('exceptionReason', "HIDDEN")
    except: return "HIDDEN"

# --- MAIN INVESTIGATION ---
if st.sidebar.button("🕵️ Start Investigation") and search_term:
    with st.spinner(f"Tracing connections for '{search_term}'..."):
        # 1. Primary Search
        base_url = "https://api.gleif.org/api/v1/lei-records"
        params = {'filter[fulltext]': search_term, 'page[size]': 15}
        
        if COUNTRIES[selected_country]:
            params['filter[entity.legalAddress.country]'] = COUNTRIES[selected_country]
            
        res = requests.get(base_url, params=params)
        
        if res.status_code == 200:
            entries = res.json().get('data', [])
            report_data = []

            for entry in entries:
                name = entry['attributes']['entity']['legalName']['name']
                lei = entry['id']
                rel = entry.get('relationships', {})
                
                # Resolve Direct Parent
                dp_lei = rel.get('direct-parent', {}).get('data', {}).get('id')
                if dp_lei:
                    dp_display = get_entity_name_by_lei(dp_lei) if deep_scan else dp_lei
                else:
                    dp_display = f"⚠️ {get_secrecy_reason(rel.get('direct-parent', {}))}"

                # Resolve Ultimate Parent
                up_lei = rel.get('ultimate-parent', {}).get('data', {}).get('id')
                if up_lei:
                    up_display = get_entity_name_by_lei(up_lei) if deep_scan else up_lei
                else:
                    up_display = f"⚠️ {get_secrecy_reason(rel.get('ultimate-parent', {}))}"

                report_data.append({
                    "Target Entity": name,
                    "Country": entry['attributes']['entity']['legalAddress']['country'],
                    "Direct Parent": dp_display,
                    "Ultimate Parent": up_display,
                    "LEI": lei
                })

            df = pd.DataFrame(report_data)
            st.subheader(f"Ownership Web for '{search_term}'")
            st.table(df) # Using table for a grittier 'report' look
            
            # Gritty Analysis Note
            st.info("💡 **Investigative Tip:** If the Direct and Ultimate parents are different, you've found a middle-tier holding company. If they are both marked 'NATURAL_PERSONS', the trail ends with an individual owner.")
        else:
            st.error("No data found or API limit reached.")
