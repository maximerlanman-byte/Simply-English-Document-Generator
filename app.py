import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from io import BytesIO

st.set_page_config(page_title="Simply English Document Generator", page_icon="📄")

st.title("📄 Simply English Document Generator")

tipo = st.selectbox(
    "Tipo de documento",
    [
        "Justificante de clase",
        "Justificante de examen",
        "Justificante de asistencia a clases",
        "Certificado de matrícula"
    ]
)

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

if tipo == "Justificante de clase":
    nombre = st.text_input("Nombre del alumno/a")
    dni = st.text_input("DNI")
    fecha = st.text_input("Fecha de la clase", "1 de junio de 2026")
    horario = st.text_input("Horario", "17:00 h a 18:30 h")
    motivo = st.text_input("Motivo obligatorio", "sesión preparatoria obligatoria")

    if st.button("Generar PDF"):
        lineas = [
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
            f"En Utrera, {fecha}.",
            "",
            "Simply English",
            "C/ Real 5, Local 1",
            "41710 Utrera (Sevilla)"
        ]
        pdf = generar_pdf("JUSTIFICANTE DE ASISTENCIA", lineas)
        st.download_button("Descargar PDF", pdf, f"Justificante_{nombre}.pdf", "application/pdf")

elif tipo == "Justificante de examen":
    nombre = st.text_input("Nombre del alumno/a")
    dni = st.text_input("DNI")
    examen = st.text_input("Examen", "Trinity ISE III")
    fecha_escrito = st.text_input("Fecha examen escrito", "3 de junio de 2026")
    horario_escrito = st.text_input("Horario examen escrito", "09:00 h a 13:00 h")
    fecha_oral = st.text_input("Fecha examen oral", "2 de junio de 2026")
    horario_oral = st.text_input("Horario autorizado examen oral", "14:00 h a 16:30 h")

    if st.button("Generar PDF"):
        lineas = [
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
            "En Utrera, 1 de junio de 2026.",
            "",
            "Simply English",
            "C/ Real 5, Local 1",
            "41710 Utrera (Sevilla)"
        ]
        pdf = generar_pdf("JUSTIFICANTE DE ASISTENCIA A EXAMEN OFICIAL", lineas)
        st.download_button("Descargar PDF", pdf, f"Justificante_examen_{nombre}.pdf", "application/pdf")

elif tipo == "Justificante de asistencia a clases":
    nombre = st.text_input("Nombre del alumno/a")
    dni = st.text_input("DNI")
    curso = st.text_input("Curso / nivel")
    dias = st.text_input("Días de clase", "lunes y miércoles")
    horario = st.text_input("Horario", "17:00 h a 18:00 h")
    matricula = st.text_input("Precio matrícula", "30 €")
    materiales = st.text_input("Precio materiales", "0 €")
    mensualidad = st.text_input("Precio mensual", "60 €")

    if st.button("Generar PDF"):
        lineas = [
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
            "Asimismo, hacemos constar que el alumno/a sí asiste a clase",
            "según el horario indicado.",
            "",
            "Y para que conste a los efectos oportunos, se expide el presente justificante.",
            "",
            "En Utrera, 1 de junio de 2026.",
            "",
            "Simply English",
            "C/ Real 5, Local 1",
            "41710 Utrera (Sevilla)"
        ]
        pdf = generar_pdf("JUSTIFICANTE DE ASISTENCIA A CLASES", lineas)
        st.download_button("Descargar PDF", pdf, f"Asistencia_clases_{nombre}.pdf", "application/pdf")

elif tipo == "Certificado de matrícula":
    nombre = st.text_input("Nombre del alumno/a")
    dni = st.text_input("DNI")
    curso = st.text_input("Curso / nivel")
    ano = st.text_input("Año académico", "2025/2026")

    if st.button("Generar PDF"):
        lineas = [
            "Por la presente, Simply English certifica que el alumno/a:",
            "",
            nombre.upper(),
            "",
            f"con DNI {dni}, se encuentra matriculado/a en nuestro centro",
            f"en el curso/nivel {curso}, correspondiente al año académico {ano}.",
            "",
            "Y para que conste a los efectos oportunos, se expide el presente certificado.",
            "",
            "En Utrera, 1 de junio de 2026.",
            "",
            "Simply English",
            "C/ Real 5, Local 1",
            "41710 Utrera (Sevilla)"
        ]
        pdf = generar_pdf("CERTIFICADO DE MATRÍCULA", lineas)
        st.download_button("Descargar PDF", pdf, f"Certificado_matricula_{nombre}.pdf", "application/pdf")
