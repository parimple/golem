#!/bin/bash
# GOLEM Test Runner

echo "🧪 Running GOLEM Integration Tests"
echo "=================================="

# Track overall status
ALL_PASSED=true

# Run cog loading tests
echo "📦 Testing Cog Loading..."
python tests/test_cog_loading.py
if [ $? -ne 0 ]; then
    echo "❌ Cog loading tests failed!"
    ALL_PASSED=false
else
    echo "✅ Cog loading tests passed!"
fi

# Run memory lint tests
echo ""
echo "🧠 Testing Memory Lint..."
python tests/test_memory_lint.py
if [ $? -ne 0 ]; then
    echo "❌ Memory lint tests failed!"
    ALL_PASSED=false
else
    echo "✅ Memory lint tests passed!"
fi

# Final result
echo ""
if [ "$ALL_PASSED" = true ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed!"
    exit 1
fi

echo ""
echo "🔍 Quick Cog Summary:"
echo "---------------------"
find cogs/commands -name "*.py" -not -name "__*" | wc -l | xargs echo "Total cogs:"
find cogs/commands -name "*.py" -not -name "__*" -exec basename {} \; | sort

echo ""
echo "✨ Test complete!"