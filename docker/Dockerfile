FROM python:3.13-slim-bookworm

# Set work directory in the container
WORKDIR /app

# Install curl and uv
RUN pip install uv

# Copy requirements files
COPY ../pyproject.toml ../uv.lock ./

# Install dependencies using uv
RUN uv sync

# Copy the rest of the application
COPY .. .

# Add virtual environment bin to path
ENV PATH="/app/.venv/bin:$PATH"

# Activate the virtual environment first then run the chainlit app
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]