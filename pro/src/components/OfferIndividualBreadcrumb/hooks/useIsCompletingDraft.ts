import { useLocation } from 'react-router'

const useIsCompletingDraft = (): boolean => {
  const location = useLocation()
  return location.pathname.includes('brouillon')
}

export default useIsCompletingDraft
