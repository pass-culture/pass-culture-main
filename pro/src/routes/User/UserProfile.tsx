import React from 'react'

import useCurrentUser from 'components/hooks/useCurrentUser'
import Spinner from 'components/layout/Spinner'
import patchIdentityAdapter from 'routes/User/adapters/patchIdentityAdapter'
import { UserProfile as UserProfileScreen } from 'screens/UserProfile'

import { serializeUserIdentity } from './adapters/serializers'

const Profile = (): JSX.Element => {
  const { currentUser, isUserInitialized } = useCurrentUser()
  if (!isUserInitialized) return <Spinner />

  return (
    <UserProfileScreen
      patchIdentityAdapter={patchIdentityAdapter}
      userIdentityInitialValues={serializeUserIdentity(currentUser)}
    />
  )
}

export default Profile
