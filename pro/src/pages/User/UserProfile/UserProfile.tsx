import { useState } from 'react'
import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { apiNew } from '@/apiClient/api'
import { GET_USER_EMAIL_PENDING_VALIDATION } from '@/commons/config/swrQueryKeys'
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

/**
 * if phone number is valid:
 * - 10 digit starting by 0
 * - n digits starting by +
 *
 * return formated phone number:
 * - 01 23 45 67 89
 * - +213 1 23 45 67 89
 *
 * otherwise, return given argument phoneNumber unchanged
 */
export const formatPhoneNumber = (phoneNumber: string | null | undefined) => {
  let formatedNumber = phoneNumber
  if (phoneNumber) {
    formatedNumber = phoneNumber.replace(/ /g, '')
    const r = /(\+?[0-9]+)([0-9])([0-9]{8})/g
    const parts = formatedNumber.split(r).slice(1, -1)

    if (parts.length !== 3) {
      return phoneNumber
    }

    const [internationalPrefix, areaPrefix, number] = parts
    const isReginalNumber = internationalPrefix === '0'
    const isInternationalNumber = /\+[0-9]+/.test(internationalPrefix)
    if (!(isReginalNumber || isInternationalNumber)) {
      return phoneNumber
    }

    let prefix = internationalPrefix + areaPrefix
    if (isInternationalNumber) {
      prefix = [internationalPrefix, areaPrefix].join(' ')
    }

    return [prefix, ...number.split(/([0-9]{2})/g).filter((num) => num)].join(
      ' '
    )
  }
  return phoneNumber
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
    () => apiNew.getUserEmailPendingValidation()
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
          displayContent={formatPhoneNumber(userPhoneInitialValues.phoneNumber)}
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
