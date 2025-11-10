# Phase 0: Clarification Workflow Example
# Use when user request contains ambiguous terms or missing context

import sys
sys.path.insert(0, '/home/jaguilar/aaxis/rnd/repositories/.claude/tools')
from clarify_engine import request_clarification, process_clarification

# Example 1: Detect ambiguity
def detect_ambiguity(user_prompt: str, command_context: dict):
    """
    Detect if user request needs clarification.
    """
    clarification_data = request_clarification(
        user_prompt=user_prompt,
        command_context=command_context  # {"command": "general_prompt"} or speckit command
    )

    # Check if clarification needed
    if not clarification_data["needs_clarification"]:
        # No ambiguity, proceed with original prompt
        return {"skip_clarification": True, "prompt": user_prompt}

    # Ambiguity detected, need to ask user
    return {
        "skip_clarification": False,
        "clarification_data": clarification_data
    }


# Example 2: Present clarification questions
def present_clarification(clarification_data: dict):
    """
    Present ambiguity summary and ask questions.
    """
    # Show summary to user
    summary = clarification_data["summary"]
    print(f"Ambiguity detected: {summary}")

    # Ask questions using AskUserQuestion tool
    question_config = clarification_data["question_config"]
    # response = AskUserQuestion(**question_config)

    return question_config


# Example 3: Process user responses
def process_user_responses(clarification_data: dict, user_responses: dict, original_prompt: str):
    """
    Generate enriched prompt from user responses.
    """
    result = process_clarification(
        engine_instance=clarification_data["engine_instance"],
        original_prompt=original_prompt,
        user_responses=user_responses,
        clarification_context=clarification_data["clarification_context"]
    )

    enriched_prompt = result["enriched_prompt"]

    # Example: "revisa el servicio" + {service: "tcm-api", namespace: "tcm-non-prod"}
    # Becomes: "revisa el servicio tcm-api en el namespace tcm-non-prod"

    return enriched_prompt


# Example 4: Full clarification workflow
def clarification_workflow(user_prompt: str):
    """
    Complete Phase 0 workflow.
    """
    # Step 1: Detect ambiguity
    detection = detect_ambiguity(user_prompt, {"command": "general_prompt"})

    if detection["skip_clarification"]:
        # No clarification needed
        return detection["prompt"]

    # Step 2: Get clarification data
    clarification_data = detection["clarification_data"]

    # Step 3: Ask user (via AskUserQuestion tool)
    question_config = present_clarification(clarification_data)
    # user_responses = AskUserQuestion(**question_config)  # Simulated

    # Step 4: Process responses and enrich prompt
    user_responses = {"service": "tcm-api", "namespace": "tcm-non-prod"}  # Example
    enriched_prompt = process_user_responses(
        clarification_data,
        user_responses,
        user_prompt
    )

    # Step 5: Use enriched prompt for Phase 1 (Routing)
    return enriched_prompt
