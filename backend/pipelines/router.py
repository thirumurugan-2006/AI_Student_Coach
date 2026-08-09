"""
Pipeline Router

Maps next_action to the appropriate Pipeline implementation.
The Router is responsible for routing, not business logic.
"""

from typing import Dict, Type, Any
from pipelines.base_pipeline import BasePipeline
from core.logger import logger


class PipelineRouter:
    """
    Router that maps next_action to Pipeline implementations.
    
    The Router answers: "Which Pipeline should handle this next_action?"
    
    It does NOT contain business logic - only routing logic.
    """
    
    def __init__(self):
        """Initialize the Router with Pipeline mappings."""
        self.pipeline_classes: Dict[str, Type[BasePipeline]] = {}
        self.pipeline_instances: Dict[str, BasePipeline] = {}
        logger.info("PipelineRouter initialized")
    
    def register_pipeline(self, next_action: str, pipeline_class: Type[BasePipeline]) -> None:
        """
        Register a Pipeline class for a specific next_action.
        
        Args:
            next_action: The action name (e.g., "survey", "assessment")
            pipeline_class: The Pipeline class to execute
        """
        self.pipeline_classes[next_action] = pipeline_class
        logger.info(f"Registered pipeline '{pipeline_class.__name__}' for action '{next_action}'")
    
    def get_pipeline(self, next_action: str, dependencies: Dict[str, Any] = None) -> BasePipeline:
        """
        Get a pipeline instance for the given action.
        
        Args:
            next_action: The action to get the pipeline for
            dependencies: Optional dependencies to inject (llm, memory, career_intelligence)
            
        Returns:
            Pipeline instance
            
        Raises:
            ValueError: If no pipeline is registered for the action
        """
        logger.info(f"PipelineRouter: get_pipeline called for action '{next_action}'")
        if next_action not in self.pipeline_classes:
            logger.error(f"PipelineRouter: No pipeline registered for action: {next_action}")
            raise ValueError(f"No pipeline registered for action: {next_action}")
        
        logger.info(f"PipelineRouter: Pipeline class found for action '{next_action}'")
        
        # Create or reuse pipeline instance
        if next_action not in self.pipeline_instances:
            pipeline_class = self.pipeline_classes[next_action]
            logger.info(f"PipelineRouter: Creating new pipeline instance for action '{next_action}'")
            
            # Inject dependencies if provided
            if dependencies:
                logger.info(f"PipelineRouter: Injecting dependencies: llm={dependencies.get('llm') is not None}, memory={dependencies.get('memory') is not None}")
                pipeline_instance = pipeline_class(
                    llm=dependencies.get('llm'),
                    memory=dependencies.get('memory'),
                    career_intelligence=dependencies.get('career_intelligence')
                )
            else:
                logger.warning(f"PipelineRouter: No dependencies provided, creating pipeline without injection")
                pipeline_instance = pipeline_class()
            
            self.pipeline_instances[next_action] = pipeline_instance
            logger.info(f"PipelineRouter: Created pipeline instance for action '{next_action}'")
        else:
            logger.info(f"PipelineRouter: Reusing existing pipeline instance for action '{next_action}'")
        
        return self.pipeline_instances[next_action]
    
    def list_registered_pipelines(self) -> Dict[str, str]:
        """
        List all registered pipeline mappings.
        
        Returns:
            Dictionary mapping next_action to pipeline class name
        """
        return {
            action: pipeline_class.__name__
            for action, pipeline_class in self.pipeline_classes.items()
        }
    
    def is_action_registered(self, next_action: str) -> bool:
        """
        Check if an action has a registered pipeline.
        
        Args:
            next_action: The action to check
            
        Returns:
            True if registered, False otherwise
        """
        return next_action in self.pipeline_classes


# Global router instance
pipeline_router = PipelineRouter()
