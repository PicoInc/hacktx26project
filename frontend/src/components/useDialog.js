import { useEffect, useRef } from 'react'

// Drives a native <dialog> from React state: showModal() gives focus trapping, Esc and a backdrop.
// Spread the returned props onto the <dialog>; keep its padding on an inner element so a click
// on the dialog itself can only mean the backdrop.
export default function useDialog(open, onClose) {
  const ref = useRef(null)

  useEffect(() => {
    const dialog = ref.current
    if (!dialog) return
    if (open && !dialog.open) dialog.showModal()
    if (!open && dialog.open) dialog.close()
  }, [open])

  return {
    ref,
    onCancel: (event) => {
      event.preventDefault() // Esc: let React state close it, so state and DOM never disagree
      onClose()
    },
    onClick: (event) => {
      if (event.target === event.currentTarget) onClose()
    },
  }
}
