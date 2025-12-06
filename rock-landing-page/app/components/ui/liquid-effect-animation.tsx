
"use client"
import { useEffect, useRef } from "react"

export function LiquidEffectAnimation() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    if (!canvasRef.current) return

    // Load the script dynamically
    const script = document.createElement("script")
    script.type = "module"
    script.textContent = `
      import LiquidBackground from 'https://cdn.jsdelivr.net/npm/threejs-components@0.0.22/build/backgrounds/liquid1.min.js';
      const canvas = document.getElementById('liquid-canvas');
      if (canvas) {
        const app = LiquidBackground(canvas);
        // Using a high-quality rock/texture image for the liquid effect
        app.loadImage('https://images.unsplash.com/photo-1614850523459-c2f4c699c52e?q=80&w=1200&auto=format&fit=crop'); 
        app.liquidPlane.material.metalness = 0.75;
        app.liquidPlane.material.roughness = 0.25;
        app.liquidPlane.uniforms.displacementScale.value = 5;
        app.setRain(false);
      }
    `
    document.body.appendChild(script)

    return () => {
        // Cleanup script if component unmounts
        if(document.body.contains(script)) {
            document.body.removeChild(script)
        }
    }
  }, [])

  return <canvas id="liquid-canvas" ref={canvasRef} className="fixed top-0 left-0 w-full h-full object-cover -z-10 opacity-60" />
}
