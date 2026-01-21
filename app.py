import streamlit as st  # <--- MUST be at the very top
import requests

# 1. Page Config must be the first Streamlit command
st.set_page_config(page_title="GLEIF Linker MVP", page_icon="🕸️")

st.title("🕸️ GLEIF Human-Link Resolver")

# 2. Main Logic
target = st.text_input("Search Company", "JPMorgan")

if st.button("🔍 Trace to Human Sources") and target:
    url = f"https://api.gleif.org/api/v1/lei-records?filter[fulltext]={target}&page[size]=5"
    
    try:
        res = requests.get(url).json()
        entities = res.get('data', [])
        
        if not entities:
            st.warning("No entities found.")
            
        for entity in entities:
            attr = entity.get('attributes', {})
            name = attr.get('entity', {}).get('legalName', {}).get('name', "Unknown")
            
            # --- THE FIX: Relationship Check ---
            rel = entity.get('relationships', {}).get('direct-parent', {})
            links = rel.get('links', {})
            
            st.subheader(f"🏢 {name}")
            
            # Use 'in' to safely check the dictionary content
            if 'reporting-exception' in links:
                # Line 13: This will now work because 'st' is globally defined
                st.error("👤 **Owned by Natural Persons**")
            else:
                st.success("🏢 **Corporate Parent Path Available**")
                
            st.divider()
            
    except Exception as e:
        st.error(f"An error occurred: {e}")
