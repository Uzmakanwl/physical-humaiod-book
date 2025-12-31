# Data Model: ROS 2 Educational Module

## Educational Content Entities

### Chapter
- **name**: string - Title of the chapter
- **slug**: string - URL-friendly identifier for the chapter
- **module**: reference to Module - The module this chapter belongs to
- **content**: string - The main content in Markdown format
- **objectives**: array of strings - Learning objectives for the chapter
- **examples**: array of references to CodeExample - Related code examples
- **prerequisites**: array of strings - Knowledge required before reading
- **duration**: number - Estimated reading/learning time in minutes

### Module
- **name**: string - Name of the educational module
- **slug**: string - URL-friendly identifier for the module
- **description**: string - Overview of the module
- **chapters**: array of references to Chapter - Ordered list of chapters
- **targetAudience**: array of strings - Who the module is designed for
- **difficulty**: enum (beginner, intermediate, advanced) - Overall difficulty level
- **estimatedDuration**: number - Total estimated time to complete the module

### CodeExample
- **title**: string - Descriptive title of the example
- **language**: string - Programming language (e.g., "python", "urdf")
- **code**: string - The actual code content
- **description**: string - Explanation of what the code does
- **chapter**: reference to Chapter - Which chapter this example belongs to
- **usage**: string - How to run or use the example
- **relatedConcepts**: array of strings - ROS 2 concepts demonstrated by the example

### Concept
- **name**: string - Name of the ROS 2 concept
- **slug**: string - URL-friendly identifier
- **definition**: string - Clear definition of the concept
- **examples**: array of references to CodeExample - Examples demonstrating the concept
- **relatedConcepts**: array of references to Concept - Other concepts this relates to
- **chapter**: reference to Chapter - Primary chapter where concept is taught

## Relationships
- Module 1-* Chapter: Each module contains multiple chapters in a specific order
- Chapter 1-* CodeExample: Each chapter can reference multiple code examples
- Chapter 1-* Concept: Each chapter introduces and explains multiple concepts
- Concept *-* Concept: Concepts can have relationships with other concepts
- CodeExample 1-* Concept: Code examples demonstrate specific concepts

## Validation Rules
1. Chapter.slug must be unique within a Module
2. Module.slug must be globally unique
3. All required fields must be present
4. CodeExample.language must be a supported language
5. Concept.name must be unique within the system
6. Chapter.objectives must contain at least one objective
7. CodeExample.usage must be provided when code is present

## State Transitions
- Content Creation Flow: DRAFT → REVIEW → APPROVED → PUBLISHED
- Chapter states track the progress of content development and quality assurance