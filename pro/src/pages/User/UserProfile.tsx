import { AppLayout } from 'app/AppLayout'
import useCurrentUser from 'hooks/useCurrentUser'
import { UserProfile as UserProfileScreen } from 'screens/UserProfile'

const Profile = (): JSX.Element => {
  const { currentUser } = useCurrentUser()

  return (
    <AppLayout>
      <UserProfileScreen
        userIdentityInitialValues={{
          firstName: currentUser.firstName || '',
          lastName: currentUser.lastName || '',
        }}
        userPhoneInitialValues={{ phoneNumber: currentUser.phoneNumber ?? '' }}
        userEmailInitialValues={{
          email: currentUser.email,
        }}
      />
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Profile
