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
import re
import unicodedata
from datetime import datetime, timedelta

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None


# ============================================================
# SIMPLY ENGLISH DOCUMENT GENERATOR
# ============================================================
# Required GitHub structure:
#
# app.py
# requirements.txt
# assets/
#   A4_template.png
#   OpenSans-Regular.ttf
#   OpenSans-Bold.ttf
#
# requirements.txt should include:
# streamlit
# pandas
# openpyxl
# reportlab
# pypdf
# ============================================================


st.set_page_config(page_title="Simply English Document Generator", page_icon="📄")
st.title("📄 Simply English Document Generator")


# ---------- ASSETS ----------

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


# ---------- BASIC HELPERS ----------

def limpiar(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip()


def safe_filename(texto):
    texto = limpiar(texto)
    if texto == "":
        texto = "alumno"
    replacements = {
        " ": "_",
        "/": "-",
        "\\": "-",
        ":": "-",
        "*": "",
        "?": "",
        '"': "",
        "<": "",
        ">": "",
        "|": "",
    }
    for old, new in replacements.items():
        texto = texto.replace(old, new)
    return texto


def normalize_name(texto):
    texto = limpiar(texto).lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = re.sub(r"[^a-z0-9 ]+", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def format_date_spanish(value):
    if value is None or limpiar(value) == "":
        return ""

    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y")

    text = limpiar(value)
    return text


def parse_time_to_dt(date_text, time_text):
    """date_text expected dd/mm/yyyy or similar. time_text HH:MM."""
    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            d = datetime.strptime(date_text.strip(), fmt)
            h, m = map(int, time_text.split(":"))
            return d.replace(hour=h, minute=m, second=0, microsecond=0)
        except Exception:
            pass
    # Fallback date if parsing fails, but keep time
    h, m = map(int, time_text.split(":"))
    return datetime(2000, 1, 1, h, m)


def floor_15(dt):
    minute = (dt.minute // 15) * 15
    return dt.replace(minute=minute, second=0, microsecond=0)


def ceil_15(dt):
    if dt.minute % 15 == 0 and dt.second == 0 and dt.microsecond == 0:
        return dt.replace(second=0, microsecond=0)
    minute = ((dt.minute // 15) + 1) * 15
    if minute == 60:
        return dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    return dt.replace(minute=minute, second=0, microsecond=0)


def calculate_authorised_oral_window(date_text, start_time, end_time):
    start_dt = parse_time_to_dt(date_text, start_time)
    end_dt = parse_time_to_dt(date_text, end_time)

    start_window = floor_15(start_dt - timedelta(hours=1))
    end_window = ceil_15(end_dt + timedelta(hours=1))

    return start_window.strftime("%H:%M h"), end_window.strftime("%H:%M h")


# ---------- TEXT DRAWING ----------

def draw_wrapped_text(
    c,
    text,
    x,
    y,
    max_chars=88,
    line_height=0.48 * cm,
    bold=False,
    font_size=10.5,
    after_space=0.22 * cm,
):
    if text is None:
        return y

    text = str(text).strip()

    # Blank line = visible paragraph gap
    if text == "":
        return y - 0.60 * cm

    font_name = font_bold() if bold else font_regular()
    c.setFont(font_name, font_size)

    wrapped = textwrap.wrap(text, width=max_chars)

    for line in wrapped:
        c.drawString(x, y, line)
        y -= line_height

    return y - after_space


def draw_document_line(c, item, x, y):
    if isinstance(item, dict):
        texto = item.get("text", "")
        bold = item.get("bold", False)
        is_name = item.get("name", False)

        if is_name:
            return draw_wrapped_text(
                c,
                texto,
                x,
                y,
                max_chars=80,
                line_height=0.50 * cm,
                bold=True,
                font_size=12.5,
                after_space=0.30 * cm,
            )

        return draw_wrapped_text(
            c,
            texto,
            x,
            y,
            max_chars=88,
            line_height=0.48 * cm,
            bold=bold,
            font_size=10.5,
            after_space=0.22 * cm,
        )

    return draw_wrapped_text(
        c,
        item,
        x,
        y,
        max_chars=88,
        line_height=0.48 * cm,
        bold=False,
        font_size=10.5,
        after_space=0.22 * cm,
    )


# ---------- PDF GENERATION ----------

def generar_pdf(titulo, lineas, fecha_emision=""):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    # Background Canva template
    if os.path.exists(TEMPLATE_PATH):
        c.drawImage(TEMPLATE_PATH, 0, 0, width=w, height=h)
    else:
        c.setFillColor(colors.white)
        c.rect(0, 0, w, h, fill=1, stroke=0)

    # Automatic title
    c.setFillColor(colors.black)
    c.setFont(font_bold(), 13.5)
    c.drawCentredString(w / 2, h - 7.15 * cm, titulo)

    # Main body area
    x = 2.7 * cm
    y = h - 8.75 * cm

    for item in lineas:
        y = draw_document_line(c, item, x, y)

    # Date above signature/stamp area
    if fecha_emision:
        c.setFont(font_regular(), 10.5)
        c.drawString(2.7 * cm, 4.1 * cm, f"En Utrera, {fecha_emision}.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# ---------- DOCUMENT TEXT TEMPLATES ----------

def lineas_justificante_clase(datos):
    nombre = limpiar(datos.get("nombre_alumno", ""))
    dni = limpiar(datos.get("dni", ""))
    fecha = limpiar(datos.get("fecha_clase", ""))
    horario = limpiar(datos.get("horario", ""))
    motivo = limpiar(datos.get("motivo_obligatorio", ""))
    fecha_emision = limpiar(datos.get("fecha_emision", fecha))

    lineas = [
        "Por la presente, Simply English certifica que el alumno/a:",
        "",
        {"text": nombre.upper(), "bold": True, "name": True},
        "",
        {"text": f"DNI: {dni}", "bold": True},
        "",
        {"text": f"FECHA: {fecha}", "bold": True},
        {"text": f"HORARIO: {horario}", "bold": True},
        "",
        f"Motivo: {motivo}.",
        "",
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

    has_written = fecha_escrito != "" and horario_escrito != ""
    has_oral = fecha_oral != "" and horario_oral != ""

    lineas = [
        "Por la presente, Simply English declara que el alumno/a:",
        "",
        {"text": nombre.upper(), "bold": True, "name": True},
        "",
        {"text": f"DNI: {dni}", "bold": True},
        "",
        "está matriculado/a para la realización del examen oficial:",
        {"text": examen.upper(), "bold": True},
    ]

    if has_written:
        lineas += [
            "",
            {"text": f"FECHA EXAMEN ESCRITO: {fecha_escrito}", "bold": True},
            {"text": f"HORARIO EXAMEN ESCRITO: {horario_escrito}", "bold": True},
        ]

    if has_oral:
        lineas += [
            "",
            {"text": f"FECHA EXAMEN ORAL: {fecha_oral}", "bold": True},
            {"text": f"HORARIO ORAL AUTORIZADO: {horario_oral}", "bold": True},
            "",
            "Este horario incluye margen adicional de una hora antes y una hora después para organización, espera y realización de la prueba.",
        ]

    lineas += [
        "",
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
    observaciones = limpiar(
        datos.get(
            "observaciones",
            "El alumno/a asiste regularmente a clase según el horario indicado.",
        )
    )

    lineas = [
        "Por la presente, Simply English certifica que el alumno/a:",
        "",
        {"text": nombre.upper(), "bold": True, "name": True},
        "",
        {"text": f"DNI: {dni}", "bold": True},
        "",
        "asiste regularmente a clases de inglés en nuestro centro.",
        "",
        {"text": f"CURSO / NIVEL: {curso}", "bold": True},
        {"text": f"DÍAS DE CLASE: {dias}", "bold": True},
        {"text": f"HORARIO: {horario}", "bold": True},
        "",
        {"text": f"MATRÍCULA: {matricula}", "bold": True},
        {"text": f"MATERIALES: {materiales}", "bold": True},
        {"text": f"MENSUALIDAD: {mensualidad}", "bold": True},
        "",
        observaciones,
        "",
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

    return None


def sheet_por_tipo(tipo):
    if tipo == "Justificante de clase":
        return "Justificante_Clase"

    if tipo == "Justificante de examen":
        return "Justificante_Examen"

    if tipo == "Justificante de asistencia a clases":
        return "Asistencia_Clases"

    return None


# ---------- TRINITY AUTO: EXCEL PARSING ----------

def level_from_product(product_name):
    product = limpiar(product_name)

    mapping = [
        ("ISE Level III", "Trinity ISE III"),
        ("ISE Level II", "Trinity ISE II"),
        ("ISE Level I", "Trinity ISE I"),
        ("ISE Foundation", "Trinity ISE Foundation"),
        ("ISE A1", "Trinity ISE A1"),
        ("ISE IV", "Trinity ISE IV"),
    ]

    for key, label in mapping:
        if key.lower() in product.lower():
            return label

    return product.replace(" (Online)", "")


def module_from_product(product_name):
    product = limpiar(product_name).lower()

    has_rw = "reading and writing" in product or ("speaking and listening" not in product)
    has_sl = "speaking and listening" in product or ("reading and writing" not in product)

    return has_rw, has_sl


def read_trinity_entry_sheet(excel_file):
    """
    Reads Trinity entry sheet.
    Expected structure based on Trinity template:
    First Name column B, Last Name column D, Candidate Number column H,
    DNI column M, Product Name column O. Candidate data starts around row 42.
    """
    raw = pd.read_excel(excel_file, sheet_name="Enrolment Sheet", header=None)

    students = []

    for _, row in raw.iterrows():
        first_name = limpiar(row.get(1, ""))
        last_name = limpiar(row.get(3, ""))
        candidate_no = limpiar(row.get(7, ""))
        dni = limpiar(row.get(12, ""))
        product = limpiar(row.get(14, ""))

        if first_name == "" or last_name == "" or product == "":
            continue

        if not ("ISE" in product):
            continue

        full_name = f"{first_name} {last_name}".strip()
        exam = level_from_product(product)
        has_rw, has_sl = module_from_product(product)

        students.append(
            {
                "nombre_alumno": full_name,
                "nombre_norm": normalize_name(full_name),
                "candidate_no": candidate_no,
                "dni": dni,
                "product": product,
                "examen": exam,
                "has_written": has_rw,
                "has_oral": has_sl,
            }
        )

    return pd.DataFrame(students)


# ---------- TRINITY AUTO: PDF PARSING ----------

def extract_pdf_text(uploaded_pdf):
    if PdfReader is None:
        raise RuntimeError("pypdf is not installed. Add pypdf to requirements.txt.")

    reader = PdfReader(uploaded_pdf)
    pages = []

    for page in reader.pages:
        pages.append(page.extract_text() or "")

    return "\n".join(pages)


def parse_trinity_timetable_pdf(uploaded_pdf):
    """
    Parses Trinity Language Timetable PDF.
    Extracts: date, start time, end time, name, candidate number.
    """
    text = extract_pdf_text(uploaded_pdf)

    all_entries = []

    # Split into timetable blocks by date
    blocks = re.split(r"(?:[A-Za-zÀ-ÿ' -]+)'s Timetable for Date - ", text)

    # The split removes date marker; easier approach: iterate date occurrences with positions
    matches = list(re.finditer(r"Timetable for Date -\s*(\d{2}/\d{2}/\d{4})", text))

    for i, match in enumerate(matches):
        date_text = match.group(1)
        start_pos = match.end()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start_pos:end_pos]

        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]

        timed_lines = []
        for line in lines:
            if re.match(r"^\d{2}:\d{2}\b", line):
                timed_lines.append(line)

        for idx, line in enumerate(timed_lines):
            # Candidate line example:
            # 14:54 Angeles Maria Jones Fernandez 1-10138013413
            m = re.match(r"^(\d{2}:\d{2})\s+(.+?)\s+(1-\d+)\b", line)
            if not m:
                continue

            start_time = m.group(1)
            name = m.group(2).strip()
            candidate_no = m.group(3).strip()

            # End time = next timed line on the timetable
            end_time = start_time
            if idx + 1 < len(timed_lines):
                end_match = re.match(r"^(\d{2}:\d{2})\b", timed_lines[idx + 1])
                if end_match:
                    end_time = end_match.group(1)

            auth_start, auth_end = calculate_authorised_oral_window(date_text, start_time, end_time)

            all_entries.append(
                {
                    "candidate_no": candidate_no,
                    "nombre_pdf": name,
                    "nombre_norm": normalize_name(name),
                    "fecha_oral": date_text,
                    "hora_oral_real": start_time,
                    "hora_oral_fin_estimada": end_time,
                    "horario_oral_autorizado": f"{auth_start} a {auth_end}",
                }
            )

    return pd.DataFrame(all_entries)


def merge_entry_and_timetable(entry_df, timetable_df):
    """
    Match by candidate number when possible; otherwise match by normalized name.
    """
    rows = []

    timetable_by_candidate = {
        limpiar(row["candidate_no"]): row.to_dict()
        for _, row in timetable_df.iterrows()
        if limpiar(row.get("candidate_no", "")) != ""
    }

    timetable_by_name = {
        limpiar(row["nombre_norm"]): row.to_dict()
        for _, row in timetable_df.iterrows()
        if limpiar(row.get("nombre_norm", "")) != ""
    }

    for _, student in entry_df.iterrows():
        student_dict = student.to_dict()
        candidate_no = limpiar(student_dict.get("candidate_no", ""))
        name_norm = limpiar(student_dict.get("nombre_norm", ""))

        oral = None

        if candidate_no and candidate_no in timetable_by_candidate:
            oral = timetable_by_candidate[candidate_no]
        elif name_norm in timetable_by_name:
            oral = timetable_by_name[name_norm]

        combined = dict(student_dict)

        if oral:
            combined.update(
                {
                    "matched_oral": True,
                    "fecha_oral": oral.get("fecha_oral", ""),
                    "hora_oral_real": oral.get("hora_oral_real", ""),
                    "hora_oral_fin_estimada": oral.get("hora_oral_fin_estimada", ""),
                    "horario_oral_autorizado": oral.get("horario_oral_autorizado", ""),
                    "nombre_pdf": oral.get("nombre_pdf", ""),
                }
            )
        else:
            combined.update(
                {
                    "matched_oral": False,
                    "fecha_oral": "",
                    "hora_oral_real": "",
                    "hora_oral_fin_estimada": "",
                    "horario_oral_autorizado": "",
                    "nombre_pdf": "",
                }
            )

        rows.append(combined)

    return pd.DataFrame(rows)


def create_trinity_pdf_data(row, fecha_escrito, horario_escrito, fecha_emision):
    has_written = bool(row.get("has_written", False))
    has_oral = bool(row.get("has_oral", False))

    datos = {
        "nombre_alumno": limpiar(row.get("nombre_alumno", "")),
        "dni": limpiar(row.get("dni", "")),
        "examen": limpiar(row.get("examen", "")),
        "fecha_emision": fecha_emision,
        "fecha_escrito": fecha_escrito if has_written else "",
        "horario_escrito": horario_escrito if has_written else "",
        "fecha_oral": limpiar(row.get("fecha_oral", "")) if has_oral else "",
        "horario_oral_autorizado": limpiar(row.get("horario_oral_autorizado", "")) if has_oral else "",
    }

    return datos


# ---------- STREAMLIT UI ----------

modo = st.radio("Modo", ["Individual", "Excel Masivo", "Trinity Exam Auto"])

tipos_documento = [
    "Justificante de clase",
    "Justificante de examen",
    "Justificante de asistencia a clases",
]


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
            "observaciones": st.text_input(
                "Observaciones",
                "El alumno/a asiste regularmente a clase según el horario indicado.",
            ),
        }

    if st.button("Generar PDF"):
        nombre = limpiar(datos.get("nombre_alumno", ""))

        if nombre == "":
            st.error("Falta el nombre del alumno/a.")
        else:
            pdf = crear_pdf_por_tipo(tipo, datos)

            st.download_button(
                "Descargar PDF",
                pdf,
                f"{tipo.replace(' ', '_')}_{safe_filename(nombre)}.pdf",
                "application/pdf",
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

                    filename = f"{tipo.replace(' ', '_')}_{safe_filename(nombre)}.pdf"
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
                    "application/zip",
                )


elif modo == "Trinity Exam Auto":
    st.subheader("Generar justificantes oficiales desde documentos Trinity")

    st.write(
        "Sube el Entry Sheet Excel y el Language Timetable PDF. "
        "La fecha y horario del examen escrito se introducen manualmente."
    )

    entry_file = st.file_uploader("Subir Entry Sheet Excel", type=["xlsx"])
    timetable_file = st.file_uploader("Subir Language Timetable PDF", type=["pdf"])

    fecha_escrito = st.text_input("Fecha examen escrito", "3 de junio de 2026")
    horario_escrito = st.text_input("Horario examen escrito", "09:00 h a 13:00 h")
    fecha_emision = st.text_input("Fecha de emisión", "1 de junio de 2026")

    if entry_file is not None and timetable_file is not None:
        if PdfReader is None:
            st.error("Falta pypdf. Añade pypdf a requirements.txt y reinicia la app.")
            st.stop()

        try:
            entry_df = read_trinity_entry_sheet(entry_file)
            timetable_df = parse_trinity_timetable_pdf(timetable_file)
            merged_df = merge_entry_and_timetable(entry_df, timetable_df)
        except Exception as e:
            st.error(f"Error leyendo los documentos Trinity: {e}")
            st.stop()

        st.success("Documentos Trinity leídos correctamente.")

        st.write("Vista previa de alumnos detectados:")
        preview_cols = [
            "nombre_alumno",
            "dni",
            "examen",
            "product",
            "candidate_no",
            "has_written",
            "has_oral",
            "matched_oral",
            "fecha_oral",
            "horario_oral_autorizado",
        ]
        existing_cols = [col for col in preview_cols if col in merged_df.columns]
        st.dataframe(merged_df[existing_cols])

        unmatched = merged_df[(merged_df["has_oral"] == True) & (merged_df["matched_oral"] == False)]

        if len(unmatched) > 0:
            st.warning(
                f"Hay {len(unmatched)} alumno(s) con Speaking & Listening que no se han encontrado en el PDF oral. "
                "Revisa la vista previa antes de generar."
            )

        if st.button("Generar ZIP Trinity"):
            zip_buffer = BytesIO()
            documentos_creados = 0

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for _, row in merged_df.iterrows():
                    nombre = limpiar(row.get("nombre_alumno", ""))

                    if nombre == "":
                        continue

                    datos = create_trinity_pdf_data(
                        row,
                        fecha_escrito=fecha_escrito,
                        horario_escrito=horario_escrito,
                        fecha_emision=fecha_emision,
                    )

                    # Skip if neither written nor oral is present
                    if limpiar(datos.get("fecha_escrito", "")) == "" and limpiar(datos.get("fecha_oral", "")) == "":
                        continue

                    pdf = crear_pdf_por_tipo("Justificante de examen", datos)

                    filename = f"Justificante_examen_{safe_filename(nombre)}.pdf"
                    zip_file.writestr(filename, pdf.getvalue())

                    documentos_creados += 1

            zip_buffer.seek(0)

            if documentos_creados == 0:
                st.error("No se ha creado ningún justificante.")
            else:
                st.success(f"ZIP Trinity generado correctamente con {documentos_creados} justificante(s).")

                st.download_button(
                    "Descargar ZIP Trinity",
                    zip_buffer,
                    "justificantes_trinity_simply_english.zip",
                    "application/zip",
                )
