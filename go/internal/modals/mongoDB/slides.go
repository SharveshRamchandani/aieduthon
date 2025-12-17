package mongodb

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

// SpeakerNote represents speaker notes for a slide
type SpeakerNote struct {
	SlideIndex         int      `bson:"slide_index" json:"slide_index"`
	SlideTitle         string   `bson:"slide_title" json:"slide_title"`
	Notes              string   `bson:"notes" json:"notes"`
	KeyPoints          []string `bson:"key_points" json:"key_points"`
	Examples           []string `bson:"examples" json:"examples"`
	AudienceEngagement string   `bson:"audience_engagement" json:"audience_engagement"`
}

// ImageMarker represents an image marker/placeholder
type ImageMarker struct {
	Marker      string                 `bson:"marker" json:"marker"`
	Token       string                 `bson:"token" json:"token"`
	Description string                 `bson:"description" json:"description"`
	Start       int                    `bson:"start" json:"start"`
	End         int                    `bson:"end" json:"end"`
	Metadata    map[string]interface{} `bson:"metadata,omitempty" json:"metadata,omitempty"`
}

// SlideCategories represents categorization metadata for slides
type SlideCategories struct {
	Subject      string   `bson:"subject" json:"subject"`
	SubjectTags  []string `bson:"subject_tags" json:"subject_tags"`
	Style        string   `bson:"style" json:"style"`
	StyleTags    []string `bson:"style_tags" json:"style_tags"`
	Audience     string   `bson:"audience" json:"audience"`
	AudienceTags []string `bson:"audience_tags" json:"audience_tags"`
	Complexity   string   `bson:"complexity" json:"complexity"`
	Topics       []string `bson:"topics" json:"topics"`
}

// SlideMetadata represents metadata for a slide deck
type SlideMetadata struct {
	TotalSlides       int                    `bson:"total_slides" json:"total_slides"`
	EstimatedDuration int                    `bson:"estimated_duration" json:"estimated_duration"`
	DifficultyLevel   string                 `bson:"difficulty_level" json:"difficulty_level"`
	TargetAudience    string                 `bson:"target_audience" json:"target_audience"`
	GeneratedAt       time.Time              `bson:"generated_at" json:"generated_at"`
	UserID            string                 `bson:"user_id" json:"user_id"`
	Context           map[string]interface{} `bson:"context" json:"context"`
}

// Slide represents generated slide decks with all content
type Slide struct {
	ID                primitive.ObjectID     `bson:"_id,omitempty" json:"id"`
	PromptID          string                 `bson:"promptId" json:"promptId"`
	Title             string                 `bson:"title" json:"title"`
	Sections          []string               `bson:"sections" json:"sections"`
	Bullets           [][]string             `bson:"bullets" json:"bullets"` // Array of arrays
	Examples          [][]string             `bson:"examples" json:"examples"`
	KeyPoints         [][]string             `bson:"key_points" json:"key_points"`
	ImagePlaceholders [][]string             `bson:"image_placeholders" json:"image_placeholders"`
	ImageMarkers      []ImageMarker          `bson:"image_markers" json:"image_markers"`
	TemplatePath      string                 `bson:"template_path,omitempty" json:"template_path,omitempty"`
	GeneratedNotes    []string               `bson:"generated_notes" json:"generated_notes"`
	SpeakerNotes      []SpeakerNote          `bson:"speaker_notes" json:"speaker_notes"`
	Style             string                 `bson:"style" json:"style"`
	MediaRefs         []string               `bson:"media_refs" json:"media_refs"`
	DiagramRefs       []string               `bson:"diagram_refs" json:"diagram_refs"`
	QuizRefs          []string               `bson:"quiz_refs" json:"quiz_refs"`
	LocalizedVersions []string               `bson:"localized_versions" json:"localized_versions"`
	Categories        SlideCategories        `bson:"categories" json:"categories"`
	TemplateMetadata  map[string]interface{} `bson:"template_metadata" json:"template_metadata"`
	Metadata          SlideMetadata          `bson:"metadata" json:"metadata"`
}
