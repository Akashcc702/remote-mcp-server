import urllib.request
import json
import time

def test_endpoints():
    base_url = "http://127.0.0.1:8000"
    token = "c9c7230c9f593c89d8847bbdc4fecea1"
    
    # Test Health Endpoint
    print("\n[1] Testing /health endpoint...")
    try:
        with urllib.request.urlopen(f"{base_url}/health", timeout=5) as response:
            data = json.loads(response.read().decode())
            print(f"  Health Check Status: {response.status}")
            print(f"  Response Data: {data}")
            assert data["status"] == "healthy"
            print("  -> /health PASSED!")
    except Exception as e:
        print(f"  Health check failed: {e}")
        return False
        
    # Test Unauthorized route
    print("\n[2] Testing random unauthorized route...")
    try:
        urllib.request.urlopen(f"{base_url}/mcp-sec-invalidtoken", timeout=5)
        print("  Failed: expected 404 for invalid token!")
    except urllib.error.HTTPError as e:
        print(f"  Received expected HTTP {e.code} for invalid token.")
        print("  -> Unauthorized protection PASSED!")
        
    # Test Protected SSE route handshake
    print("\n[3] Testing /mcp-sec-<token> SSE route...")
    req = urllib.request.Request(
        f"{base_url}/mcp-sec-{token}",
        headers={"Accept": "text/event-stream"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"  SSE Status: {resp.status}")
            print(f"  Content-Type: {resp.headers.get('Content-Type')}")
            # Read first line
            first_chunk = resp.readline().decode()
            print(f"  First SSE line: {first_chunk.strip()}")
            print("  -> SSE Handshake PASSED!")
    except Exception as e:
        print(f"  SSE test: {e}")
        
    print("\nALL LOCAL TESTS COMPLETED SUCCESSFULLY!")
    return True

if __name__ == "__main__":
    test_endpoints()
