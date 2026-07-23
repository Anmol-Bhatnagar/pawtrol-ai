"use client"

import React from "react";
import { Cpu, Database, CpuIcon, Eye, Zap, Layers, Terminal } from "lucide-react";

export default function BentoGrid() {
  // Mouse movement handler to set variables for radial highlights on hover
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    e.currentTarget.style.setProperty("--x", `${x}px`);
    e.currentTarget.style.setProperty("--y", `${y}px`);
  };

  return (
    <section id="features" className="py-24 px-6 relative max-w-7xl mx-auto">
      {/* Background spotlights */}
      <div className="absolute bottom-10 right-10 w-[500px] h-[300px] bg-brand-cyan/2 blur-[100px] rounded-full pointer-events-none" />

      {/* Header section titles */}
      <div className="text-center md:text-left mb-16 space-y-4">
        <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full border border-brand-violet/20 bg-brand-violet/5 text-[11px] font-semibold text-brand-violet uppercase tracking-wider">
          <Zap className="w-3.5 h-3.5" />
          <span>Core Capabilities</span>
        </div>
        <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-white leading-tight">
          Supercharged deep learning for lightweight servers
        </h2>
        <p className="max-w-2xl text-sm md:text-base text-zinc-400 font-medium">
          Our architecture bypasses heavy runtime framework overheads. We compile models to ONNX and execute on custom CPU engines to achieve peak efficiency.
        </p>
      </div>

      {/* Asymmetric Bento Grid */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Card 1: ONNX Latency & Performance (Colspan 8) */}
        <div
          onMouseMove={handleMouseMove}
          className="group relative col-span-1 md:col-span-8 rounded-2xl border border-white/10 bg-white/[0.01] hover:bg-white/[0.02] p-8 flex flex-col justify-between transition-all duration-300 overflow-hidden"
        >
          <div className="absolute inset-0 radial-spotlight opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
          <div className="space-y-4">
            <div className="w-10 h-10 rounded-xl bg-brand-violet/10 border border-brand-violet/20 flex items-center justify-center text-brand-violet">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white tracking-tight">
              Ultra-Low Latency Inference
            </h3>
            <p className="text-sm text-zinc-400 max-w-xl font-medium leading-relaxed">
              We compile PyTorch MobileNetV3 architectures into optimized ONNX graph operations. Running on high-performance ONNX CPU runtimes, we strip out PyTorch dependency bloat and reduce prediction speeds to under 15ms.
            </p>
          </div>
          <div className="mt-8 grid grid-cols-3 gap-4 border-t border-white/5 pt-6 font-mono">
            <div className="space-y-1 text-left">
              <span className="text-[10px] text-zinc-500 uppercase tracking-wider">ONNX CPU SPEED</span>
              <div className="text-xl font-bold text-brand-cyan">13.8 ms</div>
            </div>
            <div className="space-y-1 text-left">
              <span className="text-[10px] text-zinc-500 uppercase tracking-wider">PYTORCH SPEED</span>
              <div className="text-xl font-bold text-zinc-500">142.6 ms</div>
            </div>
            <div className="space-y-1 text-left">
              <span className="text-[10px] text-zinc-500 uppercase tracking-wider">LATENCY GAIN</span>
              <div className="text-xl font-bold text-brand-emerald">10.3x Fast</div>
            </div>
          </div>
        </div>

        {/* Card 2: Combined Dataset Engine (Colspan 4) */}
        <div
          onMouseMove={handleMouseMove}
          className="group relative col-span-1 md:col-span-4 rounded-2xl border border-white/10 bg-white/[0.01] hover:bg-white/[0.02] p-8 flex flex-col justify-between transition-all duration-300 overflow-hidden"
        >
          <div className="absolute inset-0 radial-spotlight opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
          <div className="space-y-4">
            <div className="w-10 h-10 rounded-xl bg-brand-cyan/10 border border-brand-cyan/20 flex items-center justify-center text-brand-cyan">
              <Database className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white tracking-tight">
              Consolidated Datasets
            </h3>
            <p className="text-sm text-zinc-400 font-medium leading-relaxed">
              Automatic scraper that merges Stanford Dogs (120 breeds) and Oxford Pets (dog subsets), normalizes labels, and compiles class splits dynamically.
            </p>
          </div>
          <div className="mt-6 flex items-center justify-between text-xs font-mono border-t border-white/5 pt-4 text-zinc-500">
            <span>Stanford Dogs (120)</span>
            <span className="text-brand-cyan">+</span>
            <span>Oxford Pet (37)</span>
          </div>
        </div>

        {/* Card 3: Lightweight Container Footprint (Colspan 4) */}
        <div
          onMouseMove={handleMouseMove}
          className="group relative col-span-1 md:col-span-4 rounded-2xl border border-white/10 bg-white/[0.01] hover:bg-white/[0.02] p-8 flex flex-col justify-between transition-all duration-300 overflow-hidden"
        >
          <div className="absolute inset-0 radial-spotlight opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
          <div className="space-y-4">
            <div className="w-10 h-10 rounded-xl bg-brand-emerald/10 border border-brand-emerald/20 flex items-center justify-center text-brand-emerald">
              <Layers className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white tracking-tight">
              Stateless & Thin Footprint
            </h3>
            <p className="text-sm text-zinc-400 font-medium leading-relaxed">
              Designed to host on micro/free tiers (e.g. Render, Cloud Run). ONNX removes heavy PyTorch dependency installations, reducing Docker image files to below 250MB.
            </p>
          </div>
          <div className="mt-6 grid grid-cols-2 gap-4 border-t border-white/5 pt-4 font-mono text-xs">
            <div className="text-left">
              <div className="text-zinc-500 text-[10px]">DISK VALUE</div>
              <div className="font-semibold text-white">&lt; 250 MB</div>
            </div>
            <div className="text-left">
              <div className="text-zinc-500 text-[10px]">RAM METRIC</div>
              <div className="font-semibold text-white">&lt; 80 MB</div>
            </div>
          </div>
        </div>

        {/* Card 4: JSON Audit Tracing & Observability (Colspan 8) */}
        <div
          onMouseMove={handleMouseMove}
          className="group relative col-span-1 md:col-span-8 rounded-2xl border border-white/10 bg-white/[0.01] hover:bg-white/[0.02] p-8 flex flex-col justify-between transition-all duration-300 overflow-hidden"
        >
          <div className="absolute inset-0 radial-spotlight opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
          <div className="space-y-4">
            <div className="w-10 h-10 rounded-xl bg-zinc-800 border border-white/10 flex items-center justify-center text-white">
              <Terminal className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white tracking-tight">
              Request Correlated Tracing Logs
            </h3>
            <p className="text-sm text-zinc-400 font-medium leading-relaxed">
              Every upload triggers a request tracing correlation key (`X-Request-ID`), allowing unified logging and analysis paths across all operational nodes.
            </p>
          </div>
          <div className="mt-6 border-t border-white/5 pt-4 font-mono text-[10px] text-zinc-400 space-y-1 bg-zinc-950/30 p-4 rounded-xl border border-white/5">
            <span className="text-brand-cyan">JSON LOG STATEMENT:</span>
            <div className="text-left overflow-x-auto whitespace-pre leading-relaxed">
{`{
  "timestamp": "2026-07-23T01:28:02Z",
  "level": "INFO",
  "request_id": "8c37d451-9bf8-466d-a773-fae35bb25a38",
  "message": "Prediction complete: pug (Confidence: 88.42%)",
  "latency_seconds": 0.0138
}`}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
