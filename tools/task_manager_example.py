"""
TaskManager Usage Examples

This file demonstrates practical usage patterns for TaskManager
in the context of the orchestrator workflow.
"""

from task_manager import TaskManager
import sys


def orchestrator_workflow_example():
    """
    Example: Orchestrator workflow for task management
    
    Shows how orchestrator would:
    1. Get pending tasks
    2. Present them to user
    3. Execute a task
    4. Mark it complete
    """
    
    tasks_file = '/home/jaguilar/aaxis/rnd/repositories/spec-kit-tcm-plan/specs/001-tcm-deployment-plan/tasks.md'
    
    print("="*60)
    print("ORCHESTRATOR WORKFLOW EXAMPLE")
    print("="*60)
    
    # Initialize TaskManager
    tm = TaskManager(tasks_file)
    
    # Step 1: Get project statistics
    print("\n[STEP 1] Project Status Overview")
    stats = tm.get_task_statistics()
    print(f"Project Completion: {stats['completion_rate']}%")
    print(f"Remaining Tasks: {stats['pending_tasks']}/{stats['total_tasks']}")
    
    # Step 2: Get next pending tasks
    print("\n[STEP 2] Next Pending Tasks")
    pending_tasks = tm.get_pending_tasks(limit=5)
    
    if not pending_tasks:
        print("✅ No pending tasks - Project complete!")
        return
    
    print(f"\nFound {len(pending_tasks)} pending tasks:")
    for i, task in enumerate(pending_tasks, 1):
        print(f"{i}. {task['task_id']}: {task['title']}")
    
    # Step 3: Get details for first pending task
    print(f"\n[STEP 3] Task Details for {pending_tasks[0]['task_id']}")
    task_details = tm.get_task_details(pending_tasks[0]['task_id'])
    
    print(f"Task: {task_details['title']}")
    print(f"Status: {task_details['status']}")
    
    if task_details['metadata']['agent']:
        print(f"Agent: {task_details['metadata']['agent']}")
        print(f"Security Tier: {task_details['metadata']['security_tier']}")
    
    if task_details['description']:
        print(f"\nDescription:")
        print(f"  {task_details['description'][:150]}...")
    
    if task_details['acceptance_criteria']:
        print(f"\nAcceptance Criteria:")
        for criterion in task_details['acceptance_criteria'][:3]:
            print(f"  - {criterion}")
    
    # Step 4: Simulate task completion (COMMENTED OUT)
    print(f"\n[STEP 4] Mark Task Complete (Simulated)")
    print(f"NOTE: This is a DRY RUN - not actually marking task complete")
    print(f"To actually mark complete, uncomment the following line:")
    print(f"  tm.mark_task_complete('{pending_tasks[0]['task_id']}')")
    
    # Uncomment to actually mark task complete:
    # result = tm.mark_task_complete(pending_tasks[0]['task_id'])
    # if result:
    #     print(f"✅ Task {pending_tasks[0]['task_id']} marked complete")
    # else:
    #     print(f"⚠️  Task {pending_tasks[0]['task_id']} was already complete")
    
    print("\n" + "="*60)


def bulk_task_analysis_example():
    """
    Example: Bulk analysis of all pending tasks
    
    Shows how to analyze tasks by agent, security tier, etc.
    """
    
    tasks_file = '/home/jaguilar/aaxis/rnd/repositories/spec-kit-tcm-plan/specs/001-tcm-deployment-plan/tasks.md'
    
    print("\n" + "="*60)
    print("BULK TASK ANALYSIS EXAMPLE")
    print("="*60)
    
    tm = TaskManager(tasks_file)
    
    # Get all pending tasks (use large limit)
    pending_tasks = tm.get_pending_tasks(limit=100)
    
    # Analyze by agent
    print("\n[ANALYSIS] Tasks by Agent:")
    agent_count = {}
    
    for task in pending_tasks:
        details = tm.get_task_details(task['task_id'])
        agent = details['metadata'].get('agent', 'unassigned')
        agent_count[agent] = agent_count.get(agent, 0) + 1
    
    for agent, count in sorted(agent_count.items()):
        print(f"  {agent}: {count} tasks")
    
    # Analyze by security tier
    print("\n[ANALYSIS] Tasks by Security Tier:")
    tier_count = {}
    
    for task in pending_tasks:
        details = tm.get_task_details(task['task_id'])
        tier = details['metadata'].get('security_tier', 'unknown')
        tier_count[tier] = tier_count.get(tier, 0) + 1
    
    for tier, count in sorted(tier_count.items()):
        print(f"  {tier}: {count} tasks")
    
    print("\n" + "="*60)


def quick_status_check_example():
    """
    Example: Quick status check for a specific task
    
    Shows how to quickly check task status and details
    """
    
    tasks_file = '/home/jaguilar/aaxis/rnd/repositories/spec-kit-tcm-plan/specs/001-tcm-deployment-plan/tasks.md'
    
    print("\n" + "="*60)
    print("QUICK STATUS CHECK EXAMPLE")
    print("="*60)
    
    tm = TaskManager(tasks_file)
    
    # Check specific tasks
    task_ids = ['T001', 'T010', 'T020']
    
    print("\n[CHECK] Task Status Summary:")
    for task_id in task_ids:
        try:
            details = tm.get_task_details(task_id)
            status_icon = '✅' if details['status'] == 'completed' else '⏳'
            print(f"{status_icon} {task_id}: {details['status'].upper()}")
            print(f"   {details['title'][:60]}...")
        except ValueError:
            print(f"❌ {task_id}: NOT FOUND")
    
    print("\n" + "="*60)


def error_handling_example():
    """
    Example: Proper error handling with TaskManager
    
    Shows how to handle common error scenarios
    """
    
    tasks_file = '/home/jaguilar/aaxis/rnd/repositories/spec-kit-tcm-plan/specs/001-tcm-deployment-plan/tasks.md'
    
    print("\n" + "="*60)
    print("ERROR HANDLING EXAMPLE")
    print("="*60)
    
    # Handle file not found
    print("\n[EXAMPLE 1] Handle Missing File:")
    try:
        tm = TaskManager('/nonexistent/tasks.md')
    except FileNotFoundError as e:
        print(f"✅ Caught FileNotFoundError: File doesn't exist")
    
    # Handle invalid task ID
    print("\n[EXAMPLE 2] Handle Invalid Task ID:")
    tm = TaskManager(tasks_file)
    try:
        details = tm.get_task_details('T999999')
    except ValueError as e:
        print(f"✅ Caught ValueError: Task doesn't exist")
    
    # Handle already completed task
    print("\n[EXAMPLE 3] Handle Already Completed Task:")
    result = tm.mark_task_complete('T001')  # T001 is already complete
    if not result:
        print(f"✅ Task already complete - no action taken")
    
    # Handle invalid task format
    print("\n[EXAMPLE 4] Handle Invalid Task Format:")
    try:
        tm.mark_task_complete('INVALID_ID')
    except ValueError as e:
        print(f"✅ Caught ValueError: Invalid task format")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    # Run all examples
    orchestrator_workflow_example()
    bulk_task_analysis_example()
    quick_status_check_example()
    error_handling_example()
    
    print("\n" + "="*60)
    print("ALL EXAMPLES COMPLETED SUCCESSFULLY ✅")
    print("="*60)
