from typing import List
from pydantic import BaseModel, Field


class BreedPrediction(BaseModel):
    breed: str = Field(
        ..., description="Standardized name of the predicted dog breed"
    )
    confidence: float = Field(
        ...,
        description="Confidence score mapping prediction probability (0.0 to 1.0)",
    )


class ClassificationResponse(BaseModel):
    predictions: List[BreedPrediction] = Field(
        ..., description="List of top breed predictions ordered by confidence"
    )
    latency_seconds: float = Field(
        ..., description="Total processing latency in seconds"
    )
