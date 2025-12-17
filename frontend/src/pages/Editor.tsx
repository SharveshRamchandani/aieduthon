import { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { Plus, Trash2, Download, ChevronLeft, ChevronRight, Send, Image, Network, Loader2, Sparkles, Search, Type, LayoutGrid, Orbit, BarChart3, Film, Globe2, PenSquare } from 'lucide-react';
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
  const defaultTitle = 'Agile Methodology in Software Development: Embracing Change for Success';
  const defaultContent = 'Discover how Agile transforms software development through flexibility, collaboration, and continuous improvement';

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

  const updateSlide = (index: number, field: keyof Slide, value: string) => {
    if (!presentation) return;

    const updatedSlides = [...presentation.slides];
    updatedSlides[index] = {
      ...updatedSlides[index],
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

  const deleteSlide = (targetIndex?: number) => {
    if (!presentation || presentation.slides.length <= 1) {
      toast({
        title: 'Error',
        description: 'Cannot delete the last slide',
        variant: 'destructive',
      });
      return;
    }

    const index = targetIndex ?? currentSlideIndex;
    const updatedSlides = presentation.slides.filter((_, i) => i !== index);
    savePresentation({ ...presentation, slides: updatedSlides });
    setCurrentSlideIndex(Math.max(0, index - 1));
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

  const slideRefs = useRef<Array<HTMLDivElement | null>>([]);

  const handleAiAssist = () => {
    if (!aiPrompt.trim()) return;
    
    toast({
      title: 'AI Assistance',
      description: 'AI editing features coming soon!',
    });
    setAiPrompt('');
  };

  const handleSlideClick = (index: number, event: React.MouseEvent) => {
    const target = event.target as HTMLElement;
    if (target.closest('[data-editable]')) return;
    setCurrentSlideIndex(index);
  };

  const goToSlide = (index: number) => {
    setCurrentSlideIndex(index);
    const el = slideRefs.current[index];
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start', inline: 'nearest' });
    }
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

  return (
    <div className="min-h-screen bg-background">
      <TopBar />

      {/* Right-side vertical toolbar */}
      <div className="fixed right-4 top-1/2 -translate-y-1/2 z-30 flex flex-col gap-3 rounded-2xl border border-border bg-card shadow-xl p-3 backdrop-blur">
        <Button
          variant="ghost"
          size="icon"
          className="h-10 w-10 text-slate-200 hover:bg-muted"
          aria-label="Add slide"
          title="Add slide"
          onClick={addSlide}
        >
          <Plus className="h-5 w-5" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-10 w-10 text-slate-200 hover:bg-muted"
          aria-label="Delete slide"
          title="Delete slide"
          onClick={() => deleteSlide()}
        >
          <Trash2 className="h-5 w-5" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-10 w-10 text-slate-200 hover:bg-muted"
          aria-label="Generate media"
          title="Generate media"
          onClick={handleGenerateMedia}
          disabled={isGeneratingMedia}
        >
          {isGeneratingMedia ? <Loader2 className="h-5 w-5 animate-spin" /> : <Image className="h-5 w-5" />}
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-10 w-10 text-slate-200 hover:bg-muted"
          aria-label="Export"
          title="Export"
          onClick={exportPresentation}
          disabled={isExporting}
        >
          {isExporting ? <Loader2 className="h-5 w-5 animate-spin" /> : <Download className="h-5 w-5" />}
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-10 w-10 text-slate-200 hover:bg-muted"
          aria-label="Generate notes"
          title="Generate notes"
          onClick={handleGenerateNotes}
        >
          <Sparkles className="h-5 w-5" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-10 w-10 text-slate-200 hover:bg-muted"
          aria-label="Generate quiz"
          title="Generate quiz"
          onClick={handleGenerateQuiz}
        >
          <Network className="h-5 w-5" />
        </Button>
      </div>

      {/* Left filmstrip */}
      <div className="fixed left-4 top-24 bottom-6 z-20 w-64 overflow-hidden rounded-3xl border border-border bg-card shadow-2xl flex flex-col">
        <div className="px-3 pt-3 pb-2 flex items-center gap-2">
          {/* <Button variant="ghost" size="icon" className="h-9 w-9" aria-label="Filmstrip view">
            <Film className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" className="h-9 w-9" aria-label="List view">
            <LayoutGrid className="h-4 w-4" />
          </Button> */}
          <div className="flex-2" />
          
          <Button variant="ghost" className="h-9 px-3" aria-label="New slide" onClick={addSlide}>
            Pages
          </Button>

          <Button variant="ghost" size="icon" className="h-9 w-9" aria-label="Add slide" onClick={addSlide}>
            <Plus className="h-4 w-4" />
          </Button>
        </div>
        <div className="px-3 pb-3 flex-1 overflow-y-auto space-y-3">
          {presentation.slides.map((slide, index) => {
            const isActive = currentSlideIndex === index;
            const thumbStyle = slide.imageUrl
              ? { backgroundImage: `url(${slide.imageUrl})` }
              : { backgroundImage: 'linear-gradient(135deg, #1f2937, #0f172a)' };
            return (
              <button
                key={slide.id}
                onClick={() => goToSlide(index)}
                className={`w-full text-left rounded-2xl border transition overflow-hidden group ${
                  isActive ? 'border-primary shadow-lg ring-1 ring-primary/50 bg-primary/5' : 'border-border hover:border-primary/60 bg-card'
                }`}
              >
                <div
                  className="relative h-28 w-full bg-cover bg-center"
                  style={thumbStyle}
                >
                  <div className="absolute inset-0 bg-black/25 group-hover:bg-black/15 transition" />
                  <div className="absolute left-2 bottom-2 h-7 w-7 rounded-md bg-background/90 text-xs font-semibold text-foreground flex items-center justify-center">
                    {index + 1}
                  </div>
                </div>
                <div className="px-3 py-2 bg-card">
                  <p className="text-sm font-semibold truncate">{slide.title || `Slide ${index + 1}`}</p>
                  <p className="text-xs text-muted-foreground line-clamp-2">{slide.content || 'Add content'}</p>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      <div className="container mx-auto px-4 pt-20 pb-16 pl-0 md:pl-[19rem]">
        <div className="space-y-10 pt-9">
          {presentation.slides.map((slide, index) => (
            <div
              key={slide.id}
              className="space-y-4"
              onClick={(e) => handleSlideClick(index, e)}
            >
              {/* <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">Slide {index + 1} of {presentation.slides.length}</p>
              </div> */}

              <div className="aspect-video relative overflow-hidden rounded-2xl border-2 border-border bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 shadow-xl flex items-center justify-center max-w-4xl mx-auto p-4">
                {slide.imageUrl && (
                  <img
                    src={slide.imageUrl}
                    alt={slide.title}
                    className="absolute inset-0 h-full w-full object-cover opacity-20"
                  />
                )}

                <div className="pointer-events-none absolute inset-0">
                  <div className="absolute -left-10 top-1/4 h-64 w-64 rounded-full bg-primary/20 blur-3xl" />
                  <div className="absolute right-0 top-0 h-48 w-48 rounded-full bg-white/5 blur-2xl" />
                </div>

                <div className="absolute left-6 top-8 h-16 w-1.5 rounded-full bg-primary shadow-[0_0_30px_rgba(59,130,246,0.45)]" />

                <div className="relative z-10 max-w-2xl px-6 text-center space-y-4">
                  <p className="text-xs uppercase tracking-[0.35em] text-primary/80">Presentation Preview</p>
                  <h1
                    className="text-3xl md:text-4xl font-bold text-white leading-tight focus:outline-none focus:ring-2 focus:ring-primary/60 rounded-md px-2"
                    contentEditable
                    suppressContentEditableWarning
                    data-editable
                    onInput={(e) => updateSlide(index, 'title', e.currentTarget.innerText)}
                    onBlur={(e) => updateSlide(index, 'title', e.currentTarget.innerText.trim())}
                    spellCheck={false}
                  >
                    {slide.title || defaultTitle}
                  </h1>
                  <p
                    className="text-base md:text-lg text-slate-200/80 whitespace-pre-line focus:outline-none focus:ring-2 focus:ring-primary/60 rounded-md px-3 py-2"
                    contentEditable
                    suppressContentEditableWarning
                    data-editable
                    onInput={(e) => updateSlide(index, 'content', e.currentTarget.innerText)}
                    onBlur={(e) => updateSlide(index, 'content', e.currentTarget.innerText.trim())}
                    spellCheck={false}
                  >
                    {slide.content || defaultContent}
                  </p>
                </div>

                {slide.diagramUrl && (
                  <div className="absolute bottom-6 right-6 w-32 h-32 border border-border rounded-lg bg-background/80 p-2 shadow-lg">
                    <img 
                      src={slide.diagramUrl} 
                      alt="Diagram"
                      className="h-full w-full object-contain"
                    />
                  </div>
                )}
              </div>

              {slide.speakerNotes && (
                <div className="space-y-2 bg-card border border-border rounded-2xl p-6">
                  <div className="space-y-2">
                    <Label>Speaker Notes</Label>
                    <div className="p-3 bg-muted rounded-lg text-sm space-y-2">
                      <div>
                        <strong>Main Points:</strong>
                        <ul className="list-disc list-inside ml-2">
                          {slide.speakerNotes.main_points?.map((point: string, i: number) => (
                            <li key={i}>{point}</li>
                          ))}
                        </ul>
                      </div>
                      {slide.speakerNotes.timing_notes && (
                        <div>
                          <strong>Timing:</strong> {slide.speakerNotes.timing_notes}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Editor;
