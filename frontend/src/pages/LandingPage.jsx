import React from 'react';
import { motion } from 'motion/react';
import {
  FileText,
  Briefcase,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  ShieldCheck,
  Compass,
  HelpCircle,
  FolderGit2,
  Check,
} from 'lucide-react';
import Container from '../components/Container';
import Section from '../components/Section';
import Button from '../components/Button';
import AnalysisCard from '../components/AnalysisCard';

export default function LandingPage({ onStartAnalysis }) {
  const steps = [
    {
      step: '01',
      title: 'Upload Resume',
      description: 'Upload your current PDF resume. We extract and structure your demonstrated skills and project history without saving or leaking private data.',
      icon: FileText,
    },
    {
      step: '02',
      title: 'Add Job Description',
      description: 'Paste any target job description or requirements. Our system identifies the essential tech stack, domain terms, and core qualifications.',
      icon: Briefcase,
    },
    {
      step: '03',
      title: 'Analyze & Improve',
      description: 'Receive an honest breakdown: matching skills, missing demonstrated competencies, project feedback, and truthful resume suggestions.',
      icon: Sparkles,
    },
  ];

  const features = [
    {
      title: 'Skill Matching',
      description: 'Clearly identifies overlapping technologies and qualifications directly confirmed in your resume.',
      icon: CheckCircle2,
    },
    {
      title: 'Missing Demonstrated Skills',
      description: 'Highlights job requirements not clearly visible in your experience, without falsely assuming you lack them.',
      icon: AlertCircle,
    },
    {
      title: 'Keyword Analysis',
      description: 'Informational analysis of domain terms and terminology frequency to help refine your phrasing.',
      icon: Sparkles,
    },
    {
      title: 'Project Analysis',
      description: 'Evaluates your resume projects against job needs, highlighting what is strong and where to add measurable impact.',
      icon: FolderGit2,
    },
    {
      title: 'Truthful Suggestions',
      description: 'Actionable guidance on how to present genuine experience without fabricating skills or credentials.',
      icon: ShieldCheck,
    },
    {
      title: 'Interview Preparation',
      description: 'Categorized practice questions tailored to your actual resume projects and the targeted role.',
      icon: HelpCircle,
    },
    {
      title: 'Learning Roadmap',
      description: 'A structured, week-by-week plan to systematically bridge the gap for skills missing from your background.',
      icon: Compass,
    },
  ];

  const previewSample = {
    match_score: 72,
    overview: 'Your resume has several relevant skills for this role, with some requirements that are not clearly demonstrated.',
    matched_skills: ['Python', 'Django', 'SQL', 'Machine Learning', 'Git'],
    missing_skills: ['Docker', 'AWS', 'Kubernetes', 'Redis'],
    keywords_found: ['Python', 'Django', 'REST APIs', 'PostgreSQL', 'Git'],
    keywords_missing: ['Containerization', 'Cloud Deployment', 'Distributed Queuing'],
    resume_strengths: [
      'Strong Python and Django backend development foundations.',
      'Clear relational database modeling with PostgreSQL.',
      'Practical exposure to Machine Learning pipelines and data workflows.',
    ],
    resume_weaknesses: [
      'Containerization tools (Docker/Kubernetes) are not mentioned in your resume.',
      'Cloud deployment pipelines (AWS) are not clearly demonstrated.',
      'Project descriptions could contain clearer measurable outcomes and latency metrics.',
    ],
    project_analysis: [
      {
        project: 'AI Resume Agent Platform',
        technologies: ['Python', 'Django', 'PostgreSQL', 'PyMuPDF'],
        relevance: 'High — directly matches the backend framework, database, and document parsing stack.',
        strong: 'Modular service architecture with clean boundary separation.',
        improvements: 'Mention request throughput and whether automated unit tests were implemented.',
      },
    ],
    resume_suggestions: [
      'Docker is mentioned in the job description but is not clearly demonstrated in your resume. If you have genuinely used Docker, consider adding it to the relevant project or skills section.',
      'AWS is required for cloud hosting. If you have deployed projects on AWS services, explicitly detail that operational experience.',
      'Specify the impact of your database optimizations with concrete figures where possible.',
    ],
  };

  return (
    <div className="pt-24 sm:pt-28 pb-16">
      {/* Hero Section */}
      <Section className="py-6 sm:py-10 md:py-12">
        <Container size="hero">
          {/* Main Hero White Rounded Container */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, ease: 'easeOut' }}
            className="bg-white rounded-3xl sm:rounded-[2.5rem] border border-gray-200/90 shadow-[0_4px_30px_-6px_rgba(10,27,51,0.04)] p-8 sm:p-12 md:p-16 lg:p-20 text-center relative overflow-hidden"
          >
            {/* Subtle top badge */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-gray-50 border border-gray-200/70 text-xs font-semibold text-[#0a1b33] mb-6 sm:mb-8">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>AI Resume Agent • Truthful Skill Alignment</span>
            </div>

            {/* Hero Headline */}
            <h1 className="font-display font-bold text-4xl sm:text-5xl md:text-6xl lg:text-7xl text-[#0a1b33] tracking-tight max-w-4xl mx-auto leading-[1.08]">
              Make your resume
              <br className="hidden sm:inline" /> fit the job.
            </h1>

            {/* Supporting Paragraph */}
            <p className="mt-5 sm:mt-7 text-base sm:text-lg md:text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed font-normal">
              Upload your resume, add a job description, and get a clear breakdown of what matches, what is missing, and what you can improve.
            </p>

            {/* CTA Group */}
            <div className="mt-8 sm:mt-10 flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 max-w-md mx-auto">
              <Button
                variant="primary"
                size="lg"
                className="w-full sm:w-auto"
                onClick={onStartAnalysis}
                icon={ArrowRight}
                iconPosition="right"
              >
                Analyze My Resume
              </Button>
              <Button
                variant="secondary"
                size="lg"
                className="w-full sm:w-auto"
                onClick={() => {
                  document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' });
                }}
              >
                How It Works
              </Button>
            </div>

            {/* Trust statement */}
            <p className="mt-5 text-xs text-gray-400">
              No fabrication • Objective skill verification • Privacy conscious
            </p>

            {/* Preview Sneak-Peek Graphic */}
            <div className="mt-12 sm:mt-16 pt-8 border-t border-gray-100 max-w-3xl mx-auto text-left">
              <div className="p-4 sm:p-5 rounded-2xl bg-gray-50/70 border border-gray-200/70 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-[#0a152d] text-white flex items-center justify-center font-display font-bold text-sm shrink-0">
                    72%
                  </div>
                  <div>
                    <h4 className="font-semibold text-sm text-[#0a1b33]">
                      Resume-to-job match indicator
                    </h4>
                    <p className="text-xs text-gray-500">
                      5 matched skills • 4 missing demonstrated requirements
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-600 font-medium hidden sm:inline">
                    Interactive Preview Below
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      document.getElementById('preview')?.scrollIntoView({ behavior: 'smooth' });
                    }}
                    icon={ArrowRight}
                    iconPosition="right"
                  >
                    View Result
                  </Button>
                </div>
              </div>
            </div>
          </motion.div>
        </Container>
      </Section>

      {/* How It Works Section */}
      <Section id="how-it-works" className="py-12 sm:py-16">
        <Container size="default">
          <div className="text-center max-w-xl mx-auto mb-12 sm:mb-16">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
              Process
            </span>
            <h2 className="font-display font-bold text-3xl sm:text-4xl text-[#0a1b33] mt-1">
              How It Works
            </h2>
            <p className="text-sm sm:text-base text-gray-600 mt-2">
              Three straightforward steps to evaluate and refine your resume alignment.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
            {steps.map((item, index) => {
              const Icon = item.icon;
              return (
                <div
                  key={index}
                  className="bg-white rounded-3xl border border-gray-200/90 p-8 shadow-xs flex flex-col justify-between hover:border-gray-300 transition-colors"
                >
                  <div>
                    <div className="flex items-center justify-between mb-6">
                      <div className="w-12 h-12 rounded-2xl bg-gray-50 border border-gray-100 flex items-center justify-center text-[#0a1b33]">
                        <Icon className="w-5 h-5 text-[#0a152d]" />
                      </div>
                      <span className="font-display font-bold text-xl text-gray-300">
                        {item.step}
                      </span>
                    </div>

                    <h3 className="font-display font-semibold text-xl text-[#0a1b33] mb-2">
                      {item.title}
                    </h3>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {item.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </Container>
      </Section>

      {/* What You Get Section */}
      <Section id="features" className="py-12 sm:py-16 bg-[#f4f5f7]/60 border-y border-gray-200/60">
        <Container size="default">
          <div className="text-center max-w-xl mx-auto mb-12 sm:mb-16">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
              Comprehensive Output
            </span>
            <h2 className="font-display font-bold text-3xl sm:text-4xl text-[#0a1b33] mt-1">
              What You Get
            </h2>
            <p className="text-sm sm:text-base text-gray-600 mt-2">
              Actionable, grounded analysis with zero hallucinations and truthful recommendations.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feat, index) => {
              const Icon = feat.icon;
              return (
                <div
                  key={index}
                  className="bg-white rounded-3xl border border-gray-200/90 p-6 sm:p-7 shadow-xs flex flex-col"
                >
                  <div className="w-10 h-10 rounded-2xl bg-gray-50 border border-gray-100 flex items-center justify-center text-[#0a152d] mb-4">
                    <Icon className="w-5 h-5" />
                  </div>
                  <h4 className="font-display font-semibold text-lg text-[#0a1b33] mb-2">
                    {feat.title}
                  </h4>
                  <p className="text-xs sm:text-sm text-gray-600 leading-relaxed">
                    {feat.description}
                  </p>
                </div>
              );
            })}
          </div>
        </Container>
      </Section>

      {/* Product Preview Section */}
      <Section id="preview" className="py-12 sm:py-20">
        <Container size="hero">
          <div className="text-center max-w-xl mx-auto mb-12">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
              Realistic Output Preview
            </span>
            <h2 className="font-display font-bold text-3xl sm:text-4xl text-[#0a1b33] mt-1">
              Structured Analysis Preview
            </h2>
            <p className="text-sm sm:text-base text-gray-600 mt-2">
              Here is a representative preview of an analysis comparing a Python/Django resume against a full-stack job posting.
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <AnalysisCard analysisData={previewSample} />
          </div>
        </Container>
      </Section>

      {/* Final CTA Section */}
      <Section className="py-12 sm:py-16">
        <Container size="default">
          <div className="bg-[#0a152d] text-white rounded-3xl sm:rounded-[2.5rem] p-8 sm:p-12 md:p-16 text-center shadow-md relative overflow-hidden">
            <h2 className="font-display font-bold text-3xl sm:text-4xl md:text-5xl text-white tracking-tight">
              Ready to understand your resume better?
            </h2>
            <p className="mt-4 text-sm sm:text-base md:text-lg text-gray-300 max-w-xl mx-auto leading-relaxed">
              Upload your resume and target job description now to identify matches, gaps, and practical improvements.
            </p>
            <div className="mt-8 flex justify-center">
              <Button
                variant="secondary"
                size="lg"
                onClick={onStartAnalysis}
                icon={ArrowRight}
                iconPosition="right"
              >
                Analyze Your Resume
              </Button>
            </div>
          </div>
        </Container>
      </Section>

      {/* Clean Minimal Footer */}
      <footer className="mt-12 pt-8 border-t border-gray-200 text-center text-xs text-gray-500">
        <Container size="default">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 py-4">
            <div className="flex items-center gap-2">
              <span className="font-display font-bold text-sm text-[#0a1b33]">
                Resume Agent
              </span>
              <span>•</span>
              <span>Phase 1 Architecture Setup</span>
            </div>
            <p>© 2026 AI Resume Agent. Developed with Django, React & Tailwind CSS.</p>
          </div>
        </Container>
      </footer>
    </div>
  );
}
