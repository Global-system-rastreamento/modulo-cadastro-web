FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y \
    wkhtmltopdf \
    xvfb \
    fonts-liberation \
    libfontconfig1 \
    libxrender1 \
    libxext6 \
    wget \
    libreoffice \
    libreoffice-script-provider-python \
    python3-uno \
    unoconv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV WKHTMLTOPDF_PATH=/usr/bin/wkhtmltopdf

EXPOSE 8501

CMD ["streamlit", "run", "main.py"]