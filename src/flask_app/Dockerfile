FROM sinfallas/base-python-uv:3.11
WORKDIR /app
RUN mkdir -p src
# copy project contents to /app 
COPY src src
COPY pyproject.toml .

# install all required packages with uv

# remark on opencv-python in docker: will cause dependency errors, use opencv-python-headless instead: 
# https://stackoverflow.com/questions/55313610/importerror-libgl-so-1-cannot-open-shared-object-file-no-such-file-or-directo

RUN pip install --upgrade pip 

# RUN uv pip compile pyproject.toml -o requirements.txt
# RUN pip install -r requirements.txt

## resolve package dependencies with uv and download packages with pip

RUN mkdir envs && uv venv envs/.venv

ENV PATH="/app/envs/.venv/bin:${PATH}"

RUN uv pip install . 

EXPOSE 5000
