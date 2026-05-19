"""Quick connectivity tests for FORGE backend services.

Run: python -m scripts.test_connectivity
"""

import asyncio
import sys

import httpx


async def test_database():
    """Test PostgreSQL connection."""
    print("\n--- Database Connectivity ---")
    try:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import create_async_engine

        from src.config import get_settings

        settings = get_settings()
        engine = create_async_engine(settings.database_url, echo=False)
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"  OK: Connected to PostgreSQL")
            print(f"  Version: {version}")

            result = await conn.execute(
                text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'")
            )
            count = result.scalar()
            print(f"  Tables: {count}")

        await engine.dispose()
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


async def test_deepseek_chat():
    """Test DeepSeek V4-Flash API connectivity with a tiny prompt."""
    print("\n--- DeepSeek Chat API ---")
    try:
        from src.config import get_settings

        settings = get_settings()
        if not settings.deepseek_api_key:
            print("  SKIP: DEEPSEEK_API_KEY not set")
            return False

        print(f"  Base URL: {settings.deepseek_base_url}")
        print(f"  Model: {settings.deepseek_model}")
        print(f"  API Key: {settings.deepseek_api_key[:8]}...{settings.deepseek_api_key[-4:]}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{settings.deepseek_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.deepseek_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.deepseek_model,
                    "messages": [
                        {"role": "user", "content": "Reply with only: FORGE_OK"}
                    ],
                    "max_tokens": 10,
                    "temperature": 0,
                },
            )

        if resp.status_code == 200:
            data = resp.json()
            reply = data["choices"][0]["message"]["content"].strip()
            usage = data.get("usage", {})
            print(f"  OK: Got response: '{reply}'")
            print(f"  Tokens: {usage.get('prompt_tokens', '?')} in, {usage.get('completion_tokens', '?')} out")
            return True
        else:
            print(f"  FAIL: HTTP {resp.status_code}")
            print(f"  Body: {resp.text[:300]}")
            return False

    except Exception as e:
        print(f"  FAIL: {e}")
        return False


async def test_auth_flow():
    """Test signup → login → me flow against the running server."""
    print("\n--- Auth Flow (requires running server on :8000) ---")
    base = "http://localhost:8000"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Health check
            resp = await client.get(f"{base}/health")
            if resp.status_code != 200:
                print("  SKIP: Server not running on port 8000")
                return False
            print("  Health: OK")

            # Signup
            resp = await client.post(
                f"{base}/api/v1/auth/signup",
                json={
                    "email": "connectivity-test@forge.app",
                    "password": "testpass123",
                    "name": "Connectivity Test",
                },
            )
            if resp.status_code == 201:
                print("  Signup: OK (new user)")
            elif resp.status_code == 409:
                print("  Signup: OK (user exists, testing login)")
            else:
                print(f"  Signup: FAIL ({resp.status_code}: {resp.text[:200]})")
                return False

            # Login
            resp = await client.post(
                f"{base}/api/v1/auth/login",
                json={"email": "connectivity-test@forge.app", "password": "testpass123"},
            )
            if resp.status_code != 200:
                print(f"  Login: FAIL ({resp.status_code})")
                return False
            token = resp.json()["access_token"]
            print("  Login: OK")

            # Me
            resp = await client.get(
                f"{base}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            if resp.status_code == 200:
                print(f"  /me: OK — {resp.json()['email']}")
            else:
                print(f"  /me: FAIL ({resp.status_code})")
                return False

        return True
    except httpx.ConnectError:
        print("  SKIP: Cannot connect to localhost:8000 (start server first)")
        return False
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


async def main():
    print("=" * 50)
    print("FORGE — Connectivity Tests")
    print("=" * 50)

    results = {}
    results["database"] = await test_database()
    results["deepseek"] = await test_deepseek_chat()
    results["auth_flow"] = await test_auth_flow()

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for name, ok in results.items():
        status = "PASS" if ok else "FAIL/SKIP"
        print(f"  {name:.<30} {status}")

    all_ok = all(results.values())
    print(f"\nOverall: {'ALL PASS' if all_ok else 'SOME FAILED'}")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    asyncio.run(main())
