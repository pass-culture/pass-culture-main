import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

const useFocus = (): void => {
  const location = useLocation()

  useEffect(() => {
    document.getElementById('top-page')?.focus()
  }, [location.pathname])
}

export default useFocus
