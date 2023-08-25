import { RefObject, useEffect, useState } from 'react'

// Hook that return whether an element is visible or not in viewport
const useIsElementVisible = (elementWatched: RefObject<Element>) => {
  const [isElementVisible, setIsElementVisible] = useState(false)

  /* istanbul ignore next */
  const callback = (entries: IntersectionObserverEntry[]) => {
    const [entry] = entries
    setIsElementVisible(entry.isIntersecting)
  }

  const observer = new IntersectionObserver(callback)

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

  return isElementVisible
}

export default useIsElementVisible
