import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pdfplumber
import docx
import uuid
from core.models import ParsedRequirements, Feature, AcceptanceCriteria


class RequirementsParser:
    """
    Agent 1 — Requirements Parser.
    Parses requirements documents into structured features.
    For plain text input, uses a direct rule-based parser
    instead of an LLM to avoid JSON truncation issues.
    """

    def parse_file(self, file_path: str) -> ParsedRequirements:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        extension = path.suffix.lower()

        if extension == ".pdf":
            raw_text = self._extract_pdf(path)
        elif extension == ".docx":
            raw_text = self._extract_docx(path)
        elif extension == ".txt":
            raw_text = path.read_text(encoding="utf-8")
        else:
            raise ValueError(f"Unsupported file type: {extension}. Use PDF, DOCX, or TXT.")

        return self._parse_text_directly(raw_text, source_file=path.name)

    def parse_text(self, text: str) -> ParsedRequirements:
        return self._parse_text_directly(text, source_file="direct_input")

    def _extract_pdf(self, path: Path) -> str:
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if not text.strip():
            raise ValueError("Could not extract text from PDF.")
        return text

    def _extract_docx(self, path: Path) -> str:
        doc = docx.Document(path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        if not text.strip():
            raise ValueError("Could not extract text from DOCX.")
        return text

    def _parse_text_directly(self, raw_text: str, source_file: str) -> ParsedRequirements:
        """
        Rule-based parser that extracts features and acceptance criteria
        directly from text without using an LLM.
        Looks for lines starting with 'Feature' and criteria after
        'Acceptance Criteria:' sections.
        """
        features = []
        current_feature = None
        current_criteria = []
        in_criteria_section = False
        feature_counter = 0
        criteria_counter = 0

        lines = raw_text.strip().split("\n")

        for line in lines:
            stripped = line.strip()

            if not stripped:
                continue

            # Detect feature lines — "Feature X:" or "Feature X."
            if stripped.lower().startswith("feature") and (":" in stripped or stripped[-1].isdigit()):
                # Save previous feature if exists
                if current_feature:
                    features.append(Feature(
                        id=f"F{str(feature_counter).zfill(3)}",
                        name=current_feature["name"],
                        description=current_feature["description"],
                        acceptance_criteria=current_criteria
                    ))

                feature_counter += 1
                criteria_counter = 0
                current_criteria = []
                in_criteria_section = False

                # Extract feature name — everything after the colon or number
                parts = stripped.split(":", 1)
                if len(parts) > 1:
                    name = parts[1].strip()
                else:
                    # Try splitting by space and taking rest
                    words = stripped.split()
                    name = " ".join(words[2:]) if len(words) > 2 else stripped

                current_feature = {"name": name, "description": ""}

            # Detect acceptance criteria section
            elif stripped.lower().startswith("acceptance criteria"):
                in_criteria_section = True

            # Detect individual criteria lines starting with -
            elif stripped.startswith("-") and in_criteria_section:
                criteria_counter += 1
                description = stripped[1:].strip()
                current_criteria.append(AcceptanceCriteria(
                    id=f"AC{str(criteria_counter).zfill(3)}",
                    description=description
                ))

            # Description line — the line right after the feature name
            elif current_feature and not in_criteria_section and not stripped.lower().startswith("feature"):
                if not current_feature["description"]:
                    current_feature["description"] = stripped

        # Save the last feature
        if current_feature:
            features.append(Feature(
                id=f"F{str(feature_counter).zfill(3)}",
                name=current_feature["name"],
                description=current_feature["description"],
                acceptance_criteria=current_criteria
            ))

        if not features:
            raise ValueError(
                "Could not find any features in the text. "
                "Make sure your requirements include lines starting with 'Feature'."
            )

        return ParsedRequirements(
            source_file=source_file,
            total_features=len(features),
            features=features
        )


# Single shared instance
requirements_parser = RequirementsParser()