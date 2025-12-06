
import { LiquidEffectAnimation } from "@/app/components/ui/liquid-effect-animation";
import { Button } from "@/app/components/ui/button";
import { Music } from 'lucide-react';

export default function Home() {
  const handleCallAgent = async () => {
    try {
      const response = await fetch('/api/agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: 'Hello from the frontend!' }),
      });
      const data = await response.json();
      alert(`Agent says: ${data.reply}`);
    } catch (error) {
      console.error('Error calling agent:', error);
      alert('Failed to connect to the agent.');
    }
  };

  return (
    <main className="relative flex min-h-screen flex-col items-center justify-center p-24 overflow-hidden">
      <LiquidEffectAnimation />
      <div className="z-10 text-center p-8 rounded-xl bg-black/30 backdrop-blur-md border border-gray-700 shadow-lg">
        <h1 className="text-7xl font-extrabold tracking-tighter text-white drop-shadow-lg">
          UNLEASH THE NOISE
        </h1>
        <p className="mt-4 text-lg text-gray-300 max-w-2xl mx-auto">
          We are the architects of sonic chaos, the masters of riffage, and the bringers of the mosh. Join us on our quest for auditory domination.
        </p>
        <Button 
          className="mt-8 bg-hot-pink text-white font-bold py-3 px-6 rounded-full hover:bg-electric-blue transition-all duration-300 transform hover:scale-105"
          onClick={handleCallAgent}
        >
          <Music className="mr-2 h-4 w-4" /> Call the Agent
        </Button>
      </div>
    </main>
  );
}
