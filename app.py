def get_registry_link(ra_id, entity_id):
    # Mapping the most common 'Shadow' registries
    registry_map = {
        "RA000602": f"https://find-and-update.company-information.service.gov.uk/company/{entity_id}", # UK
        "RA000435": f"https://www.lbr.lu/mjrcs/jsp/IndexAction.do", # Luxembourg
        "RA000613": f"https://opencorporates.com/companies/us_de/{entity_id}", # Delaware (via OpenCorp)
        "RA000185": f"https://www.zefix.ch/en/search/entity/list?name={entity_id}", # Switzerland
        "RA000393": f"https://www.hksar.gov.hk/", # Hong Kong
    }
    return registry_map.get(ra_id, "Registry Link Not Mapped")

# Inside your loop, change the display logic:
st.error("👤 **Owned by Natural Persons**")
reg_link = get_registry_link(reg_auth_id, reg_entity_id)

if "http" in reg_link:
    st.markdown(f"👉 **[Unmask the Human Names Here]({reg_link})**")
    st.caption(f"Search for ID: {reg_entity_id} in the portal above.")
else:
    st.info(f"Manual Search Required: {reg_auth_id} | ID: {reg_entity_id}")
