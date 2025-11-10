#!/usr/bin/env python3
"""
Demo script for the Clarification Engine

Shows how the clarification system works with different types of prompts.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from clarify_engine import request_clarification


def demo_prompt(prompt: str, description: str = ""):
    """Test a single prompt and display results."""
    print("=" * 70)
    if description:
        print(f"📝 {description}")
    print(f"Prompt: \"{prompt}\"")
    print("=" * 70)

    result = request_clarification(prompt)

    if not result["needs_clarification"]:
        print("✅ No clarification needed - prompt is specific enough\n")
        return

    print(f"⚠️  Clarification needed (score: {result['clarification_context']['ambiguity_analysis']['ambiguity_score']}/100)\n")

    # Show summary
    print(result["summary"])
    print()

    # Show questions
    for i, question in enumerate(result["question_config"]["questions"]):
        print(f"\n{'─' * 70}")
        print(f"{question['header']}")
        print(f"{'─' * 70}")
        print(f"❓ {question['question']}\n")

        for j, option in enumerate(question["options"], 1):
            print(f"  {j}. {option['label']}")
            print(f"     → {option['description']}\n")

    print()


def main():
    """Run demo with various prompt types."""

    print("\n" + "🎯" * 35)
    print("   CLARIFICATION ENGINE - DEMO")
    print("🎯" * 35 + "\n")

    # Test 1: Ambiguous service
    demo_prompt(
        "Check the API",
        "Test 1: Ambiguous service reference"
    )

    # Test 2: Specific service (no clarification)
    demo_prompt(
        "Check tcm-api service status",
        "Test 2: Specific service (should NOT need clarification)"
    )

    # Test 3: Environment mismatch
    demo_prompt(
        "Deploy to production",
        "Test 3: Environment mismatch warning"
    )

    # Test 4: Namespace ambiguity
    demo_prompt(
        "Deploy to the cluster",
        "Test 4: Namespace ambiguity"
    )

    # Test 5: Multiple ambiguities
    demo_prompt(
        "Deploy the API to the cluster",
        "Test 5: Multiple ambiguities (service + namespace)"
    )

    # Test 6: Spanish prompt
    demo_prompt(
        "Chequea el servicio",
        "Test 6: Spanish keywords"
    )

    # Test 7: Redis resource
    demo_prompt(
        "Check the Redis instance",
        "Test 7: Resource ambiguity (Redis)"
    )

    print("\n" + "✅" * 35)
    print("   DEMO COMPLETE")
    print("✅" * 35 + "\n")


if __name__ == "__main__":
    main()
