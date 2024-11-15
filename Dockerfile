FROM python:3.9-slim

WORKDIR /app

# Install TensorFlow separately with increased timeout
# The model requires TensorFlow 2.14.0
RUN pip install --no-cache-dir --timeout=1000 tensorflow==2.14.0

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update
RUN apt-get install libexpat1

COPY . .

CMD ["tail", "-f", "/dev/null"]
