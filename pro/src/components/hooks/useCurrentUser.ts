import { useDispatch, useSelector } from 'react-redux'

import { loadUser } from 'store/user/thunks'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'
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
      dispatch(loadUser())
    }
  }, [dispatch, isUserInitialized])

  return { isUserInitialized, currentUser }
}

export default useCurrentUser
