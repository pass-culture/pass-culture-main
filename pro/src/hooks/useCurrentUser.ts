import { useSelector } from 'react-redux'

import { SharedCurrentUserResponseModel } from 'apiClient/v1'
import { selectCurrentOffererId, selectCurrentUser } from 'store/user/selectors'

export interface UseCurrentUserReturn {
  currentUser: SharedCurrentUserResponseModel
  selectedOffererId: number | null
}

const useCurrentUser = (): UseCurrentUserReturn => {
  const currentUser = useSelector(selectCurrentUser)
  const selectedOffererId = useSelector(selectCurrentOffererId)

  return {
    // TODO : handle the null case by redirecting to login
    // (currently handled by the <RouteWrapper> component)
    // eslint-disable-next-line
    currentUser: currentUser!!,
    selectedOffererId,
  }
}

export default useCurrentUser
