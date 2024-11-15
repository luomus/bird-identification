# Start from a slim image with Python
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install TensorFlow separately with increased timeout
# The model requires TensorFlow 2.14.0
RUN pip install --no-cache-dir --timeout=1000 tensorflow==2.14.0

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update
RUN apt-get install libexpat1

# Copy all source code
COPY . .

# Default command to keep container alive for interactive sessions or custom runs
CMD ["tail", "-f", "/dev/null"]
