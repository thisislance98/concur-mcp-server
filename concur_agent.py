#!/usr/bin/env python3
"""
Complete example of using Concur MCP server with fast-agent
Based on: https://fast-agent.ai/mcp/#adding-a-stdio-server
"""

# This demonstrates how to use fast-agent with your Concur MCP server
# First install fast-agent: pip install fast-agent

try:
    import fast
    FAST_AGENT_AVAILABLE = True
except ImportError:
    FAST_AGENT_AVAILABLE = False
    print("⚠️  fast-agent not installed. Install with: pip install fast-agent")

if FAST_AGENT_AVAILABLE:
    @fast.agent(
        name="ConcurExpenseAgent",
        servers=["concur_reports"],  # Uses the server defined in fastagent.config.yaml
        instruction="""You are an intelligent expense management assistant that helps users analyze and manage their Concur expense reports. 

You have access to tools that can:
- Retrieve lists of expense reports
- Get detailed information about specific reports
- Test API connectivity

When analyzing expenses, provide insights about:
- Spending patterns and trends
- Report statuses and approval workflows
- Total amounts and categorization
- Any unusual or noteworthy expenses

Always be helpful, accurate, and provide actionable insights.""",
        # Optional: Filter which tools to use from the MCP server
        tools={
            "concur_reports": ["list_concur_reports", "get_concur_report_details", "test_concur_connection"]
        }
    )
    def concur_expense_agent():
        """
        An AI agent that can access and analyze Concur expense reports.
        
        This agent uses the concur_reports MCP server to:
        - List expense reports
        - Get detailed report information
        - Test API connectivity
        - Analyze spending patterns
        - Provide expense insights
        """
        pass

    # Example usage functions
    def analyze_expenses():
        """Example: Analyze all expense reports"""
        return concur_expense_agent("Show me all my expense reports and provide an analysis of my spending patterns")

    def check_pending_reports():
        """Example: Check for reports needing attention"""
        return concur_expense_agent("What expense reports do I have that need approval or attention?")

    def expense_summary():
        """Example: Get expense summary"""
        return concur_expense_agent("Give me a summary of my total expenses and break them down by report")

    def test_connection():
        """Example: Test Concur connection"""
        return concur_expense_agent("Test my connection to Concur and let me know if everything is working")

else:
    # Fallback functions when fast-agent is not available
    def analyze_expenses():
        return "Please install fast-agent first: pip install fast-agent"
    
    def check_pending_reports():
        return "Please install fast-agent first: pip install fast-agent"
    
    def expense_summary():
        return "Please install fast-agent first: pip install fast-agent"
    
    def test_connection():
        return "Please install fast-agent first: pip install fast-agent"

def main():
    """Main function to demonstrate the agent capabilities"""
    print("🤖 Concur Expense Agent with fast-agent")
    print("=" * 50)
    
    if not FAST_AGENT_AVAILABLE:
        print("❌ fast-agent not available")
        print("📦 Install with: pip install fast-agent")
        print("📁 Configuration ready in: fastagent.config.yaml")
        return
    
    print("✅ fast-agent available")
    print("📁 Configuration: fastagent.config.yaml")
    print("🔧 MCP Server: concur_reports")
    print()
    
    # Example interactions
    examples = [
        ("Test Connection", "concur_expense_agent('Test my Concur connection')"),
        ("List Reports", "concur_expense_agent('Show me my expense reports')"),
        ("Analyze Spending", "concur_expense_agent('Analyze my spending patterns')"),
        ("Check Status", "concur_expense_agent('What reports need my attention?')"),
    ]
    
    print("💡 Example agent interactions:")
    for title, code in examples:
        print(f"   {title}: {code}")
    
    print()
    print("🚀 To use the agent:")
    print("   1. Ensure fastagent.config.yaml is in your working directory")
    print("   2. Import this module: from concur_agent import concur_expense_agent")
    print("   3. Call the agent: result = concur_expense_agent('your question')")

if __name__ == "__main__":
    main()
