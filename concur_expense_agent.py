#!/usr/bin/env python3
"""
Concur Expense Agent using fast-agent
Based on the generated agent.py structure
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create the FastAgent application
fast = FastAgent("Concur Expense Agent")

# Define the Concur expense management agent
@fast.agent(
    name="ConcurExpenseAgent",
    servers=["concur_reports"],  # Uses our configured MCP server
    instruction="""You are an intelligent expense management assistant that helps users analyze and manage their Concur expense reports.

You have access to tools that can:
- Retrieve lists of expense reports from Concur
- Get detailed information about specific reports
- Test API connectivity with Concur

When analyzing expenses, provide insights about:
- Spending patterns and trends
- Report statuses and approval workflows
- Total amounts and categorization
- Any unusual or noteworthy expenses

Always be helpful, accurate, and provide actionable insights about expense management."""
)
async def concur_agent():
    """
    Interactive Concur expense management agent.
    
    This agent can help you:
    - View and analyze your expense reports
    - Check report statuses and approvals
    - Get insights into spending patterns
    - Manage expense workflows
    """
    async with fast.run() as agent:
        print("🎉 Concur Expense Agent is ready!")
        print("Ask me about your expense reports, spending analysis, or report management.")
        print("Examples:")
        print("  - 'Show me my recent expense reports'")
        print("  - 'What reports need approval?'")
        print("  - 'Analyze my spending patterns'")
        print("  - 'Test my Concur connection'")
        print()
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(concur_agent())
