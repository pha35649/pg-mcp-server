# server/tools/connection.py
from server.config import mcp
from mcp.server.fastmcp import Context
from server.logging_config import get_logger
from urllib.parse import quote_plus

logger = get_logger("pg-mcp.tools.connection")

def register_connection_tools():
    """Register the database connection tools with the MCP server."""
    logger.debug("Registering database connection tools")
    
    @mcp.tool()
    async def connect(username: str, password: str, *, ctx: Context):
        """
        Register a database connection string and return its connection ID.
        
        Args:
            username: username to connect to bioon data, string (required)
            password: password to connect to bioon data, string (required)

            ctx: Request context (injected by the framework)
            
        Returns:
            Dictionary containing the connection ID
        """
        # Get database from context
        # db = ctx.request_context.lifespan_context.get("db")
        db = mcp.state["db"]
        user_enc = quote_plus(username)
        pwd_enc  = quote_plus(password)

        connection_string = f"postgresql://{user_enc}:{pwd_enc}@db.ggezwajibfiviygxgkot.supabase.co:5432/postgres?sslmode=require"

        # Register the connection to get a connection ID
        conn_id = db.register_connection(connection_string)
        
        # Return the connection ID
        logger.info(f"Registered database connection with ID: {conn_id}")
        return {"conn_id": conn_id}
    
    @mcp.tool()
    async def disconnect(conn_id: str, *, ctx: Context):
        """
        Close a specific database connection and remove it from the pool.
        
        Args:
            conn_id: Connection ID to disconnect (required)
            ctx: Request context (injected by the framework)
            
        Returns:
            Dictionary indicating success status
        """
        # Get database from context
        # db = ctx.request_context.lifespan_context.get("db")
        db = mcp.state["db"]
        
        # Check if the connection exists
        if conn_id not in db._connection_map:
            logger.warning(f"Attempted to disconnect unknown connection ID: {conn_id}")
            return {"success": False, "error": "Unknown connection ID"}
        
        # Close the connection pool
        try:
            await db.close(conn_id)
            # Also remove from the connection mappings
            connection_string = db._connection_map.pop(conn_id, None)
            if connection_string in db._reverse_map:
                del db._reverse_map[connection_string]
            logger.info(f"Successfully disconnected database connection with ID: {conn_id}")
            return {"success": True}
        except Exception as e:
            logger.error(f"Error disconnecting connection {conn_id}: {e}")
            return {"success": False, "error": str(e)}
