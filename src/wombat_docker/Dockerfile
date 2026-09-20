# Linux hosts only.
#
# docker build -f src/wombat_docker/Dockerfile -t slug:latest src/
# docker run -v /var/wombat:/mnt/wombat --name slug slug:latest
# docker run -e stuntbox=validate -v /var/wombat:/mnt/wombat --name slug slug:latest
#
FROM python:3.11-slim

WORKDIR /app

# Create and activate virtualenv first
RUN python -m venv /app/venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV FAILURE_DIR=/mnt/wombat/failure
ENV FRESH_DIR=/mnt/wombat/fresh/slug
ENV SUCCESS_DIR=/mnt/wombat/slug/success

# Copy requirements and install them inside the venv
COPY wombat_docker/requirements.txt ./
RUN $VIRTUAL_ENV/bin/pip install --no-cache-dir -r requirements.txt

COPY wombat_docker/slug_app.py ./
COPY wombat_docker/validator.py ./
COPY helper ./helper

RUN mkdir -p /mnt/wombat
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "slug_app.py"]
