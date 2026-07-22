import React from "react";

export default function Footer() {
  return (
    <footer className="border-t border-white/5 bg-black/30 backdrop-blur-md py-12 px-6">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6 text-sm text-zinc-500">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 rounded-md bg-zinc-800 flex items-center justify-center font-bold text-zinc-400 text-xs">
            D
          </div>
          <span>
            © {new Date().getFullYear()} Dog<span className="text-zinc-400 font-semibold">AID</span>. Inspired by Clay.com aesthetic.
          </span>
        </div>

        <div className="flex items-center space-x-2 font-mono text-xs bg-emerald-950/20 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded-full">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span>ONNX Inference Service Operational</span>
        </div>
      </div>
    </footer>
  );
}
