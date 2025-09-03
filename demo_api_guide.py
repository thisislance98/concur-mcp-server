#!/usr/bin/env python3
"""
Demo script showing the get_concur_api_guide tool in action
"""

from concur_expense_tools import ConcurAPITopic, _generate_authentication_guide, _generate_expenses_guide, _generate_reports_guide

def demo_authentication_guide():
    """Demo the authentication guide."""
    print("🔐 CONCUR API AUTHENTICATION GUIDE")
    print("=" * 50)
    
    guide = _generate_authentication_guide()
    print(f"Title: {guide['title']}")
    print(f"Overview: {guide['overview']}\n")
    
    print("📋 STEP-BY-STEP INSTRUCTIONS:")
    for step in guide['how_to']['steps']:
        print(f"\n{step['step']}. {step['title']}")
        print(f"   {step['description']}")
        print(f"   Code:")
        print("   " + "\n   ".join(step['code'].split('\n')[:5]) + "...")
    
    print(f"\n📚 EXAMPLES ({len(guide['examples'])}):")
    for example in guide['examples']:
        print(f"\n• {example['title']}")
        print(f"  {example['description']}")
        print("  Code preview:")
        print("  " + "\n  ".join(example['code'].split('\n')[:3]) + "...")

def demo_expenses_guide():
    """Demo the expenses guide."""
    print("\n\n💰 CONCUR EXPENSE MANAGEMENT GUIDE")
    print("=" * 50)
    
    guide = _generate_expenses_guide()
    print(f"Title: {guide['title']}")
    print(f"Overview: {guide['overview']}\n")
    
    print("📝 KEY EXAMPLES:")
    for i, example in enumerate(guide['examples'][:3], 1):  # Show first 3
        print(f"\n{i}. {example['title']}")
        print(f"   {example['description']}")
        
        if 'dependencies' in example:
            print("   Dependencies:")
            for dep, desc in example['dependencies'].items():
                print(f"   - {dep}: {desc}")
        
        print("   Code snippet:")
        print("   " + "\n   ".join(example['code'].split('\n')[:4]) + "...")

def demo_reports_guide():
    """Demo the reports guide."""
    print("\n\n📊 CONCUR REPORTS MANAGEMENT GUIDE")
    print("=" * 50)
    
    guide = _generate_reports_guide()
    print(f"Title: {guide['title']}")
    print(f"Overview: {guide['overview']}\n")
    
    print("🔧 HOW-TO STEPS:")
    for step in guide['how_to']['steps']:
        print(f"\n• {step['title']}")
        print(f"  {step['description']}")
        print("  Code:")
        print("  " + "\n  ".join(step['code'].split('\n')[:3]) + "...")

def demo_available_topics():
    """Show all available topics."""
    print("\n\n📖 AVAILABLE DOCUMENTATION TOPICS")
    print("=" * 50)
    
    print("Currently implemented:")
    implemented = [
        (ConcurAPITopic.AUTHENTICATION, "OAuth setup and token management"),
        (ConcurAPITopic.EXPENSES, "Creating and managing expense entries (basic + advanced)"),
        (ConcurAPITopic.REPORTS, "Managing expense reports (basic + advanced)"),
    ]
    
    for topic, description in implemented:
        print(f"✅ {topic.value}: {description}")
    
    print("\nPlanned for future implementation:")
    planned = [
        (ConcurAPITopic.QUICK_START, "Quick start guide"),
        (ConcurAPITopic.EXPENSE_TYPES, "Working with expense types"),
        (ConcurAPITopic.PAYMENT_TYPES, "Payment type management"),
        (ConcurAPITopic.ERROR_HANDLING, "Error handling patterns"),
        (ConcurAPITopic.BEST_PRACTICES, "Best practices and tips"),
    ]
    
    for topic, description in planned:
        print(f"⏳ {topic.value}: {description}")

def demo_tool_usage():
    """Show how to use the tool."""
    print("\n\n🛠️  HOW TO USE THE TOOL")
    print("=" * 50)
    
    print("The get_concur_api_guide tool can be called with:")
    print()
    print("Parameters:")
    print("- topic: ConcurAPITopic enum value")
    print("- include_examples: bool (default True)")
    print("- include_howto: bool (default True)")
    print()
    print("Example calls:")
    print("1. get_concur_api_guide(topic=ConcurAPITopic.AUTHENTICATION)")
    print("2. get_concur_api_guide(topic=ConcurAPITopic.EXPENSES, include_howto=False)")
    print("3. get_concur_api_guide(topic=ConcurAPITopic.REPORTS, include_examples=False)")
    print()
    print("Returns:")
    print("- success: bool")
    print("- topic: str")
    print("- title: str")
    print("- overview: str")
    print("- how_to: dict (if include_howto=True)")
    print("- examples: list (if include_examples=True)")
    print("- dependencies: dict")
    print("- api_endpoints: dict")
    print("- message: str")

if __name__ == "__main__":
    print("🚀 CONCUR API DOCUMENTATION TOOL DEMO")
    print("=" * 60)
    print("This demo shows the comprehensive API documentation and")
    print("code examples provided by the get_concur_api_guide tool.")
    print("All examples show direct HTTP requests using Python requests library.")
    
    demo_authentication_guide()
    demo_expenses_guide()
    demo_reports_guide()
    demo_available_topics()
    demo_tool_usage()
    
    print("\n\n🎉 DEMO COMPLETE!")
    print("The get_concur_api_guide tool provides comprehensive,")
    print("practical documentation with real working code examples!")
