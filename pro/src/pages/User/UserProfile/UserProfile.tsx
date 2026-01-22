import { useState } from 'react'
import { useNavigate } from 'react-router'

import type { UserPhoneBodyModel } from '@/apiClient/v1'
import { BannerRGS } from '@/components/BannerRGS/BannerRGS'
import type { UserIdentityFormValues } from '@/components/UserIdentityForm/types'
import fullBackIcon from '@/icons/full-back.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from '@/ui-kit/Button/types'

import { Forms } from './constants'
import { UserAnonymization } from './UserAnonymization/UserAnonymization'
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
  const [currentForm, setCurrentForm] = useState<Forms | null>(null)
  const navigate = useNavigate()

  return (
    <div className={styles['profil-container']}>
      <Button
        onClick={() => navigate(-1)}
        variant={ButtonVariant.TERNARY}
        icon={fullBackIcon}
        iconPosition={IconPositionEnum.LEFT}
      >
        Retour
      </Button>
      <BannerRGS />
      <div>
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
      <UserAnonymization />
    </div>
  )
}
