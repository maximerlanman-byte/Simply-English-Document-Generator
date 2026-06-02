import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from io import BytesIO
import zipfile

st.set_page_config(page_title="Simply English Document Generator", page_icon="📄")

st.title("📄 Simply English Document Generator")

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


def generar_pdf(titulo, lineas):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    c.setFillColor(colors.white)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    c.setFillColor(colors.HexColor("#DDF5F4"))
    c.rect(0, 0, w, h * 0.18, fill=1, stroke=0)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(w / 2, h - 3 * cm, titulo)

    x = 2.5 * cm
    y = h - 5 * cm

    for linea in lineas:
        linea = limpiar(linea)

        if linea.isupper() and len(linea) > 3:
            c.setFont("Helvetica-Bold", 12)
        else:
            c.setFont("Helvetica", 11)

        c.drawString(x, y, linea)
        y -= 0.6 * cm

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

    return [
        "Por la presente, Simply English certifica que el alumno/a:",
        "",
        nombre.upper(),
        "",
        f"con DNI {dni}, deberá asistir obligatoriamente a clase el día",
        f"{fecha}, en horario de {horario}.",
        "",
        f"Motivo: {motivo}.",
        "",
        "Y para que conste a los efectos oportunos, se expide el presente justificante.",
        "",
        f"En Utrera, {fecha_emision}.",
        "",
        "Simply English",
        "C/ Real 5, Local 1",
        "41710 Utrera (Sevilla)"
    ]


def lineas_justificante_examen(datos):
    nombre = limpiar(datos.get("nombre_alumno", ""))
    dni = limpiar(datos.get("dni", ""))
    examen = limpiar(datos.get("examen", ""))
    fecha_escrito = limpiar(datos.get("fecha_escrito", ""))
    horario_escrito = limpiar(datos.get("horario_escrito", ""))
    fecha_oral = limpiar(datos.get("fecha_oral", ""))
    horario_oral = limpiar(datos.get("horario_oral_autorizado", ""))
    fecha_emision = limpiar(datos.get("fecha_emision", ""))

    return [
        "Por la presente, Simply English declara que el alumno/a:",
        "",
        nombre.upper(),
        "",
        f"DNI: {dni}",
        "",
        f"está matriculado/a para la realización del examen oficial {examen}.",
        "",
        "El alumno/a deberá asistir al centro para la realización de la prueba escrita el día:",
        fecha_escrito,
        f"Horario: de {horario_escrito}",
        "",
        "El alumno/a deberá asistir al centro para la realización de la prueba oral el día:",
        fecha_oral,
        f"Horario de asistencia autorizado: de {horario_oral}",
        "",
        "Este horario incluye margen adicional de una hora antes y una hora después",
        "para organización, espera y realización de la prueba.",
        "",
        "Y para que conste a los efectos oportunos, se expide el presente justificante.",
        "",
        f"En Utrera, {fecha_emision}.",
        "",
        "Simply English",
        "C/ Real 5, Local 1",
        "41710 Utrera (Sevilla)"
    ]


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
    observaciones = limpiar(datos.get("observaciones", ""))

    return [
        "Por la presente, Simply English certifica que el alumno/a:",
        "",
        nombre.upper(),
        "",
        f"con DNI {dni}, asiste regularmente a clases de inglés en nuestro centro.",
        "",
        f"Curso / nivel: {curso}",
        f"Días de clase: {dias}",
        f"Horario: {horario}",
        "",
        f"Precio de matrícula: {matricula}",
        f"Precio de materiales: {materiales}",
        f"Precio mensual: {mensualidad}",
        "",
        observaciones,
        "",
        "Y para que conste a los efectos oportunos, se expide el presente justificante.",
        "",
        f"En Utrera, {fecha_emision}.",
        "",
        "Simply English",
        "C/ Real 5, Local 1",
        "41710 Utrera (Sevilla)"
    ]


def crear_pdf_por_tipo(tipo, datos):
    if tipo == "Justificante de clase":
        return generar_pdf("JUSTIFICANTE DE ASISTENCIA", lineas_justificante_clase(datos))

    if tipo == "Justificante de examen":
        return generar_pdf("JUSTIFICANTE DE ASISTENCIA A EXAMEN OFICIAL", lineas_justificante_examen(datos))

    if tipo == "Justificante de asistencia a clases":
        return generar_pdf("JUSTIFICANTE DE ASISTENCIA A CLASES", lineas_asistencia_clases(datos))


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
        except Exception as e:
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
