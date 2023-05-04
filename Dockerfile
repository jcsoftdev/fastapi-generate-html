FROM python:3.9

WORKDIR /app

COPY ./app/requirements.txt /app/requirements.txt
COPY ./app/index.html /app/index.html
COPY ./app/excel_parser.html /app/excel_parser.html

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]