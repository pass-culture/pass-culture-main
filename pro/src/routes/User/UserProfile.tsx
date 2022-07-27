import React from 'react'
import Spinner from 'components/layout/Spinner'
import { UserProfile as UserProfileScreen } from 'screens/UserProfile'
import { serializeUser } from './adapters/serializer'
import useCurrentUser from 'components/hooks/useCurrentUser'

const Profile = (): JSX.Element => {
  const user = useCurrentUser()
  if (!user.isUserInitialized) return <Spinner />
  return <UserProfileScreen {...serializeUser(user)} />
}

export default Profile
