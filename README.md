# @jaguilar87/gaia-ops

Multi-agent orchestration system for Claude Code - DevOps automation toolkit.

## Overview

**Gaia-Ops** provides a complete agent orchestration system for Claude Code, enabling intelligent automation of DevOps workflows through specialized AI agents.

### Features

- **6 specialist agents** (terraform-architect, gitops-operator, gcp-troubleshooter, aws-troubleshooter, devops-developer, claude-architect)
- **3 meta-agents** (Explore, Plan, claude-architect)
- **Clarification engine** for ambiguity detection
- **Approval gates** for T3 operations (terraform apply, kubectl apply, etc.)
- **Git commit validation** with Conventional Commits
- **Context provisioning** system for intelligent agent routing
- **Complete documentation** (orchestration workflow, git standards, agent catalog)

## Installation

### Quick Start (Recommended)

Use the built-in interactive installer to set up Gaia-Ops in any project:

```bash
npx @jaguilar87/gaia-ops init
```

Or if installed globally:

```bash
npm install -g @jaguilar87/gaia-ops
gaia-init
```

This will:
1. Auto-detect your project structure (GitOps, Terraform, AppServices)
2. Ask you a few questions about your project
3. Install Claude Code if not present
4. Create `.claude/` directory with symlinks to this package
5. Generate `CLAUDE.md` with correct paths
6. Generate `AGENTS.md` symlink
7. Create `project-context.json` with your configuration

### Manual Installation

If you prefer manual setup:

```bash
npm install @jaguilar87/gaia-ops
```

Then create symlinks:

```bash
mkdir -p .claude
cd .claude
ln -s ../node_modules/@jaguilar87/gaia-ops/agents agents
ln -s ../node_modules/@jaguilar87/gaia-ops/tools tools
ln -s ../node_modules/@jaguilar87/gaia-ops/hooks hooks
ln -s ../node_modules/@jaguilar87/gaia-ops/commands commands
ln -s ../node_modules/@jaguilar87/gaia-ops/templates templates
ln -s ../node_modules/@jaguilar87/gaia-ops/config config
ln -s ../node_modules/@jaguilar87/gaia-ops/CHANGELOG.md CHANGELOG.md
```

## Usage

Once installed, the agent system is ready to use with Claude Code:

```bash
claude-code
```

Claude Code will automatically load `CLAUDE.md` and have access to all agents via the `.claude/` directory.

## Project Structure

```
node_modules/@jaguilar87/gaia-ops/
├── agents/              # Agent definitions
│   ├── terraform-architect.md
│   ├── gitops-operator.md
│   ├── gcp-troubleshooter.md
│   ├── aws-troubleshooter.md
│   ├── devops-developer.md
│   └── claude-architect.md
├── tools/               # Orchestration tools
│   ├── context_provider.py
│   ├── agent_router.py
│   ├── clarify_engine.py
│   ├── approval_gate.py
│   ├── commit_validator.py
│   └── task_manager.py
├── hooks/               # Git hooks
│   └── pre-commit
├── commands/            # Slash commands
│   ├── architect.md
│   └── speckit.*.md
├── config/              # Configuration & documentation
│   ├── AGENTS.md
│   ├── orchestration-workflow.md
│   ├── git-standards.md
│   ├── context-contracts.md
│   ├── agent-catalog.md
│   └── git_standards.json
├── templates/           # Code templates
│   ├── CLAUDE.template.md
│   └── code-examples/
│       ├── commit_validation.py
│       ├── clarification_workflow.py
│       └── approval_gate_workflow.py
├── config/              # Configuration
│   └── git_standards.json
├── CLAUDE.md            # Core orchestrator instructions
├── AGENTS.md            # System overview
├── CHANGELOG.md         # Version history
├── package.json
└── index.js             # Helper functions
```

## Your Project Structure

After installation:

```
your-project/
├── .claude/                 # Symlinked to node_modules/@aaxis/claude-agents/
│   ├── agents/              → node_modules/@aaxis/claude-agents/agents/
│   ├── tools/               → node_modules/@aaxis/claude-agents/tools/
│   ├── hooks/               → node_modules/@aaxis/claude-agents/hooks/
│   ├── commands/            → node_modules/@aaxis/claude-agents/commands/
│   ├── docs/                → node_modules/@aaxis/claude-agents/docs/
│   ├── templates/           → node_modules/@aaxis/claude-agents/templates/
│   ├── config/              → node_modules/@aaxis/claude-agents/config/
│   ├── CHANGELOG.md         → node_modules/@aaxis/claude-agents/CHANGELOG.md
│   ├── logs/                # Project-specific (NOT symlinked)
│   ├── tests/               # Project-specific (NOT symlinked)
│   └── project-context.json # Project-specific (NOT symlinked)
├── CLAUDE.md                # Generated from template
├── AGENTS.md                → node_modules/@aaxis/claude-agents/AGENTS.md
├── gitops/                  # Your GitOps manifests
├── terraform/               # Your Terraform code
├── app-services/            # Your application code
├── node_modules/
│   └── @aaxis/
│       └── claude-agents/   # This package
└── package.json
```

## API

If you need to programmatically access paths in the package:

```javascript
import {
  getAgentPath,
  getToolPath,
  getDocPath
} from '@aaxis/claude-agents';

const agentPath = getAgentPath('gitops-operator');
// → /path/to/node_modules/@aaxis/claude-agents/agents/gitops-operator.md

const toolPath = getToolPath('context_provider.py');
// → /path/to/node_modules/@aaxis/claude-agents/tools/context_provider.py

const docPath = getDocPath('orchestration-workflow.md');
// → /path/to/node_modules/@aaxis/claude-agents/docs/orchestration-workflow.md
```

## Versioning

This package follows [Semantic Versioning](https://semver.org/):

- **MAJOR:** Breaking changes to orchestrator behavior
- **MINOR:** New features, agents, or improvements
- **PATCH:** Bug fixes, clarifications, typos

Current version: **2.1.0**

See [CHANGELOG.md](./CHANGELOG.md) for version history.

## Documentation

- **Core Instructions:** [CLAUDE.md](./CLAUDE.md) (154 lines)
- **System Overview:** [AGENTS.md](./AGENTS.md) (95 lines)
- **Orchestration Workflow:** [docs/orchestration-workflow.md](./docs/orchestration-workflow.md) (735 lines)
- **Git Standards:** [docs/git-standards.md](./docs/git-standards.md) (682 lines)
- **Context Contracts:** [docs/context-contracts.md](./docs/context-contracts.md) (673 lines)
- **Agent Catalog:** [docs/agent-catalog.md](./docs/agent-catalog.md) (603 lines)

## Requirements

- **Node.js:** >=18.0.0
- **Python:** >=3.9
- **Claude Code:** Latest version
- **Git:** >=2.30

## Project Context Management

Gaia-Ops uses a versioned project context for SSOT. After installation, clone your project context:

```bash
cd .claude
git clone git@bitbucket.org:yourorg/your-project-context.git project-context
```

This keeps `project-context.json` versioned separately, while `session/` data remains local.

See [rnd-project-context](https://bitbucket.org/aaxisdigital/rnd-project-context) for an example.

## Support

- **Issues:** [GitHub Issues](https://github.com/metraton/gaia-ops/issues)
- **Repository:** [github.com/metraton/gaia-ops](https://github.com/metraton/gaia-ops)
- **Author:** Jorge Aguilar <jaguilar1897@gmail.com>

## License

MIT License - See [LICENSE](./LICENSE) for details.
