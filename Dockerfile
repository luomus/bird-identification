FROM python:3.9-slim

WORKDIR /app

# Install TensorFlow separately with increased timeout
# The model requires TensorFlow 2.14.0
COPY requirements-extra.txt .
RUN pip install --no-cache-dir --timeout=1000 -r requirements-extra.txt

RUN apt-get update
RUN apt-get install libexpat1 -y
RUN apt-get install curl -y

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "scripts.api:app", "--host", "0.0.0.0", "--port", "8000"]
