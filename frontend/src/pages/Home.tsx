"use client";

// TypeScript declarations for Speech Recognition API
declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition;
    webkitSpeechRecognition: typeof SpeechRecognition;
  }
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  abort(): void;
  onstart: ((this: SpeechRecognition, ev: Event) => any) | null;
  onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => any) | null;
  onerror: ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => any) | null;
  onend: ((this: SpeechRecognition, ev: Event) => any) | null;
}

interface SpeechRecognitionEvent extends Event {
  resultIndex: number;
  results: SpeechRecognitionResultList;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface SpeechRecognitionResultList {
  length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
  isFinal: boolean;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

declare var SpeechRecognition: {
  prototype: SpeechRecognition;
  new (): SpeechRecognition;
};

import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { Sparkles, Image, Network, Loader2, Search, Palette, Settings, Globe, Paperclip, Send, Mic, MicOff } from 'lucide-react';
import { orchestrate, generateTTSFromText, getTTSAudioURL } from '@/lib/api';
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
  const [isListening, setIsListening] = useState(false);
  const [isGeneratingTTS, setIsGeneratingTTS] = useState(false);
  const [isPlayingTTS, setIsPlayingTTS] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const navigate = useNavigate();
  const { toast } = useToast();

  // Initialize Speech Recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = locale === 'en' ? 'en-US' : locale === 'hi' ? 'hi-IN' : 'ta-IN';

        recognition.onstart = () => {
          setIsListening(true);
        };

        recognition.onresult = (event: SpeechRecognitionEvent) => {
          let interimTranscript = '';
          let finalTranscript = '';

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript + ' ';
            } else {
              interimTranscript += transcript;
            }
          }

          if (finalTranscript) {
            const newText = finalTranscript.trim();
            setPrompt(prev => prev + (prev ? ' ' : '') + newText);
          } else if (interimTranscript) {
            // Optionally show interim results
            // setPrompt(prev => prev + interimTranscript);
          }
        };

        recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
          console.error('Speech recognition error:', event.error);
          setIsListening(false);
          if (event.error === 'not-allowed') {
            toast({
              title: 'Microphone Permission Denied',
              description: 'Please allow microphone access to use voice input',
              variant: 'destructive',
            });
          } else if (event.error === 'no-speech') {
            toast({
              title: 'No Speech Detected',
              description: 'Please try speaking again',
              variant: 'destructive',
            });
          }
        };

        recognition.onend = () => {
          setIsListening(false);
          // Auto-generate TTS when voice input ends if there's text
          if (prompt.trim()) {
            handleGenerateTTSForPrompt();
          }
        };

        recognitionRef.current = recognition;
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [locale, toast]);

  // Update recognition language when locale changes
  useEffect(() => {
    if (recognitionRef.current) {
      const langMap: Record<string, string> = {
        'en': 'en-US',
        'hi': 'hi-IN',
        'ta': 'ta-IN'
      };
      recognitionRef.current.lang = langMap[locale] || 'en-US';
    }
  }, [locale]);

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

  const toggleVoiceInput = () => {
    // If TTS is playing, stop it
    if (isPlayingTTS) {
      stopTTSAudio();
      return;
    }

    if (!recognitionRef.current) {
      toast({
        title: 'Voice Input Not Available',
        description: 'Your browser does not support speech recognition. Please use Chrome, Edge, or Safari.',
        variant: 'destructive',
      });
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
      // Generate TTS when stopping if there's text
      if (prompt.trim()) {
        handleGenerateTTSForPrompt();
      }
    } else {
      try {
        recognitionRef.current.start();
      } catch (error) {
        console.error('Error starting speech recognition:', error);
        toast({
          title: 'Error',
          description: 'Failed to start voice input. Please try again.',
          variant: 'destructive',
        });
      }
    }
  };

  const handleGenerateTTSForPrompt = async () => {
    if (!prompt.trim()) {
      return;
    }

    setIsGeneratingTTS(true);
    try {
      const result = await generateTTSFromText({
        text: prompt,
        locale: locale,
        slow: false,
      });

      if (result.success && result.file_url) {
        // Play the audio
        const audioUrl = getTTSAudioURL(result.filename);
        playTTSAudio(audioUrl);
        
        toast({
          title: 'TTS Generated',
          description: 'Playing your prompt audio...',
        });
      }
    } catch (error) {
      console.error('Error generating TTS:', error);
      toast({
        title: 'TTS Generation Failed',
        description: error instanceof Error ? error.message : 'Could not generate audio',
        variant: 'destructive',
      });
    } finally {
      setIsGeneratingTTS(false);
    }
  };

  const playTTSAudio = (audioUrl: string) => {
    // Stop any currently playing audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    const audio = new Audio(audioUrl);
    audioRef.current = audio;

    audio.onplay = () => {
      setIsPlayingTTS(true);
    };

    audio.onended = () => {
      setIsPlayingTTS(false);
      audioRef.current = null;
    };

    audio.onerror = () => {
      setIsPlayingTTS(false);
      toast({
        title: 'Audio Playback Failed',
        description: 'Could not play the audio file',
        variant: 'destructive',
      });
      audioRef.current = null;
    };

    audio.play().catch((error) => {
      console.error('Error playing audio:', error);
      setIsPlayingTTS(false);
      audioRef.current = null;
    });
  };

  const stopTTSAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setIsPlayingTTS(false);
    }
  };

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

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
      
      {/* Themes Sidebar Overlay */}
      {isThemesSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-50"
          onClick={() => setIsThemesSidebarOpen(false)}
        ></div>
      )}
      
      {/* Themes Sidebar - Now on the left side */}
      {isThemesSidebarOpen && (
        <div className="fixed top-20 left-2 h-[calc(100vh-6rem)] w-96 bg-card z-50 overflow-y-auto border-border rounded-3xl scrollbar-hide">
          <div className="p-6">
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
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Search themes..."
                  className="pl-10"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              
              {/* Themes Grid */}
              <div className="grid grid-cols-1 gap-3 mt-4">
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
        </div>
      )}

      {/* Advanced Options Sidebar Overlay */}
      {isAdvancedOptionsOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
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
                            onClick={toggleVoiceInput}
                            disabled={isGenerating || isGeneratingTTS}
                            className={cn(
                              "rounded-lg px-3 py-1.5 h-auto text-sm flex items-center gap-1.5 bg-black/5 dark:bg-white/5 hover:bg-accent transition-all",
                              isListening && "bg-red-500/20 dark:bg-red-500/20 animate-pulse",
                              isPlayingTTS && "bg-blue-500/20 dark:bg-blue-500/20"
                            )}
                            title={
                              isListening 
                                ? "Stop recording" 
                                : isPlayingTTS 
                                ? "Playing audio..." 
                                : "Start voice input"
                            }
                          >
                            {isGeneratingTTS ? (
                              <>
                                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                                <span>Generating...</span>
                              </>
                            ) : isPlayingTTS ? (
                              <>
                                <MicOff className="w-3.5 h-3.5 text-blue-500" />
                                <span className="text-blue-500">Playing</span>
                              </>
                            ) : isListening ? (
                              <>
                                <MicOff className="w-3.5 h-3.5 text-red-500" />
                                <span className="text-red-500">Stop</span>
                              </>
                            ) : (
                              <>
                                <Mic className="w-3.5 h-3.5" />
                                <span>Voice</span>
                              </>
                            )}
                          </Button>

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
  );
};

export default Home;