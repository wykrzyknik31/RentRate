# GitHub Copilot Instructions for RentRate

This file provides guidance to GitHub Copilot for generating code suggestions that align with the RentRate project's standards and best practices.

## Project Overview

RentRate is a rental rate management application. When working on this project, keep in mind the domain-specific requirements for rental management, pricing calculations, and user interactions.

## Code Style

### General Guidelines
- Write clean, readable, and maintainable code
- Use meaningful variable and function names that clearly describe their purpose
- Keep functions small and focused on a single responsibility
- Avoid deep nesting; prefer early returns for error handling

### Naming Conventions
- Use camelCase for variables and functions
- Use PascalCase for classes and components
- Use UPPER_SNAKE_CASE for constants
- Use descriptive names that convey intent

### Comments and Documentation
- Write comments for complex logic or non-obvious code
- Document all public APIs, functions, and classes
- Keep comments up-to-date with code changes
- Use TODO comments with assignees for future improvements

## Architecture

### Project Structure
- Keep related files organized in logical directories
- Separate concerns: models, views, controllers, services, utilities
- Place shared/common code in appropriate utility modules
- Keep configuration separate from application logic

### Design Patterns
- Follow SOLID principles
- Prefer composition over inheritance
- Use dependency injection for better testability
- Implement proper error handling and logging

## Testing

### Test Requirements
- Write unit tests for all business logic
- Include integration tests for API endpoints
- Test edge cases and error scenarios
- Aim for high test coverage (target: 80%+)

### Test Structure
- Use descriptive test names that explain what is being tested
- Follow the Arrange-Act-Assert pattern
- Keep tests isolated and independent
- Mock external dependencies appropriately

## Security

### Best Practices
- Never hardcode credentials, API keys, or sensitive information
- Use environment variables for configuration
- Validate and sanitize all user inputs
- Implement proper authentication and authorization
- Follow the principle of least privilege

## Error Handling

- Use appropriate error types and messages
- Log errors with sufficient context for debugging
- Provide user-friendly error messages
- Handle edge cases gracefully
- Never expose sensitive information in error messages

## Performance

- Optimize database queries and use appropriate indexes
- Implement caching where appropriate
- Avoid N+1 query problems
- Use pagination for large data sets
- Profile and optimize critical paths

## Version Control

### Commit Messages
- Write clear, descriptive commit messages
- Use present tense ("Add feature" not "Added feature")
- Reference issue numbers when applicable
- Keep commits focused on a single change

### Pull Requests
- Write clear PR descriptions explaining the changes
- Keep PRs small and focused
- Request reviews from appropriate team members
- Address review comments promptly

## Accessibility

- Ensure code is accessible to all users
- Follow WCAG guidelines for web content
- Use semantic HTML elements
- Provide appropriate ARIA labels where needed

## Dependencies

- Keep dependencies up-to-date
- Review security vulnerabilities regularly
- Minimize the number of dependencies
- Choose well-maintained, popular libraries
- Document the purpose of each dependency

## Documentation

- Maintain up-to-date README files
- Document setup and installation procedures
- Provide examples for common use cases
- Keep API documentation current
- Document environment variables and configuration options

## Code Review Guidelines

When reviewing code suggestions:
- Verify correctness and functionality
- Check for security vulnerabilities
- Ensure code follows project conventions
- Validate test coverage
- Consider performance implications
- Assess maintainability and readability

## Domain-Specific Guidelines

### Rental Management
- Handle currency and monetary values with appropriate precision
- Consider timezone differences for rental periods
- Validate rental dates (start date before end date, no overlaps)
- Implement proper rate calculations with support for different time periods

### Data Validation
- Validate all rental-related data (dates, rates, properties)
- Ensure data integrity for financial calculations
- Implement appropriate constraints and business rules
- Handle edge cases in pricing and availability

## Additional Resources

- Follow language-specific best practices and idioms
- Refer to official documentation for frameworks and libraries
- Stay updated with security advisories
- Consider scalability in design decisions

---

*These instructions help GitHub Copilot provide more relevant and context-aware suggestions. Update this file as the project evolves and new patterns emerge.*
