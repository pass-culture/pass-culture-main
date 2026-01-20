import {
  selectAdminCurrentOfferer,
  selectCurrentOfferer,
} from 'commons/store/offerer/selectors'

import { useAppSelector } from './useAppSelector'

export const useIsCaledonian = (isAdmin = false) => {
  const offerer = useAppSelector(
    isAdmin ? selectAdminCurrentOfferer : selectCurrentOfferer
  )
  return offerer?.isCaledonian ?? false
}
