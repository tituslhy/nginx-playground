FROM python:3.13-slim

# Set work directory in the container
WORKDIR /app

# Install curl and uv
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/* && \
    curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy requirements files
COPY ../pyproject.toml ../uv.lock ./

# Install dependencies using uv
RUN uv sync

# Copy environment file
COPY ../.env .env

# Copy the rest of the application
COPY .. .

# Command to run the application
CMD ["python", "main.py"]