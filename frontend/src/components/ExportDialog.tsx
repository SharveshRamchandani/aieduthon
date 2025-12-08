import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { FileText, Presentation } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ExportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onExport: (format: 'pptx' | 'pdf') => void;
  isExporting?: boolean;
}

export function ExportDialog({ open, onOpenChange, onExport, isExporting = false }: ExportDialogProps) {
  const [selectedFormat, setSelectedFormat] = useState<'pptx' | 'pdf'>('pptx');

  const handleExport = () => {
    onExport(selectedFormat);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Export Presentation</DialogTitle>
          <DialogDescription>
            Choose the format you want to download your presentation in.
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid grid-cols-2 gap-4 py-4">
          <button
            type="button"
            onClick={() => setSelectedFormat('pptx')}
            className={cn(
              "flex flex-col items-center justify-center p-6 border-2 rounded-lg transition-all",
              "hover:bg-accent hover:border-accent-foreground/20",
              selectedFormat === 'pptx'
                ? "border-primary bg-primary/10"
                : "border-border"
            )}
            disabled={isExporting}
          >
            <Presentation className={cn(
              "h-8 w-8 mb-2",
              selectedFormat === 'pptx' ? "text-primary" : "text-muted-foreground"
            )} />
            <span className={cn(
              "font-medium",
              selectedFormat === 'pptx' ? "text-primary" : "text-foreground"
            )}>
              PowerPoint
            </span>
            <span className="text-xs text-muted-foreground mt-1">.pptx</span>
          </button>

          <button
            type="button"
            onClick={() => setSelectedFormat('pdf')}
            className={cn(
              "flex flex-col items-center justify-center p-6 border-2 rounded-lg transition-all",
              "hover:bg-accent hover:border-accent-foreground/20",
              selectedFormat === 'pdf'
                ? "border-primary bg-primary/10"
                : "border-border"
            )}
            disabled={isExporting}
          >
            <FileText className={cn(
              "h-8 w-8 mb-2",
              selectedFormat === 'pdf' ? "text-primary" : "text-muted-foreground"
            )} />
            <span className={cn(
              "font-medium",
              selectedFormat === 'pdf' ? "text-primary" : "text-foreground"
            )}>
              PDF
            </span>
            <span className="text-xs text-muted-foreground mt-1">.pdf</span>
          </button>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isExporting}
          >
            Cancel
          </Button>
          <Button
            onClick={handleExport}
            disabled={isExporting}
          >
            {isExporting ? 'Exporting...' : 'Download'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

