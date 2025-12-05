import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { Plus, Trash2, Download, ChevronLeft, ChevronRight, Send, Image, Network, Loader2, Sparkles } from 'lucide-react';
import { getDeck, generateMediaForDeck, exportDeck, generateSpeakerNotes, generateQuiz, SlideDeck } from '@/lib/api';

interface Slide {
  id: string;
  title: string;
  content: string;
  imageUrl: string;
  diagramUrl?: string;
  speakerNotes?: any;
}

interface Presentation {
  id: string;
  title: string;
  slides: Slide[];
  createdAt: string;
  metadata?: any;
}

const Editor = () => {
  const { id } = useParams();
  const [presentation, setPresentation] = useState<Presentation | null>(null);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [aiPrompt, setAiPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isGeneratingMedia, setIsGeneratingMedia] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    const loadDeck = async () => {
      if (!id) return;

      setIsLoading(true);
      try {
        const deck: SlideDeck = await getDeck(id);
        
        // Convert deck to presentation format
        const slides: Slide[] = deck.sections.map((section, index) => {
          const bullets = deck.bullets[index] || [];
          const mediaRefs = deck.media_refs?.[index] || [];
          const diagramRefs = deck.diagram_refs?.[index] || [];
          
          return {
            id: `${index}`,
            title: section,
            content: bullets.join('\n'),
            imageUrl: mediaRefs[0] || '',
            diagramUrl: diagramRefs[0] || '',
            speakerNotes: deck.speaker_notes?.[index],
          };
        });

        const presentation: Presentation = {
          id: deck._id,
          title: deck.title,
          slides,
          createdAt: new Date().toISOString(),
          metadata: deck.metadata,
        };

        setPresentation(presentation);
        localStorage.setItem(`presentation_${id}`, JSON.stringify(presentation));
      } catch (err) {
        toast({
          title: 'Error',
          description: err instanceof Error ? err.message : 'Failed to load deck',
          variant: 'destructive',
        });
        
        // Try to load from localStorage as fallback
        const stored = localStorage.getItem(`presentation_${id}`);
        if (stored) {
          setPresentation(JSON.parse(stored));
        }
      } finally {
        setIsLoading(false);
      }
    };

    loadDeck();
  }, [id, toast]);

  const savePresentation = (updated: Presentation) => {
    localStorage.setItem(`presentation_${id}`, JSON.stringify(updated));
    setPresentation(updated);
  };

  const updateSlide = (field: keyof Slide, value: string) => {
    if (!presentation) return;

    const updatedSlides = [...presentation.slides];
    updatedSlides[currentSlideIndex] = {
      ...updatedSlides[currentSlideIndex],
      [field]: value,
    };

    savePresentation({ ...presentation, slides: updatedSlides });
  };

  const addSlide = () => {
    if (!presentation) return;

    const newSlide: Slide = {
      id: Date.now().toString(),
      title: 'New Slide',
      content: 'Enter your content here...',
      imageUrl: '',
    };

    const updatedSlides = [...presentation.slides, newSlide];
    savePresentation({ ...presentation, slides: updatedSlides });
    setCurrentSlideIndex(updatedSlides.length - 1);
  };

  const deleteSlide = () => {
    if (!presentation || presentation.slides.length <= 1) {
      toast({
        title: 'Error',
        description: 'Cannot delete the last slide',
        variant: 'destructive',
      });
      return;
    }

    const updatedSlides = presentation.slides.filter((_, i) => i !== currentSlideIndex);
    savePresentation({ ...presentation, slides: updatedSlides });
    setCurrentSlideIndex(Math.max(0, currentSlideIndex - 1));
  };

  const exportPresentation = async () => {
    if (!id) return;

    setIsExporting(true);
    try {
      const result = await exportDeck(id);
      toast({
        title: 'Success',
        description: `Presentation exported to ${result.filePath}`,
      });
    } catch (err) {
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to export presentation',
        variant: 'destructive',
      });
    } finally {
      setIsExporting(false);
    }
  };

  const handleGenerateMedia = async () => {
    if (!id) return;

    setIsGeneratingMedia(true);
    try {
      const result = await generateMediaForDeck(id, true, true);
      toast({
        title: 'Success',
        description: 'Media generated successfully!',
      });
      
      // Reload deck to get new media
      const deck: SlideDeck = await getDeck(id);
      const slides: Slide[] = deck.sections.map((section, index) => {
        const bullets = deck.bullets[index] || [];
        const mediaRefs = deck.media_refs?.[index] || [];
        const diagramRefs = deck.diagram_refs?.[index] || [];
        
        return {
          id: `${index}`,
          title: section,
          content: bullets.join('\n'),
          imageUrl: mediaRefs[0] || '',
          diagramUrl: diagramRefs[0] || '',
          speakerNotes: deck.speaker_notes?.[index],
        };
      });

      if (presentation) {
        const updated = { ...presentation, slides };
        setPresentation(updated);
        localStorage.setItem(`presentation_${id}`, JSON.stringify(updated));
      }
    } catch (err) {
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to generate media',
        variant: 'destructive',
      });
    } finally {
      setIsGeneratingMedia(false);
    }
  };

  const handleGenerateNotes = async () => {
    if (!id) return;

    try {
      await generateSpeakerNotes(id, 'demo-user');
      toast({
        title: 'Success',
        description: 'Speaker notes generated! Reloading...',
      });
      
      // Reload deck
      const deck: SlideDeck = await getDeck(id);
      const slides: Slide[] = deck.sections.map((section, index) => {
        const bullets = deck.bullets[index] || [];
        const mediaRefs = deck.media_refs?.[index] || [];
        const diagramRefs = deck.diagram_refs?.[index] || [];
        
        return {
          id: `${index}`,
          title: section,
          content: bullets.join('\n'),
          imageUrl: mediaRefs[0] || '',
          diagramUrl: diagramRefs[0] || '',
          speakerNotes: deck.speaker_notes?.[index],
        };
      });

      if (presentation) {
        const updated = { ...presentation, slides };
        setPresentation(updated);
        localStorage.setItem(`presentation_${id}`, JSON.stringify(updated));
      }
    } catch (err) {
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to generate notes',
        variant: 'destructive',
      });
    }
  };

  const handleGenerateQuiz = async () => {
    if (!id) return;

    try {
      const result = await generateQuiz(id, 'demo-user');
      toast({
        title: 'Success',
        description: `Quiz generated! Quiz IDs: ${result.quiz_ids.join(', ')}`,
      });
    } catch (err) {
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to generate quiz',
        variant: 'destructive',
      });
    }
  };

  const handleAiAssist = () => {
    if (!aiPrompt.trim()) return;
    
    toast({
      title: 'AI Assistance',
      description: 'AI editing features coming soon!',
    });
    setAiPrompt('');
  };

  if (isLoading || !presentation) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin" />
          <p>Loading presentation...</p>
        </div>
      </div>
    );
  }

  const currentSlide = presentation.slides[currentSlideIndex];

  return (
    <div className="min-h-screen bg-background">
      <TopBar />
      
      <div className="container mx-auto px-4 pt-20 pb-16">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Slide Preview */}
          <div className="lg:col-span-2 space-y-4 pt-9">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Preview</h2>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setCurrentSlideIndex(Math.max(0, currentSlideIndex - 1))}
                  disabled={currentSlideIndex === 0}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <div className="px-4 py-2 border border-border rounded-md text-sm">
                  {currentSlideIndex + 1} / {presentation.slides.length}
                </div>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setCurrentSlideIndex(Math.min(presentation.slides.length - 1, currentSlideIndex + 1))}
                  disabled={currentSlideIndex === presentation.slides.length - 1}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* <div className="aspect-video bg-card border-2 border-border rounded-2xl p-8 flex flex-col items-center justify-center text-center">
              <h1 className="text-5xl font-bold mb-6">{currentSlide.title}</h1>
              <p className="text-lg text-muted-foreground max-w-2xl">{currentSlide.content}</p> */}
            <div className="aspect-video bg-card border-2 border-border rounded-2xl p-12 flex flex-col items-center justify-center text-center relative overflow-hidden">
              <h1 className="text-5xl font-bold mb-6 z-10">{currentSlide.title}</h1>
              <p className="text-lg text-muted-foreground max-w-2xl z-10 whitespace-pre-line">{currentSlide.content}</p>
              
              {/* Display generated image if available */}
              {currentSlide.imageUrl && (
                <div className="absolute inset-0 opacity-20 z-0">
                  <img 
                    src={currentSlide.imageUrl} 
                    alt={currentSlide.title}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}
              
              {/* Display diagram if available */}
              {currentSlide.diagramUrl && (
                <div className="absolute bottom-4 right-4 w-32 h-32 border border-border rounded-lg bg-background/80 p-2 z-10">
                  <img 
                    src={currentSlide.diagramUrl} 
                    alt="Diagram"
                    className="w-full h-full object-contain"
                  />
                </div>
              )}
            </div>

            <div className="flex gap-2 flex-wrap">
              <Button onClick={addSlide} variant="outline" className="flex-1 min-w-[120px]">
                <Plus className="h-4 w-4 mr-2" />
                Add Slide
              </Button>
              <Button onClick={deleteSlide} variant="outline" className="flex-1 min-w-[120px]">
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </Button>
              <Button 
                onClick={handleGenerateMedia} 
                variant="outline" 
                className="flex-1 min-w-[120px]"
                disabled={isGeneratingMedia}
              >
                {isGeneratingMedia ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Image className="h-4 w-4 mr-2" />
                )}
                Generate Media
              </Button>
              <Button onClick={exportPresentation} className="flex-1 min-w-[120px]" disabled={isExporting}>
                {isExporting ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Download className="h-4 w-4 mr-2" />
                )}
                Export
              </Button>
            </div>

            {/* AI Features */}
            <div className="flex gap-2 flex-wrap pt-2 border-t border-border">
              <Button onClick={handleGenerateNotes} variant="outline" size="sm" className="flex-1">
                <Sparkles className="h-4 w-4 mr-2" />
                Generate Notes
              </Button>
              <Button onClick={handleGenerateQuiz} variant="outline" size="sm" className="flex-1">
                <Network className="h-4 w-4 mr-2" />
                Generate Quiz
              </Button>
            </div>
          </div>

          {/* Editor Panel */}
          <div className="lg:col-span-1 space-y-6 pt-9">
            <h2 className="text-2xl font-bold">Edit Slide</h2>
            
            <div className="space-y-4 bg-card border border-border rounded-2xl p-6">
              <div className="space-y-2">
                <Label>Title</Label>
                <Input
                  value={currentSlide.title}
                  onChange={(e) => updateSlide('title', e.target.value)}
                  className="text-lg font-semibold"
                />
              </div>

              <div className="space-y-2">
                <Label>Content</Label>
                <Textarea
                  value={currentSlide.content}
                  onChange={(e) => updateSlide('content', e.target.value)}
                  className="min-h-[200px] resize-none"
                />
              </div>

              <div className="space-y-2">
                <Label>Image URL (Optional)</Label>
                <Input
                  value={currentSlide.imageUrl}
                  onChange={(e) => updateSlide('imageUrl', e.target.value)}
                  placeholder="https://..."
                />
                {currentSlide.imageUrl && (
                  <div className="mt-2 rounded-lg overflow-hidden border border-border">
                    <img src={currentSlide.imageUrl} alt="Slide image" className="w-full h-32 object-cover" />
                  </div>
                )}
              </div>

              {currentSlide.diagramUrl && (
                <div className="space-y-2">
                  <Label>Diagram</Label>
                  <div className="rounded-lg overflow-hidden border border-border">
                    <img src={currentSlide.diagramUrl} alt="Diagram" className="w-full h-48 object-contain bg-background" />
                  </div>
                </div>
              )}

              {currentSlide.speakerNotes && (
                <div className="space-y-2">
                  <Label>Speaker Notes</Label>
                  <div className="p-3 bg-muted rounded-lg text-sm space-y-2">
                    <div>
                      <strong>Main Points:</strong>
                      <ul className="list-disc list-inside ml-2">
                        {currentSlide.speakerNotes.main_points?.map((point: string, i: number) => (
                          <li key={i}>{point}</li>
                        ))}
                      </ul>
                    </div>
                    {currentSlide.speakerNotes.timing_notes && (
                      <div>
                        <strong>Timing:</strong> {currentSlide.speakerNotes.timing_notes}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="space-y-2 bg-card border border-border rounded-2xl p-6">
              <Label>AI Assistant</Label>
              <div className="flex gap-2">
                <Input
                  value={aiPrompt}
                  onChange={(e) => setAiPrompt(e.target.value)}
                  placeholder="Ask AI to edit this slide..."
                  onKeyDown={(e) => e.key === 'Enter' && handleAiAssist()}
                />
                <Button onClick={handleAiAssist} size="icon">
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Editor;
