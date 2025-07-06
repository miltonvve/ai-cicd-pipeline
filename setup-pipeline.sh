#!/bin/bash

# AI-Integrated CI/CD Pipeline Setup Script
# For GenAI Guru Projects

set -e

echo "🚀 Setting up AI-Integrated CI/CD Pipeline..."

# Configuration
RESOURCE_GROUP="cicd-ai-rg"
LOCATION="eastus"
ACR_NAME="genairegistry"
SUBSCRIPTION_ID=${AZURE_SUBSCRIPTION_ID}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI not installed. Please install it first."
        exit 1
    fi
    
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI not installed. Please install it first."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker not installed. Please install it first."
        exit 1
    fi
    
    print_success "All prerequisites are installed!"
}

# Setup Azure resources
setup_azure_resources() {
    print_status "Setting up Azure resources..."
    
    # Create resource group
    print_status "Creating resource group: $RESOURCE_GROUP"
    az group create --name $RESOURCE_GROUP --location $LOCATION --output none
    
    # Create Azure Container Registry
    print_status "Creating Azure Container Registry: $ACR_NAME"
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $ACR_NAME \
        --sku Premium \
        --admin-enabled true \
        --output none
    
    # Create Azure OpenAI resource
    print_status "Creating Azure OpenAI service..."
    az cognitiveservices account create \
        --name "genai-openai-service" \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --kind OpenAI \
        --sku S0 \
        --output none || print_warning "OpenAI service creation may require manual approval"
    
    # Create Application Insights
    print_status "Creating Application Insights..."
    az monitor app-insights component create \
        --app "genai-insights" \
        --location $LOCATION \
        --resource-group $RESOURCE_GROUP \
        --output none
    
    print_success "Azure resources created successfully!"
}

# Setup GitHub Actions workflows
setup_github_workflows() {
    print_status "Setting up GitHub Actions workflows..."
    
    # Create .github directory structure
    mkdir -p .github/workflows
    mkdir -p .github/actions/ai-code-review
    
    # Create main CI workflow
    cat > .github/workflows/ci-main.yml << 'EOF'
name: AI-Enhanced CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: genairegistry.azurecr.io
  AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

jobs:
  ai-code-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install openai azure-identity
      
      - name: AI Code Review
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python .github/scripts/ai-code-review.py

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: python, javascript
      
      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3

  build-and-test:
    runs-on: ubuntu-latest
    needs: [ai-code-analysis, security-scan]
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker images
        run: |
          docker build -f docker/Dockerfile.python -t test-python .
          docker build -f docker/Dockerfile.nodejs -t test-nodejs .
      
      - name: Run tests
        run: |
          docker run --rm test-python pytest
          docker run --rm test-nodejs npm test

  deploy-staging:
    runs-on: ubuntu-latest
    needs: build-and-test
    if: github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v4
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Deploy to staging
        run: |
          echo "Deploying to staging environment..."
EOF

    # Create AI code review script
    mkdir -p .github/scripts
    cat > .github/scripts/ai-code-review.py << 'EOF'
#!/usr/bin/env python3
"""
AI-powered code review script for GitHub Actions
"""
import os
import subprocess
import openai
import json

def get_git_diff():
    """Get the git diff for the current changes"""
    try:
        diff = subprocess.check_output(['git', 'diff', 'HEAD~1'], text=True)
        return diff
    except subprocess.CalledProcessError:
        return ""

def analyze_code_with_ai(diff):
    """Analyze code changes using OpenAI"""
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    prompt = f"""
    You are a senior software engineer performing a code review. 
    Analyze this git diff and provide feedback on:
    
    1. Code quality and best practices
    2. Potential bugs or issues
    3. Security concerns
    4. Performance improvements
    5. Maintainability
    
    Provide specific, actionable feedback:
    
    {diff}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert code reviewer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"AI analysis failed: {str(e)}"

def main():
    print("🤖 Starting AI code review...")
    
    diff = get_git_diff()
    if not diff:
        print("No changes detected.")
        return
    
    analysis = analyze_code_with_ai(diff)
    
    print("\n" + "="*50)
    print("AI CODE REVIEW RESULTS")
    print("="*50)
    print(analysis)
    print("="*50)
    
    # Save results for later use
    with open('ai-review-results.json', 'w') as f:
        json.dump({
            'analysis': analysis,
            'diff_size': len(diff),
            'timestamp': subprocess.check_output(['date'], text=True).strip()
        }, f, indent=2)

if __name__ == "__main__":
    main()
EOF

    chmod +x .github/scripts/ai-code-review.py
    
    print_success "GitHub workflows created!"
}

# Setup Docker configurations
setup_docker() {
    print_status "Setting up Docker configurations..."
    
    mkdir -p docker
    
    # Python Dockerfile
    cat > docker/Dockerfile.python << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "pytest"]
EOF

    # Node.js Dockerfile
    cat > docker/Dockerfile.nodejs << 'EOF'
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

CMD ["npm", "test"]
EOF

    # Docker Compose for local development
    cat > docker/docker-compose.yml << 'EOF'
version: '3.8'

services:
  python-app:
    build:
      context: ..
      dockerfile: docker/Dockerfile.python
    volumes:
      - ..:/app
    environment:
      - PYTHONPATH=/app
  
  nodejs-app:
    build:
      context: ..
      dockerfile: docker/Dockerfile.nodejs
    volumes:
      - ..:/app
    ports:
      - "3000:3000"
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: testdb
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    ports:
      - "5432:5432"
EOF

    print_success "Docker configurations created!"
}

# Setup monitoring and observability
setup_monitoring() {
    print_status "Setting up monitoring and observability..."
    
    mkdir -p monitoring
    
    # Create Application Insights configuration
    cat > monitoring/appinsights.json << 'EOF'
{
  "instrumentationKey": "TO_BE_REPLACED",
  "sampling": {
    "isEnabled": true,
    "maxTelemetryItemsPerSecond": 5
  },
  "enableAutoCollectRequests": true,
  "enableAutoCollectPerformance": true,
  "enableAutoCollectExceptions": true,
  "enableAutoCollectDependencies": true,
  "enableUsageTracking": true
}
EOF

    # Create Grafana dashboard configuration
    cat > monitoring/grafana-dashboard.json << 'EOF'
{
  "dashboard": {
    "title": "GenAI Guru CI/CD Pipeline",
    "panels": [
      {
        "title": "Build Success Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(github_actions_builds_total{result=\"success\"}[5m])) / sum(rate(github_actions_builds_total[5m]))"
          }
        ]
      },
      {
        "title": "Deployment Frequency",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(deployments_total[1h])"
          }
        ]
      },
      {
        "title": "AI Analysis Results",
        "type": "table",
        "targets": [
          {
            "expr": "ai_code_review_score"
          }
        ]
      }
    ]
  }
}
EOF

    print_success "Monitoring configurations created!"
}

# Main execution
main() {
    print_status "Starting AI-Integrated CI/CD Pipeline Setup"
    
    check_prerequisites
    setup_azure_resources
    setup_github_workflows
    setup_docker
    setup_monitoring
    
    print_success "🎉 AI-Integrated CI/CD Pipeline setup completed!"
    
    echo ""
    echo "Next steps:"
    echo "1. Set up GitHub secrets:"
    echo "   - AZURE_CREDENTIALS"
    echo "   - AZURE_SUBSCRIPTION_ID" 
    echo "   - OPENAI_API_KEY"
    echo ""
    echo "2. Configure Azure OpenAI service endpoint"
    echo "3. Set up SonarCloud integration"
    echo "4. Configure notification channels"
    echo ""
    echo "For detailed instructions, see: AI-Integrated-CICD-Plan.md"
}

# Run main function
main "$@"