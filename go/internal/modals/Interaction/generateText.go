package interaction

type GenerateText struct {
	PromptText string `json:"prompt"`
	Context map[string]any `json:"context"`
}