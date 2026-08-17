import logging

from app.domain.enums import EvidenceStatus, QuestionCategory
from app.domain.models.requests import EvaluationRequest
from app.llm.prompts import PromptBuilder
from app.llm.providers import get_llm_evaluator
from app.strategies.core import Evidence

logger = logging.getLogger(__name__)


class LLMStrategy:
    name = "llm_evaluation"

    def applicable(self, c: EvaluationRequest) -> bool:
        # LLM is heavily used for Subjective questions.
        # It can also be used for Objective/Numerical questions if configured,
        # but primarily we want it for subjective or when reference text/concepts are present.
        return c.question.category == QuestionCategory.SUBJECTIVE

    def evaluate(self, c: EvaluationRequest) -> Evidence:
        try:
            evaluator = get_llm_evaluator()
            messages = PromptBuilder.build_messages(c)
            response = evaluator.evaluate_answer(messages)

            score = response.score if response.score is not None else 0.0

            status = (
                EvidenceStatus.PASS.value
                if score >= 90
                else EvidenceStatus.PARTIAL.value
                if score >= 40
                else EvidenceStatus.FAIL.value
            )

            details = [response.explanation]
            if response.improvement_guidance:
                details.append(f"Improvement: {response.improvement_guidance}")

            return Evidence(
                strategy=self.name,
                status=status,
                score=round(score, 2),
                details=tuple(details),
                payload={
                    "covered": response.recognized_concepts,
                    "missing": response.missing_concepts,
                    "misconceptions": response.detected_misconceptions,
                    "error_type": response.error_type,
                },
            )
        except Exception as e:  # noqa: BLE001
            logger.error(f"LLM Evaluation failed: {e}")
            return Evidence(
                strategy=self.name,
                status="evaluation_failure",
                score=None,
                details=("LLM evaluation unavailable.",),
                payload={"error": str(e)},
            )
