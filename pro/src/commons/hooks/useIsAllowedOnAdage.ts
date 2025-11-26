import { selectCurrentOfferer } from 'commons/store/offerer/selectors'

import { useAppSelector } from './useAppSelector'

export const useIsAllowedOnAdage = () => {
  const offerer = useAppSelector(selectCurrentOfferer)
  return offerer?.allowedOnAdage ?? false
}
