# Agents.md

This file serves as a generic guide for interacting with LLM-driven CLI tools (such as Claude Code, Codex, Gemini CLI, or OpenCode) when working within this repository.

## Core Principles for AI Agents

When interacting with this codebase, always adhere to the following principles to ensure productivity and safety:

### 1. Context Awareness
- **Read Before Writing**: Always read the contents of a file before suggesting or applying modifications.
- **Understand the Architecture**: Refer to `CLAUDE.md` to understand the high-level service structure, networking patterns (NGINX/Ingress), and deployment workflow.
- **Respect the Environment**: Be aware that the application relies on specific Kubernetes secrets and environment variables for functionality.

### 2. Tool Usage & Execution
- **Use Dedicated Tools**: Prefer using specialized tools (e.g., `Glob` for finding files, `Grep` for searching content, `Edit` for modifications) over raw shell commands like `ls`, `cat`, or `sed`.
- **Verify Changes**: After applying a change, verify the impact by running relevant commands (e.g., `helm lint` for Helm charts or `docker build` for Docker images).

- **Plan Complex Tasks**: For non-trivial implementation tasks, use a "Plan" approach: explore the codebase, design an approach, and present it for user approval before execution.

### 3. Code Integrity & Security
- **No Secrets in Code**: Never hardcode API keys (OpenAI, Tavily), passwords, or credentials. Always use environment variables or secret management patterns.
- **Maintain Formatting**: Follow existing code style and indentation. Pay attention to `markdownlint` warnings if editing documentation files like `CLAUDE.md` or `README.md`.
- **Avoid Destructive Actions**: Do not perform destructive operations (e.g., `rm -rf`, `git reset --hard`, or deleting Kubernetes resources) without explicit user authorization.

### 4. Continuous Improvement
- **Update Documentation**: If you discover new patterns, architectural details, or critical workflows during your task, update `CLAUDE.md` to benefit future sessions.
- **Refine the Plan**: If an implementation approach fails, diagnose the root cause through investigation rather than blindly retrying the same command.

## Workflow Reference

| Task Type | Recommended Approach |
| :--- | :--- |
| **Exploration** | Use `Glob` and `Grep` to map out the codebase structure. |
| **Bug Fixing** | Identify the service, trace the logs (via Phoenix/Kubectl), and apply focused edits. |
| **Feature Addition** | Plan the changes in `src/`, update `app.py` if necessary, and verify with the container stack. |
| **Deployment Testing** | Use `helm template` and `helm lint` to validate Kubernetes configurations. |
| **Infrastructure Change** | Update `docker-compose.yml` or `helm/values.yaml` and trigger a rebuild/redeploy. |
