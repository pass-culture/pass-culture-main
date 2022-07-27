import React from 'react'
import Spinner from 'components/layout/Spinner'
import { UserProfile as UserProfileScreen } from 'screens/UserProfile'
import patchIdentityAdapter from 'routes/User/adapters/patchIdentityAdapter'
import { serializeUserIdentity } from './adapters/serializers'
import useCurrentUser from 'components/hooks/useCurrentUser'

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
