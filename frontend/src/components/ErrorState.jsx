// A failed request: what went wrong and a way to try again
export default function ErrorState({ title, onRetry }) {
  return (
    <div className="error-state" role="alert">
      <p className="error-title">{title}</p>
      <button type="button" className="btn btn-outline" onClick={onRetry}>
        Retry
      </button>
    </div>
  )
}
