# Spec-Kit 2.0 - Framework de Desarrollo de Features Estructurado

Framework simplificado para desarrollo dirigido por especificaciones con orchestración inteligente de agentes.

## 🎯 Visión General

Spec-Kit 2.0 es un workflow automatizado que traduce descripciones de features en implementaciones completas:

```
Idea → Spec → Plan → Tasks → Implementation
```

**Mejoras en 2.0**:
- ✅ **Simplificado**: 5 comandos core (antes 10)
- ✅ **Automático**: Clarificación, validación y enrichment integrados
- ✅ **Inteligente**: Auto-context desde project-context.json
- ✅ **Sin pasos manuales**: tasks-richer.py eliminado, todo inline
- ✅ **Governance simple**: ADRs inmutables vs constitution versionado

---

## 📋 Workflow Simplificado

### Paso 0: Bootstrap (Una vez por proyecto)
```bash
/speckit.init
```
- Valida/crea `project-context.json`
- Configura paths de GitOps, Terraform, GCP
- Ready para crear features

### Paso 1: Especificar Feature
```bash
/speckit.specify spec-kit-tcm-plan Add dark mode toggle to settings
```
- Crea `spec.md` con template
- **AUTO-LLENA** project context (cluster, namespace, paths)
- Genera functional requirements y user stories
- Output: `specs/00N-dark-mode-toggle/spec.md`

### Paso 2: Planear Implementación
```bash
/speckit.plan spec-kit-tcm-plan 00N-dark-mode-toggle
```
- **INTEGRA clarify**: Detecta ambigüedades, pregunta inline (max 5 questions)
- Lee governance.md para standards
- Genera plan técnico con arquitectura, data model, contracts
- Output: `plan.md`, `data-model.md`, `contracts/`, `research.md`

### Paso 3: Generar Tareas
```bash
/speckit.tasks spec-kit-tcm-plan 00N-dark-mode-toggle
```
- Genera tasks.md con metadata INLINE (no post-process)
- **INTEGRA validation**: Auto-detecta coverage gaps, inconsistencias
- **AUTO-ENRICH**: Cada task con agent, tier, tags, confidence
- **GATE**: Pausa si issues CRITICAL
- Output: `tasks.md` (listo para implement)

### Paso 4: Implementar
```bash
/speckit.implement spec-kit-tcm-plan 00N-dark-mode-toggle
```
- Lee tasks.md enriquecido
- Auto-ejecuta tasks con agentes especializados
- T2/T3 tasks → Auto-análisis antes de ejecutar
- TaskManager para files >25K tokens
- Output: Código implementado, tests, docs

---

## 🚀 Comandos Core (5)

| Comando | Propósito | Integra |
|---------|-----------|---------|
| `/speckit.init` | Bootstrap project configuration | project-context.json validation |
| `/speckit.specify` | Create feature spec | Auto-context filling |
| `/speckit.plan` | Generate implementation plan | Clarification (inline) |
| `/speckit.tasks` | Generate enriched task list | Validation + Enrichment (inline) |
| `/speckit.implement` | Execute tasks with agents | High-risk analysis (auto) |

## 🛠️ Comandos Auxiliares (3)

| Comando | Uso |
|---------|-----|
| `/speckit.add-task` | Add single task during implementation (inline enrichment) |
| `/speckit.analyze-task` | Deep analysis of specific task (auto-triggered for T2/T3) |
| `/save-session` | Export session bundle with context |

---

## 📁 Estructura de Proyecto

```
.claude-shared/speckit/
├── governance.md                 # Project-wide principles (NO versioning)
├── decisions/                    # ADRs (immutable records)
│   └── ADR-001-example.md
├── templates/
│   ├── spec-template.md
│   ├── plan-template.md
│   ├── tasks-template.md
│   └── adr-template.md
├── scripts/                      # Bash automation
└── README.md                     # This file

<speckit-root>/                   # e.g., spec-kit-tcm-plan/
└── specs/
    ├── 001-feature-name/
    │   ├── spec.md               # Auto-filled with project context
    │   ├── plan.md               # With clarifications integrated
    │   ├── tasks.md              # With inline metadata
    │   ├── data-model.md
    │   └── contracts/
    └── 002-another-feature/
```

---

## 🔑 Características Clave

### 1. Auto-Context desde project-context.json

`/specify` automáticamente llena:
- `[PROJECT_ID]` → `aaxis-rnd-general-project`
- `[CLUSTER]` → `tcm-gke-non-prod`
- `[GITOPS_PATH]` → `/path/to/gitops`
- `[TERRAFORM_PATH]` → `/path/to/terraform`

**Sin project-context.json**: Pregunta interactivamente y sugiere ejecutar `/init`.

### 2. Clarification Integrada en /plan

ANTES (Spec-Kit 1.0):
```bash
/specify ...
/clarify ...      # Manual step
/plan ...
```

AHORA (Spec-Kit 2.0):
```bash
/specify ...
/plan ...         # Clarify happens inline automatically
```

### 3. Validation Integrada en /tasks

ANTES:
```bash
/tasks ...
/analyze-plan ... # Manual validation
```

AHORA:
```bash
/tasks ...        # Validation happens inline automatically
```

### 4. Task Enrichment Inline

ANTES:
```bash
/tasks ...
python3 tasks-richer.py ... # Manual enrichment
```

AHORA:
```bash
/tasks ...        # Enrichment happens during generation
```

Cada task generada con:
```markdown
- [ ] T001 Create GKE cluster configuration
  <!-- 🤖 Agent: terraform-architect | 👁️ T0 | ⚡ 0.85 -->
  <!-- 🏷️ Tags: #terraform #infrastructure #gke -->
  <!-- 🎯 skill: terraform_infrastructure (8.0) -->
```

### 5. Governance con ADRs (No Versioning)

ANTES:
- `constitution.md` con semantic versioning (MAJOR.MINOR.PATCH)
- Complex template propagation
- Per-feature versioning

AHORA:
- `governance.md` simple (project-wide standards)
- ADRs para decisions (immutable, one per decision)
- Git history = versioning (no manual version numbers)

**Crear ADR**:
1. Copy `.claude-shared/speckit/templates/adr-template.md`
2. Fill with decision context, options, rationale
3. Save to `.claude-shared/speckit/decisions/ADR-XXX-title.md`
4. Reference in commits: `feat: implement feature (ADR-005)`

---

## 🧠 Agent Routing

Spec-Kit integra con agentes especializados:

| Agent | Triggers | Tier |
|-------|----------|------|
| **terraform-architect** | terraform, terragrunt, .tf, infrastructure, gke, vpc | T0-T3 |
| **gitops-operator** | kubectl, helm, flux, kubernetes, deployment, service | T0-T3 |
| **gcp-troubleshooter** | gcloud, GCP, cloud logging, IAM | T0 |
| **devops-developer** | docker, npm, build, test, CI, Dockerfile | T0-T1 |

**Code-First Protocol**: Todos los agentes exploran patterns existentes antes de crear nuevos recursos.

---

## 📝 Ejemplos

### Bootstrap Nuevo Proyecto
```bash
# 1. Initialize (interactive)
/speckit.init

# Questions asked:
# - GCP Project ID? aaxis-rnd-general-project
# - Region? us-central1
# - Cluster? tcm-gke-non-prod
# - GitOps path? /path/to/gitops
# - Terraform path? /path/to/terraform

# Creates .claude/project-context.json
```

### Feature Completo
```bash
# 1. Specify
/speckit.specify spec-kit-tcm-plan Add user authentication with OAuth2

# Auto-fills: project_id, cluster, gitops_path, terraform_path
# Output: specs/003-user-authentication/spec.md

# 2. Plan (with auto-clarify)
/speckit.plan spec-kit-tcm-plan 003-user-authentication

# Asks max 5 clarification questions inline:
# Q1: Which OAuth provider? (Google, GitHub, Azure)
# Q2: Session duration? (1h, 24h, 7d)
# Updates spec.md with answers
# Output: plan.md, data-model.md, contracts/

# 3. Tasks (with auto-validation)
/speckit.tasks spec-kit-tcm-plan 003-user-authentication

# Generates 25 tasks with inline metadata
# Validates coverage (100%), no critical issues
# Output: tasks.md (ready to implement)

# 4. Implement
/speckit.implement spec-kit-tcm-plan 003-user-authentication

# Executes tasks with agents:
# T001 → terraform-architect (T2)
# T002 → gitops-operator (T3)
# T003 → devops-developer (T1)
# Output: Código + commits
```

### Agregar Task Durante Implementación
```bash
/speckit.add-task spec-kit-tcm-plan 003-user-authentication

# Interactive:
# Task description? Configure session timeout middleware
# Task ID? T026
# Phase? Integration
# Parallel? No

# Generates with inline metadata:
# - [ ] T026 Configure session timeout middleware
#   <!-- 🤖 Agent: devops-developer | ✅ T1 | ⚡ 0.75 -->
#   <!-- 🏷️ Tags: #config #security #middleware -->
```

---

## 🔧 Troubleshooting

### Error: project-context.json not found
```bash
/speckit.init
# Creates .claude/project-context.json interactively
```

### Error: Task file exceeds token limit (>25K)
TaskManager handles this automatically during `/implement`. No manual intervention.

### Error: CRITICAL issues in validation
```markdown
### Validation Report
Issues: 1 critical, 2 high

| ID | Severity | Summary |
|----|----------|---------|
| A1 | CRITICAL | "Performance monitoring" has zero tasks |

# Fix: Add tasks or mark as out-of-scope in spec.md
```

### Warning: High-risk task (T2/T3)
```markdown
T055 Apply Terraform VPC changes (T3)
⚠️ HIGH RISK: Analyze before execution

# /speckit.analyze-task auto-triggered
# User approval required before execution
```

---

## 📚 Governance

- **Standards**: `.claude-shared/speckit/governance.md`
- **Decisions**: `.claude-shared/speckit/decisions/ADR-XXX-title.md`
- **Commit Format**: Conventional Commits (enforced by hooks)
- **Security Tiers**: T0 (read) → T1 (validate) → T2 (plan) → T3 (apply)

---

## 🆕 What's New in 2.0

| Feature | 1.0 | 2.0 |
|---------|-----|-----|
| Commands | 10 | **5 core + 3 aux** |
| Clarify | Manual `/clarify` | **Integrated in `/plan`** |
| Validation | Manual `/analyze-plan` | **Integrated in `/tasks`** |
| Enrichment | External `tasks-richer.py` | **Inline during generation** |
| Governance | Versioned constitution.md | **governance.md + ADRs** |
| Init | Deprecated | **Revived with project-context** |
| Auto-context | None | **project-context.json integration** |

---

## 📖 Ver También

- [Agent Prompts](../.claude-shared/agents/) - terraform-architect, gitops-operator, etc.
- [Governance](governance.md) - Project-wide standards
- [ADR Template](templates/adr-template.md) - Decision record template
- [CLAUDE.md](../../CLAUDE.md) - Orchestrator workflow

---

**Versión**: 2.0.0
**Última actualización**: 2025-11-05
**Maintainers**: Claude Code Agent System
