import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "ppt dataset"


class TemplateSelectionAgent:
	"""Chooses a PPT template based on subject/topic keywords."""

	def __init__(self, template_dir: Optional[Path] = None):
		self.template_dir = Path(template_dir or TEMPLATE_DIR)
		self.templates = self._scan_templates()

	def _scan_templates(self) -> List[Path]:
		if not self.template_dir.exists():
			logger.warning(f"Template directory not found: {self.template_dir}")
			return []
		return sorted(self.template_dir.glob("*.pptx"))

	def select_template(self, subject: str, topics: List[str]) -> Optional[str]:
		if not self.templates:
			return None
		search_terms = []
		if subject:
			search_terms.extend(subject.lower().split())
		for topic in topics:
			search_terms.extend(topic.lower().split())
		if not search_terms:
			return str(self.templates[0])
		def score(path: Path) -> int:
			name = path.stem.lower()
			return sum(1 for term in search_terms if term and term in name)
		best = max(self.templates, key=score)
		if score(best) == 0:
			return str(self.templates[0])
		return str(best)

