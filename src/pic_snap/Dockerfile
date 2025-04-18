# base image with streamlit already installed
FROM python:3.11-slim

# update working directory
WORKDIR /app

# copy relevant data
RUN mkdir -p src/pic_snap
COPY src/pic_snap src/pic_snap

# update package manager and install packages
RUN apt-get update && apt-get install -y curl
RUN pip install --upgrade pip 
RUN pip install -r src/pic_snap/requirements.txt


# expose port
EXPOSE 8501

# healthcheck as suggested in https://docs.streamlit.io/deploy/tutorials/docker
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

