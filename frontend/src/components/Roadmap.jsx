import React, { useState } from 'react';
import { Compass, CheckCircle2, ChevronDown, ChevronUp, BookOpen, Target, Wrench, Sparkles, Award } from 'lucide-react';

export default function Roadmap({ roadmapItems }) {
  const items = Array.isArray(roadmapItems) ? roadmapItems : [];
  const [expandedWeeks, setExpandedWeeks] = useState({ 0: true });

  const toggleWeek = (index) => {
    setExpandedWeeks((prev) => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const toggleAll = () => {
    const allExpanded = items.every((_, idx) => expandedWeeks[idx]);
    if (allExpanded) {
      setExpandedWeeks({});
    } else {
      const nextState = {};
      items.forEach((_, idx) => {
        nextState[idx] = true;
      });
      setExpandedWeeks(nextState);
    }
  };

  if (items.length === 0) {
    return (
      <div className="bg-white rounded-3xl border border-gray-200 p-6 sm:p-8 shadow-xs">
        <div className="mb-4">
          <h4 className="font-display font-semibold text-lg sm:text-xl text-[#0a1b33] flex items-center gap-2">
            <Compass className="w-5 h-5 text-[#0a152d]" />
            Targeted Learning Roadmap
          </h4>
          <p className="text-xs sm:text-sm text-gray-500 mt-0.5">
            A step-by-step roadmap to master the skills missing from your demonstrated experience.
          </p>
        </div>
        <div className="p-4 sm:p-5 rounded-2xl bg-gray-50/70 border border-gray-200/70 text-xs sm:text-sm text-gray-600 leading-relaxed">
          No JD-specific learning gaps identified because the job description does not provide enough technical requirements or all required skills are already demonstrated.
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-3xl border border-gray-200 p-6 sm:p-8 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h4 className="font-display font-semibold text-lg sm:text-xl text-[#0a1b33] flex items-center gap-2">
            <Compass className="w-5 h-5 text-[#0a152d]" />
            Targeted Learning Roadmap
          </h4>
          <p className="text-xs sm:text-sm text-gray-500 mt-0.5">
            Prioritized by missing required skills, prerequisite foundations, and optional preferred qualifications.
          </p>
        </div>

        {items.length > 0 && (
          <button
            onClick={toggleAll}
            className="text-xs font-medium text-[#0a152d] hover:text-blue-700 transition-colors self-start sm:self-auto cursor-pointer"
          >
            {items.every((_, idx) => expandedWeeks[idx]) ? 'Collapse All' : 'Expand All Milestones'}
          </button>
        )}
      </div>

      <div className="relative pl-6 sm:pl-8 border-l border-gray-200 ml-3 sm:ml-4 space-y-5">
        {items.map((item, index) => {
          const isExpanded = !!expandedWeeks[index];
          const isPreferred = item.priority === 'preferred';
          const hasRichData = !!(item.why_it_matters || item.what_to_learn?.length || item.practical_task || item.expected_outcome);

          return (
            <div key={index} className="relative group">
              {/* Timeline bullet dot */}
              <div className={`absolute -left-[31px] sm:-left-[39px] top-4 w-4 h-4 rounded-full bg-white border-2 flex items-center justify-center transition-colors ${
                isPreferred ? 'border-purple-600' : 'border-[#0a152d]'
              }`}>
                <div className={`w-1.5 h-1.5 rounded-full ${
                  isPreferred ? 'bg-purple-600' : 'bg-[#0a152d]'
                }`} />
              </div>

              {/* Milestone Card */}
              <div
                className={`rounded-2xl border transition-all ${
                  isExpanded
                    ? 'bg-white border-gray-300 shadow-xs'
                    : 'bg-gray-50/70 border-gray-200/70 hover:border-gray-300'
                }`}
              >
                {/* Header (Clickable to toggle) */}
                <div
                  onClick={() => toggleWeek(index)}
                  className="p-4 sm:p-5 flex items-start justify-between gap-3 cursor-pointer select-none"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-2">
                      <span className="text-xs font-semibold text-[#0a152d] bg-white border border-gray-200 px-2.5 py-0.5 rounded-full shadow-2xs">
                        {item.week}
                      </span>

                      {isPreferred ? (
                        <span className="text-[11px] font-semibold text-purple-700 bg-purple-50 border border-purple-200 px-2.5 py-0.5 rounded-full">
                          Preferred Qualification (Bonus)
                        </span>
                      ) : (
                        <span className="text-[11px] font-semibold text-amber-800 bg-amber-50 border border-amber-200 px-2.5 py-0.5 rounded-full">
                          Core Required Skill
                        </span>
                      )}

                      {item.skill && (
                        <span className="text-[11px] font-medium text-gray-700 bg-gray-100 border border-gray-200/70 px-2 py-0.5 rounded-md">
                          {item.skill}
                        </span>
                      )}
                    </div>

                    <h5 className="font-semibold text-sm sm:text-base text-[#0a1b33]">
                      {item.title}
                    </h5>

                    {!isExpanded && (
                      <p className="text-xs text-gray-500 mt-1 line-clamp-1">
                        {item.description || item.why_it_matters}
                      </p>
                    )}
                  </div>

                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleWeek(index);
                    }}
                    className="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors shrink-0 mt-0.5"
                    aria-label={isExpanded ? 'Collapse' : 'Expand'}
                  >
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-gray-600" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-gray-600" />
                    )}
                  </button>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="px-4 pb-4 sm:px-5 sm:pb-5 pt-0 border-t border-gray-100 space-y-4 mt-1">
                    {/* Why it matters */}
                    {item.why_it_matters && (
                      <div className="pt-3">
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-[#0a1b33] mb-1">
                          <Target className="w-3.5 h-3.5 text-blue-600" />
                          Why it matters
                        </div>
                        <p className="text-xs sm:text-[13px] text-gray-600 leading-relaxed pl-5">
                          {item.why_it_matters}
                        </p>
                      </div>
                    )}

                    {/* What to learn */}
                    {item.what_to_learn && item.what_to_learn.length > 0 && (
                      <div>
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-[#0a1b33] mb-1.5">
                          <BookOpen className="w-3.5 h-3.5 text-indigo-600" />
                          What to learn
                        </div>
                        <ul className="space-y-1.5 pl-5">
                          {item.what_to_learn.map((topic, ti) => (
                            <li key={ti} className="text-xs sm:text-[13px] text-gray-600 flex items-start gap-2">
                              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 shrink-0 mt-1.5" />
                              <span>{topic}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Practical task */}
                    {item.practical_task && (
                      <div className="p-3.5 sm:p-4 rounded-xl bg-gray-50 border border-gray-200/80">
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-[#0a1b33] mb-1.5">
                          <Wrench className="w-3.5 h-3.5 text-amber-600" />
                          Practical task
                        </div>
                        <p className="text-xs sm:text-[13px] text-gray-700 leading-relaxed">
                          {item.practical_task}
                        </p>
                      </div>
                    )}

                    {/* Expected outcome */}
                    {item.expected_outcome && (
                      <div className="p-3.5 sm:p-4 rounded-xl bg-emerald-50/60 border border-emerald-200/60">
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-900 mb-1">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          Expected outcome
                        </div>
                        <p className="text-xs sm:text-[13px] text-emerald-900/90 leading-relaxed">
                          {item.expected_outcome}
                        </p>
                      </div>
                    )}

                    {/* Fallback for legacy items without new fields */}
                    {!hasRichData && (
                      <div className="pt-3">
                        <p className="text-xs sm:text-sm text-gray-600 leading-relaxed">
                          {item.description}
                        </p>
                        {item.skills && item.skills.length > 0 && (
                          <div className="flex flex-wrap gap-1.5 mt-3">
                            {item.skills.map((sk, si) => (
                              <span
                                key={si}
                                className="text-[11px] font-medium text-gray-600 bg-gray-100 px-2 py-0.5 rounded-md"
                              >
                                {sk}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
