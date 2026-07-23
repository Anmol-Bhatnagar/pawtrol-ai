"use client";

import React, { useState, useEffect } from "react";
import { ArrowRight, Terminal, UploadCloud, Play, Sparkles } from "lucide-react";

export default function Hero() {
  const [selectedBreed, setSelectedBreed] = useState("pug");
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [result, setResult] = useState<any>(null);

  // Simulated dog breed statistics
  const breedData: Record<string, any> = {
    pug: {
      name: "Pug",
      image: "https://images.unsplash.com/photo-1517849845537-4d257902454a?auto=format&fit=crop&q=80&w=600",
      predictions: [
        { breed: "pug", confidence: 0.8842 },
        { breed: "french_bulldog", confidence: 0.0612 },
        { breed: "boston_terrier", confidence: 0.0321 },
      ],
    },
    chihuahua: {
      name: "Chihuahua",
      image: "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?auto=format&fit=crop&q=80&w=600",
      predictions: [
        { breed: "chihuahua", confidence: 0.9125 },
        { breed: "toy_terrier", confidence: 0.0451 },
        { breed: "pomeranian", confidence: 0.0192 },
      ],
    },
    beagle: {
      name: "Beagle",
      image: "https://images.unsplash.com/photo-1505628346881-b72b27e84530?auto=format&fit=crop&q=80&w=600",
      predictions: [
        { breed: "beagle", confidence: 0.9418 },
        { breed: "harrier", confidence: 0.0381 },
        { breed: "basset_hound", confidence: 0.0102 },
      ],
    },
  };

  const triggerInference = () => {
    setLoading(true);
    setResult(null);
    setLogs([]);

    const logSteps = [
      "POST /api/v1/dogs/classify HTTP/1.1 - payload size: 1.42MB",
      "Image signature verified: Magic Bytes [FF D8 FF E0] -> JPEG detected",
      "Preprocessing: Resizing image dimensions to 256x256...",
      "Preprocessing: Center cropping image dimensions to 224x224...",
      "Preprocessing: Normalizing channels (ImageNet mean & std)...",
      "Session Run: Initializing ONNX session input tensor...",
      "ONNX Execution: MobileNetV3-Large forward pass executed on CPU...",
      "Postprocessing: Mapping output index to breed mappings...",
      "Status Code: 200 OK - Latency: 0.0138s",
    ];

    logSteps.forEach((step, idx) => {
      setTimeout(() => {
        setLogs((prev) => [...prev, step]);
        if (idx === logSteps.length - 1) {
          setLoading(false);
          setResult(breedData[selectedBreed]);
        }
      }, (idx + 1) * 350);
    });
  };

  useEffect(() => {
    triggerInference();
  }, [selectedBreed]);

  return (
    <section id="demo" className="relative pt-32 pb-24 px-6 overflow-hidden grid-overlay">
      {/* Dynamic Radial Spotlight Behind Hero */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-brand-violet/5 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute top-[20%] left-[20%] w-[300px] h-[300px] bg-brand-cyan/5 blur-[100px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto flex flex-col items-center text-center">
        {/* Eyebrow Announcement Badge */}
        <div className="mb-6 inline-flex items-center space-x-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 backdrop-blur-md shadow-[0_0_15px_rgba(255,255,255,0.02)]">
          <Sparkles className="w-3.5 h-3.5 text-brand-cyan animate-pulse" />
          <span className="text-xs font-semibold text-zinc-300">
            Next-Gen Dog Breed Classifier (FastAPI + ONNX Runtime)
          </span>
        </div>

        {/* Hero Title */}
        <h1 className="max-w-4xl text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight text-white leading-tight">
          Build cognitive systems to identify{" "}
          <span className="bg-gradient-to-r from-brand-violet via-brand-cyan to-brand-emerald bg-clip-text text-transparent">
            dog breeds
          </span>{" "}
          instantly
        </h1>

        {/* Hero Subtext */}
        <p className="max-w-2xl mt-6 text-base md:text-lg text-zinc-400 font-medium">
          A highly-optimized deep learning classification pipeline trained on combined Stanford Dogs & Oxford Pet datasets. Deployed as a lightweight ONNX runtime microservice.
        </p>

        {/* CTA Buttons */}
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
          <a
            href="#demo"
            className="w-full sm:w-auto px-6 py-3 rounded-full text-sm font-semibold bg-white text-black hover:bg-zinc-200 transition-all duration-200 shadow-[0_0_30px_rgba(255,255,255,0.15)] flex items-center justify-center space-x-2"
          >
            <span>Try Live Sandbox</span>
            <ArrowRight className="w-4 h-4" />
          </a>
          <a
            href="#api"
            className="w-full sm:w-auto px-6 py-3 rounded-full text-sm font-semibold glass-panel text-white hover:bg-white/5 transition-all duration-200 flex items-center justify-center space-x-2"
          >
            <span>View API Endpoints</span>
          </a>
        </div>

        {/* Interactive Dashboard Workspace Card */}
        <div className="w-full max-w-4xl mt-16 glass-panel rounded-2xl border border-white/10 shadow-[0_0_50px_rgba(0,0,0,0.5)] overflow-hidden">
          {/* Dashboard Header Bar */}
          <div className="h-12 border-b border-white/5 bg-white/[0.01] px-4 flex items-center justify-between">
            <div className="flex items-center space-x-1.5">
              <div className="w-3 h-3 rounded-full bg-zinc-700" />
              <div className="w-3 h-3 rounded-full bg-zinc-700" />
              <div className="w-3 h-3 rounded-full bg-zinc-700" />
            </div>
            <div className="text-xs text-zinc-500 font-mono tracking-widest flex items-center space-x-1">
              <span>SANDBOX_CLASSIFIER_V1.ONNX</span>
            </div>
            <div className="w-12" />
          </div>

          {/* Interactive Workspace Grid */}
          <div className="grid grid-cols-1 md:grid-cols-12 min-h-[380px]">
            {/* Left Control Panel */}
            <div className="col-span-1 md:col-span-4 p-6 border-r border-white/5 flex flex-col justify-between space-y-6">
              <div>
                <h3 className="text-sm font-semibold text-white text-left mb-4">
                  Select Dog Photo
                </h3>
                <div className="grid grid-cols-3 gap-2">
                  {Object.keys(breedData).map((key) => (
                    <button
                      key={key}
                      onClick={() => setSelectedBreed(key)}
                      className={`relative aspect-square rounded-lg overflow-hidden border-2 transition-all ${
                        selectedBreed === key
                          ? "border-brand-cyan scale-102"
                          : "border-transparent opacity-60 hover:opacity-100"
                      }`}
                    >
                      <img
                        src={breedData[key].image}
                        alt={key}
                        className="w-full h-full object-cover"
                      />
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <button
                  onClick={triggerInference}
                  disabled={loading}
                  className="w-full py-3 rounded-xl bg-brand-violet hover:bg-brand-violet/90 text-white font-semibold text-xs transition-all duration-200 flex items-center justify-center space-x-2 shadow-[0_0_20px_rgba(124,58,237,0.3)] disabled:opacity-55"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Execute ONNX Inference</span>
                </button>
              </div>
            </div>

            {/* Center Preview Panel */}
            <div className="col-span-1 md:col-span-4 p-6 border-r border-white/5 flex flex-col items-center justify-center bg-white/[0.005]">
              <div className="relative w-full aspect-square rounded-xl overflow-hidden border border-white/10 max-w-[200px] shadow-[0_0_25px_rgba(0,0,0,0.3)]">
                <img
                  src={breedData[selectedBreed].image}
                  alt="Selected Dog"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>

            {/* Right Audit Logs / Output Panel */}
            <div className="col-span-1 md:col-span-4 p-6 flex flex-col justify-between space-y-6 bg-zinc-950/40 text-left font-mono">
              <div className="space-y-4">
                <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-widest flex items-center space-x-1">
                  <Terminal className="w-3.5 h-3.5 text-brand-cyan" />
                  <span>Real-time Log Stream</span>
                </h4>
                <div className="space-y-1.5 text-[10px] text-zinc-400 overflow-y-auto max-h-[180px] leading-relaxed">
                  {logs.map((log, idx) => (
                    <div key={idx} className="flex items-start space-x-1.5">
                      <span className="text-brand-violet font-semibold">&gt;</span>
                      <span>{log}</span>
                    </div>
                  ))}
                  {loading && (
                    <div className="text-brand-cyan animate-pulse font-semibold">
                      &gt; Computing inference graph...
                    </div>
                  )}
                </div>
              </div>

              {/* Inference Results Output */}
              {result && !loading && (
                <div className="pt-4 border-t border-white/5 space-y-3">
                  <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-widest">
                    Prediction Outputs
                  </h4>
                  <div className="space-y-2">
                    {result.predictions.map((pred: any, idx: number) => (
                      <div key={idx} className="space-y-1">
                        <div className="flex justify-between text-xs font-semibold">
                          <span className="text-white capitalize">
                            {pred.breed.replace("_", " ")}
                          </span>
                          <span className="text-brand-cyan font-mono">
                            {(pred.confidence * 100).toFixed(2)}%
                          </span>
                        </div>
                        <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full bg-gradient-to-r ${
                              idx === 0
                                ? "from-brand-violet to-brand-cyan"
                                : "from-zinc-700 to-zinc-600"
                            }`}
                            style={{ width: `${pred.confidence * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
