"""
Helper utilities for permissions system tests.

Provides functions for:
- Loading project and shared settings
- Merging settings with proper precedence
- Finding Claude configuration directories
- Detecting environment mode (production vs development)
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import re


def load_project_settings(project_root: Path) -> Optional[Dict[str, Any]]:
    """
    Load project-specific settings.json.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dict of settings, or None if not found
    """
    settings_path = project_root / ".claude" / "settings.json"
    
    if not settings_path.exists():
        return None
    
    try:
        with open(settings_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading project settings: {e}")
        return None


def load_shared_settings(shared_root: Path) -> Optional[Dict[str, Any]]:
    """
    Load shared settings.json from .claude-shared.
    
    Args:
        shared_root: Root directory of .claude-shared
        
    Returns:
        Dict of settings, or None if not found
    """
    settings_path = shared_root / ".claude" / "settings.json"
    
    if not settings_path.exists():
        return None
    
    try:
        with open(settings_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading shared settings: {e}")
        return None


def merge_settings(project: Dict[str, Any], shared: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge project and shared settings with proper precedence.
    
    Rules:
    - Project settings override shared settings for same keys
    - Nested dicts are merged recursively
    - Lists are replaced (not merged)
    
    Args:
        project: Project-specific settings
        shared: Shared settings
        
    Returns:
        Merged settings dict
    """
    if not project:
        return shared.copy() if shared else {}
    
    if not shared:
        return project.copy()
    
    # Start with a copy of shared
    result = shared.copy()
    
    # Recursively merge project settings
    for key, value in project.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dicts
            result[key] = merge_settings(value, result[key])
        else:
            # Replace value (project overrides shared)
            result[key] = value
    
    return result


def find_claude_config(project_root: Path) -> Optional[Path]:
    """
    Find .claude configuration directory.
    
    Args:
        project_root: Root directory to search from
        
    Returns:
        Path to .claude directory, or None if not found
    """
    claude_dir = project_root / ".claude"
    
    if claude_dir.exists() and claude_dir.is_dir():
        return claude_dir
    
    # Try parent directories (up to 3 levels)
    for parent in [project_root.parent, project_root.parent.parent]:
        claude_dir = parent / ".claude"
        if claude_dir.exists() and claude_dir.is_dir():
            return claude_dir
    
    return None


def get_environment_mode(project_root: Path) -> str:
    """
    Detect environment mode (production vs development).
    
    Checks for indicators like:
    - Project path contains "prod", "production"
    - Project path contains "dev", "development"
    - Environment variable CLAUDE_ENV
    - settings.json "environment" field
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        "production" or "development" (defaults to "development")
    """
    import os
    
    # Check environment variable
    env = os.getenv("CLAUDE_ENV", "").lower()
    if "prod" in env:
        return "production"
    if "dev" in env:
        return "development"
    
    # Check project path
    path_str = str(project_root).lower()
    if "prod" in path_str or "production" in path_str:
        return "production"
    if "dev" in path_str or "development" in path_str:
        return "development"
    
    # Check settings.json
    settings = load_project_settings(project_root)
    if settings and "environment" in settings:
        env_setting = settings["environment"].lower()
        if "prod" in env_setting:
            return "production"
        if "dev" in env_setting:
            return "development"
    
    # Default to development (safer)
    return "development"


def load_merged_settings(project_root: Path, shared_root: Path) -> Dict[str, Any]:
    """
    Load and merge project + shared settings in one call.
    
    Args:
        project_root: Root directory of the project
        shared_root: Root directory of .claude-shared
        
    Returns:
        Merged settings dict
    """
    project_settings = load_project_settings(project_root) or {}
    shared_settings = load_shared_settings(shared_root) or {}
    
    return merge_settings(project_settings, shared_settings)




def matches_any_pattern(command: str, patterns: List[str]) -> bool:
    """
    Check if command matches any pattern in the list.
    
    Supports:
    - Simple substring matching
    - Wildcard patterns with * (converted to regex)
    - Regex patterns (if they contain regex special chars)
    
    Args:
        command: Command to check
        patterns: List of patterns to match against
        
    Returns:
        True if command matches any pattern
    """
    for pattern in patterns:
        # Simple substring match
        if pattern in command:
            return True
        
        # Wildcard pattern (convert * to .*)
        if '*' in pattern:
            regex_pattern = pattern.replace('*', '.*')
            if re.search(regex_pattern, command, re.IGNORECASE):
                return True
        
        # Try as regex pattern
        try:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        except re.error:
            # Not a valid regex, skip
            pass
    
    return False


def get_permission_decision(command: str, tool: str, settings: Dict[str, Any]) -> str:
    """
    Get permission decision for a command using priority rules.
    
    Priority: deny > ask > allow > default_deny
    
    Args:
        command: Command to check
        tool: Tool name (e.g., "bash")
        settings: Merged settings dict
        
    Returns:
        "deny", "ask", "allow", or "default_deny"
    """
    if "permissions" not in settings:
        return "default_deny"
    
    if tool not in settings["permissions"]:
        return "default_deny"
    
    tool_permissions = settings["permissions"][tool]
    
    # Priority 1: Check deny list (highest priority)
    deny_patterns = tool_permissions.get("deny", [])
    if matches_any_pattern(command, deny_patterns):
        return "deny"
    
    # Priority 2: Check ask dict (medium priority)
    ask_patterns = list(tool_permissions.get("ask", {}).keys())
    if matches_any_pattern(command, ask_patterns):
        return "ask"
    
    # Priority 3: Check allow list (lowest priority)
    allow_patterns = tool_permissions.get("allow", [])
    if matches_any_pattern(command, allow_patterns):
        return "allow"
    
    # Default: deny if not explicitly allowed
    return "default_deny"


def get_permission_level(settings: Dict[str, Any], tool: str, command: str) -> str:
    """
    Determine permission level for a command.
    
    Priority: deny > ask > allow > default_deny
    
    Args:
        settings: Merged settings dict
        tool: Tool name (e.g., "bash")
        command: Command to check
        
    Returns:
        "deny", "ask", "allow", or "default_deny"
    """
    return get_permission_decision(command, tool, settings)


def validate_settings_schema(settings: Dict[str, Any]) -> bool:
    """
    Validate that settings dict has correct structure.
    
    Args:
        settings: Settings dict to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(settings, dict):
        return False
    
    # Check for required top-level keys
    if "permissions" in settings:
        permissions = settings["permissions"]
        if not isinstance(permissions, dict):
            return False
        
        # Validate each tool's permissions
        for tool, perms in permissions.items():
            if not isinstance(perms, dict):
                return False
            
            # Check that deny/allow are lists
            if "deny" in perms and not isinstance(perms["deny"], list):
                return False
            if "allow" in perms and not isinstance(perms["allow"], list):
                return False
            
            # Check that ask is a dict
            if "ask" in perms and not isinstance(perms["ask"], dict):
                return False
    
    return True
