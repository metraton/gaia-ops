#!/usr/bin/env python3
"""
Session start hook for Claude Code Agent System
Auto-primes environment and provides default context for new sessions
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class EnvironmentDetector:
    """Detects current environment and workspace context"""

    def __init__(self):
        self.cwd = Path.cwd()
        self.context = {}

    def detect_workspace(self) -> Dict[str, Any]:
        """Detect workspace type and project context"""

        context = {
            "working_directory": str(self.cwd),
            "workspace_type": "unknown",
            "projects": [],
            "tools_available": [],
            "environment": "development"
        }

        # Check for multi-project repository
        if (self.cwd / "training-compliance-management").exists():
            context["workspace_type"] = "multi-project"
            context["projects"].append({
                "name": "Training Compliance Management",
                "path": "training-compliance-management",
                "type": "application",
                "tech_stack": "Node.js/TypeScript, NestJS, Next.js"
            })

        if (self.cwd / "terraform").exists():
            context["projects"].append({
                "name": "Infrastructure",
                "path": "terraform",
                "type": "infrastructure",
                "tech_stack": "Terraform/Terragrunt"
            })

        if (self.cwd / "gitops").exists():
            context["projects"].append({
                "name": "GitOps",
                "path": "gitops",
                "type": "deployment",
                "tech_stack": "Kubernetes/Flux CD"
            })

        # Check for agent system
        if (self.cwd / ".claude").exists():
            context["agent_system"] = True
            context["projects"].append({
                "name": "Agent System",
                "path": ".claude",
                "type": "devops-automation",
                "tech_stack": "Claude Code Agents"
            })

        # Detect available tools
        tools = []
        if self._command_exists("terraform"):
            tools.append("terraform")
        if self._command_exists("kubectl"):
            tools.append("kubectl")
        if self._command_exists("helm"):
            tools.append("helm")
        if self._command_exists("gcloud"):
            tools.append("gcloud")
        if self._command_exists("flux"):
            tools.append("flux")
        if self._command_exists("docker"):
            tools.append("docker")
        if self._command_exists("npm"):
            tools.append("npm")

        context["tools_available"] = tools

        return context

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH"""
        return os.system(f"which {command} >/dev/null 2>&1") == 0

    def load_agent_config(self) -> Optional[Dict[str, Any]]:
        """Load agent system configuration"""
        settings_file = self.cwd / ".claude" / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return None

class SessionPrimer:
    """Generates session primer content"""

    def __init__(self, context: Dict[str, Any], config: Optional[Dict[str, Any]] = None):
        self.context = context
        self.config = config or {}

    def generate_banner(self) -> str:
        """Generate session start banner"""

        banner = [
            "🚀 Claude Code Agent System - Session Started",
            "=" * 50,
            "",
            f"📁 **Workspace**: {self.context['workspace_type']}",
            f"📍 **Directory**: {self.context['working_directory']}",
            f"🕐 **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]

        # Project overview
        if self.context.get("projects"):
            banner.extend([
                "📋 **Available Projects**:",
                ""
            ])

            for project in self.context["projects"]:
                icon = self._get_project_icon(project["type"])
                banner.append(f"  {icon} **{project['name']}** (`{project['path']}`)")
                banner.append(f"     └─ {project['tech_stack']}")

            banner.append("")

        # Tools available
        if self.context.get("tools_available"):
            banner.extend([
                "🛠️ **Tools Available**: " + ", ".join(self.context["tools_available"]),
                ""
            ])

        # Agent system status
        if self.context.get("agent_system"):
            banner.extend([
                "🤖 **Agent System**: Active",
                ""
            ])

            # Show available commands
            if self.config.get("commands"):
                banner.extend([
                    "⚡ **Available Commands**:",
                    ""
                ])
                for cmd_name, cmd_info in self.config["commands"].items():
                    banner.append(f"  `/{cmd_name}` - {cmd_info.get('description', 'No description')}")

                banner.append("")

        return "\n".join(banner)

    def _get_project_icon(self, project_type: str) -> str:
        """Get icon for project type"""
        icons = {
            "application": "📱",
            "infrastructure": "🏗️",
            "deployment": "⚓",
            "devops-automation": "🤖"
        }
        return icons.get(project_type, "📁")

    def generate_environment_summary(self) -> str:
        """Generate environment summary"""

        summary = [
            "## Environment Context",
            ""
        ]

        # GCP context if available
        env_config = self.config.get("environment", {})
        if env_config:
            summary.extend([
                "☁️ **Cloud Environment**:",
                f"  - Project: {env_config.get('project_id', 'Unknown')}",
                f"  - Region: {env_config.get('region', 'Unknown')}",
                f"  - Cluster: {env_config.get('cluster_name', 'Unknown')}",
                ""
            ])

        # Security context
        summary.extend([
            "🔒 **Security Context**:",
            f"  - Default Tier: {self.config.get('security', {}).get('default_tier', 'T0')}",
            "  - Read-only operations preferred",
            "  - Policy gates active",
            ""
        ])

        return "\n".join(summary)

    def generate_quick_start(self) -> str:
        """Generate quick start guide"""

        quick_start = [
            "## Quick Start",
            "",
            "### Common Workflows:",
            "",
            "1. **Diagnose Task**: `/diagnose T004` or `/diagnose 'Check cluster health'`",
            "2. **Enrich Tasks**: `/enrich --spec-kit-path=/path/to/spec`",
            "3. **View Bundles**: `ls contexts/bundles/`",
            "4. **Restore Context**: `./scripts/headless/reprime-from-bundle.sh latest`",
            "",
            "### Agent Specialists Available:",
            ""
        ]

        # Show agents if available
        agents = self.config.get("agents", {})
        for agent_name, agent_info in agents.items():
            triggers = agent_info.get("triggers", [])
            trigger_text = ", ".join(triggers[:3]) + ("..." if len(triggers) > 3 else "")
            quick_start.append(f"  - **{agent_name}**: {trigger_text}")

        quick_start.extend([
            "",
            "### Security Reminders:",
            "- All destructive operations are blocked (T3 tier)",
            "- Validation and dry-run operations are preferred",
            "- Session activities are logged for audit",
            ""
        ])

        return "\n".join(quick_start)

def session_start_hook() -> str:
    """
    Main session start hook

    Returns:
        Session primer content
    """

    try:
        # Detect environment
        detector = EnvironmentDetector()
        context = detector.detect_workspace()
        config = detector.load_agent_config()

        # Generate primer
        primer = SessionPrimer(context, config)

        # Combine sections
        content = [
            primer.generate_banner(),
            primer.generate_environment_summary(),
            primer.generate_quick_start(),
            "---",
            "",
            "🎯 **Ready for agent operations!**",
            "Use `/diagnose` to route tasks to specialized agents or explore the available projects.",
            ""
        ]

        return "\n".join(content)

    except Exception as e:
        return f"⚠️ Error generating session primer: {e}"

def main():
    """CLI interface for session start hook"""

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--check":
            # Check hook configuration
            print("🔍 Checking session start hook configuration...")

            detector = EnvironmentDetector()
            context = detector.detect_workspace()
            config = detector.load_agent_config()

            print(f"✅ Workspace detected: {context['workspace_type']}")
            print(f"✅ Projects found: {len(context.get('projects', []))}")
            print(f"✅ Tools available: {len(context.get('tools_available', []))}")

            if config:
                print(f"✅ Agent config loaded: {len(config.get('agents', {}))} agents")
            else:
                print("⚠️ Agent config not found")

            print("✅ Hook configuration check completed")

        elif command == "--init":
            # Initialize session
            print("🚀 Initializing Claude Agent session...")
            primer_content = session_start_hook()
            print(primer_content)

        else:
            print(f"Unknown command: {command}")
            print("Usage: python session_start.py [--check|--init]")

    else:
        # Default: output session primer
        primer_content = session_start_hook()
        print(primer_content)

if __name__ == "__main__":
    main()