import { selectCurrentOfferer } from 'commons/store/offerer/selectors'

import { useAppSelector } from './useAppSelector'

export const useIsCaledonian = () => {
  const offerer = useAppSelector(selectCurrentOfferer)
  return offerer?.isCaledonian ?? false
}
