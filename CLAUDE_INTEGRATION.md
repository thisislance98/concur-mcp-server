# Using Your Concur MCP Server with Claude Desktop

## 🎯 **Overview**

Your Concur MCP server can be integrated directly with Claude Desktop, allowing you to ask Claude to retrieve and analyze your expense reports using natural language!

## 🔧 **Setup Methods**

### **Method 1: FastMCP Auto-Installation (Recommended)**

The easiest way to integrate with Claude Desktop:

```bash
# Navigate to your project directory
cd /Users/I850333/projects/experiments/concur_mcp

# Activate your virtual environment
source venv/bin/activate

# Install your server with Claude Desktop
fastmcp install claude-desktop concur_mcp_server.py --with requests --with python-dotenv
```

This automatically:
- ✅ Configures Claude Desktop to use your server
- ✅ Manages dependencies (requests, python-dotenv)
- ✅ Sets up the MCP connection
- ✅ Registers your tools with Claude

### **Method 2: Manual Configuration**

If you prefer manual setup or need custom configuration:

1. **Find Claude Desktop config file:**
   ```bash
   # On macOS
   ~/Library/Application Support/Claude/claude_desktop_config.json
   
   # On Windows
   %APPDATA%\Claude\claude_desktop_config.json
   
   # On Linux
   ~/.config/Claude/claude_desktop_config.json
   ```

2. **Add your MCP server configuration:**
   ```json
   {
     "mcpServers": {
       "concur-reports": {
         "command": "python",
         "args": ["/Users/I850333/projects/experiments/concur_mcp/concur_mcp_server.py"],
         "env": {
           "CONCUR_CLIENT_ID": "your_client_id",
           "CONCUR_CLIENT_SECRET": "your_client_secret",
           "CONCUR_USERNAME": "your_username", 
           "CONCUR_PASSWORD": "your_password"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

## 💬 **How to Use with Claude**

Once configured, you can interact with your Concur data using natural language:

### **Example Conversations:**

**📋 List Reports:**
```
You: "Show me my recent expense reports"
Claude: [Uses list_concur_reports tool]
"Here are your recent expense reports:
1. Test - $2,323.00 (Submitted & Pending Approval)
2. test - $27.00 (Submitted & Pending Approval)  
3. parking - $37.00 (Submitted & Pending Approval)"
```

**🔍 Get Report Details:**
```
You: "Get details for the Test report"
Claude: [Uses get_concur_report_details tool]
"Here are the details for your Test report:
- Amount: $2,323.00
- Status: Submitted & Pending Approval
- Created: [date]
- Purpose: [business purpose]"
```

**🧪 Test Connection:**
```
You: "Check if my Concur connection is working"
Claude: [Uses test_concur_connection tool]
"Your Concur connection is working properly. 
Successfully authenticated with token length: 1648 characters"
```

**📊 Analyze Data:**
```
You: "What's the total amount of my pending expense reports?"
Claude: [Uses list_concur_reports, then analyzes the data]
"Based on your expense reports, you have $2,387.00 in pending expenses across 3 reports"
```

## 🛠️ **Available Tools in Claude**

When your MCP server is connected, Claude will have access to:

1. **`list_concur_reports`** - Retrieve your expense reports
2. **`get_concur_report_details`** - Get detailed info about specific reports  
3. **`test_concur_connection`** - Verify API connectivity

## 🔐 **Security Considerations**

### **Environment Variables (Recommended):**
```bash
# Create a .env file in your project directory
CONCUR_CLIENT_ID=your_client_id
CONCUR_CLIENT_SECRET=your_client_secret
CONCUR_USERNAME=your_username
CONCUR_PASSWORD=your_password
```

### **Claude Desktop Config (Alternative):**
```json
{
  "mcpServers": {
    "concur-reports": {
      "command": "python",
      "args": ["/path/to/your/concur_mcp_server.py"],
      "env": {
        "CONCUR_CLIENT_ID": "${CONCUR_CLIENT_ID}",
        "CONCUR_CLIENT_SECRET": "${CONCUR_CLIENT_SECRET}",
        "CONCUR_USERNAME": "${CONCUR_USERNAME}",
        "CONCUR_PASSWORD": "${CONCUR_PASSWORD}"
      }
    }
  }
}
```

## 🧪 **Testing the Integration**

1. **Start Claude Desktop**
2. **Look for MCP indicator** - You should see your server listed
3. **Test with a simple query:**
   ```
   "Can you check my Concur connection?"
   ```
4. **If working, try retrieving reports:**
   ```
   "Show me my expense reports"
   ```

## 🚨 **Troubleshooting**

### **Server Not Appearing in Claude:**
- ✅ Check Claude Desktop config file syntax (valid JSON)
- ✅ Verify file paths are absolute, not relative
- ✅ Ensure Python environment has required dependencies
- ✅ Restart Claude Desktop after config changes

### **Authentication Errors:**
- ✅ Verify environment variables are set correctly
- ✅ Test credentials with: `python simple_test.py`
- ✅ Check Concur API permissions

### **Connection Issues:**
- ✅ Ensure your virtual environment is activated
- ✅ Test server independently: `python concur_mcp_server.py`
- ✅ Check network connectivity to Concur API

## 💡 **Pro Tips**

### **Natural Language Queries:**
```
✅ "What are my highest expense reports this month?"
✅ "Show me all reports that need approval"
✅ "How much have I spent on parking expenses?"
✅ "Which reports were submitted but not approved?"
```

### **Data Analysis:**
```
✅ "Create a summary of my expense categories"
✅ "Compare this month's expenses to last month"
✅ "Find any duplicate or unusual expenses"
✅ "Generate a report for my manager"
```

### **Workflow Automation:**
```
✅ "Check for any reports that need my attention"
✅ "Remind me about pending expense approvals"
✅ "Help me categorize these expenses"
```

## 🎯 **What This Enables**

With your Concur MCP server integrated into Claude Desktop, you can:

- 🗣️ **Ask questions** about your expenses in natural language
- 📊 **Analyze spending patterns** with Claude's analytical capabilities
- 🔍 **Search and filter** reports using conversational queries
- 📈 **Generate insights** and summaries of your expense data
- 🤖 **Automate workflows** around expense management
- 📝 **Create reports** and documentation based on your data

Your Concur data becomes as easy to access as having a conversation with Claude! 🚀
