import json
import os
import logging
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    RemovalPolicy
)
from constructs import Construct

# Set up logging
logger = logging.getLogger(__name__)


class S3Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, env_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        logger.info(f"Initializing S3 stack for environment: {env_name}")
        
        # Load configuration from cdk.json
        config = self._load_config()
        env_config = config.get("context", {}).get(env_name, {})
        
        if not env_config:
            raise ValueError(f"Environment '{env_name}' not found in cdk.json")
        
        # Create S3 buckets based on configuration
        self.buckets = {}
        s3_configs = env_config.get("s3", [])
        
        logger.info(f"Found {len(s3_configs)} S3 bucket configurations for {env_name}")
        
        for bucket_config in s3_configs:
            bucket_name = bucket_config.get("bucket_name")
            if not bucket_name:
                logger.warning("Skipping bucket configuration without bucket_name")
                continue
            
            logger.info(f"Creating S3 bucket: {bucket_name}")
            
            # Create a valid construct ID from bucket name
            construct_id = self._sanitize_construct_id(bucket_name)
                
            # Create S3 bucket
            bucket = s3.Bucket(
                self, 
                construct_id,
                bucket_name=bucket_name,
                versioned=True,
                encryption=s3.BucketEncryption.S3_MANAGED,
                block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                removal_policy=RemovalPolicy.RETAIN
            )
            
            # Store bucket reference
            self.buckets[bucket_name] = bucket
            
            logger.info(f"S3 bucket created successfully: {bucket_name}")
            
            # Output bucket information
            from aws_cdk import CfnOutput
            CfnOutput(
                self,
                f"{construct_id}Name",
                value=bucket.bucket_name,
                description=f"Name of S3 bucket {bucket_name} for {env_name} environment"
            )
            
            CfnOutput(
                self,
                f"{construct_id}Arn",
                value=bucket.bucket_arn,
                description=f"ARN of S3 bucket {bucket_name} for {env_name} environment"
            )
            
            logger.debug(f"CloudFormation outputs created for bucket: {bucket_name}")
        
        logger.info(f"S3 stack initialization completed for {env_name} - Created {len(self.buckets)} buckets")
    
    def _sanitize_construct_id(self, bucket_name: str) -> str:
        """Convert bucket name to a valid CDK construct ID"""
        # Replace dots and other special characters with underscores
        # Convert to PascalCase for construct ID convention
        parts = bucket_name.replace(".", "_").replace("-", "_").split("_")
        construct_id = "".join(word.capitalize() for word in parts if word)
        logger.debug(f"Sanitized bucket name '{bucket_name}' to construct ID '{construct_id}'")
        return construct_id
    
    def _load_config(self):
        """Load configuration from cdk.json"""
        logger.debug("Loading configuration from cdk.json")
        config_path = os.path.join(os.path.dirname(__file__), "cdk.json")
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                logger.debug("Configuration loaded successfully from cdk.json")
                return config
        except FileNotFoundError:
            logger.error("cdk.json not found in the infra directory")
            raise FileNotFoundError("cdk.json not found in the infra directory")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in cdk.json: {e}")
            raise ValueError(f"Invalid JSON in cdk.json: {e}")
