import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Protocol

from app.domain.enums import EvidenceStatus, QuestionCategory, QuestionType
from app.domain.models.requests import EvaluationRequest


@dataclass(frozen=True)
class Evidence:
    strategy: str
    status: str
    score: float | None = None
    details: tuple[str, ...] = ()
    payload: dict[str, object] | None = None


class Strategy(Protocol):
    name: str

    def applicable(self, ctx: EvaluationRequest) -> bool: ...
    def evaluate(self, ctx: EvaluationRequest) -> Evidence: ...


def norm(s: str) -> str:
    return re.sub(r"[^\w]+", "", s.casefold(), flags=re.UNICODE)


def toks(s: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", s.casefold())


def similarity(a: str, b: str) -> float:
    A, B = Counter(toks(a)), Counter(toks(b))
    if not A or not B:
        return 0.0
    return 2 * sum((A & B).values()) / (sum(A.values()) + sum(B.values())) * 100


def accepted(ctx: EvaluationRequest) -> list[str]:
    out = list(ctx.reference_answer.accepted_answers)
    if ctx.reference_answer.text:
        out.append(ctx.reference_answer.text)
    return out


class OptionStrategy:
    name = "option_selection"

    def applicable(self, c: EvaluationRequest) -> bool:
        return c.question.type in {
            QuestionType.MCQ,
            QuestionType.MULTIPLE_SELECT,
            QuestionType.TRUE_FALSE,
        }

    def evaluate(self, c: EvaluationRequest) -> Evidence:
        correct = {norm(x) for x in c.reference_answer.correct_option_ids}
        selected = {norm(x) for x in re.split(r"[,;]", c.student_answer.content) if x.strip()}
        if c.question.type == QuestionType.MULTIPLE_SELECT:
            if not correct:
                return Evidence(self.name, EvidenceStatus.NOT_APPLICABLE.value)
            hit = selected & correct
            wrong = selected - correct
            score = max(0, 100 * len(hit) / len(correct) - 100 * len(wrong) / len(correct))
            status = (
                EvidenceStatus.PASS.value
                if selected == correct
                else EvidenceStatus.PARTIAL.value
                if hit
                else EvidenceStatus.FAIL.value
            )
            return Evidence(
                self.name,
                status,
                round(score, 2),
                (
                    f"Selected: {sorted(selected)}",
                    f"Missing: {sorted(correct - selected)}",
                    f"Incorrect: {sorted(wrong)}",
                ),
            )
        ok = selected == correct
        return Evidence(
            self.name,
            EvidenceStatus.PASS.value if ok else EvidenceStatus.FAIL.value,
            100 if ok else 0,
            (f"Expected: {sorted(correct)}; received: {sorted(selected)}",),
        )


class ExactStrategy:
    name = "normalized_exact_match"

    def applicable(self, c: EvaluationRequest) -> bool:
        return c.question.category == QuestionCategory.OBJECTIVE

    def evaluate(self, c: EvaluationRequest) -> Evidence:
        s = norm(c.student_answer.content)
        ok = bool(s) and any(s == norm(x) for x in accepted(c))
        return Evidence(
            self.name,
            EvidenceStatus.PASS.value if ok else EvidenceStatus.FAIL.value,
            100 if ok else 0,
            ("Matched accepted answer." if ok else "No accepted-answer match.",),
        )


class NumericStrategy:
    name = "numeric_comparison"

    def applicable(self, c: EvaluationRequest) -> bool:
        return c.question.type == QuestionType.NUMERIC

    def evaluate(self, c: EvaluationRequest) -> Evidence:
        try:
            s = float(c.student_answer.content.replace(",", ""))
            r = float(
                (c.reference_answer.text or c.reference_answer.accepted_answers[0]).replace(",", "")
            )
        except (ValueError, IndexError):
            return Evidence(self.name, EvidenceStatus.FAIL.value, 0, ("Invalid numeric value.",))
        err = abs(s - r)
        rel = err / abs(r) if r else err
        score = (
            100
            if math.isclose(s, r, rel_tol=1e-9, abs_tol=1e-9)
            else max(0, 100 * (1 - min(rel, 1)))
        )
        st = (
            EvidenceStatus.PASS.value
            if score == 100
            else EvidenceStatus.PARTIAL.value
            if score > 0
            else EvidenceStatus.FAIL.value
        )
        return Evidence(
            self.name,
            st,
            round(score, 2),
            (f"Absolute error: {err:g}.", f"Relative error: {rel:.4f}."),
            {"absolute_error": err, "relative_error": rel, "student": s, "reference": r},
        )


class FormulaStrategy:
    name = "formula_normalization"

    def applicable(self, c: EvaluationRequest) -> bool:
        return c.question.type in {
            QuestionType.FORMULA,
            QuestionType.PROOF,
            QuestionType.DERIVATION,
        }

    def evaluate(self, c: EvaluationRequest) -> Evidence:
        a = normalize_formula(c.student_answer.content)
        b = normalize_formula(c.reference_answer.text or "")
        ok = bool(a and b and a == b)
        return Evidence(
            self.name,
            EvidenceStatus.PASS.value if ok else EvidenceStatus.PARTIAL.value,
            100 if ok else 0,
            (
                "Formula matched after normalization."
                if ok
                else "Formula did not match under V1 normalization.",
            ),
        )


def normalize_formula(s: str) -> str:
    return s.casefold().replace(" ", "").replace("²", "^2").replace("×", "*").replace("−", "-")


class ConceptStrategy:
    name = "concept_coverage"

    def applicable(self, c: EvaluationRequest) -> bool:
        return bool(c.reference_answer.expected_concepts)

    def evaluate(self, c: EvaluationRequest) -> Evidence:
        ans = c.student_answer.content.casefold()
        concepts = c.reference_answer.expected_concepts
        hit = [x for x in concepts if x.casefold() in ans]
        miss = [x for x in concepts if x.casefold() not in ans]
        score = 100 * len(hit) / len(concepts)
        return Evidence(
            self.name,
            EvidenceStatus.PASS.value
            if score >= 80
            else EvidenceStatus.PARTIAL.value
            if hit
            else EvidenceStatus.FAIL.value,
            round(score, 2),
            (f"Covered {len(hit)}/{len(concepts)} concepts.",),
            {"covered": hit, "missing": miss},
        )


class UnitBasedStrategy:
    name = "unit_based_comparison"

    def applicable(self, c: EvaluationRequest) -> bool:
        return c.question.type == QuestionType.UNIT_BASED

    def evaluate(self, c: EvaluationRequest) -> Evidence:
        # Simplistic parsing of value and unit for V1
        s_val, s_unit = "", ""
        r_val, r_unit = "", ""

        student_parts = c.student_answer.content.strip().split()
        if len(student_parts) >= 2:
            s_val = student_parts[0]
            s_unit = " ".join(student_parts[1:])
        else:
            s_val = c.student_answer.content

        ref_text = c.reference_answer.text or (
            c.reference_answer.accepted_answers[0] if c.reference_answer.accepted_answers else ""
        )
        ref_parts = ref_text.strip().split()
        if len(ref_parts) >= 2:
            r_val = ref_parts[0]
            r_unit = " ".join(ref_parts[1:])
        else:
            r_val = ref_text

        if c.question.expected_unit:
            r_unit = c.question.expected_unit

        try:
            s_f = float(s_val.replace(",", ""))
            r_f = float(r_val.replace(",", ""))
            val_match = math.isclose(s_f, r_f, rel_tol=1e-9, abs_tol=1e-9)
        except ValueError:
            val_match = False

        unit_match = (norm(s_unit) == norm(r_unit)) if r_unit else True

        error_type = None
        if val_match and unit_match:
            score = 100.0
            status = EvidenceStatus.PASS.value
            details = "Both value and unit are correct."
        elif val_match and not unit_match:
            score = 50.0
            status = EvidenceStatus.PARTIAL.value
            details = f"Value is correct, but unit is incorrect. Expected unit: '{r_unit}'."
            error_type = "unit_error"
        elif not val_match and unit_match:
            score = 0.0
            status = EvidenceStatus.FAIL.value
            details = "Unit is correct, but numerical value is incorrect."
            error_type = "numeric_or_calculation_error"
        else:
            score = 0.0
            status = EvidenceStatus.FAIL.value
            details = "Both numerical value and unit are incorrect."
            error_type = "numeric_and_unit_error"

        return Evidence(
            self.name,
            status,
            score,
            (details,),
            {
                "student_value": s_val,
                "student_unit": s_unit,
                "expected_value": r_val,
                "expected_unit": r_unit,
                "error_type": error_type,
            },
        )


class GrammarStrategy:
    name = "grammar_heuristic"

    def applicable(self, c: EvaluationRequest) -> bool:
        return (
            c.question.category == QuestionCategory.SUBJECTIVE
            and c.question.subject.value == "english"
            and c.question.type
            in {
                QuestionType.SHORT_ANSWER,
                QuestionType.EXPLANATION,
                QuestionType.DESCRIPTIVE,
                QuestionType.ESSAY,
            }
        )

    def evaluate(self, c: EvaluationRequest) -> Evidence:
        issues = []
        text = c.student_answer.content
        if text and text[0].islower():
            issues.append("Response begins with lowercase text.")
        if not re.search(r"[.!?]$", text) and text:
            issues.append("Response has no terminal punctuation.")
        score = max(0, 100 - 15 * len(issues))
        return Evidence(
            self.name,
            EvidenceStatus.PASS.value if score >= 80 else EvidenceStatus.PARTIAL.value,
            score,
            tuple(issues) or ("No basic grammar-format issues detected.",),
        )


class FactualStrategy:
    name = "factual_coverage"

    def applicable(self, c: EvaluationRequest) -> bool:
        return c.question.subject.value in {"science", "history"} and bool(
            c.reference_answer.expected_concepts
        )

    def evaluate(self, c: EvaluationRequest) -> Evidence:
        return ConceptStrategy().evaluate(c)
