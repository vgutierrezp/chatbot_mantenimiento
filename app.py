import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
from io import BytesIO

# Autenticación con Google Drive
@st.experimental_singleton
def authenticate():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build('drive', 'v3', credentials=credentials)

drive_service = authenticate()

def load_data(drive_service, folder_id):
    file_list = drive_service.files().list(q=f"'{folder_id}' in parents and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'",
                                           fields="nextPageToken, files(id, name)").execute()
    data = []
    file_names = []
    
    for file in file_list.get('files', []):
        request = drive_service.files().get_media(fileId=file['id'])
        file_data = BytesIO(request.execute())
        data.append(pd.read_excel(file_data, sheet_name=None))
        file_names.append(file['name'])
    
    return data, file_names

folder_id = '1uHfThsP-2xmFZzDBvQH_m1t6_QWfM6YT'
data, file_names = load_data(drive_service, folder_id)

st.title("Chatbot de Mantenimiento")
st.write("Este chatbot te ayudará a consultar información de mantenimiento preventivo.")
st.write("Por favor, ingresa al menos uno de los filtros: Mes, Marca, Tienda o Familia.")

# Inputs para los filtros
mes = st.text_input("Ingresa el mes:")
marca = st.text_input("Ingresa la marca:")
tienda = st.text_input("Ingresa la tienda:")
familia = st.text_input("Ingresa la familia:")

# Lógica para filtrar los datos según los inputs
def filter_data(data, mes, marca, tienda, familia):
    filtered_data = []
    for df_dict in data:
        for sheet_name, df in df_dict.items():
            if mes:
                df = df[df['Mes'].str.contains(mes, case=False, na=False)]
            if marca:
                df = df[df['Marca'].str.contains(marca, case=False, na=False)]
            if tienda:
                df = df[df['Tienda'].str.contains(tienda, case=False, na=False)]
            if familia:
                df = df[df['Familia'].str.contains(familia, case=False, na=False)]
            
            if not df.empty:
                filtered_data.append(df)
    
    return pd.concat(filtered_data, ignore_index=True) if filtered_data else pd.DataFrame()

if mes or marca or tienda or familia:
    df_filtered = filter_data(data, mes, marca, tienda, familia)
    
    if not df_filtered.empty:
        columns_to_show = [
            "Mes", "Tienda", "Familia", "Tipo de Equipo", "Tipo de Servicio", "Ejecutor",
            "Frecuencia", "N° Equipos", "Ult.Prev.", "Prog.1", "Ejec.1",
            "CO", "CL", "IP", "RP"
        ]
        
        available_columns = [col for col in columns_to_show if col in df_filtered.columns]
        
        for col in ['Ult.Prev.', 'Prog.1', 'Ejec.1', 'CO', 'CL', 'IP', 'RP']:
            if col in df_filtered.columns:
                df_filtered[col] = pd.to_datetime(df_filtered[col], errors='coerce').dt.strftime('%d-%m-%Y')
        
        st.write(f"Datos filtrados para Mes: {mes or 'Todos'}, Marca: {marca or 'Todas'}, Tienda: {tienda or 'Todas'}, Familia: {familia or 'Todas'}")
        st.dataframe(df_filtered[available_columns])
        
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df_filtered[available_columns].to_excel(writer, index=False, sheet_name='Filtered Data')
        
        workbook = writer.book
        worksheet = writer.sheets['Filtered Data']
        format1 = workbook.add_format({'num_format': 'dd-mm-yyyy'})
        
        for col in ['CO', 'CL', 'IP', 'RP']:
            if col in df_filtered.columns:
                col_idx = df_filtered.columns.get_loc(col) + 1
                worksheet.set_column(col_idx, col_idx, None, format1)
        
        writer.save()
        output.seek(0)
        
        st.download_button(
            label="Descargar datos filtrados en Excel",
            data=output,
            file_name="datos_filtrados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.write("No se encontraron datos para los filtros ingresados.")
else:
    st.write("Por favor, ingresa al menos uno de los filtros: Mes, Marca, Tienda o Familia.")
