import { type RefObject, useEffect } from 'react'

export function useOnClickOrFocusOutside(
  ref: RefObject<HTMLElement | null>,
  handler: (event: Event) => void
) {
  useEffect(() => {
    const listener: EventListener = (event) => {
      if (!ref.current || ref.current.contains(event.target as Node)) {
        return
      }
      // For focusin events, ignore when focus moves to an ancestor of the
      // container (e.g. <main tabIndex={-1}>). This happens in JSDOM when
      // clicking a non-focusable child: focus lands on the nearest focusable
      // ancestor instead of the associated <input>. In real browsers this
      // isn't an issue, but the guard is valid either way — focus moving to a
      // parent shouldn't count as "outside".
      if (
        event.type === 'focusin' &&
        (event.target as Node).contains(ref.current)
      ) {
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
