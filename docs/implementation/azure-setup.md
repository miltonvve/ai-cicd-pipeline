# ☁️ Azure Setup Guide

This guide provides detailed instructions for setting up and configuring Azure resources for your AI-Integrated CI/CD Pipeline.

## 🎯 Overview

The Azure infrastructure provides:
- **Container Registry** for secure image storage
- **OpenAI Service** for AI-powered analysis
- **Container Apps** for scalable hosting
- **Application Insights** for monitoring
- **Log Analytics** for centralized logging

## 📋 Prerequisites

### Required Tools
- ✅ Azure CLI installed (`az --version`)
- ✅ Azure subscription with Contributor access
- ✅ Bicep CLI installed (optional, for infrastructure as code)

### Required Permissions
- **Subscription Contributor** - Create and manage resources
- **Cognitive Services Contributor** - Deploy OpenAI services
- **Storage Account Contributor** - Manage container registries

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)
```bash
# Clone the repository and run setup script
git clone https://github.com/miltonvve/ai-cicd-pipeline.git
cd ai-cicd-pipeline

# Set environment variables
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export OPENAI_API_KEY="your-openai-api-key"

# Run automated setup
chmod +x setup-pipeline.sh
./setup-pipeline.sh
```

### Option 2: Manual Setup
Follow the detailed steps below for full control over the setup process.

## 🔧 Manual Azure Setup

### Step 1: Authentication and Subscription

```bash
# Login to Azure
az login

# List available subscriptions
az account list --output table

# Set the target subscription
az account set --subscription "your-subscription-id"

# Verify current subscription
az account show
```

### Step 2: Create Resource Group

```bash
# Create resource group
az group create \
  --name "cicd-ai-rg" \
  --location "eastus" \
  --tags \
    project="ai-cicd-pipeline" \
    environment="production" \
    managedBy="bicep"

# Verify resource group creation
az group show --name "cicd-ai-rg"
```

### Step 3: Deploy Azure Container Registry

```bash
# Create Azure Container Registry
az acr create \
  --resource-group "cicd-ai-rg" \
  --name "genairegistry$(date +%s | tail -c 6)" \
  --sku Premium \
  --admin-enabled true \
  --location "eastus"

# Get ACR details
ACR_NAME=$(az acr list --resource-group "cicd-ai-rg" --query "[0].name" --output tsv)
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group "cicd-ai-rg" --query "loginServer" --output tsv)

echo "Container Registry: $ACR_NAME"
echo "Login Server: $ACR_LOGIN_SERVER"

# Enable vulnerability scanning (Premium feature)
az acr config security-policy update \
  --registry $ACR_NAME \
  --security-scan-enabled true
```

### Step 4: Create Azure OpenAI Service

```bash
# Create Azure OpenAI service
az cognitiveservices account create \
  --name "genai-openai-service" \
  --resource-group "cicd-ai-rg" \
  --location "eastus" \
  --kind "OpenAI" \
  --sku "S0" \
  --custom-domain "genai-openai-service"

# Get OpenAI endpoint and key
OPENAI_ENDPOINT=$(az cognitiveservices account show \
  --name "genai-openai-service" \
  --resource-group "cicd-ai-rg" \
  --query "properties.endpoint" --output tsv)

OPENAI_KEY=$(az cognitiveservices account keys list \
  --name "genai-openai-service" \
  --resource-group "cicd-ai-rg" \
  --query "key1" --output tsv)

echo "OpenAI Endpoint: $OPENAI_ENDPOINT"
echo "OpenAI Key: [REDACTED]"
```

### Step 5: Deploy AI Models

```bash
# Deploy GPT-4 model for code review
az cognitiveservices account deployment create \
  --name "genai-openai-service" \
  --resource-group "cicd-ai-rg" \
  --deployment-name "gpt-4" \
  --model-name "gpt-4" \
  --model-version "0613" \
  --model-format "OpenAI" \
  --scale-type "Standard" \
  --capacity 10

# Deploy GPT-3.5-turbo for faster operations
az cognitiveservices account deployment create \
  --name "genai-openai-service" \
  --resource-group "cicd-ai-rg" \
  --deployment-name "gpt-35-turbo" \
  --model-name "gpt-35-turbo" \
  --model-version "0613" \
  --model-format "OpenAI" \
  --scale-type "Standard" \
  --capacity 20

# List deployed models
az cognitiveservices account deployment list \
  --name "genai-openai-service" \
  --resource-group "cicd-ai-rg" \
  --output table
```

### Step 6: Create Log Analytics Workspace

```bash
# Create Log Analytics workspace
az monitor log-analytics workspace create \
  --resource-group "cicd-ai-rg" \
  --workspace-name "genai-logs" \
  --location "eastus" \
  --sku "PerGB2018"

# Get workspace ID
WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group "cicd-ai-rg" \
  --workspace-name "genai-logs" \
  --query "customerId" --output tsv)

echo "Log Analytics Workspace ID: $WORKSPACE_ID"
```

### Step 7: Create Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app "genai-insights" \
  --location "eastus" \
  --resource-group "cicd-ai-rg" \
  --workspace "/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/cicd-ai-rg/providers/Microsoft.OperationalInsights/workspaces/genai-logs"

# Get Application Insights connection string
APPINSIGHTS_CONNECTION_STRING=$(az monitor app-insights component show \
  --app "genai-insights" \
  --resource-group "cicd-ai-rg" \
  --query "connectionString" --output tsv)

echo "Application Insights Connection String: $APPINSIGHTS_CONNECTION_STRING"
```

### Step 8: Create Container App Environment

```bash
# Create Container App Environment
az containerapp env create \
  --name "genai-env" \
  --resource-group "cicd-ai-rg" \
  --location "eastus" \
  --logs-workspace-id $WORKSPACE_ID \
  --logs-workspace-key $(az monitor log-analytics workspace get-shared-keys \
    --resource-group "cicd-ai-rg" \
    --workspace-name "genai-logs" \
    --query "primarySharedKey" --output tsv)

# Create Container App for staging
az containerapp create \
  --name "genai-staging" \
  --resource-group "cicd-ai-rg" \
  --environment "genai-env" \
  --image "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest" \
  --target-port 80 \
  --ingress external \
  --cpu 0.5 \
  --memory 1Gi \
  --min-replicas 1 \
  --max-replicas 10

# Get staging app URL
STAGING_URL=$(az containerapp show \
  --name "genai-staging" \
  --resource-group "cicd-ai-rg" \
  --query "properties.configuration.ingress.fqdn" --output tsv)

echo "Staging URL: https://$STAGING_URL"
```

## 🏗️ Infrastructure as Code (Bicep)

For production deployments, use the provided Bicep templates:

### Deploy Using Bicep

```bash
# Deploy the main Bicep template
az deployment group create \
  --resource-group "cicd-ai-rg" \
  --template-file "azure/bicep/main.bicep" \
  --parameters \
    environmentName="prod" \
    projectName="genai-cicd" \
    location="eastus"

# Monitor deployment progress
az deployment group show \
  --resource-group "cicd-ai-rg" \
  --name "main" \
  --query "properties.provisioningState"
```

### Custom Bicep Parameters

Create a parameters file `azure/bicep/parameters.json`:

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "environmentName": {
      "value": "prod"
    },
    "projectName": {
      "value": "genai-cicd"
    },
    "location": {
      "value": "eastus"
    },
    "containerRegistryName": {
      "value": "genairegistry"
    },
    "openAIServiceName": {
      "value": "genai-openai-service"
    }
  }
}
```

Deploy with parameters:
```bash
az deployment group create \
  --resource-group "cicd-ai-rg" \
  --template-file "azure/bicep/main.bicep" \
  --parameters "@azure/bicep/parameters.json"
```

## 🔐 Security Configuration

### Network Security

```bash
# Create virtual network for secure communication
az network vnet create \
  --resource-group "cicd-ai-rg" \
  --name "genai-vnet" \
  --address-prefix "10.0.0.0/16" \
  --subnet-name "container-subnet" \
  --subnet-prefix "10.0.1.0/24"

# Create private endpoint for Container Registry
az network private-endpoint create \
  --resource-group "cicd-ai-rg" \
  --name "acr-private-endpoint" \
  --vnet-name "genai-vnet" \
  --subnet "container-subnet" \
  --private-connection-resource-id "/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/cicd-ai-rg/providers/Microsoft.ContainerRegistry/registries/$ACR_NAME" \
  --group-id "registry" \
  --connection-name "acr-connection"
```

### Access Control (RBAC)

```bash
# Create managed identity for Container Apps
az identity create \
  --resource-group "cicd-ai-rg" \
  --name "genai-managed-identity"

MANAGED_IDENTITY_ID=$(az identity show \
  --resource-group "cicd-ai-rg" \
  --name "genai-managed-identity" \
  --query "id" --output tsv)

# Grant ACR pull permissions to managed identity
az role assignment create \
  --assignee $MANAGED_IDENTITY_ID \
  --role "AcrPull" \
  --scope "/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/cicd-ai-rg/providers/Microsoft.ContainerRegistry/registries/$ACR_NAME"

# Grant OpenAI access to managed identity
az role assignment create \
  --assignee $MANAGED_IDENTITY_ID \
  --role "Cognitive Services User" \
  --scope "/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/cicd-ai-rg/providers/Microsoft.CognitiveServices/accounts/genai-openai-service"
```

### Key Vault Integration

```bash
# Create Key Vault for secret management
az keyvault create \
  --resource-group "cicd-ai-rg" \
  --name "genai-keyvault$(date +%s | tail -c 6)" \
  --location "eastus" \
  --sku "standard"

KEY_VAULT_NAME=$(az keyvault list --resource-group "cicd-ai-rg" --query "[0].name" --output tsv)

# Store secrets in Key Vault
az keyvault secret set \
  --vault-name $KEY_VAULT_NAME \
  --name "openai-api-key" \
  --value $OPENAI_KEY

az keyvault secret set \
  --vault-name $KEY_VAULT_NAME \
  --name "app-insights-connection-string" \
  --value $APPINSIGHTS_CONNECTION_STRING

# Grant Key Vault access to managed identity
az keyvault set-policy \
  --name $KEY_VAULT_NAME \
  --object-id $(az identity show --resource-group "cicd-ai-rg" --name "genai-managed-identity" --query "principalId" --output tsv) \
  --secret-permissions get list
```

## 📊 Monitoring Setup

### Configure Alerts

```bash
# Create action group for notifications
az monitor action-group create \
  --resource-group "cicd-ai-rg" \
  --name "genai-alerts" \
  --short-name "genai" \
  --email-receiver name="admin" email-address="admin@yourcompany.com"

# Create metric alert for high error rate
az monitor metrics alert create \
  --name "High Error Rate" \
  --resource-group "cicd-ai-rg" \
  --description "Alert when error rate exceeds 5%" \
  --condition "avg Exception_rate > 5" \
  --window-size "5m" \
  --evaluation-frequency "1m" \
  --action "/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/cicd-ai-rg/providers/microsoft.insights/actiongroups/genai-alerts" \
  --resource "/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/cicd-ai-rg/providers/Microsoft.Insights/components/genai-insights"

# Create budget alert for cost management
az consumption budget create \
  --resource-group "cicd-ai-rg" \
  --budget-name "monthly-budget" \
  --amount 500 \
  --time-grain "Monthly" \
  --time-period start-date="2024-01-01" \
  --notification threshold=80 contact-emails="admin@yourcompany.com"
```

### Custom Dashboard

```bash
# Create custom dashboard
az portal dashboard create \
  --resource-group "cicd-ai-rg" \
  --name "genai-dashboard" \
  --location "eastus" \
  --input-path "azure/dashboards/main-dashboard.json"
```

## 🔧 Environment-Specific Configuration

### Development Environment

```bash
# Deploy minimal resources for development
az deployment group create \
  --resource-group "cicd-ai-dev-rg" \
  --template-file "azure/bicep/main.bicep" \
  --parameters \
    environmentName="dev" \
    projectName="genai-cicd" \
    containerRegistryTier="Basic" \
    openAIServiceTier="F0"
```

### Production Environment

```bash
# Deploy production-ready resources
az deployment group create \
  --resource-group "cicd-ai-prod-rg" \
  --template-file "azure/bicep/main.bicep" \
  --parameters \
    environmentName="prod" \
    projectName="genai-cicd" \
    containerRegistryTier="Premium" \
    openAIServiceTier="S0" \
    enablePrivateEndpoints=true \
    enableBackup=true
```

## 💰 Cost Optimization

### Implement Cost Controls

```bash
# Set up auto-shutdown for development resources
az resource tag \
  --resource-group "cicd-ai-dev-rg" \
  --name "genai-dev-*" \
  --resource-type "Microsoft.ContainerInstance/containerGroups" \
  --tags "AutoShutdown=true" "ShutdownTime=18:00"

# Configure scaling rules for Container Apps
az containerapp revision set-mode \
  --name "genai-staging" \
  --resource-group "cicd-ai-rg" \
  --mode "Single"

# Set up budget alerts
az consumption budget create \
  --resource-group "cicd-ai-rg" \
  --budget-name "weekly-budget" \
  --amount 100 \
  --time-grain "Monthly" \
  --time-period start-date="$(date -d 'next month' +%Y-%m-01)" \
  --notification threshold=50 threshold=80 threshold=100 \
    contact-emails="admin@yourcompany.com"
```

## 🚀 Deployment Verification

### Verify All Resources

```bash
# Check resource deployment status
echo "=== Resource Group ==="
az group show --name "cicd-ai-rg" --query "properties.provisioningState"

echo "=== Container Registry ==="
az acr show --name $ACR_NAME --resource-group "cicd-ai-rg" --query "provisioningState"

echo "=== OpenAI Service ==="
az cognitiveservices account show --name "genai-openai-service" --resource-group "cicd-ai-rg" --query "properties.provisioningState"

echo "=== Application Insights ==="
az monitor app-insights component show --app "genai-insights" --resource-group "cicd-ai-rg" --query "provisioningState"

echo "=== Container App Environment ==="
az containerapp env show --name "genai-env" --resource-group "cicd-ai-rg" --query "properties.provisioningState"
```

### Test Connectivity

```bash
# Test OpenAI service
curl -H "api-key: $OPENAI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}],"max_tokens":10}' \
  "$OPENAI_ENDPOINT/openai/deployments/gpt-35-turbo/chat/completions?api-version=2023-12-01-preview"

# Test Container Registry
az acr login --name $ACR_NAME
docker pull hello-world
docker tag hello-world $ACR_LOGIN_SERVER/hello-world:test
docker push $ACR_LOGIN_SERVER/hello-world:test

# Test Application Insights
az monitor app-insights events show \
  --app "genai-insights" \
  --resource-group "cicd-ai-rg" \
  --event "requests" \
  --start-time "2024-01-01T00:00:00Z"
```

## 📋 Resource Summary

After successful deployment, you'll have:

| Resource | Purpose | Estimated Monthly Cost |
|----------|---------|----------------------|
| Container Registry (Premium) | Image storage and scanning | $30-60 |
| OpenAI Service (S0) | AI analysis and decisions | $100-500 |
| Container Apps | Application hosting | $20-100 |
| Application Insights | Monitoring and analytics | $10-50 |
| Log Analytics | Centralized logging | $5-25 |
| Key Vault | Secret management | $1-5 |

**Total Estimated Cost**: $166-740/month (varies by usage)

## 🔄 Maintenance Tasks

### Weekly Tasks
- Review cost reports and optimize resources
- Check security alerts and recommendations
- Update container images and dependencies
- Review AI model performance metrics

### Monthly Tasks
- Rotate secrets and access keys
- Review and optimize scaling policies
- Update Azure services to latest versions
- Conduct security and compliance reviews

### Quarterly Tasks
- Review architecture for optimization opportunities
- Update disaster recovery procedures
- Conduct cost optimization analysis
- Review and update RBAC permissions

---

Your Azure infrastructure is now ready to power your AI-integrated CI/CD pipeline! 🚀