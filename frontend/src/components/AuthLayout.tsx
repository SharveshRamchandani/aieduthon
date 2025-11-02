import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import femaleEducatorImg from "@/assets/generated_images/Female_educator_professional_headshot_6882492e.png";
import maleTeacherImg from "@/assets/generated_images/Male_teacher_professional_headshot_336223c3.png";
import youngEducatorImg from "@/assets/generated_images/Young_educator_professional_headshot_9f7e1f6d.png";
import teachersImg from "@/assets/generated_images/Teachers_collaborating_with_technology_3aa29599.png";

const testimonials = [
  {
    avatar: femaleEducatorImg,
    name: "Dr. Sarah Mitchell",
    handle: "@drsarahmitchell",
    text: "This platform has revolutionized how I prepare my biology lectures. What used to take hours now takes minutes, and the quality is outstanding!",
  },
  {
    avatar: maleTeacherImg,
    name: "James Rodriguez",
    handle: "@profrodriguez",
    text: "As a high school physics teacher, I've tried many tools, but this AI presentation generator truly understands educational content structure.",
  },
  {
    avatar: youngEducatorImg,
    name: "Priya Sharma",
    handle: "@teacherpriya",
    text: "My students are more engaged than ever. The presentations are professional, clear, and perfectly adapted to their learning level.",
  },
];

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  subtitle: string;
}

export default function AuthLayout({ children, title, subtitle }: AuthLayoutProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % testimonials.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const nextTestimonial = () => {
    setCurrentIndex((prev) => (prev + 1) % testimonials.length);
  };

  const prevTestimonial = () => {
    setCurrentIndex((prev) => (prev - 1 + testimonials.length) % testimonials.length);
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left Panel - Testimonials */}
      <div className="hidden lg:flex relative overflow-hidden bg-muted/30">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-10"
          style={{ backgroundImage: `url(${teachersImg})` }}
        />
        <div className="relative z-10 flex flex-col items-center justify-center p-12 w-full">
          <div className="max-w-lg w-full">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentIndex}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="bg-card border border-border rounded-2xl p-8 shadow-lg"
              >
                <div className="flex items-start gap-4 mb-6">
                  <img
                    src={testimonials[currentIndex].avatar}
                    alt={testimonials[currentIndex].name}
                    className="w-12 h-12 rounded-full object-cover"
                  />
                  <div>
                    <h3 className="font-semibold">{testimonials[currentIndex].name}</h3>
                    <p className="text-sm text-muted-foreground">
                      {testimonials[currentIndex].handle}
                    </p>
                  </div>
                </div>
                <p className="text-card-foreground leading-relaxed">
                  {testimonials[currentIndex].text}
                </p>
              </motion.div>
            </AnimatePresence>

            <div className="flex items-center justify-center gap-4 mt-8">
              <button
                onClick={prevTestimonial}
                className="w-10 h-10 rounded-lg border border-border hover:bg-accent flex items-center justify-center"
                data-testid="button-prev-testimonial"
              >
                <ChevronLeft className="h-5 w-5" />
              </button>
              <div className="flex gap-2">
                {testimonials.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentIndex(index)}
                    className={`w-2 h-2 rounded-full transition-all ${
                      index === currentIndex ? "bg-primary w-6" : "bg-muted-foreground/30"
                    }`}
                    data-testid={`button-testimonial-${index}`}
                  />
                ))}
              </div>
              <button
                onClick={nextTestimonial}
                className="w-10 h-10 rounded-lg border border-border hover:bg-accent flex items-center justify-center"
                data-testid="button-next-testimonial"
              >
                <ChevronRight className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex items-center justify-center p-8 lg:p-12">
        <div className="w-full max-w-md space-y-8">
          <div className="space-y-2">
            <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
            <p className="text-muted-foreground">{subtitle}</p>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}