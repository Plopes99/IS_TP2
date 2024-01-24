import base64
from io import BytesIO
from lxml import etree


def validator(xml_path, xsd_path) -> bool:
    decoded_content = base64.b64decode(xml_path.data)
    xml_data = BytesIO(decoded_content)

    xmlschema_doc = etree.parse(xsd_path)
    xmlschema = etree.XMLSchema(xmlschema_doc)

    xml_doc = etree.parse(xml_data)
    result = xmlschema.validate(xml_doc)

    return result