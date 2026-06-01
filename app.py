import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from io import BytesIO

st.set_page_config(page_title="Simply English Document Generator", page_icon="📄")

st.title("📄 Simply English Document Generator")

st.subheader("Crear un justificante individual")

nombre = st.text_input("Nombre del alumno/a")
dni = st.text_input("DNI")
tipo = st.selectbox(
    "Tipo de justificante",
    [
        "Justificante de asistencia a clase obligatoria",
        "Justificante de examen"
    ]
)

fecha = st.text_input("Fecha", "1 de junio de 2026")
horario = st.text_input("Horario", "17:00 h a 18:30 h")
examen = st.text_input("Examen", "Trinity ISE III")
fechas_examen = st.text_input("Fechas del examen", "2 y 3 de junio de 2026")

def crear_pdf(nombre, dni, fecha, horario, examen, fechas_examen):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    # Fondo blanco
    c.setFillColor(colors.white)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # Franja inferior aguamarina
    c.setFillColor(colors.HexColor("#DDF5F4"))
    c.rect(0, 0, w, h * 0.18, fill=1, stroke=0)

    # Título
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(w / 2, h - 3 * cm, "JUSTIFICANTE DE ASISTENCIA")

    # Texto
    y = h - 5 * cm
    x = 2.5 * cm

    c.setFont("Helvetica", 11)

    lineas = [
        "Por la presente, Simply English certifica que el alumno/a:",
        "",
        nombre.upper(),
        "",
        f"con DNI {dni}, está matriculado/a en nuestro programa de preparación",
        f"para exámenes oficiales de inglés y deberá asistir obligatoriamente",
        f"a una sesión preparatoria para el examen oficial {examen} el día",
        f"{fecha}, en horario de {horario}.",
        "",
        f"Dicha sesión forma parte de la preparación final para las pruebas",
        f"oficiales que el alumno/a realizará los días {fechas_examen}.",
        "",
        "La asistencia a esta sesión es obligatoria para garantizar la correcta",
        "preparación y organización previa a las pruebas oficiales.",
        "",
        "Y para que conste a los efectos oportunos, se expide el presente justificante.",
        "",
        f"En Utrera, {fecha}.",
        "",
        "Simply English",
        "C/ Real 5, Local 1",
        "41710 Utrera (Sevilla)"
    ]

    for linea in lineas:
        if linea == nombre.upper():
            c.setFont("Helvetica-Bold", 12)
        else:
            c.setFont("Helvetica", 11)

        c.drawString(x, y, linea)
        y -= 0.55 * cm

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

if st.button("Generar PDF"):
    if not nombre:
        st.error("Falta el nombre del alumno/a.")
    else:
        pdf = crear_pdf(nombre, dni, fecha, horario, examen, fechas_examen)
        st.success("PDF generado correctamente.")

        st.download_button(
            label="Descargar PDF",
            data=pdf,
            file_name=f"Justificante_{nombre.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
