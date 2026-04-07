FROM python:3.9-slim

WORKDIR /app

# Install TensorFlow separately with increased timeout
# The model requires TensorFlow 2.14.0
COPY api/requirements-tf.txt .
RUN pip install --no-cache-dir --timeout=1000 -r requirements-tf.txt

RUN apt-get update
RUN apt-get install libexpat1 -y
RUN apt-get install curl -y

COPY api/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy shared package and api package
COPY shared/ /app/shared/
COPY api/ /app/api/

EXPOSE 8000

CMD ["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "8000"]
