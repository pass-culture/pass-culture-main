import { setCurrentUser, setIsInitialized } from 'store/user/actions'
import { useDispatch, useSelector } from 'react-redux'

import { api } from 'apiClient/api'
import { selectCurrentUser } from 'store/user/selectors'
import { selectUserInitialized } from 'store/user/selectors'
import { useEffect } from 'react'

// FIXME: use generated types from swagger codegens
interface IAPICurrentUser {
  activity: string | null
  address: string | null
  city: string | null
  civility: string | null
  dateCreated: Date
  dateOfBirth: Date | null
  departementCode: string | null
  email: string
  externalIds: { [key: string]: { [subKey: string]: string } }
  firstName: string | null
  hasPhysicalVenues: boolean
  hasSeenProTutorials: boolean
  hasSeenProRgs: boolean
  id: string
  idPieceNumber: string | null
  isAdmin: boolean
  isEmailValidated: boolean
  lastConnectionDate: Date | null
  lastName: string | null
  needsToFillCulturalSurvey: boolean
  notificationSubscriptions: { [key: string]: boolean }
  phoneNumber: string | null
  phoneValidationStatus: string | null
  postalCode: string | null
  publicName: string | null
  roles: string[]
}

export interface IUseCurrentUserReturn {
  isUserInitialized: boolean
  currentUser: IAPICurrentUser
}

const useCurrentUser = (): IUseCurrentUserReturn => {
  const currentUser = useSelector(state => selectCurrentUser(state))
  const isUserInitialized = useSelector(state => selectUserInitialized(state))

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

  return { isUserInitialized, currentUser }
}

export default useCurrentUser
