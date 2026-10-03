import React from 'react';
import { Check, AlertCircle } from 'lucide-react';

export default function SkillList({
  title,
  subtitle,
  skills = [],
  variant = 'matched', // 'matched' | 'missing'
  emptyMessage = 'No skills identified.',
}) {
  const isMatched = variant === 'matched';

  return (
    <div className="bg-white rounded-3xl border border-gray-200/90 p-5 sm:p-6 shadow-xs">
      <div className="flex items-center justify-between gap-3 mb-2">
        <h4 className="font-display font-semibold text-base sm:text-lg text-[#0a1b33] flex items-center gap-2">
          <span
            className={`w-2.5 h-2.5 rounded-full ${
              isMatched ? 'bg-[#0a152d]' : 'bg-amber-600'
            }`}
          />
          {title}
        </h4>
        <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-gray-100 text-[#0a1b33]">
          {skills.length}
        </span>
      </div>

      {subtitle && (
        <p className="text-xs sm:text-sm text-gray-500 mb-4">
          {subtitle}
        </p>
      )}

      {skills.length === 0 ? (
        <p className="text-xs sm:text-sm text-gray-400 italic py-2">{emptyMessage}</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {skills.map((skill, idx) => {
            const skillLabel = typeof skill === 'object' && skill !== null ? (skill.skill || skill.name || String(skill)) : skill;
            const skillTooltip = typeof skill === 'object' && skill !== null ? skill.evidence : undefined;
            return (
              <span
                key={idx}
                title={skillTooltip}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs sm:text-sm font-medium transition-colors ${
                  isMatched
                    ? 'bg-gray-100 text-[#0a1b33] border border-gray-200/60'
                    : 'bg-amber-50/70 text-amber-900 border border-amber-200/60'
                }`}
              >
                {isMatched ? (
                  <Check className="w-3.5 h-3.5 text-[#0a152d] shrink-0" />
                ) : (
                  <AlertCircle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                )}
                {skillLabel}
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}
