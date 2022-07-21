import { ProfileScreen } from 'screens/User'
import React from 'react'
import Spinner from 'components/layout/Spinner'
import { serializeUser } from './adapters/serializer'
import useCurrentUser from 'components/hooks/useCurrentUser'

const Profile = (): JSX.Element => {
  const user = useCurrentUser()
  if (!user.isUserInitialized) return <Spinner />
  return <ProfileScreen {...serializeUser(user)} />
}

export default Profile
