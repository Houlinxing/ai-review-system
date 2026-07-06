import { useState, useEffect } from "react"
import axios from "axios"
import {
  BarChart, Bar,
  PieChart, Pie, Cell,
  LineChart, Line,
  XAxis, YAxis, Tooltip,
  ResponsiveContainer, Legend
} from "recharts"

const COLORS = {
  Positive: "#22c55e",
  Neutral:  "#94a3b8",
  Negative: "#ef4444",
}

export default function SentimentChart({ comments, topic, darkMode }) {
  // 柱状图 + 饼图数据
  const buckets = [
    { name: "Positive", value: comments.filter(c => c.sentiment >  0.3).length },
    { name: "Neutral",  value: comments.filter(c => c.sentiment >= -0.3 && c.sentiment <= 0.3).length },
    { name: "Negative", value: comments.filter(c => c.sentiment < -0.3).length },
  ]

  const tooltipStyle = {
    backgroundColor: darkMode ? "#1f1f22" : "#ffffff",
    border: "1px solid rgba(0,0,0,0.06)",
    borderRadius: 12,
    color: darkMode ? "#fff" : "#111",
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 22 }}>

      {/* 第一行：柱状图 + 饼图 */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 22 }}>

        {/* 柱状图 */}
        <div className="card">
          <div className="section-title">Sentiment Distribution</div>
          <div style={{ width: "100%", height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={buckets}>
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                  {buckets.map((entry) => (
                    <Cell key={entry.name} fill={COLORS[entry.name]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 饼图 */}
        <div className="card">
          <div className="section-title">Sentiment Ratio</div>
          <div style={{ width: "100%", height: 260 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={buckets}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}   // 环形图，中间空心更现代
                  outerRadius={100}
                  dataKey="value"
                  label={({ name, percent }) =>
                    `${name} ${(percent * 100).toFixed(0)}%`
                  }
                  labelLine={false}
                >
                  {buckets.map((entry) => (
                    <Cell key={entry.name} fill={COLORS[entry.name]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* 第二行：趋势折线图 */}
      <TrendChart topic={topic} darkMode={darkMode} tooltipStyle={tooltipStyle} />

    </div>
  )
}

function TrendChart({ topic, darkMode, tooltipStyle }) {
  const [trendData, setTrendData] = useState([])

  useEffect(() => {
    if (!topic) return
    axios.get(`http://127.0.0.1:8000/trend/${topic}`)
      .then(res => setTrendData(res.data.data ?? []))
      .catch(() => setTrendData([]))
  }, [topic])

  if (trendData.length < 2) return null  // 数据点太少不显示

  return (
    <div className="card">
      <div className="section-title">Sentiment Trend Over Time</div>
      <div style={{ width: "100%", height: 260 }}>
        <ResponsiveContainer>
          <LineChart data={trendData}>
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11 }}
              tickFormatter={d => d.slice(5)}  // 只显示月-日
            />
            <YAxis
              domain={[-1, 1]}
              tick={{ fontSize: 11 }}
              tickFormatter={v => v.toFixed(1)}
            />
            <Tooltip
              contentStyle={tooltipStyle}
              formatter={(value) => [value.toFixed(3), "Avg Sentiment"]}
            />
            <Line
              type="monotone"
              dataKey="avg_sentiment"
              stroke="#6366f1"
              strokeWidth={2}
              dot={{ r: 4, fill: "#6366f1" }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}