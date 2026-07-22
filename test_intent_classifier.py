# -*- coding: utf-8 -*-
"""Test IntentClassifier directly."""

from agent_reach.tool_dispatcher import IntentClassifier

if __name__ == "__main__":
    ic = IntentClassifier()
    
    test_cases = [
        ("busca en Twitter qué dicen sobre Python 4", "search_twitter"),
        ("lee esta página https://docs.djangoproject.com/en/5.2/ref/middleware/", "read_web"),
        ("busca en YouTube tutoriales de Python", "search_youtube"),
        ("lee https://github.com/nicobailon/mcporter", "read_web"),
        ("qué hay de nuevo en https://example.com", "unknown"),
        ("busca tutoriales de CORS en Django", "search_youtube"),
        ("revisa el RSS de Hacker News", "unknown"),  # This should probably match parse_rss
        ("clima en Barcelona", "weather"),
        ("buscar en mi memoria qué hice ayer", "memory_search"),
    ]
    
    all_passed = True
    for test_input, expected_intent in test_cases:
        intent, channel, action, query = ic.classify(test_input)
        status = "✓" if intent == expected_intent else "✗"
        print(f"{status} Input: {test_input}")
        print(f"  Expected: {expected_intent}")
        print(f"  Got: {intent}")
        if intent == expected_intent:
            print(f"  Query: {query}")
        print()
        if intent != expected_intent:
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("All tests passed!")
    else:
        print("Some tests failed.")
        print("\nSuggested fixes:")
        print("1. Add pattern for 'revisa el RSS' to parse_rss")
        print("2. Add pattern for 'qué hay de nuevo en' URLs")
        print("3. Fix YouTube query extraction (currently getting 'n' from 'en YouTube tutoriales de Python')")