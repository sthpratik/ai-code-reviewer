# Custom Project Guidelines

The AI Code Review Agent supports project-specific coding standards through custom guidelines files. This feature allows teams to define their own coding standards that are automatically included in all code reviews.

## Overview

When a code review is triggered, the system automatically checks for a custom guidelines file at `.amazonq/rules/coding-standards.md`. If found, the content is loaded and combined with the base review standards, providing comprehensive and project-specific code reviews.

## Setup

### 1. Create Directory Structure

```bash
mkdir -p .amazonq/rules
```

### 2. Create Guidelines File

Create `.amazonq/rules/coding-standards.md` with your project-specific standards:

```markdown
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

## Language-Specific Guidelines

### Python
- Use type hints for better code clarity
- Follow PEP 8 style guidelines
- Prefer f-strings for string formatting
- Use list/dict comprehensions for simple transformations

### JavaScript/TypeScript
- Use const/let instead of var
- Prefer async/await over Promise chains
- Use TypeScript strict mode when available
- Follow consistent naming conventions (camelCase)

### Java
- Follow standard naming conventions (camelCase for methods, PascalCase for classes)
- Use appropriate access modifiers
- Prefer composition over inheritance
- Handle checked exceptions appropriately

## Best Practices
- Follow DRY (Don't Repeat Yourself) principle
- Use version control effectively with meaningful commit messages
- Keep dependencies up to date and minimize unnecessary dependencies
- Consider backwards compatibility when making API changes
```

## Features

### Automatic Detection
- The system automatically checks for the guidelines file during every code review
- No configuration changes or command-line flags required
- Works with both local and Bitbucket PR reviews

### Language Agnostic
- Support guidelines for any programming language
- Mix multiple languages in a single guidelines file
- Generic guidelines apply to all code

### Team Collaboration
- Guidelines file can be version controlled with your code
- Share consistent standards across the entire team
- Update guidelines as your project evolves

### Flexible Format
- Use standard Markdown formatting for easy readability
- Organize guidelines with headers and bullet points
- Include code examples and explanations

## Usage Examples

### Frontend Project Guidelines

```markdown
# Frontend Coding Standards

## React/TypeScript Guidelines
- Use functional components with hooks instead of class components
- Implement proper prop types or TypeScript interfaces
- Use React.memo for performance optimization when appropriate
- Follow the single responsibility principle for components

## CSS/Styling
- Use CSS modules or styled-components for component styling
- Follow BEM naming convention for CSS classes
- Ensure responsive design for all screen sizes
- Maintain consistent spacing and typography

## Accessibility
- Include proper ARIA labels and roles
- Ensure keyboard navigation support
- Maintain proper color contrast ratios
- Test with screen readers

## Performance
- Implement lazy loading for routes and components
- Optimize images and assets
- Use React.lazy and Suspense for code splitting
- Monitor bundle size and performance metrics
```

### Backend API Guidelines

```markdown
# Backend API Coding Standards

## API Design
- Follow RESTful principles for endpoint design
- Use consistent HTTP status codes
- Implement proper error handling and responses
- Version your APIs appropriately

## Database
- Use parameterized queries to prevent SQL injection
- Implement proper indexing for query performance
- Use transactions for data consistency
- Follow database naming conventions

## Security
- Implement proper authentication and authorization
- Use HTTPS for all API endpoints
- Validate and sanitize all input data
- Implement rate limiting and request throttling

## Logging and Monitoring
- Log all important events and errors
- Use structured logging with consistent formats
- Implement health check endpoints
- Monitor API performance and error rates
```

### Mobile App Guidelines

```markdown
# Mobile App Coding Standards

## iOS (Swift)
- Follow Swift naming conventions and style guide
- Use proper memory management with ARC
- Implement proper error handling with Result types
- Use SwiftUI for new UI development

## Android (Kotlin)
- Follow Kotlin coding conventions
- Use proper lifecycle management for activities/fragments
- Implement proper dependency injection
- Use Jetpack Compose for new UI development

## Cross-Platform Considerations
- Ensure consistent user experience across platforms
- Handle platform-specific features appropriately
- Optimize for different screen sizes and orientations
- Test on multiple devices and OS versions
```

## Integration with Base Standards

Custom guidelines are combined with the base review standards defined in `config/review_standards.yaml`. The AI reviewer considers both sets of standards when evaluating code:

1. **Base Standards**: General software engineering best practices
2. **Custom Guidelines**: Project-specific requirements and conventions
3. **Combined Review**: Comprehensive evaluation using both standard sets

## Best Practices

### Writing Effective Guidelines

1. **Be Specific**: Provide concrete examples and actionable advice
2. **Stay Current**: Update guidelines as your project and team evolve
3. **Be Consistent**: Ensure guidelines align with your existing codebase
4. **Include Rationale**: Explain why certain practices are important
5. **Keep It Manageable**: Don't overwhelm with too many rules

### Team Adoption

1. **Collaborative Creation**: Involve the entire team in creating guidelines
2. **Regular Reviews**: Periodically review and update guidelines
3. **Training**: Ensure all team members understand the guidelines
4. **Enforcement**: Use the automated reviews to enforce standards consistently

### Maintenance

1. **Version Control**: Keep guidelines in your main repository
2. **Documentation**: Document any changes and the reasoning behind them
3. **Feedback Loop**: Use review results to improve guidelines over time
4. **Consistency**: Ensure guidelines don't conflict with base standards

## Troubleshooting

### Guidelines Not Loading

If custom guidelines aren't being included in reviews:

1. **Check File Location**: Ensure the file is at `.amazonq/rules/coding-standards.md`
2. **Verify Content**: Make sure the file has content (not empty)
3. **File Permissions**: Ensure the file is readable
4. **Path Issues**: Use relative paths from your project root

### Testing Guidelines

You can test if guidelines are loaded by running:

```bash
python -c "
from code_reviewer import CodeReviewer
reviewer = CodeReviewer()
if 'custom_guidelines' in reviewer.standards:
    print('✅ Custom guidelines loaded')
    print(f'Length: {len(reviewer.standards[\"custom_guidelines\"])} characters')
else:
    print('❌ Custom guidelines not found')
"
```

## Examples in Action

When custom guidelines are active, you'll see more specific and relevant feedback:

**Without Custom Guidelines:**
```
Issue: Variable name 'x' is not descriptive
Recommendation: Use more meaningful variable names
```

**With Custom Guidelines:**
```
Issue: Variable name 'x' violates project naming standards
Recommendation: Use descriptive variable names as specified in project guidelines. 
For loop counters, use 'index' or 'i' for simple cases, or descriptive names 
like 'user_index' for complex scenarios.
```

The AI reviewer becomes more context-aware and provides feedback that aligns with your specific project requirements and team conventions.
