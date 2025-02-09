We use Django 5.1 as our primary web framework. When providing guidance, prioritize Django best practices and follow the standard project structure.

Use Python 3.13 or later for code examples and snippets. Prefer modern Python features when applicable.

We run our development environment on Windows and use Docker for containerization. Any setup or troubleshooting advice should consider Windows-specific paths and Docker workflows.

Assume that the reader has an advanced understanding of Python and Django.

Dark mode is preferred for design-related examples or suggestions.

Use try-except blocks for error handling in all Python code examples. Ensure proper logging within these blocks for better error tracking.

Add logging to all Python code examples. Sentry is used for error tracking, so include Sentry integration in error handling examples.

Prefetch related objects in Django ORM queries. Ensure to handle related object queries efficiently to optimize performance.

Use database indexes in Django models. Consider indexing frequently queried fields to improve lookup speed.

Assume Sqlite as the default database unless specified otherwise.

When discussing package management, prefer uv for dependency management.

For testing, we use pytest with pytest-django, so test-related examples should follow this approach.

We follow Google style docstrings and use type hints extensively in our codebase.

Our project structure uses `config` as the base Django app, which contains settings, URLs, and other configurations. The main app is named `core`.

Docker Compose is used for managing services. Prefer Docker Compose configurations when explaining deployment and environment setup.

For version control, assume we use Git with GitHub, and provide examples using Git best practices.
