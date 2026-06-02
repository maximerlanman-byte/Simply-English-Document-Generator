import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import zipfile
import textwrap
import os

st.set_page_config(page_title="Simply English Document Generator", page_icon="📄")

st.title("📄 Simply English Document Generator")

TEMPLATE_PATH = "assets/A4_template.png"
FONT_REGULAR = "assets/OpenSans-Regular.ttf"
FONT_BOLD = "assets/OpenSans-Bold.ttf"

if os.path.exists(FONT_REGULAR):
    pdfmetrics.registerFont(TTFont("OpenSans", FONT_REGULAR))
else:
    st.warning("OpenSans-Regular.ttf not found. Using Helvetica.")
    
if os.path.exists(FONT_BOLD):
    pdfmetrics.registerFont(TTFont("OpenSans-Bold", FONT_BOLD))
else:
    st.warning("OpenSans-Bold.ttf not found. Using Helvetica-Bold.")


def font_regular():
    return "OpenSans" if os.path.exists(FONT_REGULAR) else "Helvetica"


def font_bold():
    return "OpenSans-Bold" if os.path.exists(FONT_BOLD) else "Helvetica-Bold"


modo = st.radio("Modo", ["Individual", "Excel Masivo"])

tipos_documento = [
    "Justificante de clase",
    "Justificante de examen",
    "Justificante de asistencia a clases",
]


def limpiar(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip()


def draw_wrapped_text(c, text, x, y, max_chars=90, line_height=0.50 * cm, bold=False):
    if text is None:
        return y

    text = str(text).strip()

    # Blank line = real paragraph space
    if text == "":
        return y - 0.65 * cm

    font_name = font_bold() if bold else font_regular()
    font_size = 10.5

    c.setFont(font_name, font_size)

    wrapped = textwrap.wrap(text, width=max_chars)

    for line in wrapped:
        c.drawString(x, y, line)
        y -= line_height

    # Extra space after every paragraph
    return y - 0.25 * cm


def generar_pdf(titulo, lineas, fecha_emision=""):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    # Background template
    if os.path.exists(TEMPLATE_PATH):
        c.drawImage(TEMPLATE_PATH, 0, 0, width=w, height=h)
    else:
        c.setFillColor(colors.white)
        c.rect(0, 0, w, h, fill=1, stroke=0)

    # Title
    c.setFillColor(colors.black)
    c.setFont(font_bold(), 13.5)
    c.drawCentredString(w / 2, h - 7.1 * cm, titulo)

    # Main text area
    x = 2.7 * cm
    y = h - 8.7 * cm

    for item in lineas:
        if isinstance(item, dict):
            texto = item.get("text", "")
            bold = item.get("bold", False)
        else:
            texto = item
            bold = False

        y = draw_wrapped_text(c, texto, x, y, max_chars=90, line_height=0.55 * cm, bold=bold)

    # Date above signature area
    if fecha_emision:
        c.setFont(font_regular(), 10.5)
        c.drawString(2.7 * cm, 4.1 * cm, f"En Utrera, {fecha_emision}.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def lineas_justificante_clase(datos):
    nombre = limpiar(datos.get("nombre_alumno", ""))
    dni = limpiar(datos.get("dni", ""))
    fecha = limpiar(datos.get("fecha_clase", ""))
    horario = limpiar(datos.get("horario", ""))
    motivo = limpiar(datos.get("motivo_obligatorio", ""))
    fecha_emision = limpiar(datos.get("fecha_emision", fecha))

    lineas = [
        "Por la presente, Simply English certifica que el alumno/a:",
        {"text": nombre.upper(), "bold": True},
        f"con DNI {dni}, deberá asistir obligatoriamente a clase el día {fecha}, en horario de {horario}.",
        f"Motivo: {motivo}.",
        "Y para que conste a los efectos oportunos, se expide el presente justificante.",
    ]

    return lineas, fecha_emision


def lineas_justificante_examen(datos):
    nombre = limpiar(datos.get("nombre_alumno", ""))
    dni = limpiar(datos.get("dni", ""))
    examen = limpiar(datos.get("examen", ""))
    fecha_escrito = limpiar(datos.get("fecha_escrito", ""))
    horario_escrito = limpiar(datos.get("horario_escrito", ""))
    fecha_oral = limpiar(datos.get("fecha_oral", ""))
    horario_oral = limpiar(datos.get("horario_oral_autorizado", ""))
    fecha_emision = limpiar(datos.get("fecha_emision", ""))

    lineas = [
        "Por la presente, Simply English declara que el alumno/a:",
        {"text": nombre.upper(), "bold": True},
        "",
        f"DNI: {dni}",
        f"está matriculado/a para la realización del examen oficial {examen}.",
        f"El alumno/a deberá asistir al centro para la realización de la prueba escrita el día {fecha_escrito}, en horario de {horario_escrito}.",
        f"El alumno/a deberá asistir al centro para la realización de la prueba oral el día {fecha_oral}.",
        f"Horario de asistencia autorizado para la prueba oral: de {horario_oral}.",
        "Este horario incluye margen adicional de una hora antes y una hora después para organización, espera y realización de la prueba.",
        "Y para que conste a los efectos oportunos, se expide el presente justificante.",
    ]

    return lineas, fecha_emision


def lineas_asistencia_clases(datos):
    nombre = limpiar(datos.get("nombre_alumno", ""))
    dni = limpiar(datos.get("dni", ""))
    curso = limpiar(datos.get("curso_nivel", ""))
    dias = limpiar(datos.get("dias_clase", ""))
    horario = limpiar(datos.get("horario", ""))
    matricula = limpiar(datos.get("precio_matricula", ""))
    materiales = limpiar(datos.get("precio_materiales", ""))
    mensualidad = limpiar(datos.get("precio_mensual", ""))
    fecha_emision = limpiar(datos.get("fecha_emision", ""))
    observaciones = limpiar(datos.get("observaciones", "El alumno/a asiste regularmente a clase."))

    lineas = [
        "Por la presente, Simply English certifica que el alumno/a:",
        {"text": nombre.upper(), "bold": True},
        f"con DNI {dni}, asiste regularmente a clases de inglés en nuestro centro.",
        f"Curso / nivel: {curso}",
        f"Días de clase: {dias}",
        f"Horario: {horario}",
        f"Precio de matrícula: {matricula}",
        f"Precio de materiales: {materiales}",
        f"Precio mensual: {mensualidad}",
        observaciones,
        "Y para que conste a los efectos oportunos, se expide el presente justificante.",
    ]

    return lineas, fecha_emision


def crear_pdf_por_tipo(tipo, datos):
    if tipo == "Justificante de clase":
        lineas, fecha_emision = lineas_justificante_clase(datos)
        return generar_pdf("JUSTIFICANTE DE ASISTENCIA", lineas, fecha_emision)

    if tipo == "Justificante de examen":
        lineas, fecha_emision = lineas_justificante_examen(datos)
        return generar_pdf("JUSTIFICANTE DE ASISTENCIA A EXAMEN OFICIAL", lineas, fecha_emision)

    if tipo == "Justificante de asistencia a clases":
        lineas, fecha_emision = lineas_asistencia_clases(datos)
        return generar_pdf("JUSTIFICANTE DE ASISTENCIA A CLASES", lineas, fecha_emision)


def sheet_por_tipo(tipo):
    if tipo == "Justificante de clase":
        return "Justificante_Clase"
    if tipo == "Justificante de examen":
        return "Justificante_Examen"
    if tipo == "Justificante de asistencia a clases":
        return "Asistencia_Clases"


if modo == "Individual":
    tipo = st.selectbox("Tipo de documento", tipos_documento)

    if tipo == "Justificante de clase":
        datos = {
            "nombre_alumno": st.text_input("Nombre del alumno/a"),
            "dni": st.text_input("DNI"),
            "fecha_clase": st.text_input("Fecha de la clase", "1 de junio de 2026"),
            "horario": st.text_input("Horario", "17:00 h a 18:30 h"),
            "motivo_obligatorio": st.text_input("Motivo obligatorio"),
            "fecha_emision": st.text_input("Fecha de emisión", "1 de junio de 2026"),
        }

    elif tipo == "Justificante de examen":
        datos = {
            "nombre_alumno": st.text_input("Nombre del alumno/a"),
            "dni": st.text_input("DNI"),
            "examen": st.text_input("Examen", "Trinity ISE III"),
            "fecha_escrito": st.text_input("Fecha examen escrito", "3 de junio de 2026"),
            "horario_escrito": st.text_input("Horario examen escrito", "09:00 h a 13:00 h"),
            "fecha_oral": st.text_input("Fecha examen oral", "2 de junio de 2026"),
            "horario_oral_autorizado": st.text_input("Horario oral autorizado", "14:00 h a 16:30 h"),
            "fecha_emision": st.text_input("Fecha de emisión", "1 de junio de 2026"),
        }

    elif tipo == "Justificante de asistencia a clases":
        datos = {
            "nombre_alumno": st.text_input("Nombre del alumno/a"),
            "dni": st.text_input("DNI"),
            "curso_nivel": st.text_input("Curso / nivel"),
            "dias_clase": st.text_input("Días de clase", "lunes y miércoles"),
            "horario": st.text_input("Horario", "17:00 h a 18:00 h"),
            "precio_matricula": st.text_input("Precio matrícula", "30 €"),
            "precio_materiales": st.text_input("Precio materiales", "45 €"),
            "precio_mensual": st.text_input("Precio mensual", "60 €/mes"),
            "fecha_emision": st.text_input("Fecha de emisión", "1 de junio de 2026"),
            "observaciones": st.text_input("Observaciones", "El alumno/a asiste regularmente a clase."),
        }

    if st.button("Generar PDF"):
        nombre = limpiar(datos.get("nombre_alumno", "alumno"))
        if nombre == "":
            st.error("Falta el nombre del alumno/a.")
        else:
            pdf = crear_pdf_por_tipo(tipo, datos)
            st.download_button(
                "Descargar PDF",
                pdf,
                f"{tipo.replace(' ', '_')}_{nombre.replace(' ', '_')}.pdf",
                "application/pdf"
            )


elif modo == "Excel Masivo":
    st.subheader("Generar varios documentos desde Excel")

    tipo = st.selectbox("Tipo de documento", tipos_documento)
    archivo = st.file_uploader("Subir Excel maestro", type=["xlsx"])

    if archivo is not None:
        sheet_name = sheet_por_tipo(tipo)

        try:
            df = pd.read_excel(archivo, sheet_name=sheet_name)
        except Exception:
            st.error(f"No se pudo leer la pestaña {sheet_name}. Revisa el Excel.")
            st.stop()

        df.columns = [str(col).strip() for col in df.columns]
        df = df.dropna(how="all")

        st.success(f"Excel cargado correctamente. Pestaña leída: {sheet_name}")
        st.dataframe(df)

        if st.button("Generar ZIP"):
            zip_buffer = BytesIO()
            documentos_creados = 0

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for index, fila in df.iterrows():
                    datos = fila.to_dict()
                    nombre = limpiar(datos.get("nombre_alumno", ""))

                    if nombre == "":
                        continue

                    pdf = crear_pdf_por_tipo(tipo, datos)

                    nombre_archivo = nombre.replace(" ", "_")
                    filename = f"{tipo.replace(' ', '_')}_{nombre_archivo}.pdf"

                    zip_file.writestr(filename, pdf.getvalue())
                    documentos_creados += 1

            zip_buffer.seek(0)

            if documentos_creados == 0:
                st.error("No se ha creado ningún documento. Revisa que la pestaña tenga nombre_alumno.")
            else:
                st.success(f"ZIP generado correctamente con {documentos_creados} documento(s).")

                st.download_button(
                    "Descargar ZIP",
                    zip_buffer,
                    "documentos_simply_english.zip",
                    "application/zip"
                )
