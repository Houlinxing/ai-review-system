export default function CommentsList({ comments }) {
  return (
    <div className="card" style={{ marginTop: 22 }}>
      <div className="section-title">Comments Stream</div>
      {comments.length === 0 ? (
        <p style={{ opacity: 0.4, fontSize: 14 }}>No comments yet. Search a topic above.</p>
      ) : (
        comments.map(comment => (
          <div className="comment" key={comment.id}>
            <div className="comment-content">{comment.content}</div>
            <div className="comment-meta">
              <span>{comment.platform}</span>
              <span>{comment.sentiment_label}</span>
              <span className={comment.sentiment >= 0 ? "positive" : "negative"}>
                {comment.sentiment?.toFixed(2)}
              </span>
              {comment.like_count > 0 && (
                <span>👍 {comment.like_count}</span>
              )}
            </div>
          </div>
        ))
      )}
    </div>
  )
}