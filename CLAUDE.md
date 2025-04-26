# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Test Commands

- Run server: `python manage.py runserver`
- Run all tests: `python manage.py test`
- Run app tests: `python manage.py test <app_name>`
- Run single test: `python manage.py test <app_name>.tests.<TestClass>.<test_method>`
- Test options: `--failfast`, `--keepdb`, `-k <pattern>`, `--pdb`

## Code Style Guidelines

- **Imports**: Standard Python first, Django second, local apps last
- **Naming**: Models use CamelCase, variables/functions use snake_case
- **Docstrings**: Triple quotes with parameter documentation in Spanish
- **Error Handling**: Use try/except with logging from utils/logger.py
- **Logging**: Use log_function_call and log_db_operation decorators
- **Models**: Use verbose_name and help_text for fields, include Meta class
- **Indentation**: 4 spaces
- **Line Length**: Follow PEP 8 standards
- **Security**: Avoid logging sensitive data (see is_safe_to_log in logger.py)