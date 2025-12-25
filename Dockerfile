FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY agent.py .
COPY agent_zep.py .
COPY api_server.py .
COPY .env.example .env

# Create data directory
RUN mkdir -p /app/data/memory

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "api_server.py"]
