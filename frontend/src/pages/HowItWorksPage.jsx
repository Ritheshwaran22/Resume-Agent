import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import {
  FileText,
  Briefcase,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Check,
  X,
  Lock,
} from 'lucide-react';
import Container from '../components/Container';
import Section from '../components/Section';
import Button from '../components/Button';

export default function HowItWorksPage() {
  const navigate = useNavigate();

  const steps = [
    {
      step: '01',
      title: 'Upload Your Resume PDF',
      summary: 'Secure extraction of documented experience and technical skills.',
      details: [
        'Upload any standard PDF resume up to 10 MB.',
        'PyMuPDF parses clean text layers without executing code or storing sensitive personally identifiable information.',
        'Extracts your projects, declared technologies, work achievements, and education history into structured records.',
      ],
      icon: FileText,
    },
    {
      step: '02',
      title: 'Input Target Job Requirements',
      summary: 'Deconstruct real job postings into verifiable competency criteria.',
      details: [
        'Paste the full job title and unedited requirements description from any job board.',
        'Identifies required skills versus nice-to-have qualifications.',
        'Catalogs industry keywords and core architectural domain demands.',
      ],
      icon: Briefcase,
    },
    {
      step: '03',
      title: 'Analyze, Compare & Plan',
      summary: 'Objective comparison, truthful feedback, interview prep, and learning roadmap.',
      details: [
        'Computes an internal resume-to-job match indicator strictly comparing confirmed resume content with stated job requirements.',
        'Lists demonstrated matching skills and flags requirements not clearly demonstrated.',
        'Never assumes you do not know a skill — only highlights that it is absent from your document.',
        'Delivers truthful suggestions, tailored interview questions, and a week-by-week roadmap to bridge gaps.',
      ],
      icon: Sparkles,
    },
  ];

  const comparisons = [
    {
      feature: 'Skill Evaluation',
      resumeAgent: 'Strictly verifies skills documented in your resume against job criteria.',
      genericAi: 'Guesses abilities and often fabricates claims to boost match score.',
    },
    {
      feature: 'Missing Skills',
      resumeAgent: 'Labels skills as "not demonstrated in resume" without making assumptions.',
      genericAi: 'Claims you do not know the technology or tells you to lie.',
    },
    {
      feature: 'Match Indicator',
      resumeAgent: 'Internal comparison indicator for self-improvement; no fake ATS claims.',
      genericAi: 'Promises "99% ATS Pass Rate" or false hiring probability guarantees.',
    },
    {
      feature: 'Suggestions',
      resumeAgent: 'Truthful suggestions: "If you have genuinely used X, consider mentioning it."',
      genericAi: 'Blindly adds fake technologies and keywords you may never have used.',
    },
    {
      feature: 'Interview Preparation',
      resumeAgent: 'Generates questions grounded in your actual projects and target job.',
      genericAi: 'Produces generic, disconnected question lists.',
    },
  ];

  return (
    <div className="pt-24 sm:pt-28 pb-16 min-h-screen">
      {/* Hero Header */}
      <Section className="py-6 sm:py-10">
        <Container size="default">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="text-center max-w-3xl mx-auto"
          >
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white border border-gray-200/80 text-xs font-semibold text-[#0a1b33] mb-4 shadow-2xs">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              <span>Transparent & Grounded Process</span>
            </div>
            <h1 className="font-display font-bold text-4xl sm:text-5xl md:text-6xl text-[#0a1b33] tracking-tight">
              How It Works
            </h1>
            <p className="mt-4 text-base sm:text-lg text-gray-600 leading-relaxed">
              A reliable, transparent three-step pipeline designed to evaluate your real qualifications against job postings without hallucinating credentials.
            </p>
          </motion.div>
        </Container>
      </Section>

      {/* 3 Detailed Steps */}
      <Section className="py-6 sm:py-12">
        <Container size="default">
          <div className="space-y-8 sm:space-y-12">
            {steps.map((item, index) => {
              const Icon = item.icon;
              return (
                <div
                  key={index}
                  className="bg-white rounded-3xl sm:rounded-[2.5rem] border border-gray-200/90 p-6 sm:p-10 shadow-xs flex flex-col md:flex-row gap-6 sm:gap-10 items-start"
                >
                  {/* Left Step Header */}
                  <div className="flex md:flex-col items-center md:items-start justify-between w-full md:w-56 shrink-0 gap-3">
                    <div className="w-14 h-14 rounded-2xl bg-gray-50 border border-gray-100 flex items-center justify-center text-[#0a152d]">
                      <Icon className="w-6 h-6" />
                    </div>
                    <div>
                      <span className="font-display font-bold text-2xl text-gray-300">
                        {item.step}
                      </span>
                      <h3 className="font-display font-bold text-xl text-[#0a1b33] mt-1">
                        {item.title}
                      </h3>
                    </div>
                  </div>

                  {/* Right Details */}
                  <div className="flex-1 space-y-4">
                    <p className="font-medium text-base text-[#0a1b33]">
                      {item.summary}
                    </p>
                    <ul className="space-y-2.5">
                      {item.details.map((detail, dIdx) => (
                        <li key={dIdx} className="flex items-start gap-3 text-sm text-gray-600">
                          <Check className="w-4 h-4 text-[#0a152d] shrink-0 mt-0.5" />
                          <span className="leading-relaxed">{detail}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              );
            })}
          </div>
        </Container>
      </Section>

      {/* Philosophy Comparison Table */}
      <Section className="py-12 sm:py-16">
        <Container size="default">
          <div className="text-center max-w-xl mx-auto mb-10">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
              Comparison
            </span>
            <h2 className="font-display font-bold text-3xl sm:text-4xl text-[#0a1b33] mt-1">
              Why Our Approach Is Different
            </h2>
            <p className="text-sm text-gray-600 mt-2">
              We focus on honest, actionable engineering truth rather than automated fluff.
            </p>
          </div>

          <div className="bg-white rounded-3xl sm:rounded-[2.5rem] border border-gray-200/90 shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-gray-100 bg-gray-50/60">
                    <th className="py-4 px-6 font-semibold text-[#0a1b33]">Aspect</th>
                    <th className="py-4 px-6 font-semibold text-[#0a152d] bg-gray-100/60">
                      AI Resume Agent
                    </th>
                    <th className="py-4 px-6 font-semibold text-gray-500">Generic AI Tools</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {comparisons.map((row, idx) => (
                    <tr key={idx} className="hover:bg-gray-50/40 transition-colors">
                      <td className="py-4 px-6 font-semibold text-[#0a1b33] whitespace-nowrap">
                        {row.feature}
                      </td>
                      <td className="py-4 px-6 text-[#0a1b33] bg-gray-50/30 font-medium">
                        <div className="flex items-start gap-2">
                          <Check className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                          <span>{row.resumeAgent}</span>
                        </div>
                      </td>
                      <td className="py-4 px-6 text-gray-500">
                        <div className="flex items-start gap-2">
                          <X className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                          <span>{row.genericAi}</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </Container>
      </Section>

      {/* CTA Section */}
      <Section className="py-8 sm:py-12">
        <Container size="default">
          <div className="bg-[#0a152d] text-white rounded-3xl p-8 sm:p-12 text-center shadow-md">
            <h3 className="font-display font-bold text-2xl sm:text-3xl text-white">
              Try It On Your Resume Now
            </h3>
            <p className="mt-2 text-sm sm:text-base text-gray-300 max-w-md mx-auto">
              Test your resume against any job description in less than 30 seconds.
            </p>
            <div className="mt-6 flex justify-center">
              <Button
                variant="secondary"
                size="lg"
                onClick={() => navigate('/dashboard')}
                icon={ArrowRight}
                iconPosition="right"
              >
                Go to Dashboard
              </Button>
            </div>
          </div>
        </Container>
      </Section>

      {/* Footer */}
      <footer className="mt-12 pt-8 border-t border-gray-200 text-center text-xs text-gray-500">
        <Container size="default">
          <p>© 2026 AI Resume Agent. Dedicated How It Works Page.</p>
        </Container>
      </footer>
    </div>
  );
}
