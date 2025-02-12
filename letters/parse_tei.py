import os
import json
from lxml import etree

NS = {'tei': 'http://www.tei-c.org/ns/1.0'}

def tei_node_to_html(node):
    """Recursively convert a TEI node to HTML, concatenating node.text and child.tail."""
    tag = etree.QName(node).localname
    result = node.text or ''

    for child in node:
        child_html = tei_node_to_html(child)
        result += child_html
        if child.tail:
            result += child.tail

    if tag == 'p':
        return f"<p>{result}</p>"
    elif tag == 'note':
        note_type = node.get('type', '')
        note_place = node.get('place', '')
        if note_type == 'comment' and note_place == 'bottom':
            note_text = ''.join(node.itertext()).strip()
            return f'<span class="tooltip-note" data-bs-toggle="tooltip" title="{note_text}">†</span>'
        return result
    elif tag in ('persName', 'placeName'):
        ref = node.get('ref', '')
        return f'<span class="{tag}" data-ref="{ref}">{result}</span>'
    elif tag == 'hi' and node.get('rend') == 'italic':
        return f'<em>{result}</em>'
    elif tag in ('closer', 'postscript', 'salute', 'dateline', 'signed'):
        return f'<div class="{tag}">{result}</div>'
    return result

def extract_letter_body(tree, subtype):
    """Extract the body for original or translation, avoiding duplication."""
    # Find <text> with @subtype=...
    text_nodes = tree.xpath(f"//tei:text[@subtype='{subtype}']", namespaces=NS)
    if text_nodes:
        # Grab the <body> within that text node
        body_nodes = text_nodes[0].xpath("./tei:body", namespaces=NS)
        if body_nodes:
            # Convert the entire <body> node to HTML once
            return tei_node_to_html(body_nodes[0])
        else:
            # If no <body>, just parse the entire <text>
            return tei_node_to_html(text_nodes[0])
    
    # If we didn't find <text subtype="original/translation">, fallback:
    # optionally check for @subtype on any TEI node
    alt_nodes = tree.xpath(f"//tei:*[@subtype='{subtype}']", namespaces=NS)
    if alt_nodes:
        return tei_node_to_html(alt_nodes[0])
    return None

#def extract_letter_body(tree, subtype):
 #   """Extract content based on subtype (e.g., original or translation)."""
  #  nodes = tree.xpath(f"//tei:text[@subtype='{subtype}']", namespaces=NS)
   # if nodes:
    #    body_divs = nodes[0].xpath(".//tei:body//tei:*", namespaces=NS)
     #   if body_divs:
      #      return ''.join(tei_node_to_html(child) for child in body_divs)
       # else:
        #    return ''.join(tei_node_to_html(child) for child in nodes[0])
    
    #nodes = tree.xpath(f"//tei:*[@subtype='{subtype}']", namespaces=NS)
    #if nodes:
     #   return ''.join(tei_node_to_html(child) for child in nodes[0])
    #return None

def extract_person(tree, xpath_expr):
    """Extract a person’s details using the provided XPath expression."""
    person_nodes = tree.xpath(xpath_expr, namespaces=NS)
    if person_nodes:
        node = person_nodes[0]
        forename = ' '.join(node.xpath("tei:forename/text()", namespaces=NS)).strip()
        surname = ' '.join(node.xpath("tei:surname/text()", namespaces=NS)).strip()
        nameLink = ' '.join(node.xpath("tei:nameLink/text()", namespaces=NS)).strip()
        roleName = ' '.join(node.xpath("tei:roleName/text()", namespaces=NS)).strip()
        return {
            "forename": forename,
            "surname": surname,
            "nameLink": nameLink,
            "roleName": roleName
        }
    return {}

def extract_languages(tree):
    """Extract language information from <langUsage>."""
    langs = tree.xpath("//tei:langUsage/tei:language/text()", namespaces=NS)
    langs = [lang.strip() for lang in langs if lang.strip()]
    return langs

def parse_single_file(file_path):
    tree = etree.parse(file_path)
    letter_id = os.path.splitext(os.path.basename(file_path))[0]

    def get_first(xpath_expr):
        result = tree.xpath(xpath_expr, namespaces=NS)
        if result:
            if isinstance(result[0], str):
                return ' '.join(result).strip()
            else:
                return result[0]
        return ""

    # Extract the first title from seriesStmt
    series_title = get_first("//tei:seriesStmt/tei:title[1]/text()")

    # --- Main title handling ---
    main_titles = tree.xpath("//tei:titleStmt/tei:title[@type='main']/text()", namespaces=NS)
    if len(main_titles) == 1:
        main_title = main_titles[0].strip()
        date_val = get_first("//tei:correspDesc/tei:correspAction[@type='sent']/tei:date/@when") or "Unbekannt"
        place_val = get_first("//tei:correspDesc/tei:correspAction[@type='sent']/tei:placeName//text()") or "Unbekannt"
    else:
        main_title = get_first("//tei:titleStmt/tei:title[@type='main'][@xml:lang='de']/text()")
        date_val = get_first("//tei:correspDesc/tei:correspAction[@type='sent']/tei:date/@when") or "Unbekannt"
        place_val = get_first("//tei:correspDesc/tei:correspAction[@type='sent']/tei:placeName//text()") or "Unbekannt"

    sub_title = get_first("//tei:titleStmt/tei:title[@type='sub'][@xml:lang='de']/text()")
    publisher = get_first("//tei:publicationStmt/tei:publisher/tei:orgName/text()")
    repository = get_first("//tei:sourceDesc/tei:msDesc/tei:msIdentifier/tei:repository/text()")
    collection = get_first("//tei:sourceDesc/tei:msDesc/tei:msIdentifier/tei:collection/text()")
    idno = get_first("//tei:sourceDesc/tei:msDesc/tei:msIdentifier/tei:idno/text()")
    
    original_html = extract_letter_body(tree, "original")
    translation_html = extract_letter_body(tree, "translation")

    has_volltext = bool(original_html and original_html.strip())
    has_uebersetzung = bool(translation_html and translation_html.strip())

    sender = extract_person(tree, "//tei:correspDesc/tei:correspAction[@type='sent']/tei:persName")
    receiver = extract_person(tree, "//tei:correspDesc/tei:correspAction[@type='received']/tei:persName")

    languages = extract_languages(tree)

    with open(file_path, "r", encoding="utf-8") as f:
        tei_xml = f.read()

    return {
        "id": letter_id,
        "seriesTitle": series_title,  # Added series title extraction
        "mainTitleDe": main_title,
        "subTitleDe": sub_title,
        "publisher": publisher,
        "repository": repository,
        "collection": collection,
        "idno": idno,
        "date": date_val,
        "place": place_val,
        "originalHtml": original_html,
        "translationHtml": translation_html,
        "hasVolltext": has_volltext,
        "hasUebersetzung": has_uebersetzung,
        "sender": sender,
        "receiver": receiver,
        "languages": languages,
        "teiXml": tei_xml
    }

def parse_tei_folder(folder_path):
    """Parse all TEI files in the given folder and update letters.json without overwriting."""
    letters = []
    
    if os.path.exists("letters.json"):
        with open("letters.json", "r", encoding="utf-8") as f:
            try:
                letters = json.load(f)
            except json.JSONDecodeError:
                letters = []

    existing_ids = {letter["id"] for letter in letters}

    new_letters = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            file_path = os.path.join(folder_path, filename)
            letter_data = parse_single_file(file_path)

            if letter_data["id"] not in existing_ids:
                new_letters.append(letter_data)

    if new_letters:
        letters.extend(new_letters)
        with open("letters.json", "w", encoding="utf-8") as f:
            json.dump(letters, f, ensure_ascii=False, indent=2)
        print(f"Added {len(new_letters)} new letters to letters.json")
    else:
        print("No new letters found.")

def main():
    folder_path = "data"
    parse_tei_folder(folder_path)

if __name__ == "__main__":
    main()