#!/usr/bin/env python3
"""
Deployment-ready Concur MCP Server
Minimal version optimized for deployment environments
"""

import os
import sys
import logging

# Simple logging setup
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main deployment function"""
    logger.info("🚀 Concur MCP Server - Deployment Version")
    
    # Check critical environment variables
    required_vars = ["CONCUR_CLIENT_ID", "CONCUR_CLIENT_SECRET", "CONCUR_USERNAME", "CONCUR_PASSWORD"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        logger.error(f"❌ Missing environment variables: {', '.join(missing)}")
        logger.error("Set these in your deployment platform's environment configuration")
        return False
    
    logger.info("✅ Environment variables configured")
    
    # Import and run the robust server
    try:
        # Try to import the robust server
        import concur_mcp_server_robust
        logger.info("✅ Using robust server implementation")
        
        # Run the main function
        return concur_mcp_server_robust.main()
        
    except ImportError:
        logger.warning("⚠️  Robust server not available, falling back to basic server")
        
        # Fallback to basic server
        try:
            import concur_mcp_server
            logger.info("✅ Using basic server implementation")
            
            # The basic server runs automatically when imported as main
            return True
            
        except ImportError as e:
            logger.error(f"❌ Could not import any server implementation: {e}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            logger.error("❌ Deployment failed")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("👋 Server stopped")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal deployment error: {e}")
        sys.exit(1)
