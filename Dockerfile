FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create data directory for storage
RUN mkdir -p data

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["python", "web_app.py"]