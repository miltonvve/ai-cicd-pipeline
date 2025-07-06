# 🚀 Quick Start Tutorial

Get your AI-Integrated CI/CD Pipeline up and running in 30 minutes! This tutorial will walk you through the complete setup process step by step.

## 📋 Prerequisites

Before you begin, make sure you have:

- ✅ **Azure Account** with active subscription
- ✅ **GitHub Account** with repository access
- ✅ **Docker** installed and running
- ✅ **Azure CLI** installed (`az --version`)
- ✅ **GitHub CLI** installed (`gh --version`)
- ✅ **OpenAI API Key** (for AI features)

## 🎯 Step 1: Fork or Clone the Repository

### Option A: Fork (Recommended)
```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/ai-cicd-pipeline.git
cd ai-cicd-pipeline
```

### Option B: Use as Template
```bash
# Use the repository as a template for your project
gh repo create my-ai-pipeline --template miltonvve/ai-cicd-pipeline
cd my-ai-pipeline
```

## 🔧 Step 2: Configure Environment

### Set Environment Variables
```bash
# Export required environment variables
export AZURE_SUBSCRIPTION_ID="your-azure-subscription-id"
export OPENAI_API_KEY="your-openai-api-key"
export GITHUB_TOKEN="your-github-token"  # If not using gh cli
```

### Verify Prerequisites
```bash
# Check Azure authentication
az account show

# Check GitHub authentication
gh auth status

# Check Docker
docker --version
```

## 🚀 Step 3: Run Automated Setup

### Execute Setup Script
```bash
# Make the setup script executable
chmod +x setup-pipeline.sh

# Run the complete setup
./setup-pipeline.sh
```

The setup script will:
1. ✅ Create Azure resource group
2. ✅ Deploy Azure Container Registry
3. ✅ Set up Azure OpenAI service
4. ✅ Configure Application Insights
5. ✅ Create GitHub workflows
6. ✅ Set up Docker configurations

### Expected Output
```
🚀 Setting up AI-Integrated CI/CD Pipeline...
[INFO] Checking prerequisites...
[SUCCESS] All prerequisites are installed!
[INFO] Setting up Azure resources...
[SUCCESS] Azure resources created successfully!
[INFO] Setting up GitHub workflows...
[SUCCESS] GitHub workflows created!
[SUCCESS] 🎉 AI-Integrated CI/CD Pipeline setup completed!
```

## 🔐 Step 4: Configure GitHub Secrets

The setup script will provide you with commands to set GitHub secrets:

```bash
# Example output from setup script:
# Run these commands to set up GitHub secrets:
gh secret set AZURE_CREDENTIALS --body '{
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "...",
  "tenantId": "..."
}'

gh secret set AZURE_SUBSCRIPTION_ID --body "your-subscription-id"
gh secret set OPENAI_API_KEY --body "your-openai-api-key"
```

### Verify Secrets
```bash
# List all secrets to verify they're set
gh secret list
```

## 🧪 Step 5: Test the Pipeline

### Create Test Commit
```bash
# Create a simple test file
echo "# AI Pipeline Test" > test-pipeline.md
echo "This is a test to trigger the AI-integrated CI/CD pipeline." >> test-pipeline.md

# Commit and push
git add test-pipeline.md
git commit -m "test: trigger AI-integrated CI/CD pipeline

This commit tests:
- AI code review functionality
- Automated security scanning
- Deployment decision making
- Container building and testing"

git push origin main
```

### Monitor Pipeline Execution
1. Go to your GitHub repository
2. Click on the **"Actions"** tab
3. Watch the **"AI-Enhanced CI Pipeline"** workflow run
4. Check the logs for AI analysis results

### Expected Workflow Steps
1. ✅ **AI Code Analysis** - GPT-4 reviews your changes
2. ✅ **Security Scan** - CodeQL analyzes for vulnerabilities
3. ✅ **Quality Gate** - SonarCloud checks code quality
4. ✅ **Build and Test** - Docker images are built and tested
5. ✅ **AI Deployment Decision** - AI determines deployment strategy
6. ✅ **Deploy Staging** - Automatic deployment to staging environment

## 📊 Step 6: View Results

### GitHub Actions Output
The pipeline will generate several outputs:

**AI Code Review Results:**
```
🤖 AI CODE REVIEW RESULTS
================================================
## Overall Quality Score: 8.5/10
## Files Reviewed: 1
## Critical Issues Found:
### Security Issues: 0
### Performance Issues: 0
## Top Recommendations:
- Add proper error handling
- Include unit tests for new functionality
## Deployment Recommendation:
✅ APPROVED - Low risk changes
================================================
```

**Deployment Decision:**
```
🎯 Deployment Recommendation:
Strategy: BLUE_GREEN
Risk Level: LOW
Confidence: 85%
```

### Azure Portal
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your resource group (`cicd-ai-rg`)
3. Check deployed resources:
   - Container Registry
   - OpenAI Service
   - Application Insights
   - Container Apps (if deployed)

## 🎨 Step 7: Customize for Your Project

### Add Your Application Code
```bash
# Replace example apps with your code
rm -rf examples/python-app/*
cp -r /path/to/your/app/* examples/python-app/

# Update Dockerfile if needed
vim docker/Dockerfile.python
```

### Configure AI Prompts
```python
# Edit AI review prompts in .github/scripts/ai-code-review.py
CUSTOM_REVIEW_PROMPT = """
You are reviewing code for [YOUR PROJECT TYPE].
Focus on:
1. [Your specific requirements]
2. [Your coding standards]
3. [Your security concerns]
"""
```

### Adjust Deployment Strategies
```python
# Modify deployment logic in scripts/ai-agents/deployment-decision.py
def recommend_deployment_strategy(self, assessment):
    # Add your custom logic here
    if assessment['risk_level'] == 'low' and assessment['confidence'] > 0.8:
        return "blue_green"
    # ... your custom rules
```

## 🔍 Step 8: Monitor and Optimize

### Set Up Alerts
```bash
# Configure Azure alerts for your pipeline
az monitor metrics alert create \
  --name "High Error Rate" \
  --resource-group cicd-ai-rg \
  --condition "avg Percentage CPU > 80"
```

### Review Metrics
- Check GitHub Actions usage
- Monitor Azure costs
- Review AI recommendation accuracy
- Track deployment success rates

## 🎉 Success! What's Next?

Your AI-Integrated CI/CD Pipeline is now operational! Here's what you can do next:

### Immediate Actions
- [ ] Add your team members as collaborators
- [ ] Configure branch protection rules
- [ ] Set up notification channels (Slack, Teams)
- [ ] Add more comprehensive tests

### Advanced Features
- [ ] [Configure advanced AI features](../implementation/ai-integration.md)
- [ ] [Set up monitoring dashboards](../implementation/monitoring.md)
- [ ] [Add custom deployment strategies](../implementation/deployment-strategies.md)
- [ ] [Integrate with external tools](../implementation/integrations.md)

### Optimization
- [ ] Fine-tune AI prompts for your codebase
- [ ] Optimize Docker images for faster builds
- [ ] Configure auto-scaling policies
- [ ] Set up chaos engineering tests

## 🆘 Troubleshooting

### Common Issues

**Setup Script Fails:**
```bash
# Check prerequisites
az account show
gh auth status
docker version

# Check permissions
az role assignment list --assignee $(az account show --query user.name -o tsv)
```

**GitHub Actions Fail:**
```bash
# Verify secrets
gh secret list

# Check workflow syntax
gh workflow view
```

**AI Features Not Working:**
```bash
# Verify OpenAI API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Check Azure OpenAI deployment
az cognitiveservices account show --name genai-openai-service --resource-group cicd-ai-rg
```

### Getting Help
- 📖 [Full troubleshooting guide](../troubleshooting.md)
- 💬 [GitHub Discussions](https://github.com/miltonvve/ai-cicd-pipeline/discussions)
- 🐛 [Report Issues](https://github.com/miltonvve/ai-cicd-pipeline/issues)

---

**🚀 Congratulations! You now have a cutting-edge AI-integrated CI/CD pipeline powering your development workflow!**