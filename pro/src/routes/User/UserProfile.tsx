import React from 'react'

import useCurrentUser from 'components/hooks/useCurrentUser'
import { UserProfile as UserProfileScreen } from 'screens/UserProfile'

import {
  serializeUserEmail,
  serializeUserIdentity,
  serializeUserPhone,
} from './adapters/serializers'

const Profile = (): JSX.Element => {
  const { currentUser } = useCurrentUser()

  return (
    <UserProfileScreen
      userIdentityInitialValues={serializeUserIdentity(currentUser)}
      userPhoneInitialValues={serializeUserPhone(currentUser)}
      userEmailInitialValues={serializeUserEmail(currentUser)}
    />
  )
}

export default Profile
