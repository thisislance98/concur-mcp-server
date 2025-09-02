#!/usr/bin/env python3
"""
Script to update Claude Desktop configuration with Concur credentials
"""

import json
import os
from pathlib import Path

def update_claude_config():
    """Update Claude Desktop config with Concur MCP server configuration."""
    
    # Path to Claude Desktop config
    config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    
    # Read existing config
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Claude Desktop config file not found. Creating new one.")
        config = {"mcpServers": {}}
    except json.JSONDecodeError as e:
        print(f"Error reading config file: {e}")
        return False
    
    # Ensure mcpServers exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Add the new Concur reports server configuration
    config["mcpServers"]["concur-reports"] = {
        "command": "python",
        "args": ["/Users/I850333/projects/experiments/concur_mcp/concur_mcp_server.py"],
        "env": {
            "CONCUR_CLIENT_ID": "486c51f1-1d22-41cf-b743-ca90fd4279d4",
            "CONCUR_CLIENT_SECRET": "3b615a2e-d467-40be-83c7-3e6286625813",
            "CONCUR_USERNAME": "user11@p10005178e93.com",
            "CONCUR_PASSWORD": "password12"  # Note: You may need to provide the complete password
        }
    }
    
    # Write updated config
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Successfully updated Claude Desktop configuration!")
        print("📍 Added 'concur-reports' MCP server")
        print("🔐 Credentials have been configured")
        print("\n⚠️  Please verify your CONCUR_PASSWORD is complete")
        print("🔄 Restart Claude Desktop to apply changes")
        return True
    except Exception as e:
        print(f"❌ Error writing config file: {e}")
        return False

if __name__ == "__main__":
    success = update_claude_config()
    if success:
        print("\n🎉 Configuration updated successfully!")
        print("Next steps:")
        print("1. Restart Claude Desktop")
        print("2. Ask Claude: 'Show me my Concur expense reports'")
    else:
        print("\n❌ Configuration update failed!")

