#!/usr/bin/env bash

set -e

# Parse command line arguments
JSON_MODE=false
SPECKIT_ROOT_ARG=""
FEATURE_DESCRIPTION=""

usage() {
    echo "Usage: $0 [--json] <speckit-root> <feature-description>"
    echo ""
    echo "Arguments:"
    echo "  speckit-root         Path to spec-kit root directory (e.g., spec-kit-tcm-plan)"
    echo "  feature-description  Natural language description of the feature"
    echo ""
    echo "Options:"
    echo "  --json              Output results in JSON format"
    echo "  --help, -h          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 spec-kit-tcm-plan Add dark mode toggle"
    echo "  $0 --json spec-kit-tcm-plan Implement user authentication"
    exit 0
}

# Parse arguments
POSITIONAL_ARGS=()
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
            POSITIONAL_ARGS+=("$arg")
            ;;
    esac
done

# Extract speckit-root (first positional) and feature-description (remaining)
if [ "${#POSITIONAL_ARGS[@]}" -lt 2 ]; then
    echo "ERROR: Both <speckit-root> and <feature-description> are required" >&2
    echo "" >&2
    usage
fi

SPECKIT_ROOT_ARG="${POSITIONAL_ARGS[0]}"
# Join remaining args as feature description
FEATURE_DESCRIPTION="${POSITIONAL_ARGS[@]:1}"

if [ -z "$FEATURE_DESCRIPTION" ]; then
    echo "ERROR: Feature description cannot be empty" >&2
    exit 1
fi

# Get script directory and load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

REPO_ROOT=$(get_repo_root)
cd "$REPO_ROOT"

# Resolve speckit_root to absolute path
if [[ "$SPECKIT_ROOT_ARG" = /* ]]; then
    SPECKIT_ROOT="$SPECKIT_ROOT_ARG"
else
    SPECKIT_ROOT="$REPO_ROOT/$SPECKIT_ROOT_ARG"
fi

# Validate speckit root exists
validate_speckit_root "$SPECKIT_ROOT" || exit 1

# Derive specs directory
SPECS_DIR="$SPECKIT_ROOT/specs"
ensure_specs_dir "$SPECS_DIR"

# Find highest numbered feature
HIGHEST=0
if [ -d "$SPECS_DIR" ]; then
    for dir in "$SPECS_DIR"/*; do
        [ -d "$dir" ] || continue
        dirname=$(basename "$dir")
        number=$(echo "$dirname" | grep -o '^[0-9]\+' || echo "0")
        number=$((10#$number))
        if [ "$number" -gt "$HIGHEST" ]; then
            HIGHEST=$number
        fi
    done
fi

# Generate next feature number
NEXT=$((HIGHEST + 1))
FEATURE_NUM=$(printf "%03d" "$NEXT")

# Generate feature name from description
FEATURE_NAME=$(echo "$FEATURE_DESCRIPTION" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//' | sed 's/-$//')
WORDS=$(echo "$FEATURE_NAME" | tr '-' '\n' | grep -v '^$' | head -3 | tr '\n' '-' | sed 's/-$//')
FEATURE_NAME="${FEATURE_NUM}-${WORDS}"

# Create feature directory
FEATURE_DIR="$SPECS_DIR/$FEATURE_NAME"
mkdir -p "$FEATURE_DIR"

# Copy spec template
TEMPLATE="$REPO_ROOT/.claude/speckit/templates/spec-template.md"
SPEC_FILE="$FEATURE_DIR/spec.md"
if [ -f "$TEMPLATE" ]; then
    cp "$TEMPLATE" "$SPEC_FILE"
else
    touch "$SPEC_FILE"
    echo "Warning: Spec template not found at $TEMPLATE" >&2
fi

# Output results
if $JSON_MODE; then
    printf '{"FEATURE_NAME":"%s","SPEC_FILE":"%s","FEATURE_NUM":"%s","FEATURE_DIR":"%s","SPECKIT_ROOT":"%s"}\n' \
        "$FEATURE_NAME" "$SPEC_FILE" "$FEATURE_NUM" "$FEATURE_DIR" "$SPECKIT_ROOT"
else
    echo "FEATURE_NAME: $FEATURE_NAME"
    echo "SPEC_FILE: $SPEC_FILE"
    echo "FEATURE_NUM: $FEATURE_NUM"
    echo "FEATURE_DIR: $FEATURE_DIR"
    echo "SPECKIT_ROOT: $SPECKIT_ROOT"
fi
