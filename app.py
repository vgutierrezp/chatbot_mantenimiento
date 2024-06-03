import streamlit as st
import pandas as pd
import os
from io import BytesIO

def load_data():
    folder_path = r"C:\Users\vgutierrez\OneDrive - Servicios Compartidos de Restaurantes SAC\Documentos\01 Plan Preventivo Anual NGR\Preventivo\2024 PAM\PROVEEDORES"
    all_data = []
    file_names = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".xlsx"):
            file_path = os.path.join(folder_path, file_name)
            data = pd.read_excel(file_path, sheet_name=None)
            all_data.append(data)
            file_names.append(file_name)
    return all_data, file_names

def filter_data(data, file_names, mes, marca, tienda):
    filtered_data = []
    for df, file_name in zip(data, file_names):
        for sheet_name, sheet_df in df.items():
            if all(col in sheet_df.columns for col in ['Mes', 'Marca', 'Tienda']):
                sheet_df['Mes'] = sheet_df['Mes'].astype(str)
                sheet_df['Marca'] = sheet_df['Marca'].astype(str)
                sheet_df['Tienda'] = sheet_df['Tienda'].astype(str)

                df_filtered = sheet_df.copy()
                if mes:
                    df_filtered = df_filtered[df_filtered['Mes'].str.contains(mes, case=False, na=False)]
                if marca:
                    df_filtered = df_filtered[df_filtered['Marca'].str.contains(marca, case=False, na=False)]
                if tienda:
                    df_filtered = df_filtered[df_filtered['Tienda'].str.contains(tienda, case=False, na=False)]

                if not df_filtered.empty:
                    filtered_data.append(df_filtered)
            else:
                st.warning(f"La hoja {sheet_name} en el archivo {file_name} no contiene las columnas necesarias.")
    return pd.concat(filtered_data, ignore_index=True) if filtered_data else pd.DataFrame()

st.title("Chatbot de Mantenimiento")
st.write("Este chatbot te ayudará a consultar información de mantenimiento preventivo.")

input_mes = st.text_input("Ingresa el mes:")
input_marca = st.text_input("Ingresa la marca:")
input_tienda = st.text_input("Ingresa la tienda:")

# Si cualquiera de los filtros cambia, se recarga la aplicación
if st.session_state.get("last_input_mes") != input_mes:
    st.session_state["last_input_mes"] = input_mes
    st.experimental_rerun()
if st.session_state.get("last_input_marca") != input_marca:
    st.session_state["last_input_marca"] = input_marca
    st.experimental_rerun()
if st.session_state.get("last_input_tienda") != input_tienda:
    st.session_state["last_input_tienda"] = input_tienda
    st.experimental_rerun()

if input_mes or input_marca or input_tienda:
    data, file_names = load_data()
    df_filtered = filter_data(data, file_names, input_mes, input_marca, input_tienda)
    
    if not df_filtered.empty:
        columns_to_show = [
            "Mes", "Tienda", "Familia", "Tipo de Equipo", "Tipo de Servicio", "Ejecutor",
            "Frecuencia", "N° Equipos", "Ult. Prev.", "Prog.1", "Ejec.1",
            "CO", "CL", "IP", "RP"
        ]

        available_columns = [col for col in columns_to_show if col in df_filtered.columns]

        for col in ['Ult. Prev.', 'Prog.1', 'Ejec.1', 'CO', 'CL', 'IP', 'RP']:
            if col in df_filtered.columns:
                try:
                    df_filtered[col] = pd.to_datetime(df_filtered[col], errors='coerce').dt.strftime('%d-%m-%Y')
                except Exception as e:
                    st.warning(f"Error al formatear la columna {col}: {e}")

        df_filtered = df_filtered.sort_values(by=['Mes', 'Familia'], key=lambda x: pd.Categorical(x, categories=["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"], ordered=True))

        st.write(f"Datos filtrados para Mes: {input_mes or 'Todos'}, Marca: {input_marca or 'Todas'}, Tienda: {input_tienda or 'Todas'}")
        st.dataframe(df_filtered[available_columns])
        
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df_filtered[available_columns].to_excel(writer, index=False, sheet_name='Filtered Data')
        
        workbook = writer.book
        worksheet = writer.sheets['Filtered Data']
        
        format1 = workbook.add_format({'num_format': 'dd-mm-yyyy'})
        for col in ['CO', 'CL', 'IP', 'RP']:
            if col in df_filtered.columns:
                col_idx = df_filtered.columns.get_loc(col)
                worksheet.set_column(col_idx, col_idx, None, format1)

        writer.close()
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
    st.write("Por favor, ingresa al menos uno de los filtros: Mes, Marca o Tienda.")
