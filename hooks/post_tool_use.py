#!/usr/bin/env python3
"""
Post-tool use hook for Claude Code Agent System
Implements audit logging, metrics collection, and session tracking
"""

import sys
import json
import hashlib
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_claude_dir() -> Path:
    """Find the .claude directory by searching upward from current location"""
    current = Path.cwd()

    # If we're already in a .claude directory, return it
    if current.name == ".claude":
        return current

    # Look for .claude in current directory
    claude_dir = current / ".claude"
    if claude_dir.exists():
        return claude_dir

    # Search upward through parent directories
    for parent in current.parents:
        claude_dir = parent / ".claude"
        if claude_dir.exists():
            return claude_dir

    # Fallback - use current directory's .claude (but don't create it yet)
    logger.warning(f"No .claude directory found, using {current}/.claude")
    return current / ".claude"

class AuditLogger:
    """Audit logger for tracking all tool executions"""

    def __init__(self, log_dir: Optional[str] = None):
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            # Find the correct .claude directory
            claude_dir = find_claude_dir()
            self.log_dir = claude_dir / "logs"
        self.log_dir.mkdir(exist_ok=True, parents=True)
        self.session_id = os.environ.get("CLAUDE_SESSION_ID", "default")

    def hash_output(self, output: str, max_length: int = 1000) -> str:
        """Create hash of output for audit trail"""
        # Truncate output for hashing
        truncated = output[:max_length] if len(output) > max_length else output
        return hashlib.sha256(truncated.encode()).hexdigest()[:16]

    def log_execution(self, tool_name: str, parameters: Dict,
                     result: Any, duration: float, exit_code: int = 0):
        """Log tool execution details"""

        timestamp = datetime.now().isoformat()

        # Extract command for bash tools
        command = ""
        if tool_name.lower() == "bash":
            command = parameters.get("command", "")

        # Process result
        output_preview = ""
        output_hash = ""
        if result:
            result_str = str(result)
            output_preview = result_str[:200] + "..." if len(result_str) > 200 else result_str
            output_hash = self.hash_output(result_str)

        # Create audit record
        audit_record = {
            "timestamp": timestamp,
            "session_id": self.session_id,
            "tool_name": tool_name,
            "command": command,
            "parameters": parameters,
            "duration_ms": round(duration * 1000, 2),
            "exit_code": exit_code,
            "output_hash": output_hash,
            "output_preview": output_preview
        }

        # Write to session log
        session_log_file = self.log_dir / f"session-{self.session_id}.jsonl"
        with open(session_log_file, "a") as f:
            f.write(json.dumps(audit_record) + "\n")

        # Write to daily audit log
        daily_log_file = self.log_dir / f"audit-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with open(daily_log_file, "a") as f:
            f.write(json.dumps(audit_record) + "\n")

        logger.info(f"Logged execution: {tool_name} - {command[:50]} - {duration:.2f}s")

class MetricsCollector:
    """Collect and aggregate execution metrics"""

    def __init__(self, metrics_dir: Optional[str] = None):
        if metrics_dir:
            self.metrics_dir = Path(metrics_dir)
        else:
            # Find the correct .claude directory
            claude_dir = find_claude_dir()
            self.metrics_dir = claude_dir / "metrics"
        self.metrics_dir.mkdir(exist_ok=True, parents=True)

    def record_execution(self, tool_name: str, command: str, duration: float,
                        success: bool, tier: str = "unknown"):
        """Record execution metrics"""

        timestamp = datetime.now().isoformat()

        metrics_record = {
            "timestamp": timestamp,
            "tool_name": tool_name,
            "command_type": self._classify_command(command),
            "duration_ms": round(duration * 1000, 2),
            "success": success,
            "tier": tier
        }

        # Write to metrics file
        metrics_file = self.metrics_dir / f"metrics-{datetime.now().strftime('%Y-%m')}.jsonl"
        with open(metrics_file, "a") as f:
            f.write(json.dumps(metrics_record) + "\n")

    def _classify_command(self, command: str) -> str:
        """Classify command type for metrics"""

        if "terraform" in command.lower():
            return "terraform"
        elif "kubectl" in command.lower():
            return "kubernetes"
        elif "helm" in command.lower():
            return "helm"
        elif "gcloud" in command.lower():
            return "gcp"
        elif "aws" in command.lower():
            return "aws"
        elif "flux" in command.lower():
            return "flux"
        elif "docker" in command.lower():
            return "docker"
        else:
            return "general"

    def generate_summary(self, days: int = 7) -> Dict[str, Any]:
        """Generate metrics summary for the last N days"""

        # This would typically read from metrics files and aggregate
        # For now, return a placeholder summary
        return {
            "period_days": days,
            "total_executions": 0,
            "success_rate": 0.0,
            "avg_duration_ms": 0.0,
            "top_commands": [],
            "tier_distribution": {}
        }

class NotificationHandler:
    """Handle notifications for threshold breaches or important events"""

    def __init__(self):
        self.thresholds = {
            "long_execution_seconds": 60,
            "high_failure_rate": 0.3,
            "blocked_command_count": 5
        }

    def check_thresholds(self, duration: float, success: bool, tool_name: str):
        """Check if execution crosses any notification thresholds"""

        notifications = []

        # Long execution time
        if duration > self.thresholds["long_execution_seconds"]:
            notifications.append({
                "type": "long_execution",
                "message": f"Long execution detected: {tool_name} took {duration:.1f}s",
                "severity": "warning"
            })

        # Command failure
        if not success:
            notifications.append({
                "type": "command_failure",
                "message": f"Command failed: {tool_name}",
                "severity": "error"
            })

        return notifications

class CriticalEventDetector:
    """Detect critical events that warrant context updates"""

    # Track file modifications within session
    file_modification_count = 0
    file_modification_threshold = 3

    def __init__(self):
        self.speckit_commands = [
            "/speckit.specify", "/speckit.plan", "/speckit.tasks",
            "/speckit.implement", "/speckit.constitution"
        ]

    def is_git_commit(self, tool_name: str, parameters: Dict, result: Any, success: bool) -> Optional[Dict]:
        """Detect successful git commit"""
        if not success:
            return None

        if tool_name.lower() == "bash":
            command = parameters.get("command", "")
            if "git commit" in command and result:
                # Extract commit metadata
                result_str = str(result)

                # Try to extract commit hash (format: [branch hash] message)
                commit_hash = ""
                commit_message = ""

                # Look for pattern like "[main 1a2b3c4]"
                import re
                match = re.search(r'\[[\w\-/]+ ([a-f0-9]{7,})\]', result_str)
                if match:
                    commit_hash = match.group(1)

                # Extract message (usually after the hash pattern)
                if commit_hash:
                    msg_match = re.search(r'\[[\w\-/]+ [a-f0-9]{7,}\]\s*(.+)', result_str, re.MULTILINE)
                    if msg_match:
                        commit_message = msg_match.group(1).strip().split('\n')[0]

                return {
                    "event_type": "git_commit",
                    "commit_hash": commit_hash,
                    "commit_message": commit_message,
                    "command": command
                }
        return None

    def is_git_push(self, tool_name: str, parameters: Dict, result: Any, success: bool) -> Optional[Dict]:
        """Detect successful git push"""
        if not success:
            return None

        if tool_name.lower() == "bash":
            command = parameters.get("command", "")
            if "git push" in command and result:
                result_str = str(result)

                # Extract branch info
                branch = ""
                import re
                match = re.search(r'To .+\n\s+[a-f0-9]+\.\.[a-f0-9]+\s+([\w\-/]+)\s+->', result_str)
                if match:
                    branch = match.group(1)

                return {
                    "event_type": "git_push",
                    "branch": branch,
                    "command": command
                }
        return None

    def should_update_for_file_mods(self, tool_name: str) -> Optional[Dict]:
        """Check if file modification count crosses threshold"""
        if tool_name.lower() in ["edit", "write", "notebookedit"]:
            CriticalEventDetector.file_modification_count += 1

            if CriticalEventDetector.file_modification_count >= self.file_modification_threshold:
                # Reset counter
                count = CriticalEventDetector.file_modification_count
                CriticalEventDetector.file_modification_count = 0

                return {
                    "event_type": "file_modifications",
                    "modification_count": count
                }
        return None

    def is_speckit_milestone(self, tool_name: str, parameters: Dict) -> Optional[Dict]:
        """Detect spec-kit milestone commands"""
        if tool_name.lower() == "slashcommand":
            command = parameters.get("command", "")
            for speckit_cmd in self.speckit_commands:
                if speckit_cmd in command:
                    return {
                        "event_type": "speckit_milestone",
                        "command": speckit_cmd
                    }
        return None

class ActiveContextUpdater:
    """Update active session context for critical events"""

    def __init__(self, context_path: Optional[str] = None):
        if context_path:
            self.context_path = Path(context_path)
        else:
            # Find the correct .claude directory
            claude_dir = find_claude_dir()
            self.context_path = claude_dir / "session" / "active" / "context.json"
        self.context_path.parent.mkdir(exist_ok=True, parents=True)

    def update_context(self, event_data: Dict) -> None:
        """Update active context with event data"""
        try:
            # Load existing context
            context = {}
            if self.context_path.exists():
                with open(self.context_path, 'r') as f:
                    context = json.load(f)

            # Initialize events list if not exists
            if "critical_events" not in context:
                context["critical_events"] = []

            # Add timestamp to event
            event_data["timestamp"] = datetime.now().isoformat()

            # Append new event
            context["critical_events"].append(event_data)

            # Keep only last 20 events (prevent unbounded growth)
            context["critical_events"] = context["critical_events"][-20:]

            # Update last_modified
            context["last_modified"] = datetime.now().isoformat()

            # Write back to file
            with open(self.context_path, 'w') as f:
                json.dump(context, f, indent=2)

            logger.info(f"Updated active context with event: {event_data['event_type']}")

        except Exception as e:
            logger.error(f"Error updating active context: {e}")

def post_tool_use_hook(tool_name: str, parameters: Dict, result: Any,
                      duration: float, success: bool = True) -> None:
    """
    Post-tool use hook implementation

    Args:
        tool_name: Name of the tool that was invoked
        parameters: Tool parameters
        result: Tool execution result
        duration: Execution duration in seconds
        success: Whether execution was successful
    """

    try:
        # Initialize components
        audit_logger = AuditLogger()
        metrics_collector = MetricsCollector()
        notification_handler = NotificationHandler()

        # Determine exit code
        exit_code = 0 if success else 1

        # Log execution
        audit_logger.log_execution(tool_name, parameters, result, duration, exit_code)

        # Extract command for metrics
        command = parameters.get("command", "") if tool_name.lower() == "bash" else tool_name

        # Determine tier (this would ideally come from pre_tool_use)
        tier = "unknown"  # Could be enhanced to track tier from pre-hook

        # Record metrics
        metrics_collector.record_execution(tool_name, command, duration, success, tier)

        # Check for notifications
        notifications = notification_handler.check_thresholds(duration, success, tool_name)

        for notification in notifications:
            logger.warning(f"NOTIFICATION: {notification['message']}")

        # ═══════════════════════════════════════════════════════════════
        # CRITICAL EVENT DETECTION & CONTEXT UPDATES
        # ═══════════════════════════════════════════════════════════════

        event_detector = CriticalEventDetector()
        context_updater = ActiveContextUpdater()

        # Detect git commit
        git_commit_event = event_detector.is_git_commit(tool_name, parameters, result, success)
        if git_commit_event:
            context_updater.update_context(git_commit_event)

        # Detect git push
        git_push_event = event_detector.is_git_push(tool_name, parameters, result, success)
        if git_push_event:
            context_updater.update_context(git_push_event)

        # Detect file modifications batch
        file_mod_event = event_detector.should_update_for_file_mods(tool_name)
        if file_mod_event:
            context_updater.update_context(file_mod_event)

        # Detect spec-kit milestones
        speckit_event = event_detector.is_speckit_milestone(tool_name, parameters)
        if speckit_event:
            context_updater.update_context(speckit_event)

    except Exception as e:
        logger.error(f"Error in post_tool_use_hook: {e}")

def main():
    """CLI interface for testing and metrics"""

    if len(sys.argv) < 2:
        print("Usage: python post_tool_use.py --metrics")
        print("       python post_tool_use.py --test")
        sys.exit(1)

    if sys.argv[1] == "--metrics":
        # Show current metrics
        metrics_collector = MetricsCollector()
        summary = metrics_collector.generate_summary()

        print("📊 Execution Metrics Summary")
        print(f"Period: {summary['period_days']} days")
        print(f"Total executions: {summary['total_executions']}")
        print(f"Success rate: {summary['success_rate']:.1%}")
        print(f"Average duration: {summary['avg_duration_ms']:.1f}ms")

    elif sys.argv[1] == "--test":
        # Test the post hook
        print("🧪 Testing Post-Tool Use Hook...")

        test_parameters = {"command": "kubectl get pods"}
        test_result = "pod/test-pod   1/1   Running   0   1m"

        start_time = time.time()
        post_tool_use_hook("bash", test_parameters, test_result, 0.5, True)

        print("✅ Post-hook test completed")
        print("Check .claude/logs/ for audit logs")
        print("Check .claude/metrics/ for metrics")

    else:
        print(f"Unknown command: {sys.argv[1]}")
        sys.exit(1)

if __name__ == "__main__":
    main()