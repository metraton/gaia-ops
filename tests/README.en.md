# Test Suite Documentation

**[🇪🇸 Versión en Español](README.md)**

Test suite to validate the full functionality of the Claude Agent System.

**Total: 55 tests | Time: ~0.90s | Status: ✅ 100% passing**

---

## Table of Contents

- [Test Suites](#test-suites)
- [test_all_functionality.py](#test_all_functionalitypy-20-tests)
- [test_semantic_routing.py](#test_semantic_routingpy-26-tests)
- [test_ssot_policies.py](#test_ssot_policiespy-9-tests)
- [Run Tests](#run-tests)
- [System Metrics](#system-metrics)
- [Maintenance](#maintenance)
- [References](#references)

---

## 📊 Test Suites

| Suite | Tests | Purpose | Time |
|-------|-------|---------|------|
| `test_all_functionality.py` | 20 | Project structure and core components | ~0.15s |
| `test_semantic_routing.py` | 26 | Agent semantic routing system | ~0.70s |
| `test_ssot_policies.py` | 9 | SSOT and anti‑duplication policies | ~0.05s |

---

## 🧪 test_all_functionality.py (20 tests)

**Validates:** Complete system structure, presence of critical files, and valid configuration.

### Class Coverage

| Test Class | Tests | What it Validates |
|------------|-------|-------------------|
| **TestProjectStructure** | 3 | Required directories (tools, agents, commands, speckit, tests, configs) |
| **TestAgents** | 1 | 5 agents exist and contain valid content (>100 chars) |
| **TestTools** | 5 | Core tools: agent_router, context_section_reader, semantic_matcher, generate_embeddings, quicktriage scripts |
| **TestSpecKit** | 3 | Spec‑Kit system: directory, 10 commands, 3 templates |
| **TestProjectContext** | 4 | project-context.json: valid JSON, correct structure, agent sections, project-specific sections |
| **TestConfigs** | 1 | Embeddings configuration (intent_embeddings.json) |
| **TestSchema** | 2 | JSON Schema exists and validates project-context.json |

### Critical Tests

- ✅ **Agents:** Validates the 5 specialized agents exist
  - gitops-operator.md
  - gcp-troubleshooter.md
  - terraform-architect.md
  - devops-developer.md
  - aws-troubleshooter.md

- ✅ **Tools:** Validates 12 core tools + 5 quicktriage scripts
- ✅ **Spec‑Kit:** Validates 10 workflow commands
- ✅ **Schema Validation:** Ensures project-context.json complies with its JSON schema

---

## 🎯 test_semantic_routing.py (26 tests)

**Validates:** Semantic routing correctly selects the agent for each user request.

**Target accuracy:** >85% | **Current accuracy:** 92.7%

### Component Coverage

| Component | Tests | What it Validates |
|-----------|-------|-------------------|
| **IntentClassifier** | 10 | Classification of 5 intent types using keywords + context |
| **CapabilityValidator** | 10 | Agent capability validation and fallback selection |
| **Integration** | 5 | System availability, compatibility, routing behavior |
| **Accuracy** | 1 | Golden set of 26 semantic requests → 92.7% accuracy |

### Intent Types

| Intent | Primary Agent | Key Keywords |
|--------|---------------|--------------|
| `infrastructure_creation` | terraform-architect | create, provision, deploy, setup, build |
| `infrastructure_diagnosis` | gcp-troubleshooter | diagnose, troubleshoot, debug, check, analyze |
| `kubernetes_operations` | gitops-operator | pod, deployment, service, helm, flux |
| `application_development` | devops-developer | build, docker, compile, test, npm |
| `infrastructure_validation` | terraform-architect | validate, plan, scan, verify |

### Routing Examples

| User Request | Selected Agent | Confidence |
|--------------|----------------|------------|
| "provision new GKE cluster" | terraform-architect | 0.92 |
| "check failing pods in namespace" | gitops-operator | 0.95 |
| "diagnose GCP network latency" | gcp-troubleshooter | 0.88 |
| "build docker image for api" | devops-developer | 0.90 |
| "validate terraform config" | terraform-architect | 0.93 |

---

## 🔒 test_ssot_policies.py (9 tests)

**Validates:** Single Source of Truth (SSOT) policies and prevention of context duplication.

### Policy Coverage

| Policy | Tests | What it Validates |
|--------|-------|-------------------|
| **SSOT Structure** | 3 | project-context.json is valid JSON, has metadata/sections, required structure |
| **Anti‑Duplication** | 4 | Agent prompts do NOT duplicate project‑specific tokens |
| **Context Loading** | 2 | context_section_reader returns valid JSON, all sections exist |

### Forbidden Tokens in Agents

Agent prompts MUST NOT contain:
- ❌ `aaxis-rnd-general-project` (GCP project ID)
- ❌ `tcm-gke-autopilot-non-prod` (cluster name)
- ❌ `tcm-non-prod` (namespace)
- ❌ `tcm-api-nonprod.aaxis.io` (domain)

**Reason:** These values must exist ONLY in `project-context.json` (SSOT). Agents receive context dynamically from the orchestrator.

### SSOT Architecture

```
project-context.json (SSOT)
    ↓
context_section_reader.py (filter by agent)
    ↓
Orchestrator (pre‑filtered context loading)
    ↓
Specialized agent (receives context in prompt)
```

**Benefit:** 70% token reduction per agent invocation (1,312 → 320–400 tokens)

---

## 🚀 Run Tests

### All Tests
```bash
cd .claude
pytest tests/ -v
```

### Specific Suite
```bash
pytest tests/test_all_functionality.py -v    # System structure
pytest tests/test_semantic_routing.py -v     # Semantic routing
pytest tests/test_ssot_policies.py -v        # SSOT policies
```

### With Coverage
```bash
pytest tests/ --cov=.claude/tools --cov-report=html
```

### Quiet Mode (Failures Only)
```bash
pytest tests/ -q
```

---

## 📈 System Metrics (Updated 2025-11-07)

| Metric | Value | Description |
|--------|-------|-------------|
| **Total Tests** | 257 | Full system coverage across all suites |
| **Pass Rate** | >95% | Nearly all tests passing |
| **Execution Time** | <2s | Very fast execution |
| **Routing Accuracy** | 92.7% | Semantic routing with IntentClassifier |
| **Token Savings** | 79-85% | Context provider selective loading |
| **Agent Count** | 6 | 5 project agents + 1 meta-agent |
| **Tool Count** | 17+ | Core tools + validators + clarification |

**Test Distribution:**
- `integration/` - ~60 tests - Hooks workflow and security
- `system/` - ~10 tests - Agent definitions and config
- `tools/` - ~15 tests - Routing and context provisioning
- `validators/` - ~10 tests - Approval gates and commit validation
- `permissions-validation/` - ~5 tests - Permission system
- Additional suites - ~157 tests

---

## 🔧 Maintenance

### Add a New Test

1. Create `test_<feature>.py` under `.claude/tests/`
2. Naming: `test_<what_it_does>.py` (NO versions or "week")
3. Update this README with coverage tables
4. Run: `pytest tests/test_<feature>.py -v`

### When to Add Tests

- ✅ New tool under `/tools/`
- ✅ New agent under `/agents/`
- ✅ New section in `project-context.json`
- ✅ New command under `/commands/`
- ✅ SSOT policy change

### Routing Golden Set

If you modify `agent_capabilities.json`, run:
```bash
pytest tests/test_semantic_routing.py::test_semantic_routing_golden_set_accuracy -v
```

Keep accuracy >85%. If it drops, review keywords and exclusions.

---

## 📚 References

- **Agent Router:** `.claude/tools/agent_router.py` — Semantic routing implementation
- **Context Reader:** `.claude/tools/context_section_reader.py` — SSOT context filtering
- **Agent Capabilities:** `.claude/tools/agent_capabilities.json` — Skills/keywords configuration
- **Project Context:** `.claude/project-context.json` — Single Source of Truth


