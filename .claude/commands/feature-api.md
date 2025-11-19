---
description: Two-agent workflow to implement and validate a new API feature
argument-hint: detailed description of the new API feature to implement
---

You are orchestrating a two-agent workflow to implement and validate a new API feature for the FastAPI application in main.py.

**Feature Description:** {ARGS}

## Overview

This workflow uses two specialized sub-agents that collaborate iteratively:
1. **Developer Agent**: A Python/FastAPI expert that implements the feature
2. **Tester Agent**: An API tester that reviews, tests, and provides feedback

The workflow continues until the Tester Agent outputs "APPROVED".

---

## Task 1: Launch Developer Agent

Use the Task tool to launch a **general-purpose agent** with the following specifications:

**Agent Role:** Python Developer with FastAPI Expertise

**Agent Capabilities:**
- Write Python code (FastAPI endpoints, Pydantic models)
- Write HTML/CSS/JavaScript for frontend integration
- Modify the monolithic main.py structure
- Implement proper error handling and validation

**Agent Instructions:**

```
You are a Python developer with FastAPI expertise. Your task is to implement a new API feature.

**Feature Description:** {ARGS}

**Implementation Steps:**

1. **Analysis Phase:**
   - Read main.py to understand the current structure
   - Determine required Pydantic models (validation, constraints)
   - Design API endpoint(s) (path, method, parameters, responses)
   - Plan data_store changes (in-memory storage structure)
   - Plan frontend UI updates (HTML forms, JavaScript handlers)

2. **Break Down into Sub-Tasks:**
   Create a todo list with specific sub-tasks:
   - Add/modify Pydantic models
   - Create API endpoint(s) following async pattern
   - Update data_store structure if needed
   - Add HTML UI elements in read_root()
   - Add JavaScript for API interaction
   - Implement error handling and validation

3. **Implementation:**
   - Work through each sub-task systematically
   - Follow the existing code patterns in main.py
   - Ensure security (XSS prevention, input validation)
   - Maintain the monolithic single-file design
   - Add proper HTTP status codes and error responses

4. **Output:**
   Provide a summary of:
   - What was implemented
   - New endpoints and their purposes
   - Data models added/modified
   - Frontend changes made
   - Any assumptions or design decisions

**Important Constraints:**
- All code must be in main.py (lines 1-369 structure)
- Use in-memory data_store (no external databases)
- Follow existing patterns for consistency
- Include proper type hints and documentation
```

**Expected Output from Developer Agent:**
- Completed implementation in main.py
- Summary of changes made
- List of new endpoints and their paths

---

## Task 2: Launch Tester Agent

Use the Task tool to launch a **general-purpose agent** with the following specifications:

**Agent Role:** API Tester and Code Reviewer

**Agent Capabilities:**
- Examine and review Python code
- Test API endpoints using curl commands
- Identify security vulnerabilities
- Provide actionable feedback

**Agent Instructions:**

```
You are an API tester and code reviewer. Your task is to validate the implementation from the Developer Agent.

**Feature That Was Implemented:** {ARGS}

**Testing and Review Steps:**

1. **Code Review:**
   - Read main.py to examine the new implementation
   - Check for security issues:
     * XSS vulnerabilities (proper escaping)
     * SQL/NoSQL injection risks
     * Input validation on all fields
     * Proper error handling
   - Verify code follows existing patterns
   - Check Pydantic model constraints are appropriate
   - Ensure frontend integration is complete

2. **Server Status:**
   - Check if the server is running on port 8000
   - If NOT running: Start the server using:
     `/Users/mehulmathur/Opius/practice/subagents/venv/bin/python3 main.py`
   - Wait for server to be ready

3. **Endpoint Testing:**
   - Create curl commands with appropriate test data
   - Test all new endpoints (POST, GET, PUT, DELETE as applicable)
   - Test edge cases (invalid data, missing fields, boundary conditions)
   - Verify HTTP status codes
   - Validate response formats and data

4. **Provide Feedback:**

   If all checks pass:
   - Output: "APPROVED"
   - Provide summary of what was tested
   - List validated endpoints

   If improvements needed:
   - Output: "SUGGESTIONS"
   - Provide specific, actionable feedback with:
     * What needs to be fixed
     * Why it's an issue
     * Code examples or specific changes needed
   - Reference specific line numbers in main.py
   - Prioritize issues (critical security issues first)

**Output Format:**

## Code Review Results
[Security findings, pattern compliance, validation checks]

## Test Results
[Curl commands executed and their responses]

## Verdict
APPROVED or SUGGESTIONS

[If APPROVED: summary]
[If SUGGESTIONS: detailed actionable feedback]
```

**Expected Output from Tester Agent:**
- Code review findings
- Test results with curl commands
- Verdict: "APPROVED" or "SUGGESTIONS" with specific feedback

---

## Workflow Execution

1. **Launch Developer Agent** (Task 1) and wait for implementation completion
2. **Launch Tester Agent** (Task 2) and wait for review results
3. **If Tester outputs "SUGGESTIONS":**
   - Pass the feedback back to a new Developer Agent instance
   - Repeat the cycle until Tester outputs "APPROVED"
4. **If Tester outputs "APPROVED":**
   - Workflow complete
   - Present final summary to user

**Note:** The agents are stateless, so each iteration requires launching new agent instances with context from previous iterations.
