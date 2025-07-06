# Contributing to AI-Integrated CI/CD Pipeline

Thank you for your interest in contributing to the AI-Integrated CI/CD Pipeline! This guide will help you get started with contributing to the project.

## 🎯 How to Contribute

We welcome contributions in many forms:
- 🐛 **Bug Reports** - Help us identify and fix issues
- ✨ **Feature Requests** - Suggest new capabilities
- 📝 **Documentation** - Improve guides and examples
- 💻 **Code Contributions** - Implement features and fixes
- 🧪 **Testing** - Add tests and improve coverage
- 🎨 **Examples** - Create new use cases and templates

## 🚀 Getting Started

### 1. Fork and Clone the Repository

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/ai-cicd-pipeline.git
cd ai-cicd-pipeline

# Add the upstream repository
git remote add upstream https://github.com/miltonvve/ai-cicd-pipeline.git
```

### 2. Set Up Development Environment

```bash
# Install required tools
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run tests to ensure everything works
python -m pytest tests/
```

### 3. Create a Feature Branch

```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

## 📋 Development Guidelines

### Code Style

We follow these coding standards:
- **Python**: PEP 8, Black formatting, type hints
- **JavaScript/TypeScript**: ESLint, Prettier formatting
- **YAML**: 2-space indentation, consistent structure
- **Documentation**: Clear, concise, with examples

### Commit Message Format

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(ai): add custom prompt templates for code review
fix(azure): resolve container registry authentication issue
docs(setup): update quick start guide with new prerequisites
```

### Testing Requirements

- **Unit Tests**: All new functions must have unit tests
- **Integration Tests**: Test AI integrations with mock responses
- **Documentation Tests**: Ensure all examples work correctly

```bash
# Run tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Test specific AI components
python -m pytest tests/test_ai_agents.py -v
```

## 🤖 AI Components Development

### Adding New AI Agents

1. **Create the Agent Class**:
```python
# scripts/ai-agents/new_agent.py
class NewAIAgent:
    def __init__(self):
        self.client = openai.OpenAI()
        
    def analyze(self, input_data):
        """Main analysis method"""
        # Implementation here
        pass
```

2. **Add Configuration**:
```yaml
# config/ai-agents.yml
new_agent:
  enabled: true
  model: "gpt-4"
  temperature: 0.3
  max_tokens: 1000
```

3. **Create Tests**:
```python
# tests/test_new_agent.py
def test_new_agent_analysis():
    agent = NewAIAgent()
    result = agent.analyze(test_input)
    assert result is not None
```

### AI Prompt Guidelines

- **Be Specific**: Clear, detailed instructions
- **Include Context**: Provide relevant background information
- **Set Expectations**: Define output format and requirements
- **Test Thoroughly**: Validate with various inputs

Example good prompt:
```python
PROMPT_TEMPLATE = """
You are a senior {language} developer reviewing code for security vulnerabilities.

Context:
- Project Type: {project_type}
- Security Standards: {standards}

Analyze this code for:
1. SQL injection vulnerabilities
2. XSS attack vectors
3. Authentication bypasses
4. Input validation issues

Return results in JSON format:
{
  "vulnerabilities": [
    {
      "type": "sql_injection",
      "severity": "high|medium|low", 
      "line": 42,
      "description": "User input not sanitized",
      "recommendation": "Use parameterized queries"
    }
  ]
}

Code to analyze:
{code}
"""
```

## 📚 Documentation Contributions

### Documentation Structure

```
docs/
├── implementation/     # Setup and configuration guides
├── tutorials/         # Step-by-step tutorials
├── api/              # API documentation
└── examples/         # Code examples and templates
```

### Writing Guidelines

- **Clear Headings**: Use descriptive section titles
- **Step-by-Step**: Break complex processes into steps
- **Code Examples**: Include working code samples
- **Screenshots**: Add visuals where helpful
- **Links**: Reference related documentation

### Documentation Testing

```bash
# Check markdown links
markdown-link-check docs/**/*.md

# Test code examples
python scripts/test-docs-examples.py

# Build documentation locally
mkdocs serve
```

## 🔧 Azure Infrastructure Contributions

### Bicep Templates

When modifying Azure infrastructure:

1. **Update Bicep Files**: Modify `azure/bicep/main.bicep`
2. **Test Deployment**: Validate in development environment
3. **Update Documentation**: Document new resources
4. **Add Parameters**: Make resources configurable

```bicep
// Example: Adding new resource
resource newResource 'Microsoft.Service/resourceType@2023-01-01' = {
  name: '${resourceBaseName}-new-resource'
  location: location
  tags: tags
  properties: {
    // Resource properties
  }
}
```

### Testing Infrastructure Changes

```bash
# Validate Bicep syntax
az bicep build --file azure/bicep/main.bicep

# What-if deployment
az deployment group what-if \
  --resource-group "test-rg" \
  --template-file azure/bicep/main.bicep \
  --parameters environmentName="dev"

# Deploy to test environment
az deployment group create \
  --resource-group "test-rg" \
  --template-file azure/bicep/main.bicep \
  --parameters environmentName="dev"
```

## 🧪 Testing Guidelines

### Test Categories

1. **Unit Tests**: Test individual functions/classes
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows
4. **Performance Tests**: Test AI response times and costs

### Writing Tests

```python
# Example unit test
def test_ai_code_reviewer():
    reviewer = AICodeReviewer()
    mock_response = create_mock_openai_response()
    
    with patch('openai.OpenAI.chat.completions.create', return_value=mock_response):
        result = reviewer.analyze_code("sample code")
        
    assert result['quality_score'] >= 1
    assert result['quality_score'] <= 10
    assert 'recommendations' in result

# Example integration test  
def test_deployment_decision_integration():
    engine = AIDeploymentEngine()
    
    # Test with low-risk changes
    low_risk_factors = {
        'code_complexity': 0.2,
        'dependency_changes': 0.1,
        'test_coverage': 0.1
    }
    
    decision = engine.calculate_risk_score(low_risk_factors)
    assert decision['recommended_strategy'] == 'blue_green'
```

### Mock AI Responses

```python
# Create realistic mock responses for testing
def create_mock_openai_response():
    return Mock(
        choices=[
            Mock(
                message=Mock(
                    content='{"quality_score": 8, "recommendations": ["Add error handling"]}'
                )
            )
        ]
    )
```

## 📝 Pull Request Process

### Before Submitting

- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] Commit messages follow convention
- [ ] No sensitive information in commits

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (describe)

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or breaking changes documented)

## Screenshots/Examples
<!-- Add screenshots or examples if applicable -->
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests
2. **AI Review**: Automated code quality analysis
3. **Human Review**: Maintainer reviews code
4. **Feedback**: Address any requested changes
5. **Merge**: Approved PRs are merged

## 🐛 Bug Reports

### Bug Report Template

```markdown
## Bug Description
Clear description of the issue

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Ubuntu 22.04]
- Python Version: [e.g., 3.11]
- Azure CLI Version: [e.g., 2.50.0]
- OpenAI API Version: [e.g., 1.3.0]

## Additional Context
Logs, screenshots, or other relevant information
```

## ✨ Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Solution
How should this feature work?

## Alternatives Considered
What other approaches did you consider?

## Additional Context
Any other relevant information
```

## 🚀 Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in appropriate files
- [ ] GitHub release created
- [ ] Docker images published

## 🤝 Community Guidelines

### Code of Conduct

- **Be Respectful**: Treat everyone with respect
- **Be Inclusive**: Welcome diverse perspectives
- **Be Constructive**: Provide helpful feedback
- **Be Patient**: Help newcomers learn

### Getting Help

- **Documentation**: Check existing docs first
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Discord**: Join our community Discord server

## 🎖️ Recognition

Contributors are recognized in:
- **README.md**: Contributors section
- **Release Notes**: Major contributions highlighted
- **GitHub**: Contributor badges and stats

## 📞 Contact

- **Project Maintainer**: [@miltonvve](https://github.com/miltonvve)
- **Email**: milton@vectorverseevolve.ai
- **Discord**: GenAI Guru Community

---

Thank you for contributing to the AI-Integrated CI/CD Pipeline! Your contributions help make software development smarter and more efficient for everyone. 🚀