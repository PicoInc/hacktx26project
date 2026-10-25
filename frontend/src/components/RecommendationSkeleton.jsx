// Placeholder cards in the same layout as RecommendationList (three horizontal cards, stacked)
function SkeletonCard({ top }) {
  return (
    <div className={top ? 'card rec-card rec-card-top skeleton-card' : 'card rec-card skeleton-card'}>
      <div className="rec-main">
        <div className="skeleton skeleton-badge" />
        <div className="skeleton skeleton-title" />
        <div className="skeleton skeleton-price" />
        <div className="skeleton skeleton-line" />
        <div className="skeleton skeleton-line short" />
      </div>
      <div className="rec-body">
        <div className="skeleton skeleton-line" />
        <div className="skeleton skeleton-line" />
        <div className="skeleton skeleton-line short" />
        <div className="skeleton skeleton-button" />
      </div>
    </div>
  )
}

export default function RecommendationSkeleton() {
  return (
    <div className="rec-list" aria-busy="true" aria-live="polite">
      <span className="visually-hidden">Finding your best move…</span>
      <SkeletonCard top />
      <SkeletonCard />
      <SkeletonCard />
    </div>
  )
}
