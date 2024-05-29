import { useEffect, RefObject } from 'react'

export function useOnClickOrFocusOutside(
  ref: RefObject<HTMLElement>,
  handler: (event: Event) => void
) {
  useEffect(() => {
    const listener: EventListener = (event) => {
      if (!ref.current || ref.current.contains(event.target as Node)) {
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
