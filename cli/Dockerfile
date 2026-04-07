FROM python:3.9-slim

WORKDIR /app

# Install TensorFlow separately with increased timeout
# The model requires TensorFlow 2.14.0
COPY cli/requirements-tf.txt .
RUN pip install --no-cache-dir --timeout=1000 -r requirements-tf.txt

RUN apt-get update && apt-get install -y libexpat1 curl && rm -rf /var/lib/apt/lists/*

COPY cli/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared package and cli package
COPY shared/ /app/shared/
COPY cli/ /app/cli/

CMD ["bash"]

