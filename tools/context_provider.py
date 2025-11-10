import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any

# This script is expected to be run from the root of the repository.
# The project context file is located at `.claude/project-context.json`.
# We construct the path relative to the script's assumed execution location.
DEFAULT_CONTEXT_PATH = Path(".claude/project-context.json")

# Defines the mandatory keys that form the "Context Contract" for each agent.
AGENT_CONTRACTS: Dict[str, List[str]] = {
    "terraform-architect": [
        "project_details",
        "terraform_infrastructure",
        "operational_guidelines",
    ],
    "gitops-operator": [
        "project_details",
        "gitops_configuration",
        "infrastructure_topology",
        "cluster_details",
        "operational_guidelines",
    ],
    "gcp-troubleshooter": [
        "project_details",
        "infrastructure_topology",
        "terraform_infrastructure",
        "gitops_configuration",
        "application_services",
        "monitoring_observability",
    ],
    "aws-troubleshooter": [
        "project_details",
        "infrastructure_topology",
        "terraform_infrastructure",
        "gitops_configuration",
        "application_services",
        "monitoring_observability",
    ],
    # devops-developer has a more generic contract, often needing the full view.
    "devops-developer": [
        "project_details",
        "application_architecture",
        "application_services",
        "development_standards",
        "operational_guidelines"
    ]
}

def load_project_context(context_path: Path) -> Dict[str, Any]:
    """Loads the project context from the specified JSON file."""
    if not context_path.is_file():
        print(f"Error: Context file not found at {context_path}", file=sys.stderr)
        sys.exit(1)
    with open(context_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_contract_context(project_context: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
    """Extracts the contract-defined context for a given agent."""
    contract_keys = AGENT_CONTRACTS.get(agent_name)
    if not contract_keys:
        print(
            f"Warning: No contract found for agent '{agent_name}'. Returning empty contract.",
            file=sys.stderr,
        )
        return {}

    sections = project_context.get("sections", {})
    if not sections:
        raise KeyError("project-context.json must contain a 'sections' object.")
    return {key: sections[key] for key in contract_keys if key in sections}


def get_semantic_enrichment(
    project_context: Dict[str, Any], contract_keys: List[str], user_task: str
) -> Dict[str, Any]:
    """
    Performs semantic analysis to find additional relevant context.

    NOTE: This is a placeholder implementation. A real implementation would use
    vector embeddings (e.g., SentenceTransformers, OpenAI embeddings) to find
    sections of the project_context semantically similar to the user_task.

    For now, it performs a simple keyword match, excluding keys already in the contract.
    """
    sections = project_context.get("sections", {})
    if not sections:
        raise KeyError("project-context.json must contain a 'sections' object.")
    enrichment: Dict[str, Any] = {}
    contract_key_set = set(contract_keys)
    potential_keys = set(sections.keys()) - contract_key_set
    task_words = {word.strip(".,:;!?") for word in user_task.lower().split()}

    for key in potential_keys:
        normalized_key = key.lower()
        if normalized_key in task_words:
            enrichment[key] = sections[key]

    # Light metadata hints when the user asks about freshness/versioning.
    metadata = project_context.get("metadata")
    if metadata and any(word in {"metadata", "version", "updated"} for word in task_words):
        enrichment.setdefault("metadata", metadata)

    # Heuristic: include matching services based on task wording.
    def normalize_services(raw: Any) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        if isinstance(raw, list):
            for svc in raw:
                if isinstance(svc, dict) and svc.get("name"):
                    normalized.append(svc)
        elif isinstance(raw, dict):
            for name, payload in raw.items():
                entry = {"name": name}
                if isinstance(payload, dict):
                    entry.update(payload)
                normalized.append(entry)
        return normalized

    candidate_services: List[Dict[str, Any]] = []
    candidate_services.extend(normalize_services(sections.get("application_services")))

    service_catalog = sections.get("service_catalog")
    if isinstance(service_catalog, dict):
        candidate_services.extend(
            normalize_services(service_catalog.get("applications"))
        )

    app_arch = sections.get("application_architecture")
    if isinstance(app_arch, dict):
        candidate_services.extend(normalize_services(app_arch.get("services")))

    if candidate_services and "application_services" not in contract_key_set:
        matched = [
            svc for svc in candidate_services
            if svc.get("name", "").lower() in user_task.lower()
        ]
        if matched:
            enrichment["application_services"] = matched

    return enrichment

def main():
    """Main function to generate and print the context payload."""
    parser = argparse.ArgumentParser(
        description="""
        Generates a structured context payload for a Claude agent based on its contract
        and a semantic analysis of the user's task.
        """
    )
    parser.add_argument("agent_name", choices=AGENT_CONTRACTS.keys(), help="The name of the agent being invoked.")
    parser.add_argument("user_task", help="The user's task or query for the agent.")
    parser.add_argument(
        "--context-file",
        type=Path,
        default=DEFAULT_CONTEXT_PATH,
        help=f"Path to the project-context.json file. Defaults to '{DEFAULT_CONTEXT_PATH}'"
    )

    args = parser.parse_args()

    project_context = load_project_context(args.context_file)
    
    contract_context = get_contract_context(project_context, args.agent_name)
    
    enrichment_context = get_semantic_enrichment(
        project_context,
        list(contract_context.keys()),
        args.user_task
    )

    final_payload = {
        "contract": contract_context,
        "enrichment": enrichment_context
    }

    print(json.dumps(final_payload, indent=2))

if __name__ == "__main__":
    main()
