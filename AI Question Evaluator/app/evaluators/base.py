from abc import ABC, abstractmethod
from statistics import mean

from app.domain.enums import EvaluationStatus
from app.domain.models.requests import (
    ConceptAnalysis,
    Dimension,
    ErrorAnalysis,
    EvaluationRequest,
    EvaluationResponse,
    Feedback,
)
from app.strategies.core import Strategy


class SubjectPlugin(ABC):
    name = "base"

    @property
    @abstractmethod
    def strategies(self) -> list[Strategy]: ...
    def applicable(self, c: EvaluationRequest) -> list[Strategy]:
        return [s for s in self.strategies if s.applicable(c)]

    def evaluate(self, c: EvaluationRequest) -> EvaluationResponse:
        ev = [s.evaluate(c) for s in self.applicable(c)]

        # Check if LLM explicitly failed
        llm_failure = next((e for e in ev if e.status == "evaluation_failure"), None)

        # For subjective questions, if LLM fails, the whole evaluation fails
        if llm_failure and c.question.category == "subjective":
            usable = []
        else:
            usable = [e for e in ev if e.score is not None]
        if not usable:
            if llm_failure:
                return EvaluationResponse(
                    status=EvaluationStatus.EVALUATION_FAILURE,
                    score=None,
                    confidence=0.0,
                    dimensions={},
                    concept_analysis=ConceptAnalysis(),
                    error_analysis=ErrorAnalysis(
                        explanation="LLM evaluation failed.",
                        severity="major",
                        error_type="evaluation_failure",
                    ),
                    feedback=Feedback(
                        summary="Evaluation failed due to an infrastructure error.",
                        explanation=str(llm_failure.payload.get("error", "LLM provider error"))
                        if llm_failure.payload
                        else "Unknown error.",
                    ),
                    metadata={
                        "plugin": self.name,
                        "strategies": [e.strategy for e in ev],
                        "source": c.student_answer.source,
                    },
                )

            return EvaluationResponse(
                status=EvaluationStatus.INSUFFICIENT_REFERENCE,
                score=None,
                confidence=0.25,
                dimensions={},
                concept_analysis=ConceptAnalysis(),
                error_analysis=ErrorAnalysis(explanation="Insufficient reference information."),
                feedback=Feedback(
                    summary="The answer could not be reliably evaluated.",
                    explanation="Provide a correct/reference answer or rubric.",
                ),
                metadata={
                    "plugin": self.name,
                    "strategies": [e.strategy for e in ev],
                    "source": c.student_answer.source,
                },
            )
        # Default to average, but then apply strict precedence overrides based on question type
        score = round(mean(float(e.score or 0.0) for e in usable), 2)

        # 1. Objective: deterministic correctness dominates
        if c.question.category == "objective":
            decisive = next(
                (e for e in ev if e.strategy in {"option_selection", "normalized_exact_match"}),
                None,
            )
            if decisive:
                score = decisive.score or 0.0

        # 2. Numerical: specific strategies dominate
        elif c.question.category == "numerical":
            if c.question.type == "numeric":
                num = next((e for e in ev if e.strategy == "numeric_comparison"), None)
                if num:
                    score = num.score or 0.0
            elif c.question.type == "unit_based":
                unit = next((e for e in ev if e.strategy == "unit_based_comparison"), None)
                if unit:
                    score = unit.score or 0.0
            elif c.question.type == "formula":
                form = next((e for e in ev if e.strategy == "formula_normalization"), None)
                if form:
                    score = form.score or 0.0

        # 3. Subjective: LLM evidence is primary, particularly for proofs and derivations
        elif c.question.category == "subjective":
            llm = next((e for e in ev if e.strategy == "llm_evaluation"), None)
            if llm:
                score = llm.score or 0.0

        status = (
            EvaluationStatus.CORRECT
            if score >= 90
            else EvaluationStatus.PARTIALLY_CORRECT
            if score >= 40
            else EvaluationStatus.INCORRECT
        )
        covered = []
        missing = []
        for e in ev:
            if e.payload:
                cov = e.payload.get("covered", [])
                if isinstance(cov, list):
                    covered += [str(x) for x in cov]
                mis = e.payload.get("missing", [])
                if isinstance(mis, list):
                    missing += [str(x) for x in mis]
        
        # Reconciliation: if any strategy (like LLM) marks it as covered, it's not missing.
        correct_set = list(dict.fromkeys(covered))
        missing_set = [m for m in dict.fromkeys(missing) if m not in correct_set]
        
        concepts = ConceptAnalysis(correct=correct_set, missing=missing_set)
        
        total_expected = len(c.reference_answer.expected_concepts) if c.reference_answer.expected_concepts else (len(concepts.correct) + len(concepts.missing))
        
        dims = {
            "correctness": Dimension(score=score, evidence=list(dict.fromkeys(d for e in ev for d in e.details))),
            "completeness": Dimension(
                score=round(
                    100 * len(concepts.correct) / max(1, total_expected),
                    2,
                ),
                evidence=[
                    f"{len(concepts.correct)} concepts covered; {len(concepts.missing)} missing."
                ],
            ),
            "relevance": Dimension(
                score=score, evidence=["Derived from applicable evaluation evidence."]
            ),
            "clarity": Dimension(score=100, evidence=["No default clarity penalty applied."]),
        }
        error = ErrorAnalysis()
        if status != EvaluationStatus.CORRECT:
            explicit_error_type = next(
                (
                    str(e.payload.get("error_type"))
                    for e in ev
                    if e.payload and e.payload.get("error_type")
                ),
                None,
            )

            error.error_type = (
                explicit_error_type
                if explicit_error_type
                else "numeric_or_calculation_error"
                if any(e.strategy == "numeric_comparison" for e in ev)
                else "incorrect_selection_or_answer"
                if c.question.category.value == "objective"
                else "missing_or_incorrect_concepts"
                if concepts.missing
                else "incomplete_or_inaccurate_response"
            )
            error.severity = "major" if score < 40 else "minor"
            error.explanation = " ".join(d for e in ev for d in e.details[:2])
            num = next((e for e in ev if e.strategy == "numeric_comparison"), None)
            if num and num.payload:
                error.distance_from_correct = {
                    "absolute_error": float(str(num.payload.get("absolute_error", 0))),
                    "relative_error": float(str(num.payload.get("relative_error", 0))),
                }
        ref = c.reference_answer.text or ", ".join(c.reference_answer.accepted_answers)
        explanation = (
            (f"Expected answer/reference: {ref}. " if ref else "")
            + (f"Missing concepts: {', '.join(concepts.missing)}. " if concepts.missing else "")
            + (f"Recognized concepts: {', '.join(concepts.correct)}." if concepts.correct else "")
        )
        feedback = Feedback(
            summary=f"The answer is {status.value.replace('_', ' ')} ({score:.2f}/100).",
            explanation=explanation
            or "Evaluation completed using the applicable domain strategies.",
            improvement_hint=("Review: " + ", ".join(concepts.missing) + ".")
            if concepts.missing
            else "Verify the reasoning and final answer before submitting.",
        )
        confidence = round(min(0.99, 0.85), 2)
        from app.config import settings

        metadata_dict: dict[str, object] = {
            "plugin": self.name,
            "strategies": [e.strategy for e in ev],
            "source": c.student_answer.source,
        }

        if any(e.strategy == "llm_evaluation" for e in ev):
            metadata_dict["llm_provider"] = settings.llm_provider
            metadata_dict["llm_model"] = settings.llm_model

        return EvaluationResponse(
            status=status,
            score=score,
            confidence=confidence,
            dimensions=dims,
            concept_analysis=concepts,
            error_analysis=error,
            feedback=feedback,
            metadata=metadata_dict,
        )
