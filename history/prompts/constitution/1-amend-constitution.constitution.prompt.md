---
id: 1
title: amend-constitution
stage: constitution
date: 2025-12-22
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 002-ros2-python-agent-integration
user: user
command: /sp.constitution
labels: [constitution, spec-driven, ai-book, rag-chatbot]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
 - .specify/templates/plan-template.md
 - .specify/templates/spec-template.md
 - .specify/templates/tasks-template.md
tests: []
---

## Prompt

```
/sp.constitution

Project: AI/Spec-Driven Book with Embedded RAG Chatbot

Objective:
Create and deploy a technical book using Claude Code and Spec-Kit Plus, published via Docusaurus
to GitHub Pages, with an embedded RAG chatbot for book-aware Q&A, including selected-text-only answers.

Core principles:
- Spec-first, AI-assisted development
- Technical accuracy from official documentation
- Clarity for professional developers
- Reproducible setup and deployment

Standards:
- Book written in Markdown/MDX using Docusaurus
- Content generated/refined via Claude Code
- Specs defined and enforced using Spec-Kit Plus
- Runnable, up-to-date code examples only

RAG chatbot:
- Embedded in the book UI
- Uses OpenAI Agents/ChatKit SDKs
- FastAPI backend
- Neon Serverless Postgres (metadata/sessions)
- Qdrant Cloud (Free Tier) for vectors
- Answers strictly from indexed book content
- Supports user-selected-text-only Q&A

Constraints:
- 0% plagiarism tolerance
- No deprecated APIs
- Free-tier–compatible services
- Clear
```

## Response snapshot

Updated the project constitution to reflect the AI/Spec-Driven Book with Embedded RAG Chatbot project. The new constitution includes:

1. Six core principles:
   - I. Spec-First Development (NON-NEGOTIABLE)
   - II. AI-Assisted Development
   - III. Technical Accuracy and Originality
   - IV. Docusaurus-Based Documentation Standard
   - V. Spec-Kit Plus Compliance
   - VI. Free-Tier Compatible Architecture

2. Additional sections:
   - Technical Standards (Content Standards, RAG Chatbot Requirements, Deployment Standards)
   - Development Workflow (Content Creation Process, Quality Assurance, Collaboration Standards)
   - Governance

3. Updated template files to align with the new constitution:
   - plan-template.md: Added constitutional check gates
   - spec-template.md: Added constitutional alignment check
   - tasks-template.md: Added constitutional compliance requirements

The constitution version was updated from 1.0.0 to 1.1.0 to reflect the addition of new principles and sections.

## Outcome

- ✅ Impact: Updated constitution to match project requirements and aligned templates
- 🧪 Tests: No tests required for this configuration change
- 📁 Files: Updated 4 files (.specify/memory/constitution.md, 3 template files)
- 🔁 Next prompts: Ready to proceed with feature specification and implementation
- 🧠 Reflection: Constitution now properly reflects the AI/Spec-Driven Book project with RAG chatbot requirements

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin feature specification based on new constitution