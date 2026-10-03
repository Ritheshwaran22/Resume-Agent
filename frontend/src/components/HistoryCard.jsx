import React from 'react';
import { Clock, ArrowRight, CheckCircle2, AlertCircle, FileText } from 'lucide-react';
import Button from './Button';

export default function HistoryCard({
  item,
  onOpen,
  className = '',
}) {
  const {
    id = 1,
    job_title = 'Senior Backend Engineer',
    resume_filename,
    resume_name = 'Software_Engineer_Resume.pdf',
    match_score = null,
    created_at = '',
    analysis_status = 'complete',
    required_skills_matched_count = 0,
    required_skills_total_count = 0,
    required_skills_missing_count = 0,
    result = {},
  } = item || {};

  const displayFilename = resume_filename || resume_name;

  // Derive counts from result if not directly on item
  const matchedCount =
    required_skills_matched_count ||
    (result?.required_skills_matched ? result.required_skills_matched.length : 0);
  const totalCount =
    required_skills_total_count ||
    result?.required_skills_total ||
    (matchedCount + (result?.required_skills_missing ? result.required_skills_missing.length : 0));
  const missingCount =
    required_skills_missing_count ||
    (result?.required_skills_missing ? result.required_skills_missing.length : 0);

  const status = analysis_status || result?.analysis_status || 'complete';
  const isInsufficient = match_score === null || match_score === undefined || status === 'insufficient_jd';

  // Format date nicely
  let formattedDate = created_at;
  if (created_at && !isNaN(Date.parse(created_at))) {
    const d = new Date(created_at);
    formattedDate = d.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  }

  return (
    <div
      onClick={onOpen}
      className={`p-5 rounded-3xl bg-white border border-gray-200 hover:border-gray-300 shadow-xs hover:shadow-sm transition-all cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${className}`}
    >
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2 mb-1.5">
          <span className="font-semibold text-base text-[#0a1b33] truncate max-w-sm">
            {job_title}
          </span>
          <span
            className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${
              isInsufficient
                ? 'bg-amber-100/70 text-amber-900 border border-amber-200/60'
                : 'bg-gray-100 text-[#0a152d] border border-gray-200/60'
            }`}
          >
            {isInsufficient ? 'N/A' : `${match_score}% Match`}
          </span>
          <span
            className={`text-[11px] font-medium px-2 py-0.5 rounded-full ${
              isInsufficient
                ? 'bg-amber-50 text-amber-700'
                : 'bg-emerald-50 text-emerald-700'
            }`}
          >
            {isInsufficient ? 'Insufficient JD' : 'Completed'}
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-gray-500">
          <span className="flex items-center gap-1.5 truncate max-w-[220px] font-medium text-gray-700">
            <FileText className="w-3.5 h-3.5 text-gray-400 shrink-0" />
            <span className="truncate">{displayFilename}</span>
          </span>
          <span>•</span>
          <span className="font-medium text-[#0a1b33]">
            {isInsufficient
              ? 'Requirements Undefined'
              : `${matchedCount} / ${totalCount} required skills`}
            {!isInsufficient && missingCount > 0 && (
              <span className="text-gray-400 font-normal"> ({missingCount} missing)</span>
            )}
          </span>
          <span>•</span>
          <span className="flex items-center gap-1 text-gray-400">
            <Clock className="w-3 h-3" />
            {formattedDate}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0 self-end sm:self-center">
        <Button variant="secondary" size="sm" icon={ArrowRight} iconPosition="right">
          View Details
        </Button>
      </div>
    </div>
  );
}

