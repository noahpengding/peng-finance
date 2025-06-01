FROM python:3.12-slim

ENV PATH="/app/.venv/bin:$PATH"

# Set working directory
WORKDIR /app

RUN pip install --upgrade pip && \
    pip install hatchling uv

COPY pyproject.toml ./
RUN uv venv .venv  && \
    uv pip install --no-cache-dir .

# Copy application code
COPY . /app

# Expose port and run Streamlit via uv
EXPOSE 8501
ENTRYPOINT ["uv", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]