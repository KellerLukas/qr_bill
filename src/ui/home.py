import streamlit as st
import pandas as pd
from src.ui.style import style
from src.letter.letter import Letter, LetterMeta
from src.utils.company_address import Company
from src.config.known_companies import KnownCreditors, KnownDebtors
from src.config.paths import OUTPUT_PATH

REQ_COLUMNS = ["Firma", "Name", "Anrede", "Betrag", "Ref-Nr", "Strasse", "Plz", "Nr", "Ort"]

def setup_page():
    st.set_page_config(page_title="TVW Billing Tool")
    st.markdown(style, unsafe_allow_html=True)


def configure_title():
    st.markdown("# TVW Billing Tool")
    st.markdown("Create QR Bills")
    
def configure_single_bill():
    st.markdown("## Create Single bill")
    st.markdown("### Creditor")
    creditor = select_company("Creditor")
    
    st.markdown("### Debtor")
    debtor = select_company("Debtor")
    
    st.markdown("### Content")
    title = st.text_input("Title:", value="", placeholder="Rechnung")
    subtitle = st.text_input("Subtitle:", value="")
    salutation = st.text_input("Salutation:", value="",)
    text = st.text_area("Text:", value="")
    amount = st.text_input("Amount:", value="")
    reference_number = st.text_input("Reference Number:", value="")
    additional_information = st.text_input("Additional Information:", value="")

    meta = LetterMeta(title=title,
                    subtitle=subtitle,
                    salutation=salutation,
                    text=text,
                    amount=amount,
                    reference_number=reference_number,
                    additional_information=additional_information,
                    creditor=creditor,
                    debtor=debtor)
    if st.button(label="Create"):
        create_bill(meta)
    
    # Section divider and spacing
    st.markdown('<div class="section-spacing"></div>', unsafe_allow_html=True)

def configure_bulk_bill():
    st.markdown("## Create Bills in Bulk ")
    uploaded_file = st.file_uploader("Upload CSV:", type="csv", accept_multiple_files=False)
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file, sep=";", dtype='string').fillna("")
        st.write(data)
        for col in REQ_COLUMNS:
            if col not in data.columns:
                raise ValueError(f"Column {col} is required!")
        st.markdown("### Creditor")
        creditor = select_company("Creditor")

        st.markdown("### Content")
        st.markdown(f"Available variables: {list(data.columns)}")
        title = st.text_input("Title:", value="", placeholder="Rechnung")
        subtitle = st.text_input("Subtitle:", value="")
        text = st.text_input("Text:", value="")
        additional_information = st.text_input("Additional Information:", value="")
        if st.button(label="Bulk Create"):
            create_bills_in_bulk(data, title=title, subtitle=subtitle, text=text, additional_information=additional_information, creditor=creditor)

    # Section divider and spacing
    st.markdown('<div class="section-spacing"></div>', unsafe_allow_html=True)

def create_bill(meta: LetterMeta):
    with open("src/letter/templates/template_tvw.tex") as f:
        template_tex = f.read()
    letter = Letter(meta=meta, template_tex=template_tex, out_path=OUTPUT_PATH)
    letter.to_pdf()
    st.toast(f"Created Bill for {meta.debtor.company}")

def create_bills_in_bulk(data: pd.DataFrame, creditor: Company, title: str, subtitle: str, text: str, additional_information: str):
    step = 1/len(data)
    current = 0
    progress_bar = st.progress(current)
    for idx in range(len(data)):
        row = data.loc[idx,:]
        current += step
        progress_bar.progress(current)
        debtor = Company(company=row["Firma"],
                         name=row["Name"],
                         street=row["Strasse"],
                         house_num=row["Nr"],
                         pcode=row["Plz"],
                         city=row["Ort"])
        meta = LetterMeta(title=title,
                    subtitle=subtitle.format(**row),
                    salutation=row["Anrede"],
                    text=text.format(**row),
                    amount=row["Betrag"],
                    reference_number=row["Ref-Nr"],
                    additional_information=additional_information.format(**row),
                    creditor=creditor,
                    debtor=debtor)
        create_bill(meta=meta)
    st.toast("Done creating Bills")
    
def select_company(type: str):
    if type not in ["Creditor", "Debtor"]:
        raise ValueError(f"Type must be Creditor or Debtor but is {type}")
    if type == "Creditor":
        options = list(KnownCreditors().__dict__.values())
    else:
        options = list(KnownDebtors().__dict__.values())
    options.append(f"New {type}")
    company = st.selectbox(f"Select {type}:", options)
    
    if company == f"New {type}":
        company = enter_new_company(type)
    return company

def enter_new_company(type: str):
    if type not in ["Creditor", "Debtor"]:
        raise ValueError(f"Type must be Creditor or Debtor but is {type}")
    company = st.text_input(f"{type} Company:", value="")
    name = st.text_input(f"{type} Name:", value="")
    street = st.text_input(f"{type} Street:", value="")
    house_num = st.text_input(f"{type} House Number:", value="")
    pcode = st.text_input(f"{type} Postal Code:", value="")
    city = st.text_input(f"{type} City:", value="")
    if type == "Creditor":
        account = st.text_input(f"{type} Account:", value="")
    else:
        account = None
    company = Company(company=company,
                    name=name,
                    street=street,
                    house_num=house_num,
                    pcode=pcode,
                    city=city,
                    account=account)
    return company
        
def main():
    setup_page()
    configure_title()
    tab_single, tab_bulk = st.tabs(["Single", "Bulk"])
    with tab_single:
        configure_single_bill()
    with tab_bulk:
        configure_bulk_bill()   

if __name__ == "__main__":
    main()