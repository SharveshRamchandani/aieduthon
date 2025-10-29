"""
Test script for AI agents - demonstrates the core pipeline
"""

import json
from datetime import datetime
from agents.prompt_to_slide_agent import PromptToSlideAgent
from agents.quiz_generation_agent import QuizGenerationAgent
from agents.speaker_notes_agent import SpeakerNotesAgent


def test_ai_pipeline():
    """Test the complete AI pipeline"""
    print("🤖 Testing AI Presentation Generation Pipeline")
    print("=" * 60)
    
    # Sample prompt
    prompt = """
    Create a presentation about Photosynthesis for 10th grade students.
    Cover the basic process, importance for life on Earth, and include 
    practical examples. Make it engaging and educational.
    """
    
    user_id = "test_user_001"
    
    print(f"📝 Input Prompt: {prompt[:100]}...")
    print()
    
    # Step 1: Generate slides
    print("1️⃣ Generating slides...")
    slide_agent = PromptToSlideAgent()
    slide_result = slide_agent.generate_slides(
        prompt_text=prompt,
        user_id=user_id,
        locale="en",
        context={"grade_level": "10th", "subject": "biology"}
    )
    
    if slide_result["success"]:
        deck_id = slide_result["deck_id"]
        slide_deck = slide_result["slide_deck"]
        print(f"✅ Generated {slide_deck.total_slides} slides")
        print(f"   Title: {slide_deck.title}")
        print(f"   Duration: {slide_deck.estimated_duration} seconds")
        print(f"   Difficulty: {slide_deck.difficulty_level}")
        print()
        
        # Step 2: Generate quiz
        print("2️⃣ Generating quiz...")
        quiz_agent = QuizGenerationAgent()
        quiz_result = quiz_agent.generate_quiz(
            deck_id=deck_id,
            user_id=user_id,
            quiz_type="comprehensive"
        )
        
        if quiz_result["success"]:
            quizzes = quiz_result["quizzes"]
            total_questions = sum(q.total_questions for q in quizzes)
            print(f"✅ Generated {len(quizzes)} quiz(es) with {total_questions} total questions")
            print()
            
            # Step 3: Generate speaker notes
            print("3️⃣ Generating speaker notes...")
            notes_agent = SpeakerNotesAgent()
            notes_result = notes_agent.generate_speaker_notes(
                deck_id=deck_id,
                user_id=user_id,
                audience_level="intermediate",
                presentation_style="educational"
            )
            
            if notes_result["success"]:
                speaker_notes = notes_result["speaker_notes"]
                print(f"✅ Generated speaker notes for {len(speaker_notes)} slides")
                print()
                
                # Display sample results
                print("📊 Sample Results:")
                print("-" * 40)
                
                # Show first slide
                if slide_deck.slides:
                    first_slide = slide_deck.slides[0]
                    print(f"First Slide: {first_slide.title}")
                    print(f"Bullets: {len(first_slide.bullets)}")
                    print(f"Examples: {len(first_slide.examples)}")
                
                # Show first quiz question
                if quizzes and quizzes[0].questions:
                    first_question = quizzes[0].questions[0]
                    print(f"\nFirst Quiz Question: {first_question.question_text}")
                    print(f"Type: {first_question.question_type}")
                    print(f"Difficulty: {first_question.difficulty}")
                
                # Show speaker notes sample
                if speaker_notes:
                    first_note = speaker_notes[0]
                    print(f"\nSpeaker Notes Sample:")
                    print(f"Main Points: {len(first_note.main_points)}")
                    print(f"Talking Points: {len(first_note.talking_points)}")
                    print(f"Timing: {first_note.timing_notes}")
                
                print("\n🎉 Pipeline test completed successfully!")
                print(f"📁 All data saved to database with deck_id: {deck_id}")
                
            else:
                print(f"❌ Speaker notes generation failed: {notes_result['error']}")
        else:
            print(f"❌ Quiz generation failed: {quiz_result['error']}")
    else:
        print(f"❌ Slide generation failed: {slide_result['error']}")


def test_individual_agents():
    """Test individual agents separately"""
    print("\n🔬 Testing Individual Agents")
    print("=" * 40)
    
    # Test prompt analysis
    slide_agent = PromptToSlideAgent()
    test_prompt = "Explain machine learning basics for college students"
    
    print("Testing prompt analysis...")
    analysis = slide_agent._analyze_prompt(test_prompt, {"grade_level": "college"})
    print(f"Detected subject: {analysis['subject']}")
    print(f"Complexity: {analysis['complexity']}")
    print(f"Estimated slides: {analysis['estimated_slides']}")
    print(f"Topics: {analysis['key_topics']}")


if __name__ == "__main__":
    try:
        test_ai_pipeline()
        test_individual_agents()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
