import { useEffect, useState } from 'react';
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
import type { ExportStyle } from '@/lib/api';

interface ExportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onExport: (format: 'pptx' | 'pdf', style: ExportStyle) => void;
  isExporting?: boolean;
  initialStyle?: ExportStyle;
}

export function ExportDialog({
  open,
  onOpenChange,
  onExport,
  isExporting = false,
  initialStyle = 'template',
}: ExportDialogProps) {
  const [selectedFormat, setSelectedFormat] = useState<'pptx' | 'pdf'>('pptx');
  const [selectedStyle, setSelectedStyle] = useState<ExportStyle>(initialStyle);

  useEffect(() => {
    setSelectedStyle(initialStyle);
  }, [initialStyle, open]);

  const handleExport = () => {
    onExport(selectedFormat, selectedStyle);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[460px]">
        <DialogHeader>
          <DialogTitle>Export presentation</DialogTitle>
          <DialogDescription>
            Choose how you want to download this deck – file format and layout style.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-2">
          <div>
            <p className="mb-2 text-sm font-medium text-foreground">File format</p>
            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setSelectedFormat('pptx')}
                className={cn(
                  'flex flex-col items-center justify-center p-4 border-2 rounded-lg transition-all',
                  'hover:bg-accent hover:border-accent-foreground/20',
                  selectedFormat === 'pptx' ? 'border-primary bg-primary/10' : 'border-border',
                )}
                disabled={isExporting}
              >
                <Presentation
                  className={cn(
                    'h-7 w-7 mb-1',
                    selectedFormat === 'pptx' ? 'text-primary' : 'text-muted-foreground',
                  )}
                />
                <span
                  className={cn(
                    'text-sm font-medium',
                    selectedFormat === 'pptx' ? 'text-primary' : 'text-foreground',
                  )}
                >
                  PowerPoint
                </span>
                <span className="text-[11px] text-muted-foreground mt-0.5">.pptx</span>
              </button>

              <button
                type="button"
                onClick={() => setSelectedFormat('pdf')}
                className={cn(
                  'flex flex-col items-center justify-center p-4 border-2 rounded-lg transition-all',
                  'hover:bg-accent hover:border-accent-foreground/20',
                  selectedFormat === 'pdf' ? 'border-primary bg-primary/10' : 'border-border',
                )}
                disabled={isExporting}
              >
                <FileText
                  className={cn(
                    'h-7 w-7 mb-1',
                    selectedFormat === 'pdf' ? 'text-primary' : 'text-muted-foreground',
                  )}
                />
                <span
                  className={cn(
                    'text-sm font-medium',
                    selectedFormat === 'pdf' ? 'text-primary' : 'text-foreground',
                  )}
                >
                  PDF
                </span>
                <span className="text-[11px] text-muted-foreground mt-0.5">.pdf</span>
              </button>
            </div>
          </div>

          <div>
            <p className="mb-2 text-sm font-medium text-foreground">Export layout</p>
            <div className="inline-flex rounded-full bg-muted px-1 py-1">
              <button
                type="button"
                className={cn(
                  'px-3 py-1 text-xs rounded-full transition-colors',
                  selectedStyle === 'template'
                    ? 'bg-background text-foreground font-semibold shadow-sm'
                    : 'text-muted-foreground hover:text-foreground',
                )}
                disabled={isExporting}
                onClick={() => setSelectedStyle('template')}
              >
                Use template
              </button>
              <button
                type="button"
                className={cn(
                  'px-3 py-1 text-xs rounded-full transition-colors',
                  selectedStyle === 'preview'
                    ? 'bg-background text-foreground font-semibold shadow-sm'
                    : 'text-muted-foreground hover:text-foreground',
                )}
                disabled={isExporting}
                onClick={() => setSelectedStyle('preview')}
              >
                Preview style
              </button>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isExporting}>
            Cancel
          </Button>
          <Button onClick={handleExport} disabled={isExporting}>
            {isExporting ? 'Exporting…' : 'Download'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

