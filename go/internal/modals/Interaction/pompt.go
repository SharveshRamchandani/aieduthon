
package interaction

type ReceivedPrompts struct {
	Prompt          string         `json:"prompt"`
	UserId          string         `json:"userId"`
	Locale          string         `json:"locale"`
	Context         map[string]any `json:"context"`
	GenerateImages  bool           `json:"generate_images"`
	GenerateDiagrams bool          `json:"generate_diagrams"`
	EstimatedSlides *int           `json:"estimated_slides,omitempty"`
	QuizQuestions   *int           `json:"quiz_questions,omitempty"`
	QuizType        string         `json:"quiz_type,omitempty"`
	AudienceLevel   string         `json:"audience_level,omitempty"`
	PresentationStyle string       `json:"presentation_style,omitempty"`
}