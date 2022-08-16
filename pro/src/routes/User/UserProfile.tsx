import React from 'react'

import useCurrentUser from 'components/hooks/useCurrentUser'
import { UserProfile as UserProfileScreen } from 'screens/UserProfile'

import { serializeUserIdentity } from './adapters/serializers'

const Profile = (): JSX.Element => {
  const { currentUser } = useCurrentUser()
  return (
    <UserProfileScreen
      userIdentityInitialValues={serializeUserIdentity(currentUser)}
    />
  )
}

export default Profile
