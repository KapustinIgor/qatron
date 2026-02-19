"""BDD feature parser for Gherkin files."""
import re
from typing import List, Dict, Optional
from pathlib import Path


class GherkinParser:
    """Parse Gherkin feature files into structured data."""

    @staticmethod
    def parse_feature_file(file_path: Path) -> Optional[Dict]:
        """Parse a Gherkin feature file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            return GherkinParser.parse_feature_content(content, str(file_path))
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    @staticmethod
    def parse_feature_content(content: str, file_path: str = "") -> Optional[Dict]:
        """Parse Gherkin content string."""
        lines = content.split("\n")
        feature = {
            "file_path": file_path,
            "name": None,
            "description": [],
            "tags": [],
            "scenarios": [],
        }

        current_scenario = None
        current_step = None
        in_background = False
        in_examples = False
        examples_table = []

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Feature line
            if line.startswith("Feature:"):
                feature["name"] = line.replace("Feature:", "").strip()
                i += 1
                # Collect description until Scenario/Background/Tag
                while i < len(lines):
                    desc_line = lines[i].strip()
                    if desc_line.startswith(("@", "Scenario", "Background", "Feature")):
                        break
                    if desc_line and not desc_line.startswith("#"):
                        feature["description"].append(desc_line)
                    i += 1
                feature["description"] = "\n".join(feature["description"]).strip()
                continue

            # Tags
            if line.startswith("@"):
                tags = re.findall(r"@\w+", line)
                if current_scenario:
                    current_scenario["tags"].extend(tags)
                else:
                    feature["tags"].extend(tags)
                i += 1
                continue

            # Background
            if line.startswith("Background:"):
                in_background = True
                i += 1
                continue

            # Scenario/Scenario Outline
            if line.startswith("Scenario:") or line.startswith("Scenario Outline:"):
                if current_scenario:
                    feature["scenarios"].append(current_scenario)
                current_scenario = {
                    "name": line.split(":", 1)[1].strip(),
                    "type": "scenario_outline" if "Outline" in line else "scenario",
                    "tags": [],
                    "steps": [],
                    "examples": [],
                }
                in_background = False
                in_examples = False
                i += 1
                continue

            # Examples table
            if line.startswith("Examples:"):
                in_examples = True
                examples_table = []
                i += 1
                # Read header
                if i < len(lines):
                    header_line = lines[i].strip()
                    if "|" in header_line:
                        examples_table.append([cell.strip() for cell in header_line.split("|")[1:-1]])
                        i += 1
                continue

            # Examples table rows
            if in_examples and "|" in line:
                row = [cell.strip() for cell in line.split("|")[1:-1]]
                if row and any(cell for cell in row):  # Non-empty row
                    examples_table.append(row)
                i += 1
                continue

            # Step (Given/When/Then/And/But)
            step_match = re.match(r"^(Given|When|Then|And|But)\s+(.+)$", line, re.IGNORECASE)
            if step_match:
                step_type = step_match.group(1).lower()
                step_text = step_match.group(2).strip()

                # Check for data table
                step_data_table = None
                if i + 1 < len(lines) and lines[i + 1].strip().startswith("|"):
                    step_data_table = []
                    j = i + 1
                    while j < len(lines) and "|" in lines[j]:
                        row = [cell.strip() for cell in lines[j].split("|")[1:-1]]
                        if row:
                            step_data_table.append(row)
                        j += 1
                    i = j - 1

                step = {
                    "type": step_type,
                    "text": step_text,
                    "data_table": step_data_table,
                }

                if current_scenario:
                    current_scenario["steps"].append(step)
                i += 1
                continue

            i += 1

        # Add last scenario
        if current_scenario:
            if examples_table and len(examples_table) > 1:
                current_scenario["examples"] = examples_table
            feature["scenarios"].append(current_scenario)

        return feature if feature["name"] else None

    @staticmethod
    def scan_repository(repo_path: Path, pattern: str = "**/*.feature") -> List[Dict]:
        """Scan repository for feature files and parse them."""
        features = []
        for feature_file in repo_path.glob(pattern):
            parsed = GherkinParser.parse_feature_file(feature_file)
            if parsed:
                features.append(parsed)
        return features
