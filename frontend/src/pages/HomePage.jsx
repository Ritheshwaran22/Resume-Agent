import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
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
} from 'lucide-react';
import Container from '../components/Container';
import Section from '../components/Section';
import Button from '../components/Button';
import { useAuth } from '../context/AuthContext';

export default function HomePage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const corePillars = [
    {
      step: '01',
      title: 'How It Works',
      desc: 'Transparent 3-step pipeline: upload resume PDF, input target job requirements, and get truthful gap analysis.',
      link: '/how-it-works',
      action: 'Learn workflow',
    },
    {
      step: '02',
      title: 'Core Features',
      desc: 'Deep matching for skills, missing demonstrated skills, project relevance, truthful suggestions, and learning roadmaps.',
      link: '/features',
      action: 'Explore features',
    },
    {
      step: '03',
      title: 'Live Preview',
      desc: 'Inspect an interactive analysis result preview showing realistic scores, match breakdowns, and structured outputs.',
      link: '/preview',
      action: 'View live preview',
    },
  ];

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
                onClick={() => navigate(isAuthenticated ? '/dashboard' : '/register')}
                icon={ArrowRight}
                iconPosition="right"
              >
                {isAuthenticated ? 'Open Dashboard' : 'Analyze My Resume'}
              </Button>
              <Button
                variant="secondary"
                size="lg"
                className="w-full sm:w-auto"
                onClick={() => navigate('/how-it-works')}
              >
                How It Works
              </Button>
            </div>

            {/* Trust statement */}
            <p className="mt-5 text-xs text-gray-400">
              No fabrication • Objective skill verification • Privacy conscious
            </p>

            {/* Preview Banner linking to /preview */}
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
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => navigate('/preview')}
                    icon={ArrowRight}
                    iconPosition="right"
                  >
                    Explore Live Preview
                  </Button>
                </div>
              </div>
            </div>
          </motion.div>
        </Container>
      </Section>

      {/* Navigation Cards to Explore Dedicated Pages */}
      <Section className="py-10 sm:py-16">
        <Container size="default">
          <div className="text-center max-w-xl mx-auto mb-10 sm:mb-12">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
              Platform Overview
            </span>
            <h2 className="font-display font-bold text-3xl sm:text-4xl text-[#0a1b33] mt-1">
              Explore the Application
            </h2>
            <p className="text-sm sm:text-base text-gray-600 mt-2">
              Browse each section to learn how our AI Resume Agent works, inspect features, and test the analysis.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
            {corePillars.map((item, index) => (
              <div
                key={index}
                className="bg-white rounded-3xl border border-gray-200/90 p-8 shadow-xs flex flex-col justify-between hover:border-gray-300 transition-colors"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span className="font-display font-bold text-lg text-gray-400">
                      {item.step}
                    </span>
                    <span className="w-2 h-2 rounded-full bg-[#0a152d]" />
                  </div>
                  <h3 className="font-display font-semibold text-xl text-[#0a1b33] mb-2">
                    {item.title}
                  </h3>
                  <p className="text-sm text-gray-600 leading-relaxed mb-6">
                    {item.desc}
                  </p>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate(item.link)}
                  icon={ArrowRight}
                  iconPosition="right"
                  className="w-full justify-center"
                >
                  {item.action}
                </Button>
              </div>
            ))}
          </div>
        </Container>
      </Section>

      {/* Final Call to Action */}
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
                onClick={() => navigate(isAuthenticated ? '/dashboard' : '/register')}
                icon={ArrowRight}
                iconPosition="right"
              >
                {isAuthenticated ? 'Launch Dashboard' : 'Get Started Free'}
              </Button>
            </div>
          </div>
        </Container>
      </Section>

      {/* Footer */}
      <footer className="mt-12 pt-8 border-t border-gray-200 text-center text-xs text-gray-500">
        <Container size="default">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 py-4">
            <div className="flex items-center gap-2">
              <span className="font-display font-bold text-sm text-[#0a1b33]">
                Resume Agent
              </span>
              <span>•</span>
              <span>Phase 1 Multi-Page Architecture</span>
            </div>
            <p>© 2026 AI Resume Agent. Built with Django, React & Tailwind CSS.</p>
          </div>
        </Container>
      </footer>
    </div>
  );
}
