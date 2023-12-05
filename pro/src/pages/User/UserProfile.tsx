import React from 'react'

import { AppLayout } from 'app/AppLayout'
import useCurrentUser from 'hooks/useCurrentUser'
import { UserProfile as UserProfileScreen } from 'screens/UserProfile'

import {
  serializeUserEmail,
  serializeUserIdentity,
  serializeUserPhone,
} from './adapters/serializers'

const Profile = (): JSX.Element => {
  const { currentUser } = useCurrentUser()

  return (
    <AppLayout>
      <UserProfileScreen
        userIdentityInitialValues={serializeUserIdentity(currentUser)}
        userPhoneInitialValues={serializeUserPhone(currentUser)}
        userEmailInitialValues={serializeUserEmail(currentUser)}
      />
    </AppLayout>
  )
}

export default Profile
