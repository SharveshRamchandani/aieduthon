package interaction

type GenerateQuiz struct {
	UserId     string `json:"userId"`
	QuizType   string `json:"quiz_type,omitempty"`
	Difficulty string `json:"difficulty,omitempty"`
}
