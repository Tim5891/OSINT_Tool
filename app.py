import streamlit as st
import requests

st.set_page_config(page_title="GLEIF Linker MVP", page_icon="🕸️")
st.title("🕸️ GLEIF Human-Link Resolver")

target = st.text_input("Search Company", "JPMorgan")

if st.button("🔍 Trace to Human Sources") and target:
    # 1. Get the LEI Record
    url = f"https://api.gleif.org/api/v1/lei-records?filter[fulltext]={target}&page[size]=5"
    res = requests.get(url).json()
    
    for entity in res.get('data', []):
        name = entity['attributes']['entity']['legalName']['name']
        lei = entity['id']
        reg_authority = entity['attributes']['registration']['registrationAuthorityEntityID']
        
        # 2. Check for the 'Human Owner' Flag
        rel = entity.get('relationships', {}).get('direct-parent', {})
        exception = rel.get('links', {}).get('reporting-exception', "None")
        
        st.subheader(f"🏢 {name}")
        st.write(f"**LEI:** `{lei}`")
        
        col1, col2 = st.columns(2)
        with col1:
            if "reporting-exception" in str(exception):
                st.error("👤 **Owned by Natural Persons** (Hidden in GLEIF)")
            else:
                st.success("🏢 **Owned by Corporate Parent**")
        
        with col2:
            # This is your 'Jump' point to find the actual names
            st.info(f"📍 **Local Registry ID:** `{reg_authority}`")
            # We can build a dynamic link based on the authority
            if "RA000602" in entity['attributes']['registration']['registrationAuthorityID']: # UK
                st.markdown(f"[View Directors on UK Register](https://find-and-update.company-information.service.gov.uk/company/{reg_authority})")

        st.divider()
