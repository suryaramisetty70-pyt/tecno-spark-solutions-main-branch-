"""
Event Bus - Enables pub/sub communication between agents
Agents can publish events and subscribe to events from other agents
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import uuid

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Types of events in the system"""
    AGENT_REGISTERED = "agent_registered"
    AGENT_ACTIVATED = "agent_activated"
    AGENT_DEACTIVATED = "agent_deactivated"
    AGENT_ERROR = "agent_error"
    INTENT_RECEIVED = "intent_received"
    INTENT_PROCESSED = "intent_processed"
    MEMORY_SAVED = "memory_saved"
    MEMORY_RETRIEVED = "memory_retrieved"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    NOTIFICATION_SENT = "notification_sent"
    INTEGRATION_CONNECTED = "integration_connected"
    INTEGRATION_DISCONNECTED = "integration_disconnected"
    TOOL_EXECUTED = "tool_executed"
    CUSTOM = "custom"


@dataclass
class Event:
    """Represents an event in the system"""
    event_type: EventType
    source_agent: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: int = field(default=5)  # 1-10, higher = more important

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source_agent": self.source_agent,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority
        }


@dataclass
class EventSubscription:
    """Represents a subscription to events"""
    subscription_id: str
    agent_id: str
    event_types: Set[EventType]
    handler: Callable
    created_at: datetime = field(default_factory=datetime.now)
    active: bool = True


class EventBus:
    """
    Central event bus for agent communication.
    Implements pub/sub pattern for loose coupling between agents.
    """

    def __init__(self, max_event_history: int = 1000):
        """
        Initialize event bus.

        Args:
            max_event_history: Maximum number of events to keep in history
        """
        self.logger = logging.getLogger(__name__)
        self.subscriptions: Dict[str, List[EventSubscription]] = {}
        self.event_history: List[Event] = []
        self.max_event_history = max_event_history
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.logger.info("✅ Event Bus initialized")

    async def subscribe(
        self,
        agent_id: str,
        event_types: List[EventType],
        handler: Callable
    ) -> str:
        """
        Subscribe agent to events.

        Args:
            agent_id: ID of subscribing agent
            event_types: List of event types to subscribe to
            handler: Async function to call when event occurs

        Returns:
            Subscription ID
        """
        subscription_id = str(uuid.uuid4())
        subscription = EventSubscription(
            subscription_id=subscription_id,
            agent_id=agent_id,
            event_types=set(event_types),
            handler=handler
        )

        # Store subscription
        for event_type in event_types:
            key = event_type.value
            if key not in self.subscriptions:
                self.subscriptions[key] = []
            self.subscriptions[key].append(subscription)

        self.logger.info(
            f"Agent {agent_id} subscribed to {len(event_types)} event types"
        )

        return subscription_id

    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events.

        Args:
            subscription_id: Subscription ID to remove

        Returns:
            True if unsubscribed successfully
        """
        for event_type_subs in self.subscriptions.values():
            for i, sub in enumerate(event_type_subs):
                if sub.subscription_id == subscription_id:
                    event_type_subs.pop(i)
                    self.logger.info(f"Unsubscribed: {subscription_id}")
                    return True
        return False

    async def publish(
        self,
        event_type: EventType,
        source_agent: str,
        data: Dict[str, Any],
        priority: int = 5
    ) -> str:
        """
        Publish event to all subscribers.

        Args:
            event_type: Type of event
            source_agent: Agent publishing the event
            data: Event data
            priority: Event priority (1-10)

        Returns:
            Event ID
        """
        event = Event(
            event_type=event_type,
            source_agent=source_agent,
            data=data,
            priority=priority
        )

        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_event_history:
            self.event_history.pop(0)

        # Get subscribers for this event type
        subscribers = self.subscriptions.get(event_type.value, [])

        self.logger.debug(
            f"Publishing event {event_type.value} to {len(subscribers)} subscribers"
        )

        # Notify all subscribers
        for subscription in subscribers:
            if subscription.active:
                try:
                    # Queue event for async processing
                    await asyncio.create_task(
                        subscription.handler(event)
                    )
                except Exception as e:
                    self.logger.error(
                        f"Error notifying subscriber {subscription.agent_id}: {e}",
                        exc_info=True
                    )

        return event.event_id

    async def get_event_history(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get event history.

        Args:
            event_type: Filter by event type
            limit: Maximum number of events to return

        Returns:
            List of events
        """
        if event_type:
            events = [
                e for e in self.event_history
                if e.event_type == event_type
            ]
        else:
            events = self.event_history

        # Return most recent events
        return [e.to_dict() for e in events[-limit:]]

    async def get_agent_events(
        self,
        agent_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get events from specific agent.

        Args:
            agent_id: Agent ID
            limit: Maximum number of events

        Returns:
            List of events from agent
        """
        events = [
            e for e in self.event_history
            if e.source_agent == agent_id
        ]
        return [e.to_dict() for e in events[-limit:]]

    def get_bus_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        total_subscriptions = sum(
            len(subs) for subs in self.subscriptions.values()
        )

        return {
            "event_types": len(self.subscriptions),
            "total_subscriptions": total_subscriptions,
            "event_history_size": len(self.event_history),
            "max_history": self.max_event_history
        }

    async def clear_history(self) -> None:
        """Clear event history"""
        self.event_history.clear()
        self.logger.info("Event history cleared")

    async def get_subscription_info(self, agent_id: str) -> Dict[str, Any]:
        """Get subscription information for agent"""
        agent_subscriptions = []

        for event_type_subs in self.subscriptions.values():
            for sub in event_type_subs:
                if sub.agent_id == agent_id:
                    agent_subscriptions.append({
                        "subscription_id": sub.subscription_id,
                        "event_types": [et.value for et in sub.event_types],
                        "created_at": sub.created_at.isoformat(),
                        "active": sub.active
                    })

        return {
            "agent_id": agent_id,
            "subscriptions": agent_subscriptions,
            "total": len(agent_subscriptions)
        }
