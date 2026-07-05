use std::sync::Mutex;
use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Vote {
    pub agent_id: String,
    pub approve: bool,
    pub comment: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConsensusProposal {
    pub proposal_id: String,
    pub description: String,
    pub payload: String,
}

pub struct ConsensusManager {
    pub active_votes: Mutex<Vec<Vote>>,
}

impl ConsensusManager {
    pub fn new() -> Self {
        Self {
            active_votes: Mutex::new(Vec::new()),
        }
    }

    pub fn cast_vote(&self, vote: Vote) {
        if let Ok(mut votes) = self.active_votes.lock() {
            votes.push(vote);
        }
    }

    pub fn check_consensus(&self) -> bool {
        if let Ok(votes) = self.active_votes.lock() {
            if votes.is_empty() {
                return false;
            }
            let approves = votes.iter().filter(|v| v.approve).count();
            approves > votes.len() / 2
        } else {
            false
        }
    }

    pub fn clear_votes(&self) {
        if let Ok(mut votes) = self.active_votes.lock() {
            votes.clear();
        }
    }
}

pub fn global_consensus_manager() -> &'static ConsensusManager {
    use std::sync::OnceLock;
    static MANAGER: OnceLock<ConsensusManager> = OnceLock::new();
    MANAGER.get_or_init(ConsensusManager::new)
}
