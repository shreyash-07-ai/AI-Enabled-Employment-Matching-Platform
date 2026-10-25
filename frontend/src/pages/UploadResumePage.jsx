import { useState } from 'react';
import { uploadResume, getMyResumes } from '../services/api';
import { FiUploadCloud, FiFile, FiCheck } from 'react-icons/fi';
import { useEffect } from 'react';

export default function UploadResumePage() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [resumes, setResumes] = useState([]);

  useEffect(() => {
    getMyResumes()
      .then((res) => setResumes(res.data))
      .catch(() => {});
  }, [success]);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setSuccess(false);
    try {
      const formData = new FormData();
      formData.append('file', file);
      await uploadResume(formData);
      setSuccess(true);
      setFile(null);
    } catch (err) {
      alert('Upload failed: ' + (err.response?.data?.error || 'Unknown error'));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="animate-fade-in max-w-2xl">
      <h1 className="text-2xl font-bold mb-1">Upload Resume</h1>
      <p className="text-slate-500 text-sm mb-8">Upload your resume to get AI-powered job matching</p>

      <form onSubmit={handleUpload}>
        <div
          className={`glass-card text-center py-16 cursor-pointer transition-all ${
            file ? 'border-indigo-500/30' : 'border-dashed border-2 border-slate-700'
          }`}
          onClick={() => document.getElementById('resume-file').click()}
        >
          {success ? (
            <>
              <FiCheck className="text-4xl text-green-400 mx-auto mb-3" />
              <div className="text-green-400 font-medium">Resume uploaded successfully!</div>
              <div className="text-xs text-slate-500 mt-1">AI is now extracting skills and information</div>
            </>
          ) : file ? (
            <>
              <FiFile className="text-4xl text-indigo-400 mx-auto mb-3" />
              <div className="text-slate-200 font-medium">{file.name}</div>
              <div className="text-xs text-slate-500 mt-1">{(file.size / 1024).toFixed(1)} KB — Click to change</div>
            </>
          ) : (
            <>
              <FiUploadCloud className="text-4xl text-slate-600 mx-auto mb-3" />
              <div className="text-slate-400">Click to upload or drag & drop</div>
              <div className="text-xs text-slate-600 mt-1">PDF, DOCX (Max 10MB)</div>
            </>
          )}
          <input
            id="resume-file"
            type="file"
            accept=".pdf,.docx,.doc"
            className="hidden"
            onChange={(e) => { setFile(e.target.files[0]); setSuccess(false); }}
          />
        </div>

        {file && !success && (
          <button type="submit" className="btn-primary w-full mt-4" disabled={uploading}>
            {uploading ? 'Uploading & Parsing...' : 'Upload Resume'}
          </button>
        )}
      </form>

      {/* Previous Resumes */}
      {resumes.length > 0 && (
        <div className="mt-10">
          <h2 className="text-sm font-semibold text-slate-300 mb-4">📄 Your Resumes</h2>
          <div className="space-y-2">
            {resumes.map((r) => (
              <div key={r.id} className="flex items-center justify-between p-3 rounded-xl bg-slate-800/40 border border-slate-700/30">
                <div>
                  <div className="text-sm text-slate-200">{r.file?.split('/').pop()}</div>
                  <div className="text-xs text-slate-500">{new Date(r.uploaded_at).toLocaleDateString()}</div>
                </div>
                {r.extracted_skills && (
                  <div className="text-xs text-slate-500 max-w-xs truncate">
                    {r.extracted_skills}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
