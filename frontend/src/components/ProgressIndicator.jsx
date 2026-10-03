import React from 'react';
import { motion } from 'motion/react';
import { Check, Circle } from 'lucide-react';

export default function ProgressIndicator({
  currentStep = 1, // 0 to 4
  steps = [
    { id: 1, label: 'Extracting resume information' },
    { id: 2, label: 'Comparing required skills' },
    { id: 3, label: 'Checking evidence' },
    { id: 4, label: 'Preparing recommendations' },
  ],
}) {
  return (
    <div className="w-full max-w-md mx-auto bg-white rounded-3xl border border-gray-200 p-6 sm:p-8 shadow-xs">
      <div className="text-center mb-6">
        <h4 className="font-display font-semibold text-lg text-[#0a1b33]">
          Analyzing your resume...
        </h4>
        <p className="text-xs sm:text-sm text-gray-500 mt-1">
          Evaluating demonstrated skills against stated requirements
        </p>
        <p className="text-xs text-blue-600 font-medium mt-2 animate-pulse">
          This may take a little while...
        </p>
      </div>



      <div className="space-y-4">
        {steps.map((step, index) => {
          const isDone = index < currentStep;
          const isCurrent = index === currentStep;
          const isPending = index > currentStep;

          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.08 }}
              className={`flex items-center justify-between p-3.5 rounded-2xl border transition-all ${
                isCurrent
                  ? 'bg-gray-50/80 border-[#0a152d]/30 shadow-xs'
                  : isDone
                  ? 'bg-white border-gray-100'
                  : 'bg-white/40 border-gray-100/60 opacity-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <span
                  className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold ${
                    isDone
                      ? 'bg-[#0a152d] text-white'
                      : isCurrent
                      ? 'bg-white border-2 border-[#0a152d] text-[#0a152d]'
                      : 'bg-gray-100 text-gray-400'
                  }`}
                >
                  {isDone ? (
                    <Check className="w-3.5 h-3.5 stroke-[2.5]" />
                  ) : isCurrent ? (
                    <span className="w-2 h-2 rounded-full bg-[#0a152d] animate-pulse" />
                  ) : (
                    <span>{index + 1}</span>
                  )}
                </span>
                <span
                  className={`text-sm ${
                    isCurrent
                      ? 'font-semibold text-[#0a1b33]'
                      : isDone
                      ? 'text-[#0a1b33]'
                      : 'text-gray-400'
                  }`}
                >
                  {step.label}
                </span>
              </div>

              <div className="text-xs font-mono">
                {isDone && <span className="text-[#0a152d] font-semibold">✓</span>}
                {isCurrent && <span className="text-[#0a152d] animate-pulse font-bold">•</span>}
                {isPending && <span className="text-gray-300">○</span>}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
