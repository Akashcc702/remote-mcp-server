# Claude & Antigravity Remote MCP Server (Render.com 0-Cost Deployment)

This repository contains a production-ready, secure Model Context Protocol (MCP) server designed to be deployed on **Render.com** (Free Tier - 0 Cost) and connected to multiple **Claude.ai** and **Antigravity** accounts simultaneously.

## Features
- **0 Cost Deployment**: Designed for Render.com Free Web Service.
- **Auto SSL/TLS**: Render provides free HTTPS certificates out of the box (no Caddy or manual certs required).
- **Token Protected Endpoint**: Routes are protected by a 32-character secret hex token (`/mcp-sec-<token>`).
- **24/7 Keep-Alive**: Built-in `/health` route for free uptime monitors (e.g., UptimeRobot, Cron-job.org) to prevent Render free instance sleeping.
- **Multi-Client Support**: Tested with multiple Claude accounts and Antigravity instances simultaneously.

## Secret Token
- **Token:** `c9c7230c9f593c89d8847bbdc4fecea1`
- **Protected SSE Endpoint:** `/mcp-sec-c9c7230c9f593c89d8847bbdc4fecea1`
- **Health Check Endpoint:** `/health`

## Render.com Setup
1. Push this folder to a GitHub repository.
2. In [Render Dashboard](https://dashboard.render.com), click **New +** -> **Web Service**.
3. Select your repository.
4. Render will read `render.yaml` automatically, or configure:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
5. Deploy the service.

## Connecting to Claude.ai
1. Go to [claude.ai](https://claude.ai) -> Profile -> Settings -> Connectors.
2. Click **Add Custom Connector**.
3. Enter Name: `Remote Cloud Ops`
4. Enter URL:
   `https://<YOUR-RENDER-APP-NAME>.onrender.com/mcp-sec-c9c7230c9f593c89d8847bbdc4fecea1`
5. Save. Repeat for up to 4 Claude accounts.

## Connecting to Antigravity
Add to your Antigravity MCP configuration:
```json
{
  "mcpServers": {
    "remote-cloud-ops": {
      "url": "https://<YOUR-RENDER-APP-NAME>.onrender.com/mcp-sec-c9c7230c9f593c89d8847bbdc4fecea1"
    }
  }
}
```
