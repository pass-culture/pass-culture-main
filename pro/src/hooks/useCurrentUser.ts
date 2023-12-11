import { useSelector } from 'react-redux'

import { SharedCurrentUserResponseModel } from 'apiClient/v1'
import { selectCurrentUser } from 'store/user/selectors'

export interface UseCurrentUserReturn {
  currentUser: SharedCurrentUserResponseModel
}

const useCurrentUser = (): UseCurrentUserReturn => {
  const currentUser = useSelector(selectCurrentUser)

  return {
    // TODO : handle the null case by redirecting to login
    // (currently handled by the <RouteWrapper> component)
    // eslint-disable-next-line
    currentUser: currentUser!!
  }
}

export default useCurrentUser
