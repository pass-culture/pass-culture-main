import React from 'react'

import useCurrentUser from 'components/hooks/useCurrentUser'
import { UserProfile as UserProfileScreen } from 'screens/UserProfile'

import {
  serializeUserIdentity,
  serializeUserPhone,
} from './adapters/serializers'

const Profile = (): JSX.Element => {
  const { currentUser } = useCurrentUser()
  return (
    <UserProfileScreen
      userIdentityInitialValues={serializeUserIdentity(currentUser)}
      userPhoneInitialValues={serializeUserPhone(currentUser)}
    />
  )
}

export default Profile
