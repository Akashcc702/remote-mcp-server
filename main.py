import os
import sys
import platform
import datetime
import io
import contextlib
import uvicorn
from starlette.responses import JSONResponse
from mcp.server.mcpserver import MCPServer

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

# 5. Build the Starlette SSE application with token-protected routes
# GET /mcp-sec-<token> -> SSE stream
# POST /mcp-sec-<token>/messages/ -> Message receiver
app = mcp.sse_app(
    sse_path=f"/mcp-sec-{AUTH_TOKEN}",
    message_path=f"/mcp-sec-{AUTH_TOKEN}/messages/"
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"=======================================================")
    print(f"Starting MCP Server on port {port}")
    print(f"SSE Endpoint: http://localhost:{port}/mcp-sec-{AUTH_TOKEN}")
    print(f"Health Check: http://localhost:{port}/health")
    print(f"=======================================================")
    uvicorn.run(app, host="0.0.0.0", port=port)
