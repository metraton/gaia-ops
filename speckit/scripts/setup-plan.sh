#!/usr/bin/env bash

set -e

# Parse command line arguments
JSON_MODE=false
SPECKIT_ROOT_ARG=""
FEATURE_NAME_ARG=""

usage() {
    echo "Usage: $0 [--json] <speckit-root> <feature-name>"
    echo ""
    echo "Arguments:"
    echo "  speckit-root      Path to spec-kit root directory (e.g., spec-kit-tcm-plan)"
    echo "  feature-name      Feature name (e.g., 004-project-guidance-deployment)"
    echo ""
    echo "Options:"
    echo "  --json            Output results in JSON format"
    echo "  --help, -h        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 spec-kit-tcm-plan 004-project-guidance-deployment"
    echo "  $0 --json spec-kit-tcm-plan 004-project-guidance-deployment"
    echo "  $0 /absolute/path/to/spec-kit-tcm-plan 004-project-guidance-deployment"
    exit 0
}

for arg in "$@"; do
    case "$arg" in
        --json)
            JSON_MODE=true
            ;;
        --help|-h)
            usage
            ;;
        -*)
            echo "Unknown option: $arg" >&2
            usage
            ;;
        *)
            # First positional arg = speckit-root, second = feature-name
            if [[ -z "$SPECKIT_ROOT_ARG" ]]; then
                SPECKIT_ROOT_ARG="$arg"
            elif [[ -z "$FEATURE_NAME_ARG" ]]; then
                FEATURE_NAME_ARG="$arg"
            fi
            ;;
    esac
done

# Validate required arguments
if [[ -z "$SPECKIT_ROOT_ARG" ]] || [[ -z "$FEATURE_NAME_ARG" ]]; then
    echo "ERROR: Both <speckit-root> and <feature-name> are required" >&2
    echo "" >&2
    usage
fi

# Get script directory and load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Get all paths from explicit arguments (no config.json needed!)
eval $(get_feature_paths "$SPECKIT_ROOT_ARG" "$FEATURE_NAME_ARG") || exit 1

# Validate speckit root exists
validate_speckit_root "$SPECKIT_ROOT" || exit 1

# Ensure specs directory exists
ensure_specs_dir "$SPECS_DIR"

# Ensure feature directory exists
mkdir -p "$FEATURE_DIR"

# Copy plan template if it exists
TEMPLATE="$TEMPLATES_DIR/plan-template.md"
if [[ -f "$TEMPLATE" ]]; then
    cp "$TEMPLATE" "$IMPL_PLAN"
    echo "Copied plan template to $IMPL_PLAN"
else
    echo "Warning: Plan template not found at $TEMPLATE"
    # Create a basic plan file if template doesn't exist
    touch "$IMPL_PLAN"
fi

# Output results
if $JSON_MODE; then
    printf '{"FEATURE_SPEC":"%s","IMPL_PLAN":"%s","FEATURE_DIR":"%s","FEATURE_NAME":"%s","SPECKIT_ROOT":"%s"}\n' \
        "$FEATURE_SPEC" "$IMPL_PLAN" "$FEATURE_DIR" "$FEATURE_NAME" "$SPECKIT_ROOT"
else
    echo "FEATURE_SPEC: $FEATURE_SPEC"
    echo "IMPL_PLAN: $IMPL_PLAN"
    echo "FEATURE_DIR: $FEATURE_DIR"
    echo "FEATURE_NAME: $FEATURE_NAME"
    echo "SPECKIT_ROOT: $SPECKIT_ROOT"
fi
