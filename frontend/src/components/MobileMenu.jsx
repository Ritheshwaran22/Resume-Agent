import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, ArrowRight } from 'lucide-react';
import Button from './Button';

export default function MobileMenu({
  isOpen,
  onClose,
  activeView,
  setActiveView,
}) {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 md:hidden flex flex-col bg-white/95 backdrop-blur-md p-6">
        <div className="flex items-center justify-between pb-6 border-b border-gray-100">
          <span className="font-display font-bold text-lg text-[#0a1b33]">
            Resume Agent
          </span>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-gray-900 rounded-full hover:bg-gray-100"
            aria-label="Close menu"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <nav className="flex flex-col gap-4 py-8 text-base font-medium">
          <button
            onClick={() => {
              setActiveView('landing');
              onClose();
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }}
            className="text-left py-2 text-[#0a1b33] hover:text-[#0a152d]"
          >
            Home
          </button>
          <button
            onClick={() => {
              setActiveView('landing');
              onClose();
              setTimeout(() => {
                document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' });
              }, 100);
            }}
            className="text-left py-2 text-gray-600 hover:text-[#0a1b33]"
          >
            How it works
          </button>
          <button
            onClick={() => {
              setActiveView('landing');
              onClose();
              setTimeout(() => {
                document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
              }, 100);
            }}
            className="text-left py-2 text-gray-600 hover:text-[#0a1b33]"
          >
            Features
          </button>
          <button
            onClick={() => {
              setActiveView('landing');
              onClose();
              setTimeout(() => {
                document.getElementById('preview')?.scrollIntoView({ behavior: 'smooth' });
              }, 100);
            }}
            className="text-left py-2 text-gray-600 hover:text-[#0a1b33]"
          >
            Live Preview
          </button>
          <button
            onClick={() => {
              setActiveView('dashboard');
              onClose();
            }}
            className="text-left py-2 font-semibold text-[#0a1b33]"
          >
            Dashboard
          </button>
        </nav>

        <div className="mt-auto pt-6 border-t border-gray-100 flex flex-col gap-3">
          <Button
            variant="primary"
            size="lg"
            className="w-full justify-center"
            onClick={() => {
              setActiveView('dashboard');
              onClose();
            }}
            icon={ArrowRight}
            iconPosition="right"
          >
            Launch Dashboard
          </Button>
        </div>
      </div>
    </AnimatePresence>
  );
}
