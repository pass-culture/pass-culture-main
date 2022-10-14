import { useSelector } from 'react-redux'

import { SharedCurrentUserResponseModel } from 'apiClient/v1'
import { selectCurrentUser, selectUserInitialized } from 'store/user/selectors'

export interface IUseCurrentUserReturn {
  isUserInitialized: boolean
  currentUser: SharedCurrentUserResponseModel
}

const useCurrentUser = (): IUseCurrentUserReturn => {
  const currentUser = useSelector(selectCurrentUser)
  const isUserInitialized = useSelector(selectUserInitialized)

  return {
    isUserInitialized,
    currentUser: currentUser as SharedCurrentUserResponseModel,
  }
}

export default useCurrentUser
