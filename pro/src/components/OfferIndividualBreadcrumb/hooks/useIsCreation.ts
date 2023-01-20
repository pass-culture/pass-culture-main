import { useLocation } from 'react-router'

const useIsCreation = (): boolean => {
  const location = useLocation()
  return location.pathname.includes('creation')
}

export default useIsCreation
