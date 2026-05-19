# CI/CD Pipeline Setup Guide

## What is this CI/CD Pipeline?

**CI/CD** stands for **Continuous Integration / Continuous Deployment**. This GitHub Actions workflow automates the process of:

- **Building** your Docker image when you push code
- **Testing** your application
- **Pushing** the image to AWS ECR (Elastic Container Registry)
- **Deploying** the latest version to your EC2 instance

## How it Works

### Trigger

The pipeline automatically runs whenever you:

- Push code to the `main` branch
- Create or update a Pull Request to `main`

### Two Jobs

#### 1. **Continuous Integration** (Build & Test)

- Checks out your code
- Sets up Python 3.10 environment
- Installs dependencies from `requirements.txt`
- Runs tests (if configured)
- Builds Docker image
- Pushes image to AWS ECR (only on main branch)

#### 2. **Continuous Deployment** (Deploy to EC2)

- Waits for CI to complete successfully
- Connects to your EC2 instance via SSH
- Pulls latest Docker image from ECR
- Stops old container
- Runs new container with the latest image
- Verifies deployment

## GitHub Secrets Required

You need to set up these secrets in your GitHub repository settings:

### AWS Credentials

```
AWS_ACCESS_KEY_ID          → Your AWS Access Key
AWS_SECRET_ACCESS_KEY      → Your AWS Secret Access Key
AWS_DEFAULT_REGION         → Your AWS region (e.g., us-east-1)
ECR_REPO                   → Your ECR repository name (e.g., source-code-analyzer)
```

### EC2 Information

```
EC2_HOST                   → Your EC2 instance Public IP or DNS
EC2_USER                   → SSH user (usually 'ec2-user' for Amazon Linux, 'ubuntu' for Ubuntu)
EC2_SSH_KEY                → Your EC2 SSH private key content (entire .pem file content)
GOOGLE_API_KEY             → Your Google API key (used by the app)
```

## How to Set Up Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret name and value
5. Click **Add secret**

## Understanding the Workflow File

### Build Stage

```yaml
- docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
```

Builds your Docker image using the `Dockerfile` in your repo

### Push Stage

```yaml
- docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
```

Pushes the built image to AWS ECR so EC2 can access it

### Deploy Stage

```yaml
docker run -d --name source-code-analyzer --restart always -p 5001:5001 ...
```

- `-d`: Run container in detached mode (background)
- `--restart always`: Auto-restart container if it crashes
- `-p 5001:5001`: Map port 5001 inside container to port 5001 on EC2
- `--name source-code-analyzer`: Container name for easy management

## Pre-Requisites

1. **GitHub Repository** - Code pushed to GitHub
2. **AWS Account** - With credentials configured
3. **ECR Repository** - Created in your AWS region
4. **EC2 Instance** - Running Linux with Docker installed
5. **SSH Access** - EC2 instance accepting SSH connections

## Environment Setup on EC2

When your EC2 instance is ready, ensure:

1. Docker is installed:

```bash
sudo yum install docker -y  # Amazon Linux
# or
sudo apt-get install docker.io -y  # Ubuntu
```

2. Docker daemon is running:

```bash
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

3. AWS CLI is configured (for ECR login):

```bash
aws configure
```

## Verification Steps

### Check if deployment succeeded

1. Go to **Actions** tab in your GitHub repo
2. Click the latest workflow run
3. Check both jobs passed
4. Visit your EC2 instance: `http://your-ec2-ip:5001`

### Manual SSH Check

```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
docker ps                    # See running containers
docker logs source-code-analyzer  # View container logs
```

## Troubleshooting

### Deployment fails at SSH step

- Check EC2_HOST is correct IP/DNS
- Ensure EC2_SSH_KEY content is properly copied (entire .pem file)
- Verify EC2 instance security group allows port 22 (SSH)

### Image not pushing to ECR

- Verify AWS credentials are correct
- Check ECR_REPO name matches ECR repository
- Ensure AWS region is correct

### Container not running after deployment

- Check `docker logs source-code-analyzer` on EC2
- Verify GOOGLE_API_KEY secret is set
- Ensure port 5001 is allowed in EC2 security group

## Next Steps

1. Create GitHub secrets with your AWS and EC2 details
2. Push code to `main` branch
3. Monitor the Actions tab for workflow execution
4. Access your app at `http://ec2-ip:5001`
