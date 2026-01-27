import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useCurrentUser } from '@/commons/hooks/useCurrentUser'
import { UserProfile } from '@/pages/User/UserProfile/UserProfile'

const Profile = (): JSX.Element => {
  const { currentUser } = useCurrentUser()

  return (
    <BasicLayout mainHeading="Profil" displayLateralPanel={false}>
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
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Profile
