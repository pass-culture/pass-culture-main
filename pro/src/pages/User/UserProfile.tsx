import { FullLayout } from '@/app/App/layouts/FullLayout/FullLayout'
import { useCurrentUser } from '@/commons/hooks/useCurrentUser'
import { UserProfile } from '@/pages/User/UserProfile/UserProfile'

const Profile = (): JSX.Element => {
  const { currentUser } = useCurrentUser()

  return (
    <FullLayout mainHeading="Profil">
      <UserProfile
        userIdentityInitialValues={{
          firstName: currentUser.firstName || '',
          lastName: currentUser.lastName || '',
        }}
        userPhoneInitialValues={{ phoneNumber: currentUser.phoneNumber ?? '' }}
        userEmailInitialValues={{
          email: currentUser.email,
        }}
      />
    </FullLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Profile
