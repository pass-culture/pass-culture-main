import { selectCurrentOfferer } from 'commons/store/offerer/selectors'
import { useSelector } from 'react-redux'

export const useIsAllowedOnAdage = () => {
  const offerer = useSelector(selectCurrentOfferer)
  return offerer?.allowedOnAdage ?? false
}
