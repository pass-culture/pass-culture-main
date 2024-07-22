import { RefObject, useEffect, useState } from 'react'

// Hook that return whether an element is visible or not in viewport
export const useIsElementVisible = (
  elementWatched: RefObject<Element>,
  obeserverOptions?: IntersectionObserverInit
) => {
  const [isElementVisible, setIsElementVisible] = useState(false)
  const [hasVisibilityChanged, setHasVisibilityChanged] = useState(false)

  /* istanbul ignore next */
  const callback = (entries: IntersectionObserverEntry[]) => {
    const [entry] = entries
    setHasVisibilityChanged(entry?.isIntersecting !== isElementVisible)
    setIsElementVisible(entry?.isIntersecting ?? false)
  }

  const observer = new IntersectionObserver(callback, obeserverOptions)

  useEffect(() => {
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
  }, [elementWatched, observer])

  return [isElementVisible, hasVisibilityChanged]
}
