FROM python:3.11-slim

WORKDIR /app

# copy project contents to /app 
COPY src/flask_app .
COPY pyproject.toml .

# install all required packages with uv
RUN pip install --upgrade pip && pip install uv

RUN uv pip compile pyproject.toml -o requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5000
