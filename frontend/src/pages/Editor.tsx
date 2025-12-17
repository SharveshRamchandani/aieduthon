import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { Plus, Trash2, Download, ChevronLeft, ChevronRight, Send, Image, Network, Loader2, Sparkles, Search, Type, LayoutGrid, Orbit, BarChart3, Film, Globe2, PenSquare, List, X, MessageSquare, MonitorPlay } from 'lucide-react';
import { getDeck, generateMediaForDeck, exportDeck, generateSpeakerNotes, generateQuiz, downloadDeckImages, SlideDeck } from '@/lib/api';

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
  const [viewMode, setViewMode] = useState<'filmstrip' | 'list'>('filmstrip');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isPresenting, setIsPresenting] = useState(false);
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
        const normalizeDiagramUrl = (url?: string) => {
          if (!url) return '';
          if (url.startsWith('http') || url.startsWith('/media') || url.startsWith('data:')) return url;
          return '';
        };

        const slides: Slide[] = deck.sections.map((section, index) => {
          const bullets = deck.bullets[index] || [];
          const mediaRefs = deck.media_refs?.[index] || [];
          const diagramRefs = deck.diagram_refs?.[index] || [];
          
          return {
            id: `${index}`,
            title: section,
            content: bullets.join('\n'),
            imageUrl: mediaRefs[0] || '',
            diagramUrl: normalizeDiagramUrl(diagramRefs[0]),
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
      await exportDeck(id);
      toast({
        title: 'Success',
        description: 'Presentation exported successfully!',
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
          diagramUrl: normalizeDiagramUrl(diagramRefs[0]),
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

  const handleDownloadImages = async () => {
    if (!id) return;

    try {
      await downloadDeckImages(id);
      toast({
        title: 'Success',
        description: 'Downloading all images used in this deck as a ZIP file.',
      });
    } catch (err) {
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to download images',
        variant: 'destructive',
      });
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
          diagramUrl: normalizeDiagramUrl(diagramRefs[0]),
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
      if (result && result.quiz_ids) {
        toast({
          title: 'Success',
          description: `Quiz generated! Quiz IDs: ${result.quiz_ids.join(', ')}`,
        });
      } else {
        toast({
          title: 'Success',
          description: 'Quiz generated and downloaded!',
        });
      }
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

  const handleSlideClick = (index: number, event: React.MouseEvent) => {
    const target = event.target as HTMLElement;
    if (target.closest('[data-editable]')) return;
    setCurrentSlideIndex(index);
  };

  // Scroll to current slide when it changes
  useEffect(() => {
    if (presentation && isSidebarOpen) {
      const slideElement = document.getElementById(`slide-thumbnail-${currentSlideIndex}`);
      if (slideElement) {
        slideElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }
  }, [currentSlideIndex, presentation, isSidebarOpen]);

  // Keyboard controls when in presentation mode
  useEffect(() => {
    if (!isPresenting) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (!presentation) return;
      if (event.key === 'Escape') {
        setIsPresenting(false);
        return;
      }
      if (event.key === 'ArrowRight' || event.key === 'PageDown' || event.key === ' ') {
        setCurrentSlideIndex((prev) =>
          Math.min(prev + 1, presentation.slides.length - 1),
        );
      }
      if (event.key === 'ArrowLeft' || event.key === 'PageUp') {
        setCurrentSlideIndex((prev) => Math.max(prev - 1, 0));
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isPresenting, presentation]);

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
    <div className="min-h-screen bg-background flex">
      <TopBar />

      {/* Left Sidebar */}
      {isSidebarOpen && (
        <div className="fixed left-0 top-20 h-[calc(100vh-6rem)] w-80 bg-card border-r border-border z-20 flex flex-col">
          {/* Top Bar */}
          <div className="flex items-center justify-between p-3 border-b border-border bg-card">
            <div className="flex items-center gap-2">
              <p>Pages</p>
              {/* <Button
                variant="ghost"
                size="icon"
                className={`h-8 w-8 ${viewMode === 'filmstrip' ? 'bg-muted' : ''}`}
                onClick={() => setViewMode('filmstrip')}
                title="Filmstrip view"
              >
                <Film className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className={`h-8 w-8 ${viewMode === 'list' ? 'bg-muted' : ''}`}
                onClick={() => setViewMode('list')}
                title="List view"
              >
                <List className="h-4 w-4" />
              </Button> */}
            </div>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 px-3 text-sm"
                  onClick={addSlide}
                >
                  <Plus className="h-4 w-4 mr-1" />
                  New
                </Button>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={() => setIsSidebarOpen(false)}
                title="Close sidebar"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Slide Thumbnails */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3">
            {presentation.slides.map((slide, index) => (
              <div
                key={slide.id}
                id={`slide-thumbnail-${index}`}
                className={`relative cursor-pointer rounded-lg border-2 transition-all ${
                  currentSlideIndex === index
                    ? 'border-primary shadow-lg shadow-primary/20'
                    : 'border-border hover:border-muted-foreground/50'
                }`}
                onClick={() => {
                  setCurrentSlideIndex(index);
                  // Scroll to slide in main view
                  const slideElement = document.getElementById(`main-slide-${index}`);
                  if (slideElement) {
                    slideElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                  }
                }}
              >
                {/* Slide Number Badge */}
                <div className="absolute bottom-2 left-2 z-10 h-6 w-6 rounded-full bg-card/90 border border-border flex items-center justify-center">
                  <span className="text-xs font-medium text-foreground">{index + 1}</span>
                </div>

                {/* Slide Thumbnail Preview */}
                <div className="aspect-video relative overflow-hidden rounded-lg bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
                  {slide.imageUrl && (
                    <img
                      src={slide.imageUrl}
                      alt={slide.title}
                      className="absolute inset-0 h-full w-full object-cover opacity-30"
                    />
                  )}
                  
                  <div className="absolute inset-0 p-3 flex flex-col justify-center">
                    <h3 className="text-xs font-semibold text-white line-clamp-2 mb-1">
                      {slide.title || `Slide ${index + 1}`}
                    </h3>
                    {viewMode === 'list' && (
                      <p className="text-[10px] text-slate-300/70 line-clamp-2">
                        {slide.content || ''}
                      </p>
                    )}
                  </div>

                  {/* Selected indicator */}
                  {currentSlideIndex === index && (
                    <div className="absolute inset-0 border-2 border-primary rounded-lg pointer-events-none" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sidebar Toggle Button (when closed) */}
      {!isSidebarOpen && (
        <Button
          variant="ghost"
          size="icon"
          className="fixed left-4 top-20 z-20 h-10 w-10 bg-card border border-border"
          onClick={() => setIsSidebarOpen(true)}
          title="Open sidebar"
        >
          <Film className="h-5 w-5" />
        </Button>
      )}

      {/* Main Content Area */}
      <div className={`flex-1 transition-all ${isSidebarOpen ? 'ml-80' : 'ml-0'}`}>
        {/* Right-side vertical toolbar */}
        <div className="fixed right-4 top-1/2 -translate-y-1/2 z-30 flex flex-col gap-3 rounded-2xl border border-border bg-card/95 shadow-xl p-3">
        
        
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
          aria-label="Download images"
          title="Download images ZIP"
          onClick={handleDownloadImages}
        >
          <Image className="h-5 w-5" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-10 w-10 text-slate-200 hover:bg-muted"
          aria-label="Start presentation"
          title="Start presentation"
          onClick={() => setIsPresenting(true)}
        >
          <MonitorPlay className="h-5 w-5" />
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

      

      {/* AI Chat Button - Separate below toolbar */}
      <div className="fixed right-4 top-[calc(50%+180px)] z-30">
        <Button
          variant="default"
          size="lg"
          className="h-12 px-6 rounded-half bg-primary text-primary-foreground hover:bg-primary/90 shadow-lg shadow-primary/20 flex items-center gap-2"
          onClick={() => {
            toast({
              title: 'AI Chat',
              description: 'AI Chat feature coming soon!',
            });
          }}
        >
          <MessageSquare className="h-5 w-5" />
          <span className="font-medium">AI Chat</span>
        </Button>
        
      </div>

        <div className="container mx-auto px-4 pt-20 pb-16">
          <div className="space-y-10 pt-9">
            {presentation.slides.map((slide, index) => (
              <div
                key={slide.id}
                id={`main-slide-${index}`}
                className={`space-y-4 transition-all ${
                  currentSlideIndex === index ? 'ring-2 ring-primary/50 rounded-2xl p-2' : ''
                }`}
                onClick={(e) => {
                  handleSlideClick(index, e);
                  setCurrentSlideIndex(index);
                }}
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
                  <div className="relative">
                    <h1
                      className="text-3xl md:text-4xl font-bold text-white leading-tight focus:outline-none focus:ring-2 focus:ring-primary/60 rounded-md px-2 min-h-[3rem] relative z-10"
                      contentEditable
                      suppressContentEditableWarning
                      data-editable
                      onInput={(e) => {
                        const text = e.currentTarget.innerText;
                        updateSlide(index, 'title', text);
                      }}
                      onBlur={(e) => {
                        const text = e.currentTarget.innerText.trim();
                        if (!text) {
                          e.currentTarget.innerText = '';
                        } else {
                          e.currentTarget.innerText = text;
                        }
                        updateSlide(index, 'title', text);
                      }}
                      spellCheck={false}
                    >
                      {slide.title || ''}
                    </h1>
                    {!slide.title && (
                      <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-0">
                        <span className="text-3xl md:text-4xl font-bold text-white/50">{defaultTitle}</span>
                      </div>
                    )}
                  </div>
                  <div className="relative">
                    <p
                      className="text-base md:text-lg text-slate-200/80 whitespace-pre-line focus:outline-none focus:ring-2 focus:ring-primary/60 rounded-md px-3 py-2 min-h-[4rem] relative z-10"
                      contentEditable
                      suppressContentEditableWarning
                      data-editable
                      onInput={(e) => {
                        const text = e.currentTarget.innerText;
                        updateSlide(index, 'content', text);
                      }}
                      onBlur={(e) => {
                        const text = e.currentTarget.innerText.trim();
                        if (!text) {
                          e.currentTarget.innerText = '';
                        } else {
                          e.currentTarget.innerText = text;
                        }
                        updateSlide(index, 'content', text);
                      }}
                      spellCheck={false}
                    >
                      {slide.content || ''}
                    </p>
                    {!slide.content && (
                      <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-0">
                        <span className="text-base md:text-lg text-slate-300/50">{defaultContent}</span>
                      </div>
                    )}
                  </div>
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

              </div>
            ))}
          </div>
        </div>
      </div>
      {/* Fullscreen presentation mode */}
      {isPresenting && presentation && (
        <div className="fixed inset-0 z-50 bg-black flex flex-col">
          <div className="flex items-center justify-between px-6 py-3 bg-black/60 text-white text-sm">
            <div>
              {presentation.title} &middot; Slide {currentSlideIndex + 1} of {presentation.slides.length}
            </div>
            <div className="flex items-center gap-2">
              <span className="hidden md:inline text-xs text-white/70">
                Use ← → or space, Esc to exit
              </span>
              <Button
                variant="outline"
                size="sm"
                className="border-white/40 text-white bg-transparent hover:bg-white/10"
                onClick={() => setIsPresenting(false)}
              >
                Exit
              </Button>
            </div>
          </div>
          <div className="flex-1 flex items-center justify-center px-4 pb-6">
            {presentation.slides[currentSlideIndex] && (
              <div className="w-full max-w-6xl aspect-video relative overflow-hidden rounded-3xl border border-white/20 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 shadow-2xl flex items-center justify-center p-8">
                {presentation.slides[currentSlideIndex].imageUrl && (
                  <img
                    src={presentation.slides[currentSlideIndex].imageUrl}
                    alt={presentation.slides[currentSlideIndex].title}
                    className="absolute inset-0 h-full w-full object-cover opacity-25"
                  />
                )}
                <div className="absolute inset-0 pointer-events-none">
                  <div className="absolute -left-16 top-1/4 h-72 w-72 rounded-full bg-primary/25 blur-3xl" />
                  <div className="absolute right-0 top-0 h-56 w-56 rounded-full bg-white/10 blur-3xl" />
                </div>
                <div className="relative z-10 max-w-3xl text-center space-y-6">
                  <h1 className="text-4xl md:text-5xl font-bold text-white leading-tight">
                    {presentation.slides[currentSlideIndex].title || 'Untitled slide'}
                  </h1>
                  <p className="text-lg md:text-2xl text-slate-100/85 whitespace-pre-line">
                    {presentation.slides[currentSlideIndex].content || ''}
                  </p>
                </div>
                {presentation.slides[currentSlideIndex].diagramUrl && (
                  <div className="absolute bottom-8 right-8 w-40 h-40 border border-white/30 rounded-xl bg-black/70 p-2 shadow-xl">
                    <img
                      src={presentation.slides[currentSlideIndex].diagramUrl}
                      alt="Diagram"
                      className="h-full w-full object-contain"
                    />
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Editor;