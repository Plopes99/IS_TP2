import xml.etree.ElementTree as ET

from functions.entities.disaster import Disaster


class Country:

    def __init__(self, name):
        Country.counter += 1
        self._id = Country.counter
        self._name = name
        self._disasters = []

    def to_xml(self):
        el = ET.Element("Country")
        el.set("id", str(self._id))
        el.set("name", self._name)

        disasters_el = ET.Element("Disasters")
        for disaster in self._disasters:
            disasters_el.append(disaster.to_xml())

        el.append(disasters_el)
        return el

    def add_disaster(self, disaster: Disaster):
        self._disasters.append(disaster)

    def get_id(self):
        return self._id

    def __str__(self):
        return f"name: {self._name}, id:{self._id}"


Country.counter = 0
