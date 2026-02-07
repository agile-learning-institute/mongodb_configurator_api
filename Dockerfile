# Use Python 3.12 slim image
FROM python:3.12-slim

# Set the working directory
WORKDIR /opt/mongo_configurator

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for better caching
COPY Pipfile Pipfile.lock ./

# Install pipenv
RUN pip install pipenv

# Copy only the application code and necessary files
COPY configurator/ ./configurator/
COPY docs/ ./docs/
COPY README.md LICENSE ./

# Copy playground test cases for development/testing to /input
COPY tests/test_cases/passing_template/api_playground/* /input/api_config/
COPY tests/test_cases/passing_template/configurations/* /input/configurations/
COPY tests/test_cases/passing_template/dictionaries/* /input/dictionaries/
COPY tests/test_cases/passing_template/enumerators/* /input/enumerators/
COPY tests/test_cases/passing_template/migrations/* /input/migrations/
COPY tests/test_cases/passing_template/test_data/* /input/test_data/
COPY tests/test_cases/passing_template/types/* /input/types/

# Create build timestamp
RUN echo $(date +'%Y%m%d-%H%M%S') > /opt/mongo_configurator/configurator/API_BUILT_AT

# Install dependencies
RUN pipenv install --deploy --system

# Install Gunicorn for production
RUN pip install gunicorn

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /opt/mongo_configurator && \
    chown -R app:app /input && \
    find /input -type d -exec chmod 755 {} \; && \
    find /input -type f -exec chmod 644 {} \;

# Switch to non-root user
USER app

# Default API port (override with ARG when building; extenders set ENV API_PORT in their image)
ARG API_PORT=8081
ENV PYTHONPATH=/opt/mongo_configurator/configurator
ENV API_PORT=${API_PORT}
EXPOSE ${API_PORT}

# Bind at runtime using API_PORT so extenders can set ENV API_PORT and expose their port
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${API_PORT} --timeout 10 --preload configurator.server:app"]
