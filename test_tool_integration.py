# -*- coding: utf-8 -*-
"""Test Katy's tool calling system integration."""

import sys
sys.path.insert(0, r"C:\Users\Admin\Desktop\Agent-Reach")

from agent_reach.tool_dispatcher import IntentClassifier, ToolGate, ToolDispatcher


def test_intent_classifier():
    """Test IntentClassifier with various inputs."""
    print("=== Test IntentClassifier ===")
    ic = IntentClassifier()
    
    test_cases = [
        ("busca en Twitter qué dicen sobre Python 4", "twitter_search"),
        ("lee https://twitter.com/user/status/123", "twitter_read"),
        ("busca en YouTube tutoriales de Python", "youtube_search"),
        ("qué dicen en YouTube sobre React", "youtube_search"),
        ("revisa el RSS de https://example.com/feed", "rss_parse"),
        ("lee https://docs.djangoproject.com", "web_read"),
        ("busca en internet información sobre IA", "web_search"),
        ("clima en Barcelona", "weather"),
        ("cuánto es 2 + 2", "calculate"),
        ("recuerda que mi nombre es Juan", "memory_store"),
        ("esto no tiene sentido", "unknown"),
    ]
    
    passed = 0
    failed = 0
    
    for user_input, expected_intent in test_cases:
        intent, channel, action, extracted = ic.classify(user_input)
        
        # Check if intent matches (or is close enough)
        intent_match = (
            intent == expected_intent or
            (expected_intent == "web_search" and intent == "web_search") or
            (expected_intent == "unknown" and intent == "unknown")
        )
        
        status = "✓" if intent_match else "✗"
        if intent_match:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} Input: '{user_input[:50]}...'")
        print(f"  Expected: {expected_intent}, Got: {intent} ({channel}.{action})")
        if extracted:
            print(f"  Extracted: {extracted[:50]}...")
        print()
    
    print(f"Results: {passed}/{passed+failed} passed\n")
    return failed == 0


def test_tool_gate():
    """Test ToolGate permission checking."""
    print("=== Test ToolGate ===")
    tg = ToolGate()
    
    test_cases = [
        ("twitter", "search", True),
        ("web", "read", True),
        ("admin", "execute", False),
        ("payment", "transfer", False),
        ("twitter", "post", True),  # Requires confirmation
    ]
    
    passed = 0
    failed = 0
    
    for channel, action, expected in test_cases:
        is_allowed, reason = tg.check(channel, action)
        
        status = "✓" if is_allowed == expected else "✗"
        if is_allowed == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} {channel}.{action}: {is_allowed} (expected: {expected})")
        print(f"  Reason: {reason}")
        print()
    
    print(f"Results: {passed}/{passed+failed} passed\n")
    return failed == 0


def test_tool_dispatcher():
    """Test ToolDispatcher with sample inputs."""
    print("=== Test ToolDispatcher ===")
    dispatcher = ToolDispatcher()
    
    test_cases = [
        "busca en Twitter qué dicen sobre Python",
        "lee https://example.com",
    ]
    
    passed = 0
    failed = 0
    
    for user_input in test_cases:
        try:
            result = dispatcher.dispatch(user_input, raw=True, verbose=True)
            if result.success:
                passed += 1
                print(f"✓ '{user_input[:40]}...' -> Success")
            else:
                failed += 1
                print(f"✗ '{user_input[:40]}...' -> Failed: {result.error[:100]}")
        except Exception as e:
            failed += 1
            print(f"✗ '{user_input[:40]}...' -> Error: {e}")
        print()
    
    print(f"Results: {passed}/{passed+failed} passed\n")
    return failed == 0


if __name__ == "__main__":
    print("Katy Tool Calling System Integration Tests\n")
    
    all_passed = True
    all_passed &= test_intent_classifier()
    all_passed &= test_tool_gate()
    all_passed &= test_tool_dispatcher()
    
    print("=" * 50)
    if all_passed:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed.")
        sys.exit(1)
