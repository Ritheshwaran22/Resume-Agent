import React from 'react';
import { CheckCircle2, AlertCircle, Sparkles, FolderGit2, Info, ArrowUpRight } from 'lucide-react';
import SkillList from './SkillList';
import ScoreBreakdownCard from './ScoreBreakdownCard';

export default function AnalysisCard({ analysisData }) {

  if (!analysisData) return null;

  const {
    match_score = null,
    analysis_status = 'complete',
    status_message = null,
    overview = 'Your resume demonstrates strong technical foundations relevant to this role, with several key job requirements that are not clearly demonstrated in your current experience descriptions.',
    matched_skills = ['Python', 'Django', 'REST APIs', 'PostgreSQL', 'Git', 'System Architecture'],
    missing_skills = ['Docker', 'AWS ECS', 'Kubernetes', 'Redis Caching'],
    required_skills_matched = null,
    required_skills_missing = null,
    preferred_skills_matched = [],
    preferred_skills_missing = [],
    skills_demonstrated = [],
    skills_mentioned = [],
    scoring_formula = '',
    keywords_found = ['Python', 'Django', 'REST', 'PostgreSQL', 'CI/CD', 'API Design'],
    keywords_missing = ['Containerization', 'Microservices', 'Distributed Systems'],
    resume_strengths = [
      'Strong hands-on experience building backend services with Python and Django.',
      'Demonstrated relational database architecture and query optimization using PostgreSQL.',
      'Clear project implementations showing end-to-end API lifecycle management.',
    ],
    resume_weaknesses = [
      'Cloud deployment and containerization requirements (Docker, AWS) are not demonstrated.',
      'Project descriptions focus primarily on features rather than measurable performance impacts.',
      'Caching and high-throughput queuing technologies mentioned in the job post are absent.',
    ],
    project_analysis = [
      {
        project: 'E-Commerce REST API & Inventory Service',
        technologies: ['Python', 'Django', 'DRF', 'PostgreSQL'],
        relevance: 'High — directly mirrors the backend framework and data persistence stack in the job description.',
        strong: 'Good schema structuring and comprehensive authentication setup with JWT.',
        improvements: 'The resume describes the project functionality but does not provide a measurable performance result.',
      },
      {
        project: 'Real-Time Notification Worker',
        technologies: ['Python', 'WebSockets', 'Celery'],
        relevance: 'Medium — demonstrates background processing, but job description specifically asks for Redis caching.',
        strong: 'Shows asynchronous workflow handling.',
        improvements: 'The resume describes the project functionality but does not provide a measurable performance result.',
      },
    ],
    resume_suggestions = [
      'Docker is mentioned in the job description but is not clearly demonstrated in your resume. If you have genuinely used Docker or containerized services, consider adding it to your projects or skills section.',
      'AWS deployment is listed as a primary requirement. If you have configured cloud instances or CI/CD pipelines targeting AWS, highlight that concrete exposure.',
      'Quantify results where possible: rather than stating "optimized queries", state the approximate latency reduction or database table size handled.',
    ],
  } = analysisData;

  const isInsufficientJd = match_score === null || match_score === undefined || analysis_status === 'insufficient_jd';
  const hasPreferredSkills = (preferred_skills_matched && preferred_skills_matched.length > 0) || (preferred_skills_missing && preferred_skills_missing.length > 0);

  const displayRequiredMatched = required_skills_matched || matched_skills;
  const displayRequiredMissing = required_skills_missing || missing_skills;

  return (
    <div className="space-y-6">
      {/* Overview & Match Indicator Hero Card */}
      <div className="bg-white rounded-3xl border border-gray-200 p-6 sm:p-8 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-gray-100">
          <div className="max-w-xl">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
              Resume Analysis
            </span>
            <h3 className="font-display font-bold text-2xl sm:text-3xl text-[#0a1b33] mt-1">
              Alignment Summary
            </h3>
            <p className="text-sm sm:text-base text-gray-600 mt-2 leading-relaxed">
              {overview}
            </p>
          </div>

          {/* Match Score Indicator */}
          <div className="flex flex-col items-start md:items-end justify-center shrink-0">
            <div className="flex items-baseline gap-1">
              <span className={`font-display font-extrabold ${isInsufficientJd ? 'text-4xl sm:text-5xl text-amber-700' : 'text-5xl sm:text-6xl text-[#0a152d]'}`}>
                {isInsufficientJd ? 'N/A' : `${match_score}%`}
              </span>
            </div>
            <span className={`text-xs font-semibold mt-1 ${isInsufficientJd ? 'text-amber-800' : 'text-gray-500'}`}>
              {isInsufficientJd ? 'Insufficient JD Details' : 'Resume-to-job match indicator'}
            </span>
            <span className="text-[11px] text-gray-400 mt-0.5">
              {isInsufficientJd ? 'Cannot evaluate match without specific JD requirements' : 'Comparison indicator • Not a hiring probability'}
            </span>
          </div>
        </div>

        {/* Status message or disclaimer banner */}
        {status_message && (
          <div className="mt-4 flex items-center gap-2 p-3 bg-amber-50/80 rounded-2xl text-xs text-amber-900 border border-amber-200/80">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
            <span>{status_message}</span>
          </div>
        )}

        <div className="mt-4 flex items-center gap-2 p-3 bg-gray-50 rounded-2xl text-xs text-gray-500 border border-gray-100">
          <Info className="w-4 h-4 text-gray-400 shrink-0" />
          <span>
            This match indicator evaluates demonstrated skills against stated requirements. It does not predict recruiter decisions or guarantee ATS screening outcomes.
          </span>
        </div>
      </div>

      {/* Transparent Score Breakdown (Why this score?) */}
      <ScoreBreakdownCard analysisData={analysisData} />

      {/* Required Skills Grid */}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <SkillList
          title={hasPreferredSkills ? "Required Skills Matched" : "Matched Skills"}
          subtitle={hasPreferredSkills ? "Required skills present in your resume" : "Skills present in both your resume and the target job description"}
          skills={displayRequiredMatched}
          variant="matched"
          emptyMessage={isInsufficientJd ? "No target requirements to match against (insufficient JD details)." : "No matching skills identified."}
        />
        <SkillList
          title={hasPreferredSkills ? "Required Skills Missing" : "Missing Demonstrated Skills"}
          subtitle={hasPreferredSkills ? "Core job requirements not demonstrated in your resume" : "Job requirements that are not clearly demonstrated in your resume"}
          skills={displayRequiredMissing}
          variant="missing"
          emptyMessage={isInsufficientJd ? "No missing skills identified (insufficient JD details)." : "All required skills demonstrated."}
        />
      </div>

      {/* Preferred Skills Grid (Separated from Required) */}
      {hasPreferredSkills && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <SkillList
            title="Preferred Skills Matched"
            subtitle="Optional / preferred skills confirmed in your resume"
            skills={preferred_skills_matched}
            variant="matched"
            emptyMessage="No preferred skills matched."
          />
          <SkillList
            title="Preferred Skills Missing"
            subtitle="Preferred skills not found (does not reduce required match score)"
            skills={preferred_skills_missing}
            variant="missing"
            emptyMessage="All preferred skills matched."
          />
        </div>
      )}

      {/* Keywords Analysis */}
      <div className="bg-white rounded-3xl border border-gray-200 p-6 sm:p-8 shadow-xs">
        <div className="mb-4">
          <h4 className="font-display font-semibold text-lg sm:text-xl text-[#0a1b33]">
            Keyword Analysis
          </h4>
          <p className="text-xs sm:text-sm text-gray-500 mt-0.5">
            Key domain terms identified in the job description and their presence in your document.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-4 rounded-2xl bg-gray-50/70 border border-gray-100">
            <h5 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2.5">
              Keywords Found in Resume ({keywords_found.length})
            </h5>
            <div className="flex flex-wrap gap-1.5">
              {keywords_found.length === 0 ? (
                <span className="text-xs text-gray-400 italic">None identified</span>
              ) : (
                keywords_found.map((kw, i) => (
                  <span
                    key={i}
                    className="px-2.5 py-1 bg-white text-xs text-[#0a1b33] rounded-full border border-gray-200/80 font-medium"
                  >
                    {kw}
                  </span>
                ))
              )}
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-gray-50/70 border border-gray-100">
            <h5 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2.5">
              Keywords Missing / Undemonstrated ({keywords_missing.length})
            </h5>
            <div className="flex flex-wrap gap-1.5">
              {keywords_missing.length === 0 ? (
                <span className="text-xs text-gray-400 italic">None identified</span>
              ) : (
                keywords_missing.map((kw, i) => (
                  <span
                    key={i}
                    className="px-2.5 py-1 bg-white text-xs text-amber-900 rounded-full border border-amber-200/60 font-medium"
                  >
                    {kw}
                  </span>
                ))
              )}
            </div>
          </div>
        </div>

        <p className="text-[11px] text-gray-400 mt-3">
          Note: Keyword matching is purely informational. Adding keywords without genuine experience is discouraged.
        </p>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-3xl border border-gray-200 p-6 sm:p-8 shadow-xs">
          <h4 className="font-display font-semibold text-lg text-[#0a1b33] mb-3 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-[#0a152d]" />
            Resume Strengths
          </h4>
          <ul className="space-y-3 text-sm text-gray-600">
            {resume_strengths.map((str, idx) => (
              <li key={idx} className="flex items-start gap-2.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#0a152d] shrink-0 mt-2" />
                <span className="leading-relaxed">{str}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white rounded-3xl border border-gray-200 p-6 sm:p-8 shadow-xs">
          <h4 className="font-display font-semibold text-lg text-[#0a1b33] mb-3 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-amber-600" />
            Areas for Improvement
          </h4>
          <ul className="space-y-3 text-sm text-gray-600">
            {resume_weaknesses.map((weak, idx) => (
              <li key={idx} className="flex items-start gap-2.5">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-600 shrink-0 mt-2" />
                <span className="leading-relaxed">{weak}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Project Analysis */}
      <div className="bg-white rounded-3xl border border-gray-200 p-6 sm:p-8 shadow-xs">
        <div className="mb-6">
          <h4 className="font-display font-semibold text-lg sm:text-xl text-[#0a1b33] flex items-center gap-2">
            <FolderGit2 className="w-5 h-5 text-[#0a152d]" />
            Project Breakdown
          </h4>
          <p className="text-xs sm:text-sm text-gray-500 mt-0.5">
            Factual evaluation of projects identified in the candidate resume.
          </p>
        </div>

        <div className="space-y-4">
          {project_analysis.map((item, idx) => (
            <div
              key={idx}
              className="p-5 rounded-2xl bg-gray-50/60 border border-gray-200/80 space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <h5 className="font-semibold text-base text-[#0a1b33]">
                  {item.project}
                </h5>
                <div className="flex flex-wrap gap-1.5">
                  {(item.technologies || []).map((t, ti) => (
                    <span
                      key={ti}
                      className="px-2 py-0.5 bg-white border border-gray-200 rounded-md text-[11px] font-medium text-gray-700"
                    >
                      {typeof t === 'object' && t !== null ? t.name || String(t) : t}
                    </span>
                  ))}
                </div>
              </div>

              <div className="text-xs sm:text-sm text-gray-600 space-y-1.5">
                <p>
                  <strong className="text-[#0a1b33]">Job Relevance:</strong> {item.relevance}
                </p>
                <p>
                  <strong className="text-[#0a1b33]">What is strong:</strong> {item.strong}
                </p>
                <p>
                  <strong className="text-[#0a1b33]">What could be improved:</strong>{' '}
                  <span className="text-gray-700">{item.improvements}</span>
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Truthful Resume Improvement Suggestions */}
      <div className="bg-white rounded-3xl border border-gray-200 p-6 sm:p-8 shadow-xs">
        <h4 className="font-display font-semibold text-lg sm:text-xl text-[#0a1b33] mb-2 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-[#0a152d]" />
          Truthful Resume Improvement Suggestions
        </h4>
        <p className="text-xs sm:text-sm text-gray-500 mb-5">
          Actionable recommendations based on what is missing. Never fabricate claims or experience.
        </p>

        <div className="space-y-3">
          {resume_suggestions.map((suggestion, idx) => (
            <div
              key={idx}
              className="p-4 rounded-2xl bg-gray-50/60 border border-gray-200/80 flex items-start gap-3"
            >
              <span className="w-6 h-6 rounded-full bg-[#0a152d] text-white flex items-center justify-center text-xs font-semibold shrink-0 mt-0.5">
                {idx + 1}
              </span>
              <p className="text-xs sm:text-sm text-[#0a1b33] leading-relaxed">
                {suggestion}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
