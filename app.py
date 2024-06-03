import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

# Autenticación de Google Drive
@st.experimental_singleton
def authenticate():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build('drive', 'v3', credentials=credentials)

drive_service = authenticate()

def load_data(drive_service, folder_id):
    query = f"'{folder_id}' in parents and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
    results = drive_service.files().list(q=query).execute()
    items = results.get('files', [])
    
    data = []
    file_names = []

    for item in items:
        file_id = item['id']
        file_name = item['name']
        request = drive_service.files().get_media(fileId=file_id)
        file_data = request.execute()
        with open(file_name, "wb") as f:
            f.write(file_data)
        data.append(pd.read_excel(file_name))
        file_names.append(file_name)

    return data, file_names

folder_id = '1uHfThsP-2xmFZzDBvQH_m1t6_QWfM6YT'
data, file_names = load_data(drive_service, folder_id)

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
        st.write(f"Resultados de {file_names[i]}")
        st.write(df)
