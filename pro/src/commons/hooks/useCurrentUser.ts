import type { SharedCurrentUserResponseModel } from '@/apiClient/v1'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { selectCurrentUser } from '@/commons/store/user/selectors'

import { assertOrFrontendError } from '../errors/assertOrFrontendError'
import { useAppSelector } from './useAppSelector'

interface UseCurrentUserReturn {
  currentUser: SharedCurrentUserResponseModel
  selectedOffererId: number | null
}

export const useCurrentUser = (): UseCurrentUserReturn => {
  const currentUser = useAppSelector(selectCurrentUser)
  const selectedOffererId = useAppSelector(selectCurrentOffererId)

  assertOrFrontendError(
    currentUser,
    '`useCurrentUser()` should only be used on authenticated pages. Use `useSelector(selectCurrentUser)` otherwise.'
  )

  return {
    currentUser,
    selectedOffererId,
  }
}
