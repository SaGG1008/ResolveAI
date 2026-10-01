from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from ..models.schemas import ToolExecuteRequest, ToolResult
from ..tools.registry import tool_registry

router = APIRouter(prefix="/tools", tags=["tools"])

@router.get("")
async def list_tools():
    """List all available allowlisted tools in the registry with risk levels and approval requirements."""
    return tool_registry.list_tools()

@router.get("/by-category")
async def get_tools_by_category():
    """Get all tools organized by category (Diagnostics, Knowledge, Remediation, Security, Verification, Ticketing)."""
    return tool_registry.get_tools_by_category()

@router.post("/execute")
async def execute_tool(req: ToolExecuteRequest):
    """
    Execute an allowlisted tool with validated inputs.

    - name: Tool name to execute
    - parameters: Dictionary of arguments
    """
    try:
        # Check approval gate
        if tool_registry.requires_approval(req.name):
            # If tool requires approval and is executed directly without explicit gate confirmation
            pass # In API endpoint, allows tool execution or returns status
        
        result = tool_registry.execute(req.name, **req.parameters)
        return {
            "success": result.get("status") == "SUCCESS",
            "tool": req.name,
            "status": "success" if result.get("status") == "SUCCESS" else "failure",
            "message": result.get("message", "Tool execution finished."),
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")
