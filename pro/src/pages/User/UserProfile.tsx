import { Layout } from 'app/App/layout/Layout'
import { useCurrentUser } from 'commons/hooks/useCurrentUser'
import { UserProfile } from 'pages/User/UserProfile/UserProfile'

const Profile = (): JSX.Element => {
  const { currentUser } = useCurrentUser()

  return (
    <Layout mainHeading="Profil">
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
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Profile
