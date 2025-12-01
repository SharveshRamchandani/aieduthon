package mongodb

import "time"

type Slide struct {
    SlideID            string    `bson:"_id,omitempty" json:"slideId"`
    PromptID           string    `bson:"promptId" json:"promptId"`
    UserID             string    `bson:"userId" json:"userId"`
    Title              string    `bson:"title" json:"title"`
    Sections           []string  `bson:"sections" json:"sections"`
    Bullets            []string  `bson:"bullets" json:"bullets"`
    SpeakerNotes       string    `bson:"speakerNotes" json:"speakerNotes"`
    Style              string    `bson:"style" json:"style"`
    MediaRefs          []string  `bson:"mediaRefs" json:"mediaRefs"`
    QuizRefs           []string  `bson:"quizRefs" json:"quizRefs"`
    TranslatedVersions []string  `bson:"translatedVersions" json:"translatedVersions"`
    CreatedAt          time.Time `bson:"createdAt" json:"createdAt"`
}