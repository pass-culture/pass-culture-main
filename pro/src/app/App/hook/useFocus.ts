import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

export const useFocus = (): void => {
  const location = useLocation()

  useEffect(() => {
    /* istanbul ignore next : E2E tested */
    document.getElementById('content-wrapper')?.scrollTo(0, 0)
    document.getElementById('top-page')?.focus()
  }, [location.pathname])
}
