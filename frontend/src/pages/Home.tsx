import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';
import { Sparkles } from 'lucide-react';

const Home = () => {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const generateSlides = async () => {
    if (!prompt.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a topic or prompt',
        variant: 'destructive',
      });
      return;
    }

    setIsGenerating(true);

    // Simulate AI generation
    setTimeout(() => {
      const mockSlides = [
        {
          id: '1',
          title: 'Introduction',
          content: `Welcome to ${prompt}. This presentation will cover the key concepts and important details.`,
          imageUrl: '',
        },
        {
          id: '2',
          title: 'Key Concepts',
          content: 'Understanding the fundamental principles and core ideas behind this topic.',
          imageUrl: '',
        },
        {
          id: '3',
          title: 'Detailed Explanation',
          content: 'Deep dive into the specifics, examples, and practical applications.',
          imageUrl: '',
        },
        {
          id: '4',
          title: 'Summary',
          content: 'Key takeaways and important points to remember from this presentation.',
          imageUrl: '',
        },
      ];

      const presentationId = Date.now().toString();
      localStorage.setItem(`presentation_${presentationId}`, JSON.stringify({
        id: presentationId,
        title: prompt,
        slides: mockSlides,
        createdAt: new Date().toISOString(),
      }));

      setIsGenerating(false);
      navigate(`/editor/${presentationId}`);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-background">
      <TopBar />
      
      <div className="container mx-auto px-4 pt-32 pb-16">
        <div className="max-w-3xl mx-auto space-y-8">
          <div className="text-center space-y-4">
            <h1 className="text-5xl font-bold tracking-tight">
              What would you like to create?
            </h1>
            <p className="text-lg text-muted-foreground">
              Describe your presentation topic and let AI do the rest
            </p>
          </div>

          <div className="bg-card border border-border rounded-2xl p-8 space-y-6">
            <div className="space-y-3">
              <Textarea
                placeholder="E.g., 'Photosynthesis for Class 10' or 'Introduction to Machine Learning'..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="min-h-[200px] text-base resize-none rounded-xl"
              />
              <div className="text-sm text-muted-foreground">
                Be specific about your topic, target audience, and any key points you want to cover
              </div>
            </div>

            <Button
              onClick={generateSlides}
              disabled={isGenerating}
              size="lg"
              className="w-full rounded-xl text-base py-6"
            >
              {isGenerating ? (
                'Generating Presentation...'
              ) : (
                <>
                  Generate Presentation
                  <Sparkles className="ml-2 h-5 w-5" />
                </>
              )}
            </Button>
          </div>

         
        </div>
      </div>
    </div>
  );
};

export default Home;
