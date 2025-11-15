# Project-Specific Coding Standards

## General Code Review Guidelines

### Code Quality
- Use meaningful variable and function names that clearly express intent
- Keep functions small and focused on a single responsibility
- Avoid deep nesting (max 3-4 levels)
- Remove commented-out code and debug statements
- Ensure consistent code formatting throughout the project

### Error Handling
- Always handle errors gracefully with appropriate error messages
- Use specific error types rather than generic exceptions
- Log errors with sufficient context for debugging
- Fail fast when invalid inputs are detected

### Documentation
- All public APIs must have clear documentation
- Include usage examples for complex functionality
- Document any non-obvious business logic or algorithms
- Keep README and documentation up to date

### Performance
- Avoid premature optimization but be mindful of obvious inefficiencies
- Consider memory usage for data-intensive operations
- Use appropriate data structures for the use case
- Profile code when performance issues are suspected

### Security
- Never commit secrets, API keys, or sensitive data
- Validate and sanitize all external inputs
- Use secure communication protocols (HTTPS, TLS)
- Follow principle of least privilege for access controls

### Testing
- Write tests for critical business logic
- Include both positive and negative test scenarios
- Use descriptive test names that explain the expected behavior
- Mock external dependencies to ensure test isolation

### Language-Specific Guidelines

#### Python
- Use type hints for better code clarity
- Follow PEP 8 style guidelines
- Prefer f-strings for string formatting
- Use list/dict comprehensions for simple transformations

#### JavaScript/TypeScript
- Use const/let instead of var
- Prefer async/await over Promise chains
- Use TypeScript strict mode when available
- Follow consistent naming conventions (camelCase)

#### Java
- Follow standard naming conventions (camelCase for methods, PascalCase for classes)
- Use appropriate access modifiers
- Prefer composition over inheritance
- Handle checked exceptions appropriately

#### General Best Practices
- Follow DRY (Don't Repeat Yourself) principle
- Use version control effectively with meaningful commit messages
- Keep dependencies up to date and minimize unnecessary dependencies
- Consider backwards compatibility when making API changes
