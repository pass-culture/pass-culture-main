import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'

import { api } from 'apiClient/api'
import { SharedCurrentUserResponseModel } from 'apiClient/v1'
import { setCurrentUser, setIsInitialized } from 'store/user/actions'
import { selectCurrentUser, selectUserInitialized } from 'store/user/selectors'

export interface IUseCurrentUserReturn {
  isUserInitialized: boolean
  currentUser: SharedCurrentUserResponseModel
}

// TODO user is now initialized on application's root.
// remove isUserInitialized as it's always true
const useCurrentUser = (): IUseCurrentUserReturn => {
  const currentUser = useSelector(selectCurrentUser)
  const isUserInitialized = useSelector(selectUserInitialized)

  const dispatch = useDispatch()
  useEffect(() => {
    if (!isUserInitialized) {
      api
        .getProfile()
        .then(user => {
          dispatch(setCurrentUser(user ? user : null))
        })
        .catch(() => setCurrentUser(null))
        .finally(() => {
          dispatch(setIsInitialized())
        })
    }
  }, [dispatch, isUserInitialized])

  return {
    isUserInitialized,
    currentUser: currentUser as SharedCurrentUserResponseModel,
  }
}

export default useCurrentUser
