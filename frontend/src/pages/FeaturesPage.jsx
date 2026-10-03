import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import {
  CheckCircle2,
  AlertCircle,
  Sparkles,
  FolderGit2,
  ShieldCheck,
  HelpCircle,
  Compass,
  ArrowRight,
  Layers,
} from 'lucide-react';
import Container from '../components/Container';
import Section from '../components/Section';
import Button from '../components/Button';

export default function FeaturesPage() {
  const navigate = useNavigate();

  const featureList = [
    {
      id: 'skill-matching',
      icon: CheckCircle2,
      badge: 'Core Engine',
      title: 'Skill Matching Engine',
      description:
        'Accurately verifies overlapping technical skills, tools, and methodologies that are explicitly stated in both your resume and the job specification. No guessing or vague assumptions.',
      bullets: [
        'Deterministic parsing of programming languages, frameworks, and databases',
        'Distinguishes between primary requirements and secondary qualifications',
        'Presents matched technologies in clean, accessible pill badges',
      ],
    },
    {
      id: 'missing-skills',
      icon: AlertCircle,
      badge: 'Truthful Analysis',
      title: 'Missing Demonstrated Skills',
      description:
        'Pinpoints requirements stated in the job post that are not clearly demonstrated in your resume. Crucially, the system notes that the skill is not demonstrated rather than alleging you do not possess it.',
      bullets: [
        'Separates absent requirements from documented experience',
        'Helps identify overlooked qualifications you forgot to document',
        'Provides honest context so you can update relevant projects',
      ],
    },
    {
      id: 'keyword-analysis',
      icon: Sparkles,
      badge: 'Informational',
      title: 'Domain Keyword Analysis',
      description:
        'Scans the job description for key industry domain keywords and checks their presence in your resume document. Clear disclaimers reinforce that keyword matching is purely informational and not an ATS guarantee.',
      bullets: [
        'Identifies high-frequency technical terminology',
        'Distinguishes found keywords from missing terms',
        'Maintains transparency without making false algorithmic claims',
      ],
    },
    {
      id: 'project-analysis',
      icon: FolderGit2,
      badge: 'Deep Evaluation',
      title: 'Project-Level Relevance & Analysis',
      description:
        'Evaluates each individual project mentioned in your resume. Breaks down the technologies used, relevance to the targeted job, what is strong, and where to improve descriptions.',
      bullets: [
        'Inspects architecture and tooling cited in project descriptions',
        'Highlights whether projects align with target backend/frontend requirements',
        'Recommends quantifiable outcomes (latency, throughput, user metrics)',
      ],
    },
    {
      id: 'resume-suggestions',
      icon: ShieldCheck,
      badge: 'Anti-Hallucination',
      title: 'Truthful Improvement Suggestions',
      description:
        'Never invents skills, companies, degrees, or metrics. All suggestions guide you to highlight real experience truthfully or clarify phrasing.',
      bullets: [
        'Recommends additions conditionally (e.g. "If you have genuinely used Docker...")',
        'Prevents dangerous resume fabrications that fail in technical interviews',
        'Constructive pointers for impact metrics and clear outcome statements',
      ],
    },
    {
      id: 'interview-prep',
      icon: HelpCircle,
      badge: 'Career Prep',
      title: 'Targeted Interview Questions',
      description:
        'Generates customized technical, project, and behavioral interview questions based on your confirmed resume projects and the targeted role expectations.',
      bullets: [
        'Resume & Background inquiries',
        'Architecture & Technical deep-dives',
        'Project consistency and edge-case questions',
        'Job-specific and behavioral scenarios',
      ],
    },
    {
      id: 'learning-roadmap',
      icon: Compass,
      badge: 'Growth Track',
      title: 'Structured Learning Roadmap',
      description:
        'Creates a realistic, week-by-week self-study curriculum specifically prioritized around the technologies and requirements absent from your demonstrated background.',
      bullets: [
        'Weekly focus milestones tailored to your career trajectory',
        'Hands-on implementation steps rather than passive theory',
        'Directly addresses high-priority gaps in target positions',
      ],
    },
  ];

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
              <Layers className="w-3.5 h-3.5 text-[#0a152d]" />
              <span>Full Feature Suite</span>
            </div>
            <h1 className="font-display font-bold text-4xl sm:text-5xl md:text-6xl text-[#0a1b33] tracking-tight">
              Platform Features
            </h1>
            <p className="mt-4 text-base sm:text-lg text-gray-600 leading-relaxed">
              Explore every capability engineered to give you an objective, truthful, and actionable resume analysis experience.
            </p>
          </motion.div>
        </Container>
      </Section>

      {/* Feature Grid */}
      <Section className="py-6 sm:py-12">
        <Container size="default">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {featureList.map((feat) => {
              const Icon = feat.icon;
              return (
                <div
                  key={feat.id}
                  className="bg-white rounded-3xl sm:rounded-[2.5rem] border border-gray-200/90 p-8 sm:p-10 shadow-xs flex flex-col justify-between hover:border-gray-300 transition-colors"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-6">
                      <div className="w-12 h-12 rounded-2xl bg-gray-50 border border-gray-100 flex items-center justify-center text-[#0a152d]">
                        <Icon className="w-6 h-6" />
                      </div>
                      <span className="text-xs font-semibold px-3 py-1 rounded-full bg-gray-100 text-[#0a1b33]">
                        {feat.badge}
                      </span>
                    </div>

                    <h3 className="font-display font-bold text-xl sm:text-2xl text-[#0a1b33] mb-3">
                      {feat.title}
                    </h3>
                    <p className="text-sm text-gray-600 leading-relaxed mb-6">
                      {feat.description}
                    </p>

                    <div className="pt-4 border-t border-gray-100 space-y-2">
                      {feat.bullets.map((b, i) => (
                        <div key={i} className="flex items-start gap-2.5 text-xs sm:text-sm text-gray-600">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#0a152d] shrink-0 mt-2" />
                          <span>{b}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </Container>
      </Section>

      {/* Action Buttons */}
      <Section className="py-8 sm:py-12">
        <Container size="default">
          <div className="bg-[#0a152d] text-white rounded-3xl p-8 sm:p-12 text-center shadow-md">
            <h3 className="font-display font-bold text-2xl sm:text-3xl text-white">
              Ready to see these features in action?
            </h3>
            <p className="mt-2 text-sm sm:text-base text-gray-300 max-w-md mx-auto">
              Test with your real resume or inspect the interactive live demo.
            </p>
            <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-3">
              <Button
                variant="secondary"
                size="lg"
                onClick={() => navigate('/dashboard')}
                icon={ArrowRight}
                iconPosition="right"
              >
                Start New Analysis
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="text-white border-gray-600 hover:bg-white/10"
                onClick={() => navigate('/preview')}
              >
                View Live Preview
              </Button>
            </div>
          </div>
        </Container>
      </Section>

      {/* Footer */}
      <footer className="mt-12 pt-8 border-t border-gray-200 text-center text-xs text-gray-500">
        <Container size="default">
          <p>© 2026 AI Resume Agent. Dedicated Features Page.</p>
        </Container>
      </footer>
    </div>
  );
}
