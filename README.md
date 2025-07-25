# MongoDB Configurator API

This project builds a the [MongoDB Configurator](https://github.com/agile-learning-institute/mongodb_configurator) API. This API supports the [MongoDB Configurator SPA](https://github.com/agile-learning-institute/mongodb_configurator_spa)

## Quick Start

### Prerequisites

- [Python](https://www.python.org/downloads/) 3.12 or later
- [Pipenv](https://pipenv.pypa.io/en/latest/installation.html)
- [StepCI](https://github.com/stepci/stepci/blob/main/README.md)
- [Docker Desktop](https://docs.docker.com/get-started/get-docker/)
- [MongoDB Compass](https://www.mongodb.com/products/compass) *optional*

### Quick Start
```bash
# Clone the repository
git clone git@github.com:agile-learning-institute/mongodb_configurator_api.git
cd mongodb_configurator_api
pipenv install --dev
pipenv run service
# Open http://localhost:8082/
```

### Developer Commands

```bash
# Run unit tests
pipenv run test

# Select a test_case for the server
export INPUT_FOLDER=./tests/test_cases/small_sample
export INPUT_FOLDER=./tests/test_cases/large_sample
export INPUT_FOLDER=./tests/test_cases/playground

# Set Debug Mode if needed
export LOGGING_LEVEL=DEBUG

#####################
# Running test server  - uses INPUT_FOLDER setting# 
pipenv run database     # Start the backing mongo database
pipenv run dev          # Start the server locally - expects database to be running
pipenv run debug        # Start locally with DEBUG logging
pipenv run batch        # Run locally in Batch mode (process and exit)

#####################
# Building and Testing the container (before a PR)
pipenv run container    # Build the container
pipenv run api          # Run the DB and API containers
pipenv run service      # Run the DB, API, and SPA containers
# visit http://localhost:8082 

pipenv run down         # Stops all testing containers

################################
# Black Box Testing with StepCI 
export INPUT_FOLDER=./tests/test_cases/stepci
pipenv run api
pipenv run stepci

```

## Separation of Concerns
The /configurator directory contains source code.
```
configurator/
├── routes/                     # Flask HTTP Handlers
│   ├── config_routes.py            # API Config Routes
│   ├── configuration_routes.py     # Configuration Routes
│   ├── database_routes.py          # Database Routes
│   ├── dictionary_routes.py        # Dictionary Routes
│   ├── enumerator_routes.py        # Enumerator Routes
│   ├── migration_routes.py         # Migration Routes
│   ├── test_data_routes.py         # Test Data Routes
│   ├── type_routes.py              # Type Routes
├── services/                   # Processing, Rendering Models
│   ├── configuration_services.py   # Configuration Services
│   ├── dictionary_services.py      # Dictionary Services
│   ├── enumerator_service.py       # Enumerator Services
│   ├── template_service.py         # Template Services
│   ├── type_services.py            # Type Services
├── utils/                      # Utilities
│   ├── config.py                   # API Configuration
│   ├── configurator_exception.py   # Exception Classes
│   ├── ejson_encoder.py            # Extended JSON Encoder
│   ├── file_io.py                  # File IO Wrappers
│   ├── mongo_io.py                 # MongoDB Wrappers
│   ├── route_decorators.py         # Route Decorators
│   ├── version_manager.py          # Version Manager
│   ├── version_number.py           # Version Number utility
├── server.py                   # Application Entrypoint
```

## Testing
The `tests/` directory contains python unit tests, stepci black box, and testing data.
```
tests/
├── test_server.py          # Server.py unit tests
├── integration/            # Integration tests dependent on backing services
├── models/                 # Model class unit tests
├── routes/                 # Route class unit tests
├── services/               # Service layer unit tests
├── utils/                  # Utility unit tests
├── stepci/                 # API Black Box testing
├── test_cases/             # Test data 
│   ├── failing_*/          # Integration Test data for failure use cases
│   ├── failing_not_parsable/   # Non yaml/json files
│   ├── failing_refs/           # Circular/Missing Refs
│   ├── passing_*/          # Integration Test data for success use cases
│   ├── passing_complex_refs/   # one_of plus refs
│   ├── passing_config_files/   # API Config file testing
│   ├── passing_empty/          # Minimum valid input
│   ├── passing_process/        # More complex processing
│   ├── passing_template/       # Playground / new project template
│   ├── passing_type_renders/   # Custom type render testing
│   ├── playground/         # Playground for interactive testing
│   ├── stepci/             # Configuration for step ci testing - setup/tear down in tests

```
The Docker build will package passing_template into the containers /playground folder to support playground deployments.

## API Documentation

The complete API documentation with interactive testing is available:
- [API Server docs/index.html](http://localhost:8081/docs/index.html) if the API is running
- GoLive on [index.html](./docs/index.html)

The Swagger UI provides:
- Interactive endpoint testing
- Auto-generated curl commands for each endpoint
- Request/response schemas
- Parameter documentation

### Quick API Examples

```bash
# Health check
curl -X GET http://localhost:8081/api/health

# Get current configuration
curl -X GET http://localhost:8081/api/config/

# List all configurations
curl -X GET http://localhost:8081/api/configurations/

# Process all configurations
curl -X POST http://localhost:8081/api/configurations/

# Lock all types
curl -X PATCH http://localhost:8081/api/types/
```
---
