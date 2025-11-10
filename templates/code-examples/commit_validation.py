# Git Commit Validation Example
# Use this pattern for ALL commit operations (orchestrator and agents)

import sys
sys.path.insert(0, '/home/jaguilar/aaxis/rnd/repositories/.claude/tools')
from commit_validator import safe_validate_before_commit

# Example 1: Orchestrator-level commit (ad-hoc)
def orchestrator_commit(commit_message: str):
    """
    Orchestrator creates ad-hoc commit.
    """
    # Validate
    if not safe_validate_before_commit(commit_message):
        return {
            "status": "failed",
            "reason": "commit_message_validation_failed"
        }

    # Only if validation passes: proceed with git operations
    # Execute: git add . && git commit -m "$commit_message"
    return {"status": "success"}


# Example 2: Agent-level commit (realization phase)
def agent_commit_in_realization(realization_package: dict):
    """
    Agent creates commit as part of workflow realization.
    """
    commit_message = realization_package["git_operations"]["commit_message"]

    # Validate (same validation as orchestrator)
    if not safe_validate_before_commit(commit_message):
        return {
            "status": "failed",
            "reason": "commit_message_validation_failed",
            "message": "Orchestrator provided invalid commit message"
        }

    # Proceed with git operations
    # Execute: git add . && git commit -m "$commit_message" && git push
    return {"status": "success"}


# Example 3: Generating commit message
def generate_commit_message(changes: dict) -> str:
    """
    Generate commit message following Conventional Commits.
    """
    commit_type = changes.get("type", "chore")  # feat, fix, refactor, etc.
    scope = changes.get("scope", "")  # helmrelease, terraform, etc.
    description = changes.get("description", "")  # imperative mood, <72 chars

    if scope:
        return f"{commit_type}({scope}): {description}"
    else:
        return f"{commit_type}: {description}"


# Example 4: Handling validation failure
def commit_with_retry(commit_message: str, max_retries: int = 2):
    """
    Attempt commit with validation, regenerate if fails.
    """
    for attempt in range(max_retries):
        if safe_validate_before_commit(commit_message):
            # Valid, proceed
            return {"status": "success", "message": commit_message}

        # Invalid, regenerate
        commit_message = regenerate_commit_message(commit_message, attempt)

    # All attempts failed
    return {
        "status": "failed",
        "reason": "Cannot generate valid commit message after retries"
    }


def regenerate_commit_message(original: str, attempt: int) -> str:
    """
    Regenerate commit message after validation failure.
    """
    # Implement regeneration logic based on validation errors
    # Example: shorten if too long, fix imperative mood, remove forbidden footers
    return original  # Placeholder
