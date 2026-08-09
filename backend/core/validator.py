from typing import Any, TypeVar, Type
from pydantic import BaseModel, ValidationError
import asyncio

T = TypeVar('T', bound=BaseModel)

class OutputValidator:
    """
    Validates structured outputs from the LLM.
    Ensures that the LLM's response strictly adheres to the requested Pydantic schema.
    """
    
    @staticmethod
    async def validate_schema_async(data: Any, schema: Type[T]) -> T:
        """
        Async version of validate_schema that can handle coroutines.
        
        Args:
            data: The raw data returned by the LLM (e.g., a dictionary parsed from JSON).
            schema: The expected Pydantic model class.
            
        Returns:
            An instance of the validated Pydantic model.
            
        Raises:
            ValueError: If the data fails validation.
        """
        try:
            # If data is a coroutine, await it first
            if asyncio.iscoroutine(data):
                data = await data
                
            if isinstance(data, dict):
                return schema(**data)
            elif isinstance(data, str):
                return schema.model_validate_json(data)
            else:
                return schema.model_validate(data)
        except ValidationError as e:
            # Here we could integrate with logging or a retry mechanism
            raise ValueError(f"Output validation failed for schema {schema.__name__}: {str(e)}")
    
    @staticmethod
    def validate_schema(data: Any, schema: Type[T]) -> T:
        """
        Validates the provided data against the given Pydantic schema.
        
        Args:
            data: The raw data returned by the LLM (e.g., a dictionary parsed from JSON).
            schema: The expected Pydantic model class.
            
        Returns:
            An instance of the validated Pydantic model.
            
        Raises:
            ValueError: If the data fails validation.
        """
        try:
            if isinstance(data, dict):
                return schema(**data)
            elif isinstance(data, str):
                return schema.model_validate_json(data)
            else:
                return schema.model_validate(data)
        except ValidationError as e:
            # Here we could integrate with logging or a retry mechanism
            raise ValueError(f"Output validation failed for schema {schema.__name__}: {str(e)}")
