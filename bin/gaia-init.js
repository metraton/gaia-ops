#!/usr/bin/env node

/**
 * @jaguilar87/gaia-ops - Installer CLI
 *
 * Interactive installer for Gaia-Ops agent system
 *
 * Usage:
 *   npx @jaguilar87/gaia-ops init                # Interactive mode
 *   npx @jaguilar87/gaia-ops init --non-interactive  # Non-interactive mode
 *   gaia-init                                     # If installed globally
 *
 * CLI Options:
 *   --non-interactive          Skip interactive prompts, use defaults or provided values
 *   --gitops <path>            GitOps directory path
 *   --terraform <path>         Terraform directory path
 *   --app-services <path>      App services directory path
 *   --project-id <id>          GCP Project ID
 *   --region <region>          Primary region (default: us-central1)
 *   --cluster <name>           Cluster name
 *   --skip-claude-install      Skip Claude Code installation
 *
 * Environment Variables:
 *   CLAUDE_GITOPS_DIR          GitOps directory path
 *   CLAUDE_TERRAFORM_DIR       Terraform directory path
 *   CLAUDE_APP_SERVICES_DIR    App services directory path
 *   CLAUDE_PROJECT_ID          GCP Project ID
 *   CLAUDE_REGION              Primary region
 *   CLAUDE_CLUSTER_NAME        Cluster name
 *
 * Features:
 * - Auto-detects project structure (GitOps, Terraform, AppServices)
 * - Installs Claude Code if not present
 * - Generates CLAUDE.md with correct paths
 * - Creates .claude/ symlinks to npm package
 * - Non-invasive: works from any directory
 */

import { fileURLToPath } from 'url';
import { dirname, join, relative } from 'path';
import fs from 'fs/promises';
import { existsSync } from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';
import prompts from 'prompts';
import chalk from 'chalk';
import ora from 'ora';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';
import { PACKAGE_ROOT, getTemplatePath } from '@jaguilar87/gaia-ops';

const execAsync = promisify(exec);
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const CWD = process.cwd();

// ============================================================================
// Auto-detection logic
// ============================================================================

/**
 * Detect project structure by scanning for common directories
 */
async function detectProjectStructure() {
  const spinner = ora('Detecting project structure...').start();

  const detected = {
    gitops: null,
    terraform: null,
    appServices: null,
    git: null
  };

  try {
    const entries = await fs.readdir(CWD);

    // GitOps candidates
    const gitopsCandidates = [
      'gitops',
      'non-prod-rnd-gke-gitops',
      'k8s',
      'kubernetes',
      'manifests',
      'deployments'
    ];
    for (const candidate of gitopsCandidates) {
      if (entries.includes(candidate)) {
        detected.gitops = `./${candidate}`;
        break;
      }
    }

    // Terraform candidates
    const terraformCandidates = [
      'terraform',
      'tf',
      'infrastructure',
      'iac',
      'infra'
    ];
    for (const candidate of terraformCandidates) {
      if (entries.includes(candidate)) {
        detected.terraform = `./${candidate}`;
        break;
      }
    }

    // AppServices candidates
    const appServicesCandidates = [
      'app-services',
      'services',
      'apps',
      'applications',
      'src'
    ];
    for (const candidate of appServicesCandidates) {
      if (entries.includes(candidate)) {
        detected.appServices = `./${candidate}`;
        break;
      }
    }

    // Git root
    if (entries.includes('.git')) {
      detected.git = '.';
    }

    spinner.succeed('Project structure detected');
  } catch (error) {
    spinner.fail('Failed to detect project structure');
    throw error;
  }

  return detected;
}

/**
 * Check if Claude Code is installed
 */
async function checkClaudeCodeInstalled() {
  try {
    // Try 'claude' command first (common alias)
    await execAsync('claude --version');
    return true;
  } catch {
    try {
      // Fallback to 'claude-code' command
      await execAsync('claude-code --version');
      return true;
    } catch {
      return false;
    }
  }
}

// ============================================================================
// CLI Argument Parsing
// ============================================================================

/**
 * Parse CLI arguments
 */
function parseCliArguments() {
  return yargs(hideBin(process.argv))
    .usage('Usage: $0 [options]')
    .option('non-interactive', {
      alias: 'y',
      type: 'boolean',
      description: 'Skip interactive prompts, use defaults or provided values',
      default: false
    })
    .option('gitops', {
      type: 'string',
      description: 'GitOps directory path'
    })
    .option('terraform', {
      type: 'string',
      description: 'Terraform directory path'
    })
    .option('app-services', {
      type: 'string',
      description: 'App services directory path'
    })
    .option('project-id', {
      type: 'string',
      description: 'GCP Project ID'
    })
    .option('region', {
      type: 'string',
      description: 'Primary region (default: us-central1)',
      default: 'us-central1'
    })
    .option('cluster', {
      type: 'string',
      description: 'Cluster name'
    })
    .option('skip-claude-install', {
      type: 'boolean',
      description: 'Skip Claude Code installation',
      default: false
    })
    .help('h')
    .alias('h', 'help')
    .version('1.0.0')
    .alias('v', 'version')
    .parse();
}

/**
 * Get configuration from CLI args, environment variables, and detected values
 */
function getConfiguration(detected, args) {
  // Priority: CLI args > Environment variables > Detected values > Defaults

  const config = {
    gitops: args.gitops || process.env.CLAUDE_GITOPS_DIR || detected.gitops || './gitops',
    terraform: args.terraform || process.env.CLAUDE_TERRAFORM_DIR || detected.terraform || './terraform',
    appServices: args.appServices || process.env.CLAUDE_APP_SERVICES_DIR || detected.appServices || './app-services',
    projectId: args.projectId || process.env.CLAUDE_PROJECT_ID || '',
    region: args.region || process.env.CLAUDE_REGION || 'us-central1',
    clusterName: args.cluster || process.env.CLAUDE_CLUSTER_NAME || '',
    installClaudeCode: !args.skipClaudeInstall
  };

  return config;
}

/**
 * Validate required configuration values
 */
function validateConfiguration(config, nonInteractive) {
  const errors = [];

  if (!config.projectId && nonInteractive) {
    errors.push('--project-id is required in non-interactive mode');
  }

  if (!config.clusterName && nonInteractive) {
    errors.push('--cluster is required in non-interactive mode');
  }

  if (errors.length > 0) {
    console.error(chalk.red('\n❌ Configuration errors:\n'));
    errors.forEach(error => console.error(chalk.red(`  - ${error}`)));
    console.error(chalk.gray('\nProvide values via CLI args or environment variables.\n'));
    process.exit(1);
  }

  return true;
}

// ============================================================================
// Interactive prompts
// ============================================================================

/**
 * Present interactive wizard to user
 */
async function runInteractiveWizard(detected) {
  console.log(chalk.cyan.bold('\n🤖 Claude Code Agent System Installer\n'));
  console.log(chalk.gray('This wizard will set up the Claude Code agent system for your project.\n'));

  const questions = [
    {
      type: 'text',
      name: 'gitops',
      message: '📦 GitOps directory (Flux/Kubernetes manifests):',
      initial: detected.gitops || './gitops',
      validate: value => value.trim().length > 0
    },
    {
      type: 'text',
      name: 'terraform',
      message: '🔧 Terraform directory (infrastructure as code):',
      initial: detected.terraform || './terraform',
      validate: value => value.trim().length > 0
    },
    {
      type: 'text',
      name: 'appServices',
      message: '🚀 App Services directory (application code):',
      initial: detected.appServices || './app-services',
      validate: value => value.trim().length > 0
    },
    {
      type: 'text',
      name: 'projectId',
      message: '🌐 GCP Project ID (e.g., aaxis-rnd-non-prod):',
      validate: value => value.trim().length > 0
    },
    {
      type: 'text',
      name: 'region',
      message: '🌍 Primary Region (e.g., us-central1):',
      initial: 'us-central1',
      validate: value => value.trim().length > 0
    },
    {
      type: 'text',
      name: 'clusterName',
      message: '☸️  Cluster Name (e.g., non-prod-rnd-gke):',
      validate: value => value.trim().length > 0
    },
    {
      type: 'confirm',
      name: 'installClaudeCode',
      message: '📥 Install Claude Code if not present?',
      initial: true
    }
  ];

  const responses = await prompts(questions);

  // User cancelled
  if (Object.keys(responses).length < questions.length) {
    console.log(chalk.yellow('\n⚠️  Installation cancelled by user\n'));
    process.exit(0);
  }

  return responses;
}

// ============================================================================
// Installation steps
// ============================================================================

/**
 * Install Claude Code CLI
 */
async function installClaudeCode() {
  const spinner = ora('Installing Claude Code...').start();

  try {
    await execAsync('npm install -g @anthropic-ai/claude-code');
    spinner.succeed('Claude Code installed successfully');
  } catch (error) {
    spinner.fail('Failed to install Claude Code');
    console.error(chalk.red('\nError:'), error.message);
    console.log(chalk.yellow('\nPlease install Claude Code manually:'));
    console.log(chalk.gray('  npm install -g @anthropic-ai/claude-code\n'));
    throw error;
  }
}

/**
 * Create .claude/ directory structure with symlinks
 */
async function createClaudeDirectory() {
  const spinner = ora('Creating .claude/ directory...').start();

  try {
    const claudeDir = join(CWD, '.claude');

    // Create base directory
    await fs.mkdir(claudeDir, { recursive: true });

    // Calculate relative path from .claude/ to node_modules/@jaguilar87/gaia-ops
    const packagePath = join(CWD, 'node_modules', '@jaguilar87', 'gaia-ops');
    const relativePath = relative(claudeDir, packagePath);

    // Create symlinks to npm package
    const symlinks = [
      { target: join(relativePath, 'agents'), link: join(claudeDir, 'agents') },
      { target: join(relativePath, 'tools'), link: join(claudeDir, 'tools') },
      { target: join(relativePath, 'hooks'), link: join(claudeDir, 'hooks') },
      { target: join(relativePath, 'commands'), link: join(claudeDir, 'commands') },
      { target: join(relativePath, 'templates'), link: join(claudeDir, 'templates') },
      { target: join(relativePath, 'config'), link: join(claudeDir, 'config') },
      { target: join(relativePath, 'speckit'), link: join(claudeDir, 'speckit') },
      { target: join(relativePath, 'CHANGELOG.md'), link: join(claudeDir, 'CHANGELOG.md') }
    ];

    for (const { target, link } of symlinks) {
      // Remove existing symlink if present
      if (existsSync(link)) {
        await fs.unlink(link);
      }
      await fs.symlink(target, link);
    }

    // Create project-specific directories (NOT symlinked)
    await fs.mkdir(join(claudeDir, 'logs'), { recursive: true });
    await fs.mkdir(join(claudeDir, 'tests'), { recursive: true });

    spinner.succeed('.claude/ directory created with symlinks');
  } catch (error) {
    spinner.fail('Failed to create .claude/ directory');
    throw error;
  }
}

/**
 * Generate CLAUDE.md from template
 */
async function generateClaudeMd(config) {
  const spinner = ora('Generating CLAUDE.md...').start();

  try {
    // Read template
    const templatePath = getTemplatePath('CLAUDE.template.md');
    let template = await fs.readFile(templatePath, 'utf-8');

    // Replace placeholders
    template = template.replace(/{{PROJECT_ID}}/g, config.projectId);
    template = template.replace(/{{REGION}}/g, config.region);
    template = template.replace(/{{CLUSTER_NAME}}/g, config.clusterName);
    template = template.replace(/{{GITOPS_PATH}}/g, config.gitops);
    template = template.replace(/{{TERRAFORM_PATH}}/g, config.terraform);
    template = template.replace(/{{APP_SERVICES_PATH}}/g, config.appServices);

    // Write to current directory
    const claudeMdPath = join(CWD, 'CLAUDE.md');
    await fs.writeFile(claudeMdPath, template, 'utf-8');

    spinner.succeed('CLAUDE.md generated');
  } catch (error) {
    spinner.fail('Failed to generate CLAUDE.md');
    throw error;
  }
}

/**
 * Generate AGENTS.md symlink
 */
async function generateAgentsMd() {
  const spinner = ora('Creating AGENTS.md symlink...').start();

  try {
    const agentsMdLink = join(CWD, 'AGENTS.md');
    const packagePath = join(CWD, 'node_modules', '@jaguilar87', 'gaia-ops', 'config', 'AGENTS.md');
    const relativePath = relative(CWD, packagePath);

    // Remove existing if present
    if (existsSync(agentsMdLink)) {
      await fs.unlink(agentsMdLink);
    }

    await fs.symlink(relativePath, agentsMdLink);

    spinner.succeed('AGENTS.md symlink created');
  } catch (error) {
    spinner.fail('Failed to create AGENTS.md symlink');
    throw error;
  }
}

/**
 * Generate project-context.json
 */
async function generateProjectContext(config) {
  const spinner = ora('Generating project-context.json...').start();

  try {
    const projectContext = {
      version: '1.0',
      last_updated: new Date().toISOString(),
      project_details: {
        id: config.projectId,
        region: config.region,
        environment: 'non-prod',
        cluster_name: config.clusterName
      },
      terraform_infrastructure: {
        layout: {
          base_path: config.terraform,
          module_structure: 'terragrunt'
        },
        provider_credentials: {
          gcp: {
            project: config.projectId,
            region: config.region
          }
        }
      },
      gitops_configuration: {
        repository: {
          path: config.gitops,
          platform: 'flux'
        },
        flux_details: {
          namespaces: []
        }
      },
      application_services: {
        base_path: config.appServices,
        services: []
      },
      operational_guidelines: {
        commit_standards: {
          format: 'conventional_commits',
          validation_required: true,
          config_path: '.claude/config/git_standards.json'
        }
      }
    };

    const projectContextPath = join(CWD, '.claude', 'project-context.json');
    await fs.writeFile(projectContextPath, JSON.stringify(projectContext, null, 2), 'utf-8');

    spinner.succeed('project-context.json generated');
  } catch (error) {
    spinner.fail('Failed to generate project-context.json');
    throw error;
  }
}

/**
 * Install @jaguilar87/gaia-ops as dependency
 */
async function installClaudeAgentsPackage() {
  const spinner = ora('Installing @jaguilar87/gaia-ops package...').start();

  try {
    // Check if package.json exists
    const packageJsonPath = join(CWD, 'package.json');
    if (!existsSync(packageJsonPath)) {
      // Create minimal package.json
      const packageJson = {
        name: 'my-project',
        version: '1.0.0',
        private: true,
        dependencies: {}
      };
      await fs.writeFile(packageJsonPath, JSON.stringify(packageJson, null, 2), 'utf-8');
    }

    // Install @jaguilar87/gaia-ops
    // NOTE: In production, this would install from npm registry
    // For now, we'll use local path
    await execAsync('npm install @jaguilar87/gaia-ops');

    spinner.succeed('@jaguilar87/gaia-ops package installed');
  } catch (error) {
    spinner.fail('Failed to install @jaguilar87/gaia-ops');
    throw error;
  }
}

// ============================================================================
// Main installer flow
// ============================================================================

async function main() {
  try {
    // Parse CLI arguments
    const args = parseCliArguments();

    // Clear console unless in non-interactive mode
    if (!args.nonInteractive) {
      console.clear();
    }

    // Step 1: Check Claude Code installation
    const claudeCodeInstalled = await checkClaudeCodeInstalled();
    if (!claudeCodeInstalled) {
      console.log(chalk.yellow('⚠️  Claude Code is not installed\n'));
    } else {
      console.log(chalk.green('✅ Claude Code is already installed\n'));
    }

    // Step 2: Auto-detect project structure
    const detected = await detectProjectStructure();

    // Step 3: Get configuration (CLI args, env vars, detected, or interactive)
    let config;
    if (args.nonInteractive) {
      // Non-interactive mode: use CLI args, env vars, and detected values
      config = getConfiguration(detected, args);
      validateConfiguration(config, true);

      // Display configuration being used
      console.log(chalk.cyan('\n📋 Configuration:\n'));
      console.log(chalk.gray(`  GitOps:       ${config.gitops}`));
      console.log(chalk.gray(`  Terraform:    ${config.terraform}`));
      console.log(chalk.gray(`  App Services: ${config.appServices}`));
      console.log(chalk.gray(`  Project ID:   ${config.projectId}`));
      console.log(chalk.gray(`  Region:       ${config.region}`));
      console.log(chalk.gray(`  Cluster:      ${config.clusterName}\n`));
    } else {
      // Interactive mode: run wizard with pre-filled detected values
      config = await runInteractiveWizard(detected);
    }

    // Step 4: Install Claude Code if requested
    if (config.installClaudeCode && !claudeCodeInstalled) {
      await installClaudeCode();
    }

    // Step 5: Install @jaguilar87/gaia-ops package
    await installClaudeAgentsPackage();

    // Step 6: Create .claude/ directory with symlinks
    await createClaudeDirectory();

    // Step 7: Generate CLAUDE.md
    await generateClaudeMd(config);

    // Step 8: Generate AGENTS.md symlink
    await generateAgentsMd();

    // Step 9: Generate project-context.json
    await generateProjectContext(config);

    // Success message
    console.log(chalk.green.bold('\n✅ Installation complete!\n'));
    console.log(chalk.gray('Next steps:'));
    console.log(chalk.gray('  1. Review CLAUDE.md and adjust paths if needed'));
    console.log(chalk.gray('  2. Update .claude/project-context.json with your services'));
    console.log(chalk.gray('  3. Start Claude Code: claude-code\n'));
    console.log(chalk.cyan('📚 Documentation: .claude/config/\n'));

  } catch (error) {
    console.error(chalk.red('\n❌ Installation failed\n'));
    console.error(error);
    process.exit(1);
  }
}

main();
