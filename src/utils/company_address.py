from typing import Optional
from pydantic import BaseModel
from qrbill.bill import StructuredAddress

class Company(BaseModel):
    display_name: Optional[str] = None
    company: str
    name: str = ""
    street: str
    house_num: str
    pcode: str
    city: str
    country: Optional[str] = "CH"
    account: Optional[str] = None
    _structured_address: StructuredAddress = None
    
    @property
    def structured_address(self):
        if self._structured_address is None:
            self._structured_address = StructuredAddress(name=self.company, street=self.street, house_num=self.house_num, pcode=self.pcode, city=self.city, country=self.country)
        return self._structured_address
    
    def __str__(self):
        if self.display_name is None:
            return self.company
        return self.display_name
    
        
    