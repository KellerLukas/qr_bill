import os
from uuid import uuid4

class TempFile:
    def __init__(self, suffix: str):
        self.suffix = suffix
        self.name =  f"{str(uuid4())}.{self.suffix}"

    def __del__(self):
        try:
            os.remove(self.name)
        except: 
            pass