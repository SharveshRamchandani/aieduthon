"use client";

import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { Sparkles, Image, Network, Loader2, Search, Palette, Settings,Menu ,ChevronLeft, Globe, Paperclip, Send } from 'lucide-react';
import { orchestrate } from '@/lib/api';
import { Textarea } from '@/components/ui/textarea';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

const Home = () => {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generateImages, setGenerateImages] = useState(true);
  const [generateDiagrams, setGenerateDiagrams] = useState(true);
  const [gradeLevel, setGradeLevel] = useState('');
  const [subject, setSubject] = useState('');
  const [locale, setLocale] = useState('en');
  const [searchTerm, setSearchTerm] = useState('');
  const [isThemesSidebarOpen, setIsThemesSidebarOpen] = useState(false);
  const [isAdvancedOptionsOpen, setIsAdvancedOptionsOpen] = useState(false);
  const [showSearch, setShowSearch] = useState(true);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [estimatedSlides, setEstimatedSlides] = useState('');
  const [quizCount, setQuizCount] = useState('');
  const navigate = useNavigate();
  const { toast } = useToast();

  // Auto-resize textarea
  useEffect(() => {
    adjustHeight();
  }, [prompt]);

  const adjustHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 164)}px`;
    }
  };
  const presentations = [
  { id: "1", title: "Photosynthesis – Class 10" },
  { id: "2", title: "Machine Learning Basics" },
  { id: "3", title: "Business Strategy Pitch" },
];

// 🔹 Presentations sidebar state
const [isHistoryCollapsed, setIsHistoryCollapsed] = useState(false);
const [isMobileView, setIsMobileView] = useState(false);
const [desktopHistoryState, setDesktopHistoryState] = useState(false);

useEffect(() => {
  const handleResize = () => {
    const mobile = window.innerWidth < 1024;
    setIsMobileView(mobile);

    if (mobile) {
      setDesktopHistoryState(isHistoryCollapsed);
      setIsHistoryCollapsed(true);
    } else {
      setIsHistoryCollapsed(desktopHistoryState);
    }
  };

  handleResize();
  window.addEventListener("resize", handleResize);
  return () => window.removeEventListener("resize", handleResize);
}, [desktopHistoryState, isHistoryCollapsed]);

const toggleHistorySidebar = () => {
  const next = !isHistoryCollapsed;
  setIsHistoryCollapsed(next);
  if (!isMobileView) setDesktopHistoryState(next);
};


  // Sample themes data - in a real app this would come from an API
  const themes = [
    { id: 1, name: 'Business Professional', preview: '💼' },
    { id: 2, name: 'Academic', preview: '📚' },
    { id: 3, name: 'Creative', preview: '🎨' },
    { id: 4, name: 'Minimalist', preview: '⚪' },
    { id: 5, name: 'Tech', preview: '💻' },
    { id: 6, name: 'Nature', preview: '🌿' },
    { id: 7, name: 'Education', preview: '🎓' },
    { id: 8, name: 'Medical', preview: '🩺' },
  ];

  const filteredThemes = themes.filter(theme => 
    theme.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSubmit = () => {
    if (prompt.trim()) {
      generateSlides();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Handle file upload if needed
      console.log('File selected:', file.name);
    }
  };

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
      if (estimatedSlides) {
        const parsed = parseInt(estimatedSlides, 10);
        if (!Number.isNaN(parsed)) {
          context.estimated_slides = parsed;
        }
      }
      if (quizCount) {
        const parsedQuiz = parseInt(quizCount, 10);
        if (!Number.isNaN(parsedQuiz)) {
          context.quiz_questions = parsedQuiz;
        }
      }
      if (generateImages || generateDiagrams) context.generate_media = true;

      const data = await orchestrate({
        prompt,
        userId: 'demo-user',
        locale,
        context,
        generate_images: generateImages,
        generate_diagrams: generateDiagrams,
        estimated_slides: context.estimated_slides,
        quiz_questions: context.quiz_questions,
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
<div
  className={`transition-all duration-300
  ${isHistoryCollapsed ? "ml-16" : "ml-20"}`}
>
      {/* 🔹 Presentations / History Sidebar */}
<div
  className={`fixed left-2 top-4 h-[calc(100vh-2rem)] bg-card
  border border-border
  rounded-2xl
  transition-all duration-300 z-50 shadow-sm
  ${isHistoryCollapsed ? "w-16" : "w-64"}`}
>
  <div className="pt-10 px-3 space-y-2">
  {!isHistoryCollapsed && (
    <h2 className="px-2 text-md font-bold uppercase tracking-wide text-muted-foreground text-center mb-4">
      Your Presentations
    </h2>
  )}
<div className="mx-2 mb-4 h-px bg-foreground" />
  {presentations.map((p) => (
    <button
      key={p.id}
      className={`
        group w-full flex items-center gap-3
        rounded-xl px-3 py-2.5
        text-sm font-medium text-foreground
        transition-all duration-200
        hover:bg-accent/70
        focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring
        ${isHistoryCollapsed ? "justify-center" : "justify-start"}
      `}
    >
      {/* Icon */}
      <span
        className="
          flex h-9 w-9 items-center justify-center
          rounded-lg bg-muted text-muted-foreground
          group-hover:bg-background group-hover:text-foreground
          transition-colors
        "
      >
        📄
      </span>

      {/* Title */}
      {!isHistoryCollapsed && (
        <span className="truncate">
          {p.title}
        </span>
      )}
    </button>
  ))}
</div>


  {/* Toggle Button */}
  <button
    onClick={toggleHistorySidebar}
    className="fixed bottom-16 z-40 bg-white text-black border border-border rounded-xl p-3 shadow-md"
    style={{
      left: isHistoryCollapsed ? "20px" : "240px",
    }}
  >
    {isHistoryCollapsed ? (
      <Menu className="w-4 h-4" />
    ) : (
      <ChevronLeft className="w-4 h-4" />
    )}
  </button>
</div>


      
      {/* Themes Sidebar Overlay */}
      {isThemesSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-50"
          onClick={() => setIsThemesSidebarOpen(false)}
        ></div>
      )}
      
      {/* Themes Sidebar - Now on the left side */}
      {isThemesSidebarOpen && (
  <div className="fixed top-20 left-2 h-[calc(100vh-6rem)] w-96 bg-card z-50 border-border rounded-3xl overflow-hidden flex flex-col">
    
    {/* 🔒 Fixed / Sticky Header */}
    <div className="p-6 border-b border-border bg-card sticky top-0 z-10">
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Themes</h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsThemesSidebarOpen(false)}
          >
            ✕
          </Button>
        </div>

        <p className="text-muted-foreground text-sm">
          Choose a theme for your presentation or search for specific styles
        </p>

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground h-4 w-4" />
          <Input
            placeholder="Search themes..."
            className="pl-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>
    </div>

    {/* 🔽 Scrollable Content */}
    <div className="flex-1 overflow-y-auto p-6">
      <div className="grid grid-cols-1 gap-3">
        {filteredThemes.map((theme) => (
          <div
            key={theme.id}
            className="border border-border rounded-lg p-4 hover:bg-accent cursor-pointer transition-colors"
            onClick={() => setIsThemesSidebarOpen(false)}
          >
            <div className="flex items-center gap-3">
              <div className="text-2xl">{theme.preview}</div>
              <span className="font-medium text-sm">{theme.name}</span>
            </div>
          </div>
        ))}
      </div>
    </div>

  </div>
)}


      {/* Advanced Options Sidebar Overlay */}
      {isAdvancedOptionsOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-50"
          onClick={() => setIsAdvancedOptionsOpen(false)}
        ></div>
      )}
      
      {/* Advanced Options Sidebar - On the right side */}
      {isAdvancedOptionsOpen && (
        <div className="fixed top-20 right-2 h-[calc(100vh-6rem)] w-96 bg-card border-l  z-50 border-border rounded-3xl scrollbar-hide">
          <div className="p-6">
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold">Advanced Options</h2>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setIsAdvancedOptionsOpen(false)}
                >
                  ✕
                </Button>
              </div>
              
              <div className="space-y-4">
                <div className="grid grid-cols-1 gap-4">
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
                <div className="space-y-2">
                  <Label>Estimated Slides</Label>
                  <Input
                    type="number"
                    min={3}
                    max={30}
                    placeholder="e.g., 10"
                    value={estimatedSlides}
                    onChange={(e) => setEstimatedSlides(e.target.value)}
                    disabled={isGenerating}
                  />
                  <p className="text-xs text-muted-foreground">
                    Request between 3–30 slides (defaults to AI estimate if empty)
                  </p>
                </div>
                <div className="space-y-2">
                  <Label>MCQs to Generate</Label>
                  <Input
                    type="number"
                    min={1}
                    max={50}
                    placeholder="e.g., 8"
                    value={quizCount}
                    onChange={(e) => setQuizCount(e.target.value)}
                    disabled={isGenerating}
                  />
                  <p className="text-xs text-muted-foreground">
                    Choose how many quiz MCQs to create (1–50). Defaults to 10 if empty.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="container mx-auto px-0 pt-44 pb-16">
        <div className="text-center space-y-4 mb-8">
          <h1 className="text-5xl font-bold tracking-tight">
            What would you like to create?
          </h1>
          <p className="text-lg text-muted-foreground">
            Describe your presentation topic and let AI do the rest
          </p>
        </div>

        <div className="flex flex-col items-center gap-8 mx-30 max-w-none">
          {/* Center - Input Form with new UI */}
          <div className="w-full lg:w-2/3">
            <div className="bg-card border border-border rounded-2xl p-8 space-y-6">
              <div className="space-y-3">
                {/* New AI Input Component */}
                <div className="w-full py-4">
                  <div className="relative max-w-3xl w-full mx-auto">
                    <div className="relative flex flex-col">
                      <div className="overflow-y-auto" style={{ maxHeight: '500px' }}>
                        <Textarea
                          value={prompt}
                          placeholder="E.g., 'Photosynthesis for Class 10' or 'Introduction to Machine Learning'..."
                          className="w-full rounded-xl rounded-b-none px-4 py-4 bg-black/5 dark:bg-white/5 border-none dark:text-white placeholder:text-black/70 dark:placeholder:text-white/70 resize-none focus-visible:ring-0 leading-[1.4] text-base"
                          ref={textareaRef}
                          onKeyDown={(e) => {
                            if (e.key === "Enter" && !e.shiftKey) {
                              e.preventDefault();
                              handleSubmit();
                            }
                          }}
                          onChange={(e) => {
                            setPrompt(e.target.value);
                            adjustHeight();
                          }}
                        />
                      </div>

                      <div className="h-14 bg-black/5 dark:bg-white/5 rounded-b-xl flex items-center justify-between px-3">
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setIsThemesSidebarOpen(true)}
                            className="rounded-lg px-3 py-1.5 h-auto text-sm flex items-center gap-1.5 bg-black/5 dark:bg-white/5 hover:bg-accent"
                          >
                            <Palette className="w-3.5 h-3.5" />
                            Themes
                          </Button>
                          
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setIsAdvancedOptionsOpen(true)}
                            className="rounded-lg px-3 py-1.5 h-auto text-sm flex items-center gap-1.5 bg-black/5 dark:bg-white/5 hover:bg-accent"
                          >
                            <Settings className="w-3.5 h-3.5" />
                            Advanced
                          </Button>
                        </div>
                        
                        <Button
                          onClick={handleSubmit}
                          disabled={isGenerating || !prompt.trim()}
                          className="rounded-lg px-4 py-1.5 h-auto text-sm flex items-center gap-1.5"
                        >
                          {isGenerating ? (
                            <>
                              <Loader2 className="w-3.5 h-3.5 animate-spin" />
                              Generating...
                            </>
                          ) : (
                            <>
                              Generate
                              <Sparkles className="w-3.5 h-3.5" />
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="text-sm text-muted-foreground text-center">
                  Be specific about your topic, target audience, and any key points you want to cover
                </div>
              </div>

              {/* Buttons Row */}
              {/* <div className="flex gap-7">
                <Button
                  variant="outline"
                  onClick={() => setIsThemesSidebarOpen(true)}
                  className="flex-1 rounded-xl text-base py-6"
                >
                  <Palette className="mr-2 h-3 w-3" />
                  Themes
                </Button>
                
                <Button
                  variant="outline"
                  onClick={() => setIsAdvancedOptionsOpen(true)}
                  className="flex-1 rounded-xl text-base py-6"
                >
                  <Settings className="mr-2 h-3 w-3" />
                  Advanced Options
                </Button>
              </div> */}
            </div>
          </div>

          {/* Your Presentations Section */}
          {/* <div className="w-full lg:w-2/3 pt-20">
            <div className="bg-card border border-border rounded-2xl p-8">
              <h2 className="text-2xl font-bold mb-6">Your Presentations</h2>
              <div className="text-center py-12">
                <div className="text-muted-foreground mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <p className="text-muted-foreground">You haven't created any presentations yet.</p>
                <p className="text-muted-foreground text-sm mt-2">Generate your first presentation to get started!</p>
              </div>
            </div>
          </div> */}
        </div>
      </div>
    </div>
    </div>
  );
};

export default Home;