package mongodb	

import "time"

type Translation struct {
    TranslationID      string    `bson:"_id,omitempty" json:"translationId"`
    SlideID            string    `bson:"slideId" json:"slideId"`
    LangCode           string    `bson:"langCode" json:"langCode"`
    TranslatedSections []string  `bson:"translatedSections" json:"translatedSections"`
    Locale             string    `bson:"locale" json:"locale"`
    LocalExamples      []string  `bson:"localExamples" json:"localExamples"`
    LocalImages        []string  `bson:"localImages" json:"localImages"`
    CreatedAt          time.Time `bson:"createdAt" json:"createdAt"`
}