import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Clock, AlertCircle } from 'lucide-react';
import Container from '../components/Container';
import Button from '../components/Button';
import AnalysisCard from '../components/AnalysisCard';
import InterviewQuestionCard from '../components/InterviewQuestionCard';
import Roadmap from '../components/Roadmap';
import { fetchAnalysisDetail } from '../services/api';

export default function AnalysisDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    fetchAnalysisDetail(id)
      .then((data) => {
        if (isMounted) {
          setAnalysis(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.response?.data?.detail || 'Could not load the requested analysis.');
          setLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, [id]);

  if (loading) {
    return (
      <div className="pt-32 pb-16 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 rounded-full border-2 border-[#0a152d] border-t-transparent animate-spin mx-auto mb-3" />
          <p className="text-sm text-gray-500 font-medium">Loading analysis report...</p>
        </div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="pt-32 pb-16 min-h-screen">
        <Container size="default">
          <div className="bg-white rounded-3xl border border-gray-200 p-8 sm:p-12 text-center max-w-lg mx-auto shadow-xs">
            <AlertCircle className="w-10 h-10 text-red-500 mx-auto mb-4" />
            <h2 className="font-display font-bold text-xl text-[#0a1b33]">
              Analysis Not Found
            </h2>
            <p className="text-sm text-gray-500 mt-2 mb-6">
              {error || 'This analysis record does not exist or does not belong to your account.'}
            </p>
            <Button variant="primary" onClick={() => navigate('/dashboard')}>
              Return to Dashboard
            </Button>
          </div>
        </Container>
      </div>
    );
  }

  const status = analysis.result?.analysis_status || analysis.analysis_status || 'complete';
  const isInsufficient = analysis.match_score === null || analysis.match_score === undefined || status === 'insufficient_jd';
  const formattedDate = new Date(analysis.created_at).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });

  return (
    <div className="pt-24 sm:pt-28 pb-16 min-h-screen">
      <Container size="hero">
        {/* Navigation & Breadcrumbs */}
        <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/dashboard')}
              icon={ArrowLeft}
              iconPosition="left"
            >
              Back to Dashboard
            </Button>
            <div className="h-4 w-px bg-gray-200" />
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
              Analysis History Detail
            </span>
          </div>
        </div>

        {/* Dedicated Analysis Header Card */}
        <div className="mb-8 p-6 sm:p-8 rounded-3xl bg-white border border-gray-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2.5">
              <span
                className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${
                  isInsufficient
                    ? 'bg-amber-50 text-amber-700 border border-amber-200/60'
                    : 'bg-emerald-50 text-emerald-700 border border-emerald-200/60'
                }`}
              >
                {isInsufficient ? 'Insufficient JD' : 'Completed'}
              </span>
              <span className="text-xs text-gray-400 flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" />
                {formattedDate}
              </span>
            </div>
            <h1 className="font-display font-bold text-2xl sm:text-3xl text-[#0a1b33]">
              {analysis.job_title}
            </h1>
            <p className="text-xs sm:text-sm text-gray-500">
              Evaluated with: <span className="font-semibold text-gray-700">{analysis.resume_filename || 'Uploaded Resume'}</span>
            </p>
          </div>

          <div className="flex items-center gap-3 bg-gray-50 px-5 py-3 rounded-2xl border border-gray-200/80 shrink-0 self-start md:self-auto">
            <div className="text-right">
              <span className="block text-[11px] font-semibold uppercase tracking-wider text-gray-400">
                Match Score
              </span>
              <span className={`font-display font-extrabold text-3xl sm:text-4xl ${isInsufficient ? 'text-amber-700' : 'text-[#0a152d]'}`}>
                {isInsufficient ? 'N/A' : `${analysis.match_score}%`}
              </span>
            </div>
          </div>
        </div>


        <div className="space-y-8">
          <AnalysisCard analysisData={analysis.result} />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-4">
            <InterviewQuestionCard questionsByCategory={analysis.result?.interview_questions} />
            <Roadmap roadmapItems={analysis.result?.learning_roadmap} />
          </div>
        </div>
      </Container>
    </div>
  );
}
