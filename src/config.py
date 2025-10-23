"""
Simple configuration for risk_manager
Only includes what's actually needed for the agent to run.
"""

import os
from typing import Dict, Any, List

class Config:
    """
    Simple configuration class - only essential properties.
    The generator handles folder/file structure based on JSON config.
    """
    
    def __init__(self) -> None:
        # Basic project info
        self.project_name: str = "risk_manager"
        self.framework: str = "langgraph"
        
        # Runtime info
        self.runtime_type: str = "fastapi"
        self.port: int = 8000
        
        # Graph configuration for complex routing
        # This is the primary configuration - users can modify this for parallel execution, conditional routing, etc.
        # The finalizer node is ALWAYS included to enable parallelization and data merging
        self.graph_config = {
            "nodes": {
                "behavioral_analizer": {"node_name": "behavioral_analizer"},
                "decision_aggregator": {"node_name": "decision_aggregator"},
                "geographic_analizer": {"node_name": "geographic_analizer"},
                "merchant_risk_analizer": {"node_name": "merchant_risk_analizer"},
                "parse_final_decision": {"node_name": "parse_final_decision"},
                "pattern_detector": {"node_name": "pattern_detector"},
                "velocity_checker": {"node_name": "velocity_checker"},
                "finalizer": {"node_name": "finalizer", "type": "finalizer", "description": "Merges results from parallel execution"}
            },
            "edges": [
                {"from": "START", "to": "behavioral_analizer"},
                {"from": "behavioral_analizer", "to": "decision_aggregator"},
                {"from": "decision_aggregator", "to": "geographic_analizer"},
                {"from": "geographic_analizer", "to": "merchant_risk_analizer"},
                {"from": "merchant_risk_analizer", "to": "parse_final_decision"},
                {"from": "parse_final_decision", "to": "pattern_detector"},
                {"from": "pattern_detector", "to": "velocity_checker"}, {"from": "velocity_checker", "to": "finalizer"},
                {"from": "finalizer", "to": "END"}
            ],
            "conditional_edges": []
        }
        
        # Agent stages (kept for backward compatibility - derived from graph_config)
        self.agent_stages: List[str] = list(self.graph_config["nodes"].keys())
        
        # Example parallel configuration (commented out - users can uncomment and modify):
        # self.graph_config = {
        #     "nodes": {
        #         "analyzer": {"node_name": "analyzer"},
        #         "tool1": {"node_name": "tool1"},
        #         "tool2": {"node_name": "tool2"},
        #         "finalizer": {"node_name": "finalizer"}
        #     },
        #     "edges": [
        #         {"from": "START", "to": "analyzer"},
        #         {"from": "analyzer", "to": "tool1"},      # Parallel execution
        #         {"from": "analyzer", "to": "tool2"},      # Parallel execution
        #         {"from": "tool1", "to": "finalizer"},     # LangGraph auto-merges results
        #         {"from": "tool2", "to": "finalizer"},     # LangGraph auto-merges results
        #         {"from": "finalizer", "to": "END"}
        #     ],
        #     "conditional_edges": []
        # }
        
        # Environment variables (for actual runtime configuration)
        self.handit_api_key = os.getenv("HANDIT_API_KEY")
        self.model_provider = os.getenv("MODEL_PROVIDER", "mock")
        self.model_name = os.getenv("MODEL_NAME", "mock-llm")
    
    def get_model_config(self, node_name: str = None) -> Dict[str, Any]:
        """
        Get model configuration for a node.
        
        Args:
            node_name: Optional node name for node-specific config
            
        Returns:
            Model configuration
        """
        return {
            "provider": self.model_provider,
            "name": self.model_name
        }
    
    def get_node_model_config(self, node_name: str = None) -> Dict[str, Any]:
        """
        Get model configuration for a specific node (alias for get_model_config).
        
        Args:
            node_name: Optional node name for node-specific config
            
        Returns:
            Model configuration
        """
        return self.get_model_config(node_name)
    
    def get_node_tools_config(self, node_name: str) -> List[str]:
        """
        Get tools for a specific node.
        
        Args:
            node_name: Name of the node
            
        Returns:
            List of available tools (empty for now - implement as needed)
        """
        # Return empty list by default - tools can be added per node as needed
        return []
