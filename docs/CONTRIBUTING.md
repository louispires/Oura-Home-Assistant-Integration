# Contributing to Oura Ring v2 Custom Component

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature or bugfix
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.13 or higher
- Home Assistant development environment
- Oura Ring account with API access

### Local Development

1. Clone the repository:

```bash
git clone https://github.com/louispires/oura-v2-custom-component.git
cd oura-v2-custom-component
```

1. Copy the integration to your Home Assistant config:

```bash
cp -r custom_components/oura /path/to/homeassistant/config/custom_components/
```

1. Restart Home Assistant

## Code Standards

### Python Style

- Follow PEP 8 style guidelines
- Use type hints for all functions and methods
- Use meaningful variable and function names
- Add docstrings to all classes and methods

### Home Assistant Standards

- Follow [Home Assistant integration quality scale](https://developers.home-assistant.io/docs/integration_quality_scale_index/)
- Use async functions where appropriate
- Implement proper error handling
- Use the DataUpdateCoordinator pattern for API calls
- Follow the OAuth2 flow implementation guidelines

### Code Formatting

We use:

- `black` for code formatting
- `isort` for import sorting
- `pylint` for linting
- `mypy` for type checking

## Testing

### Automated Tests

This project includes a comprehensive automated test suite covering API behavior, coordinator processing, statistics import/reconciliation, setup flow, sensors, and diagnostics.

#### Running Tests with Docker (Recommended)

```bash
# Run all tests
docker compose -f docker-compose.test.yml run --rm test

# Run specific test file
docker compose -f docker-compose.test.yml run --rm test pytest tests/test_sensor.py -v

# Run specific test
docker compose -f docker-compose.test.yml run --rm test pytest tests/test_sensor.py::test_sensor_device_info -v
```

#### Test Structure

- **`tests/test_api.py`**: API client behavior and endpoint handling
- **`tests/test_api_reauth_propagation.py`**: OAuth reauth propagation paths
- **`tests/test_application_credentials.py`**: OAuth endpoint behavior and fallback logic
- **`tests/test_config_flow.py`**: Config flow and options flow
- **`tests/test_coordinator.py`**: Coordinator data processing and orchestration
- **`tests/test_entity_categories.py`**: Entity category and state class checks
- **`tests/test_integration_setup.py`**: Setup/unload lifecycle validation
- **`tests/test_ring_battery.py`**: Ring battery and charging diagnostics
- **`tests/test_sensor.py`**: Sensor entity behavior and attributes
- **`tests/test_statistics.py`**: Statistics metadata and transformation logic
- **`tests/test_statistics_import.py`**: Historical and reconciliation import coverage

#### Test Fixtures

The `tests/conftest.py` file provides reusable fixtures:

- `mock_config_entry`: Configured ConfigEntry with OAuth2 tokens
- `mock_hass`: Mocked HomeAssistant instance
- `mock_oura_api_client`: API client with sample data
- `mock_coordinator_with_data`: Coordinator with pre-populated data

See `tests/README.md` for detailed testing documentation and the latest per-file count.

### Manual Testing

Before submitting a pull request:

1. Test the integration in a real Home Assistant environment
2. Verify all sensors are working correctly
3. Test OAuth2 authentication flow
4. Check for any error messages in logs

## Pull Request Process

1. **Update Documentation**: Update README.md if you add new features
2. **Add Comments**: Comment your code where necessary
3. **Test**: Ensure all functionality works as expected
4. **Commit Messages**: Use clear and descriptive commit messages
5. **PR Description**: Clearly describe what your changes do and why

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Example:

```
feat: Add heart rate variability sensor

Added new sensor for tracking HRV trends over time.
Includes proper state class and device class.

Closes #123
```

## Reporting Issues

When reporting issues, please include:

1. Home Assistant version
2. Integration version
3. Detailed description of the issue
4. Steps to reproduce
5. Relevant log entries
6. Expected vs actual behavior

## Feature Requests

We welcome feature requests! Please:

1. Check if the feature has already been requested
2. Clearly describe the feature and its use case
3. Explain how it would benefit users
4. Consider contributing the feature yourself

## Questions?

If you have questions about contributing, feel free to:

1. Open an issue with the "question" label
2. Join the discussion in existing issues
3. Check the [Home Assistant developer documentation](https://developers.home-assistant.io/)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing!
