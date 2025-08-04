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

# Copy playground test cases for development/testing
COPY tests/test_cases/passing_template/api_playground/* /playground/api_config/
COPY tests/test_cases/passing_template/configurations/* /playground/configurations/
COPY tests/test_cases/passing_template/dictionaries/* /playground/dictionaries/
COPY tests/test_cases/passing_template/enumerators/* /playground/enumerators/
COPY tests/test_cases/passing_template/migrations/* /playground/migrations/
COPY tests/test_cases/passing_template/test_data/* /playground/test_data/
COPY tests/test_cases/passing_template/types/* /playground/types/
RUN chmod -R 777 /playground

# Create build timestamp
RUN echo $(date +'%Y%m%d-%H%M%S') > /opt/mongo_configurator/configurator/API_BUILT_AT

# Install dependencies
RUN pipenv install --deploy --system

# Install Gunicorn for production
RUN pip install gunicorn

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /opt/mongo_configurator && \
    chown -R app:app /playground

# Switch to non-root user
USER app

# Expose the port
EXPOSE 8081

# Set environment variables
ENV PYTHONPATH=/opt/mongo_configurator/configurator
ENV API_PORT=8081

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8081", "--timeout", "10", "--preload", "configurator.server:app"]
