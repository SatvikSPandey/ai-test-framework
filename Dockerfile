FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies needed by Selenium, Playwright, and pdfplumber
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    chromium \
    chromium-driver \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first so Docker can cache this layer
# If requirements.txt doesn't change, Docker skips reinstalling packages
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers inside the container
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy the entire project into the container
COPY . .

# Create the outputs directory
RUN mkdir -p outputs

# Expose ports for Streamlit and FastAPI
EXPOSE 8501 8000

# Default command runs the Streamlit UI
CMD ["streamlit", "run", "ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]