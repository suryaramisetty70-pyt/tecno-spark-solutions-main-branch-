use std::collections::HashMap;
use std::sync::{Arc, Mutex, OnceLock};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SwarmTopology {
    Mesh,
    Hierarchical,
}

#[derive(Debug, Clone)]
pub struct SwarmAgent {
    pub id: String,
    pub name: String,
    pub agent_type: String,
    pub status: String,
}

pub struct SwarmCoordinator {
    pub topology: SwarmTopology,
    pub agents: Mutex<HashMap<String, SwarmAgent>>,
}

impl SwarmCoordinator {
    pub fn new(topology: SwarmTopology) -> Self {
        Self {
            topology,
            agents: Mutex::new(HashMap::new()),
        }
    }

    pub fn register_agent(&self, agent: SwarmAgent) {
        if let Ok(mut agents) = self.agents.lock() {
            agents.insert(agent.id.clone(), agent);
        }
    }

    pub fn unregister_agent(&self, id: &str) {
        if let Ok(mut agents) = self.agents.lock() {
            agents.remove(id);
        }
    }

    pub fn list_agents(&self) -> Vec<SwarmAgent> {
        if let Ok(agents) = self.agents.lock() {
            agents.values().cloned().collect()
        } else {
            Vec::new()
        }
    }
}

pub fn global_swarm_coordinator() -> &'static SwarmCoordinator {
    static COORDINATOR: OnceLock<SwarmCoordinator> = OnceLock::new();
    COORDINATOR.get_or_init(|| SwarmCoordinator::new(SwarmTopology::Hierarchical))
}
