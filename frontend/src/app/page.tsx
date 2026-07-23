import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import BentoGrid from "@/components/BentoGrid";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground font-sans relative overflow-hidden">
      {/* Background radial overlays */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-[600px] pointer-events-none z-0">
        <div className="absolute top-[-100px] left-[10%] w-[350px] h-[350px] bg-brand-violet/10 blur-[130px] rounded-full" />
        <div className="absolute top-[100px] right-[10%] w-[350px] h-[350px] bg-brand-cyan/8 blur-[130px] rounded-full" />
      </div>

      <Navbar />
      
      <main className="flex-grow z-10 relative">
        <Hero />
        <BentoGrid />
      </main>

      <Footer />
    </div>
  );
}
