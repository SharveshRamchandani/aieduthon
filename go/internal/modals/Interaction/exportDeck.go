package interaction

type ExportDeck struct {
	OutputDir *string `json:"output_dir,omitempty"`
	Format    string  `json:"format"` // "pptx" or "pdf"
	UserName  string  `json:"user_name"`
}
