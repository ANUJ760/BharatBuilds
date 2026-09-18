import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';

interface ComputeStackProps extends cdk.StackProps {
  vpc: any;
}

export class ComputeStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ComputeStackProps) {
    super(scope, id, props);
    // TODO: Fargate cluster, Lambda functions
  }
}
