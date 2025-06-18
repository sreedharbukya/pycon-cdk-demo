import json
import os
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    CfnOutput
)
from constructs import Construct


class VpcStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, env_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Load configuration from cdk.json
        config = self._load_config()
        env_config = config.get("context", {}).get(env_name, {})
        
        if not env_config:
            raise ValueError(f"Environment '{env_name}' not found in cdk.json")
        
        # Get VPC configuration
        vpc_config = env_config.get("vpc", {})
        
        if not vpc_config:
            raise ValueError(f"VPC configuration not found for environment '{env_name}'")
        
        # Create VPC
        self.vpc = ec2.Vpc(
            self,
            f"Vpc-{env_name}",
            ip_addresses=ec2.IpAddresses.cidr(vpc_config.get("cidr", "10.0.0.0/16")),
            max_azs=vpc_config.get("max_azs", 2),
            enable_dns_hostnames=vpc_config.get("enable_dns_hostnames", True),
            enable_dns_support=vpc_config.get("enable_dns_support", True),
            nat_gateways=1 if vpc_config.get("enable_nat_gateway", True) else 0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"public-subnet-{env_name}",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name=f"private-subnet-{env_name}",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name=f"isolated-subnet-{env_name}",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ]
        )
        
        # Create a security group for web services
        self.web_security_group = ec2.SecurityGroup(
            self,
            f"WebSecurityGroup-{env_name}",
            vpc=self.vpc,
            description=f"Security group for web services in {env_name}",
            allow_all_outbound=True
        )
        
        # Add ingress rules to web security group
        self.web_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP traffic"
        )
        
        self.web_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS traffic"
        )
        
        # Create a security group for database services
        self.db_security_group = ec2.SecurityGroup(
            self,
            f"DatabaseSecurityGroup-{env_name}",
            vpc=self.vpc,
            description=f"Security group for database services in {env_name}",
            allow_all_outbound=False
        )
        
        # Allow database access from web security group
        self.db_security_group.add_ingress_rule(
            peer=ec2.Peer.security_group_id(self.web_security_group.security_group_id),
            connection=ec2.Port.tcp(3306),
            description="Allow MySQL access from web services"
        )
        
        self.db_security_group.add_ingress_rule(
            peer=ec2.Peer.security_group_id(self.web_security_group.security_group_id),
            connection=ec2.Port.tcp(5432),
            description="Allow PostgreSQL access from web services"
        )
        
        # Create VPC endpoints for common AWS services
        self._create_vpc_endpoints()
        
        # CloudFormation outputs
        CfnOutput(
            self,
            f"VpcId-{env_name}",
            value=self.vpc.vpc_id,
            description=f"VPC ID for {env_name} environment"
        )
        
        CfnOutput(
            self,
            f"VpcCidr-{env_name}",
            value=self.vpc.vpc_cidr_block,
            description=f"VPC CIDR block for {env_name} environment"
        )
        
        CfnOutput(
            self,
            f"PublicSubnetIds-{env_name}",
            value=",".join([subnet.subnet_id for subnet in self.vpc.public_subnets]),
            description=f"Public subnet IDs for {env_name} environment"
        )
        
        CfnOutput(
            self,
            f"PrivateSubnetIds-{env_name}",
            value=",".join([subnet.subnet_id for subnet in self.vpc.private_subnets]),
            description=f"Private subnet IDs for {env_name} environment"
        )
        
        CfnOutput(
            self,
            f"WebSecurityGroupId-{env_name}",
            value=self.web_security_group.security_group_id,
            description=f"Web security group ID for {env_name} environment"
        )
        
        CfnOutput(
            self,
            f"DatabaseSecurityGroupId-{env_name}",
            value=self.db_security_group.security_group_id,
            description=f"Database security group ID for {env_name} environment"
        )
    
    def _create_vpc_endpoints(self):
        """Create VPC endpoints for AWS services"""
        # S3 Gateway endpoint
        self.vpc.add_gateway_endpoint(
            "S3GatewayEndpoint",
            service=ec2.GatewayVpcEndpointAwsService.S3,
            subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)]
        )
        
        # DynamoDB Gateway endpoint
        self.vpc.add_gateway_endpoint(
            "DynamoDbGatewayEndpoint",
            service=ec2.GatewayVpcEndpointAwsService.DYNAMODB,
            subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)]
        )
    
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