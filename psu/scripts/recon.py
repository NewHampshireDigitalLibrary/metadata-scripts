"""CLI script reconciles OAI XML w/Geonames & write into remediation.xslt."""
import sys
from argparse import ArgumentParser
from xml.etree import ElementTree as etree
from analyzeCDM import Record
from parseXML import parserx
from lookupAPIs import lookupGeonames

OAI_NS = "{http://www.openarchives.org/OAI/2.0/}"
DC_NS = "{http://purl.org/dc/elements/1.1/}"
DCTERMS_NS = "{http://purl.org/dc/terms/}"
OCLC_NS = "{http://purl.org/oclc/terms/}"

NSMAP = {
    "xsl": "http://www.w3.org/1999/XSL/Transform",
    "nhdl": "http://github.com/cmharlow/nhdl-mdx/",
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "dcterms": "http://purl.org/dc/terms/",
    "dc": "http://purl.org/dc/elements/1.1/"
}

def main():
    """CLI & Main Reconciliation Workflow."""
    parser = ArgumentParser(usage='%(prog)s [options] data_filename.xml')
    parser.add_argument("-d", "--delimiter", dest="delimiter",
                        default=False, help="delimiter to split the field value on.")
    parser.add_argument("-e", "--element", dest="element", default="dcterms:spatial",
                        help="element to reconcile")
    parser.add_argument("-r", "--reconciled", dest="reconciled", default="remediation.xslt",
                        help="name of file with reconciled XSL dictionary.")
    parser.add_argument("-p", "--param", dest="param", default="geonamesLocation",
                        help="name of XSL file's reconciled values param to parse and extend.")
    parser.add_argument("file", help="datafile you want parsed for reconciliation values")

    args = parser.parse_args()

    # Returns the help text if there are no flags or a datafile present.
    if not sys.argv:
        parser.print_help()
        exit()

    # Namespace dictionary creation for ease of working with NS namespaces.
    # This is used to generate a nsmap based off of the given data file.
    def fixtag(ns, tag):
        return '{' + NSMAP[ns] + '}' + tag

    # Already matched values will go into this dictionary
    matched_dict = {}

    # Parsing reconciliation XSL's determined param dictionary for values already reconciled:
    for event, elem in etree.iterparse(args.reconciled, events=('end', 'start-ns')):
        if event == 'end':
            if elem.tag == fixtag("xsl", "param") and elem.attrib.get("name") == args.param:
                for lookup in elem.iter(fixtag("nhdl", "lookup")):
                    orig_value = lookup.attrib.get("string")
                    gn_uri = lookup.attrib.get("uri")
                    coords = lookup.attrib.get("coordinates")
                    label = lookup.text

                    matched_dict[orig_value] = {}
                    matched_dict[orig_value]["uri"] = gn_uri
                    matched_dict[orig_value]["coords"] = coords
                    matched_dict[orig_value]["label"] = label

    # Data values to be reconciled
    original_values = []

    # Parsing each record in harvest file and applying lookups on designating element:
    for event, elem in etree.iterparse(args.file, events=('end', 'start-ns')):
        if event == 'end':
            if elem.tag == fixtag("oai", "record"):
                r = Record(elem, args)
                # move along if record is deleted or None
                if r.get_record_status() != "deleted" and r.get_elements(NSMAP):
                    for i in r.get_elements(NSMAP):
                        if args.delimiter:
                            split = i.split(args.delimiter)
                            for j in split:
                                original_values.append(j.strip())
                        else:
                            original_values.append(i.strip())
                elem.clear()

    # Pass array of unique, raw values not already matched to Regex Parser
    # Then pass the values to Geonames Lookup & Add to matched_dict
    for value in set(original_values):
        already_matched = matched_dict.get(value)
        if already_matched is None or already_matched.get("uri") is None:
            search_dict = parserx(value)
            # Pass parsed values to GeoNames Look-up API
            resp_dict = lookupGeonames(search_dict)
            orig_value = value
            uri = resp_dict.get("uri")
            coords = resp_dict.get("coords")
            label = resp_dict.get("label")

            # Add new lookup values
            matched_dict[orig_value] = {}
            matched_dict[orig_value]["uri"] = uri
            matched_dict[orig_value]["coords"] = coords
            matched_dict[orig_value]["label"] = label

    # Write values back to XSL
    outfile = etree.parse(args.reconciled)
    outfile = outfile.getroot()
    node = "{http://www.w3.org/1999/XSL/Transform}param[@name='" + args.param + "']"
    param_node = outfile.find(node)
    param_node.clear()
    param_node.set('name', args.param)

    # unique_values = set(val for val in matched_dict.values())
    for matched in set(matched_dict):
        new_item = etree.SubElement(param_node, fixtag("nhdl", "lookup"))
        if matched:
            new_item.set('string', matched)
        if matched_dict[matched].get("uri"):
            new_item.set('uri', matched_dict[matched].get("uri"))
        if matched_dict[matched].get("coords"):
            new_item.set('coordinates', matched_dict[matched].get("coords"))
        new_item.text = matched_dict[matched].get("label")
    outdata = etree.tostring(outfile)
    myfile = open("reconciled-" + args.reconciled, "wb")
    myfile.write(outdata)

if __name__ == "__main__":
    main()
