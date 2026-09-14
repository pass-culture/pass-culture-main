import type { JSX } from 'react'

import { FullLayout } from '@/app/App/layouts/FullLayout/FullLayout'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureCurrentUser } from '@/commons/store/user/selectors'
import { UserProfile } from '@/pages/User/UserProfile/UserProfile'

import styles from './UserProfile/UserProfile.module.scss'

const Profile = (): JSX.Element => {
  const currentUser = useAppSelector(ensureCurrentUser)

  return (
    <FullLayout>
      <div className={styles['content-wrapper']}>
        <h1 className={styles['title']}>Profil</h1>
        <UserProfile
          userIdentityInitialValues={{
            firstName: currentUser.firstName || '',
            lastName: currentUser.lastName || '',
          }}
          userPhoneInitialValues={{
            phoneNumber: currentUser.phoneNumber ?? '',
          }}
          userEmailInitialValues={{
            email: currentUser.email,
          }}
        />
      </div>
    </FullLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Profile
