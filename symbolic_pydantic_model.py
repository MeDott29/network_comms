from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import List, Optional, Dict

class ConcreteLayer(BaseModel):
    """Represents the raw elements being abstracted, such as individual stars."""
    name: str
    description: str
    properties: Optional[Dict[str, Union[str, float]]] = None  # e.g., brightness, distance

class SymbolismLayer(BaseModel):
    """Represents the symbolic meaning or metaphor of the abstraction."""
    metaphor: str
    meaning: str
    origin: Optional[str] = None  # Cultural or mythological origin

class AbstractLayer(BaseModel):
    """Represents the abstraction, such as a constellation."""
    name: str
    description: str
    related_concepts: List[str] = Field(default_factory=list)  # Related ideas or themes

    @field_validator("description")
    def validate_description(cls, v):
        """Ensure the description is at least 10 characters long."""
        if len(v) < 10:
            raise ValueError("Description must be at least 10 characters long.")
        return v

class AbstractionLanguage(BaseModel):
    """Main model that captures relationships between abstraction layers."""
    abstract: AbstractLayer
    concrete: List[ConcreteLayer] = Field(min_items=1)  # Ensure at least one element
    symbolism: Optional[SymbolismLayer] = None

    def describe(self) -> str:
        """Generate a detailed summary of the abstraction language."""
        summary = f"'{self.abstract.name}' abstracts the following elements:\n"
        for item in self.concrete:
            summary += f"  - {item.name}: {item.description}\n"
            if item.properties:
                summary += f"    Properties: {item.properties}\n"
        if self.symbolism:
            summary += (
                f"\nSymbolism: '{self.symbolism.metaphor}' represents "
                f"'{self.symbolism.meaning}'"
            )
            if self.symbolism.origin:
                summary += f" (Origin: {self.symbolism.origin})"
        return summary

# Example Usage
if __name__ == "__main__":
    try:
        # Create an abstraction of the Orion constellation
        orion = AbstractionLanguage(
            abstract=AbstractLayer(
                name="Orion",
                description="A constellation representing a hunter from Greek mythology.",
                related_concepts=["Hunter", "Greek Mythology", "Winter Sky"]
            ),
            concrete=[
                ConcreteLayer(
                    name="Betelgeuse",
                    description="A red supergiant star forming Orion's shoulder.",
                    properties={"brightness": "variable", "distance": 642.5}
                ),
                ConcreteLayer(
                    name="Rigel",
                    description="A bright blue supergiant marking Orion's foot.",
                    properties={"brightness": "very bright", "distance": 863}
                ),
                ConcreteLayer(
                    name="Orion Nebula",
                    description="A stellar nursery located below Orion's belt.",
                    properties={"type": "emission nebula", "distance": 1350}
                )
            ],
            symbolism=SymbolismLayer(
                metaphor="Hunter",
                meaning="Symbolizes strength and courage, essential for survival.",
                origin="Ancient Greek Mythology"
            )
        )

        print(orion.describe())

    except ValidationError as e:
        print(f"Validation Error: {e}")
