#!/bin/bash

echo "═══════════════════════════════════════════════════════════════"
echo "🧪 CHATGPT MCP HTTP GATEWAY - COMPREHENSIVE TEST"
echo "═══════════════════════════════════════════════════════════════"

BASE="http://localhost:8095"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_count=0
passed=0
failed=0

run_test() {
    local name="$1"
    local command="$2"
    local expected="$3"
    
    test_count=$((test_count + 1))
    echo ""
    echo -e "${YELLOW}Test $test_count: $name${NC}"
    
    result=$(eval "$command" 2>&1)
    
    if echo "$result" | grep -q "$expected"; then
        echo -e "${GREEN}✅ PASS${NC}"
        passed=$((passed + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "Expected: $expected"
        echo "Got: $result"
        failed=$((failed + 1))
    fi
}

# Test 1: Health Check
run_test "Health Check" \
    "curl -s $BASE/health | jq -r '.status'" \
    "healthy"

# Test 2: Root Endpoint
run_test "Root Endpoint" \
    "curl -s $BASE/ | jq -r '.service'" \
    "ChatGPT MCP HTTP Gateway"

# Test 3: Quantum Hash
run_test "Quantum Hash" \
    "curl -s -X POST $BASE/mcp/tools/quantum_hash -H 'Content-Type: application/json' -d '{\"data\":\"test\"}' | jq -r '.algorithm'" \
    "quantum-sha256"

# Test 4: Quantum Verify
HASH=$(curl -s -X POST $BASE/mcp/tools/quantum_hash -H 'Content-Type: application/json' -d '{"data":"test"}' | jq -r '.hash')
run_test "Quantum Verify" \
    "curl -s -X POST $BASE/mcp/tools/quantum_verify -H 'Content-Type: application/json' -d '{\"data\":\"test\",\"expected_hash\":\"$HASH\"}' | jq -r '.verified'" \
    "true"

# Test 5: Merkle Root
run_test "Merkle Root" \
    "curl -s -X POST $BASE/mcp/tools/quantum_merkle_root -H 'Content-Type: application/json' -d '{\"leaves\":[\"a\",\"b\",\"c\"]}' | jq -r '.leaf_count'" \
    "3"

# Test 6: Create Manifest
run_test "Create Manifest" \
    "curl -s -X POST $BASE/mcp/tools/create_manifest -H 'Content-Type: application/json' -d '{\"files\":[{\"path\":\"/test\",\"hash\":\"xyz\"}]}' | jq -r '.status'" \
    "CRYSTALLINE"

# Test 7: KG Query
run_test "KG Query" \
    "curl -s -X POST $BASE/mcp/tools/kg_query -H 'Content-Type: application/json' -d '{\"query\":\"quantum\",\"limit\":1}' | jq -r '.total'" \
    "0"

# Test 8: Quantum State Resource
run_test "Quantum State Resource" \
    "curl -s $BASE/mcp/resources/quantum/state | jq -r '.resource'" \
    "vault://quantum/state"

# Test 9: Manifests Resource
run_test "Manifests Resource" \
    "curl -s $BASE/mcp/resources/manifests/latest | jq -r '.manifests' | jq 'type'" \
    "array"

# Test 10: CORS Headers
run_test "CORS Headers" \
    "curl -s -I $BASE/health | grep -i 'access-control-allow-origin'" \
    "Access-Control-Allow-Origin: *"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "📊 TEST RESULTS"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo -e "Total Tests: $test_count"
echo -e "${GREEN}Passed: $passed${NC}"
echo -e "${RED}Failed: $failed${NC}"
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED - ChatGPT MCP Gateway is fully functional!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed - Check logs: npx pm2 logs chatgpt-mcp-http${NC}"
    exit 1
fi
