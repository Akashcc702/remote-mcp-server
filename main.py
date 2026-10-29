import os
import sys
import platform
import datetime
import io
import contextlib
import uvicorn
from starlette.responses import JSONResponse, Response
from starlette.middleware.cors import CORSMiddleware
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

# 1. 32-character Secret Token (can be overridden via environment variable MCP_TOKEN)
AUTH_TOKEN = os.environ.get("MCP_TOKEN", "c9c7230c9f593c89d8847bbdc4fecea1")

# 2. Initialize MCP Server
mcp = MCPServer("cloud-remote-ops")

# 3. Define Tools for Claude and Antigravity
@mcp.tool()
def get_server_status() -> str:
    """Returns the operational status, OS, Python version, and server timestamp."""
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return (
        f"Server Status: OPERATIONAL\n"
        f"UTC Time: {now}\n"
        f"Platform: {platform.system()} {platform.release()} ({platform.machine()})\n"
        f"Python: {platform.python_version()}\n"
        f"Process ID: {os.getpid()}"
    )

@mcp.tool()
def execute_python_code(code: str) -> str:
    """Executes Python code in the cloud environment and captures standard output."""
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            exec_globals = {"__builtins__": __builtins__}
            exec(code, exec_globals)
        output = buffer.getvalue()
        return output if output else "Execution finished with no output."
    except Exception as e:
        return f"Error executing code: {type(e).__name__}: {str(e)}"

@mcp.tool()
def echo_message(message: str) -> str:
    """Echoes a message back to verify connectivity and test latency across connected accounts."""
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"[{now}] Echo received: {message}"

# 4. Custom Health Endpoint for Keep-Alive Pings (UptimeRobot / Cron-job.org)
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint to keep Render.com free tier awake 24/7."""
    return JSONResponse({
        "status": "healthy",
        "service": "cloud-remote-ops-mcp",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    })

# 5. Disable DNS rebinding protection so Render.com public domain works properly
security_settings = TransportSecuritySettings(
    enable_dns_rebinding_protection=False,
    allowed_hosts=["*"],
    allowed_origins=["*"]
)

# 6. Build the Starlette SSE application with token-protected routes
# GET /mcp-sec-<token> -> SSE stream
# POST /mcp-sec-<token>/messages/ -> Message receiver
app = mcp.sse_app(
    sse_path=f"/mcp-sec-{AUTH_TOKEN}",
    message_path=f"/mcp-sec-{AUTH_TOKEN}/messages/",
    transport_security=security_settings
)

# 7. Add CORS Middleware so Claude web clients can interact seamlessly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# 8. Wrap SSE route to accept POST and OPTIONS preflight checks from Claude connector broker
for route in app.routes:
    if hasattr(route, "path") and route.path == f"/mcp-sec-{AUTH_TOKEN}":
        orig_endpoint = route.endpoint
        async def handle_probe_and_sse(request, _orig=orig_endpoint):
            if request.method == "OPTIONS":
                return Response(status_code=200, headers={"Allow": "GET, POST, OPTIONS, HEAD"})
            if request.method == "POST":
                return JSONResponse({"jsonrpc": "2.0", "result": {"status": "ok", "transport": "sse"}})
            return await _orig(request)
        route.endpoint = handle_probe_and_sse
        route.methods = {"GET", "POST", "OPTIONS", "HEAD"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"=======================================================")
    print(f"Starting MCP Server on port {port}")
    print(f"SSE Endpoint: http://localhost:{port}/mcp-sec-{AUTH_TOKEN}")
    print(f"Health Check: http://localhost:{port}/health")
    print(f"=======================================================")
    uvicorn.run(app, host="0.0.0.0", port=port)
