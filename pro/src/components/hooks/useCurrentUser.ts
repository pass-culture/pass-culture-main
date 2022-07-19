import { setCurrentUser, setIsInitialized } from 'store/user/actions'
import { useDispatch, useSelector } from 'react-redux'

import { SharedCurrentUserResponseModel } from 'apiClient/v1'
import { api } from 'apiClient/api'
import { selectCurrentUser } from 'store/user/selectors'
import { selectUserInitialized } from 'store/user/selectors'
import { useEffect } from 'react'

export interface IUseCurrentUserReturn {
  isUserInitialized: boolean
  currentUser: SharedCurrentUserResponseModel
}

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
