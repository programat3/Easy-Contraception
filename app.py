from flask import Flask, render_template, send_file
import requests
from weasyprint import HTML,Document
import google.generativeai as genai
import pdfx
import ssl
import io
import os
import tempfile
import gc
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ssl._create_default_https_context = ssl._create_stdlib_context

app = Flask(__name__)

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=80)

@app.route("/")
def hello_world():
    return "<p>No habilitado</p>"

@app.route("/<medicamento>")
def about(medicamento):
    web = f"http://www.ispch.cl/categorias-alertas/anamed/?buscar={medicamento}"
    html = HTML(url=web)
    pdf_m = html.write_pdf()
    pdf_io = io.BytesIO(pdf_m)
    lotes = []
    razones = ""
    fecha = ""
    med = medicamento.upper()
    genai.configure(api_key=os.environ.get('API_KEY'))
    generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    )
    pdf_gemini = genai.upload_file(pdf_io, mime_type='application/pdf')
    prompt = f"si no hay registros en la tabla, responde el número 0 separado por una coma otro 0. Si hay registros en la tabla, responde el número 1 separado por una coma de la fecha más nueva existente en la tabla, en formato DD-MM-AAAA."
    response = model.generate_content([prompt, pdf_gemini])
    response_number, date = response.text.split(',')
    response_number = int(response_number)

    if response_number == 1:
        temp_pdf = tempfile.NamedTemporaryFile(delete_on_close=False, suffix=".pdf")
        try:
            temp_pdf.write(pdf_m)
            temp_pdf_path = temp_pdf.name
            temp_pdf.close()

            pdf_x = pdfx.PDFx(temp_pdf_path)
            
            enlaces = pdf_x.get_references_as_dict()
            
            
        finally:
            del pdf_x
            gc.collect()
            os.remove(temp_pdf_path)
        urls = enlaces
        dia,mes,agno = date.split('-')
        alerta_url = ""
        for url in urls['pdf']:
            if  mes.strip() in str(url) and agno.strip() in str(url): 
                alerta_url = url
                break
        response_alerta = requests.get(alerta_url,verify=False)
        if response_alerta.status_code == 200:
            pdf_alerta = response_alerta.content
            pdf_alerta_io = io.BytesIO(bytes(pdf_alerta))
            pdf_gemini_alerta = genai.upload_file(pdf_alerta_io, mime_type='application/pdf')
            prompt_alerta = f"Según el pdf adjunto qué números de serie o lotes tienen alertas o han tenido alertas en el pasado, entrega sólo los números separados por comas"
            response_alerta_lotes = model.generate_content([prompt_alerta, pdf_gemini_alerta])
            prompt_razones = f"según el pdf adjunto, qué razones se dan para la alerta, si es que hay alguna, en español"
            response_alerta_razones = model.generate_content([prompt_razones, pdf_gemini_alerta])
            lotes = response_alerta_lotes.text.split(',')
            razones = response_alerta_razones.text
            alerta = True
            fecha = f'{dia} del {mes} del {agno}'
    else:  
       alerta = False
    return render_template('index.html',alerta=alerta,medicamento=med,lotes=lotes,razones=razones, fecha=fecha)

    