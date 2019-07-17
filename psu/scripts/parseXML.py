"""Parse provided harvested OAI-PMH XML file for Reconciliation."""
import re

def parserx(value):
    # Androscoggin River (United States, North and Central America : river)
    # Florida (United States, North and Central America : state)
    # La Tuque (Quebec province, Canada : inhabited place)
    psugeneral_re = re.compile('(.*)\((.*)\,(.*)\:(.*)\)')
    # Saco River (United States : river)
    # Sandwich Dome (New Hampshire : peak)
    # Washington (District of Colombia : inhabited place)
    psugeneral2_re = re.compile('(.*)\((.*)\:(.*)\)')

    # Set defaults for parse search values
    search_dict = {
        "name": None,
        "parent": None,
        "grandparent": None,
        "type": None
    }

    if re.match(psugeneral_re, value.lower()):
        match = re.search(psugeneral_re, value.lower().strip())
        search_dict["name"] = match.group(1).strip()
        search_dict["parent"] = match.group(2).strip()
        search_dict["grandparent"] = match.group(3).strip()
        search_dict["type"] = match.group(4).strip()
    elif re.match(psugeneral2_re, value.lower()):
        match = re.search(psugeneral2_re, value.lower().strip())
        search_dict["name"] = match.group(1).strip()
        search_dict["parent"] = match.group(2).strip()
        search_dict["type"] = match.group(3).strip()
    else:
        search_dict["name"] = value.strip()

    return(search_dict)
