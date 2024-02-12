import decimal
from enum import Enum
from gettext import gettext
from typing import Optional
from uuid import UUID

from src.infrastructure.common.domain_model import DomainModel


class Category(Enum):
    SANDWICHES = 'SANDWICHES'
    HEALTHY = 'HEALTHY'
    PIZZA = 'PIZZA'
    JAPANESE = 'JAPANESE'
    SWEETS_AND_CAKES = 'SWEETS_AND_CAKES'
    ACAI = 'ACAI'
    ARABIC = 'ARABIC'
    ICE_CREAM = 'ICE_CREAM'
    ITALIAN = 'ITALIAN'
    BAKERY = 'BAKERY'
    CHINESE = 'CHINESE'
    GOURMET = 'GOURMET'
    FRIED_PASTRY = 'FRIED_PASTRY'
    MEAT = 'MEAT'
    SNACKS = 'SNACKS'
    PREPARED_MEAL = 'PREPARED_MEAL'

    def user_friendly_name(self):
        return {
            self.SANDWICHES: gettext('Sandwiches'),
            self.HEALTHY: gettext('Healthy'),
            self.PIZZA: gettext('Pizza'),
            self.JAPANESE: gettext('Japanese'),
            self.SWEETS_AND_CAKES: gettext('Sweets and Cakes'),
            self.ACAI: gettext('Acai'),
            self.ARABIC: gettext('Arabic'),
            self.ICE_CREAM: gettext('Ice Cream'),
            self.ITALIAN: gettext('Italian'),
            self.BAKERY: gettext('Bakery'),
            self.CHINESE: gettext('Chinese'),
            self.GOURMET: gettext('Gourmet'),
            self.FRIED_PASTRY: gettext('Fried Pastry'),
            self.MEAT: gettext('Meat'),
            self.SNACKS: gettext('Snacks'),
            self.PREPARED_MEAL: gettext('Prepared Meal'),
        }[self]


class Point(DomainModel):
    def __init__(self, latitude: decimal, longitude: decimal):
        self.latitude = latitude
        self.longitude = longitude


class State(Enum):
    SP = 'SP'
    RJ = 'RJ'
    MG = 'MG'
    RS = 'RS'
    SC = 'SC'
    PR = 'PR'
    ES = 'ES'
    BA = 'BA'
    CE = 'CE'
    PE = 'PE'
    PA = 'PA'
    MA = 'MA'
    GO = 'GO'
    AM = 'AM'
    PB = 'PB'
    RN = 'RN'
    AL = 'AL'
    MT = 'MT'
    DF = 'DF'
    MS = 'MS'
    SE = 'SE'
    RO = 'RO'
    TO = 'TO'
    AC = 'AC'
    AP = 'AP'
    RR = 'RR'

    def user_friendly_name(self):
        return {
            self.SP: gettext('São Paulo'),
            self.RJ: gettext('Rio de Janeiro'),
            self.MG: gettext('Minas Gerais'),
            self.RS: gettext('Rio Grande do Sul'),
            self.SC: gettext('Santa Catarina'),
            self.PR: gettext('Paraná'),
            self.ES: gettext('Espírito Santo'),
            self.BA: gettext('Bahia'),
            self.CE: gettext('Ceará'),
            self.PE: gettext('Pernambuco'),
            self.PA: gettext('Pará'),
            self.MA: gettext('Maranhão'),
            self.GO: gettext('Goiás'),
            self.AM: gettext('Amazonas'),
            self.PB: gettext('Paraíba'),
            self.RN: gettext('Rio Grande do Norte'),
            self.AL: gettext('Alagoas'),
            self.MT: gettext('Mato Grosso'),
            self.DF: gettext('Distrito Federal'),
            self.MS: gettext('Mato Grosso do Sul'),
            self.SE: gettext('Sergipe'),
            self.RO: gettext('Rondônia'),
            self.TO: gettext('Tocantins'),
            self.AC: gettext('Acre'),
            self.AP: gettext('Amapá'),
            self.RR: gettext('Roraima'),
        }[self]


class Address(DomainModel):
    def __init__(self, street: str, number: str, neighborhood: str, city: str, state: State,
                 zip_code: str, complement: Optional[str], point: Optional[Point]):
        self.street = street
        self.number = number
        self.neighborhood = neighborhood
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.complement = complement
        self.point = point


class Restaurant(DomainModel):
    def __init__(self, id: UUID, user_id: UUID, category: Category, name: str, address: Address,
                 document_number: str, logo_url: Optional[str], description: Optional[str]):
        self.id = id
        self.user_id = user_id
        self.category = category
        self.name = name
        self.address = address
        self.document_number = document_number
        self.logo_url = logo_url
        self.description = description
