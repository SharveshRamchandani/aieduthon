import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { 
  User, 
  Settings, 
  MessageSquare, 
  Video, 
  Bell, 
  Palette, 
  HardDrive, 
  Keyboard, 
  HelpCircle,
  Edit2,
  LogOut,
  Camera,
  Upload,
  X
} from "lucide-react";

interface ProfileModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const ProfileModal = ({ open, onOpenChange }: ProfileModalProps) => {
  const [activeTab, setActiveTab] = useState("general");
  const [profileImage, setProfileImage] = useState<string | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const modalRef = useRef<HTMLDivElement>(null);
  const { user, logout } = useAuth();
  
  // Form states for editable fields
  const [formData, setFormData] = useState({
    full_name: user?.name || '',
    email: user?.email || '',
    phone: '',
    location: '',
    about: ''
  });

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
    { id: "general", label: "General", icon: User },
    // { id: "account", label: "Account", icon: Settings },
    // { id: "chats", label: "Chats", icon: MessageSquare },
    // { id: "video", label: "Video & voice", icon: Video },
    // { id: "notifications", label: "Notifications", icon: Bell },
    // { id: "personalization", label: "Personalization", icon: Palette },
    // { id: "storage", label: "Storage", icon: HardDrive },
    // { id: "shortcuts", label: "Shortcuts", icon: Keyboard },
    // { id: "help", label: "Help", icon: HelpCircle },
  ];

  // Get user initials for avatar fallback
  const getUserInitials = () => {
    if (!user?.name) return 'U';
    return user.name
      .split(' ')
      .map(name => name[0])
      .join('')
      .toUpperCase();
  };

  // Handle profile image upload
  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Please select a valid image file');
        return;
      }
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('Image size should be less than 5MB');
        return;
      }
      
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        setProfileImage(result);
        alert('Profile image updated successfully');
      };
      reader.readAsDataURL(file);
    }
  };

  // Handle form updates
  const handleUpdateProfile = async () => {
    setIsUpdating(true);
    try {
      // Here you would typically call an API to update the user profile
      // For now, we'll just show a success message
      alert('Profile updated successfully');
    } catch (error) {
      alert('Failed to update profile');
    } finally {
      setIsUpdating(false);
    }
  };

  // Handle logout
  const handleLogout = async () => {
    try {
      logout();
      onOpenChange(false);
      alert('Logged out successfully');
    } catch (error) {
      alert('Failed to logout');
    }
  };

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
        {/* <div className="w-64 bg-muted p-4 rounded-l-lg">
          <div className="mb-6">
            <h2 className="text-lg font-serif font-semibold">Profile Settings</h2>
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
        </div> */}

        {/* Main Content */}
        <div className="flex-1 p-6 overflow-y-hidden">
          <div className="mb-2">
            <h2 className="text-2xl text-center font-serif font-semibold">Profile Settings</h2>
          </div>
          {activeTab === "general" && (
            <div className="space-y-6">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <div className="h-20 w-20 rounded-full bg-primary flex items-center justify-center">
                    {profileImage ? (
                      <img 
                        src={profileImage} 
                        alt={user?.name || "User"} 
                        className="h-20 w-20 rounded-full object-cover"
                      />
                    ) : (
                      <span className="text-primary-foreground text-lg font-semibold font-serif">
                        {getUserInitials()}
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="absolute -bottom-2 -right-2 h-8 w-8 rounded-full bg-background border-2 border-border flex items-center justify-center hover:bg-accent transition-colors duration-200"
                  >
                    <Camera className="h-4 w-4" />
                  </button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleImageUpload}
                  />
                </div>
                <div className="flex-1">
                  <h2 className="text-2xl font-bold font-serif">
                    {user?.name || 'User'}
                  </h2>
                  <p className="text-sm text-muted-foreground mb-2">{user?.email}</p>
                  <button 
                    onClick={() => fileInputRef.current?.click()}
                    className="flex items-center px-3 py-1 text-sm text-muted-foreground hover:text-foreground hover:bg-accent rounded-md transition-colors duration-200"
                  >
                    <Upload className="mr-2 h-4 w-4" />
                    Change profile picture
                  </button>
                </div>
              </div>

              <div className="border-t border-border pt-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Full Name</label>
                    <input 
                      type="text"
                      value={formData.full_name}
                      onChange={(e) => setFormData(prev => ({ ...prev, full_name: e.target.value }))}
                      placeholder="Enter your full name"
                      className="w-full px-3 py-2 border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent bg-background"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1">Email</label>
                    <input 
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                      placeholder="Enter your email"
                      className="w-full px-3 py-2 border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent bg-background"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Phone Number</label>
                    <input 
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
                      placeholder="Enter your phone number"
                      className="w-full px-3 py-2 border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent bg-background"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Location</label>
                    <input 
                      type="text"
                      value={formData.location}
                      onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
                      placeholder="Enter your location"
                      className="w-full px-3 py-2 border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent bg-background"
                    />
                  </div>
                </div>

                <div className="flex gap-3 mt-6">
                  <button 
                    onClick={handleUpdateProfile}
                    disabled={isUpdating}
                    className="flex-1 bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                  >
                    {isUpdating ? 'Updating...' : 'Update Profile'}
                  </button>
                  <button 
                    onClick={() => onOpenChange(false)}
                    className="px-4 py-2 border border-input text-foreground rounded-lg hover:bg-accent transition-colors duration-200 font-medium"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === "account" && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold font-serif">Account Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Username</label>
                  <input 
                    type="text"
                    defaultValue="johndoe" 
                    className="w-full px-3 py-2 border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent bg-background"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Change Password</label>
                  <input 
                    type="password" 
                    placeholder="Enter new password" 
                    className="w-full px-3 py-2 border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent bg-background"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Timezone</label>
                  <input 
                    type="text"
                    defaultValue="UTC+05:30" 
                    className="w-full px-3 py-2 border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent bg-background"
                  />
                </div>
              </div>
            </div>
          )}

          {activeTab === "notifications" && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold font-serif">Notification Preferences</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium">Email notifications</label>
                  <input type="checkbox" defaultChecked className="h-4 w-4 text-primary" />
                </div>
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium">Push notifications</label>
                  <input type="checkbox" defaultChecked className="h-4 w-4 text-primary" />
                </div>
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium">SMS notifications</label>
                  <input type="checkbox" className="h-4 w-4 text-primary" />
                </div>
              </div>
            </div>
          )}

          {/* Add other tab contents as needed */}
          {activeTab !== "general" && activeTab !== "account" && activeTab !== "notifications" && (
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

export default ProfileModal;