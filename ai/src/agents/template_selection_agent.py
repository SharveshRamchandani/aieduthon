import logging
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "ppt dataset"

STYLE_ALIASES = {
	"academic": {"academic", "educational", "training"},
	"storytelling": {"storytelling", "narrative", "humanities"},
	"business_pitch": {"business pitch", "pitch", "startup", "business"},
	"technical_briefing": {"technical", "technical briefing", "technology", "engineering"},
	"general": {"general", "default", "informative"},
}

STOPWORDS = {
	"the", "of", "and", "a", "to", "for", "in", "on", "with", "by", "an", "about", "introduction", "intro"
}

TEMPLATE_LIBRARY = {
	"black and grey monocrome business company presentation.pptx": {
		"subjects": {"business", "economics", "entrepreneurship"},
		"styles": {"business_pitch", "general"},
		"audiences": {"professional", "training"},
	},
	"black and white modern sunday sermon church presentation.pptx": {
		"subjects": {"history", "culture", "storytelling"},
		"styles": {"storytelling", "general"},
		"audiences": {"school", "college"},
	},
	"black and white modern technology presentation.pptx": {
		"subjects": {"science", "technology", "engineering"},
		"styles": {"technical_briefing"},
		"audiences": {"college", "professional"},
	},
	"black and white photographer portfolio presentation.pptx": {
		"subjects": {"arts", "design", "storytelling"},
		"styles": {"storytelling"},
		"audiences": {"school", "college"},
	},
	"black and white simple minimalist pitch deck marketing presentation.pptx": {
		"subjects": {"business", "marketing", "economics"},
		"styles": {"business_pitch"},
		"audiences": {"professional"},
	},
	"blue and green modern artificial intelligence presentation.pptx": {
		"subjects": {"science", "technology", "math"},
		"styles": {"technical_briefing", "academic"},
		"audiences": {"college", "professional"},
	},
	"blue and white minimalist corporate sustainable business presentation.pptx": {
		"subjects": {"business", "environment", "geography"},
		"styles": {"business_pitch", "academic"},
		"audiences": {"professional", "college"},
	},
	"blue and white modern cyber security presentation.pptx": {
		"subjects": {"technology", "science"},
		"styles": {"technical_briefing"},
		"audiences": {"college", "professional"},
	},
	"blue grey minimalist elegant business proposal presentation.pptx": {
		"subjects": {"business", "economics"},
		"styles": {"business_pitch"},
		"audiences": {"professional"},
	},
	"blue minimalist project presentation.pptx": {
		"subjects": {"science", "general"},
		"styles": {"academic", "general"},
		"audiences": {"school", "college"},
	},
	"blue simple geometric project presentation.pptx": {
		"subjects": {"science", "technology", "math"},
		"styles": {"technical_briefing", "academic"},
		"audiences": {"school", "college"},
	},
	"brown green aesthetic group project presentation.pptx": {
		"subjects": {"history", "geography", "storytelling"},
		"styles": {"academic", "storytelling"},
		"audiences": {"school"},
	},
	"cyan gradient technology startup business company presentation.pptx": {
		"subjects": {"technology", "business"},
		"styles": {"business_pitch", "technical_briefing"},
		"audiences": {"professional"},
	},
	"green modern financial management presentation.pptx": {
		"subjects": {"business", "economics", "finance"},
		"styles": {"business_pitch", "academic"},
		"audiences": {"college", "professional"},
	},
	"grey black minimalist simple project presentation.pptx": {
		"subjects": {"general", "science"},
		"styles": {"technical_briefing", "general"},
		"audiences": {"college", "professional"},
	},
	"grey blue minimalist modern presentation .pptx": {
		"subjects": {"general"},
		"styles": {"general", "academic"},
		"audiences": {"school", "college", "professional"},
	},
	"grey minimalist professional project presentation.pptx": {
		"subjects": {"general", "business"},
		"styles": {"general", "business_pitch"},
		"audiences": {"professional"},
	},
	"social media marketing report presentation.pptx": {
		"subjects": {"business", "marketing"},
		"styles": {"business_pitch"},
		"audiences": {"college", "professional"},
	},
}


@dataclass
class TemplateProfile:
	path: str
	subjects: Set[str]
	styles: Set[str]
	audiences: Set[str]
	keywords: Set[str]


class TemplateSelectionAgent:
	"""Chooses an appropriate PPT template based on subject, audience, and style."""

	def __init__(self, template_dir: Optional[Path] = None):
		self.template_dir = Path(template_dir or TEMPLATE_DIR)
		self.templates = self._scan_templates()
		self.template_profiles = self._build_template_profiles()

	def _scan_templates(self) -> List[Path]:
		if not self.template_dir.exists():
			logger.warning(f"Template directory not found: {self.template_dir}")
			return []
		return sorted(self.template_dir.glob("*.pptx"))

	def _build_template_profiles(self) -> List["TemplateProfile"]:
		profiles: List[TemplateProfile] = []
		for template_path in self.templates:
			filename = template_path.name.lower()
			metadata = TEMPLATE_LIBRARY.get(filename, {})
			keywords = metadata.get("keywords") or self._keywords_from_filename(template_path.stem)

			profiles.append(
				TemplateProfile(
					path=str(template_path),
					subjects=set(metadata.get("subjects", {"general"})),
					styles=set(metadata.get("styles", {"general"})),
					audiences=set(metadata.get("audiences", {"school", "college", "professional"})),
					keywords=set(keywords),
				)
			)

		return profiles

	def select_template(
		self,
		subject: str,
		topics: List[str],
		audience: Optional[str] = None,
		presentation_style: Optional[str] = None,
	) -> Optional[str]:
		"""Return the best matching template based on content metadata."""
		if not self.template_profiles:
			return None

		subject_key = (subject or "general").lower()
		audience_key = (audience or "").lower()
		style_key = self._normalize_style(presentation_style)
		topic_keywords = self._extract_topic_keywords(subject, topics)

		best_score = float("-inf")
		candidates: List[TemplateProfile] = []

		for profile in self.template_profiles:
			score = self._score_profile(profile, subject_key, topic_keywords, style_key, audience_key)
			if score > best_score:
				best_score = score
				candidates = [profile]
			elif abs(score - best_score) < 0.01:
				candidates.append(profile)

		if best_score <= 0:
			# Fall back to a random template for variety
			return str(random.choice(self.templates))

		return random.choice(candidates).path

	def _normalize_style(self, presentation_style: Optional[str]) -> str:
		if not presentation_style:
			return "general"

		style = presentation_style.strip().lower()
		for canonical, aliases in STYLE_ALIASES.items():
			if style == canonical or style in aliases:
				return canonical

		return "general"

	def _extract_topic_keywords(self, subject: str, topics: List[str]) -> Set[str]:
		keywords: Set[str] = set()
		candidates = []

		if subject:
			candidates.extend(subject.split())

		for topic in topics or []:
			candidates.extend(topic.split())

		for raw_word in candidates:
			word = re.sub(r"[^a-z0-9]", "", raw_word.lower())
			if word and word not in STOPWORDS:
				keywords.add(word)

		return keywords

	def _score_profile(
		self,
		profile: TemplateProfile,
		subject: str,
		keywords: Set[str],
		style: str,
		audience: str,
	) -> float:
		score = 0.0

		if subject in profile.subjects:
			score += 5
		elif subject != "general" and subject in profile.keywords:
			score += 3

		if style in profile.styles:
			score += 4
		elif style == "general" and "general" in profile.styles:
			score += 1

		if audience and audience in profile.audiences:
			score += 2
		elif "general" in profile.audiences:
			score += 0.5

		for kw in keywords:
			if kw in profile.keywords:
				score += 1.5

		# Slight boost for versatile templates
		if "general" in profile.subjects:
			score += 0.25

		return score

	def _keywords_from_filename(self, filename: str) -> Set[str]:
		words = re.split(r"\s+", filename.lower())
		return {word for word in words if word and word not in STOPWORDS}

