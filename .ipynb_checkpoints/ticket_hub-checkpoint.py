import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image
import numpy as np
from collections import ChainMap, defaultdict
import difflib
import altair as alt
import matplotlib.pyplot as plt
from operator import itemgetter
from datetime import datetime, timedelta
import openpyxl
import streamlit_shadcn_ui as ui
import random
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.stylable_container import stylable_container
from streamlit_option_menu import option_menu
from streamlit_elements import elements, mui, html, dashboard
from fpdf import FPDF
import base64
import matplotlib.image as mpimg
import re


### SET WEB APP CONFIGURATIONS

favicon = Image.open('data/images/club-cannon-icon-black')

st.set_page_config(page_title='Club Cannon Ticket Hub', 
                  layout='wide',
				  page_icon=favicon,
				  initial_sidebar_state='collapsed')

### LOAD HEADER IMAGE
@st.cache_data
def load_image(path):
    return Image.open(path)

image = load_image('data/images/club-cannon-logo-bbb.png')


### DISPLAY HEADER IMAGE    
col1, col2, col3 = st.columns(3)
col2.image(image, 
        use_container_width=True)

@st.cache_data
def load_bg(path):
    return mpimg.imread(path)
    
bg_image = load_bg('data/images/club-cannon-icon-black.png')


### LOAD IN FILES
sho = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSclmO1idctTSOMkSdjnD5CaC0fyIjge0mZLC7QNc0IUdFmF_PQz8QpG2TDZIqvv7XTuYZ9HHYzADkR/pub?output=xlsx"
handheld = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTGAQzhxahfwfOntAvvkV0zmYdvH330TKkVZjA0ziU-EMPjvU_qWjdJIQz8OtpNYtsOT7EmusxCPcP9/pub?output=xlsx"
button = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR6wxi0QWMr1NGU4Ox0rVM-r0zZMSSFjLvXxCB-Fo2PGIHZCQ4dgxXNgpgWrirbvIe8cM19F8iacTqS/pub?output=xlsx"
jets = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQYE7Rq_D1K4BrLm6Me14OvVVXGTpBsGQjl_-XBgRS7JrSUm7kiS09Gn2wqNsAdLAceqfOedy-5VpEj/pub?output=xlsx"
led = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRDsxtI4mbdPGEwjECodc8nutJdVJDwRWiZOC1KHMG18hkiaLm1ZPUVQlGNgAmWupn-PzSNNiY1NuBo/pub?output=xlsx"


### CREATE UNIQUE CUSTOMER LIST
@st.cache_data
def load_customers(path):

    df = pd.read_excel(path, usecols=['Customer'])['Customer']

    return df

df = load_customers('data/files/SOD 2.18.26.xlsx')


### CORRECT NAME DISCREPENCIES IN CUSTOMER LIST
CUSTOMER_MAP = {
    'Tim Doyle': 'Timothy Doyle',
    'ESTEFANIA URBAN': 'Estefania Urban',
    'estefania urban': 'Estefania Urban',
    'JR Torres': 'Jorge Torres',
    'Saul Dominguez': 'Coco Bongo',
    'Paul Souza': 'Pyro Spectaculars Industries, Inc.',
    'Pyro Spectaculars Industries, Inc. ': 'Pyro Spectaculars Industries, Inc.',
    'CHRISTOPHER BARTOSIK': 'Christopher Bartosik',
    'Jon Ballog': 'Blair Entertainment / Pearl AV',
    'Jon ballog': 'Blair Entertainment / Pearl AV',
    'Jack Bermo': 'Jack Bermeo',
    'Tonz of Fun': 'Eric Walker',
    'Travis S. Johnson': 'Travis Johnson',
    'Yang Gao': 'Nebula NY',
    'Adam Stipe': 'Special Event Services (SES)',
    'Michael Brammer': 'Special Event Services (SES)',
    'ffp effects inc c/o Third Encore': 'FFP FX',
    'Disney Worldwide Services, Inc': 'Disney Cruise Line',
    'Jeff Meuzelaar / Pinnacle Productions': 'Jeff Meuzelaar',
    'Creative Production & Design': 'Justin Jenkins',
    'Justin Jenkins / Creative Production & Design': 'Justin Jenkins',
    'Andrew Pla / Rock The House': 'Steve Tanruther / Rock The House',
    'Ryan Konikoff / ROCK THE HOUSE': 'Steve Tanruther / Rock The House',
    'Cole M. Blessinger': 'Cole Blessinger',
    'Parti Line International, LLC': 'Fluttter Feti',
    'MICHAEL MELICE': 'Michael Melice',
    'Michael Brammer / Special Event Services': 'Special Event Services (SES)',
    'Dios Vazquez ': 'Dios Vazquez',
    'Brilliant Stages Ltd T/A TAIT': 'Brilliant Stages',
    'San Clemente High School Attn Matt Reid': 'Matthew Reid',
    'Anita Chandra / ESP Gaming': 'Anita Chandra',
    'randy hood': 'Randy Hood',
    'Randy Hood / Hood And Associates / talent': 'Randy Hood',
    'Steve VanderHeyden (Band Ayd Event Group)': 'Steve Vanderheyden / Band Ayd Event Group',
    'Steve VanderHeyden': 'Steve Vanderheyden / Band Ayd Event Group',
    'Kyle Kelly': 'Special FX Rentals',
    'MARIE COVELLI': 'Marie Covelli',
    'Frank Brown': 'Frank Brown / Night Nation Run',
    'Matt Spencer / SDCM': 'Matt Spencer',
    'Solotech U.S. Corporation': 'Solotech',
    'Michael Bedkowski': 'POSH DJs',
    'Kyle Jonas': 'POSH DJs',
    'Evan Ruga': 'POSH DJs',
    'Sean Devaney': 'POSH DJs',
    'Brian Uychich': 'POSH DJs',
    'Omar Sánchez Jiménez / Pyrofetti FX': 'Pyrofetti Efectos Especiales SA de CV',
    'Omar Sánchez Jiménez / Pyrofetti Fx': 'Pyrofetti Efectos Especiales SA de CV',
    'Omar Jimenez / Pyrofetti efectos especiales': 'Pyrofetti Efectos Especiales SA de CV',
    'Oscar Jimenez / Pyrofetti Fx': 'Pyrofetti Efectos Especiales SA de CV',
    'Gilbert / Pyrotec Sa': 'Pyrofetti Efectos Especiales SA de CV',
    'Gilbert / Pyrotec S.A.': 'Pyrofetti Efectos Especiales SA de CV',
    'Gilbert Salazar / Pyrotec S.A.': 'Pyrofetti Efectos Especiales SA de CV',
    'Image SFX (Gordo)': 'Image SFX',
    'Image SFX (Drake 6 Jets)': 'Image SFX',
    'Image SFX (Drake 18 Jets)': 'Image SFX',
    'Image SFX (Water Cannon Deposit)': 'Image SFX',
    'Shadow Mountain Productions': 'Tanner Valerio',
    'Tanner Valerio / Shadow Mountain Productions': 'Tanner Valerio',
    'Tanner Valero': 'Tanner Valerio',
    'Tanner Valerio / Shadow Mountain Productions (GEAR TO RETURN)': 'Tanner Valerio',
    'Tanner Valerio / Shadow Mountain productions (GEAR TO RETURN)': 'Tanner Valerio',
    'Tanner Valerio / Shadow Mountain productions': 'Tanner Valerio',
    'Blast Pyrotechnics': 'Blaso Pyrotechnics',
    'Pyrotecnico ': 'Pyrotecnico',
    'PYROTECNICO ': 'PYROTECNICO',
    'Pyrotecnico': 'PYROTECNICO',
    'Pyrotek FX ': 'Pyrotek FX',
    'Pyrotek Fx ': 'Pyrotek Fx',
    'Pyro Spectacular Industries': 'Pyro Spectaculars Industries, Inc.',
    'SK PYRO SPECIAL EFFECTS': 'SK Pyro Special Effects',
    'Illuminated Integration / Nashville Live': 'Illuminated Integration',
    'edgar guerrero': 'Edgar Guerrero',
    'HEDGER SANCHEZ': 'Hedger Sanchez',
    'Gear Club Direct Pro - Luis Garcia': 'Gear Club Direct',
    'edgar Rojas': 'Edgar Rojas',
    'Grant ashling': 'Grant Ashling',
    'Sebastian Gomez': 'Sebastian Gómez',
    'Ravinder singh': 'Ravinder Singh',
    'Eric Swanson / Slightly Stoopid': 'Slightly Stoopid',
    'the bouffants / David Griffin': 'David Griffin',
    'Anthony Mendoza (Infusion Lounge)': 'Anthony Mendoza',
    'The Party Stage Company / Ryan Smith': 'Ryan Smith',
    'Rafael Urban (Re-ship charge)': 'Rafael Urban',
    'California Pro Sound And Light': 'California Pro Sound and Light',
    'Max Moussier / Sound Miami Nightclub': 'Max Moussier',
    'Tony Tannous (Sound Agents Australia)': 'Tony Tannous',
    'Carlos BURGOS': 'Carlos Burgos',
    'Jonathan / Visual Edge': 'Visual Edge',
    'David Belogolovsky (6 solenoids)': 'David Belogolovsky',
    'amar gill': 'Amar Gill',
    'ARIEL MARTINEZ': 'Ariel Martinez',
    'JOSE ANTONIO MAR HERNANDEZ': 'Jose Antonio Mar Hernandez',
    'Alma Delia Rivero Sánchez': 'Alma Delia Rivero Sanchez',
    'PROMEDSA': 'Promedsa',
    'JABARI JOHNSON': 'Jabari Johnson',
    'Paul Klassenn / Laird FX': 'Paul Klaassen / Laird FX',
    'Parag Enterprises / Divine FX': 'Divine FX',
    'Romin Zandi ': 'Romin Zandi',
    'Romin Zandi (Personal)': 'Romin Zandi',
    'cesar palomino': 'Cesar Palomino',
    'zcibeiro Medina': 'Zcibeiro Medina',
    'Gregory Lomangino': 'Greg Lomangino',
    'Rory McElroy ': 'Rory McElroy',
    'Ronald Michel ': 'Ronald Michel',
    'Roland Mendoza': 'Rolando Mendoza',
    'rolando mendoza': 'Rolando Mendoza',
    'Rochester Red Wings / Morrie': 'Morrie Silver',
    'ROBERT SIMPSON': 'Robert Simpson',
    'ER Productions (Device programmer)': 'ER Productions',
    'University of Wyoming / Shelley': 'University of Wyoming',
    'Mario moreno': 'Mario Moreno',
    'gregory morris': 'Gregory Morris',
    'preston M Murray': 'Preston M Murray',
    'Jorge Pulido Ayala / MIA Eventos': 'Jorge Ayala',
    'Jorge Pulido Ayala': 'Jorge Ayala',
    'Jorge Ayala / MIA Eventos': 'Jorge Ayala',
    'Garth Hoffmann ': 'Garth Hoffmann',
    'Ernesto Koncept Systems / Khalil': 'Ernesto Koncept Systems',
    'jose ramos': 'Jose Ramos',
    'RAMON': 'Ramon',
    '4WALL ENTERTAINMENT, INC. ': '4WALL ENTERTAINMENT, INC.',
    'alex allen': 'Alex Allen',
    'Advanced Entertainment Services ': 'Advanced Entertainment Services',
    'adrian zerla': 'Adrian Zerla',
    'Anthony LoBosco': 'Anthony Lobosco',
    'ANTHONY DAMPLO': 'Anthony Damplo',
    'matthew reid': 'Matthew Reid',
    'Matt Reid': 'Matthew Reid',
    'PROVIDE CO.,LTD.': 'Provide Co., LTD',
    'Gear Club Direct ': 'Gear Club Direct',
    'Cole bibler': 'Cole Bibler',
    'cole bibler': 'Cole Bibler',
    'juan gil': 'Juan Gil',
    'juan mora': 'Juan Mora',
    'LEGACY MARLEY': 'Legacy Marley',
    'Ben steele': 'Ben Steele',
    'Benjamin Steele': 'Ben Steele',
    'Marisol Padilla Padilla': 'Marisol Padilla',
    'Bes Entertainment / Matt Besemer': 'Matt Besemer',
    'John Wright / Valdosta State University': 'John Wright',
    'Valdosta University': 'John Wright',
    'Deep South Productions ': 'Deep South Productions',
    'Sean Weaver / David Hays / Boland FX': 'Sean Weaver',
    'Sean Weaver / Universal Studios Orlando': 'Sean Weaver',
    'DEYRON BELL': 'Deyron Bell',
    'Toucan Productions, Inc.': 'Toucan Productions',
    'Pro FX Inc': 'Pro FX',
    'SMG Events / Adam Lucero ': 'SMG Events',
    'SMG Events / Adam Lucero': 'SMG Events',
    'SMG Events/Adam Lucero ': 'SMG Events',
    'SMG Events/Adam Lucero': 'SMG Events',
    'MICHAEL GREENBERG': 'Michael Greenberg',
    'ADAM MORGAN': 'Adam Morgan',
    'Complete Production Resources ': 'Complete Production Resources',
    'James Kerns': 'James Mitchell Kerns',
    '4wall entertainment LLC': '4WALL ENTERTAINMENT, INC.',
    '4Wall Entertainment, LLC': '4WALL ENTERTAINMENT, INC.'
}

@st.cache_data
def normalize_customers(s: pd.Series) -> pd.Series:
    # light canonicalization first to catch spacing/case variance
    s2 = s.astype("string").str.strip()
    # apply explicit mapping exactly once
    s2 = s2.replace(CUSTOMER_MAP)
    return s2


### STANDARDIZE NAMES
df = normalize_customers(df)

### CREATE LIST OF UNIQUE CUSTOMERS
@st.cache_data
def gen_cust_list():
    customer_list = df.dropna().drop_duplicates().tolist()
    return customer_list

customer_list = gen_cust_list()
    
### CREATE DATAFRAMES FROM GOOGLE SHEETS
@st.cache_data
def load_file(file_link):

    df = pd.read_excel(file_link, dtype={'RMA#:': str, 'Serial Number:': str, 'Repair sales order #:': str}, engine="openpyxl")
    df['Customer:'] = normalize_customers(df['Customer:'])

    return df

df_sho = load_file(sho)
df_handheld = load_file(handheld)
df_button = load_file(button)
df_jets = load_file(jets)
df_led = load_file(led)


# MERGE DATA INTO A SINGLE DATAFRAME

master_cols = ["Today's date:", 'Customer:', 'RMA#:', 'Select product:', 'Serial Number:', 'What is the issue?', 'Parts used in repair:', 'Testing:', 'How long did the repair take?', 'Please provide any other relevant info here:', 'Repair sales order #:', 'Extra 1', 'Extra 2', 'Extra 3']  

@st.cache_data
def merge_df():
    merged_df = pd.concat([df_sho, df_handheld, df_button, df_jets, df_led], ignore_index=True)
    return merged_df

merged_df = merge_df()

cols_to_clean = ['RMA#:', 'Serial Number:', 'Repair sales order #:']

def clean_preserve_string(x):
    if pd.isna(x):
        return pd.NA
    x_str = str(x).replace(',', '').strip()
    if re.fullmatch(r'\d+', x_str):
        return x_str  # Return as string to preserve leading zeros
    return x  # Return original if not all digits

@st.cache_data
def clean_cols(df):
    for col in cols_to_clean:
        if col in df.columns:
            df[col] = df[col].apply(clean_preserve_string)

    return df

merged_df = clean_cols(merged_df)

### DROP GOOGLE SHEETS ENTRY TIMESTAMP
merged_df.drop(columns='Timestamp', inplace=True)


### CREATE LIST OF CUSTOMERS IN RMA DATABASE
rma_customer_list = merged_df['Customer:'].tolist()

customers = list(set(customer_list + rma_customer_list))
    
# DEFINE PRODUCT LIST
products = ['Choose your product', 'Shomaster', 'Shostarter', 'The Button', 'Pro Jet', 'Micro Jet MKII', 'Quad Jet', 'Cryo Clamp', 'DMX Jet MKI', 'DMX Jet MKII', 'Power Jet', 'Handheld MKI', 'Handheld MKII', 'LED Attachment', 'Other']

### CREATE SEARCH FUNCTION

search_functions = ['Customer', 'RMA#', 'Serial#', 'Product', 'Date']

col1, col2, col3 = st.columns([.25, .5, .25])


col2.header('Ticket Hub')


with col2:
    search_type = st.multiselect('', options=search_functions, max_selections=1, placeholder='Search Type')
    st.divider()


### DEFINE SEARCH-TYPE VIEWS

# CUSTOMER
def show_customer():

    ### CHANGE DATETIME TO DATE
    merged_df["Today's date:"] = merged_df["Today's date:"].dt.date
    
    st.subheader('Customer Search')
    customer = st.multiselect('Enter Customer', customers, max_selections=1)
    st.header('')
    
    if customer:
        if customer[0] in customers or any(customer[0] in s for s in customers):
            results = merged_df[merged_df['Customer:'].str.contains(customer[0], case=False, na=False)]
            if not results.empty:
                for _, row in results.iterrows():
                    with st.expander(f"{row.get('Customer:', 'Unknown')} | {row.get('Select product:', '')}"):
                        for col in merged_df.columns:
                            # skip "Timestamp"
                            if col == "Timestamp":
                                continue
                            # skip Extra columns if they are empty
                            if col.startswith(("Extra", "Please")) and (pd.isna(row[col]) or str(row[col]).strip() == ""):
                                continue
                            # otherwise display
                            st.markdown(f"<u><b>{col}</b></u> {row[col]}", unsafe_allow_html=True)
        else:
            st.write('Sorry, no matching results were found.')
        

# RMA#
def show_rma():

    ### CHANGE DATETIME TO DATE
    merged_df["Today's date:"] = merged_df["Today's date:"].dt.date
    
    st.subheader('RMA Search')
    rma_num = st.text_input('Enter RMA#')
    st.header('')

    if rma_num:
        results = merged_df[merged_df['RMA#:'].str.contains(rma_num, case=False, na=False)]
        if not results.empty:
            for _, row in results.iterrows():
                with st.expander(f"{row.get('Customer:', 'Unknown')} | {row.get('Select product:', '')}"):
                    for col in merged_df.columns:
                        # skip "Timestamp"
                        if col == "Timestamp":
                            continue
                        # skip Extra columns if they are empty
                        if col.startswith(("Extra", "Please")) and (pd.isna(row[col]) or str(row[col]).strip() == ""):
                            continue
                        # otherwise display
                        st.markdown(f"<u><b>{col}</b></u> {row[col]}", unsafe_allow_html=True)
        else:
            st.write('Sorry, no matching results were found.')

# SERIAL#
def show_serial():

    ### CHANGE DATETIME TO DATE
    merged_df["Today's date:"] = merged_df["Today's date:"].dt.date
    
    st.subheader('Serial Number Search')
    serial_num = st.text_input('Enter Serial#')
    st.header('')
    
    if serial_num:
        results = merged_df[merged_df['Serial Number:'].str.contains(serial_num, case=False, na=False)]
        if not results.empty:
            for _, row in results.iterrows():
                with st.expander(f"{row.get('Customer:', 'Unknown')} | {row.get('Select product:', '')}"):
                    for col in merged_df.columns:
                        # skip "Timestamp"
                        if col == "Timestamp":
                            continue
                        # skip Extra columns if they are empty
                        if col.startswith(("Extra", "Please")) and (pd.isna(row[col]) or str(row[col]).strip() == ""):
                            continue
                        # otherwise display
                        st.markdown(f"<u><b>{col}</b></u> {row[col]}", unsafe_allow_html=True)     
        else:
            st.write('Sorry, no matching results were found.')

# PRODUCT
def show_product():

    ### CHANGE DATETIME TO DATE
    merged_df["Today's date:"] = merged_df["Today's date:"].dt.date
    
    st.subheader('Product Search')
    product = st.selectbox('Select product', products, placeholder='Choose your product')
    st.header('')

    if product != 'Choose your product':
        product_choice = merged_df[merged_df['Select product:'].str.contains(product, case=False, na=False)]
        if not product_choice.empty:
            for _, row in product_choice.iterrows():
                with st.expander(f"{row.get('Customer:', 'Unknown')} | {row.get('Select product:', '')}"):
                    for col in merged_df.columns:
                        # skip "Timestamp"
                        if col == "Timestamp":
                            continue
                        # skip Extra columns if they are empty
                        if col.startswith(("Extra", "Please")) and (pd.isna(row[col]) or str(row[col]).strip() == ""):
                            continue
                        # otherwise display
                        st.markdown(f"<u><b>{col}</b></u> {row[col]}", unsafe_allow_html=True)
                
# DATE
def show_date():
    
    st.subheader('Date Search')
    date = st.date_input('Select date')
    st.header('')

    if date:
        # Ensure the column name is quoted properly
        filtered_df = merged_df[merged_df["Today's date:"] == pd.to_datetime(date)]
        if not filtered_df.empty:
            for _, row in filtered_df.iterrows():
                with st.expander(f"{row.get('Customer:', 'Unknown')} | {row.get('Select product:', '')}"):
                    for col in merged_df.columns:
                        # skip "Timestamp"
                        if col == "Timestamp":
                            continue
                        # skip Extra columns if they are empty
                        if col.startswith(("Extra", "Please")) and (pd.isna(row[col]) or str(row[col]).strip() == ""):
                            continue
                        # otherwise display
                        st.markdown(f"<u><b>{col}</b></u> {row[col]}", unsafe_allow_html=True)
        else:
            st.write('No matching records found.')


### MENU OPTIONS

pages = {
    'Customer': show_customer, 
    'RMA#': show_rma,
    'Serial#': show_serial,
    'Product': show_product,
    'Date': show_date,
}

### DISPLAY SELECTION

if search_type:
    for selected in search_type:
        with col2:
            pages[selected]()

















