export default function StatsGrid({ stats }) {
  const fontSize = stats.topic?.length > 20 ? "1.2rem"
                 : stats.topic?.length > 10 ? "1.6rem"
                 : "2.1rem"

  return (
    <div className="stats-grid">

      <div className="card stats-card">
        <div className="label">Topic</div>
        <div className="value" style={{
          fontSize,
          lineHeight: 1.3,
          wordBreak: "break-word",
        }}>
          {stats.topic}
        </div>
      </div>

      <div className="card stats-card">
        <div className="label">Comments</div>
        <div className="value">{stats.total_comments}</div>
      </div>

      <div className="card stats-card">
        <div className="label">Sentiment</div>
        <div className="value">{stats.average_sentiment?.toFixed(2)}</div>
      </div>

    </div>
  )
}