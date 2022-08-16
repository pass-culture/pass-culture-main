import React from 'react'

import useCurrentUser from 'components/hooks/useCurrentUser'
import patchIdentityAdapter from 'routes/User/adapters/patchIdentityAdapter'
import { UserProfile as UserProfileScreen } from 'screens/UserProfile'

import { serializeUserIdentity } from './adapters/serializers'

const Profile = (): JSX.Element => {
  const { currentUser } = useCurrentUser()
  // Route should handle retrive data and serialize them for the screen.

  return (
    <UserProfileScreen
      // ?? maybe patch could be directly handle by the form
      patchIdentityAdapter={patchIdentityAdapter}
      userIdentityInitialValues={serializeUserIdentity(currentUser)}
    />
  )
}

export default Profile
