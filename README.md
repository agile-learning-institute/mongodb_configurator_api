# MongoDB Configurator API

This project builds a the [MongoDB Configurator](https://github.com/agile-learning-institute/mongodb_configurator) API. This API packages configurations for deployment, and supports the [MongoDB Configurator SPA](https://github.com/agile-learning-institute/mongodb_configurator_spa)

## Quick Start

NOTE: If you want to use the Configurator - see [MongoDB Configurator](https://github.com/agile-learning-institute/mongodb_configurator) for instructions. 

If you are an API developer looking to contribute - you're in the right place!

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
export INPUT_FOLDER=./tests/test_cases/passing_process
export INPUT_FOLDER=./tests/test_cases/passing_template
export INPUT_FOLDER=./tests/test_cases/stepci

# Set Debug Mode if needed
export LOGGING_LEVEL=DEBUG

#####################
# Running test server  - uses INPUT_FOLDER setting# 
pipenv run database     # Start the backing mongo database
pipenv run dev          # RUn the dev server - expects database to be running
pipenv run debug        # Start locally with DEBUG logging
pipenv run batch        # Run locally in Batch mode (process and exit)

#####################
# Building and Testing the container
pipenv run container    # Build the container
pipenv run service      # DB, API and SPA containers
pipenv run api          # DB, API containers, uses $INPUT_FOLDER
pipenv run playground   # DB, API /input (ignores $INPUT_FOLDER)
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
│   ├── enumerator_routes.py        # Enumeration Routes
│   ├── migration_routes.py         # Migration Routes
│   ├── test_data_routes.py         # Test Data Routes
│   ├── type_routes.py              # Type Routes
├── services/                   # Processing, Rendering Models
│   ├── property                    # Dictionary and Type Properties
│   │   ├── base.py                 # Base class for all types
│   │   ├── property.py             # Polymorphic Type factory
│   │   ├── {name}_type.py          # Type specific with render details
│   │   ├── ...
│   ├── service_base.py             # Base class for file based services ⭐️
│   ├── configuration_services.py   # ⭐️Configuration Services [Version]
│   ├── dictionary_services.py      # ⭐️Dictionary Services
│   ├── enumerator_service.py       # ⭐️Enumeration Services
│   ├── type_services.py            # ⭐️Type Services
│   ├── template_service.py         # Service to create new Config and Dictionary
│   ├── configuration_version.py    # Configuration Version
│   ├── enumerators.py              # Convenience wrapper for all [Enumeration]
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
├── integration/            # Integration tests dependent on backing test_case
├── routes/                 # Route class unit tests
├── services/               # Service layer unit tests
├── stepci/                 # API Black Box testing
├── utils/                  # Utility unit tests
├── test_cases/             # Test data 
│   ├── failing_*/          # Integration Test data for failure use cases
│   ├── passing_*/          # Integration Test data for success use cases
│   ├── passing_type_renders/   # Not in process_and_render tests
│   ├── playground/         # Playground for interactive testing
│   ├── stepci/             # Configuration for step ci testing - setup/tear down in tests

```
The Docker build will package passing_template into the containers /input folder to support playground deployments.

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
curl -X GET http://localhost:8081/api/health | jq

# Get current configuration
curl -X GET http://localhost:8081/api/config/ | jq

# List all configurations
curl -X GET http://localhost:8081/api/configurations/ | jq

# Process all configurations
curl -X POST http://localhost:8081/api/configurations/ | jq

# Lock all types
curl -X PATCH http://localhost:8081/api/types/ | jq

# Update a dictionary
curl -X PUT localhost:8081/api/dictionaries/sample.1.0.0.yaml/ \
  -H "Content-Type: application/json" \
  --data @./temp.json | jq
```
---

### Configurability
The [Config utility singleton](./configurator/utils/config.py) is used to manage all API Configuration options. See the code to understand options, and the [Configurator SRE Guide](https://github.com/agile-learning-institute/mongodb_configurator/blob/main/SRE.md) for more information.