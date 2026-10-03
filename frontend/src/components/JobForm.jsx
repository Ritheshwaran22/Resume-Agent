import React from 'react';
import { Briefcase, FileText, Sparkles, ArrowRight } from 'lucide-react';
import Button from './Button';

export default function JobForm({
  jobTitle,
  setJobTitle,
  jobDescription,
  setJobDescription,
  onSubmit,
  isSubmitting = false,
  disabled = false,
}) {
  const isReady = jobTitle.trim().length > 2 && jobDescription.trim().length > 30;

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (isReady && !isSubmitting && !disabled) {
          onSubmit();
        }
      }}
      className="space-y-5"
    >
      <div>
        <label
          htmlFor="job-title"
          className="block text-xs font-semibold text-[#0a1b33] uppercase tracking-wider mb-2"
        >
          Target Job Title
        </label>
        <div className="relative rounded-2xl border border-gray-200 bg-white focus-within:border-[#0a152d] focus-within:ring-1 focus-within:ring-[#0a152d] transition-all shadow-xs">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-400">
            <Briefcase className="w-4 h-4" />
          </div>
          <input
            id="job-title"
            type="text"
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
            placeholder="e.g. Senior Backend Engineer (Python / Django)"
            className="w-full pl-11 pr-4 py-3.5 text-sm sm:text-base text-[#0a1b33] placeholder-gray-400 bg-transparent rounded-2xl focus:outline-none"
            disabled={disabled || isSubmitting}
            required
          />
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-2">
          <label
            htmlFor="job-description"
            className="block text-xs font-semibold text-[#0a1b33] uppercase tracking-wider"
          >
            Job Description
          </label>
          <span className="text-xs text-gray-400">
            {jobDescription.length} characters
          </span>
        </div>
        <div className="rounded-2xl border border-gray-200 bg-white focus-within:border-[#0a152d] focus-within:ring-1 focus-within:ring-[#0a152d] transition-all shadow-xs">
          <textarea
            id="job-description"
            rows={7}
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the complete job description, requirements, responsibilities, and qualifications here..."
            className="w-full p-4 text-sm sm:text-base text-[#0a1b33] placeholder-gray-400 bg-transparent rounded-2xl focus:outline-none resize-y min-h-[140px]"
            disabled={disabled || isSubmitting}
            required
          />
        </div>
        <p className="mt-1.5 text-xs text-gray-400">
          Paste the raw requirements so the agent can identify matching skills, missing demonstrated skills, and truthful suggestions.
        </p>
      </div>

      <div className="pt-2">
        <Button
          type="submit"
          variant="primary"
          size="lg"
          className="w-full sm:w-auto"
          disabled={!isReady || isSubmitting || disabled}
          icon={ArrowRight}
          iconPosition="right"
        >
          {isSubmitting ? 'Analyzing Resume...' : 'Analyze Resume'}
        </Button>
      </div>
    </form>
  );
}
