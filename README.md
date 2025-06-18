# PyCon CDK Demo

A comprehensive AWS Cloud Development Kit (CDK) project built for **PyCon 2025 Singapore**, demonstrating infrastructure as code best practices with Python. This project showcases multi-environment deployments, VPC networking, S3 storage, and configuration-driven infrastructure as a practical learning example for conference attendees.

## 🏗️ Project Overview

This educational CDK application was created for **PyCon 2025 Singapore** to demonstrate real-world infrastructure as code patterns. It deploys AWS infrastructure across multiple environments (development, staging, production) with:

- **VPC Stack**: Complete networking setup with public/private subnets, security groups, and VPC endpoints
- **S3 Stack**: Managed S3 buckets with encryption and lifecycle policies
- **Multi-Environment Support**: Environment-specific configurations and deployments
- **Configuration-Driven**: Centralized configuration management via `cdk.json`
- **Comprehensive Logging**: Structured logging across all stack components
- **Best Practices**: Production-ready patterns suitable for learning and adaptation

### 🇸🇬 PyCon 2025 Singapore Context

This project serves as a hands-on demonstration of:

- Modern Python-based infrastructure automation
- Multi-environment deployment strategies
- AWS CDK best practices and patterns
- Configuration management techniques
- Observability and logging in infrastructure code

## 📋 Prerequisites

- **Python**: >= 3.13
- **Node.js**: >= 14.x (for CDK CLI)
- **AWS CLI**: Configured with appropriate credentials
- **uv**: Python package manager (recommended)

### AWS Account Setup

Ensure your AWS account is configured and you have the necessary permissions to create:

- VPCs and networking resources
- S3 buckets
- IAM roles and policies
- CloudFormation stacks

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### 2. Install CDK CLI (Optional - using uv run npx)

```bash
# Option 1: Global installation
npm install -g aws-cdk

# Option 2: Use npx with uv (recommended - no global install needed)
# Commands will use: uv run npx cdk [command]
```

### 3. Bootstrap CDK (First time only for the specific environment)

```bash
# Using global CDK
cdk bootstrap

# Using npx with uv (recommended)
uv run npx cdk bootstrap
```

### 4. Deploy Infrastructure

```bash
# Deploy to development environment
uv run npx cdk deploy --all --context env=development

# Or specify an environment
uv run npx cdk deploy --all --context env=staging

# Traditional method (if globally installed)
cdk deploy --all --context env=staging
```

## 📁 Project Structure

```
pycon-cdk-demo/
├── infra/
│   ├── app.py              # CDK application entry point
│   ├── cdk.json            # CDK configuration and environment settings
│   ├── vpc.py              # VPC stack implementation
│   ├── s3.py               # S3 stack implementation
│   └── cdk.out/            # CDK synthesis output (generated)
├── pyproject.toml          # Python project configuration
├── uv.lock                 # Dependency lock file
└── README.md               # This file
```

## ⚙️ Configuration

### Environment Configuration (`cdk.json`)

The project uses a centralized configuration approach via `cdk.json`:

```json
{
  "context": {
    "development": {
      "env": "development",
      "region": "us-east-1",
      "vpc": {
        "region": "us-east-1",
        "cidr": "10.0.0.0/16",
        "max_azs": 2,
        "enable_nat_gateway": false
      },
      "s3": [
        {
          "bucket_name": "pycon.day1.store.development"
        }
      ]
    }
  }
}
```

### Supported Environments

| Environment     | VPC CIDR    | Max AZs | NAT Gateway | S3 Buckets |
| --------------- | ----------- | ------- | ----------- | ---------- |
| **development** | 10.0.0.0/16 | 2       | ❌          | 1          |
| **staging**     | 10.1.0.0/16 | 2       | ❌          | 1          |
| **production**  | 10.2.0.0/16 | 3       | ✅          | 1          |

## 🛠️ Usage

### Deployment Commands

```bash
# List all stacks
uv run npx cdk list

# Deploy all stacks to development
uv run npx cdk deploy --all --context env=development

# Deploy to specific environment
uv run npx cdk deploy --all --context env=production

# Deploy specific stack
uv run npx cdk deploy VpcStack-development

# View planned changes for all stacks
uv run npx cdk diff --all --context env=staging

# View planned changes for specific stack
uv run npx cdk diff -c env=development S3Stack-development

# Traditional commands (if CDK globally installed)
cdk list
cdk deploy --all --context env=production
cdk diff --all --context env=staging
```

### Environment Variables

Set the following environment variables:

```bash
export CDK_DEFAULT_ACCOUNT="123456789012"  # Your AWS Account ID
export CDK_ENV="development"               # Target environment (optional)
```

### Stack Dependencies

The stacks are deployed in the following order:

1. **VpcStack**: Core networking infrastructure
2. **S3Stack**: Storage resources (independent of VPC)

## 🏗️ Infrastructure Components

### VPC Stack Features

- **Networking**: Multi-AZ setup with public, private, and isolated subnets
- **Security Groups**:
  - Web Security Group (HTTP/HTTPS access)
  - Database Security Group (MySQL/PostgreSQL access from web tier)
- **VPC Endpoints**: S3 and DynamoDB gateway endpoints for cost optimization
- **NAT Gateway**: Environment-specific (enabled in production only)

### S3 Stack Features

- **Encryption**: Server-side encryption with S3-managed keys
- **Versioning**: Enabled for all buckets
- **Public Access**: Blocked by default
- **Retention**: RETAIN policy to prevent accidental deletion

## 🔧 Development

### Adding New Environments

1. Add environment configuration to `cdk.json`:

```json
"new-env": {
  "env": "new-env",
  "region": "us-west-2",
  "vpc": { ... },
  "s3": [ ... ]
}
```

2. Deploy with the new environment:

```bash
cdk deploy --all --context env=new-env
```

### Modifying Infrastructure

1. Update the relevant stack file (`vpc.py` or `s3.py`)
2. Update configuration in `cdk.json` if needed
3. Preview changes: `cdk diff --all`
4. Deploy changes: `cdk deploy --all`

### Logging

The application includes comprehensive logging:

- **INFO**: Major operations and milestones
- **DEBUG**: Detailed configuration and processing information
- **ERROR**: Exception handling and critical issues
- **WARNING**: Non-critical issues

View logs during deployment to monitor progress and troubleshoot issues.

## 📊 Monitoring and Outputs

Each stack provides CloudFormation outputs for integration:

### VPC Stack Outputs

- VPC ID
- VPC CIDR block
- Public/Private subnet IDs
- Security group IDs

### S3 Stack Outputs

- Bucket names
- Bucket ARNs

Access outputs via AWS Console or CLI:

```bash
aws cloudformation describe-stacks --stack-name VpcStack-development
```

## 🧹 Cleanup

To avoid ongoing AWS charges, destroy resources when no longer needed:

```bash
# Destroy all stacks in development
uv run npx cdk destroy --all --context env=development

# Destroy specific stack
uv run npx cdk destroy S3Stack-development

# Traditional method (if globally installed)
cdk destroy --all --context env=development
```

**⚠️ Warning**: S3 buckets have a RETAIN policy. Delete bucket contents manually before stack destruction.

## 🔍 Troubleshooting

### Common Issues

1. **Bootstrap Error**: Ensure CDK is bootstrapped in your target region
2. **Permission Denied**: Verify AWS credentials and IAM permissions
3. **Resource Conflicts**: Check for existing resources with the same names
4. **Environment Not Found**: Verify environment exists in `cdk.json`

### Debug Commands

```bash
# View CDK version
uv run npx cdk --version

# Verify AWS credentials
aws sts get-caller-identity

# List available environments
python -c "import json; print(list(json.load(open('infra/cdk.json'))['context'].keys()))"

# Traditional CDK version check (if globally installed)
cdk --version
```

## 📚 Dependencies

- **aws-cdk-lib**: ^2.201.0 - AWS CDK library
- **constructs**: ^10.4.2 - CDK constructs framework
- **Python**: >=3.13 - Runtime environment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For questions and support:

- Open an issue in this repository
- Check the [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- Review [CDK API Reference](https://docs.aws.amazon.com/cdk/api/v2/)

## 🙏 Acknowledgments

This project was created for **PyCon 2025 Singapore** as an educational resource for the Python community. Special thanks to:

- PyCon Singapore organizers and volunteers
- AWS CDK development team
- Python community contributors

---

**Built with ❤️ for PyCon 2025 Singapore using AWS CDK and Python** 🇸🇬
