import { useAppSelector } from './useAppSelector'

export const useIsCaledonian = (isAdmin = false) => {
  const selectedPartnerVenue = useAppSelector(
    (store) => store.user.selectedPartnerVenue
  )
  const selectedAdminOfferer = useAppSelector(
    (store) => store.user.selectedAdminOfferer
  )
  return isAdmin
    ? selectedAdminOfferer?.isCaledonian
    : selectedPartnerVenue?.isCaledonian
}
