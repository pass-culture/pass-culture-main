import { selectCurrentOfferer } from 'commons/store/offerer/selectors'
import { useSelector } from 'react-redux'

export const useIsCaledonian = () => {
  const offerer = useSelector(selectCurrentOfferer)
  return offerer?.isCaledonian ?? false
}
