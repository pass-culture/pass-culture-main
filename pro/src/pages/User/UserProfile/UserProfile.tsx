import { useState } from 'react'
import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_USER_EMAIL_PENDING_VALIDATION } from '@/commons/config/swrQueryKeys'
import { formatPhoneNumber } from '@/commons/utils/formatPhoneNumber'
import { BannerRGS } from '@/components/BannerRGS/BannerRGS'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullBackIcon from '@/icons/full-back.svg'
import type { UserIdentityFormValues } from '@/pages/User/UserProfile/UserIdentityForm/types'
import { UserIdentityForm } from '@/pages/User/UserProfile/UserIdentityForm/UserIdentityForm'
import { UserPasswordForm } from '@/pages/User/UserProfile/UserPasswordForm/UserPasswordForm'
import {
  UserPhoneForm,
  type UserPhoneInitialValues,
} from '@/pages/User/UserProfile/UserPhoneForm/UserPhoneForm'

import { BannerPendingEmailValidation } from './BannerPendingEmailValidation/BannerPendingEmailValidation'
import { Forms } from './constants'
import { UserAnonymization } from './UserAnonymization/UserAnonymization'
import { UserDynamicPanel } from './UserDynamicPanel/UserDynamicPanel'
import {
  UserEmailForm,
  type UserEmailInitialValues,
} from './UserEmailForm/UserEmailForm'
import styles from './UserProfile.module.scss'

interface UserProfileProps {
  userIdentityInitialValues: UserIdentityFormValues
  userPhoneInitialValues: UserPhoneInitialValues
  userEmailInitialValues: UserEmailInitialValues
}

export const UserProfile = ({
  userIdentityInitialValues,
  userPhoneInitialValues,
  userEmailInitialValues,
}: UserProfileProps): JSX.Element => {
  const [currentForm, setCurrentForm] = useState<Forms | null>(null)

  const navigate = useNavigate()

  const { data: pendingEmailValidation } = useSWR(
    [GET_USER_EMAIL_PENDING_VALIDATION],
    () => api.getUserEmailPendingValidation()
  )

  return (
    <div className={styles['profil-container']}>
      <Button
        onClick={() => navigate(-1)}
        variant={ButtonVariant.TERTIARY}
        color={ButtonColor.NEUTRAL}
        icon={fullBackIcon}
        iconPosition={IconPositionEnum.LEFT}
        label="Retour"
      />

      <BannerRGS />

      <div>
        <UserDynamicPanel
          title="Prénom et nom"
          form={Forms.USER_IDENTITY}
          currentForm={currentForm}
          setCurrentForm={setCurrentForm}
          displayContent={
            <p>
              {userIdentityInitialValues.firstName}{' '}
              {userIdentityInitialValues.lastName}
            </p>
          }
        >
          {(closeForm) => (
            <UserIdentityForm
              closeForm={closeForm}
              initialValues={userIdentityInitialValues}
            />
          )}
        </UserDynamicPanel>

        <UserDynamicPanel
          title="Téléphone"
          form={Forms.USER_PHONE}
          currentForm={currentForm}
          setCurrentForm={setCurrentForm}
          displayContent={formatPhoneNumber(
            userPhoneInitialValues.phoneNumber,
            'NATIONAL'
          )}
        >
          {(closeForm) => (
            <UserPhoneForm
              closeForm={closeForm}
              initialValues={userPhoneInitialValues}
            />
          )}
        </UserDynamicPanel>

        <UserDynamicPanel
          title="Adresse email de connexion"
          form={Forms.USER_EMAIL}
          currentForm={currentForm}
          setCurrentForm={setCurrentForm}
          displayContent={
            <>
              {userEmailInitialValues.email}

              {pendingEmailValidation?.newEmail && (
                <BannerPendingEmailValidation
                  email={pendingEmailValidation.newEmail}
                />
              )}
            </>
          }
        >
          {(closeForm) => <UserEmailForm closeForm={closeForm} />}
        </UserDynamicPanel>

        <UserDynamicPanel
          title="Mot de passe"
          form={Forms.USER_PASSWORD}
          currentForm={currentForm}
          setCurrentForm={setCurrentForm}
          displayContent={
            <>
              <p>Mot de passe</p>
              <p>***************</p>{' '}
            </>
          }
        >
          {(closeForm) => <UserPasswordForm closeForm={closeForm} />}
        </UserDynamicPanel>
      </div>

      <UserAnonymization />
    </div>
  )
}
