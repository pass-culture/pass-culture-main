import { useState } from 'react'

import { api } from '@/apiClient/api'
import type { UserPhoneBodyModel } from '@/apiClient/v1'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { logout } from '@/commons/store/user/dispatchers/logout'
import { BannerRGS } from '@/components/BannerRGS/BannerRGS'
import type { UserIdentityFormValues } from '@/components/UserIdentityForm/types'
import { Button } from '@/ui-kit/Button/Button'

import { Forms } from './constants'
import { UserEmail, type UserEmailInitialValues } from './UserEmail/UserEmail'
import { UserIdentity } from './UserIdentity/UserIdentity'
import { UserPassword } from './UserPassword/UserPassword'
import { UserPhone } from './UserPhone/UserPhone'
import styles from './UserProfile.module.scss'

interface UserProfileProps {
  userIdentityInitialValues: UserIdentityFormValues
  userPhoneInitialValues: UserPhoneBodyModel
  userEmailInitialValues: UserEmailInitialValues
}

export const UserProfile = ({
  userIdentityInitialValues,
  userPhoneInitialValues,
  userEmailInitialValues,
}: UserProfileProps): JSX.Element => {
  const dispatch = useAppDispatch()
  const [currentForm, setCurrentForm] = useState<Forms | null>(null)

  return (
    <div className={styles['profil-container']}>
      <BannerRGS className={styles.banner} />
      <UserIdentity
        setCurrentForm={(value: Forms | null) => setCurrentForm(value)}
        initialValues={userIdentityInitialValues}
        showForm={currentForm === Forms.USER_IDENTITY}
      />
      <UserPhone
        setCurrentForm={(value: Forms | null) => setCurrentForm(value)}
        initialValues={userPhoneInitialValues}
        showForm={currentForm === Forms.USER_PHONE}
      />
      <UserEmail
        setCurrentForm={(value: Forms | null) => setCurrentForm(value)}
        initialValues={userEmailInitialValues}
        showForm={currentForm === Forms.USER_EMAIL}
      />
      <UserPassword
        setCurrentForm={(value: Forms | null) => setCurrentForm(value)}
        showForm={currentForm === Forms.USER_PASSWORD}
      />

      <Button
        onClick={async () => {
          await api.anonymize()
          dispatch(logout())
        }}
      >
        ANOMYSE MOI
      </Button>
    </div>
  )
}
