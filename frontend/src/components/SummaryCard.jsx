export default function SummaryCard({ summary }) {
  if (!summary) return null

  const verdictStyle = {
    "推荐":   { bg: "rgba(34,197,94,0.12)",  color: "#16a34a", border: "rgba(34,197,94,0.3)"  },
    "不推荐": { bg: "rgba(239,68,68,0.12)",  color: "#dc2626", border: "rgba(239,68,68,0.3)"  },
    "中立":   { bg: "rgba(148,163,184,0.12)", color: "#64748b", border: "rgba(148,163,184,0.3)" },
  }

  const vs = verdictStyle[summary.verdict] ?? verdictStyle["中立"]

  return (
    <div className="card" style={{ marginBottom: 22 }}>
      <div className="section-title">AI Summary</div>

      {/* 推荐徽章 + 一句话理由 */}
      <div style={{ display: "flex", alignItems: "center", gap: 12,
                    marginBottom: 16, paddingBottom: 16,
                    borderBottom: "1px solid rgba(128,128,128,0.12)" }}>
        <span style={{
          background: vs.bg, color: vs.color,
          border: `1px solid ${vs.border}`,
          borderRadius: 8, padding: "4px 14px",
          fontSize: 13, fontWeight: 600, whiteSpace: "nowrap"
        }}>
          {summary.verdict}
        </span>
        <p style={{ margin: 0, fontSize: 14, opacity: 0.75 }}>
          {summary.verdict_reason}
        </p>
      </div>

      {/* 综合总结 */}
      {summary.summary && (
        <p style={{ fontSize: 14, lineHeight: 1.8, marginBottom: 18, opacity: 0.82 }}>
          {summary.summary}
        </p>
      )}

      {/* 优点 / 缺点 两栏 */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
        <SubCard title="优点" items={summary.pros}  icon="✓" color="#16a34a" />
        <SubCard title="缺点" items={summary.cons}  icon="✗" color="#dc2626" />
      </div>

      {/* 实用建议 */}
      {summary.tips?.length > 0 && (
        <SubCard title="实用建议" items={summary.tips} icon="→" color="#2563eb" />
      )}
    </div>
  )
}

function SubCard({ title, items, icon, color }) {
  if (!items?.length) return null
  return (
    <div style={{
      background: "rgba(128,128,128,0.05)",
      border: "1px solid rgba(128,128,128,0.1)",
      borderRadius: 8, padding: 14
    }}>
      <p style={{ fontSize: 11, letterSpacing: 1, textTransform: "uppercase",
                  opacity: 0.5, margin: "0 0 10px" }}>{title}</p>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {items.map((item, i) => (
          <div key={i} style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
            <span style={{ color, fontWeight: 700, fontSize: 13, marginTop: 1 }}>{icon}</span>
            <span style={{ fontSize: 13, lineHeight: 1.5 }}>{item}</span>
          </div>
        ))}
      </div>
    </div>
  )
}