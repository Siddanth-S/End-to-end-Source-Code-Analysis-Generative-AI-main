# AWS CI/CD Deployment Checklist

## Phase 1: AWS Setup

### Create ECR Repository

- [ ] Go to AWS Console → ECR
- [ ] Click "Create repository"
- [ ] Repository name: `source-code-analyzer`
- [ ] Save the repository URI 637423531772.dkr.ecr.ap-south-1.amazonaws.com/source-code-analyser (e.g., `123456789.dkr.ecr.us-east-1.amazonaws.com/source-code-analyzer`)

### Create IAM User for CI/CD

- [ ] Go to IAM → Users → Create User
- [ ] Username: `github-ci-cd`
- [ ] Add permissions:
  - [ ] `AmazonEC2ContainerRegistryPowerUser` (for ECR access)
  - [ ] `AmazonEC2FullAccess` (if deploying via API)
- [ ] Create access key (save Access Key ID & Secret Access Key)

### Launch EC2 Instance

- [ ] Go to EC2 Dashboard → Launch Instance
- [ ] Choose: Ubuntu 20.04 LTS (or Amazon Linux 2)
- [ ] Instance type: t2.micro (or t2.small)
- [ ] Configure security group:
  - [ ] Allow SSH (port 22) from your IP
  - [ ] Allow HTTP (port 80) - optional
  - [ ] Allow HTTPS (port 443) - optional
  - [ ] Allow port 5001 (your Flask app)
- [ ] Create/select SSH key pair
- [ ] Launch instance
- [ ] Note the Public IP address

### Setup Docker on EC2

- [ ] SSH into EC2:
  ```bash
  ssh -i your-key.pem ec2-user@your-instance-ip
  # or for Ubuntu:
  ssh -i your-key.pem ubuntu@your-instance-ip
  ```
- [ ] Install Docker:

  ```bash
  # Amazon Linux
  sudo yum update -y
  sudo yum install docker -y
  sudo systemctl start docker
  sudo systemctl enable docker
  sudo usermod -aG docker $USER

  # Ubuntu
  sudo apt-get update
  sudo apt-get install docker.io -y
  sudo systemctl start docker
  sudo systemctl enable docker
  sudo usermod -aG docker $USER
  ```

- [ ] Install AWS CLI:
  ```bash
  sudo yum install awscli -y  # or apt-get for Ubuntu
  ```
- [ ] Exit and reconnect SSH session for docker group to take effect

## Phase 2: GitHub Setup

### Add GitHub Secrets

- [ ] Go to GitHub repo → Settings → Secrets and variables → Actions
- [ ] Add these secrets:

| Secret Name             | Value                                              |
| ----------------------- | -------------------------------------------------- |
| `AWS_ACCESS_KEY_ID`     | From IAM user created above                        |
| `AWS_SECRET_ACCESS_KEY` | From IAM user created above                        |
| `AWS_DEFAULT_REGION`    | Your AWS region (e.g., `us-east-1`)                |
| `ECR_REPO`              | ECR repository name (e.g., `source-code-analyzer`) |
| `EC2_HOST`              | EC2 instance Public IP                             |
| `EC2_USER`              | SSH user (`ec2-user` or `ubuntu`)                  |
| `EC2_SSH_KEY`           | Contents of your EC2 .pem file                     |
| `GOOGLE_API_KEY`        | Your Google Generative AI API key                  |

### Verify Workflow File

- [ ] Check `.github/workflows/cicd.yaml` exists in main branch
- [ ] Verify all secrets are set by going to Actions tab

## Phase 3: First Deployment

### Test the Pipeline

- [ ] Make a small change to your code
- [ ] Commit and push to main branch:
  ```bash
  git add .
  git commit -m "Trigger CI/CD pipeline"
  git push origin main
  ```
- [ ] Go to GitHub Actions tab
- [ ] Watch the workflow execute

### Monitor Execution

- [ ] Continuous-Integration job:
  - [ ] Should build Docker image
  - [ ] Should push to ECR
- [ ] Continuous-Deployment job:
  - [ ] Should pull image from ECR
  - [ ] Should deploy to EC2

### Verify Application

- [ ] SSH into EC2: `docker ps` (should show running container)
- [ ] Check logs: `docker logs source-code-analyzer`
- [ ] Test in browser: `http://your-ec2-ip:5001`

## Phase 4: Ongoing Maintenance

### Regular Checks

- [ ] Monitor GitHub Actions for failed deployments
- [ ] Check EC2 instance health
- [ ] Verify logs on EC2: `docker logs source-code-analyzer`
- [ ] Monitor AWS costs (EC2, ECR storage)

### Troubleshooting Workflow

If deployment fails:

1. [ ] Check GitHub Actions logs for error messages
2. [ ] Verify secrets are correct
3. [ ] SSH into EC2 and check Docker:
   ```bash
   docker ps -a          # See all containers
   docker logs <container-id>  # View error logs
   docker pull $registry/$repo:latest  # Manually pull to test
   ```
4. [ ] Check EC2 security groups allow required ports
5. [ ] Verify IAM user has correct permissions

### Auto-Restart on Crashes

The workflow includes `--restart always` flag, so:

- [ ] Container auto-restarts if it crashes
- [ ] Check health with: `docker inspect source-code-analyzer`

## Useful Commands

### On EC2

```bash
# View running containers
docker ps

# View container logs
docker logs source-code-analyzer -f  # -f for follow/tail

# Stop container
docker stop source-code-analyzer

# Remove container
docker rm source-code-analyzer

# Login to ECR and pull manually
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker pull 123456789.dkr.ecr.us-east-1.amazonaws.com/source-code-analyzer:latest
```

### Local (for testing before pushing)

```bash
# Build Docker image locally
docker build -t source-code-analyzer:local .

# Run locally to test
docker run -p 5001:5001 -e GOOGLE_API_KEY=your-key source-code-analyzer:local

# Test app
curl http://localhost:5001
```

## Security Notes

⚠️ **Important**:

- Never commit `.pem` files or API keys to GitHub
- GitHub Secrets are encrypted at rest
- EC2_SSH_KEY should be the **entire content** of your .pem file
- Rotate AWS access keys periodically
- Use IAM roles instead of access keys in production (advanced)

## Cost Estimation

Approximate monthly costs:

- EC2 t2.micro: ~$10-15 (eligible for free tier)
- ECR storage: ~$0.10-1 (depends on image size)
- Data transfer: ~$0-5 (depends on usage)

## References

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [AWS ECR Docs](https://docs.aws.amazon.com/ecr/)
- [AWS EC2 Docs](https://docs.aws.amazon.com/ec2/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
