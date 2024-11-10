from flask import Flask, send_file
import requests
from weasyprint import HTML
import google.generativeai as genai
import secret  # Asegura que el archivo tenga la clave API dentro de `secret.py`
from bs4 import BeautifulSoup
import ssl
import io

ssl._create_default_https_context = ssl._create_stdlib_context

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/medicamentos/<medicamento>")
def about(medicamento):
    #1) obtener el medicamento
    #2) búsqueda en web de ispch en alertas
    #3) impresion de la página en pdf
    #4) consulta a la IA si el medicamento encuentra alertas
    #5) obtener los nro de lote de la alerta
    #6) respuesta al usuario sobre alertas
    web = f"http://www.ispch.cl/categorias-alertas/anamed/?buscar={medicamento}"
    html = HTML(url=web)
    pdf = html.write_pdf()
    pdf_io = io.BytesIO(pdf)
    
    genai.configure(api_key=secret.Secrets().secret_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    pdf_gemini = genai.upload_file(pdf_io, mime_type='application/pdf')
    prompt = f"según el pdf adjunto hay elementos en la tabla que indican que el medicamento {medicamento} tiene alertas, respecto al pdf y la tabla adjunta, indica el número 1 si el medicamento tiene registros en la tabla, o el número 0 si el medicamento no tiene alertas. indica únicamente el número"
    response = model.generate_content([prompt, pdf_gemini])
    response_number = int(response.text)

    if response_number == 1:
        return f"<p>El medicamento {medicamento} tiene alertas</p>"
    else:  
        return f"<p>El medicamento {medicamento} no tiene alertas</p>"