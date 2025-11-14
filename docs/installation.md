# Installation Guide

## Prerequisites

- Python 3.8 or higher
- Git
- AWS CLI configured with Bedrock access
- Bitbucket account with API access (for PR reviews)

## Step 1: Clone Repository

```bash
git clone <repository-url>
cd codeReviewAgent
```

## Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Environment Configuration

1. Copy the environment template:
   ```bash
   cp .env.template .env
   ```

2. Edit `.env` file with your credentials:
   ```bash
   # Bitbucket Configuration
   BITBUCKET_URL=https://git.cnvrmedia.net/rest/api/1.0
   BITBUCKET_TOKEN=your_bitbucket_token_here
   
   # AWS Configuration (for Bedrock)
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   ```

## Step 5: AWS Bedrock Setup

### Option 1: AWS CLI Configuration
```bash
aws configure
```

### Option 2: Environment Variables
Set the following environment variables:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`

### Option 3: IAM Role (for EC2/Lambda)
Attach an IAM role with Bedrock permissions to your compute instance.

### Required AWS Permissions

Your AWS user/role needs the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
            ]
        }
    ]
}
```

## Step 6: Verify Installation

Test the installation with a local review:

```bash
python main.py --mode local --base-branch main
```

If successful, you should see output indicating the review process has started.

## Troubleshooting

### Common Issues

**1. AWS Bedrock Access Denied**
- Ensure your AWS credentials have Bedrock permissions
- Check if Claude 3.5 Sonnet is available in your region
- Verify the model ID is correct

**2. Git Command Not Found**
- Install Git on your system
- Ensure Git is in your system PATH

**3. Python Module Import Errors**
- Verify you're using the correct Python version (3.8+)
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

**4. Bitbucket API Errors**
- Verify your Bitbucket token has the correct permissions
- Check if the workspace and repository names are correct
- Ensure the token hasn't expired

### Getting Help

If you encounter issues:

1. Check the [Troubleshooting](troubleshooting.md) guide
2. Review the logs for error messages
3. Verify all prerequisites are met
4. Test with a minimal example first
