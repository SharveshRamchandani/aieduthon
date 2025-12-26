package interaction

type GenerateSpeakerNotes struct {
	UserId            string `json:"userId"`
	AudienceLevel     string `json:"audience_level,omitempty"`
	PresentationStyle string `json:"presentation_style,omitempty"`
}
