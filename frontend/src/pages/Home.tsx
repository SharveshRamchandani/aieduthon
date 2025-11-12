import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { Sparkles, Image, Network, Loader2 } from 'lucide-react';
import { orchestrate } from '@/lib/api';

const Home = () => {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generateImages, setGenerateImages] = useState(true);
  const [generateDiagrams, setGenerateDiagrams] = useState(true);
  const [gradeLevel, setGradeLevel] = useState('');
  const [subject, setSubject] = useState('');
  const [locale, setLocale] = useState('en');
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
    try {
      const context: Record<string, any> = {};
      if (gradeLevel) context.grade_level = gradeLevel;
      if (subject) context.subject = subject;
      if (generateImages || generateDiagrams) context.generate_media = true;

      const data = await orchestrate({
        prompt,
        userId: 'demo-user',
        locale,
        context,
        generate_images: generateImages,
        generate_diagrams: generateDiagrams,
      });

      setIsGenerating(false);
      
      toast({
        title: 'Success',
        description: `Presentation generated! ${data.mediaGenerated ? 'Images and diagrams included.' : ''}`,
      });

      navigate(`/editor/${data.deckId}`);
    } catch (err) {
      setIsGenerating(false);
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to generate slides',
        variant: 'destructive',
      });
    }
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
                disabled={isGenerating}
              />
              <div className="text-sm text-muted-foreground">
                Be specific about your topic, target audience, and any key points you want to cover
              </div>
            </div>

            {/* Advanced Options */}
            <div className="space-y-4 border-t border-border pt-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Grade Level (Optional)</Label>
                  <Input
                    placeholder="e.g., 10th, College"
                    value={gradeLevel}
                    onChange={(e) => setGradeLevel(e.target.value)}
                    disabled={isGenerating}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Subject (Optional)</Label>
                  <Input
                    placeholder="e.g., Biology, Math"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    disabled={isGenerating}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Language</Label>
                <Select value={locale} onValueChange={setLocale} disabled={isGenerating}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="hi">Hindi</SelectItem>
                    <SelectItem value="ta">Tamil</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-3">
                <Label className="text-base font-semibold">Multimodal Features</Label>
                <div className="flex items-center justify-between p-3 border border-border rounded-lg">
                  <div className="flex items-center gap-2">
                    <Image className="h-5 w-5" />
                    <span>Generate Images</span>
                  </div>
                  <Switch
                    checked={generateImages}
                    onCheckedChange={setGenerateImages}
                    disabled={isGenerating}
                  />
                </div>
                <div className="flex items-center justify-between p-3 border border-border rounded-lg">
                  <div className="flex items-center gap-2">
                    <Network className="h-5 w-5" />
                    <span>Generate Diagrams</span>
                  </div>
                  <Switch
                    checked={generateDiagrams}
                    onCheckedChange={setGenerateDiagrams}
                    disabled={isGenerating}
                  />
                </div>
              </div>
            </div>

            <Button
              onClick={generateSlides}
              disabled={isGenerating}
              size="lg"
              className="w-full rounded-xl text-base py-6"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Generating Presentation...
                </>
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
