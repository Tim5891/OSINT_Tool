import streamlit as st
import requests

st.set_page_config(page_title="GLEIF Linker MVP", page_icon="🕸️")
st.title("🕸️ GLEIF Human-Link Resolver")

target = st.text_input("Search Company", "JPMorgan")

if st.button("🔍 Trace to Human Sources") and target:
    # GLEIF API search
    url = f"https://api.gleif.org/api/v1/lei-records?filter[fulltext]={target}&page[size]=5"
    res = requests.get(url).json()
    
    entities = res.get('data', [])
    if not entities:
        st.warning("No entities found.")
    
    for entity in entities:
        attr = entity.get('attributes', {})
        entity_name = attr.get('entity', {}).get('legalName', {}).get('name', "Unknown Name")
        lei = entity.get('id')
        
        # --- SAFE EXTRACTION OF REGISTRATION DATA ---
        reg = attr.get('registration', {})
        # The key path is: attributes -> registration -> registrationAuthorityEntityID
        reg_auth_id = reg.get('registrationAuthorityID', "N/A")
        reg_entity_id = reg.get('registrationAuthorityEntityID', "N/A")
        
        st.subheader(f"🏢 {entity_name}")
        st.write(f"**LEI:** `{lei}`")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Check for ownership type
            rel = entity.get('relationships', {}).get('direct-parent', {})
            if 'reporting-exception' in str(rel.get('links', {})):
                st.error("👤 **Owned by Natural Persons**")
            else:
                st.success("🏢 **Corporate Parent Path Available**")
        
        with col2:
            st.info(f"📍 **Registry Code:** `{reg_auth_id}`")
            if reg_entity_id != "N/A":
                st.write(f"**Local ID:** `{reg_entity_id}`")
                
                # Dynamic Link Logic for UK (RA000602)
                if reg_auth_id == "RA000602":
                    st.markdown(f"🔗 [View UK Directors](https://find-and-update.company-information.service.gov.uk/company/{reg_entity_id})")
                # Dynamic Link Logic for Luxembourg (RA000435)
                elif reg_auth_id == "RA000435":
                    st.markdown(f"🔗 [Search Luxembourg RBE](https://www.lbr.lu/)")
            else:
                st.write("No Local Registry ID found in GLEIF record.")

        st.divider()
