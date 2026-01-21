import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="The Deep Web Audit", page_icon="🕵️", layout="wide")

st.title("🕵️ The Deep Web Audit: Persons & Entities")

# --- USER INPUT ---
target_name = st.text_input("Enter a Name (Person or Company)", placeholder="e.g. Jamie Dimon or JPMorgan")

if st.button("🚀 Conduct Dual-Source Audit") and target_name:
    # 1. Search OpenOwnership for the HUMAN connection
    oo_url = f"https://register.openownership.org/api/v1/search?q={target_name}"
    oo_res = requests.get(oo_url).json()
    
    oo_items = oo_res.get('items', [])
    
    if oo_items:
        st.subheader(f"👤 Human Control Links for '{target_name}'")
        records = []
        for item in oo_items:
            # Look for LEIs embedded in OpenOwnership records
            identifiers = item.get('entity', {}).get('identifiers', [])
            lei = next((i['id'] for i in identifiers if i['scheme'] == 'GB-LEI' or 'LEI' in i['scheme']), "N/A")
            
            records.append({
                "Person": item.get('person', {}).get('name', 'N/A'),
                "Company": item.get('entity', {}).get('name', 'N/A'),
                "Jurisdiction": item.get('entity', {}).get('jurisdiction', '??'),
                "Connection": item.get('type', 'Owner/Director'),
                "LEI": lei
            })
        
        df_oo = pd.DataFrame(records)
        st.table(df_oo)

        # 2. PIVOT: If we found LEIs, let's look them up in GLEIF
        leis_found = [r['LEI'] for r in records if r['LEI'] != "N/A"]
        if leis_found:
            st.subheader("🕸️ Global Corporate Web (GLEIF Pivot)")
            for lei in set(leis_found):
                gleif_url = f"https://api.gleif.org/api/v1/lei-records/{lei}"
                gleif_res = requests.get(gleif_url).json()
                
                # Show the parent company for each LEI found
                st.write(f"**Tracing LEI {lei}...**")
                # (Add your parent-lookup logic here to show the hierarchy)
                st.divider()
    else:
        st.info("No person-based ownership records found. Searching for entity names instead...")
        # (Insert your previous GLEIF search logic here as a fallback)
