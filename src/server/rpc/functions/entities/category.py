import xml.etree.ElementTree as ET

from functions.entities.country import Country

class Category:
    def __init__(self, code):
        self._code = code
        self._accident_type, self._damage_type = self.get_category_types(code)
        self._countries = []

    def get_category_types(self, code):
        accident_types = {
            'A': 'Accident',
            'I': 'Incident',
            'H': 'Hijacking',
            'C': 'Criminal occurrence',
            'O': 'Other occurrence',
            'U': 'Type of occurrence unknown'
        }
        damage_types = {
            '1': 'Hull-loss',
            '2': 'Repairable damage'
        }

        accident_type = accident_types.get(code[0], 'Unknown') if code else 'Unknown'  # Evita IndexError
        damage_type = damage_types.get(code[1], 'Unknown') if code else 'Unknown'  # Evita IndexError

        return accident_type, damage_type

    def to_xml(self):
        el = ET.Element("Category")
        el.set("Accident Types", self._accident_type)
        el.set("Damage Types", self._damage_type)

        countries_el = ET.Element("Countries")
        for country in self._countries:
            countries_el.append(country.to_xml())

        el.append(countries_el)
        return el

    def add_country(self, country:Country):
        self._countries.append(country)

    def __str__(self):
        return f"{self._code}, Accident Type:{self._accident_type}, Damage Type:{self._damage_type}, "


Category.counter = 0
