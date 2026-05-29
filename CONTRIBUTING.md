# Contributing to Tecno Spark Solutions

Welcome to the Buddy AI Operating System project! We're building the world's most advanced AI ecosystem. Here's how you can help.

## Code of Conduct

- Be respectful and inclusive
- Focus on the problem, not the person
- Welcome diverse perspectives
- Help others grow

## Getting Started

1. **Fork the repository**
2. **Clone your fork**: `git clone <your-fork-url>`
3. **Create a branch**: `git checkout -b feature/your-feature-name`
4. **Set up development**: `make setup && make dev`
5. **Make changes and test**
6. **Commit with clear messages**
7. **Push and create a PR**

## Development Workflow

### Backend Development
```bash
cd backend
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate  # Windows

uvicorn api.main:app --reload
```

### Frontend Development
```bash
cd frontend-web
npm run dev
```

### Run Tests
```bash
make test          # All tests
cd backend && pytest tests/unit  # Just unit tests
```

### Code Quality
```bash
make lint          # Check code quality
make format        # Auto-format code
```

## Commit Messages

Use clear, descriptive commit messages:

```
[Component] Brief description

Longer explanation of the change, why it was made, and any relevant context.

Fixes #123  (if applicable)
```

Examples:
- `[Backend] Implement intent router for agent dispatch`
- `[Frontend] Add chat interface component`
- `[Agents] Create base agent framework`
- `[Docs] Update README with setup instructions`

## Pull Requests

### PR Title Format
```
[Component] Brief description
```

### PR Checklist
- [ ] Tests pass locally (`make test`)
- [ ] Code follows style guidelines (`make lint`)
- [ ] Commits are clear and descriptive
- [ ] Documentation is updated
- [ ] No breaking changes (or documented)

### PR Description Template
```markdown
## What
Brief description of the changes

## Why
Why are these changes necessary?

## How
How do the changes work?

## Testing
How to test the changes?

## Related
Fixes #123
Relates to #456
```

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use Black for formatting

```python
async def process_intent(
    intent: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """Process user intent and return response."""
    pass
```

### TypeScript/React
- Use TypeScript for type safety
- Follow ESLint rules
- Use functional components
- Maximum line length: 100 characters

```typescript
interface AgentProps {
  agentId: string
  onProcess: (intent: string) => Promise<void>
}

const AgentComponent: React.FC<AgentProps> = ({
  agentId,
  onProcess
}) => {
  // Implementation
}
```

## Project Structure

Understand the architecture before contributing:

```
Backend Layers:
1. API (fastapi routes)
2. Services (business logic)
3. Core (buddy core, agent manager)
4. Agents (agent implementations)
5. DB (database models)

Frontend Layers:
1. Pages (page components)
2. Components (reusable UI)
3. Hooks (custom hooks)
4. Store (state management)
5. API (API client)
```

## Agent Development

To create a new agent:

1. **Create agent folder**: `backend/agents/my_agent/`
2. **Inherit from BaseAgent**:
   ```python
   from agents.base_agent import BaseAgent, Tool

   class MyAgent(BaseAgent):
       def __init__(self):
           super().__init__(
               agent_id="my_agent",
               name="My Agent",
               description="What does this agent do?"
           )

       async def process_intent(self, intent: str, context: dict) -> dict:
           # Implementation
           pass

       async def execute_action(self, action: str, parameters: dict) -> dict:
           # Implementation
           pass

       def register_tools(self) -> List[Tool]:
           # Return list of tools
           pass
   ```

3. **Register with Buddy Core**
4. **Add tests**
5. **Add documentation**

## Testing

### Unit Tests
```python
# backend/tests/unit/test_my_component.py
import pytest

@pytest.mark.asyncio
async def test_process_intent():
    # Test implementation
    pass
```

### Integration Tests
```python
# backend/tests/integration/test_agent_workflow.py
@pytest.mark.asyncio
async def test_multi_agent_workflow():
    # Test implementation
    pass
```

### Frontend Tests
```typescript
// frontend-web/src/__tests__/Component.test.tsx
import { render, screen } from '@testing-library/react'
import Component from '@components/Component'

test('renders component', () => {
  render(<Component />)
  expect(screen.getByText(/text/i)).toBeInTheDocument()
})
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to functions/classes
- Create architecture docs for complex features
- Update CHANGELOG.md

## Areas to Contribute

### High Priority
- [ ] Database schema and migrations
- [ ] API endpoint implementation
- [ ] Agent implementations (Personal Assistant, Memory, etc.)
- [ ] Frontend UI components
- [ ] Real-time WebSocket communication
- [ ] Ollama integration for local models

### Medium Priority
- [ ] Enhanced memory systems
- [ ] Multi-agent coordination
- [ ] Workflow builder
- [ ] Integration marketplace
- [ ] Analytics dashboard

### Welcome but Not Required
- [ ] Performance optimizations
- [ ] UI/UX improvements
- [ ] Documentation enhancements
- [ ] Tooling improvements

## Questions or Issues?

- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions
- **Discord**: Join the community (link coming)

---

Thank you for contributing to making AI work for everyone! 🚀
