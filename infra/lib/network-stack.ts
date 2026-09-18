import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';

export class NetworkStack extends cdk.Stack {
  // TODO: VPC, ALB
  public readonly vpc: any;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    // TODO: define VPC and Application Load Balancer
  }
}
