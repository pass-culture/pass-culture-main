import { useEffect } from 'react'

export default function useOnClickOrFocusOutside(ref, handler) {
  useEffect(() => {
    const listener = event => {
      if (!ref.current || ref.current.contains(event.target)) {
        return
      }
      handler(event)
    }

    document.addEventListener('mousedown', listener)
    document.addEventListener('focusin', listener)
    document.addEventListener('touchstart', listener)

    return () => {
      document.removeEventListener('mousedown', listener)
      document.removeEventListener('focusin', listener)
      document.removeEventListener('touchstart', listener)
    }
  }, [ref, handler])
}
