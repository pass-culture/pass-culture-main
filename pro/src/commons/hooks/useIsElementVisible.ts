import { type MutableRefObject, useEffect, useRef, useState } from 'react'

// Hook that return whether an element is visible or not in viewport
export const useIsElementVisible = (
  elementWatched: MutableRefObject<HTMLLIElement | HTMLDivElement | null>,
  observerOptions?: IntersectionObserverInit
) => {
  const [isElementVisible, setIsElementVisible] = useState(false)
  const [hasVisibilityChanged, setHasVisibilityChanged] = useState(false)

  const prevVisibilityRef = useRef<boolean | null>(null)

  useEffect(() => {
    const callback = (entries: IntersectionObserverEntry[]) => {
      const isVisible = entries[0].isIntersecting

      if (prevVisibilityRef.current !== null) {
        setHasVisibilityChanged(prevVisibilityRef.current !== isVisible)
      }

      prevVisibilityRef.current = isVisible
      setIsElementVisible(isVisible)
    }

    const observer = new IntersectionObserver(callback, observerOptions)
    const element = elementWatched.current

    if (element) {
      observer.observe(element)
    }

    return () => observer.disconnect()
  }, [elementWatched, observerOptions])

  return [isElementVisible, hasVisibilityChanged]
}
