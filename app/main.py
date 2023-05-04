import base64
import csv
import os
import shutil
import tempfile
import zipfile
from io import BytesIO
from typing import Optional

import pandas as pd
from fastapi import FastAPI, File, Form, Response, UploadFile
from fastapi.responses import HTMLResponse, Response, StreamingResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def show_html():
    with open('./index.html', 'r') as html_file:
        content = html_file.read()
        return content
    
@app.get("/excel", response_class=HTMLResponse)
async def show_html():
    with open('./excel_parser.html', 'r') as html_file:
        content = html_file.read()
        return content
 
@app.post("/generate_html")
async def generate_html(file: UploadFile = File(...)):
    # Create a temporary directory to extract the uploaded ZIP file
    with tempfile.TemporaryDirectory() as temp_dir:
        zip = zipfile.ZipFile(BytesIO(await file.read()), 'r')
        zip.extractall(temp_dir)

        # Open and process the CSV file
        with open(os.path.join(temp_dir, 'eblast.csv'), 'r', newline='', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            data = [row for row in reader]

        data.sort(key=lambda x: x['Image Name'])

        rows = []
        current_row = []
        for row in data:
            if current_row and row['Image Name'].split("-")[0] == current_row[0]['Image Name'].split("-")[0]:
                current_row.append(row)
            else:
                rows.append(current_row)
                current_row = [row]
        rows.append(current_row)

        # Create the HTML file
        os.makedirs(os.path.join(temp_dir, 'images'), exist_ok=True)
        html_file_path = os.path.join(temp_dir, 'index.html')
        with open(html_file_path, 'w') as html_file:
            html_file.write("""
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="UTF-8">
<style>
table {
 border-collapse: collapse;
}
body {
    max-width: 650px;
    margin: 0 auto;
}
.row {
    display: flex;
}
img {
    display: block;
}

</style>
</head>
<body>
<table cellspacing="0" border="0" fr-original-style cellpadding="0">
<tbody>
            """)
            for row in rows:
                # html_file.write('<tr class="row">\n')
                html_file.write("""
                <table cellspacing="0" border="0" fr-original-style cellpadding="0">
                <tbody>
                <tr>
                """)
                for image in row:
                    html_file.write('<td >\n')
                    if image["Link"]:
                        html_file.write(f'<a href="{image["Link"]}">')
                    image_path = os.path.join(temp_dir, 'images', image["Image Name"])
                    zip_path = f'images/{image["Image Name"]}'
                    with zip.open(zip_path) as zip_file:
                        with open(image_path, 'wb') as f:
                            shutil.copyfileobj(zip_file, f)
                    html_file.write(f'<img src="data:image/png;base64,{base64.b64encode(open(image_path, "rb").read()).decode()}" alt="{image["Subject"]}" title="{image["Subject"]}">')
                    if image["Link"]:
                        html_file.write('</a>')
                    html_file.write('</td>\n')
                html_file.write("""
                </tr>
                </tbody>
                </table>
                """)
            html_file.write("""
</tbody>
</table>
</body>
</html>
            """)

        # Return the generated HTML file for download
        file_name = 'index.html'
        file_path = html_file_path
        file_size = os.path.getsize(file_path)
        return StreamingResponse(open(file_path, 'rb'), media_type='text/html', headers={
            'Content-Disposition': f'attachment; filename="{file_name}"',
            'Content-Length': str(file_size),
        })

@app.post("/hello-world")
def hello_world(file: UploadFile = File(...)):
    return {"filename": file.filename}


# @app.post("/filter_excel")
# async def filter_excel(header_row: int, filter_word: str, file: UploadFile = File(...)):
#     # Load the Excel file into a DataFrame, with column names from the specified header row
#     df = pd.read_excel(file.file, header=header_row-1)

#     # Filter the DataFrame by the specified keyword in the "Load Work Type" column
#     filtered_df = df[df['Load Work Type'].str.contains(filter_word)]

#     # Write the filtered DataFrame to a new sheet in the same Excel file
#     excel_file = BytesIO()
#     with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
#         filtered_df.to_excel(writer, sheet_name='Filtered')

#     # Set the file pointer to the beginning of the stream
#     excel_file.seek(0)

#     # Create the response object with the Excel file contents
#     response = Response(content=excel_file.getvalue(),
#                         media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
#                         headers={'Content-Disposition': f'attachment; filename="filtered_excel.xlsx"'})

#     return response

@app.post("/filter_excel")
async def filter_excel(
    header_row: Optional[int] = Form(None),
    new_sheet_name: Optional[str] = Form(None),
    filter_word: str = Form(...),
    file: UploadFile = File(...)):

    header_row = int(header_row or 2)
    new_sheet_name = new_sheet_name or 'Filtered Data'
    # Leer el archivo Excel en un DataFrame
    excel_file = BytesIO(await file.read())
    df = pd.read_excel(excel_file, header=header_row-1)

    # Aplicar el filtro al DataFrame
    filtered_df = df[df['Load Work Type'].str.contains(filter_word)]

    # Agregar una hoja nueva con los datos filtrados
    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a') as writer:
        filtered_df.to_excel(writer, sheet_name=new_sheet_name)

    # Establecer el puntero del archivo al inicio del stream
    excel_file.seek(0)

    # Crear el objeto de respuesta con el contenido del archivo Excel
    response = Response(content=excel_file.getvalue(),
                        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        headers={'Content-Disposition': f'attachment; filename="{new_sheet_name}.xlsx"'})

    return response