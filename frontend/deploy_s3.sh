#!/bin/bash
set -e

echo "🚀 Starting 60-Second Frontend Deployment..."

# 1. Extract backend URL from CloudFormation
echo "🔍 Fetching Backend API URL..."
API_URL=$(aws cloudformation describe-stacks --stack-name deployed-backend --query "Stacks[0].Outputs[?OutputKey=='BackendApiUrl'].OutputValue" --output text)
echo "✅ Found Backend API: $API_URL"

# 2. Extract Cognito info from .env
USER_POOL_ID=$(grep COGNITO_USER_POOL_ID ../.env | cut -d '=' -f2)
CLIENT_ID=$(grep COGNITO_APP_CLIENT_ID ../.env | cut -d '=' -f2)

# 3. Create frontend/.env
echo "VITE_API_BASE_URL=$API_URL" > .env
echo "VITE_COGNITO_USER_POOL_ID=$USER_POOL_ID" >> .env
echo "VITE_COGNITO_APP_CLIENT_ID=$CLIENT_ID" >> .env
echo "✅ Injected Environment Variables."

# 4. Build React App
echo "📦 Building React App (this takes ~30 seconds)..."
npm run build

# 5. Create S3 Bucket and Deploy
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET_NAME="smallops-frontend-${ACCOUNT_ID}"
REGION="ap-south-1"

echo "☁️ Provisioning S3 Hosting ($BUCKET_NAME)..."
aws s3 mb s3://$BUCKET_NAME --region $REGION || true
aws s3 website s3://$BUCKET_NAME/ --index-document index.html --error-document index.html

# Disable Block Public Access
aws s3api put-public-access-block --bucket $BUCKET_NAME --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# Add Public Read Policy
cat <<POLICY > policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
POLICY
sleep 2 # wait for public access block to propagate
aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://policy.json
rm policy.json

echo "⬆️ Uploading to S3..."
aws s3 sync dist/ s3://$BUCKET_NAME/

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "🌐 Your App is Live at: http://$BUCKET_NAME.s3-website.$REGION.amazonaws.com"
