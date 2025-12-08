import { useState, useRef, useEffect } from "react";
import { 
  Settings as SettingsIcon, 
  Moon, 
  Globe, 
  Bell, 
  Shield, 
  Database,
  Monitor,
  X
} from "lucide-react";

interface SettingsModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const SettingsModal = ({ open, onOpenChange }: SettingsModalProps) => {
  const [activeTab, setActiveTab] = useState("general");
  const modalRef = useRef<HTMLDivElement>(null);

  // Close modal when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
        onOpenChange(false);
      }
    };

    if (open) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [open, onOpenChange]);

  const menuItems = [
    { id: "general", label: "General", icon: SettingsIcon },
    { id: "appearance", label: "Appearance", icon: Moon },
    { id: "language", label: "Language & Region", icon: Globe },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "privacy", label: "Privacy & Security", icon: Shield },
    { id: "data", label: "Data & Storage", icon: Database },
    { id: "advanced", label: "Advanced", icon: Monitor },
  ];

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div 
        ref={modalRef}
        className="bg-card text-foreground rounded-lg shadow-xl max-w-4xl w-full h-[82vh] m-4 flex relative border border-border"
      >
        {/* Close button */}
        <button
          onClick={() => onOpenChange(false)}
          className="absolute top-4 right-4 z-10 p-2 hover:bg-accent rounded-full transition-colors duration-200"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Sidebar */}
        <div className="w-64 bg-muted p-4 rounded-l-lg">
          <div className="mb-6">
            <h2 className="text-lg font-serif font-semibold">Settings</h2>
          </div>
          <nav className="space-y-1">
            {menuItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200 ${
                  activeTab === item.id
                    ? 'bg-accent text-accent-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                }`}
              >
                <item.icon className="mr-3 h-4 w-4" />
                {item.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6 overflow-y-auto">
          {activeTab === "general" && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold font-serif">General Settings</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between py-3 border-b border-border">
                  <div>
                    <label className="text-sm font-medium">Auto-save changes</label>
                    <p className="text-xs text-muted-foreground">Automatically save your work</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" defaultChecked className="sr-only peer" />
                    <div className="w-11 h-6 bg-muted-foreground peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-background after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between py-3 border-b border-border">
                  <div>
                    <label className="text-sm font-medium">Show tooltips</label>
                    <p className="text-xs text-muted-foreground">Display helpful tooltips</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" defaultChecked className="sr-only peer" />
                    <div className="w-11 h-6 bg-muted-foreground peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-background after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>

                <div className="py-3">
                  <label className="block text-sm font-medium mb-2">Backup frequency</label>
                  <select className="w-full px-3 py-2 border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent bg-background">
                    <option value="hourly">Every hour</option>
                    <option value="daily" selected>Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="never">Never</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {activeTab === "appearance" && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold font-serif">Appearance</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Theme</label>
                  <select className="w-full px-3 py-2 border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent bg-background">
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                    <option value="system" selected>System</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Font size</label>
                  <select className="w-full px-3 py-2 border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent bg-background">
                    <option value="small">Small</option>
                    <option value="medium" selected>Medium</option>
                    <option value="large">Large</option>
                  </select>
                </div>

                <div className="flex items-center justify-between py-3">
                  <div>
                    <label className="text-sm font-medium">Compact mode</label>
                    <p className="text-xs text-muted-foreground">Use less space in the interface</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" />
                    <div className="w-11 h-6 bg-muted-foreground peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-background after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>
              </div>
            </div>
          )}

          {activeTab === "notifications" && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold font-serif">Notification Settings</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between py-3 border-b border-border">
                  <div>
                    <label className="text-sm font-medium">Desktop notifications</label>
                    <p className="text-xs text-muted-foreground">Show notifications on desktop</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" defaultChecked className="sr-only peer" />
                    <div className="w-11 h-6 bg-muted-foreground peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-background after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between py-3 border-b border-border">
                  <div>
                    <label className="text-sm font-medium">Sound notifications</label>
                    <p className="text-xs text-muted-foreground">Play sound for notifications</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" defaultChecked className="sr-only peer" />
                    <div className="w-11 h-6 bg-muted-foreground peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-background after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between py-3">
                  <div>
                    <label className="text-sm font-medium">Email digest</label>
                    <p className="text-xs text-muted-foreground">Receive daily email summary</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" />
                    <div className="w-11 h-6 bg-muted-foreground peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-background after:rounded-full after:h-5 w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>
              </div>
            </div>
          )}

          {activeTab === "privacy" && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold font-serif">Privacy & Security</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between py-3 border-b border-border">
                  <div>
                    <label className="text-sm font-medium">Two-factor authentication</label>
                    <p className="text-xs text-muted-foreground">Add extra security to your account</p>
                  </div>
                  <button className="px-4 py-2 text-sm border border-input text-foreground rounded-lg hover:bg-accent transition-colors duration-200 font-medium">
                    Enable
                  </button>
                </div>

                <div className="flex items-center justify-between py-3 border-b border-border">
                  <div>
                    <label className="text-sm font-medium">Data analytics</label>
                    <p className="text-xs text-muted-foreground">Help improve our service</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" defaultChecked className="sr-only peer" />
                    <div className="w-11 h-6 bg-muted-foreground peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-background after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>

                <div className="py-3">
                  <label className="block text-sm font-medium mb-2">Session timeout</label>
                  <select className="w-full px-3 py-2 border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent bg-background">
                    <option value="15">15 minutes</option>
                    <option value="30" selected>30 minutes</option>
                    <option value="60">1 hour</option>
                    <option value="never">Never</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {activeTab === "language" && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold font-serif">Language & Region</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Language</label>
                  <select className="w-full px-3 py-2 border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent bg-background">
                    <option value="en" selected>English</option>
                    <option value="es">Spanish</option>
                    <option value="fr">French</option>
                    <option value="de">German</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Region</label>
                  <select className="w-full px-3 py-2 border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent bg-background">
                    <option value="us" selected>United States</option>
                    <option value="uk">United Kingdom</option>
                    <option value="ca">Canada</option>
                    <option value="au">Australia</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Date format</label>
                  <select className="w-full px-3 py-2 border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent bg-background">
                    <option value="mdy" selected>MM/DD/YYYY</option>
                    <option value="dmy">DD/MM/YYYY</option>
                    <option value="ymd">YYYY-MM-DD</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Add other tab contents as needed */}
          {!["general", "appearance", "notifications", "privacy", "language"].includes(activeTab) && (
            <div className="flex items-center justify-center h-full">
              <p className="text-muted-foreground">
                {menuItems.find(item => item.id === activeTab)?.label} settings coming soon...
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;