#!/usr/bin/env python3
import os
import json
import logging
from aws_cdk import App, Environment
from s3 import S3Stack
from vpc import VpcStack

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration from cdk.json"""
    config_path = os.path.join(os.path.dirname(__file__), "cdk.json")
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("cdk.json not found in the infra directory")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in cdk.json: {e}")


def main():
    app = App()
    
    # Load configuration from cdk.json
    config = load_config()
    
    # Get environment from context or environment variable
    env_name = app.node.try_get_context("env") or os.environ.get("CDK_ENV", "development")
    aws_account_id = os.environ["CDK_DEFAULT_ACCOUNT"]
    
    # Get environment-specific configuration
    env_config = config.get("context", {}).get(env_name, {})
    if not env_config:
        raise ValueError(f"Environment '{env_name}' not found in cdk.json")
    
    # Read region from environment configuration
    region = env_config.get("region")
    if not region:
        raise ValueError(f"Region not found for environment '{env_name}' in cdk.json")
    
    logger.info(f"Deploying to environment: {env_name}")
    logger.info(f"Using region: {region}")
    logger.info(f"Using account: {aws_account_id}")

    
    # AWS environment configuration
    aws_env = Environment(account=aws_account_id, region=region)
    
    # Create the VPC stack first
    vpc_stack = VpcStack(
        app,
        f"VpcStack-{env_name}",
        env_name=env_name,
        env=aws_env,
        description=f"VPC infrastructure for {env_name} environment"
    )
    
    # Create the S3 stack
    s3_stack = S3Stack(
        app, 
        f"S3Stack-{env_name}",
        env_name=env_name,
        env=aws_env,
        description=f"S3 buckets for {env_name} environment"
    )
    
    # Add tags to all resources in both stacks
    for stack in [vpc_stack, s3_stack]:
        stack.tags.set_tag("Environment", env_name)
        stack.tags.set_tag("Project", "pycon")
        stack.tags.set_tag("Region", region)
    
    logger.info("CDK synthesis completed successfully")
    app.synth()


if __name__ == "__main__":
    main()

