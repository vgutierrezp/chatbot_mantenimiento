import streamlit as st
from google.oauth2 import service_account
import gspread
import pandas as pd
from gspread_dataframe import get_as_dataframe

# Autenticación de Google Sheets
@st.experimental_singleton
def authenticate():
    credentials = service_account.Credentials.from_service_account_info(st.secrets["gdrive"])
    client = gspread.authorize(credentials)
    return client

drive_service = authenticate()

# Cargar datos desde Google Sheets
def load_data(sheet_id):
    sheet = drive_service.open_by_key(sheet_id)
    worksheet_list = sheet.worksheets()
    data = []
    sheet_names = []

    for worksheet in worksheet_list:
        df = get_as_dataframe(worksheet)
        data.append(df)
        sheet_names.append(worksheet.title)

    return data, sheet_names

sheet_id = '1uHfThsP-2xmFZzDBvQH_m1t6_QWfM6YT'
data, sheet_names = load_data(sheet_id)

st.title("Chatbot de Mantenimiento")
st.write("Este chatbot te ayudará a consultar información de mantenimiento preventivo.")
st.write("Por favor, ingresa al menos uno de los filtros: Mes, Marca, Tienda o Familia.")

mes = st.text_input("Ingresa el mes:")
marca = st.text_input("Ingresa la marca:")
tienda = st.text_input("Ingresa la tienda:")
familia = st.text_input("Ingresa la familia:")

# Lógica para filtrar los datos según los inputs
for i, df in enumerate(data):
    if mes:
        df = df[df['Mes'] == mes]
    if marca:
        df = df[df['Marca'] == marca]
    if tienda:
        df = df[df['Tienda'] == tienda]
    if familia:
        df = df[df['Familia'] == familia]

    if not df.empty:
        st.write(f"Resultados de {sheet_names[i]}")
        st.write(df)
