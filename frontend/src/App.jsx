import { useState, useEffect } from "react"
import axios from "axios"
import SearchBar     from "./components/SearchBar"
import SearchHistory from "./components/SearchHistory"
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
  const [history,  setHistory]  = useState([])   
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  useEffect(() => {
    document.body.className = darkMode ? "dark" : ""
  }, [darkMode])

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API}/topics`)
      setHistory(res.data.data)
    } catch (err) {
      console.warn("获取搜索历史失败:", err)
    }
  }

  const loadResults = async (t) => {
    const [statsRes, commentsRes, summaryRes] = await Promise.all([
      axios.get(`${API}/stats/${t}`),
      axios.get(`${API}/comments?topic=${t}`),
      axios.get(`${API}/summary/${t}`),
    ])
    setStats(statsRes.data.data)
    setComments(commentsRes.data)
    setSummary(summaryRes.data.data.summary)
  }

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

      await loadResults(topic.trim())
      fetchHistory()   // 搜索完刷新历史列表

    } catch (err) {
      console.error("搜索失败:", err)
    } finally {
      setLoading(false)
    }
  }

  // 点击历史记录：直接读缓存，不重新抓取
  const selectHistoryTopic = async (t) => {
    setTopic(t)
    setLoading(true)
    setSummary(null)
    setStats(null)
    setComments([])
    try {
      await loadResults(t)
    } catch (err) {
      console.error("加载历史记录失败:", err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="layout">
      <SearchHistory
        topics={history}
        onSelect={selectHistoryTopic}
        currentTopic={topic}
        onDeleted={fetchHistory}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

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
            <SentimentChart comments={comments} topic={topic} darkMode={darkMode} />
          </>
        )}

        <CommentsList comments={comments} darkMode={darkMode} />

      </div>
    </div>
  )
}