import React from 'react';
import { Check, X, Info, Calculator, ShieldCheck } from 'lucide-react';

export default function ScoreBreakdownCard({ analysisData }) {
  if (!analysisData) return null;

  const {
    match_score = null,
    analysis_status = 'complete',
    scoring_formula = '',
    required_skills_total = 0,
    required_skills_matched = [],
    required_skills_missing = [],
    preferred_skills_total = 0,
    preferred_skills_matched = [],
    preferred_skills_missing = [],
    skills_breakdown = [],
    skills_demonstrated = [],
    skills_mentioned = [],
  } = analysisData;

  const isInsufficientJd = match_score === null || match_score === undefined || analysis_status === 'insufficient_jd';

  const reqMatchedCount = required_skills_matched.length;
  const reqTotalCount = required_skills_total || (required_skills_matched.length + required_skills_missing.length);
  const prefMatchedCount = preferred_skills_matched.length;
  const prefTotalCount = preferred_skills_total || (preferred_skills_matched.length + preferred_skills_missing.length);
  const hasPreferred = prefTotalCount > 0;

  // Helper to retrieve backend-provided evidence status for any skill
  const getSkillStatus = (skillName) => {
    const sLower = String(skillName).trim().toLowerCase();
    const foundInBreakdown = (skills_breakdown || []).find(
      (b) => b.skill && b.skill.trim().toLowerCase() === sLower
    );

    if (foundInBreakdown) {
      return {
        status: foundInBreakdown.status, // 'matched' | 'missing'
        mentioned: foundInBreakdown.mentioned,
        demonstrated: foundInBreakdown.demonstrated, // 'Yes' | 'Unclear' | 'No'
        evidence: foundInBreakdown.evidence || '',
      };
    }

    // Fallback using backend arrays
    const isMatched =
      required_skills_matched.some((s) => s.toLowerCase() === sLower) ||
      preferred_skills_matched.some((s) => s.toLowerCase() === sLower);
    const isDemo = skills_demonstrated.some((s) => s.toLowerCase() === sLower);
    const isMent = skills_mentioned.some((s) => s.toLowerCase() === sLower);

    return {
      status: isMatched ? 'matched' : 'missing',
      mentioned: isMent || isMatched,
      demonstrated: isDemo ? 'Yes' : (isMatched ? 'Unclear' : 'No'),
      evidence: '',
    };
  };

  return (
    <div className="bg-white rounded-3xl border border-gray-200 p-6 sm:p-8 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-gray-100">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
            Transparent Evaluation
          </span>
          <h3 className="font-display font-bold text-2xl text-[#0a1b33] mt-0.5 flex items-center gap-2">
            Why this score?
          </h3>
          <p className="text-xs sm:text-sm text-gray-500 mt-1">
            Auditable, deterministic calculation based directly on verified required skills.
          </p>
        </div>

        <div className="flex items-center gap-3 bg-gray-50 px-4 py-2.5 rounded-2xl border border-gray-200/80 shrink-0 self-start sm:self-auto">
          <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
            Score:
          </span>
          <span className={`font-display font-extrabold text-2xl sm:text-3xl ${isInsufficientJd ? 'text-amber-700' : 'text-[#0a152d]'}`}>
            {isInsufficientJd ? 'N/A' : `${match_score}%`}
          </span>
        </div>
      </div>

      {isInsufficientJd ? (
        <div className="py-6 text-center text-sm text-gray-500">
          <p className="font-medium text-amber-900">
            No score could be evaluated because the job description lacks specific skill requirements.
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Provide a complete job description with explicit technical requirements to generate a score.
          </p>
        </div>
      ) : (
        <div className="mt-6 space-y-6">
          {/* Required Skills Section */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-semibold text-[#0a1b33] flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#0a152d]" />
                Required Skills
              </h4>
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-gray-100 text-[#0a1b33]">
                {reqMatchedCount} of {reqTotalCount} matched
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {/* Matched Required Skills */}
              {required_skills_matched.map((skill, idx) => {
                const info = getSkillStatus(skill);
                const isDemo = info.demonstrated === 'Yes';
                return (
                  <div
                    key={`req-m-${idx}`}
                    className="flex items-center justify-between p-3 rounded-2xl bg-gray-50/80 border border-gray-200/70 text-xs sm:text-sm"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center shrink-0">
                        <Check className="w-3.5 h-3.5 stroke-[2.5]" />
                      </span>
                      <span className="font-medium text-[#0a1b33] truncate">
                        {skill}
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5 shrink-0">
                      <span className="px-2 py-0.5 rounded-md text-[10px] sm:text-[11px] font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200/60">
                        Matched
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded-md text-[10px] sm:text-[11px] font-medium border ${
                          isDemo
                            ? 'bg-blue-50 text-blue-800 border-blue-200/60'
                            : 'bg-gray-100 text-gray-700 border-gray-200'
                        }`}
                        title={info.evidence || undefined}
                      >
                        {isDemo ? 'Demonstrated' : 'Mentioned in Resume'}
                      </span>
                    </div>
                  </div>
                );
              })}

              {/* Missing Required Skills */}
              {required_skills_missing.map((skill, idx) => {
                const info = getSkillStatus(skill);
                return (
                  <div
                    key={`req-miss-${idx}`}
                    className="flex items-center justify-between p-3 rounded-2xl bg-amber-50/40 border border-amber-200/60 text-xs sm:text-sm"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <span className="w-5 h-5 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center shrink-0">
                        <X className="w-3.5 h-3.5 stroke-[2.5]" />
                      </span>
                      <span className="font-medium text-amber-950 truncate">
                        {skill}
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5 shrink-0">
                      <span className="px-2 py-0.5 rounded-md text-[10px] sm:text-[11px] font-semibold bg-amber-100/70 text-amber-900 border border-amber-200/70">
                        Missing
                      </span>
                      <span className="px-2 py-0.5 rounded-md text-[10px] sm:text-[11px] font-medium bg-gray-100 text-gray-600 border border-gray-200">
                        Not Found
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Formula Display Box */}
          <div className="p-4 rounded-2xl bg-gray-50 border border-gray-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs sm:text-sm">
            <div className="flex items-center gap-2 text-gray-600">
              <Calculator className="w-4 h-4 text-[#0a152d] shrink-0" />
              <span className="font-semibold text-[#0a1b33]">Deterministic Formula:</span>
              <span className="font-mono bg-white px-2 py-0.5 rounded-md border border-gray-200 text-[#0a152d]">
                {reqMatchedCount} / {reqTotalCount} × 100 = {match_score}%
              </span>
            </div>
            <span className="text-[11px] text-gray-400">
              Zero arbitrary boosts or score floors applied.
            </span>
          </div>

          {/* Preferred Skills Section */}
          {hasPreferred && (
            <div className="pt-4 border-t border-gray-100">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-semibold text-[#0a1b33] flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-gray-400" />
                  Preferred Skills
                </h4>
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-gray-100 text-gray-700">
                  {prefMatchedCount} of {prefTotalCount} matched
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {preferred_skills_matched.map((skill, idx) => (
                  <div
                    key={`pref-m-${idx}`}
                    className="flex items-center justify-between p-3 rounded-2xl bg-gray-50/80 border border-gray-200/70 text-xs sm:text-sm"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center shrink-0">
                        <Check className="w-3.5 h-3.5 stroke-[2.5]" />
                      </span>
                      <span className="font-medium text-[#0a1b33] truncate">
                        {skill}
                      </span>
                    </div>
                    <span className="px-2 py-0.5 rounded-md text-[10px] sm:text-[11px] font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200/60">
                      Matched (Bonus)
                    </span>
                  </div>
                ))}

                {preferred_skills_missing.map((skill, idx) => (
                  <div
                    key={`pref-miss-${idx}`}
                    className="flex items-center justify-between p-3 rounded-2xl bg-gray-50/50 border border-gray-200/50 text-xs sm:text-sm"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <span className="w-5 h-5 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center shrink-0">
                        <X className="w-3.5 h-3.5 stroke-[2.5]" />
                      </span>
                      <span className="font-medium text-gray-600 truncate">
                        {skill}
                      </span>
                    </div>
                    <span className="px-2 py-0.5 rounded-md text-[10px] sm:text-[11px] font-medium bg-gray-100 text-gray-500 border border-gray-200">
                      Missing (Optional)
                    </span>
                  </div>
                ))}
              </div>

              <div className="mt-3 flex items-center gap-2 p-3 bg-blue-50/60 rounded-2xl text-xs text-blue-900 border border-blue-100">
                <Info className="w-4 h-4 text-blue-700 shrink-0" />
                <span>
                  Preferred skills are shown separately and do not reduce the required-skill match score.
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
