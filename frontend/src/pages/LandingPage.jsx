import { Link } from 'react-router-dom';
import { FiCheckCircle, FiZap, FiShield, FiTrendingUp, FiUsers, FiTarget } from 'react-icons/fi';

const features = [
  { icon: <FiZap />, title: 'AI-Powered Matching', desc: 'Semantic NLP engine that understands context, not just keywords. "Team management" matches "Leadership skills" automatically.' },
  { icon: <FiTarget />, title: 'Match Score Analytics', desc: 'Get detailed percentage scores with skill gap analysis for every job application.' },
  { icon: <FiShield />, title: 'Smart Resume Parsing', desc: 'Upload PDF/DOCX resumes and our AI extracts skills, education, and experience automatically.' },
  { icon: <FiTrendingUp />, title: 'Candidate Ranking', desc: 'Recruiters see applicants ranked by AI relevance, saving hours of manual screening.' },
  { icon: <FiUsers />, title: 'Role-Based Dashboards', desc: 'Tailored analytics dashboards for Job Seekers, Recruiters, and Administrators.' },
  { icon: <FiCheckCircle />, title: 'Resume Suggestions', desc: 'Get actionable recommendations to improve your resume and increase match scores.' },
];

const stats = [
  { value: '95%', label: 'Matching Accuracy' },
  { value: '3x', label: 'Faster Screening' },
  { value: '10K+', label: 'Resumes Processed' },
  { value: '500+', label: 'Jobs Matched' },
];

const steps = [
  { num: '01', title: 'Upload Resume', desc: 'Upload your resume in PDF or DOCX format. Our AI instantly parses and analyses it.' },
  { num: '02', title: 'AI Analysis', desc: 'NLP engine extracts skills, builds embeddings, and matches against job descriptions semantically.' },
  { num: '03', title: 'Get Matched', desc: 'Receive ranked job matches with detailed score breakdowns and improvement suggestions.' },
];

export default function LandingPage() {
  return (
    <div className="gradient-bg min-h-screen">
      {/* ── Navbar ────────────────────────────────── */}
      <nav className="flex items-center justify-between px-8 py-5 max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold">
            AI
          </div>
          <span className="text-xl font-bold text-white">MatchAI</span>
        </div>
        <div className="flex items-center gap-4">
          <Link to="/login" className="text-slate-300 hover:text-white transition text-sm font-medium">
            Sign In
          </Link>
          <Link to="/register" className="btn-primary text-sm !py-2.5 !px-5">
            Get Started
          </Link>
        </div>
      </nav>

      {/* ── Hero ──────────────────────────────────── */}
      <section className="relative overflow-hidden">
        <div className="blob w-96 h-96 bg-indigo-600 top-20 left-10" />
        <div className="blob w-80 h-80 bg-purple-600 top-40 right-20" style={{ animationDelay: '2s' }} />

        <div className="gradient-hero relative z-10 text-center py-28 px-6 max-w-5xl mx-auto">
          <div className="inline-block mb-6 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-medium tracking-wide">
            🚀 AI-Enabled Employment Matching Platform
          </div>
          <h1 className="text-5xl md:text-7xl font-black leading-tight mb-6">
            Find Your Perfect
            <br />
            <span className="gradient-text">Career Match</span>
          </h1>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Our intelligent recruitment platform uses NLP and semantic AI to match
            job seekers with the right opportunities — beyond simple keyword matching.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link to="/register" className="btn-primary text-base !py-3.5 !px-8">
              Start Matching — Free
            </Link>
            <Link to="/register?role=RECRUITER" className="btn-outline text-base !py-3.5 !px-8">
              I'm a Recruiter
            </Link>
          </div>
        </div>
      </section>

      {/* ── Stats ─────────────────────────────────── */}
      <section className="max-w-5xl mx-auto px-6 py-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map((s) => (
            <div key={s.label} className="glass-card text-center">
              <div className="text-3xl font-black gradient-text">{s.value}</div>
              <div className="text-xs text-slate-500 mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Features ──────────────────────────────── */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Powered by <span className="gradient-text">Advanced AI</span>
          </h2>
          <p className="text-slate-400 max-w-xl mx-auto">
            Our platform leverages TF-IDF, BM25, and Sentence Transformers (SBERT)
            to deliver semantic understanding of resumes and job descriptions.
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {features.map((f) => (
            <div key={f.title} className="glass-card group">
              <div className="w-12 h-12 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 text-xl mb-4 group-hover:scale-110 transition-transform">
                {f.icon}
              </div>
              <h3 className="text-lg font-bold text-slate-100 mb-2">{f.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How It Works ──────────────────────────── */}
      <section className="max-w-5xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            How It <span className="gradient-text">Works</span>
          </h2>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((s) => (
            <div key={s.num} className="relative">
              <div className="text-6xl font-black text-indigo-500/10 mb-2">{s.num}</div>
              <h3 className="text-xl font-bold text-slate-100 mb-2">{s.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Testimonials ──────────────────────────── */}
      {/* <section className="max-w-5xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold">What People <span className="gradient-text">Say</span></h2>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            { name: 'Priya S.', role: 'Software Engineer', text: 'The AI matching found me a perfect role that I would have missed on traditional job boards.' },
            { name: 'Raj M.', role: 'HR Manager', text: 'We reduced our screening time by 70% using the automatic candidate ranking feature.' },
            { name: 'Ananya K.', role: 'Data Analyst', text: 'The missing skills suggestions helped me improve my resume and land more interviews.' },
          ].map((t) => (
            <div key={t.name} className="glass-card">
              <p className="text-sm text-slate-300 italic mb-4">"{t.text}"</p>
              <div className="text-sm font-bold text-slate-100">{t.name}</div>
              <div className="text-xs text-slate-500">{t.role}</div>
            </div>
          ))}
        </div>
      </section> */}

      {/* ── CTA ───────────────────────────────────── */}
      <section className="max-w-4xl mx-auto px-6 py-20 text-center">
        <div className="glass-card !py-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Find Your <span className="gradient-text">Perfect Match?</span>
          </h2>
          <p className="text-slate-400 mb-8 max-w-lg mx-auto">
            Join thousands of job seekers and recruiters using AI-powered matching.
          </p>
          <Link to="/register" className="btn-primary text-base !py-3.5 !px-10">
            Get Started Now
          </Link>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────── */}
      <footer className="border-t border-slate-800 py-8 text-center">
        <p className="text-xs text-slate-600">
          © 2026 MatchAI — AI-Enabled Employment Matching Platform | Final Year BE Project
        </p>
      </footer>
    </div>
  );
}
