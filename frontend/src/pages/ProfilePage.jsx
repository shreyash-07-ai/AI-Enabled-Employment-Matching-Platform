import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { getJobSeekerProfile, updateJobSeekerProfile, getRecruiterProfile, updateRecruiterProfile } from '../services/api';

export default function ProfilePage() {
  const { user } = useAuth();
  const isSeeker = user?.role === 'JOB_SEEKER';
  const [form, setForm] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const fetcher = isSeeker ? getJobSeekerProfile : getRecruiterProfile;
    fetcher()
      .then((res) => { setForm(res.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSaved(false);
    try {
      const updater = isSeeker ? updateJobSeekerProfile : updateRecruiterProfile;
      await updater(form);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      alert('Failed to save: ' + JSON.stringify(err.response?.data || 'Error'));
    } finally {
      setSaving(false);
    }
  };

  const updateField = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="animate-fade-in max-w-2xl">
      <h1 className="text-2xl font-bold mb-1">My Profile</h1>
      <p className="text-slate-500 text-sm mb-8">
        {isSeeker ? 'Keep your profile updated for better matching' : 'Your company profile'}
      </p>

      {saved && (
        <div className="mb-4 p-3 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 text-sm">
          ✅ Profile saved successfully!
        </div>
      )}

      <form onSubmit={handleSave} className="glass-card space-y-5">
        {isSeeker ? (
          <>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Phone</label>
                <input className="input-field" placeholder="Phone number" value={form.phone || ''} onChange={updateField('phone')} />
              </div>
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Location</label>
                <input className="input-field" placeholder="City, Country" value={form.location || ''} onChange={updateField('location')} />
              </div>
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Education</label>
              <textarea className="input-field min-h-[80px]" placeholder="Your education background" value={form.education || ''} onChange={updateField('education')} />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Years of Experience</label>
              <input type="number" className="input-field" value={form.experience_years || 0} onChange={updateField('experience_years')} min="0" step="0.5" />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Skills (comma-separated)</label>
              <textarea className="input-field min-h-[80px]" placeholder="Python, React, Machine Learning..." value={form.skills || ''} onChange={updateField('skills')} />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Certifications</label>
              <textarea className="input-field" placeholder="AWS Certified, Google Analytics..." value={form.certifications || ''} onChange={updateField('certifications')} />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Projects</label>
              <textarea className="input-field min-h-[80px]" placeholder="Describe key projects..." value={form.projects || ''} onChange={updateField('projects')} />
            </div>
          </>
        ) : (
          <>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Company Name</label>
              <input className="input-field" placeholder="Your company" value={form.company_name || ''} onChange={updateField('company_name')} />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Company Website</label>
              <input className="input-field" placeholder="https://..." value={form.company_website || ''} onChange={updateField('company_website')} />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Your Position</label>
              <input className="input-field" placeholder="HR Manager" value={form.position || ''} onChange={updateField('position')} />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Phone</label>
              <input className="input-field" placeholder="Phone number" value={form.phone || ''} onChange={updateField('phone')} />
            </div>
          </>
        )}

        <button type="submit" className="btn-primary w-full" disabled={saving}>
          {saving ? 'Saving...' : 'Save Profile'}
        </button>
      </form>
    </div>
  );
}
