from app.evaluators.base import SubjectPlugin
from app.strategies.core import (
    ConceptStrategy,
    ExactStrategy,
    FactualStrategy,
    OptionStrategy,
    Strategy,
    UnitBasedStrategy,
)
from app.strategies.llm import LLMStrategy


class HistoryPlugin(SubjectPlugin):
    name = "history"

    @property
    def strategies(self) -> list[Strategy]:
        return [
            OptionStrategy(),
            ExactStrategy(),
            ConceptStrategy(),
            FactualStrategy(),
            LLMStrategy(),
            UnitBasedStrategy(),
        ]
