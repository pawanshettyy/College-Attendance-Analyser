FROM python:3.9-slim

WORKDIR /app

# Install required system dependencies for PDF processing and health check
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    libpoppler-cpp-dev \
    pkg-config \
    python3-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Define health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Set the entrypoint
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]