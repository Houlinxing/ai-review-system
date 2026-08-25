import axios from "axios"
import { formatChromeStyle } from '../utils/formatDate'
const API = "http://127.0.0.1:8000"
function SidebarIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2.5" y="3" width="15" height="14" rx="2.5" stroke="currentColor" strokeWidth="1.4"/>
      <line x1="8" y1="3.5" x2="8" y2="16.5" stroke="currentColor" strokeWidth="1.4"/>
    </svg>
  )
}
function groupByDate(topics) {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)
  const week = new Date(today)
  week.setDate(today.getDate() - 7)
  const groups = { "今天": [], "昨天": [], "7天内": [], "更早": [] }
  topics.forEach(item => {
    const d = new Date(item.last_searched_at)
    const dDate = new Date(d.getFullYear(), d.getMonth(), d.getDate())
    if (dDate.getTime() === today.getTime()) groups["今天"].push(item)
    else if (dDate.getTime() === yesterday.getTime()) groups["昨天"].push(item)
    else if (dDate >= week) groups["7天内"].push(item)
    else groups["更早"].push(item)
  })
  return Object.entries(groups).filter(([, list]) => list.length > 0)
}
export default function SearchHistory({ topics, onSelect, currentTopic, onDeleted, collapsed, onToggleCollapse }) {
  const grouped = groupByDate(topics)
  const handleDelete = async (e, topic) => {
    e.stopPropagation()
    if (!confirm(`删除「${topic}」的所有数据？此操作无法撤销。`)) return
    try {
      await axios.delete(`${API}/topics/${encodeURIComponent(topic)}`)
      onDeleted()
    } catch (err) {
      console.error("删除失败:", err)
    }
  }
  const handleClearAll = async () => {
    if (!confirm(`清空全部 ${topics.length} 条搜索历史？此操作无法撤销。`)) return
    try {
      await axios.delete(`${API}/topics`)
      onDeleted()
    } catch (err) {
      console.error("清空失败:", err)
    }
  }
  if (collapsed) {
    return (
      <div className="sidebar sidebar-collapsed">
        <button className="sidebar-toggle" onClick={onToggleCollapse} title="展开历史记录">
          <SidebarIcon />
        </button>
      </div>
    )
  }
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <button className="sidebar-toggle" onClick={onToggleCollapse} title="收起历史记录">
          <SidebarIcon />
        </button>
        <div className="sidebar-title">最近搜索</div>
      </div>
      {topics.length === 0 ? (
        <p style={{ opacity: 0.4, fontSize: 13, padding: "0 4px" }}>暂无搜索记录</p>
      ) : (
        <div className="history-scroll">
          {grouped.map(([label, items]) => (
            <div key={label} className="history-group">
              <div className="history-group-label">{label}</div>
              {items.map(item => (
                <div
                  key={item.topic}
                  className={`history-item ${item.topic === currentTopic ? "active" : ""}`}
                  onClick={() => onSelect(item.topic)}
                >
                  <div className="history-row">
                    <div className="history-topic">{item.topic}</div>
                    <button
                      className="history-delete"
                      onClick={(e) => handleDelete(e, item.topic)}
                      title="删除"
                    >
                      ×
                    </button>
                  </div>
                  <div className="history-date">{formatChromeStyle(item.last_searched_at)}</div>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
      {topics.length > 0 && (
        <button className="history-clear-all" onClick={handleClearAll}>
          清空全部历史
        </button>
      )}
    </div>
  )
}