import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';

export class FrontendStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    // TODO: S3 bucket + CloudFront distribution
  }
}
