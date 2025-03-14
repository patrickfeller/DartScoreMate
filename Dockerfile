FROM python:3.11-slim

WORKDIR /app

# copy the contents to /app 
COPY . /app

# install all required packages
RUN pip install --upgrade pip 

RUN pip install -r src/python/requirements.txt

EXPOSE 5000

WORKDIR /app/src/python

# run the Flask app object with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]