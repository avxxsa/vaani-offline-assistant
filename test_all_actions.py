#!/usr/bin/env python
"""Test script to verify all Vaani assistant actions work"""

from brain.brain import process_text
from brain.memory import list_todos, get_journal
import sys

def test_actions():
    """Test all action types"""
    
    test_cases = [
        ("नमस्ते", "Nepali greeting"),
        ("what is the time", "English time query"),
        ("add task buy milk", "Add todo"),
        ("show my tasks", "List todos"),
        ("what is the date", "Date query"),
        ("hello there", "Simple greeting fallback"),
        ("who are you", "Identity query"),
    ]
    
    print("=" * 60)
    print("VAANI ASSISTANT - ACTION TEST SUITE")
    print("=" * 60)
    
    results = {"passed": 0, "failed": 0, "errors": []}
    
    for user_input, description in test_cases:
        try:
            print(f"\n▶ Testing: {description}")
            print(f"  Input: '{user_input}'")
            response = process_text(user_input)
            
            if response and response != "__EXIT__":
                print(f"  ✓ Response: {response[:70]}{'...' if len(response) > 70 else ''}")
                results["passed"] += 1
            else:
                print(f"  ⚠ No response generated")
                results["failed"] += 1
                
        except Exception as e:
            print(f"  ✗ ERROR: {str(e)[:60]}")
            results["errors"].append((description, str(e)))
            results["failed"] += 1
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✓ Passed: {results['passed']}")
    print(f"✗ Failed: {results['failed']}")
    
    if results["errors"]:
        print(f"\nErrors ({len(results['errors'])}):")
        for desc, error in results["errors"]:
            print(f"  - {desc}: {error[:50]}")
    
    # Check persistent storage
    print("\n" + "=" * 60)
    print("STORAGE STATUS")
    print("=" * 60)
    todos = list_todos()
    print(f"  Todos saved: {len(todos)}")
    if todos:
        for i, todo in enumerate(todos[:3], 1):
            print(f"    {i}. {todo}")
    
    return results["failed"] == 0

if __name__ == "__main__":
    success = test_actions()
    sys.exit(0 if success else 1)
