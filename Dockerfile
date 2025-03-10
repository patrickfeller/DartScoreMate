FROM python:3.11-slim

# Set working directory to src/pyhton 
WORKDIR src/pyhton

# copy the contents to /app 
COPY . /app

# install all required packages
RUN pip install requirements.txt

# run the Flask app object located in src/python/main.py with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.python.main:app"]