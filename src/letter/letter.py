import re
import os
import subprocess
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from src.bill.bill import Bill
from src.utils.temp_file import TempFile
from src.utils.company_address import Company
from src.config.paths import TEX_PATH

AVAILABLE_PLACEHOLDERS = ['dcombined_name', 'dstreet', 'dcity', 'dhouse_num', 'date', 'title', 'subtitle', 'salutation', 'text', 'bill_path', 'files_path']


class LetterMeta(BaseModel):
    title: str
    subtitle: str
    salutation: str
    text: str
    creditor: Company
    debtor: Company
    amount: str
    currency: Optional[str] = "CHF"
    reference_number: Optional[str] = None
    additional_information: Optional[str] = None
    language: Optional[str] = "de"
    


class Letter:
    def __init__(self, meta: LetterMeta, template_tex: str, out_path:str = ""):
        self.meta = meta
        self.bill = Bill(creditor=self.meta.creditor, 
                         amount=self.meta.amount,
                         currency=self.meta.currency,
                         debtor=self.meta.debtor,
                         reference_number=self.meta.reference_number,
                         additional_information=self.meta.additional_information,
                         language=self.meta.language)
        self.out_path = out_path
        self.template_tex = self._convert_tex_template_to_fstring(template_tex)
    
    
    def to_pdf(self):
        temp_file = TempFile("pdf")
        self.bill.to_pdf(temp_file.name, full_page=False)
        combined_name = self.bill.creditor.company
        if self.bill.debtor.name:
            combined_name += f"\\\\{self.bill.debtor.name}"
        tex_content = self.template_tex.format(dcombined_name=combined_name,
                                    dstreet=self.bill.debtor.street,
                                    dhouse_num=self.bill.debtor.house_num,
                                    dcity=self.bill.debtor.city,
                                    date=datetime.now().strftime("%d.%m.%Y"),
                                    title=self.meta.title,
                                    subtitle=self.meta.subtitle,
                                    salutation=self.meta.salutation,
                                    text=self.meta.text,
                                    bill_path=temp_file.name,
                                    files_path=os.path.join(os.path.dirname(__file__), "templates", "files"))
        self._compile_latex(tex_content)
        
    def _format_tex_template(self, template: str, **kwargs) -> str:
        fstring = self._convert_tex_template_to_fstring(template=template)
        for kwarg in kwargs:
            if self._has_lb_placeholder(kwarg):
                pass
        
    def _has_lb_placeholder(self, template: str, placeholder: str) -> bool:
        return f"{placeholder}__lb" in template
        
    def _convert_tex_template_to_fstring(self, template: str) -> str:
        """
        takes proper LaTex file with placeholders in the format "XXVARIABLE". 
        Escapes all curly brackets {} -> {{}} and replaces
        XXVARIABLE by {variable}
        """
        template = template.replace("{","{{")
        template = template.replace("}","}}")
        
        pattern = "XX[A-Z_]+"
        matches = re.findall(pattern, template)
        
        for match in set(matches):
            placeholder = match[2:].lower()
            if placeholder not in AVAILABLE_PLACEHOLDERS:
                raise ValueError(f"Template contains unknown placeholder: {match}")
            template = template.replace(match, f"{{{placeholder}}}")
        return template
        
        
    def _compile_latex(self, tex_string: str):
        temp_file = TempFile("tex")
        with open (temp_file.name, "w") as file:
            file.write(tex_string)
            file.close()
        file_name = self._create_filename()
        for _ in range(2): #run twice to get the correct placement of the bill
            subprocess.run([TEX_PATH, temp_file.name,'-output-directory', self.template_tex]) 
        if self.out_path:
            os.makedirs(self.out_path,exist_ok=True)
        os.rename(temp_file.name.replace("tex","pdf"), os.path.join(self.out_path, file_name))
        self._cleanup_tex_files(temp_file.name)
        
    def _create_filename(self):
        name_underscore = self.bill.debtor.company.replace(' ','_')
        special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('é'):'e',
                        ord('è'):'e', ord('ë'):'e', ord('\n'):'?'}
        clean_name = name_underscore.translate(special_char_map)
        filename = f"{clean_name}_{datetime.now().strftime("%Y-%m-%d")}.pdf"
        return filename
    
    def _cleanup_tex_files(self, tex_filename: str):
        tex_suffixes = ["log", "aux"]
        for suffix in tex_suffixes:
            try:
                os.remove(tex_filename.replace("tex", suffix))
            except:
                pass
    
