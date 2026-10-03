import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'motion/react';
import {
  FileText,
  Briefcase,
  Play,
  RotateCcw,
  Clock,
  User,
  CheckCircle2,
  AlertCircle,
  Activity,
  ArrowLeft,
  Sparkles,
  Trash2,
  Upload,
  Plus,
  ArrowRight,
  ExternalLink,
} from 'lucide-react';
import Container from '../components/Container';
import Button from '../components/Button';
import UploadBox from '../components/UploadBox';
import JobForm from '../components/JobForm';
import AnalysisCard from '../components/AnalysisCard';
import InterviewQuestionCard from '../components/InterviewQuestionCard';
import Roadmap from '../components/Roadmap';
import HistoryCard from '../components/HistoryCard';
import ProgressIndicator from '../components/ProgressIndicator';
import { useAuth } from '../context/AuthContext';
import {
  checkHealth,
  fetchResumes,
  uploadResume,
  deleteResume,
  startAnalysis,
  fetchAnalyses,
} from '../services/api';

export default function DashboardShell({ onBackToHome, initialTab = 'new-analysis' }) {
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleBack = () => {
    if (onBackToHome) {
      onBackToHome();
    } else {
      navigate('/');
    }
  };

  const [activeTab, setActiveTab] = useState(initialTab); // 'new-analysis' | 'results' | 'history' | 'resumes'

  useEffect(() => {
    if (initialTab) {
      setActiveTab(initialTab);
    }
  }, [initialTab]);

  const [healthStatus, setHealthStatus] = useState({ loading: true, healthy: false, data: null });
  const [resumes, setResumes] = useState([]);
  const [selectedResumeId, setSelectedResumeId] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileError, setFileError] = useState(null);
  const [uploadingResume, setUploadingResume] = useState(false);

  // Resume deletion confirmation dialog state
  const [resumeToDelete, setResumeToDelete] = useState(null);
  const [isDeletingResume, setIsDeletingResume] = useState(false);

  const [jobTitle, setJobTitle] = useState('Senior Backend Engineer (Python / Django)');
  const [jobDescription, setJobDescription] = useState(
    'We are looking for a Senior Backend Engineer with strong Python and Django REST framework experience. Must have demonstrated expertise with PostgreSQL, Docker containerization, AWS cloud deployments, and CI/CD automation. Exposure to Redis caching and microservices architecture is a plus.'
  );

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState(0);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [currentAnalysisId, setCurrentAnalysisId] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);

  const [historyList, setHistoryList] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Load health and existing user data
  useEffect(() => {
    let isMounted = true;

    checkHealth()
      .then((data) => {
        if (isMounted) setHealthStatus({ loading: false, healthy: true, data });
      })
      .catch((err) => {
        if (isMounted) setHealthStatus({ loading: false, healthy: false, error: err.message });
      });

    loadUserResumes();
    loadUserAnalyses();

    return () => {
      isMounted = false;
    };
  }, []);

  const loadUserResumes = async () => {
    try {
      const data = await fetchResumes();
      setResumes(data);
      if (data.length > 0 && !selectedResumeId) {
        setSelectedResumeId(data[0].id);
        setSelectedFile({ name: data[0].filename, size: 0, isExisting: true });
      }
    } catch (err) {
      console.error('Failed to load user resumes:', err);
    }
  };

  const loadUserAnalyses = async () => {
    setLoadingHistory(true);
    try {
      const data = await fetchAnalyses();
      setHistoryList(data);
    } catch (err) {
      console.error('Failed to load user analyses:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleFileSelect = async (file, err) => {
    setFileError(err);
    if (!file || err) {
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
    setUploadingResume(true);
    setFileError(null);

    try {
      const savedResume = await uploadResume(file);
      setSelectedResumeId(savedResume.id);
      await loadUserResumes();
    } catch (uploadErr) {
      const msg =
        uploadErr.response?.data?.detail ||
        uploadErr.response?.data?.file?.[0] ||
        uploadErr.response?.data?.[0] ||
        'Failed to process and extract text from the PDF.';
      setFileError(msg);
      setSelectedFile(null);
      setSelectedResumeId(null);
    } finally {
      setUploadingResume(false);
    }
  };

  const handleFileRemove = () => {
    setSelectedFile(null);
    setSelectedResumeId(null);
    setFileError(null);
  };

  // Open confirmation modal
  const promptDeleteResume = (resume, e) => {
    if (e) e.stopPropagation();
    setResumeToDelete(resume);
  };

  // Perform confirmed deletion
  const confirmDeleteResume = async () => {
    if (!resumeToDelete) return;
    setIsDeletingResume(true);
    try {
      await deleteResume(resumeToDelete.id);
      if (selectedResumeId === resumeToDelete.id) {
        setSelectedResumeId(null);
        setSelectedFile(null);
      }
      await loadUserResumes();
      await loadUserAnalyses();
      setResumeToDelete(null);
    } catch (err) {
      console.error('Failed to delete resume:', err);
    } finally {
      setIsDeletingResume(false);
    }
  };

  const handleStartAnalysis = async () => {
    if (!selectedResumeId) {
      setFileError('Please select or upload a resume PDF first.');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisStep(0);
    setAnalysisError(null);

    // Visual step progression
    const progressTimer = setInterval(() => {
      setAnalysisStep((prev) => (prev < 3 ? prev + 1 : prev));
    }, 650);

    try {
      const payload = {
        resume_id: selectedResumeId,
        job_title: jobTitle.trim(),
        job_description: jobDescription.trim(),
      };

      const res = await startAnalysis(payload);
      clearInterval(progressTimer);
      setAnalysisStep(3);

      setTimeout(() => {
        setIsAnalyzing(false);
        setAnalysisResult(res.result);
        setCurrentAnalysisId(res.id);
        setActiveTab('results');
        loadUserAnalyses();
        loadUserResumes();
      }, 400);
    } catch (err) {
      clearInterval(progressTimer);
      setIsAnalyzing(false);
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.non_field_errors?.[0] ||
        'Analysis could not be completed. Please try again in a moment. Your resume and job description were not modified.';
      setAnalysisError(msg);
    }
  };

  const handleOpenHistoricalAnalysis = (item) => {
    setAnalysisResult(item.result);
    setCurrentAnalysisId(item.id);
    setActiveTab('results');
  };

  const selectedResume = resumes.find((r) => r.id === selectedResumeId);

  return (
    <div className="pt-24 sm:pt-28 pb-16 min-h-screen">
      <Container size="hero">
        {/* Top Control Bar */}
        <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={handleBack}
              icon={ArrowLeft}
              iconPosition="left"
            >
              Back to Home
            </Button>
            <div className="h-4 w-px bg-gray-200" />
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
              Application Dashboard
            </span>
          </div>

          {/* Backend API Health Status Indicator */}
          <div className="flex items-center gap-2 self-start sm:self-center">
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white border border-gray-200 text-xs shadow-2xs">
              <span
                className={`w-2 h-2 rounded-full ${
                  healthStatus.healthy ? 'bg-emerald-500' : 'bg-amber-500'
                }`}
              />
              <span className="font-medium text-gray-700">
                API: {healthStatus.healthy ? 'Online' : 'Connecting...'}
              </span>
            </div>
            {user && (
              <span className="text-xs font-semibold text-gray-500 hidden sm:inline">
                User: {user.username}
              </span>
            )}
          </div>
        </div>

        {/* Dashboard Main White Shell */}
        <div className="bg-white rounded-3xl sm:rounded-[2.5rem] border border-gray-200/90 shadow-[0_4px_30px_-6px_rgba(10,27,51,0.03)] p-6 sm:p-10 md:p-12">
          {/* Header Banner */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-8 border-b border-gray-100">
            <div>
              <h1 className="font-display font-bold text-3xl sm:text-4xl text-[#0a1b33]">
                Welcome{user?.username ? `, ${user.username}` : ''}.
              </h1>
              <p className="text-sm sm:text-base text-gray-600 mt-1">
                Analyze your resume against a real job description.
              </p>
            </div>

            {/* Dashboard Navigation Tabs */}
            <div className="flex flex-wrap items-center gap-1.5 bg-gray-100/80 p-1.5 rounded-full w-fit">
              <button
                onClick={() => setActiveTab('new-analysis')}
                className={`px-4 py-2 rounded-full text-xs sm:text-sm font-medium transition-all cursor-pointer ${
                  activeTab === 'new-analysis'
                    ? 'bg-white text-[#0a1b33] shadow-xs font-semibold'
                    : 'text-gray-600 hover:text-[#0a1b33]'
                }`}
              >
                New Analysis
              </button>
              {analysisResult && (
                <button
                  onClick={() => setActiveTab('results')}
                  className={`px-4 py-2 rounded-full text-xs sm:text-sm font-medium transition-all cursor-pointer ${
                    activeTab === 'results'
                      ? 'bg-white text-[#0a1b33] shadow-xs font-semibold'
                      : 'text-gray-600 hover:text-[#0a1b33]'
                  }`}
                >
                  Current Result ({analysisResult.match_score != null ? `${analysisResult.match_score}%` : 'N/A'})
                </button>
              )}
              <button
                onClick={() => setActiveTab('history')}
                className={`px-4 py-2 rounded-full text-xs sm:text-sm font-medium transition-all cursor-pointer ${
                  activeTab === 'history'
                    ? 'bg-white text-[#0a1b33] shadow-xs font-semibold'
                    : 'text-gray-600 hover:text-[#0a1b33]'
                }`}
              >
                Recent Analyses ({historyList.length})
              </button>
              <button
                onClick={() => setActiveTab('resumes')}
                className={`px-4 py-2 rounded-full text-xs sm:text-sm font-medium transition-all cursor-pointer ${
                  activeTab === 'resumes'
                    ? 'bg-white text-[#0a1b33] shadow-xs font-semibold'
                    : 'text-gray-600 hover:text-[#0a1b33]'
                }`}
              >
                My Resumes ({resumes.length})
              </button>
            </div>
          </div>

          {analysisError && (
            <div className="mt-6 p-4 rounded-2xl bg-red-50 border border-red-100 flex items-start gap-2.5 text-xs text-red-700">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
              <span>{analysisError}</span>
            </div>
          )}

          {/* Main Content Area */}
          <div className="mt-8">
            {isAnalyzing ? (
              <div className="py-12">
                <ProgressIndicator currentStep={analysisStep} />
              </div>
            ) : activeTab === 'new-analysis' ? (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                {/* Left Column: Step 1 Select Resume */}
                <div className="lg:col-span-5 space-y-6">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-display font-semibold text-lg text-[#0a1b33] flex items-center gap-2">
                        <span className="w-6 h-6 rounded-full bg-[#0a152d] text-white flex items-center justify-center text-xs font-bold shrink-0">
                          1
                        </span>
                        Select Resume
                      </h3>
                      <button
                        type="button"
                        onClick={() => setActiveTab('resumes')}
                        className="text-xs font-medium text-gray-500 hover:text-[#0a152d]"
                      >
                        Manage Resumes ({resumes.length})
                      </button>
                    </div>
                    <p className="text-xs text-gray-500 mb-4">
                      Upload or select a previously uploaded resume PDF.
                    </p>

                    <UploadBox
                      file={selectedFile}
                      onFileSelect={handleFileSelect}
                      onFileRemove={handleFileRemove}
                      error={fileError}
                      disabled={uploadingResume}
                    />

                    {uploadingResume && (
                      <p className="mt-2 text-xs text-blue-600 font-medium animate-pulse">
                        Uploading and parsing PDF with PyMuPDF...
                      </p>
                    )}

                    {/* Previously Uploaded Resumes List */}
                    {resumes.length > 0 && (
                      <div className="mt-6 pt-6 border-t border-gray-100">
                        <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2.5">
                          Saved Resumes in Your Account
                        </h4>
                        <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                          {resumes.map((r) => {
                            const isSelected = selectedResumeId === r.id;
                            return (
                              <div
                                key={r.id}
                                onClick={() => {
                                  setSelectedResumeId(r.id);
                                  setSelectedFile({ name: r.filename, size: 0, isExisting: true });
                                  setFileError(null);
                                }}
                                className={`p-3 rounded-2xl border transition-all cursor-pointer flex items-center justify-between gap-3 ${
                                  isSelected
                                    ? 'bg-gray-50 border-[#0a152d] ring-1 ring-[#0a152d]'
                                    : 'bg-white border-gray-200 hover:border-gray-300'
                                }`}
                              >
                                <div className="flex items-center gap-2.5 min-w-0">
                                  <FileText className="w-4 h-4 text-[#0a152d] shrink-0" />
                                  <div className="min-w-0">
                                    <span className="text-xs font-medium text-[#0a1b33] truncate block">
                                      {r.filename}
                                    </span>
                                    <span className="text-[10px] text-gray-400">
                                      {r.file_size} • {r.analysis_count || 0} analyses
                                    </span>
                                  </div>
                                </div>
                                <div className="flex items-center gap-2 shrink-0">
                                  {isSelected && (
                                    <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
                                      Active
                                    </span>
                                  )}
                                  <button
                                    type="button"
                                    onClick={(e) => promptDeleteResume(r, e)}
                                    className="p-1 text-gray-400 hover:text-red-500 rounded-md hover:bg-gray-100"
                                    title="Delete resume"
                                  >
                                    <Trash2 className="w-3.5 h-3.5" />
                                  </button>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Privacy Guarantee */}
                  <div className="p-4 rounded-2xl bg-gray-50/60 border border-gray-100 text-xs text-gray-500">
                    <p className="font-semibold text-gray-700 mb-1">Strict User Isolation</p>
                    Your resumes and analysis records are tied strictly to your authenticated account and are never shared across users.
                  </div>
                </div>

                {/* Right Column: Step 2, 3, 4 Target Job Form & Pre-submission Summary */}
                <div className="lg:col-span-7 bg-gray-50/50 p-6 sm:p-8 rounded-3xl border border-gray-200/80 space-y-6">
                  <div>
                    <h3 className="font-display font-semibold text-lg text-[#0a1b33] flex items-center gap-2 mb-1">
                      <span className="w-6 h-6 rounded-full bg-[#0a152d] text-white flex items-center justify-center text-xs font-bold shrink-0">
                        2 & 3
                      </span>
                      Job Information
                    </h3>
                    <p className="text-xs text-gray-500">
                      Enter the target role and paste unedited job requirements.
                    </p>
                  </div>

                  {/* Form fields */}
                  <div className="space-y-4">
                    <div>
                      <label
                        htmlFor="job-title-input"
                        className="block text-xs font-semibold text-[#0a1b33] uppercase tracking-wider mb-2"
                      >
                        Step 2: Enter Job Title
                      </label>
                      <div className="relative rounded-2xl border border-gray-200 bg-white focus-within:border-[#0a152d] focus-within:ring-1 focus-within:ring-[#0a152d] transition-all shadow-xs">
                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-400">
                          <Briefcase className="w-4 h-4" />
                        </div>
                        <input
                          id="job-title-input"
                          type="text"
                          value={jobTitle}
                          onChange={(e) => setJobTitle(e.target.value)}
                          placeholder="e.g. Backend Developer"
                          className="w-full pl-11 pr-4 py-3 text-sm text-[#0a1b33] placeholder-gray-400 bg-transparent rounded-2xl focus:outline-none"
                          disabled={isAnalyzing}
                        />
                      </div>
                    </div>

                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <label
                          htmlFor="job-desc-input"
                          className="block text-xs font-semibold text-[#0a1b33] uppercase tracking-wider"
                        >
                          Step 3: Paste Job Description
                        </label>
                        <span className="text-xs text-gray-400 font-mono">
                          {jobDescription.length} characters
                        </span>
                      </div>
                      <div className="rounded-2xl border border-gray-200 bg-white focus-within:border-[#0a152d] focus-within:ring-1 focus-within:ring-[#0a152d] transition-all shadow-xs">
                        <textarea
                          id="job-desc-input"
                          rows={6}
                          value={jobDescription}
                          onChange={(e) => setJobDescription(e.target.value)}
                          placeholder="Paste the complete job description with required and preferred skills..."
                          className="w-full p-4 text-sm text-[#0a1b33] placeholder-gray-400 bg-transparent rounded-2xl focus:outline-none resize-y min-h-[130px]"
                          disabled={isAnalyzing}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Step 4: Pre-submission Summary & CTA */}
                  <div className="pt-2 border-t border-gray-200/80 space-y-4">
                    <h4 className="text-xs font-semibold text-[#0a1b33] uppercase tracking-wider flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-[#0a152d] text-white flex items-center justify-center text-[10px] font-bold">
                        4
                      </span>
                      Pre-Submission Summary
                    </h4>

                    <div className="p-4 rounded-2xl bg-white border border-gray-200 shadow-2xs space-y-2 text-xs">
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div>
                          <span className="text-gray-400 block text-[11px]">Selected Resume:</span>
                          <span className="font-semibold text-[#0a1b33] truncate block" title={selectedResume?.filename || 'No resume selected'}>
                            {selectedResume?.filename || selectedFile?.name || 'No resume selected'}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-400 block text-[11px]">Target Job:</span>
                          <span className="font-semibold text-[#0a1b33] truncate block" title={jobTitle}>
                            {jobTitle.trim() || 'Untitled Role'}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-400 block text-[11px]">Job Description:</span>
                          <span className="font-semibold text-[#0a1b33] block">
                            {jobDescription.length} characters
                          </span>
                        </div>
                      </div>
                    </div>

                    {!selectedResumeId && (
                      <p className="text-xs text-amber-700 font-medium">
                        * Please select or upload a resume on the left to proceed with analysis.
                      </p>
                    )}

                    <Button
                      type="button"
                      variant="primary"
                      size="lg"
                      className="w-full sm:w-auto"
                      disabled={!selectedResumeId || jobDescription.trim().length === 0 || isAnalyzing || uploadingResume}
                      onClick={handleStartAnalysis}
                      icon={ArrowRight}
                      iconPosition="right"
                    >
                      {isAnalyzing ? 'Analyzing Resume...' : 'Analyze Resume'}
                    </Button>
                  </div>
                </div>
              </div>
            ) : activeTab === 'results' ? (
              <div className="space-y-8">
                {analysisResult ? (
                  <>
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setActiveTab('new-analysis')}
                        icon={RotateCcw}
                        iconPosition="left"
                      >
                        Start New Analysis
                      </Button>

                      {currentAnalysisId && (
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => navigate(`/analysis/${currentAnalysisId}`)}
                          icon={ExternalLink}
                          iconPosition="right"
                        >
                          Open Permanent Report URL
                        </Button>
                      )}
                    </div>

                    <AnalysisCard analysisData={analysisResult} />

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-4">
                      <InterviewQuestionCard questionsByCategory={analysisResult?.interview_questions} />
                      <Roadmap roadmapItems={analysisResult?.learning_roadmap} />
                    </div>
                  </>
                ) : (
                  <div className="p-12 text-center bg-gray-50 rounded-3xl border border-gray-100 max-w-lg mx-auto">
                    <AlertCircle className="w-10 h-10 text-gray-400 mx-auto mb-3" />
                    <h3 className="font-display font-semibold text-lg text-[#0a1b33]">
                      No analysis selected
                    </h3>
                    <p className="text-xs sm:text-sm text-gray-500 mt-1 mb-5">
                      Run a new analysis or select one from your saved analysis history.
                    </p>
                    <Button variant="primary" size="sm" onClick={() => setActiveTab('new-analysis')}>
                      Go to New Analysis
                    </Button>
                  </div>
                )}
              </div>
            ) : activeTab === 'history' ? (
              <div className="space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div>
                    <h3 className="font-display font-bold text-xl sm:text-2xl text-[#0a1b33]">
                      Recent Analyses
                    </h3>
                    <p className="text-xs sm:text-sm text-gray-500 mt-0.5">
                      All previous resume evaluations saved in your account.
                    </p>
                  </div>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => setActiveTab('new-analysis')}
                    icon={Plus}
                    iconPosition="left"
                  >
                    New Analysis
                  </Button>
                </div>

                {loadingHistory ? (
                  <div className="py-12 text-center">
                    <div className="w-6 h-6 rounded-full border-2 border-[#0a152d] border-t-transparent animate-spin mx-auto mb-2" />
                    <p className="text-xs text-gray-500">Loading analysis history...</p>
                  </div>
                ) : historyList.length === 0 ? (
                  <div className="p-12 text-center bg-gray-50 rounded-3xl border border-gray-100 max-w-md mx-auto">
                    <Clock className="w-10 h-10 text-gray-400 mx-auto mb-3" />
                    <h4 className="font-display font-semibold text-lg text-[#0a1b33]">
                      No analyses yet.
                    </h4>
                    <p className="text-xs sm:text-sm text-gray-500 mt-1 mb-5">
                      Compare your resume with a real job description to see your match.
                    </p>
                    <Button variant="primary" size="sm" onClick={() => setActiveTab('new-analysis')}>
                      Start your first analysis
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {historyList.map((item) => (
                      <HistoryCard
                        key={item.id}
                        item={item}
                        onOpen={() => handleOpenHistoricalAnalysis(item)}
                      />
                    ))}
                  </div>
                )}
              </div>
            ) : activeTab === 'resumes' ? (
              <div className="space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div>
                    <h3 className="font-display font-bold text-xl sm:text-2xl text-[#0a1b33]">
                      My Resumes
                    </h3>
                    <p className="text-xs sm:text-sm text-gray-500 mt-0.5">
                      Manage uploaded resumes and view past evaluation counts.
                    </p>
                  </div>
                </div>

                {/* Upload Trigger Area */}
                <div className="p-6 rounded-3xl bg-gray-50/70 border border-gray-200/80">
                  <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                    Upload New Resume PDF
                  </h4>
                  <UploadBox
                    file={null}
                    onFileSelect={handleFileSelect}
                    onFileRemove={() => {}}
                    error={fileError}
                    disabled={uploadingResume}
                  />
                  {uploadingResume && (
                    <p className="mt-2 text-xs text-blue-600 font-medium animate-pulse">
                      Uploading and parsing resume with PyMuPDF...
                    </p>
                  )}
                </div>

                {/* Resumes List */}
                {resumes.length === 0 ? (
                  <div className="p-12 text-center bg-gray-50 rounded-3xl border border-gray-100 max-w-md mx-auto">
                    <FileText className="w-10 h-10 text-gray-400 mx-auto mb-3" />
                    <h4 className="font-display font-semibold text-lg text-[#0a1b33]">
                      No resumes uploaded yet.
                    </h4>
                    <p className="text-xs sm:text-sm text-gray-500 mt-1">
                      Upload your resume to start your first analysis.
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {resumes.map((r) => {
                      const isSelected = selectedResumeId === r.id;
                      const uploadDate = new Date(r.uploaded_at).toLocaleDateString('en-GB', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric',
                      });

                      return (
                        <div
                          key={r.id}
                          className={`p-5 rounded-3xl bg-white border transition-all flex flex-col justify-between gap-4 shadow-xs ${
                            isSelected ? 'border-[#0a152d] ring-1 ring-[#0a152d]' : 'border-gray-200'
                          }`}
                        >
                          <div className="space-y-2">
                            <div className="flex items-center justify-between gap-2">
                              <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
                                {r.file_size}
                              </span>
                              {isSelected ? (
                                <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200/60">
                                  Active Selection
                                </span>
                              ) : (
                                <span className="text-[11px] font-medium text-gray-500 bg-gray-100 px-2.5 py-0.5 rounded-full">
                                  {r.analysis_count || 0} analyses
                                </span>
                              )}
                            </div>

                            <div className="flex items-start gap-3">
                              <div className="w-10 h-10 rounded-2xl bg-gray-100 flex items-center justify-center text-[#0a152d] shrink-0 mt-0.5">
                                <FileText className="w-5 h-5" />
                              </div>
                              <div className="min-w-0 flex-1">
                                <h5 className="font-semibold text-sm sm:text-base text-[#0a1b33] truncate" title={r.filename}>
                                  {r.filename}
                                </h5>
                                <p className="text-xs text-gray-400 mt-0.5 flex items-center gap-1">
                                  <Clock className="w-3 h-3" /> Uploaded on {uploadDate}
                                </p>
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center justify-between pt-3 border-t border-gray-100 gap-2">
                            <Button
                              variant={isSelected ? 'secondary' : 'outline'}
                              size="sm"
                              onClick={() => {
                                setSelectedResumeId(r.id);
                                setSelectedFile({ name: r.filename, size: 0, isExisting: true });
                                setActiveTab('new-analysis');
                              }}
                            >
                              {isSelected ? 'Ready in Form' : 'Use for Analysis'}
                            </Button>

                            <button
                              type="button"
                              onClick={(e) => promptDeleteResume(r, e)}
                              className="p-2 text-gray-400 hover:text-red-600 rounded-xl hover:bg-red-50 transition-colors"
                              title="Delete resume"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            ) : null}
          </div>
        </div>
      </Container>

      {/* Delete Confirmation Modal */}
      <AnimatePresence>
        {resumeToDelete && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-3xl border border-gray-200 p-6 sm:p-8 max-w-md w-full shadow-lg"
            >
              <div className="w-12 h-12 rounded-2xl bg-red-50 text-red-600 flex items-center justify-center mb-4">
                <Trash2 className="w-6 h-6" />
              </div>
              <h3 className="font-display font-bold text-xl text-[#0a1b33]">
                Delete "{resumeToDelete.filename}"?
              </h3>
              <p className="text-xs sm:text-sm text-gray-500 mt-2 mb-6 leading-relaxed">
                This will remove the resume and may affect access to analyses associated with it.
              </p>
              <div className="flex items-center justify-end gap-3">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setResumeToDelete(null)}
                  disabled={isDeletingResume}
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  className="bg-red-600 hover:bg-red-700 text-white border-red-600"
                  onClick={confirmDeleteResume}
                  disabled={isDeletingResume}
                >
                  {isDeletingResume ? 'Deleting...' : 'Delete'}
                </Button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
