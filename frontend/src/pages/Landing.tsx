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
          
          <div className="flex gap-4 flex-col">
            <h1 className="text-5xl md:text-7xl max-w-6xl tracking-tighter text-center font-regular">
              <span className="text-primary">Personalized Presentation Generator for</span>
              <span className="relative flex w-full justify-center overflow-hidden text-center md:pb-4 md:pt-1">
                &nbsp;
                {titles.map((title, index) => (
                  <motion.span
                    key={index}
                    className="absolute font-semibold"
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
            <div className="flex gap-4 flex-col items-center">
            <button className="btn" onClick={handleGetStarted}>
            <svg className="sparkle" width="24" height="24" viewBox="0 0 24 24" strokeWidth="1">
                <path d="M14.187 8.096L15 5.25L15.813 8.096C16.0231 8.82683 16.4171 9.49215 16.9577 10.0294C17.4984 10.5666 18.1676 10.9578 18.9005 11.1649L21.75 12L18.9005 12.8351C18.1676 13.0422 17.4984 13.4334 16.9577 13.9706C16.4171 14.5078 16.0231 15.1732 15.813 15.904L15 18.75L14.187 15.904C13.9769 15.1732 13.5829 14.5078 13.0423 13.9706C12.5016 13.4334 11.8324 13.0422 11.0995 12.8351L8.25 12L11.0995 11.1649C11.8324 10.9578 12.5016 10.5666 13.0423 10.0294C13.5829 9.49215 13.9769 8.82683 14.187 8.096Z" />
              <path d="M6 12H8.25" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M18.75 12H21" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M10.0913 3.62305L11.25 6.75" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M13.7412 17.25L12.5825 20.377" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M3.62305 13.9087L6.75 12.75" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M17.25 13.7412L20.377 12.5825" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <span className="text">Get Started</span>
              <MoveRight className="w-4 h-4" />
            </button>
          </div>

            <p className="text-lg  md:text-2xl leading-relaxed tracking-tight text-muted-foreground max-w-6xl text-center">
               Create professional, structured presentations in seconds with AI. 
              Simply describe your topic, and watch as our intelligent system generates 
              beautiful, editable slides tailored for education.
            </p>
            
          </div>
          
        </div>
        
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
          background: linear-gradient(0deg,#A47CF3,#683FEA);
          box-shadow: inset 0px 1px 0px 0px rgba(255, 255, 255, 0.4),
          inset 0px -4px 0px 0px rgba(0, 0, 0, 0.2),
          0px 0px 0px 4px rgba(255, 255, 255, 0.2),
          0px 0px 180px 0px #9917FF;
          transform: translateY(-2px);
        }

        .btn:hover .text {
          color: white;
        }

        .btn:hover .sparkle {
          fill: white;
          transform: scale(1.2);
        }
      `}</style>
    </div>
    
  );
};

export default Landing;