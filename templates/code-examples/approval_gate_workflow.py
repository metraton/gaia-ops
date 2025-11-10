# Phase 4: Approval Gate Workflow Example
# MANDATORY for T3 operations (terraform apply, kubectl apply, git push to main)

import sys
sys.path.insert(0, '/home/jaguilar/aaxis/rnd/repositories/.claude/tools')
from approval_gate import request_approval, process_approval_response

# Example 1: Generate approval summary
def generate_approval_summary(realization_package: dict, agent_name: str, phase: str):
    """
    Generate structured approval summary from realization package.
    """
    approval_data = request_approval(
        realization_package=realization_package,
        agent_name=agent_name,  # "gitops-operator", "terraform-architect", etc.
        phase=phase  # "Phase 3.3", "Deploy production", etc.
    )

    # approval_data contains:
    # - summary: Human-readable breakdown
    # - question_config: Pre-formatted for AskUserQuestion
    # - gate_instance: Reference for validation step

    return approval_data


# Example 2: Present summary and ask user
def ask_user_approval(approval_data: dict):
    """
    Present approval summary and ask for user decision.
    """
    # Show summary
    print(approval_data["summary"])

    # Ask question (3 options: Approve, Reject, Other)
    question_config = approval_data["question_config"]
    # response = AskUserQuestion(**question_config)  # Simulated

    # Example response
    response = {"answers": {"question_1": "✅ Aprobar y ejecutar"}}

    return response


# Example 3: Validate user response
def validate_approval(approval_data: dict, user_response: dict, realization_package: dict, agent_name: str, phase: str):
    """
    Process user response and determine if approved.
    """
    validation = process_approval_response(
        gate_instance=approval_data["gate_instance"],
        user_response=user_response["answers"]["question_1"],
        realization_package=realization_package,
        agent_name=agent_name,
        phase=phase
    )

    # validation contains:
    # - approved: Boolean (True if user approved)
    # - action: String ("proceed", "halt_workflow", "clarify_with_user")
    # - reason: String (explanation)

    return validation


# Example 4: Enforcement rules
def enforce_approval_gate(validation: dict):
    """
    Enforce approval gate rules before proceeding to Phase 5.
    """
    if validation["approved"]:
        # Approved, proceed to Phase 5 (Realization)
        return {"allow_phase_5": True}

    if validation["action"] == "halt_workflow":
        # Rejected, STOP workflow
        return {
            "allow_phase_5": False,
            "message": "User rejected realization. Workflow halted."
        }

    if validation["action"] == "clarify_with_user":
        # Need more info, re-run approval gate
        return {
            "allow_phase_5": False,
            "message": "Clarification needed. Re-run approval gate."
        }

    # Default: deny
    return {"allow_phase_5": False, "message": "Unknown validation state"}


# Example 5: Full approval gate workflow
def approval_gate_workflow(realization_package: dict, agent_name: str, phase: str):
    """
    Complete Phase 4 workflow (MANDATORY for T3 operations).
    """
    # Step 1: Generate approval summary
    approval_data = generate_approval_summary(realization_package, agent_name, phase)

    # Step 2: Ask user for approval
    user_response = ask_user_approval(approval_data)

    # Step 3: Validate response
    validation = validate_approval(
        approval_data,
        user_response,
        realization_package,
        agent_name,
        phase
    )

    # Step 4: Enforce rules
    enforcement = enforce_approval_gate(validation)

    if not enforcement["allow_phase_5"]:
        # Cannot proceed to Phase 5
        return {
            "status": "blocked",
            "message": enforcement["message"]
        }

    # Approved, can proceed to Phase 5
    return {
        "status": "approved",
        "message": "User approved. Proceeding to Phase 5 (Realization)."
    }


# Example 6: CRITICAL - Cannot skip approval gate
def attempt_to_skip_approval_gate():
    """
    This is an ANTI-PATTERN. NEVER do this.
    """
    # ❌ WRONG: Skip approval gate for T3 operation
    # Task(subagent_type="gitops-operator", prompt="Deploy to prod")  # Direct realization
    # This violates Rule 5.1 [P0]: Approval Gate Enforcement

    # ✅ CORRECT: Always go through approval gate
    # Phase 3: Planning -> Phase 4: Approval Gate -> Phase 5: Realization
    pass
