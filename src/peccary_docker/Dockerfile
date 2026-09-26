#
# docker build -f src/peccary_docker/Dockerfile -t slug:latest src/
# docker run -v /var/peccary:/mnt/peccary --name slug slug:latest
# docker run -e stuntbox=loader -v /var/peccary:/mnt/peccary --name slug slug:latest
#
FROM python:3.11-slim

WORKDIR /app

# Create and activate virtualenv first
RUN python -m venv /app/venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV FAILURE_DIR=/mnt/peccary/failure
ENV FRESH_DIR=/mnt/peccary/slug/slug-v1

ENV DB_CONN=postgresql+psycopg2://slug_client:batabat@172.17.0.1:5432/slug

# Copy requirements and install them inside the venv
COPY peccary_docker/requirements.txt ./
RUN $VIRTUAL_ENV/bin/pip install --no-cache-dir -r requirements.txt

COPY helper/ ./helper/
COPY peccary_docker/slug_app.py ./
COPY peccary_docker/loader.py ./

RUN mkdir -p /mnt/peccary
CMD ["python", "slug_app.py"]
