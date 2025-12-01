/**
 * AI Test Page - Test individual AI features
 */

import { useState } from 'react';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import { Loader2, Sparkles, Image, Network } from 'lucide-react';
import { generateText, generateImage, generateDiagram } from '@/lib/api';

const AITest = () => {
  const { toast } = useToast();
  
  // Text Generation
  const [textPrompt, setTextPrompt] = useState('');
  const [textResult, setTextResult] = useState('');
  const [isGeneratingText, setIsGeneratingText] = useState(false);

  // Image Generation
  const [imagePrompt, setImagePrompt] = useState('');
  const [imageResult, setImageResult] = useState<string[]>([]);
  const [isGeneratingImage, setIsGeneratingImage] = useState(false);
  const [imageWidth, setImageWidth] = useState(1024);
  const [imageHeight, setImageHeight] = useState(1024);

  // Diagram Generation
  const [diagramType, setDiagramType] = useState('flowchart');
  const [diagramDescription, setDiagramDescription] = useState('');
  const [diagramResult, setDiagramResult] = useState('');
  const [isGeneratingDiagram, setIsGeneratingDiagram] = useState(false);

  const handleGenerateText = async () => {
    if (!textPrompt.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a prompt',
        variant: 'destructive',
      });
      return;
    }

    setIsGeneratingText(true);
    try {
      const result = await generateText({
        prompt: textPrompt,
        context: { grade_level: '10th', subject: 'general' },
      });
      setTextResult(result.text);
      toast({
        title: 'Success',
        description: result.cached ? 'Result from cache' : 'Text generated successfully',
      });
    } catch (err) {
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to generate text',
        variant: 'destructive',
      });
    } finally {
      setIsGeneratingText(false);
    }
  };

  const handleGenerateImage = async () => {
    if (!imagePrompt.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a prompt',
        variant: 'destructive',
      });
      return;
    }

    setIsGeneratingImage(true);
    try {
      const result = await generateImage({
        prompt: imagePrompt,
        width: imageWidth,
        height: imageHeight,
      });
      setImageResult(result.urls);
      toast({
        title: 'Success',
        description: result.cached ? 'Result from cache' : 'Image generated successfully',
      });
    } catch (err) {
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to generate image',
        variant: 'destructive',
      });
    } finally {
      setIsGeneratingImage(false);
    }
  };

  const handleGenerateDiagram = async () => {
    if (!diagramDescription.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a description',
        variant: 'destructive',
      });
      return;
    }

    setIsGeneratingDiagram(true);
    try {
      const result = await generateDiagram({
        diagram_type: diagramType,
        description: diagramDescription,
        format: 'png',
      });
      setDiagramResult(result.file_path);
      toast({
        title: 'Success',
        description: 'Diagram generated successfully',
      });
    } catch (err) {
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to generate diagram',
        variant: 'destructive',
      });
    } finally {
      setIsGeneratingDiagram(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <TopBar />
      
      <div className="container mx-auto px-4 pt-20 pb-16">
        <div className="max-w-6xl mx-auto space-y-8">
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold tracking-tight">AI Features Test</h1>
            <p className="text-lg text-muted-foreground">
              Test individual AI generation features
            </p>
          </div>

          <Tabs defaultValue="text" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="text">
                <Sparkles className="h-4 w-4 mr-2" />
                Text Generation
              </TabsTrigger>
              <TabsTrigger value="image">
                <Image className="h-4 w-4 mr-2" />
                Image Generation
              </TabsTrigger>
              <TabsTrigger value="diagram">
                <Network className="h-4 w-4 mr-2" />
                Diagram Generation
              </TabsTrigger>
            </TabsList>

            {/* Text Generation Tab */}
            <TabsContent value="text">
              <Card>
                <CardHeader>
                  <CardTitle>Text Generation (LLM)</CardTitle>
                  <CardDescription>Generate text content using Hugging Face LLMs</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Prompt</Label>
                    <Textarea
                      placeholder="E.g., 'Explain photosynthesis in simple terms'"
                      value={textPrompt}
                      onChange={(e) => setTextPrompt(e.target.value)}
                      className="min-h-[100px]"
                    />
                  </div>
                  <Button onClick={handleGenerateText} disabled={isGeneratingText} className="w-full">
                    {isGeneratingText ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Generate Text
                      </>
                    )}
                  </Button>
                  {textResult && (
                    <div className="p-4 bg-muted rounded-lg">
                      <Label className="mb-2 block">Result:</Label>
                      <p className="whitespace-pre-wrap">{textResult}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Image Generation Tab */}
            <TabsContent value="image">
              <Card>
                <CardHeader>
                  <CardTitle>Image Generation (Stable Diffusion)</CardTitle>
                  <CardDescription>Generate educational images using Stable Diffusion</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Prompt</Label>
                    <Textarea
                      placeholder="E.g., 'Educational illustration of photosynthesis process'"
                      value={imagePrompt}
                      onChange={(e) => setImagePrompt(e.target.value)}
                      className="min-h-[100px]"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Width</Label>
                      <Input
                        type="number"
                        value={imageWidth}
                        onChange={(e) => setImageWidth(parseInt(e.target.value))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Height</Label>
                      <Input
                        type="number"
                        value={imageHeight}
                        onChange={(e) => setImageHeight(parseInt(e.target.value))}
                      />
                    </div>
                  </div>
                  <Button onClick={handleGenerateImage} disabled={isGeneratingImage} className="w-full">
                    {isGeneratingImage ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Image className="mr-2 h-4 w-4" />
                        Generate Image
                      </>
                    )}
                  </Button>
                  {imageResult.length > 0 && (
                    <div className="space-y-2">
                      <Label>Generated Images:</Label>
                      <div className="grid grid-cols-2 gap-4">
                        {imageResult.map((url, index) => (
                          <div key={index} className="border border-border rounded-lg overflow-hidden">
                            <img src={url} alt={`Generated ${index + 1}`} className="w-full h-auto" />
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Diagram Generation Tab */}
            <TabsContent value="diagram">
              <Card>
                <CardHeader>
                  <CardTitle>Diagram Generation</CardTitle>
                  <CardDescription>Generate educational diagrams using Graphviz/Matplotlib</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Diagram Type</Label>
                    <Select value={diagramType} onValueChange={setDiagramType}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="flowchart">Flowchart</SelectItem>
                        <SelectItem value="hierarchy">Hierarchy</SelectItem>
                        <SelectItem value="cycle">Cycle</SelectItem>
                        <SelectItem value="chart">Chart</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Description</Label>
                    <Textarea
                      placeholder="E.g., 'Photosynthesis cycle showing conversion of sunlight to glucose'"
                      value={diagramDescription}
                      onChange={(e) => setDiagramDescription(e.target.value)}
                      className="min-h-[100px]"
                    />
                  </div>
                  <Button onClick={handleGenerateDiagram} disabled={isGeneratingDiagram} className="w-full">
                    {isGeneratingDiagram ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Network className="mr-2 h-4 w-4" />
                        Generate Diagram
                      </>
                    )}
                  </Button>
                  {diagramResult && (
                    <div className="space-y-2">
                      <Label>Generated Diagram:</Label>
                      <div className="border border-border rounded-lg overflow-hidden">
                        <img src={diagramResult} alt="Diagram" className="w-full h-auto" />
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default AITest;

