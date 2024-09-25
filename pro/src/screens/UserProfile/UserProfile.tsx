import { useState } from 'react'
import { useTranslation } from 'react-i18next'

import { UserPhoneBodyModel } from 'apiClient/v1'
import { BannerRGS } from 'components/Banner/BannerRGS'
import { UserIdentityFormValues } from 'components/UserIdentityForm/types'

import { Forms } from './constants'
import { UserEmail, UserEmailInitialValues } from './UserEmail'
import { UserIdentity } from './UserIdentity'
import { UserPassword } from './UserPassword'
import { UserPhone } from './UserPhone'
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
  const { t } = useTranslation('common')
  const [currentForm, setCurrentForm] = useState<Forms | null>(null)
  return (
    <div className={styles['profil-container']}>
      <h1 className={styles['profil-title']}>{t('profile')}</h1>
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
    </div>
  )
}
