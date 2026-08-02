import { useState, useEffect } from "react"
import axios from "axios"
import SearchBar     from "./components/SearchBar"
import StatsGrid     from "./components/StatsGrid"
import SummaryCard   from "./components/SummaryCard"
import SentimentChart from "./components/SentimentChart"
import CommentsList  from "./components/CommentsList"
import "./styles/global.css"

const API = "http://127.0.0.1:8000"

export default function App() {
  const [topic,    setTopic]    = useState("")
  const [stats,    setStats]    = useState(null)
  const [comments, setComments] = useState([])
  const [summary,  setSummary]  = useState(null)
  const [darkMode, setDarkMode] = useState(false)
  const [loading,  setLoading]  = useState(false)

  useEffect(() => {
    document.body.className = darkMode ? "dark" : ""
  }, [darkMode])

  const searchTopic = async () => {
    if (!topic.trim()) return
    setLoading(true)
    setSummary(null)
    setStats(null)
    setComments([])

    try {
       await Promise.all([
        axios.post(`${API}/crawl/youtube/keyword`, {
          keyword: topic.trim(),
          max_videos: 3,
          max_results_per_video: 20,
        }).catch(err => console.warn("YouTube抓取失败:", err)),

        axios.post(`${API}/crawl/bilibili/keyword`, {
          keyword: topic.trim(),
          max_videos: 3,
          max_results_per_video: 20,
        }).catch(err => console.warn("B站抓取失败:", err)),
      ])

      const [statsRes, commentsRes, summaryRes] = await Promise.all([
        axios.get(`${API}/stats/${topic.trim()}`),
        axios.get(`${API}/comments?topic=${topic.trim()}`),
        axios.get(`${API}/summary/${topic.trim()}`),
      ])

      setStats(statsRes.data.data)
      setComments(commentsRes.data)
      setSummary(summaryRes.data.data.summary)

    } catch (err) {
      console.error("搜索失败:", err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={`app ${darkMode ? "dark" : ""}`}>

      <div className="topbar">
        <div className="logo">AI Review</div>
        <button className="theme-btn" onClick={() => setDarkMode(!darkMode)}>
          {darkMode ? "Light" : "Dark"}
        </button>
      </div>

      <div className="hero">
        <h1 className="hero-title">AI Review Dashboard</h1>
        <p className="hero-subtitle">
          Aggregate opinions from social media, analyze sentiment with AI,
          and visualize global user feedback through a clean modern dashboard.
        </p>
      </div>

      <SearchBar
        topic={topic}
        setTopic={setTopic}
        onSearch={searchTopic}
        loading={loading}
      />

      {stats && (
        <>
          <StatsGrid stats={stats} />
          {summary && <SummaryCard summary={summary} />}
          <SentimentChart comments={comments} 
          topic={topic}  
          darkMode={darkMode} />
        </>
      )}

      <CommentsList comments={comments} darkMode={darkMode} />

    </div>
  )
}