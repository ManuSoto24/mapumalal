import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fpdf import FPDF

# Configurar la conexión con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("registro-de-terrenos-chml-a194d54a5c46.json", scope)
client = gspread.authorize(creds)

# Abrir la hoja de cálculo y seleccionar la hoja
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1pJ9rjiED41Zh4sENtTKzi3kfzFkP8LnIcQBJm0Xbt6Y/edit?usp=sharing").sheet1

# Función para generar el PDF
def generate_pdf(name, surname, id_number, total_score, user_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Resultado de Evaluación", ln=True, align='C')
    
    # Información Personal
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Nombre: {name}", ln=True)
    pdf.cell(200, 10, f"Apellido: {surname}", ln=True)
    pdf.cell(200, 10, f"Documento de Identidad: {id_number}", ln=True)
    
    # Puntaje Total
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, f"Puntaje Total: {total_score}", ln=True)
    
    # Información de las categorías
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Detalles por Categoría:", ln=True)
    for key, value in user_data.items():
        if key not in ["Nombre", "Apellido", "Documento de Identidad", "Puntaje Total"]:
            pdf.cell(200, 10, f"{key}: {value}", ln=True)
    
    # Guardar el PDF
    pdf_output = f"resultado_{name}_{surname}.pdf"
    pdf.output(pdf_output)
    
    return pdf_output

# Título de la Aplicación
st.title("Demanda de Terrenos by José Soto - si funciona la vendo")

# Botones de sesión
if st.button("Abrir Sesión"):
    st.session_state.logged_in = True
    st.success("Sesión abierta. Puedes comenzar a ingresar datos.")

if st.button("Cerrar Sesión"):
    st.session_state.logged_in = False
    st.success("Sesión cerrada.")

# Mostrar un mensaje si no se ha iniciado sesión
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Por favor, abre una sesión para ingresar datos.")
else:
    # Ingresar Datos Personales
    name = st.text_input("Nombre")
    surname = st.text_input("Apellido")
    id_number = st.text_input("Documento de Identidad")

    # Definir las categorías y sus ítems con puntajes
    criteria = {
        "Antigüedad de la solicitud": {
            "Más de 10 años": 100,
            "Entre 5 y 9 años": 50,
            "Menos 5 años": 30
        },
        "Tipo de vivienda actual": {
            "Local adaptado a vivienda": 25,
            "Vivienda precaria": 50,
            "Casa o dpto.": 15
        },
        "Cantidad de personas que duermen por habitación": {
            "Hasta 2 personas": 30,
            "Hasta 3 personas": 50,
            "4 o más": 100
        },
        "Tenencia de la vivienda": {
            "Propietario de la vivienda o terreno": 0,
            "Alquilada": 50,
            "Cedida": 15,
            "Compartida": 25
        },
        "Ubicación de la vivienda": {
            "Zona inundable": 21,
            "Zona de pendientes bardas o cañadones": 21,
            "Zona Urbana": 7,
            "Sector Basural": 21
        },
        "Grupo Familiar": {
            "Familia monoparental": 25,
            "Menores de 18 años en el hogar": 25,
            "Integrantes de la familia con discapacidad": 50
        },
        "Residencia": {
            "1 punto por cada año o fracción mayor a 6 meses de residencia cuando supere los 10 años": 100,
            "Nativo con residencia permanente": 200
        },
        "Ingresos del/los solicitantes": {
            "Menor o igual a 1 S.M.V.M.": 30,
            "Entre 1 y 3 S.M.V.M.": 50,
            "Entre 3 y 5 S.M.V.M.": 80,
            "Mayor de 6 S.M.V.M.": 100
        },
        "Estabilidad laboral - Relación de dependencia": {
            "Menor a 1 año": 10,
            "Entre 1 y 5 años": 30,
            "Entre 5 y 10 años": 50,
            "Más de 10 años": 100
        },
        "Estabilidad laboral independiente": {
            "Menor a 1 año": 10,
            "Entre 1 y 5 años": 30,
            "Entre 5 y 10 años": 50,
            "Más de 10 años": 100
        },
        "Informe de: Central de Deudores del Sistema Financiero": {
            "0 o 1": 100,
            "2": 50,
            "3 o más": 0
        },
        "Título estudios superiores": {
            "Sí": 25,
            "No": 0
        },
        "Antecedente para ejecución de obra": {
            "Planos": 50,
            "Prepago de vivienda": 100,
            "Nada": 0
        }
    }

    # Inicializar una variable para el puntaje total y un diccionario para guardar las selecciones
    total_score = 0
    user_data = {
        "Nombre": name,
        "Apellido": surname,
        "Documento de Identidad": id_number
    }

    # Crear listas desplegables para cada criterio y capturar las selecciones
    for criterion, options in criteria.items():
        selected_option = st.selectbox(f'{criterion}', options.keys())
        total_score += options[selected_option]
        user_data[criterion] = selected_option

    # Agregar el puntaje total al diccionario
    user_data["Puntaje Total"] = total_score

    # Guardar los datos en la hoja de cálculo
    if st.button("Guardar y agregar a la base de datos"):
        if name and surname and id_number:
            # Convertir el diccionario a una lista ordenada para la hoja de cálculo
            row = [user_data[key] for key in user_data.keys()]
            sheet.append_row(row)
            st.success("Datos guardados exitosamente.")
        else:
            st.error("Por favor, completa todos los campos de datos personales.")

    # Generar PDF y ofrecerlo para descargar
    if st.button("Generar PDF"):
        if name and surname and id_number:
            pdf_file = generate_pdf(name, surname, id_number, total_score, user_data)
            with open(pdf_file, "rb") as file:
                st.download_button(label="Descargar PDF", data=file, file_name=pdf_file, mime="application/pdf")
        else:
            st.error("Por favor, completa todos los campos de datos personales.")
