import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { TopBar } from '@/components/TopBar';
import { ArrowRight, Sparkles, Zap, Target } from 'lucide-react';
import { motion } from 'framer-motion';
import teacherImg from '@/assets/generated_images/Teacher_presenting_educational_content_ca781504.png';
import aiInterfaceImg from '@/assets/generated_images/AI_presentation_interface_showcase_488dcd59.png';
import teachersImg from '@/assets/generated_images/Teachers_collaborating_with_technology_3aa29599.png';

const features = [
  {
    title: "AI-Powered Generation",
    image: aiInterfaceImg,
    icon: Sparkles,
  },
  {
    title: "Instant Creation",
    image: teacherImg,
    icon: Zap,
  },
  {
    title: "Professional Results",
    image: teachersImg,
    icon: Target,
  },
];

const Landing = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleGetStarted = () => {
    if (user) {
      navigate('/home');
    } else {
      navigate('/login');
    }
  };

  return (
    <section className="relative min-h-screen flex items-center overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-accent/5" />
      <TopBar />
      
      <div className="container mx-auto px-8 py-24 relative z-20">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left Column - Marketing Copy */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="max-w-xl space-y-6"
          >
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-5xl lg:text-6xl font-bold leading-tight tracking-tight"
            >
              Personalized Presentation Generator{" "}
              <span className="text-primary">for Education</span>
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-lg text-muted-foreground leading-relaxed"
            >
              Create professional, structured presentations in seconds with AI. 
              Simply describe your topic, and watch as our intelligent system generates 
              beautiful, editable slides tailored for education.
            </motion.p>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Button
                size="lg"
                onClick={handleGetStarted}
                data-testid="button-get-started"
                className="h-12 px-8 text-base rounded-xl font-semibold"
              >
                Get Started
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </motion.div>
          </motion.div>

          {/* Right Column - Feature Showcase */}
          <div className="relative h-[600px] hidden lg:block">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, scale: 0.8, y: 50 }}
                animate={{
                  opacity: 1,
                  scale: 1,
                  y: 0,
                }}
                transition={{
                  delay: 0.5 + index * 0.2,
                  duration: 0.5,
                }}
                className="absolute"
                style={{
                  top: `${index * 180}px`,
                  left: `${(index % 2) * 150}px`,
                  zIndex: features.length - index,
                }}
              >
                <div className="bg-card border border-border rounded-2xl p-6 shadow-lg w-64 hover:shadow-xl transition-shadow">
                  <div className="aspect-video rounded-lg overflow-hidden mb-4">
                    <img
                      src={feature.image}
                      alt={feature.title}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <feature.icon className="h-5 w-5 text-primary" />
                    </div>
                    <h3 className="font-semibold text-sm">{feature.title}</h3>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Landing;