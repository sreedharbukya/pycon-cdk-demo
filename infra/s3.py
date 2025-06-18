import json
import os
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    RemovalPolicy
)
from constructs import Construct


class S3Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, env_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Load configuration from cdk.json
        config = self._load_config()
        env_config = config.get("context", {}).get(env_name, {})
        
        if not env_config:
            raise ValueError(f"Environment '{env_name}' not found in cdk.json")
        
        # Create S3 buckets based on configuration
        self.buckets = {}
        s3_configs = env_config.get("s3", [])
        
        for bucket_config in s3_configs:
            bucket_name = bucket_config.get("bucket_name")
            if not bucket_name:
                continue
            
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
    
    def _sanitize_construct_id(self, bucket_name: str) -> str:
        """Convert bucket name to a valid CDK construct ID"""
        # Replace dots and other special characters with underscores
        # Convert to PascalCase for construct ID convention
        parts = bucket_name.replace(".", "_").replace("-", "_").split("_")
        return "".join(word.capitalize() for word in parts if word)
    
    def _load_config(self):
        """Load configuration from cdk.json"""
        config_path = os.path.join(os.path.dirname(__file__), "cdk.json")
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("cdk.json not found in the infra directory")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in cdk.json: {e}")
