import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { Sparkles, ArrowRight, Play, CheckCircle2, RotateCcw } from 'lucide-react';
import Container from '../components/Container';
import Section from '../components/Section';
import Button from '../components/Button';
import AnalysisCard from '../components/AnalysisCard';
import InterviewQuestionCard from '../components/InterviewQuestionCard';
import Roadmap from '../components/Roadmap';

export default function PreviewPage() {
  const navigate = useNavigate();

  const scenarios = [
    {
      id: 'backend',
      label: 'Senior Backend Engineer',
      title: 'Senior Backend Engineer (Python / Django / Cloud)',
      data: {
        match_score: 74,
        overview:
          'Your resume demonstrates strong technical foundations relevant to this role, with several key job requirements (Docker, AWS, Redis) that are not clearly demonstrated in your current project descriptions.',
        matched_skills: ['Python', 'Django', 'REST APIs', 'PostgreSQL', 'Git', 'System Architecture'],
        missing_skills: ['Docker', 'AWS ECS', 'Kubernetes', 'Redis Caching'],
        keywords_found: ['Python', 'Django', 'REST', 'PostgreSQL', 'CI/CD', 'API Design'],
        keywords_missing: ['Containerization', 'Microservices', 'Distributed Systems'],
        resume_strengths: [
          'Strong hands-on experience building backend services with Python and Django.',
          'Demonstrated relational database architecture and query optimization using PostgreSQL.',
          'Clear project implementations showing end-to-end API lifecycle management.',
        ],
        resume_weaknesses: [
          'Cloud deployment and containerization requirements (Docker, AWS) are not demonstrated.',
          'Project descriptions focus primarily on features rather than measurable performance impacts.',
          'Caching and high-throughput queuing technologies mentioned in the job post are absent.',
        ],
        project_analysis: [
          {
            project: 'E-Commerce REST API & Inventory Service',
            technologies: ['Python', 'Django', 'DRF', 'PostgreSQL'],
            relevance: 'High — directly mirrors the backend framework and data persistence stack in the job description.',
            strong: 'Good schema structuring and comprehensive authentication setup with JWT.',
            improvements: 'Clarify request throughput, query latency benchmarks, and whether automated test suites were used.',
          },
          {
            project: 'Real-Time Notification Worker',
            technologies: ['Python', 'WebSockets', 'Celery'],
            relevance: 'Medium — demonstrates background processing, but job description specifically asks for Redis caching.',
            strong: 'Shows asynchronous workflow handling.',
            improvements: 'Mention the broker used and if you have genuinely utilized Redis, specify that detail.',
          },
        ],
        resume_suggestions: [
          'Docker is mentioned in the job description but is not clearly demonstrated in your resume. If you have genuinely used Docker or containerized services, consider adding it to your projects or skills section.',
          'AWS deployment is listed as a primary requirement. If you have configured cloud instances or CI/CD pipelines targeting AWS, highlight that concrete exposure.',
          'Quantify results where possible: rather than stating "optimized queries", state the approximate latency reduction or database table size handled.',
        ],
      },
    },
    {
      id: 'fullstack',
      label: 'Full Stack Engineer',
      title: 'Full Stack Engineer (Django + React)',
      data: {
        match_score: 82,
        overview:
          'Your resume presents a balanced full-stack skill profile aligning closely with both frontend React interfaces and backend Django REST APIs. CI/CD automation and container orchestration represent the primary undemonstrated areas.',
        matched_skills: ['Python', 'Django', 'JavaScript', 'React', 'Tailwind CSS', 'PostgreSQL', 'Git'],
        missing_skills: ['Docker Compose', 'GitHub Actions CI/CD', 'AWS CloudFront'],
        keywords_found: ['Full Stack', 'Django', 'React', 'RESTful APIs', 'State Management'],
        keywords_missing: ['Automated Pipelines', 'Cloud CDN', 'Infrastructure as Code'],
        resume_strengths: [
          'Direct exposure to both frontend React state paradigms and backend Django ORM.',
          'Clean modular frontend component structure demonstrated in portfolio projects.',
          'Consistent use of Git version control and collaborative workflows.',
        ],
        resume_weaknesses: [
          'Testing methodologies (unit/integration test coverage) are not articulated.',
          'Automated deployment scripts and container builds are not mentioned.',
        ],
        project_analysis: [
          {
            project: 'Interactive Task Management Dashboard',
            technologies: ['React', 'Tailwind CSS', 'Django REST', 'PostgreSQL'],
            relevance: 'Very High — identical tech stack to the job description.',
            strong: 'Responsive UI execution and clean JWT session management.',
            improvements: 'Include Lighthouse accessibility scores or load time metrics if measured.',
          },
        ],
        resume_suggestions: [
          'If you have written automated tests using Jest or pytest, explicitly mention test coverage percentage.',
          'Highlight experience with Docker if you used it in local development environments.',
        ],
      },
    },
  ];

  const [activeScenario, setActiveScenario] = useState(scenarios[0]);

  return (
    <div className="pt-24 sm:pt-28 pb-16 min-h-screen">
      {/* Header */}
      <Section className="py-6 sm:py-10">
        <Container size="default">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="text-center max-w-3xl mx-auto"
          >
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white border border-gray-200/80 text-xs font-semibold text-[#0a1b33] mb-4 shadow-2xs">
              <Sparkles className="w-3.5 h-3.5 text-[#0a152d]" />
              <span>Interactive Output Showcase</span>
            </div>
            <h1 className="font-display font-bold text-4xl sm:text-5xl md:text-6xl text-[#0a1b33] tracking-tight">
              Live Analysis Preview
            </h1>
            <p className="mt-4 text-base sm:text-lg text-gray-600 leading-relaxed">
              Explore an authentic simulation of the structured analysis, match indicator, project evaluation, interview questions, and learning roadmap.
            </p>

            {/* Scenario Switcher */}
            <div className="mt-8 inline-flex items-center gap-2 p-1.5 bg-white rounded-full border border-gray-200 shadow-2xs">
              {scenarios.map((sc) => (
                <button
                  key={sc.id}
                  onClick={() => setActiveScenario(sc)}
                  className={`px-4 py-2 rounded-full text-xs sm:text-sm font-medium transition-all cursor-pointer ${
                    activeScenario.id === sc.id
                      ? 'bg-[#0a152d] text-white shadow-xs font-semibold'
                      : 'text-gray-600 hover:text-[#0a1b33]'
                  }`}
                >
                  {sc.label}
                </button>
              ))}
            </div>
          </motion.div>
        </Container>
      </Section>

      {/* Main Analysis Results Preview */}
      <Section className="py-6 sm:py-10">
        <Container size="hero">
          <div className="max-w-4xl mx-auto space-y-8">
            <AnalysisCard analysisData={activeScenario.data} />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-4">
              <InterviewQuestionCard />
              <Roadmap />
            </div>
          </div>
        </Container>
      </Section>

      {/* Bottom CTA to Test Real Resume */}
      <Section className="py-8 sm:py-12">
        <Container size="default">
          <div className="bg-[#0a152d] text-white rounded-3xl p-8 sm:p-12 text-center shadow-md">
            <h3 className="font-display font-bold text-2xl sm:text-3xl text-white">
              Ready to evaluate your own resume?
            </h3>
            <p className="mt-2 text-sm sm:text-base text-gray-300 max-w-md mx-auto">
              Upload your PDF resume in the dashboard and compare it with any real job posting.
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
          <p>© 2026 AI Resume Agent. Dedicated Preview Page.</p>
        </Container>
      </footer>
    </div>
  );
}
