

# --- PAGE CONFIG ---
st.set_page_config(page_title="Offshore Forensic Audit", page_icon="🕵️", layout="wide")

st.title("🕵️ Global Shell Company Audit")
st.markdown("Investigating corporate secrecy and reporting exceptions via the GLEIF API.")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Investigation Parameters")
country_code = st.sidebar.text_input("Enter Country Code (e.g., KY, VG, LU, DE)", value="KY").upper()
num_records = st.sidebar.slider("Number of Entities to Audit", 5, 50, 15)

# --- API LOGIC ---
@st.cache_data(ttl=3600) # Cache for 1 hour so you don't spam the API
def run_audit(country, limit):
    url = f"https://api.gleif.org/api/v1/lei-records?filter[entity.legalAddress.country]={country}&page[size]={limit}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json().get('data', [])

def get_exception_reason(p_data):
    exception_url = p_data.get('links', {}).get('reporting-exception')
    if not exception_url:
        return "DISCLOSED"
    try:
        ex_res = requests.get(exception_url).json()
        attr = ex_res['data']['attributes']
        return attr.get('exceptionReason') or attr.get('exceptionReasons', ["UNKNOWN"])[0]
    except:
        return "LOOKUP_ERROR"

# --- MAIN DASHBOARD ---
if st.button("🚀 Begin Forensic Scan"):
    with st.spinner(f"Scouring {country_code} registries..."):
        data = run_audit(country_code, num_records)
        
        if data:
            audit_results = []
            for record in data:
                name = record['attributes']['entity']['legalName']['name']
                rel = record.get('relationships', {})
                
                # Check Direct Parent
                dp_reason = get_exception_reason(rel.get('direct-parent', {}))
                
                audit_results.append({
                    "Entity Name": name,
                    "Direct Parent Status": dp_reason,
                    "LEI": record['id']
                })
            
            df = pd.DataFrame(audit_results)
            
            # --- METRICS & VISUALS ---
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Raw Investigation Data")
                st.dataframe(df, use_container_width=True)
                
            with col2:
                st.subheader("Secrecy Breakdown")
                fig = px.pie(df, names='Direct Parent Status', hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)
                
            # --- ANOMALY HIGHLIGHTS ---
            st.divider()
            st.subheader("🚩 Potential Shell Anomalies")
            hidden_count = len(df[df['Direct Parent Status'] != 'DISCLOSED'])
            st.warning(f"Found {hidden_count} entities with non-disclosed ownership in this batch.")
            
        else:
            st.error("Could not retrieve data. Check the country code.")
