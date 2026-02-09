# Java Copilot Instructions for NHS FHIR Validator Lambda

---
description: 'Brief description of the instruction purpose and scope'
applyTo: 'src/**/*.java'
---

## Project Overview
This is an AWS Lambda-based FHIR validator service that validates FHIR resources against UK Core and NHS Digital implementation guides. The project uses Java 21, Maven, HAPI FHIR library, and AWS Lambda runtime.

## Code Style and Conventions

### Package Structure
- Follow the existing package structure: `software.nhs.fhirvalidator.*`
- Main packages:
  - `controller` - Main validation logic and controllers
  - `handler` - AWS Lambda handlers
  - `service` - Business logic services
  - `util` - Utility classes
  - `models` - Data models
  - `configuration` - Configuration classes

### Naming Conventions
- Use descriptive class names that clearly indicate their purpose
- Controllers should end with `Controller` (e.g., `ValidateController`)
- Handlers should end with `Handler` (e.g., `HandlerStream`)
- Services should end with `Service` or descriptive names (e.g., `ImplementationGuideParser`, `CapabilityStatementApplier`)
- Utility classes should end with `Utils` (e.g., `FhirUtils`, `OperationOutcomeUtils`)
- Use camelCase for methods and variables
- Constants should be UPPER_SNAKE_CASE

### Class Structure
- Always include proper package declarations
- Group imports logically (Java standard library, third-party, project imports)
- Include class-level Javadoc comments explaining the purpose
- Initialize logger as: `Logger log = LogManager.getLogger(ClassName.class);`
- Place constructor parameters and fields at the top of the class

### Logging
- Use Log4j2 for logging: `import org.apache.logging.log4j.LogManager;` and `import org.apache.logging.log4j.Logger;`
- Initialize logger: `Logger log = LogManager.getLogger(ClassName.class);`
- Use appropriate log levels: `log.info()`, `log.error()`, `log.debug()`, `log.warn()`
- Include meaningful context in log messages
- Log exceptions with both message and stack trace: `log.error(ex.getMessage(), ex);`

### Error Handling
- Use try-catch blocks appropriately
- Wrap checked exceptions in RuntimeException when necessary with descriptive messages
- Log errors before throwing exceptions
- Use specific exception types when available (e.g., `InvalidRequestException`, `DataFormatException`)

### FHIR-Specific Patterns
- Use HAPI FHIR library classes and interfaces
- Common FHIR imports:
  - `import org.hl7.fhir.r4.model.*;` for FHIR R4 models
  - `import org.hl7.fhir.instance.model.api.IBaseResource;`
  - `import ca.uhn.fhir.context.FhirContext;`
  - `import ca.uhn.fhir.validation.FhirValidator;`
- Always work with FHIR resources through proper HAPI FHIR APIs
- Use `FhirContext` for parsing and serialization operations
- Handle both single resources and Bundle resources appropriately

### AWS Lambda Patterns
- Implement `RequestStreamHandler` for stream-based handlers
- Use `@Logging(clearState = true)` annotation for Lambda Powertools logging
- Handle initialization in constructor to benefit from Lambda container reuse
- Use environment variables for configuration (e.g., `PROFILE_MANIFEST_FILE`)

### Testing Patterns
- Use JUnit 5 for testing (`import org.junit.jupiter.api.Test;`)
- Use static imports for assertions: `import static org.junit.jupiter.api.Assertions.*;`
- Use Mockito for mocking: `import static org.mockito.Mockito.mock;`
- Include `LogCaptor` for testing log output: `import nl.altindag.log.LogCaptor;`
- Test class names should end with `Test`

### Stream API Usage
- Use Java Streams appropriately for collection processing
- Common patterns seen in codebase:
  ```java
  list.stream()
      .map(transformation)
      .filter(predicate)
      .collect(Collectors.toList());
  ```

### Utility Class Patterns
- Make utility classes final with private constructor
- Include this pattern for utility classes:
  ```java
  private UtilityClassName() {
      throw new IllegalStateException("Utility class");
  }
  ```

### Resource Management
- Use proper resource management with try-with-resources when needed
- Handle IOException appropriately when working with resources
- Use `ResourceUtils.getResourceContent()` for loading classpath resources

### JSON Processing
- Use Gson for JSON processing
- Common imports: `import com.google.gson.*;`
- Handle `JsonSyntaxException` when parsing JSON

## Dependencies
- Java 21
- HAPI FHIR library
- AWS Lambda runtime
- AWS Lambda Powertools
- Log4j2 for logging
- JUnit 5 for testing
- Mockito for mocking
- Gson for JSON processing

## Best Practices
1. Always include proper error handling and logging
2. Use descriptive variable and method names
3. Include Javadoc comments for public methods and classes
4. Follow the existing architectural patterns in the codebase
5. Ensure proper resource cleanup
6. Use appropriate FHIR validation patterns
7. Handle both single resources and Bundles in validation logic
8. Use environment variables for configuration
9. Implement proper Lambda initialization patterns for performance
10. Write comprehensive unit tests with proper mocking

## Common Code Patterns

### Controller Pattern
```java
public class ExampleController {
    private final SomeService service;
    Logger log = LogManager.getLogger(ExampleController.class);
    
    public ExampleController(String configParam) {
        this.service = new SomeService(configParam);
    }
    
    public ResultType performOperation(InputType input) {
        log.info("Starting operation with input: {}", input);
        try {
            return service.process(input);
        } catch (Exception ex) {
            log.error("Error processing operation: {}", ex.getMessage(), ex);
            throw new RuntimeException("Operation failed", ex);
        }
    }
}
```

### Validation Pattern
```java
public OperationOutcome validate(String resourceContent) {
    try {
        IBaseResource resource = fhirContext.newJsonParser().parseResource(resourceContent);
        ValidationResult result = validator.validateWithResult(resource);
        return (OperationOutcome) result.toOperationOutcome();
    } catch (DataFormatException ex) {
        log.error("Invalid FHIR format: {}", ex.getMessage());
        return createErrorOperationOutcome(ex.getMessage());
    }
}
```

When generating Java code for this project, always follow these patterns and conventions to maintain consistency with the existing codebase.