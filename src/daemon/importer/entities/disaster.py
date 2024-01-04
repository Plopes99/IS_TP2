import xml.etree.ElementTree as ET


class Disaster:
    def __init__(self, date, aircraft_type, operator, fatalities, category_code):
        self._date = date
        self._aircraft_type = aircraft_type
        self._operator = operator
        self._fatalities = fatalities
        self._category_code = self.validate_set(category_code)

    def to_xml(self):
        el = ET.Element("Disaster")
        el.set("Date", self._date)
        el.set("Aircraft Type", self._aircraft_type)
        el.set("Operator", self._operator)
        el.set("Fatalities", self._fatalities)
        el.set("Category Code", self._category_code)
        return el

    def validate_set(self, value):
        return value if value else "Unknown"

