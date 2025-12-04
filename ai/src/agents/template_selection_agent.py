import logging
import random
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "ppt dataset"


class TemplateSelectionAgent:
	"""Chooses a PPT template.

	Originally this tried to match by subject/topic keywords. For the current
	use case we want more visual variety, so we select a random template from
	the available set on every run.
	"""

	def __init__(self, template_dir: Optional[Path] = None):
		self.template_dir = Path(template_dir or TEMPLATE_DIR)
		self.templates = self._scan_templates()

	def _scan_templates(self) -> List[Path]:
		if not self.template_dir.exists():
			logger.warning(f"Template directory not found: {self.template_dir}")
			return []
		return sorted(self.template_dir.glob("*.pptx"))

	def select_template(self, subject: str, topics: List[str]) -> Optional[str]:
		"""Return a random template path for visual variety."""
		if not self.templates:
			return None
		return str(random.choice(self.templates))

