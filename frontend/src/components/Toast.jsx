import { useEffect } from 'react'

const DISMISS_MS = 4000

// Bottom-center confirmation; renders nothing until there's a message
export default function Toast({ message, onDismiss }) {
  useEffect(() => {
    if (!message) return
    const timer = setTimeout(onDismiss, DISMISS_MS)
    return () => clearTimeout(timer)
  }, [message, onDismiss])

  if (!message) return null

  return (
    <div className="toast" role="status">
      <span>{message}</span>
      <button type="button" className="toast-close" aria-label="Dismiss" onClick={onDismiss}>
        ×
      </button>
    </div>
  )
}
