import { selectCurrentOfferer } from 'commons/store/offerer/selectors'

import { useAppSelector } from './useAppSelector'

export const useIsCaledonian = (isAdmin = false) => {
  const offerer = useAppSelector(selectCurrentOfferer)
  const isAdminOfferer = useAppSelector(
    (store) => store.user.selectedAdminOfferer
  )
  return isAdmin ? isAdminOfferer?.isCaledonian : offerer?.isCaledonian
}
