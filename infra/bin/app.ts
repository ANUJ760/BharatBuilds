#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { NetworkStack } from '../lib/network-stack';
import { ComputeStack } from '../lib/compute-stack';
import { DataStack } from '../lib/data-stack';
import { AuthStack } from '../lib/auth-stack';
import { FrontendStack } from '../lib/frontend-stack';

const app = new cdk.App();

const networkStack = new NetworkStack(app, 'BharatBuilds-Network');
const dataStack = new DataStack(app, 'BharatBuilds-Data');
const authStack = new AuthStack(app, 'BharatBuilds-Auth');
const computeStack = new ComputeStack(app, 'BharatBuilds-Compute', {
  vpc: networkStack.vpc,
});
const frontendStack = new FrontendStack(app, 'BharatBuilds-Frontend');
