# server/prompts/natural_language.py
import importlib.resources
import jinja2
from server.config import mcp
from server.logging_config import get_logger
from mcp.server.fastmcp.prompts import base

logger = get_logger("pg-mcp.prompts.natural_language")

# Set up Jinja2 template environment using importlib.resources
template_env = jinja2.Environment(
    loader=jinja2.FunctionLoader(lambda name: 
        importlib.resources.read_text('server.prompts.templates', name)
    )
)

def register_natural_language_prompts():
    """Register prompts with the MCP server."""
    logger.debug("Registering natural language to SQL prompts")

    @mcp.prompt()
    async def start_bioon():
        """
        Prompt to guide AI agents in connecting to bioon ecosystem.
        """        
        # Render the prompt template     
        prompt_template = template_env.get_template("start_bioon.md.jinja2")
        prompt_text = prompt_template.render()
        
        return [base.UserMessage(prompt_text)]
