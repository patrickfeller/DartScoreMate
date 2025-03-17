FROM python:3.11-slim

WORKDIR /app

# copy project contents to /app 
COPY . /app

# install all required packages with uv
RUN pip install --upgrade pip && pip install uv

RUN uv pip compile pyproject.toml -o requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5000

WORKDIR /app/src/python

# run the Flask app object with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]