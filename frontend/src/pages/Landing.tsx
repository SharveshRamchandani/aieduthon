import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { MoveRight, PhoneCall } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { TopBar } from '@/components/TopBar';
import { 
  ArrowRight, CheckCircle2, Zap, LayoutTemplate, 
  Sparkles, Globe, FileText, Presentation 
} from 'lucide-react';
import Animation1 from "@/components/Animation";
import VerticalCarousel from "@/components/Carousel";
import VerticalCarousel2 from "../components/Carousel2";
import { Footer7 } from "@/components/Footer";




const Landing = () => {
  const [titleNumber, setTitleNumber] = useState(0);
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const titles = useMemo(
    () => ["Students", "Teachers & Educators", "Working Professionals", "Startup Teams & Creator", "Researchers & Academics","Corporate Teams"],
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
const [displayedText1, setDisplayedText1] = useState('');
  const [displayedText2, setDisplayedText2] = useState('');

  const [showCursor1, setShowCursor1] = useState(true);
  
  const [showCursorSubtitle, setShowCursorSubtitle] = useState(false);

  const text1 = "While Coco generates your presentation, just sit back and relax!";
  
  

  useEffect(() => {
    let timeout1: ReturnType<typeof setTimeout>;
    let timeout2: ReturnType<typeof setTimeout>;

    let cursorTimeout1: ReturnType<typeof setTimeout>;
   

    // First line typewriter
    const typeText1 = () => {
      let i = 0;
      const type = () => {
        if (i < text1.length) {
          setDisplayedText1(text1.slice(0, i + 1));
          i++;
          timeout1 = setTimeout(type, 100);
        } 
      };
      type();
    };

    

    // Start the animation
    typeText1();
    

    // Cleanup
    return () => {
      clearTimeout(timeout1);
      clearTimeout(timeout2);
   
   
    };
  }, []);

  return (
    <div className="w-full min-h-screen overflow-y-hidden">
      <TopBar />
      <div className="container mx-auto ">  
        <div className="flex gap-8 py-50 lg:py-34 sm:py-32 md:py-32 items-center justify-center flex-col ">
          
          <div className="flex gap-4 flex-col ">
            <h1 className="text-5xl md:text-7xl sm:text-7xl max-w-8xl tracking-tighter text-center font-semibold pt-20 scrollbar-hide">
              <span className="text-primary">Personalized Presentation Generator for</span>
              <span className=" text-8xl relative flex w-full justify-center overflow-hidden text-center md:pb-4 md:pt-6">
                &nbsp;
                {titles.map((title, index) => (
                  <motion.span
                    key={index}
                    className="absolute font-bold"
                    initial={{ opacity: 0, y: -100 }}
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

              <div>
              </div>
            </h1>

          <div className="flex gap-4 flex-col items-center pt-16 pb-16">
            <button className="btn" onClick={handleGetStarted}>
              <svg
                className="sparkle"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                strokeWidth="1"
              >
                <path d="M14.187 8.096L15 5.25L15.813 8.096C16.0231 8.82683 16.4171 9.49215 16.9577 10.0294C17.4984 10.5666 18.1676 10.9578 18.9005 11.1649L21.75 12L18.9005 12.8351C18.1676 13.0422 17.4984 13.4334 16.9577 13.9706C16.4171 14.5078 16.0231 15.1732 15.813 15.904L15 18.75L14.187 15.904C13.9769 15.1732 13.5829 14.5078 13.0423 13.9706C12.5016 13.4334 11.8324 13.0422 11.0995 12.8351L8.25 12L11.0995 11.1649C11.8324 10.9578 12.5016 10.5666 13.0423 10.0294C13.5829 9.49215 13.9769 8.82683 14.187 8.096Z" />
                <path d="M6 12H8.25" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M18.75 12H21" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M10.0913 3.62305L11.25 6.75" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M13.7412 17.25L12.5825 20.377" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M3.62305 13.9087L6.75 12.75" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M17.25 13.7412L20.377 12.5825" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <span className="text">Get Started</span>
              <MoveRight className="w-6 h-6 " />
            </button>
          </div>
          </div>


          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 w-full max-w-[1400px] mx-auto">
            
             {/* Row 1: Text on the left + right card */}
             <div className="flex items-top justify-start">
              <div className="w-full lg:max-w-2xl space-y-4 ">
              <h2 className="text-6xl  font-bold mb-4   text-left">
                    Create professional, structured presentations in seconds with AI.
                  </h2>
                
                
              </div>
            </div>

            <div className="flex justify-end">
              <div className="w-full lg:w-[1000px] rounded-3xl p-2 border  hover:shadow-lg transition-all group overflow-hidden relative min-h-[400px] bg-black text-white border-gray-900 dark:bg-white dark:text-black dark:border-gray-200">
                <div className="relative z-10">
                  
                </div>

                
                  <div className="p-4 h-full w-full flex items-center justify-center">
                    <div className="w-full h-full" style={{ height: '100%', minHeight: '350px' }}>
                      <VerticalCarousel />
                    </div>
                  
                </div>
              </div>
            </div>
            
            
            {/* Row 2: Left card + text on the right */}
            
            <div className="flex justify-end pt-10 ">
              <div className="flex justify-end">
              <div className="w-full lg:w-[700px] rounded-3xl p-2 border  hover:shadow-lg transition-all group overflow-hidden relative min-h-[400px] bg-black text-white border-gray-900 dark:bg-white dark:text-black dark:border-gray-200">
                <div className="relative z-10">
                  
                </div>

                
                  <div className="p-4 h-full w-full flex items-center justify-center">
                    <div className="w-full h-full" style={{ height: '100%', minHeight: '350px' }}>
                      <VerticalCarousel2 />
                    </div>
                  
                </div>
              </div>
            </div>
            </div>

           <div className="flex items-start justify-end pt-10">
              <div className="w-full lg:max-w-xl space-y-4 ">
              <h2 className="text-6xl  font-bold mb-4 leading-tight text-right">
                   Define your topic. Get editable, stunning slides.
                                     </h2>
                
                
              </div>
            </div>

           
          </div>


 <div className="min-h-screen flex items-center justify-center">
  <div className="w-[1200px] rounded-3xl p-8 border hover:shadow-lg transition-all overflow-hidden min-h-[600px] bg-black text-white border-gray-900 dark:bg-white dark:text-black dark:border-gray-200">
    
    {/* Center Gradient Div */}
    <div
      className="w-full h-[540px] rounded-2xl
                 flex items-center justify-center
                 bg-[linear-gradient(135deg,#7EC8E3_0%,#9BB8FF_25%,#B9B6FF_50%,#D9C8FF_75%,#E6C7B8_100%)]"
    >
      <h2 className="text-5xl md:text-8xl max-w-3xl font-bold leading-tight text-center">
        So, what do you want to create today?
      </h2>
    </div>

  </div>
</div>



  
  
  
   <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 w-full max-w-[1400px] mx-auto">
  <div className="pt-10">
  <h2 className="text-4xl md:text-7xl font-bold mb-4 leading-tight text-left ">
                    <span className="text-accent-brown block">
                      {displayedText1}
                      {showCursor1 && <span className="animate-pulse">|</span>}
                    </span>
                  </h2>
               

                </div>

                
    <div className="relative z-10 top-20 right-30">
<div className=" items-center justify-center  ">
      <Animation1 />
    </div>
    
    </div>
    
  </div>
   </div>
          <Footer7 />
        </div> 
        
        
      
      <style>{`
        .btn {
          border: none;
          width: 15em;
          height: 4.5em;
          border-radius: 3em;
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 12px;
          background: #1C1A1C;
          cursor: pointer;
          transition: all 450ms ease-in-out;
        }

        .sparkle {
          fill: #AAAAAA;
          transition: all 800ms ease;
        }

        .text {
          font-weight: 600;
          color: #AAAAAA;
          font-size: medium;
        }

        .btn:hover {
          font-weight:800,
          inset 0px -4px 0px 0px rgba(0, 0, 0, 0.2),
          0px 0px 0px 4px rgba(255, 255, 255, 0.2),
          0px 0px 180px 0px #000000;
          transform: translateY(-2px);
        }

        .btn:hover .text {
          color: white;
          font-size:20px,
          transition: 4ms ease-in-out;
        }

        .btn:hover .sparkle {
          fill: white;
          transform: scale(1.2);
        }
        .btn:hover .moveRight{
        background:white,
        }
      `}</style>
    </div>
    
  );
};

export default Landing;