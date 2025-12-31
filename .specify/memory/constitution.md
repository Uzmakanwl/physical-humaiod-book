<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.1.0
- Modified principles: All principles updated to reflect AI/Spec-Driven Book with Embedded RAG Chatbot project
- Added sections: Technical Standards, Development Workflow, RAG Chatbot Requirements
- Removed sections: None
- Templates requiring updates: ✅ Updated
- Follow-up TODOs: None
-->
# AI/Spec-Driven Book with Embedded RAG Chatbot Constitution

## Core Principles

### I. Spec-First Development (NON-NEGOTIABLE)
Every feature and component must be defined in a formal specification before implementation begins. Specifications must include clear acceptance criteria, interfaces, and validation methods. This ensures reproducible, well-understood development outcomes and prevents scope creep.

### II. AI-Assisted Development
Leverage Claude Code and other AI tools for all aspects of development including content creation, code generation, testing, and documentation. AI assistance must enhance human creativity and productivity while maintaining technical accuracy and quality standards.

### III. Technical Accuracy and Originality
All content and code must be technically accurate, derived from official documentation, and completely original with 0% plagiarism tolerance. All examples must be runnable and kept up-to-date with current APIs and best practices. No deprecated APIs or frameworks allowed.

### IV. Docusaurus-Based Documentation Standard
All book content must be authored in Markdown/MDX using Docusaurus as the publishing platform. This ensures consistent formatting, proper navigation, search capability, and seamless deployment to GitHub Pages with minimal maintenance overhead.

### V. Spec-Kit Plus Compliance
All project artifacts must comply with Spec-Kit Plus methodology including specs, plans, tasks, and Prompt History Records. This ensures systematic, traceable, and reproducible development processes aligned with best practices.

### VI. Free-Tier Compatible Architecture

All infrastructure and service choices must be compatible with free tiers of cloud services (Neon Serverless Postgres, Qdrant Cloud Free Tier, etc.) to ensure accessibility and cost-effectiveness. Architecture decisions must consider budget constraints while maintaining functionality.

## Technical Standards

### Content Standards
- All book content written in Markdown/MDX using Docusaurus
- Content generated/refined via Claude Code with human oversight
- Specs defined and enforced using Spec-Kit Plus methodology
- Runnable, up-to-date code examples only - no theoretical snippets
- Technical accuracy verified against official documentation

### RAG Chatbot Requirements
- Embedded in the book UI for seamless user experience
- Uses OpenAI Agents/ChatKit SDKs for intelligent Q&A
- FastAPI backend for scalability and performance
- Neon Serverless Postgres for metadata and session storage
- Qdrant Cloud (Free Tier) for vector storage and retrieval
- Answers strictly sourced from indexed book content only
- Supports user-selected-text-only Q&A for precise context

### Deployment Standards
- Published via Docusaurus to GitHub Pages
- Automated deployment pipeline required
- Clear, reproducible setup instructions for contributors
- Version control for all content and configuration

## Development Workflow

### Content Creation Process
- All content follows spec-first approach with clear requirements
- Claude Code used for initial content generation and refinement
- Human review and validation required for technical accuracy
- Peer review process for all substantial content changes
- Regular updates to ensure code examples remain current

### Quality Assurance
- All code examples must be tested and verified as runnable
- Content must pass plagiarism detection
- Technical accuracy validated against official documentation
- Cross-reference checking to ensure consistency
- Accessibility compliance for UI components

### Collaboration Standards
- Clear attribution for all AI-assisted contributions
- Proper version control practices for collaborative work
- Regular Prompt History Records (PHRs) for all development activities
- Architectural Decision Records (ADRs) for significant technology choices

## Governance

All team members must adhere to these constitutional principles. Deviations require formal amendment process with clear justification. All pull requests must verify compliance with these principles. Complexity must be justified with clear benefits. Use this constitution as the primary guidance for all development decisions.

**Version**: 1.1.0 | **Ratified**: 2025-12-22 | **Last Amended**: 2025-12-22
