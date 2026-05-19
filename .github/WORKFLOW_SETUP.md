# GitHub Actions CI/CD Setup Guide

## Overview
This project uses GitHub Actions to automatically build Docker images and deploy to AWS ECR when code is pushed to the main branch.

## Workflow: `.github/workflows/cicd.yaml`

### Trigger
- **Event**: Push to `main` branch
- **Runner**: Self-hosted (EC2 instance)

### Pipeline Steps

1. **Pull latest code**
   - Clones repository to `/home/ubuntu/source-code-analyzer`
   - Checks out the latest main branch

2. **Build Docker image**
   - Runs `docker build -t source-code-analyzer:latest .`
   - Reads `Dockerfile` and installs all dependencies from `requirements.txt`
   - Creates container image ready for deployment

3. **Push to ECR**
   - Authenticates with AWS ECR using provided credentials
   - Tags image with ECR repository URL
   - Pushes image to Amazon Elastic Container Registry

4. **Deploy container**
   - Stops and removes any existing container
   - Pulls latest image from ECR
   - Runs container with:
     - Name: `source-code-analyzer`
     - Port mapping: `5001:5001`
     - Auto-restart policy: `always`
     - Environment variable: `GOOGLE_API_KEY`

## Required Configuration

### GitHub Repository Secrets
Set these in repository Settings → Secrets and variables → Actions:

```
AWS_ACCESS_KEY_ID          - Your AWS access key ID
AWS_SECRET_ACCESS_KEY      - Your AWS secret access key
AWS_DEFAULT_REGION         - AWS region (e.g., us-east-1)
ECR_REPO                   - ECR repository name
GOOGLE_API_KEY             - Google Generative AI API key
```

### Self-Hosted Runner Requirements
The EC2 instance must have:
- GitHub Actions runner installed and configured
- Docker installed and running
- AWS CLI installed
- Git installed
- Network access to:
  - GitHub (github.com)
  - AWS ECR service
  - Internet (for docker pulls)

### EC2 Instance Setup (One-time)
```bash
# Install Docker
sudo apt-get update
sudo apt-get install -y docker.io

# Install AWS CLI
sudo apt-get install -y awscli

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# Download and start GitHub Actions runner
mkdir ~/actions-runner && cd ~/actions-runner
curl -o actions-runner-linux-x64-2.X.X.tar.gz -L https://github.com/actions/runner/releases/download/vX.X.X/actions-runner-linux-x64-2.X.X.tar.gz
tar xzf ./actions-runner-linux-x64-2.X.X.tar.gz
./config.sh --url https://github.com/Siddanth-S/End-to-end-Source-Code-Analysis-Generative-AI-main --token XXXX
./run.sh
```

## Dependencies Fixed (May 2024)

Previous version conflicts have been resolved in `requirements.txt`:

| Package | Issue | Fixed Version |
|---------|-------|---------------|
| langchain-community | 0.1.24 doesn't exist | 0.0.38 |
| langchain-core | 0.1.42 too old | 0.1.53 |
| google-generativeai | 0.5.0 incompatible | 0.8.6 |

All packages now resolve without conflicts.

## Testing the Pipeline

### Local Test (Before Push)
```bash
# Test Docker build locally
docker build -t source-code-analyzer:latest .

# Run container
docker run -p 5001:5001 -e GOOGLE_API_KEY=your_key source-code-analyzer:latest

# Test at http://localhost:5001
```

### Trigger CI/CD Pipeline
```bash
# Make a change and push to main
git add .
git commit -m "Test CI/CD pipeline"
git push origin main
```

### Monitor Workflow
- Go to: https://github.com/Siddanth-S/End-to-end-Source-Code-Analysis-Generative-AI-main/actions
- Click the workflow run to see real-time logs
- Check each step for success/failure

## Troubleshooting

### Workflow Not Triggering
- Verify `.github/workflows/cicd.yaml` exists and is valid YAML
- Check that you pushed to `main` branch (not other branches)
- Ensure self-hosted runner is online and connected

### Docker Build Fails
- Check `requirements.txt` for valid package versions
- Verify `Dockerfile` is syntactically correct
- Check system dependencies are installed (git, build-essential)

### ECR Push Fails
- Verify AWS credentials are correct in GitHub Secrets
- Ensure ECR repository exists in AWS account
- Check AWS region matches `AWS_DEFAULT_REGION`

### Container Deployment Fails
- Verify port 5001 is not in use on EC2
- Check `GOOGLE_API_KEY` is set correctly
- Ensure Docker has network access to ECR

## Current Status
✅ Workflow YAML validated
✅ All dependencies compatible
✅ Docker build tested
✅ Ready for deployment

**Next Step**: Push code to main branch to trigger the pipeline.
