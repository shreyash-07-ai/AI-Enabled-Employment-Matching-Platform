import { useEffect, useState } from 'react';
import { getMyApplications, getMatchAnalysis } from '../services/api';
import ScoreBadge from '../components/ScoreBadge';

export default function MyApplicationsPage() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    getMyApplications()
      .then((res) => { setApplications(res.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const showAnalysis = async (appId) => {
    try {
      const res = await getMatchAnalysis(appId);
      setAnalysis(res.data);
    } catch {
      alert('Could not load analysis');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <h1 className="text-2xl font-bold mb-1">My Applications</h1>
      <p className="text-slate-500 text-sm mb-8">Track your job applications and match scores</p>

      {/* Analysis Modal */}
      {analysis && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setAnalysis(null)}>
          <div className="glass-card max-w-lg w-full max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-slate-100">🎯 Match Analysis</h3>
              <button onClick={() => setAnalysis(null)} className="text-slate-500 hover:text-slate-300 text-xl">✕</button>
            </div>
            <div className="text-sm text-slate-400 mb-2">Job: <span className="text-slate-200 font-medium">{analysis.job_title}</span></div>
            
            <div className="grid grid-cols-3 gap-3 my-4">
              <div className="stat-card !p-3 text-center">
                <div className="text-lg font-bold text-indigo-400">{analysis.tfidf_score}%</div>
                <div className="text-[10px] text-slate-500">TF-IDF</div>
              </div>
              <div className="stat-card !p-3 text-center">
                <div className="text-lg font-bold text-violet-400">{analysis.bm25_score}%</div>
                <div className="text-[10px] text-slate-500">BM25</div>
              </div>
              <div className="stat-card !p-3 text-center">
                <div className="text-lg font-bold text-green-400">{analysis.sbert_score}%</div>
                <div className="text-[10px] text-slate-500">SBERT</div>
              </div>
            </div>

            <div className="text-center mb-4">
              <div className="text-3xl font-black gradient-text">{analysis.match_score_pct}%</div>
              <div className="text-xs text-slate-500">Combined Match Score</div>
            </div>

            <div className="mb-3">
              <div className="text-xs text-slate-500 mb-2">✅ Matched Skills</div>
              <div className="flex flex-wrap gap-1.5">
                {(analysis.matched_skills || []).map((s) => (
                  <span key={s} className="px-2 py-0.5 rounded-full bg-green-500/10 text-green-400 text-[11px] border border-green-500/20">{s}</span>
                ))}
                {(analysis.matched_skills || []).length === 0 && <span className="text-slate-600 text-xs">None</span>}
              </div>
            </div>

            <div className="mb-3">
              <div className="text-xs text-slate-500 mb-2">❌ Missing Skills</div>
              <div className="flex flex-wrap gap-1.5">
                {(analysis.missing_skills || []).map((s) => (
                  <span key={s} className="px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 text-[11px] border border-red-500/20">{s}</span>
                ))}
                {(analysis.missing_skills || []).length === 0 && <span className="text-slate-600 text-xs">All covered!</span>}
              </div>
            </div>

            {(analysis.suggestions || []).length > 0 && (
              <div>
                <div className="text-xs text-slate-500 mb-2">💡 Suggestions</div>
                <ul className="space-y-1">
                  {analysis.suggestions.map((s, i) => (
                    <li key={i} className="text-xs text-slate-400 pl-3 border-l-2 border-indigo-500/30">{s}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Applications List */}
      <div className="space-y-3">
        {applications.map((app) => (
          <div key={app.id} className="glass-card flex items-center justify-between">
            <div>
              <div className="text-sm font-bold text-slate-200">{app.job_title}</div>
              <div className="text-xs text-slate-500 mt-1">
                Applied {new Date(app.applied_at).toLocaleDateString()} •{' '}
                <span className={
                  app.status === 'SHORTLISTED' ? 'text-green-400' :
                  app.status === 'REJECTED' ? 'text-red-400' :
                  app.status === 'HIRED' ? 'text-blue-400' :
                  'text-slate-400'
                }>
                  {app.status}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <ScoreBadge score={Number(app.match_score_pct)} />
              <button onClick={() => showAnalysis(app.id)} className="text-xs text-indigo-400 hover:text-indigo-300">
                View Analysis
              </button>
            </div>
          </div>
        ))}
        {applications.length === 0 && (
          <p className="text-center text-slate-600 py-12">No applications yet. Browse jobs to get started!</p>
        )}
      </div>
    </div>
  );
}
