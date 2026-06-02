import { useState, useEffect } from "react";
import axios from "axios";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

function App() {
  const [topic, setTopic] = useState("");
  const [stats, setStats] = useState(null);
  const [comments, setComments] = useState([]);
  const [summary, setSummary] = useState("");
  const [darkMode, setDarkMode] = useState(false);
  const [loading, setLoading] = useState(false);

  const sentimentData = [
    {
      name: "Positive",
      value: comments.filter((c) => c.sentiment > 0).length,
    },
    {
      name: "Neutral",
      value: comments.filter((c) => c.sentiment === 0).length,
    },
    {
      name: "Negative",
      value: comments.filter((c) => c.sentiment < 0).length,
    },
  ];

 const searchTopic = async () => {

  setLoading(true);

  try {

    const statsRes = await axios.get(
      `http://127.0.0.1:8000/stats/${topic}`
    );

    const commentsRes = await axios.get(
      `http://127.0.0.1:8000/comments?topic=${topic}`
    );

    const summaryRes = await axios.get(
      `http://127.0.0.1:8000/summary/${topic}`
    );

    setStats(statsRes.data);

    setComments(commentsRes.data);

    animateSummary(summaryRes.data.summary);

  } catch (error) {

    console.error(error);

  } finally {

    setLoading(false);

  }
};

const animateSummary = (text) => {

  if (!text || typeof text !== "string") {
    setSummary("No summary available");
    return;
  }

  setSummary("");

  let index = 0;

  const interval = setInterval(() => {

    setSummary((prev) =>
      prev + text[index]
    );

    index++;

    if (index >= text.length) {
      clearInterval(interval);
    }

  }, 18);
};

  useEffect(() => {
    document.body.style.background = darkMode
      ? "#0f0f10"
      : "#f5f5f7";

    document.body.style.transition =
      "background 0.35s ease";
  }, [darkMode]);

  return (
    <>
      <style>{`

        * {
          box-sizing: border-box;
        }

        body {
          margin: 0;
          font-family:
            Inter,
            -apple-system,
            BlinkMacSystemFont,
            "SF Pro Display",
            sans-serif;
          color: ${darkMode ? "#f5f5f5" : "#111"};
        }

        .app {
          min-height: 100vh;
          padding: 60px 8vw;
          background:
            ${darkMode
              ? "linear-gradient(to bottom, #0f0f10, #151517)"
              : "linear-gradient(to bottom, #ffffff, #f3f4f6)"};

          transition: all 0.35s ease;
        }

        .topbar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 70px;
        }

        .logo {
          font-size: 1.9rem;
          font-weight: 700;
          letter-spacing: -1px;
        }

        .theme-button {
          border: none;
          background:
            ${darkMode ? "#1f1f22" : "#ffffff"};
          color:
            ${darkMode ? "#fff" : "#111"};

          padding: 10px 18px;
          border-radius: 14px;
          cursor: pointer;
          font-size: 0.95rem;

          box-shadow:
            ${darkMode
              ? "0 0 0 rgba(0,0,0,0)"
              : "0 6px 24px rgba(0,0,0,0.06)"};

          transition: all 0.25s ease;
        }

        .theme-button:hover {
          transform: scale(1.04);
        }

        .hero {
          margin-bottom: 55px;
        }

        .hero-title {
          font-size: clamp(3rem, 6vw, 5.5rem);
          font-weight: 800;
          letter-spacing: -4px;
          line-height: 1;
          margin-bottom: 20px;
        }

        .hero-subtitle {
          max-width: 760px;
          line-height: 1.8;
          color:
            ${darkMode
              ? "rgba(255,255,255,0.6)"
              : "rgba(0,0,0,0.55)"};

          font-size: 1.05rem;
        }

        .search-box {
          display: flex;
          gap: 16px;
          margin-bottom: 55px;
          flex-wrap: wrap;
        }

        .input {
          flex: 1;
          min-width: 280px;

          border: none;

          background:
            ${darkMode ? "#1b1b1d" : "#ffffff"};

          color:
            ${darkMode ? "#fff" : "#111"};

          padding: 18px 22px;

          border-radius: 18px;

          font-size: 1rem;

          outline: none;

          box-shadow:
            ${darkMode
              ? "0 0 0 rgba(0,0,0,0)"
              : "0 8px 30px rgba(0,0,0,0.06)"};

          transition: all 0.25s ease;
        }

        .input:focus {
          transform: translateY(-1px);
        }

        .button {
          border: none;

          background:
            ${darkMode ? "#ffffff" : "#111111"};

          color:
            ${darkMode ? "#111" : "#fff"};

          padding: 18px 26px;

          border-radius: 18px;

          cursor: pointer;

          font-weight: 600;

          transition: all 0.25s ease;
        }

        .button:hover {
          transform: scale(1.04);
        }

        .stats-grid {
          display: grid;

          grid-template-columns:
            repeat(auto-fit, minmax(220px, 1fr));

          gap: 22px;

          margin-bottom: 28px;
        }

        .card {
          background:
            ${darkMode
              ? "rgba(255,255,255,0.04)"
              : "rgba(255,255,255,0.8)"};

          backdrop-filter: blur(12px);

          border:
            1px solid
            ${darkMode
              ? "rgba(255,255,255,0.05)"
              : "rgba(0,0,0,0.04)"};

          border-radius: 24px;

          padding: 28px;

          transition:
            transform 0.28s ease,
            box-shadow 0.28s ease;

          box-shadow:
            ${darkMode
              ? "none"
              : "0 10px 40px rgba(0,0,0,0.06)"};
        }

        .card:hover {
          transform:
            translateY(-4px)
            scale(1.01);

          box-shadow:
            ${darkMode
              ? "0 10px 40px rgba(0,0,0,0.2)"
              : "0 16px 40px rgba(0,0,0,0.08)"};
        }

        .label {
          font-size: 0.82rem;

          text-transform: uppercase;

          letter-spacing: 1px;

          margin-bottom: 14px;

          color:
            ${darkMode
              ? "rgba(255,255,255,0.5)"
              : "rgba(0,0,0,0.45)"};
        }

        .value {
          font-size: 2.1rem;
          font-weight: 700;
          letter-spacing: -1px;
        }

        .section-title {
          font-size: 0.85rem;

          letter-spacing: 1.6px;

          text-transform: uppercase;

          margin-bottom: 20px;

          color:
            ${darkMode
              ? "rgba(255,255,255,0.45)"
              : "rgba(0,0,0,0.45)"};
        }

        .summary-text {
          line-height: 1.9;

          color:
            ${darkMode
              ? "rgba(255,255,255,0.82)"
              : "rgba(0,0,0,0.75)"};

          font-size: 1rem;
        }

        .comments-wrapper {
          margin-top: 10px;
        }

        .comment {
          padding: 24px 0;

          border-bottom:
            1px solid
            ${darkMode
              ? "rgba(255,255,255,0.05)"
              : "rgba(0,0,0,0.05)"};

          transition: all 0.25s ease;
        }

        .comment:hover {
          transform: translateX(4px);
        }

        .comment-content {
          font-size: 1.05rem;
          line-height: 1.8;
          margin-bottom: 12px;
        }

        .comment-meta {
          display: flex;
          gap: 18px;
          flex-wrap: wrap;

          font-size: 0.82rem;

          color:
            ${darkMode
              ? "rgba(255,255,255,0.45)"
              : "rgba(0,0,0,0.45)"};
        }

        .positive {
          color: #22c55e;
        }

        .negative {
          color: #ef4444;
        }

      `}</style>

      <div className="app">

        <div className="topbar">

          <div className="logo">
            AI Review
          </div>

          <button
            className="theme-button"
            onClick={() =>
              setDarkMode(!darkMode)
            }
          >
            {darkMode ? "Light" : "Dark"}
          </button>

        </div>

        <div className="hero">

          <div className="hero-title">
            AI Review Dashboard
          </div>

          <div className="hero-subtitle">
            Aggregate opinions from social media,
            analyze sentiment with AI,
            and visualize global user feedback
            through a clean modern dashboard.
          </div>

        </div>

        <div className="search-box">

          <input
            className="input"
            type="text"
            placeholder="Search topic..."
            value={topic}
            onChange={(e) =>
              setTopic(e.target.value)
            }
          />

          <button
            className="button"
            onClick={searchTopic}
            disabled={loading}
          >
            {loading ? "Analyzing..." : "Analyze"}
          </button>

        </div>

        {stats && (
          <>
            <div className="stats-grid">

              <div className="card">
                <div className="label">
                  Topic
                </div>

                <div className="value">
                  {stats.topic}
                </div>
              </div>

              <div className="card">
                <div className="label">
                  Comments
                </div>

                <div className="value">
                  {stats.total_comments}
                </div>
              </div>

              <div className="card">
                <div className="label">
                  Sentiment
                </div>

                <div className="value">
                  {stats.average_sentiment?.toFixed(2)}
                </div>
              </div>

            </div>

            {summary && (
              <div className="card">

                <div className="section-title">
                  AI Summary
                </div>

                <div className="summary-text">
                  {summary}
                </div>

              </div>
            )}

            <div className="card">

              <div className="section-title">
                Sentiment Analysis
              </div>

              <div
                style={{
                  width: "100%",
                  height: 320,
                }}
              >
                <ResponsiveContainer>

                  <BarChart data={sentimentData}>

                    <XAxis dataKey="name" />

                    <YAxis />

                    <Tooltip
                      contentStyle={{
                        backgroundColor:
                          darkMode
                            ? "#1f1f22"
                            : "#ffffff",

                        border:
                          "1px solid rgba(0,0,0,0.06)",

                        borderRadius: "12px",

                        color:
                          darkMode
                            ? "#fff"
                            : "#111",
                      }}

                      labelStyle={{
                        color:
                          darkMode
                            ? "#fff"
                            : "#111",
                      }}

                      itemStyle={{
                        color:
                          darkMode
                            ? "#fff"
                            : "#111",
                      }}
                    />

                    <Bar
                      dataKey="value"
                      radius={[10, 10, 0, 0]}
                    />

                  </BarChart>

                </ResponsiveContainer>
              </div>

            </div>
          </>
        )}

        <div
          className="card"
          style={{
            marginTop: "28px",
          }}
        >

          <div className="section-title">
            Comments Stream
          </div>

          <div className="comments-wrapper">

            {comments.map((comment) => (
              <div
                className="comment"
                key={comment.id}
              >

                <div className="comment-content">
                  {comment.content}
                </div>

                <div className="comment-meta">

                  <span>
                    {comment.platform}
                  </span>

                  <span>
                    {comment.region}
                  </span>

                  <span
                    className={
                      comment.sentiment >= 0
                        ? "positive"
                        : "negative"
                    }
                  >
                    sentiment:
                    {" "}
                    {comment.sentiment}
                  </span>

                </div>

              </div>
            ))}

          </div>

        </div>

      </div>
    </>
  );
}

export default App;