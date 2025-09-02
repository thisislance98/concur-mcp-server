# Using Your Concur MCP Server with fast-agent

## 🎯 Overview

[fast-agent](https://fast-agent.ai/mcp/#adding-a-stdio-server) provides advanced MCP server management and agent orchestration capabilities. Your Concur MCP server can be integrated with fast-agent for more sophisticated expense management workflows.

## 📋 Setup Instructions

### Step 1: Install fast-agent
```bash
pip install fast-agent
```

### Step 2: Configuration File
Your `fastagent.config.yaml` is already configured:

```yaml
mcp:
  concur_reports:
    command: "python"
    args: ["/Users/I850333/projects/experiments/concur_mcp/concur_mcp_server.py"]
    env:
      CONCUR_CLIENT_ID: "486c51f1-1d22-41cf-b743-ca90fd4279d4"
      CONCUR_CLIENT_SECRET: "3b615a2e-d467-40be-83c7-3e6286625813"
      CONCUR_USERNAME: "user11@p10005178e93.com"
      CONCUR_PASSWORD: "password12"
```

### Step 3: Create Your Agent
Use the example in `concur_agent.py`:

```python
import fast

@fast.agent(
    name="ConcurExpenseAgent",
    servers=["concur_reports"],
    instruction="You are an expense management assistant..."
)
def concur_expense_agent():
    pass
```

## 🚀 Usage Examples

### Basic Usage
```python
from concur_agent import concur_expense_agent

# Analyze expenses
result = concur_expense_agent("Show me my expense reports and analyze spending patterns")

# Check pending reports
result = concur_expense_agent("What reports need approval?")

# Get specific report details
result = concur_expense_agent("Tell me about my Test expense report")
```

### Advanced Filtering
According to the [fast-agent documentation](https://fast-agent.ai/mcp/#adding-a-stdio-server), you can filter which tools the agent uses:

```python
@fast.agent(
    name="ConcurExpenseAgent",
    servers=["concur_reports"],
    tools={
        "concur_reports": ["list_concur_reports", "test_concur_connection"]
    }  # Only use specific tools
)
def filtered_concur_agent():
    pass
```

## 💡 Benefits of fast-agent vs Claude Desktop

| Feature | Claude Desktop | fast-agent |
|---------|----------------|------------|
| **Agent Orchestration** | ❌ Basic chat | ✅ Advanced workflows |
| **MCP Server Management** | ❌ Manual config | ✅ Automated management |
| **Tool Filtering** | ❌ All tools | ✅ Selective tool access |
| **Multi-Server Support** | ✅ Yes | ✅ Advanced integration |
| **Sampling Support** | ❌ No | ✅ Yes |
| **Elicitations** | ❌ No | ✅ Forms/Auto-cancel |
| **Workflow Automation** | ❌ Limited | ✅ Full automation |

## 🔧 Advanced Configuration Options

Based on the [fast-agent MCP documentation](https://fast-agent.ai/mcp/#adding-a-stdio-server), you can add:

### Implementation Spoofing
```yaml
mcp:
  concur_reports:
    command: "python"
    args: ["/path/to/concur_mcp_server.py"]
    implementation:
      name: "concur-expense-client"
      version: "1.0.0"
```

### Roots (File System Access)
```yaml
mcp:
  concur_reports:
    command: "python"
    args: ["/path/to/concur_mcp_server.py"]
    roots:
      uri: "file:///path/to/expense/files"
      name: "Expense Documents"
```

### Sampling (AI-powered responses)
```yaml
mcp:
  concur_reports:
    command: "python"
    args: ["/path/to/concur_mcp_server.py"]
    sampling:
      model: "openai.gpt-4"
```

## 🧪 Testing Your Setup

1. **Test the configuration:**
   ```bash
   cd /Users/I850333/projects/experiments/concur_mcp
   python concur_agent.py
   ```

2. **Verify MCP server works:**
   ```bash
   python simple_test.py
   ```

3. **Run the agent:**
   ```python
   from concur_agent import concur_expense_agent
   result = concur_expense_agent("Test my Concur connection")
   print(result)
   ```

## 🎯 Use Cases

### Expense Analysis Workflows
```python
# Multi-step expense analysis
result = concur_expense_agent("""
1. Test my Concur connection
2. Get all my expense reports
3. Analyze spending patterns by category
4. Identify any reports that need attention
5. Provide a summary with recommendations
""")
```

### Automated Reporting
```python
# Generate weekly expense report
weekly_report = concur_expense_agent("""
Create a weekly expense summary including:
- Total expenses this week
- Breakdown by category
- Status of pending reports
- Any unusual expenses requiring review
""")
```

### Compliance Checking
```python
# Check for compliance issues
compliance_check = concur_expense_agent("""
Review my expense reports for:
- Missing receipts or documentation
- Expenses exceeding policy limits
- Reports pending approval too long
- Duplicate or suspicious expenses
""")
```

## 🚨 Troubleshooting

### Configuration Issues
- Ensure `fastagent.config.yaml` is in your working directory
- Verify Python path is correct in the config
- Check that all environment variables are set

### Connection Problems
- Test your MCP server independently: `python simple_test.py`
- Verify Concur credentials are valid
- Check network connectivity

### fast-agent Issues
- Install latest version: `pip install --upgrade fast-agent`
- Check fast-agent documentation: https://fast-agent.ai/
- Verify YAML syntax in config file

## 🎉 You're Ready!

Your Concur MCP server is now configured to work with fast-agent, giving you powerful expense management automation capabilities!

**Next Steps:**
1. Install fast-agent: `pip install fast-agent`
2. Test the configuration: `python concur_agent.py`
3. Create custom expense management workflows
4. Integrate with other MCP servers for comprehensive business automation
