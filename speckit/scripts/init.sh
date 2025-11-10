#!/bin/bash
# ============================================================================
# DEPRECATED: This script is no longer needed in Spec-Kit 2.0
# ============================================================================
#
# Spec-Kit 2.0 uses explicit arguments instead of config.json:
#
# OLD WORKFLOW (config.json required):
#   /speckit.init --root spec-kit-tcm-plan
#   /speckit.plan
#   /speckit.tasks
#
# NEW WORKFLOW (no initialization needed):
#   /speckit.plan spec-kit-tcm-plan 004-feature-name
#   /speckit.tasks spec-kit-tcm-plan 004-feature-name
#
# All commands now receive two explicit arguments:
#   1. <speckit-root>: Path to spec-kit directory
#   2. <feature-name>: Name of the feature
#
# This eliminates the need for config.json and makes all operations explicit.
#
# If you need to migrate from Spec-Kit 1.0, simply start using the new
# command format. Your existing specs/ directories will work unchanged.
#
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ⚠️  DEPRECATED: /speckit.init is no longer needed in Spec-Kit 2.0"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Spec-Kit 2.0 uses explicit arguments instead of config.json."
echo ""
echo "NEW USAGE:"
echo "  /speckit.plan <speckit-root> <feature-name>"
echo ""
echo "EXAMPLE:"
echo "  /speckit.plan spec-kit-tcm-plan 004-project-guidance-deployment"
echo ""
echo "No initialization is required. Just use the commands with explicit paths!"
echo ""
exit 1
