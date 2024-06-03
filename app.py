import streamlit as st
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pandas as pd

# Autenticación de Google Drive
@st.experimental_singleton
def authenticate():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    return GoogleDrive(gauth)

drive = authenticate()

def load_data(drive, folder_id):
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"}).GetList()
    data = []
    file_names = []

    for file in file_list:
        file.GetContentFile(file['title'])
        data.append(pd.read_excel(file['title']))
        file_names.append(file['title'])

    return data, file_names

folder_id = '1uHfThsP-2xmFZzDBvQH_m1t6_QWfM6YT'
data, file_names = load_data(drive, folder_id)

st.title("Chatbot de Mantenimiento")
st.write("Este chatbot te ayudará a consultar información de mantenimiento preventivo.")
st.write("Por favor, ingresa al menos uno de los filtros: Mes, Marca o Tienda.")

mes = st.text_input("Ingresa el mes:")
marca = st.text_input("Ingresa la marca:")
tienda = st.text_input("Ingresa la tienda:")

# Lógica para filtrar los datos según los inputs
for i, df in enumerate(data):
    if mes:
        df = df[df['Mes'] == mes]
    if marca:
        df = df[df['Marca'] == marca]
    if tienda:
        df = df[df['Tienda'] == tienda]

    if not df.empty:
        st.write(f"Resultados de {file_names[i]}")
        st.write(df)
