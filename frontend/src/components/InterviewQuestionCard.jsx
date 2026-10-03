import React, { useState } from 'react';
import { HelpCircle, ChevronDown, ChevronUp, Lightbulb, Sparkles } from 'lucide-react';

export default function InterviewQuestionCard({ questionsByCategory }) {
  const defaultQuestions = {
    'Resume-Based Questions': [
      {
        question: 'Can you walk through the technical architecture of your recent projects and key design decisions?',
        guidance: 'Be ready to discuss the directory structure, main components, reasons for choosing your stack, and data flow across services.'
      },
      {
        question: 'How have you structured error handling, logging, and data validation across your services?',
        guidance: 'Highlight specific exception handlers, structured logger configurations, and input validation routines you implemented.'
      }
    ],
    'Technical Questions': [
      {
        question: 'How do you approach database schema design, indexing, and query optimization?',
        guidance: 'Explain normalization principles, index selectivity, primary/foreign key relations, and query execution plans.'
      },
      {
        question: 'What strategies do you use when diagnosing performance bottlenecks or unexpected exceptions?',
        guidance: 'Outline log inspection, stack trace isolation, local reproduction, and query profiling methods.'
      }
    ],
    'Project Questions': [
      {
        question: 'In your past projects, what was the most challenging technical obstacle you solved and how did you resolve it?',
        guidance: 'Use the STAR method: describe the obstacle, diagnostic steps taken, trade-offs evaluated, and the final working solution.'
      },
      {
        question: 'How do you ensure proper data consistency and maintainability when building backend applications?',
        guidance: 'Discuss database transactions (ACID), migration workflows, modular code structure, and automated unit tests.'
      }
    ],
    'Job-Specific Questions': [
      {
        question: 'How does your practical development experience align with the technical expectations of this position?',
        guidance: 'Connect your hands-on project work directly to the role requirements while honestly addressing areas you are actively learning.'
      }
    ],
    'Behavioral Questions': [
      {
        question: 'Tell me about a time you had to deliver a feature with an unfamiliar technology stack or tight deadlines.',
        guidance: 'Focus on your rapid learning process, documentation review, prototyping in isolation, and steady delivery.'
      },
      {
        question: 'How do you collaborate with team members when reviewing code and discussing architecture decisions?',
        guidance: 'Emphasize constructive feedback, active listening, readability standards, and shared team outcomes.'
      }
    ]
  };

  const categories = (questionsByCategory && Object.keys(questionsByCategory).length > 0)
    ? questionsByCategory
    : defaultQuestions;
  const categoryKeys = Object.keys(categories);
  const [activeCategory, setActiveCategory] = useState(categoryKeys[0]);
  const [expandedQuestions, setExpandedQuestions] = useState({});

  // Ensure active category is valid if categories prop changes
  const currentCategory = categories[activeCategory] ? activeCategory : categoryKeys[0];
  const questionsList = categories[currentCategory] || [];

  const toggleQuestion = (idx) => {
    setExpandedQuestions((prev) => ({
      ...prev,
      [idx]: !prev[idx]
    }));
  };

  const toggleAll = () => {
    const allExpanded = questionsList.every((_, idx) => expandedQuestions[idx]);
    if (allExpanded) {
      setExpandedQuestions({});
    } else {
      const nextState = {};
      questionsList.forEach((_, idx) => {
        nextState[idx] = true;
      });
      setExpandedQuestions(nextState);
    }
  };

  return (
    <div className="bg-white rounded-3xl border border-gray-200 p-6 sm:p-8 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h4 className="font-display font-semibold text-lg sm:text-xl text-[#0a1b33] flex items-center gap-2">
            <HelpCircle className="w-5 h-5 text-[#0a152d]" />
            Targeted Interview Questions
          </h4>
          <p className="text-xs sm:text-sm text-gray-500 mt-0.5">
            Curated practice questions based directly on your resume, projects, and the job requirements.
          </p>
        </div>

        {questionsList.length > 0 && (
          <button
            onClick={toggleAll}
            className="text-xs font-medium text-[#0a152d] hover:text-blue-700 transition-colors self-start sm:self-auto cursor-pointer"
          >
            {questionsList.every((_, idx) => expandedQuestions[idx]) ? 'Collapse All' : 'Expand All Guidance'}
          </button>
        )}
      </div>

      {/* Category Pills */}
      <div className="flex flex-wrap gap-2 mb-6">
        {Object.keys(categories).map((cat) => (
          <button
            key={cat}
            onClick={() => {
              setActiveCategory(cat);
              setExpandedQuestions({});
            }}
            className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-colors cursor-pointer ${
              currentCategory === cat
                ? 'bg-[#0a152d] text-white shadow-xs'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {cat} ({categories[cat]?.length || 0})
          </button>
        ))}
      </div>

      {/* Questions List for Active Category */}
      <div className="space-y-3.5">
        {questionsList.map((item, idx) => {
          const isString = typeof item === 'string';
          const qText = isString ? item : item?.question;
          const guidanceText = isString ? null : item?.guidance;
          const isExpanded = !!expandedQuestions[idx];

          return (
            <div
              key={idx}
              className={`rounded-2xl border transition-all ${
                isExpanded
                  ? 'bg-white border-blue-200/80 shadow-xs'
                  : 'bg-gray-50/70 border-gray-200/70 hover:border-gray-300'
              }`}
            >
              {/* Question Header */}
              <div
                onClick={() => guidanceText && toggleQuestion(idx)}
                className={`p-4 sm:p-5 flex items-start gap-3.5 ${
                  guidanceText ? 'cursor-pointer select-none' : ''
                }`}
              >
                <span className="w-7 h-7 rounded-xl bg-white border border-gray-200 text-[#0a1b33] flex items-center justify-center text-xs font-semibold shrink-0 mt-0.5 shadow-2xs">
                  Q{idx + 1}
                </span>

                <div className="flex-1 min-w-0">
                  <p className="text-xs sm:text-sm font-medium text-[#0a1b33] leading-relaxed">
                    {qText}
                  </p>

                  {guidanceText && (
                    <div className="mt-2.5 flex items-center gap-1.5">
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-blue-700 bg-blue-50 border border-blue-200/60 px-2 py-0.5 rounded-md">
                        <Lightbulb className="w-3 h-3 text-blue-600" />
                        {isExpanded ? 'Hide preparation guidance' : 'Show preparation guidance'}
                      </span>
                    </div>
                  )}
                </div>

                {guidanceText && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleQuestion(idx);
                    }}
                    className="p-1 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors shrink-0 mt-0.5"
                    aria-label={isExpanded ? 'Collapse' : 'Expand'}
                  >
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-gray-600" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-gray-600" />
                    )}
                  </button>
                )}
              </div>

              {/* Expandable Preparation Guidance */}
              {isExpanded && guidanceText && (
                <div className="px-4 pb-4 sm:px-5 sm:pb-5 pt-0">
                  <div className="p-3.5 sm:p-4 rounded-xl bg-blue-50/50 border border-blue-100/80 text-xs sm:text-sm text-gray-700 leading-relaxed">
                    <div className="flex items-center gap-1.5 font-semibold text-xs text-blue-900 mb-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                      Preparation Guidance
                    </div>
                    <p className="text-gray-600 text-xs sm:text-[13px] leading-relaxed">
                      {guidanceText}
                    </p>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
