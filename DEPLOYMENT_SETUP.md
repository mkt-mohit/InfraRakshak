# AWS ECR + EC2 Deployment Setup Guide

This guide will help you set up the CI/CD pipeline to deploy your Streamlit app to AWS EC2 using Docker and ECR.

---

## Prerequisites Checklist

- ✅ AWS Account with $100 credit
- ✅ EC2 instance running (IP: 43.205.236.114)
- ✅ SSH connection working
- ✅ GitHub repository configured

---

## Step 1: Create AWS ECR Repository

### Option A: Using AWS Console

1. **Go to AWS Console** → Services → **Elastic Container Registry (ECR)**
2. Click **"Create repository"**
3. Configure:
   - **Visibility**: Private
   - **Repository name**: `infrarakshak-streamlit`
   - **Tag immutability**: Disabled
   - **Scan on push**: Enabled (optional)
4. Click **"Create repository"**

### Option B: Using AWS CLI

```bash
aws ecr create-repository \
    --repository-name infrarakshak-streamlit \
    --region us-east-1
```

---

## Step 2: Create AWS IAM User for GitHub Actions

### Create IAM User with ECR Permissions

1. **Go to AWS Console** → **IAM** → **Users** → **Add users**
2. User name: `github-actions-ecr`
3. Select **"Programmatic access"**
4. Click **"Next: Permissions"**

### Attach Policies

Click **"Attach policies directly"** and add these policies:
- ✅ `AmazonEC2ContainerRegistryFullAccess`
- ✅ `AmazonEC2ContainerRegistryPowerUser`

Or create a custom policy with minimal permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload"
            ],
            "Resource": "*"
        }
    ]
}
```

5. Click **"Next"** → **"Create user"**
6. **IMPORTANT**: Save the credentials shown:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

---

## Step 3: Configure EC2 Security Group

Allow inbound traffic on port 8501 (Streamlit):

1. **Go to AWS Console** → **EC2** → **Security Groups**
2. Select your EC2 instance's security group
3. Click **"Edit inbound rules"**
4. Click **"Add rule"**:
   - **Type**: Custom TCP
   - **Port range**: 8501
   - **Source**: `0.0.0.0/0` (or your specific IP for security)
   - **Description**: Streamlit UI
5. Click **"Save rules"**

---

## Step 4: Add GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `AWS_ACCESS_KEY_ID` | `AKIA...` | From IAM user creation |
| `AWS_SECRET_ACCESS_KEY` | `wJal...` | From IAM user creation |
| `VM_IP` | `43.205.236.114` | Your EC2 public IP |
| `DEPLOY_KEY` | (private key content) | Already configured |
| `SSH_HOST_KEY` | (host key content) | Already configured |

---

## Step 5: Update Workflow Configuration (Optional)

If your AWS region is different from `us-east-1`, edit `.github/workflows/ci-cd.yml`:

```yaml
env:
  AWS_REGION: us-east-1  # Change to your region (e.g., ap-south-1)
  ECR_REPOSITORY: infrarakshak-streamlit
```

---

## Step 6: Deploy!

### Push to GitHub

```bash
git add .
git commit -m "Add Docker and CI/CD pipeline for AWS ECR deployment"
git push origin main
```

### Monitor Deployment

1. Go to GitHub → Your Repository → **Actions** tab
2. Watch the workflow run:
   - ✅ Build & Push Docker Image to ECR
   - ✅ Deploy to EC2

### Access Your App

Once deployment completes, access your Streamlit app at:

```
http://43.205.236.114:8501
```

---

## Step 7: Verify Deployment on EC2

SSH into your EC2 instance and check:

```bash
# Check running containers
sudo docker ps

# Check container logs
sudo docker logs infrarakshak-app

# Check Streamlit health
curl http://localhost:8501/_stcore/health
```

---

## Troubleshooting

### Issue: Container not starting

```bash
# Check logs
sudo docker logs infrarakshak-app

# Restart container
sudo docker restart infrarakshak-app
```

### Issue: Cannot access Streamlit UI

1. Check EC2 Security Group allows port 8501
2. Check container is running: `sudo docker ps`
3. Check firewall on EC2: `sudo ufw status`

### Issue: ECR authentication failed

```bash
# On EC2, manually login to ECR
aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.us-east-1.amazonaws.com
```

---

## Cost Optimization Tips

With $100 AWS credit:

1. **Use t2.micro or t3.micro** instances (Free tier eligible)
2. **ECR costs**: First 500 MB/month is free, then $0.10/GB/month
3. **Expected monthly cost**: ~$5-10 for EC2 + minimal ECR costs
4. **Your $100 credit**: Should last 10-20 months

---

## What the CI/CD Pipeline Does

1. ✅ **Build**: Creates Docker image with your Streamlit app
2. ✅ **Push**: Uploads image to AWS ECR (your private registry)
3. ✅ **Deploy**: SSHs into EC2, pulls latest image, runs container
4. ✅ **Expose**: Makes app accessible at http://43.205.236.114:8501

---

## Next Steps

- ✅ Monitor your app logs: `sudo docker logs -f infrarakshak-app`
- ✅ Set up HTTPS with Let's Encrypt (optional)
- ✅ Configure custom domain (optional)
- ✅ Set up CloudWatch monitoring (optional)

---

## Support

If you encounter issues:
1. Check GitHub Actions logs
2. SSH into EC2 and check `docker logs`
3. Verify AWS credentials and ECR repository exist
4. Ensure Security Group allows port 8501
