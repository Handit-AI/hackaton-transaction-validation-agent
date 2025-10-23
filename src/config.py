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
        self.port: int = 8001
        
        # Graph configuration for PARALLEL FRAUD DETECTION
        # This configuration enables parallel execution of 5 analyzer nodes
        # Flow: START → orchestrator → (5 parallel analyzers) → decision_aggregator → finalizer → END
        self.graph_config = {
            "nodes": {
                # Control node - dispatches to analyzers
                "orchestrator": {
                    "node_name": "orchestrator",
                    "type": "control",
                    "description": "Parse transaction and dispatch to parallel analyzers"
                },

                # Analyzer nodes (run in parallel)
                "pattern_detector": {
                    "node_name": "pattern_detector",
                    "type": "llm",
                    "description": "Detect known fraud patterns and attack signatures",
                    "model_temperature": 0.1
                },
                "behavioral_analizer": {
                    "node_name": "behavioral_analizer",
                    "type": "llm",
                    "description": "Analyze deviations from user behavioral baseline",
                    "model_temperature": 0.1
                },
                "velocity_checker": {
                    "node_name": "velocity_checker",
                    "type": "llm",
                    "description": "Check for rapid-fire attacks and velocity abuse",
                    "model_temperature": 0.1
                },
                "merchant_risk_analizer": {
                    "node_name": "merchant_risk_analizer",
                    "type": "llm",
                    "description": "Assess merchant trustworthiness and category risk",
                    "model_temperature": 0.1
                },
                "geographic_analizer": {
                    "node_name": "geographic_analizer",
                    "type": "llm",
                    "description": "Detect location-based fraud and impossible travel",
                    "model_temperature": 0.1
                },

                # Aggregation node
                "decision_aggregator": {
                    "node_name": "decision_aggregator",
                    "type": "llm",
                    "description": "Aggregate all analyzer results into final decision",
                    "model_temperature": 0.2
                },

                # Finalizer (always included for parallel execution)
                "finalizer": {
                    "node_name": "finalizer",
                    "type": "finalizer",
                    "description": "Merges results from parallel execution"
                }
            },
            "edges": [
                # START to orchestrator
                {"from": "START", "to": "orchestrator"},

                # PARALLEL EXECUTION - orchestrator to all analyzers
                {"from": "orchestrator", "to": "pattern_detector"},
                {"from": "orchestrator", "to": "behavioral_analizer"},
                {"from": "orchestrator", "to": "velocity_checker"},
                {"from": "orchestrator", "to": "merchant_risk_analizer"},
                {"from": "orchestrator", "to": "geographic_analizer"},

                # CONVERGENCE - all analyzers to decision aggregator
                {"from": "pattern_detector", "to": "decision_aggregator"},
                {"from": "behavioral_analizer", "to": "decision_aggregator"},
                {"from": "velocity_checker", "to": "decision_aggregator"},
                {"from": "merchant_risk_analizer", "to": "decision_aggregator"},
                {"from": "geographic_analizer", "to": "decision_aggregator"},

                # Sequential final processing
                {"from": "decision_aggregator", "to": "finalizer"},
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
        self.model_provider = os.getenv("MODEL_PROVIDER_HACKATON", "mock")
        self.model_name = os.getenv("MODEL_NAME_HACKATON", "mock-llm")

        # Fraud Detection Configuration
        self.analyzer_weights = {
            "pattern_detector": 0.25,
            "behavioral_analizer": 0.20,
            "velocity_checker": 0.25,
            "merchant_risk_analizer": 0.15,
            "geographic_analizer": 0.15
        }

        self.risk_thresholds = {
            "decline": 70,
            "review": 40,
            "approve": 0
        }

        # Parallel execution settings
        self.parallel_timeout = 10.0  # seconds
        self.min_analyzers_required = 3  # minimum analyzers needed for decision
    
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
