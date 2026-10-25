export default function ScoreBadge({ score }) {
  const level =
    score >= 60 ? 'score-high' :
    score >= 35 ? 'score-medium' : 'score-low';

  return (
    <span className={`score-badge ${level}`}>
      {score}%
    </span>
  );
}
