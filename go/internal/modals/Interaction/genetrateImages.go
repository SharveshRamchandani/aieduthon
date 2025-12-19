package interaction

type GenerateImages struct{
	PromptText string `json:"prompt"`
	ImgWidth int `json:"width"`
	ImgHeight int `json:"height"`
}