import requests
import time

def test_swarm_workflow():
    """Test complete swarm delegation workflow"""

    # 1. Check swarm API health
    response = requests.get("http://localhost:8300/health")
    assert response.status_code == 200
    print("✓ Swarm API healthy")

    # 2. Get cost estimate
    response = requests.get("http://localhost:8300/api/swarm/cost-estimate", params={"tokens": 50000})
    estimate = response.json()
    assert "cost_usd" in estimate
    print(f"✓ Cost estimate: ${estimate['cost_usd']:.4f}")

    # 3. Delegate sample task
    test_task = "Write a Python function to calculate fibonacci numbers"
    response = requests.post(
        "http://localhost:8300/api/swarm/delegate",
        params={"prompt": test_task, "estimated_tokens": 5000}
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Task delegated successfully")
        print(f"  Tokens used: {result['tokens_used']}")
        print(f"  Cost: ${result['cost_usd']:.4f}")
        print(f"  Output preview: {result['output'][:200]}...")
        return True
    else:
        print(f"✗ Delegation failed: {response.text}")
        return False

if __name__ == "__main__":
    success = test_swarm_workflow()
    exit(0 if success else 1)
