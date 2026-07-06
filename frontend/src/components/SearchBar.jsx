export default function SearchBar({ topic, setTopic, onSearch, loading }) {
  return (
    <div className="search-box">
      <input
        className="input"
        type="text"
        placeholder="Search topic..."
        value={topic}
        onChange={e => setTopic(e.target.value)}
        onKeyDown={e => e.key === "Enter" && !loading && onSearch()}
      />
      <button className="button" onClick={onSearch} disabled={loading}>
        {loading ? "Analyzing..." : "Analyze"}
      </button>
    </div>
  )
}