"""AWS CDK infrastructure stacks for MicroAgent."""
from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambda_,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_cognito as cognito,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_events as events,
    aws_events_targets as targets,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct


class DataStack(Stack):
    """DynamoDB and S3 resources."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB single-table design
        self.table = dynamodb.Table(
            self, "MicroAgentTable",
            partition_key=dynamodb.Attribute(name="pk", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="sk", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # GSI for organization-level queries
        self.table.add_global_secondary_index(
            index_name="GSI1",
            partition_key=dynamodb.Attribute(name="GSI1PK", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="GSI1SK", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL,
        )

        # S3 for artifacts
        self.bucket = s3.Bucket(
            self, "MicroAgentArtifacts",
            removal_policy=RemovalPolicy.RETAIN,
            versioned=True,
        )

        CfnOutput(self, "TableName", value=self.table.table_name)
        CfnOutput(self, "BucketName", value=self.bucket.bucket_name)


class AuthStack(Stack):
    """Cognito User Pool for authentication."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.user_pool = cognito.UserPool(
            self, "MicroAgentUserPool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            removal_policy=RemovalPolicy.RETAIN,
        )

        self.user_pool_client = cognito.UserPoolClient(
            self, "MicroAgentUserPoolClient",
            user_pool=self.user_pool,
            auth_flows=cognito.AuthFlow(
                user_password_auth=True,
                user_srp_auth=True,
            ),
            prevent_user_existence_errors=True,
        )

        CfnOutput(self, "UserPoolId", value=self.user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=self.user_pool_client.user_pool_client_id)


class ComputeStack(Stack):
    """Lambda functions for API and agent execution."""

    def __init__(self, scope: Construct, construct_id: str, table, bucket, user_pool, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda handler for API
        self.api_handler = lambda_.Function(
            self, "MicroAgentAPI",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="main.handler",
            code=lambda_.Code.from_asset("backend/"),
            timeout=Duration.seconds(30),
            environment={
                "DYNAMODB_TABLE_NAME": table.table_name,
                "S3_BUCKET_NAME": bucket.bucket_name,
                "COGNITO_USER_POOL_ID": user_pool.user_pool_id,
            },
        )

        table.grant_read_write_data(self.api_handler)
        bucket.grant_read_write(self.api_handler)

        # API Gateway
        self.api = apigw.RestApi(self, "MicroAgentAPI",
            rest_api_name="MicroAgent API",
            deploy_options=apigw.StageOptions(
                stage_name="v1",
                throttling_rate_limit=100,
                throttling_burst_limit=200,
            ),
        )

        self.api.root.add_proxy(
            default_integration=apigw.LambdaIntegration(self.api_handler),
        )

        CfnOutput(self, "ApiEndpoint", value=self.api.url)


class MonitoringStack(Stack):
    """EventBridge and Step Functions for workflow orchestration."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # EventBridge rule to trigger workflow runs
        self.rule = events.Rule(
            self, "MicroAgentWorkflowRule",
            schedule=events.Schedule.rate(Duration.minutes(5)),
        )

        CfnOutput(self, "EventRuleName", value=self.rule.rule_name)
