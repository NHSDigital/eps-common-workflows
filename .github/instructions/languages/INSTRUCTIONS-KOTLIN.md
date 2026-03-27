# Copilot Instructions for Kotlin Files

---
description: 'Brief description of the instruction purpose and scope'
applyTo: 'src/**/*.kt'
---
## Project Overview
This is a FHIR R4 validation service built with Spring Boot and Kotlin. The service validates FHIR resources against implementation guides and profiles using the HAPI FHIR library.

## Code Style and Conventions

### Package Structure
- Follow the established package structure: `com.example.fhirvalidator.{layer}`
- Layers: `controller`, `service`, `configuration`, `model`, `util`
- Test packages mirror main packages with same structure

### Class and Function Naming
- Use PascalCase for classes and interfaces
- Use camelCase for functions, variables, and properties
- Use descriptive names that clearly indicate purpose
- Example: `ValidateController`, `parseAndValidateResource()`

### Kotlin-Specific Patterns
- Use data classes for simple model objects (like `SimplifierPackage`)
- Prefer immutable properties (`val`) over mutable (`var`) when possible
- Use nullable types (`String?`) when values can be null
- Use safe call operator (`?.`) and Elvis operator (`?:`) for null handling
- Use `lateinit var` for dependency injection in tests with `@Mock` annotations

### Spring Framework Conventions
- Use constructor injection for dependencies (primary pattern in this codebase)
- Annotate configuration classes with `@Configuration`
- Annotate service classes with `@Service`
- Annotate REST controllers with `@RestController`
- Use `@Bean` methods in configuration classes
- Use `@PostMapping`, `@GetMapping` etc. for endpoint mapping

## Logging Patterns
- Use KotlinLogging library: `import io.github.oshai.kotlinlogging.KotlinLogging`
- Create logger instance: `private val logger = KotlinLogging.logger {}`
- Use structured logging with payload maps:
  ```kotlin
  logger.atError {
      message = "Error description"
      cause = exception
      payload = buildMap(capacity = 2) {
          put("key1", value1)
          put("key2", value2)
      }
  }
  ```
- Use string templates in log messages: `logger.info { "Processing message $requestId" }`

## FHIR-Specific Patterns
- Use HAPI FHIR library classes (`FhirContext`, `FhirValidator`, etc.)
- Handle FHIR resources with `IBaseResource` interface
- Use `OperationOutcome` for validation results
- Parse FHIR JSON using `fhirContext.newJsonParser()`
- Extract Bundle entries when processing Bundle resources
- Apply profiles and validate resources in service layer

## Error Handling
- Catch `DataFormatException` for parser errors
- Return structured `OperationOutcome` objects for validation errors
- Use meaningful error messages in diagnostics
- Include request IDs for traceability
- Log errors with appropriate context

## Testing Patterns
- Use JUnit 5 (`@Test`, `@ExtendWith`)
- Use Mockito for mocking (`@Mock`, `@InjectMocks`, `@ExtendWith(MockitoExtension::class)`)
- Test class names end with `Test`
- Use `internal` visibility for test classes
- Use descriptive test method names with underscores: `methodName_condition_expectedResult`
- Use `lateinit var` for mock objects and test subjects

## Dependency Injection
- Use constructor-based dependency injection as primary pattern
- Inject `FhirContext`, `FhirValidator`, and custom services
- Configuration classes provide `@Bean` methods
- Use Spring's IoC container for all service dependencies

## Utility Functions
- Create extension functions for common operations (like `createOperationOutcome`)
- Use top-level functions for utilities that don't require state
- Prefer functional programming patterns where appropriate
- Use collection operations (`map`, `filter`, `flatMap`) for data processing

## File Organization
- One public class per file
- File name should match the primary class name
- Group related utility functions in dedicated files
- Keep configuration separate from business logic

## Resource Management
- Use Spring Boot's resource management for FHIR packages
- Handle npm packages for implementation guides
- Use proper cleanup for validation support chains
- Cache expensive operations like snapshot generation

## API Design
- REST endpoints follow FHIR conventions (`$validate`)
- Use appropriate HTTP methods and status codes
- Accept both `application/json` and `application/fhir+json`
- Include proper request/response headers
- Support optional headers like `x-request-id`

## When writing new code:
1. Follow the existing architectural patterns
2. Use the established logging format
3. Include proper error handling
4. Write corresponding unit tests
5. Use Spring dependency injection
6. Handle FHIR resources appropriately
7. Maintain package structure conventions
8. Use Kotlin idioms and null safety features