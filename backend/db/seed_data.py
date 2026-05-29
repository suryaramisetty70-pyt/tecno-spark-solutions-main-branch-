"""
Seed data for database initialization (optional)
Run this after migrations to populate initial agents and system data
"""

from db.database import SyncSessionLocal
from db.models import Agent


def seed_agents():
    """Add built-in agents"""
    db = SyncSessionLocal()

    agents_data = [
        {
            "agent_id": "personal_assistant",
            "name": "Personal Assistant",
            "description": "Core orchestrator agent for multi-agent coordination",
            "version": "0.1.0",
            "status": "active",
            "capabilities": [
                "intent_understanding",
                "agent_coordination",
                "conversation",
                "task_management"
            ]
        },
        {
            "agent_id": "memory_agent",
            "name": "Memory Agent",
            "description": "Save, retrieve and manage user memories",
            "version": "0.1.0",
            "status": "active",
            "capabilities": [
                "save_memory",
                "retrieve_memory",
                "semantic_search",
                "knowledge_base_management"
            ]
        },
        {
            "agent_id": "productivity_agent",
            "name": "Productivity Agent",
            "description": "Task and to-do management",
            "version": "0.1.0",
            "status": "active",
            "capabilities": [
                "task_management",
                "time_blocking",
                "focus_mode",
                "goal_tracking"
            ]
        },
        {
            "agent_id": "email_agent",
            "name": "Email Agent",
            "description": "Email sending, receiving and management",
            "version": "0.1.0",
            "status": "active",
            "capabilities": [
                "send_email",
                "receive_email",
                "gmail_integration",
                "outlook_integration",
                "thread_management",
                "smart_replies"
            ]
        },
        {
            "agent_id": "researcher_agent",
            "name": "Researcher Agent",
            "description": "Web research and information aggregation",
            "version": "0.1.0",
            "status": "active",
            "capabilities": [
                "web_research",
                "information_aggregation",
                "source_verification",
                "report_generation"
            ]
        },
        {
            "agent_id": "student_agent",
            "name": "Student Agent",
            "description": "Academic support and learning management",
            "version": "0.1.0",
            "status": "active",
            "capabilities": [
                "assignment_tracking",
                "study_planning",
                "exam_preparation",
                "course_progress"
            ]
        },
        {
            "agent_id": "news_agent",
            "name": "News Agent",
            "description": "News aggregation and trend detection",
            "version": "0.1.0",
            "status": "active",
            "capabilities": [
                "news_aggregation",
                "topic_feeds",
                "trend_detection",
                "summary_generation"
            ]
        },
        {
            "agent_id": "automation_agent",
            "name": "Automation Agent",
            "description": "Workflow creation and task automation",
            "version": "0.1.0",
            "status": "active",
            "capabilities": [
                "workflow_creation",
                "workflow_execution",
                "task_automation",
                "integration_bridging",
                "schedule_management"
            ]
        },
    ]

    for agent_data in agents_data:
        # Check if agent already exists
        existing = db.query(Agent).filter(Agent.agent_id == agent_data["agent_id"]).first()
        if not existing:
            agent = Agent(**agent_data)
            db.add(agent)

    db.commit()
    db.close()
    print("✅ Agents seeded successfully")


if __name__ == "__main__":
    seed_agents()
