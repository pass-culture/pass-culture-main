import { RefObject, useEffect, useState } from 'react'

// Hook that return whether an element is visible or not in viewport
export const useIsElementVisible = (
  elementWatched: RefObject<Element>,
  observerOptions?: IntersectionObserverInit
) => {
  const [isElementVisible, setIsElementVisible] = useState(false)
  const [hasVisibilityChanged, setHasVisibilityChanged] = useState(false)

  useEffect(() => {
    /* istanbul ignore next */
    const callback = (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries
      setHasVisibilityChanged(entry.isIntersecting !== isElementVisible)
      setIsElementVisible(entry.isIntersecting)
    }
    const observer = new IntersectionObserver(callback, observerOptions)
    const element = elementWatched.current
    if (element) {
      observer.observe(element)
    }

    return () => {
      if (element) {
        observer.unobserve(element)
        observer.disconnect()
      }
    }
  }, [elementWatched, isElementVisible, observerOptions])

  return [isElementVisible, hasVisibilityChanged]
}
