from app.evaluators.base import SubjectPlugin
from app.strategies.core import (
    ConceptStrategy,
    ExactStrategy,
    FormulaStrategy,
    NumericStrategy,
    OptionStrategy,
    Strategy,
    UnitBasedStrategy,
)
from app.strategies.llm import LLMStrategy


class MathematicsPlugin(SubjectPlugin):
    name = "mathematics"

    @property
    def strategies(self) -> list[Strategy]:
        return [
            OptionStrategy(),
            ExactStrategy(),
            NumericStrategy(),
            FormulaStrategy(),
            ConceptStrategy(),
            LLMStrategy(),
            UnitBasedStrategy(),
        ]
