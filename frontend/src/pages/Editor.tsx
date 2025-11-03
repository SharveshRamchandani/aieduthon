import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { Plus, Trash2, Download, ChevronLeft, ChevronRight, Send } from 'lucide-react';

interface Slide {
  id: string;
  title: string;
  content: string;
  imageUrl: string;
}

interface Presentation {
  id: string;
  title: string;
  slides: Slide[];
  createdAt: string;
}

const Editor = () => {
  const { id } = useParams();
  const [presentation, setPresentation] = useState<Presentation | null>(null);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [aiPrompt, setAiPrompt] = useState('');
  const { toast } = useToast();

  useEffect(() => {
    if (id) {
      const stored = localStorage.getItem(`presentation_${id}`);
      if (stored) {
        setPresentation(JSON.parse(stored));
      }
    }
  }, [id]);

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

  const exportPresentation = () => {
    toast({
      title: 'Export Coming Soon',
      description: 'PPTX export functionality will be available in the next update',
    });
  };

  const handleAiAssist = () => {
    if (!aiPrompt.trim()) return;
    
    toast({
      title: 'AI Assistance',
      description: 'AI editing features coming soon!',
    });
    setAiPrompt('');
  };

  if (!presentation) {
    return <div className="min-h-screen bg-background flex items-center justify-center">Loading...</div>;
  }

  const currentSlide = presentation.slides[currentSlideIndex];

  return (
    <div className="min-h-screen bg-background">
      <TopBar />
      
      <div className="container mx-auto px-4 pt-20 pb-16">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Slide Preview */}
          <div className="space-y-4">
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

            <div className="aspect-video bg-card border-2 border-border rounded-2xl p-12 flex flex-col items-center justify-center text-center">
              <h1 className="text-5xl font-bold mb-6">{currentSlide.title}</h1>
              <p className="text-lg text-muted-foreground max-w-2xl">{currentSlide.content}</p>
            </div>

            <div className="flex gap-2">
              <Button onClick={addSlide} variant="outline" className="flex-1">
                <Plus className="h-4 w-4 mr-2" />
                Add Slide
              </Button>
              <Button onClick={deleteSlide} variant="outline" className="flex-1">
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </Button>
              <Button onClick={exportPresentation} className="flex-1">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </div>

          {/* Editor Panel */}
          <div className="space-y-6">
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
              </div>
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
