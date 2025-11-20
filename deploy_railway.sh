#!/bin/bash

# SANTANDER QUANT DESK - Quick Deploy Script

echo "🚀 Santander Quant Desk - Railway Deployment"
echo "=============================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null
then
    echo "⚠️  Railway CLI not found. Installing..."
    npm i -g @railway/cli
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Initialize project
echo "📦 Initializing Railway project..."
railway init

# Deploy
echo "🚀 Deploying to Railway..."
railway up

# Show URL
echo ""
echo "✅ Deployment complete!"
echo "🌐 Opening in browser..."
railway open

echo ""
echo "🎉 Your Quant Desk is now live on Railway!"
echo "📊 Check Railway Dashboard for logs and metrics"
