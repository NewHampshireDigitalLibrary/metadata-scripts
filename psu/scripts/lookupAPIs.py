"""Lookups Script Class to Match values against Geonames."""
import requests


def lookupGeonames(search_dict):
    # http://www.geonames.org/export/geonames-search.html
    gn_url = "http://api.geonames.org/searchJSON?username=charlow2&maxRows=5"
    name = search_dict.get("name")
    parent = search_dict.get("parent")
    grandparent = search_dict.get("grandparent")
    type = search_dict.get("type")
    q = ', '.join(filter(None, (parent, grandparent)))
    lang = "en"
    countryBias = "US"
    if q:
        resp = requests.get(gn_url + "&name=" + name + "&q=" + q)
    else:
        resp = requests.get(gn_url + "&name=" + name)

    match_array = resp.json().get("geonames")
    if match_array:
        top_match = match_array[0]
        geonameId = top_match.get("geonameId")
        gn_uri = "http://sws.geonames.org/" + str(geonameId) + "/"
        gn_name = top_match.get("name")
        adminName1 = top_match.get("adminName1")
        adminName2 = top_match.get("adminName2")
        countryName = top_match.get("countryName")
        label_ext = ', '.join(filter(None, (gn_name, adminName1, adminName2, countryName)))
        lng = top_match.get("lng")
        lat = top_match.get("lat")
        coords = lat + ", " + lng

        resp_dict = {}
        resp_dict["uri"] = gn_uri
        resp_dict["coords"] = coords
        resp_dict["label"] = label_ext
    else:
        label_ext = ', '.join(filter(None, (name, parent, grandparent)))

        resp_dict = {}
        resp_dict["uri"] = None
        resp_dict["coords"] = None
        resp_dict["label"] = label_ext
    return(resp_dict)
