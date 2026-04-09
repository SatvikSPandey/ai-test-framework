import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import uuid
from core.models import (
    ParsedRequirements, GeneratedTestCases, TestCase, TestStep, Priority
)
from core.llm_client import llm_client
from core.config import settings


class TestCaseGenerator:
    """
    Agent 2 — Test Case Generator.
    Takes a ParsedRequirements object from Agent 1.
    Uses the LLM to generate BDD-style test cases for each feature.
    Outputs a GeneratedTestCases object ready for Agent 3.
    """

    def generate(self, parsed_requirements: ParsedRequirements) -> GeneratedTestCases:
        all_test_cases = []

        for feature in parsed_requirements.features:
            print(f"  Generating test cases for: {feature.name}")
            test_cases = self._generate_for_feature(feature)
            all_test_cases.extend(test_cases)

        deduplicated = self._deduplicate(all_test_cases)

        return GeneratedTestCases(
            total_test_cases=len(deduplicated),
            test_cases=deduplicated
        )

    def _generate_for_feature(self, feature) -> list[TestCase]:
        # Keep criteria short — just descriptions, no ids
        criteria_text = ", ".join([
            ac.description for ac in feature.acceptance_criteria
        ])

        prompt = f"""Generate 3 BDD test cases for this feature.
Feature: {feature.name}
Criteria: {criteria_text}

Return JSON only:
{{
  "test_cases": [
    {{
      "id": "TC001",
      "title": "short title",
      "priority": "high",
      "preconditions": ["precondition 1"],
      "steps": [
        {{"step_number": 1, "action": "Given the user is on the page"}},
        {{"step_number": 2, "action": "When the user performs action"}},
        {{"step_number": 3, "action": "Then the expected result occurs"}}
      ],
      "expected_result": "what should happen",
      "confidence_score": 0.9
    }}
  ]
}}"""

        data = llm_client.generate_json(prompt)

        test_cases = []
        for i, tc in enumerate(data.get("test_cases", [])):
            confidence = float(tc.get("confidence_score", 0.8))
            if confidence < settings.confidence_threshold:
                continue

            steps = [
                TestStep(
                    step_number=s.get("step_number", idx + 1),
                    action=s.get("action", "")
                )
                for idx, s in enumerate(tc.get("steps", []))
            ]

            test_cases.append(TestCase(
                id=tc.get("id", f"TC{str(uuid.uuid4())[:4].upper()}"),
                feature_id=feature.id,
                title=tc.get("title", f"Test case {i+1}"),
                priority=Priority(tc.get("priority", "medium")),
                preconditions=tc.get("preconditions", []),
                steps=steps,
                expected_result=tc.get("expected_result", ""),
                confidence_score=confidence
            ))

        return test_cases

    def _deduplicate(self, test_cases: list[TestCase]) -> list[TestCase]:
        seen_titles = set()
        unique = []
        for tc in test_cases:
            normalised = tc.title.lower().strip()
            if normalised not in seen_titles:
                seen_titles.add(normalised)
                unique.append(tc)
        return unique


# Single shared instance
test_case_generator = TestCaseGenerator()