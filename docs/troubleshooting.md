# 🔧 Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the AI-Integrated CI/CD Pipeline.

## 🚨 Common Issues

### GitHub Actions Failures

#### Issue: "Azure Authentication Failed"
```
Error: Azure login failed with error: AADSTS700016
```

**Solution:**
```bash
# Check if service principal exists and has correct permissions
az ad sp show --id $CLIENT_ID

# Verify AZURE_CREDENTIALS secret format
gh secret set AZURE_CREDENTIALS --body '{
  "clientId": "your-client-id",
  "clientSecret": "your-client-secret", 
  "subscriptionId": "your-subscription-id",
  "tenantId": "your-tenant-id"
}'

# Test authentication locally
az login --service-principal -u $CLIENT_ID -p $CLIENT_SECRET --tenant $TENANT_ID
```

#### Issue: "OpenAI API Rate Limit Exceeded"
```
Error: Rate limit exceeded for gpt-4 in organization
```

**Solution:**
```bash
# Check your OpenAI usage
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/usage

# Implement exponential backoff in ai-code-review.py
def ai_request_with_retry(self, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return self.client.chat.completions.create(...)
        except openai.RateLimitError:
            wait_time = 2 ** attempt
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")
```

#### Issue: "Docker Build Fails"
```
Error: failed to solve with frontend dockerfile.v0
```

**Solution:**
```bash
# Check Dockerfile syntax
docker build --no-cache -f docker/Dockerfile.python .

# Verify base image availability
docker pull python:3.11-slim

# Check for file permissions
ls -la docker/
chmod +r docker/Dockerfile.python

# Clean Docker cache
docker system prune -f
```

### Azure Resource Issues

#### Issue: "Container Registry Access Denied"
```
Error: unauthorized: authentication required
```

**Solution:**
```bash
# Check ACR admin status
az acr show --name $ACR_NAME --query "adminUserEnabled"

# Enable admin user if needed
az acr update --name $ACR_NAME --admin-enabled true

# Get credentials
az acr credential show --name $ACR_NAME

# Test login
az acr login --name $ACR_NAME
```

#### Issue: "Azure OpenAI Service Unavailable"
```
Error: The resource is not available in the specified region
```

**Solution:**
```bash
# Check available regions for OpenAI
az cognitiveservices account list-kinds --query "[?kind=='OpenAI'].locations"

# Check service status
az cognitiveservices account show \
  --name "genai-openai-service" \
  --resource-group "cicd-ai-rg" \
  --query "properties.provisioningState"

# Redeploy in supported region
az cognitiveservices account create \
  --name "genai-openai-service-2" \
  --resource-group "cicd-ai-rg" \
  --location "eastus2" \
  --kind "OpenAI" \
  --sku "S0"
```

#### Issue: "Container App Deployment Failed"
```
Error: The container group 'genai-staging' is in failed state
```

**Solution:**
```bash
# Check container app logs
az containerapp logs show \
  --name "genai-staging" \
  --resource-group "cicd-ai-rg"

# Check environment status
az containerapp env show \
  --name "genai-env" \
  --resource-group "cicd-ai-rg" \
  --query "properties.provisioningState"

# Restart container app
az containerapp revision restart \
  --name "genai-staging" \
  --resource-group "cicd-ai-rg"
```

### AI Integration Issues

#### Issue: "AI Code Review Returns Empty Results"
```
AI analysis failed: Invalid response format
```

**Solution:**
```python
# Add response validation in ai-code-review.py
def validate_ai_response(self, response):
    try:
        content = response.choices[0].message.content
        
        # Check if response contains JSON
        if '{' not in content:
            return self.get_fallback_response()
        
        # Validate JSON structure
        parsed = json.loads(content)
        required_fields = ['quality_score', 'recommendations']
        
        for field in required_fields:
            if field not in parsed:
                return self.get_fallback_response()
        
        return parsed
    except Exception as e:
        logger.error(f"Response validation failed: {e}")
        return self.get_fallback_response()

def get_fallback_response(self):
    return {
        "quality_score": 5,
        "security_issues": [],
        "recommendations": ["Manual review required - AI analysis failed"],
        "overall_assessment": "AI analysis unavailable"
    }
```

#### Issue: "Deployment Decision AI Gives Inconsistent Results"
```
AI deployment decision changed for identical code
```

**Solution:**
```python
# Add deterministic inputs in deployment-decision.py
def normalize_input_data(self, risk_factors):
    """Ensure consistent input format for AI"""
    normalized = {}
    for key, value in risk_factors.items():
        if isinstance(value, float):
            normalized[key] = round(value, 3)  # Limit precision
        else:
            normalized[key] = value
    return normalized

def get_stable_ai_assessment(self, risk_factors):
    """Get consistent AI assessment"""
    normalized_factors = self.normalize_input_data(risk_factors)
    
    # Use deterministic prompt
    prompt = self.build_deterministic_prompt(normalized_factors)
    
    # Use consistent model parameters
    response = self.client.chat.completions.create(
        model="gpt-4",
        messages=[...],
        temperature=0.1,  # Low temperature for consistency
        seed=42  # Fixed seed for reproducibility
    )
    
    return self.parse_response(response)
```

## 🔍 Diagnostic Tools

### GitHub Actions Debugging

#### Enable Debug Logging
```yaml
# Add to your workflow
- name: Enable Debug Logging
  run: echo "ACTIONS_STEP_DEBUG=true" >> $GITHUB_ENV

# Or set repository secret
gh secret set ACTIONS_STEP_DEBUG --body "true"
```

#### Check Workflow Status
```bash
# List workflow runs
gh run list --limit 10

# Get specific run details
gh run view $RUN_ID

# Download logs
gh run download $RUN_ID
```

### Azure Diagnostics

#### Resource Health Check
```bash
# Check all resources in resource group
az resource list --resource-group "cicd-ai-rg" --output table

# Check specific resource health
az resource show \
  --resource-group "cicd-ai-rg" \
  --name "genai-openai-service" \
  --resource-type "Microsoft.CognitiveServices/accounts" \
  --query "properties.provisioningState"

# Check activity logs
az monitor activity-log list \
  --resource-group "cicd-ai-rg" \
  --max-events 50 \
  --output table
```

#### Application Insights Queries
```kql
-- Check AI API response times
requests
| where name contains "ai-analysis"
| summarize avg(duration) by bin(timestamp, 5m)
| render timechart

-- Check error rates
exceptions
| where timestamp > ago(24h)
| summarize count() by type, bin(timestamp, 1h)
| render timechart

-- Check deployment success rates
customEvents
| where name == "deployment-decision"
| extend strategy = tostring(customDimensions.strategy)
| extend success = tostring(customDimensions.success)
| summarize success_rate = countif(success == "true") * 100.0 / count() by strategy
```

### AI Performance Monitoring

#### Create Monitoring Script
```python
#!/usr/bin/env python3
"""
AI Performance Monitor
"""
import json
import time
import openai
from datetime import datetime, timedelta

class AIPerformanceMonitor:
    def __init__(self):
        self.client = openai.OpenAI()
        self.metrics = []
    
    def test_ai_response_time(self):
        """Test AI API response time"""
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "status": "success",
                "response_time": response_time,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def check_model_availability(self):
        """Check if required models are available"""
        try:
            models = self.client.models.list()
            available_models = [model.id for model in models.data]
            
            required_models = ["gpt-4", "gpt-3.5-turbo"]
            model_status = {}
            
            for model in required_models:
                model_status[model] = model in available_models
            
            return model_status
        except Exception as e:
            return {"error": str(e)}
    
    def run_diagnostics(self):
        """Run comprehensive AI diagnostics"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "response_time_test": self.test_ai_response_time(),
            "model_availability": self.check_model_availability()
        }
        
        return results

if __name__ == "__main__":
    monitor = AIPerformanceMonitor()
    results = monitor.run_diagnostics()
    print(json.dumps(results, indent=2))
```

## 🛠️ Recovery Procedures

### Rollback Failed Deployment

#### GitHub Actions Rollback
```bash
# Revert to previous commit
git revert HEAD --no-edit
git push origin main

# Or rollback to specific commit
git reset --hard $PREVIOUS_COMMIT_SHA
git push --force-with-lease origin main
```

#### Azure Container App Rollback
```bash
# List revisions
az containerapp revision list \
  --name "genai-staging" \
  --resource-group "cicd-ai-rg" \
  --output table

# Activate previous revision
az containerapp ingress traffic set \
  --name "genai-staging" \
  --resource-group "cicd-ai-rg" \
  --revision-weight $PREVIOUS_REVISION=100
```

### Restore from Backup

#### Container Registry Backup
```bash
# List repository tags
az acr repository show-tags --name $ACR_NAME --repository myapp

# Restore from backup tag
docker pull $ACR_LOGIN_SERVER/myapp:backup-$DATE
docker tag $ACR_LOGIN_SERVER/myapp:backup-$DATE $ACR_LOGIN_SERVER/myapp:latest
docker push $ACR_LOGIN_SERVER/myapp:latest
```

### Emergency Procedures

#### Disable AI Features
```yaml
# Add to workflow to bypass AI analysis
- name: Skip AI Analysis
  if: ${{ vars.EMERGENCY_MODE == 'true' }}
  run: echo "AI analysis skipped due to emergency mode"

# Set emergency mode
gh variable set EMERGENCY_MODE --body "true"
```

#### Manual Deployment Override
```bash
# Manual deployment bypassing AI decision
az containerapp update \
  --name "genai-staging" \
  --resource-group "cicd-ai-rg" \
  --image "$ACR_LOGIN_SERVER/myapp:$TAG" \
  --revision-suffix "manual-$(date +%s)"
```

## 📞 Getting Help

### Internal Resources
1. **Check Documentation**: Review relevant docs in `/docs/` folder
2. **Search Issues**: Check existing GitHub issues for similar problems
3. **Review Logs**: Always check GitHub Actions and Azure logs first

### External Resources
1. **GitHub Actions Docs**: https://docs.github.com/en/actions
2. **Azure Documentation**: https://docs.microsoft.com/en-us/azure/
3. **OpenAI API Docs**: https://platform.openai.com/docs

### Community Support
1. **GitHub Discussions**: https://github.com/miltonvve/ai-cicd-pipeline/discussions
2. **Stack Overflow**: Tag questions with `azure`, `github-actions`, `openai`
3. **Reddit Communities**: r/DevOps, r/AZURE, r/MachineLearning

### Creating Support Tickets

#### GitHub Issue Template
```markdown
## Problem Description
Brief description of the issue

## Environment
- Repository: 
- Workflow: 
- Azure Region: 
- Last Working Version: 

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Logs and Screenshots
```

#### Azure Support
```bash
# Create Azure support ticket
az support tickets create \
  --ticket-name "AI-CICD Pipeline Issue" \
  --description "Description of the issue" \
  --problem-classification "/subscriptions/$SUBSCRIPTION_ID/providers/Microsoft.Support/services/service-guid/problemClassifications/problem-classification-guid" \
  --severity "moderate" \
  --contact-country "US" \
  --contact-email "your-email@company.com" \
  --contact-first-name "Your" \
  --contact-last-name "Name" \
  --contact-language "en-us" \
  --contact-method "email" \
  --contact-timezone "Pacific Standard Time"
```

## 🚨 Emergency Contacts

### Critical Issues (Production Down)
- **Primary**: On-call engineer (Slack: @oncall)
- **Secondary**: Team lead (Email: team-lead@company.com)
- **Escalation**: Engineering manager (Phone: xxx-xxx-xxxx)

### Non-Critical Issues
- **GitHub Issues**: Create detailed issue with logs
- **Team Chat**: #devops-support channel
- **Documentation**: Check troubleshooting docs first

---

Remember: Most issues can be resolved by checking logs, verifying configurations, and following the diagnostic procedures outlined above. When in doubt, start with the basics: authentication, network connectivity, and resource availability.