import { useRef, useEffect } from 'react'
import { useLocation } from 'react-router-dom'

export const useFocus = (): void => {
  const location = useLocation()
  const previousLocation = useRef(location);
  const isInternalNavigation = previousLocation.current.pathname !== location.pathname;
  console.log('isInternalNavigation', isInternalNavigation, previousLocation.current.pathname, location.pathname)

  useEffect(() => {
    previousLocation.current = location;
  }, [location]);

  useEffect(() => {
    /* istanbul ignore next : E2E tested */
    document.getElementById('content-wrapper')?.scrollTo(0, 0)

    const backToNav = document.getElementById('back-to-nav-link')
    const currentFocusId = document.activeElement?.id

    const isFocusAlreadyGiven = currentFocusId === 'back-to-nav-link' || currentFocusId === 'top-page'

    if (!isFocusAlreadyGiven) {
      if (isInternalNavigation && backToNav) {
        backToNav.focus()
      } else {
        document.getElementById('top-page')?.focus()
      }
    }

  }, [isInternalNavigation, location.pathname])
}
