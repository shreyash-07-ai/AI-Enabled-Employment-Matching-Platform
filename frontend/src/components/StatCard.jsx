export default function StatCard({ icon, value, label, color = 'text-violet-400' }) {
  return (
    <div className="stat-card animate-fade-in">
      <div className="flex items-center gap-3 mb-2">
        <span className={`text-2xl ${color}`}>{icon}</span>
      </div>
      <div className={`stat-value ${color}`}>{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}
