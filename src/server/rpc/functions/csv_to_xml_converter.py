import xml.dom.minidom as md
import xml.etree.ElementTree as ET

from functions.csv_reader import CSVReader
from functions.entities.country import Country
from functions.entities.disaster import Disaster
from functions.entities.category import Category


class CSVtoXMLConverter:

    def __init__(self, path):
        self._reader = CSVReader(path)

    def to_xml(self):

        # read countries
        countries = self._reader.read_entities(
            attr="Country",
            builder=lambda row: Country(row["Country"])
        )

        # read categories
        categories = self._reader.read_entities(
            attr="category",
            builder=lambda row: Category(row["category"])
        )

        # read disasters
        def after_creating_disaster(disaster, row):
            # add the disaster to the appropriate country
            countries[row["Country"]].add_disaster(disaster)

        self._reader.read_entities(
            attr="date",
            builder=lambda row: Disaster(
                date=row["date"],
                aircraft_type=row["Air-craft type"],
                operator=row["operator"],
                fatalities=row["fatilites"],
                category_code=row["category"]
            ),
            after_create=after_creating_disaster
        )

        # generate the final xml
        root_el = ET.Element("airplane_disasters")

        for category in categories.values():
            category_el = ET.Element("category")
            category_el.set("name", category._code)
            category_el.set("accident_type", category._accident_type)
            category_el.set("damage_type", category._damage_type)

            for country in countries.values():
                country_el = ET.Element("country")
                country_el.set("name", country._name)

                for disaster in country._disasters:
                    if disaster._category_code == category._code:
                        disaster_el = ET.Element("disaster")
                        disaster_el.append(ET.Element("date", text=disaster._date))
                        disaster_el.append(ET.Element("aircraft_type", text=disaster._aircraft_type))
                        disaster_el.append(ET.Element("operator", text=disaster._operator))
                        disaster_el.append(ET.Element("fatalities", text=str(disaster._fatalities)))

                        country_el.append(disaster_el)

                category_el.append(country_el)

            root_el.append(category_el)

        return root_el

    def to_xml_str(self):
        xml_tree = self.to_xml()
        xml_str = ET.tostring(xml_tree, encoding='utf-8', method='xml').decode()

        dom = md.parseString(xml_str)
        return dom.toprettyxml()

