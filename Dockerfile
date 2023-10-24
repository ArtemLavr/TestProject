FROM python:3.9

RUN pip install --upgrade pip


WORKDIR /code

COPY . .

RUN pip install -r app/requirements.txt

CMD ["python", "app/api.py"]