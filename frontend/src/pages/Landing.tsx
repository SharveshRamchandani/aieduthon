import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { MoveRight, PhoneCall } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { TopBar } from '@/components/TopBar';

const Landing = () => {
  const [titleNumber, setTitleNumber] = useState(0);
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const titles = useMemo(
    () => ["Students", "Teachers & Educators", "Working Professionals", "Startup Teams & Creator", "Researchers & Academics","Corporate Trainers & Coaches"],
    []
  );

  const handleGetStarted = () => {
    if (user) {
      navigate('/home');
    } else {
      navigate('/login');
    }
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (titleNumber === titles.length - 1) {
        setTitleNumber(0);
      } else {
        setTitleNumber(titleNumber + 1);
      }
    }, 2000);
    return () => clearTimeout(timeoutId);
  }, [titleNumber, titles]);

  return (
    <div className="w-full min-h-screen">
      <TopBar />
      <div className="container mx-auto">
        <div className="flex gap-8 py-20 lg:py-40 items-center justify-center flex-col">
          <div>
            
          </div>
          <div className="flex gap-4 flex-col">
            <h1 className="text-5xl md:text-7xl max-w-6xl tracking-tighter text-center font-regular">
              <span className="text-primary">Personalized Presentation Generator for</span>
              <span className="relative flex w-full justify-center overflow-hidden text-center md:pb-4 md:pt-1">
                &nbsp;
                {titles.map((title, index) => (
                  <motion.span
                    key={index}
                    className="absolute font-semibold"
                    initial={{ opacity: 0, y: "-100" }}
                    transition={{ type: "spring", stiffness: 50 }}
                    animate={
                      titleNumber === index
                        ? {
                            y: 0,
                            opacity: 1,
                          }
                        : {
                            y: titleNumber > index ? -150 : 150,
                            opacity: 0,
                          }
                    }
                  >
                    {title}
                  </motion.span>
                ))}
              </span>
            </h1>

            <p className="text-lg md:text-2xl leading-relaxed tracking-tight text-muted-foreground max-w-4xl text-center">
               Create professional, structured presentations in seconds with AI. 
              Simply describe your topic, and watch as our intelligent system generates 
              beautiful, editable slides tailored for education.
            </p>
          </div>
          <Button variant="secondary" size="sm" className="gap-4" onClick={handleGetStarted}>
              Get Started <MoveRight className="w-4 h-4" />
            </Button>
        </div>
      </div>
    </div>
  );
};

export default Landing;