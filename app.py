import streamlit as st

st.set_page_config(
    page_title="Simply English Document Generator",
    page_icon="📄"
)

st.title("📄 Simply English Document Generator")

modo = st.radio(
    "What would you like to do?",
    [
        "Create one document",
        "Create documents from Excel"
    ]
)

tipo = st.selectbox(
    "Document type",
    [
        "Exam Attendance Certificate",
        "Mandatory Class Attendance",
        "Enrollment Certificate",
        "Custom Certificate"
    ]
)

if modo == "Create one document":

    nombre = st.text_input("Student Name")
    dni = st.text_input("DNI")
    fecha = st.text_input("Date")

    if st.button("Generate PDF"):
        st.success("PDF generation will go here.")

else:

    archivo = st.file_uploader(
        "Upload Excel",
        type=["xlsx"]
    )

    if archivo:
        st.success("Excel uploaded successfully.")  
