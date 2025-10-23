"""
risk_manager LangGraph Agent
"""

from typing import Dict, Any

from .config import Config
from .graph import create_graph

class LangGraphAgent:
    """
    Main LangGraph agent class that orchestrates the graph execution
    """
    
    def __init__(self, config: Config = None, graph = None):
        """
        Initialize the LangGraph agent
        
        Args:
            config: Configuration object (optional, will create default if not provided)
            graph: Pre-initialized graph (optional, will create from config if not provided)
        """
        self.config = config or Config()
        self.graph = graph or create_graph(self.config)
    
    async def process(self, input_data: str, model_type: str = "vanilla") -> Any:
        """
        Process input through the LangGraph
        
        Args:
            input_data: Input data to process
            model_type: Type of model execution ("vanilla", "full", or "online")
            
        Returns:
            Processed result from the graph
            
        Raises:
            Exception: If processing fails
        """
        try:
            # Pass model_type through the input data if it's a dict
            if isinstance(input_data, dict):
                input_data = {**input_data, "model_type": model_type}
            else:
                # For string inputs, wrap in dict
                input_data = {"input": str(input_data), "model_type": model_type}
            
            result = await self.graph.execute(input_data)
            return result
        except Exception as e:
            print(f"❌ Error processing request: {e}")
            raise
    
    def get_graph_info(self) -> Dict[str, Any]:
        """
        Get information about the graph structure
        
        Returns:
            Dictionary containing graph structure information
        """
        try:
            return self.graph.get_graph_info()
        except Exception as e:
            return {
                "error": f"Could not retrieve graph info: {str(e)}",
                "agent": "risk_manager",
                "framework": "langgraph"
            }
    
    def get_agent_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this agent
        
        Returns:
            Dictionary containing agent metadata
        """
        return {
            "name": "risk_manager",
            "framework": "langgraph",
            "language": "python",
            "runtime": "fastapi",
            "version": "1.0.0"
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the agent
        
        Returns:
            Dictionary containing health status
        """
        try:
            # Test basic functionality
            graph_info = self.get_graph_info()
            
            return {
                "status": "healthy",
                "agent": "risk_manager",
                "framework": "langgraph",
                "graph_available": "error" not in graph_info,
                "config_loaded": self.config is not None
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "agent": "risk_manager",
                "framework": "langgraph",
                "error": str(e)
            }
