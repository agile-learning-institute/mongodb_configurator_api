# MongoDB Configurator API

This project builds the [MongoDB Configurator](https://github.com/agile-learning-institute/mongodb_configurator) API. This API packages configurations for deployment, and supports the [MongoDB Configurator SPA](https://github.com/agile-learning-institute/mongodb_configurator_spa)

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
pipenv run dev          # Run the dev server - expects database to be running
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

### Custom Templates (for API extenders)

The API uses default templates when creating new collections via `POST /api/configurations/collection/{name}`.

#### Dictionary template (`default_new_dictionary.yaml`)

**Default value**: An object root with `_id`, `name`, `description`, `status`, `created`, `last_saved`:
```yaml
name: root
description: "{{description}}"
type: object
properties:
  - name: _id
    type: identifier
    required: true
  - name: name
    type: word
    required: true
  - name: description
    type: sentence
    required: false
  - name: status
    type: enum
    enums: default_status
    required: true
  - name: created
    type: breadcrumb
    required: true
  - name: last_saved
    type: breadcrumb
    required: true
```

**Location** (checked in order):
1. **Override**: `{INPUT_FOLDER}/{API_CONFIG_FOLDER}/templates/default_new_dictionary.yaml`
2. **Built-in**: `configurator/templates/default_new_dictionary.yaml`

#### Configuration template (`default_new_configuration.yaml`)

**Default value**: Default `add_indexes` for the initial version (nameIndex, statusIndex, createdIndex, savedIndex).

**Location** (checked in order):
1. **Override**: `{INPUT_FOLDER}/{API_CONFIG_FOLDER}/templates/default_new_configuration.yaml`
2. **Built-in**: `configurator/templates/default_new_configuration.yaml`

**Playground/Docker**: The Dockerfile loads `tests/test_cases/passing_template/api_playground/templates/` into `/input/api_config/templates/`. Both templates are included.

To provide custom templates in your extended image:
1. Create your template files with placeholders `{{collection_name}}` and `{{description}}` (dictionary only)
2. Copy to `/input/api_config/templates/` in your Dockerfile
3. Ensure the `api_config/templates/` directory exists

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
The Docker build packages `passing_template` into the container's `/input` folder for playground deployments. The `api_playground/` subfolder (config files and `templates/default_new_dictionary.yaml`) is copied to `/input/api_config/`.

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

**IMPORTANT**: The MongoDB Configurator API is designed with an intentional security model that reflects its three primary use cases:

### Use Case 1: Data Engineer (Local Development)
- **Purpose**: Edit and create configuration files locally
- **Security Posture**: Minimal security overhead - intentionally permissive
- **Configuration**: `BUILT_AT=Local` (from file), `MONGODB_REQUIRE_TLS=false`
- **Capabilities**: Full write access to all configuration files. Note that these configurations are still in git change management, so changes aren't permanent till committed. This mode Will only run with a local containerized MongoDB backing database.

### Use Case 2: Software Engineer (Local Development)
- **Purpose**: Apply packaged configurations in local dev database, view deployed configurations
- **Security Posture**: Minimal security overhead - read operations and local processing
- **Configuration**: `BUILT_AT=<timestamp>` (from file), `MONGODB_REQUIRE_TLS=false`
- **Capabilities**: Read access, local database operations, configuration viewing

### Use Case 3: Cloud/Production (Batch Processing)
- **Purpose**: Apply packaged configurations in production databases
- **Security Posture**: Secure batch-style runtime with no API access
- **Configuration**: `BUILT_AT=<timestamp>`, `MONGODB_REQUIRE_TLS=true`, `AUTO_PROCESS=true`, `EXIT_AFTER_PROCESSING=true`
- **Capabilities**: No API, batch processing, secure MongoDB connections


The [Config utility singleton](./configurator/utils/config.py) is used to manage all API Configuration options. See the code to understand options, and the [Configurator SRE Guide](https://github.com/agile-learning-institute/mongodb_configurator/blob/main/SRE.md) for more information.