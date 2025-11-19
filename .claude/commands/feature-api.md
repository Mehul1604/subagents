---
description: Three-agent workflow to implement, validate, and deploy a new API feature
argument-hint: detailed description of the new API feature to implement
---

You are orchestrating a three-agent workflow to implement, validate, and deploy a new API feature for the FastAPI application in main.py.

**Feature Description:** {ARGS}

## Overview

This workflow uses three specialized sub-agents that collaborate iteratively:
1. **Developer Agent**: A Python/FastAPI expert that implements the feature
2. **Tester Agent**: An API tester that reviews, tests, and provides feedback
3. **GitHub Agent**: A version control specialist that creates tests, commits, and pushes code

The workflow continues until the Tester Agent outputs "APPROVED", then the GitHub Agent handles deployment.

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

## Task 3: Launch GitHub Agent (After Approval)

Use the Task tool to launch a **general-purpose agent WITH THE GITHUB SKILL** with the following specifications:

**Agent Role:** Version Control and Testing Specialist

**Agent Skill:** github (located at .claude/skills/github.md)

**Agent Capabilities:**
- Create comprehensive Python test files using pytest
- Run test suites and verify all tests pass
- Execute git operations (commit, push, branch management)
- Use GitHub MCP tools for PR creation and repository management
- Update requirements.txt with testing dependencies

**Agent Instructions:**

```
You are a GitHub and testing specialist with the github skill. Your task is to test, commit, and push the approved feature implementation.

**Feature That Was Implemented and Approved:** {ARGS}

**Your Workflow:**

1. **Create Comprehensive Tests:**
   - Create `tests/` directory if it doesn't exist
   - Create `tests/test_main.py` with pytest test cases
   - Write tests for ALL new endpoints implemented
   - Include tests for:
     * Valid input cases (happy path)
     * Invalid input cases (validation errors)
     * Edge cases (boundary conditions)
     * Error handling
   - Use FastAPI TestClient for endpoint testing
   - Add fixtures to clear data_store between tests

2. **Update Dependencies:**
   - Check if `pytest>=8.0.0` is in requirements.txt, add if missing
   - Check if `httpx>=0.27.0` is in requirements.txt, add if missing
   - These are needed for the test framework and TestClient

3. **Run Test Suite:**
   - Execute: `/Users/mehulmathur/Opius/practice/subagents/venv/bin/python3 -m pytest tests/ -v`
   - Verify ALL tests pass
   - If any test fails, debug and fix before proceeding
   - Do NOT commit if tests fail

4. **Git Operations:**
   - Check current status: `git status`
   - Review changes: `git diff`
   - Stage files: `git add main.py tests/ requirements.txt`
   - Create descriptive commit with format:
     ```
     feat: Add [feature name]

     - New endpoint(s): [list endpoints]
     - Data models: [list models]
     - Frontend changes: [summary]
     - Tests added: [number] test cases covering all scenarios

     🤖 Generated with Claude Code (https://claude.com/claude-code)

     Co-Authored-By: Claude <noreply@anthropic.com>
     ```
   - Commit the changes
   - Push to origin main: `git push origin main`

5. **Output Summary:**
   Provide a detailed summary including:
   - Test files created and number of test cases
   - Test execution results (all passed/failures)
   - Git commit message used
   - Files committed
   - Push status
   - GitHub repository link

**Important:**
- Do NOT skip test creation - it's mandatory
- Do NOT commit if tests fail
- Follow the github skill guidelines precisely
- Use the python interpreter at: /Users/mehulmathur/Opius/practice/subagents/venv/bin/python3
```

**Expected Output from GitHub Agent:**
- Test files created with comprehensive coverage
- Test execution results (all passing)
- Git commit completed with descriptive message
- Code pushed to GitHub successfully
- Summary of all operations

---

## Workflow Execution

1. **Launch Developer Agent** (Task 1) and wait for implementation completion
2. **Launch Tester Agent** (Task 2) and wait for review results
3. **If Tester outputs "SUGGESTIONS":**
   - Pass the feedback back to a new Developer Agent instance
   - Repeat the cycle (Tasks 1-2) until Tester outputs "APPROVED"
4. **If Tester outputs "APPROVED":**
   - Launch GitHub Agent (Task 3) with the github skill
   - Wait for testing, commit, and push completion
   - Workflow complete
   - Present final summary to user

**Note:** The agents are stateless, so each iteration requires launching new agent instances with context from previous iterations. The GitHub Agent MUST use the github skill for proper testing and version control operations.
