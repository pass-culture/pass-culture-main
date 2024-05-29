import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

export const useFocus = (): void => {
  const location = useLocation()

  useEffect(() => {
    document.getElementById('top-page')?.focus()
  }, [location.pathname])
}
