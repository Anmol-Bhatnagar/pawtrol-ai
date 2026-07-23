"use client"

import React, { useState } from "react";
import { Menu, X, ArrowRight } from "lucide-react";

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 glass-panel border-b border-white/5 bg-background/50 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-violet to-brand-cyan flex items-center justify-center font-bold text-white text-sm shadow-[0_0_15px_rgba(124,58,237,0.3)]">
            D
          </div>
          <span className="font-bold text-white text-lg tracking-tight">
            Dog<span className="text-brand-cyan">AID</span>
          </span>
        </div>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center space-x-8">
          <a
            href="#features"
            className="text-sm font-medium text-zinc-400 hover:text-white transition-colors duration-200"
          >
            Features
          </a>
          <a
            href="#demo"
            className="text-sm font-medium text-zinc-400 hover:text-white transition-colors duration-200"
          >
            Interactive Demo
          </a>
          <a
            href="#metrics"
            className="text-sm font-medium text-zinc-400 hover:text-white transition-colors duration-200"
          >
            Accuracy Metrics
          </a>
          <a
            href="#api"
            className="text-sm font-medium text-zinc-400 hover:text-white transition-colors duration-200"
          >
            API Docs
          </a>
        </nav>

        {/* Right Action Button */}
        <div className="hidden md:flex items-center space-x-4">
          <a
            href="#demo"
            className="px-4 py-2 rounded-full text-xs font-semibold bg-white text-black hover:bg-zinc-200 transition-colors duration-200 flex items-center space-x-1 shadow-[0_0_20px_rgba(255,255,255,0.1)]"
          >
            <span>Classify Image</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </a>
        </div>

        {/* Mobile Menu Toggle Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 text-zinc-400 hover:text-white transition-colors duration-200"
          aria-label="Toggle menu"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden glass-panel border-b border-white/5 bg-background/95 py-6 px-6 space-y-4">
          <nav className="flex flex-col space-y-4">
            <a
              href="#features"
              onClick={() => setMobileMenuOpen(false)}
              className="text-base font-medium text-zinc-400 hover:text-white transition-colors duration-200"
            >
              Features
            </a>
            <a
              href="#demo"
              onClick={() => setMobileMenuOpen(false)}
              className="text-base font-medium text-zinc-400 hover:text-white transition-colors duration-200"
            >
              Interactive Demo
            </a>
            <a
              href="#metrics"
              onClick={() => setMobileMenuOpen(false)}
              className="text-base font-medium text-zinc-400 hover:text-white transition-colors duration-200"
            >
              Accuracy Metrics
            </a>
            <a
              href="#api"
              onClick={() => setMobileMenuOpen(false)}
              className="text-base font-medium text-zinc-400 hover:text-white transition-colors duration-200"
            >
              API Docs
            </a>
          </nav>
          <div className="pt-4 border-t border-white/5">
            <a
              href="#demo"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full justify-center px-4 py-3 rounded-full text-sm font-semibold bg-white text-black hover:bg-zinc-200 transition-colors duration-200 flex items-center space-x-1 shadow-[0_0_20px_rgba(255,255,255,0.1)]"
            >
              <span>Classify Image</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>
      )}
    </header>
  );
}
