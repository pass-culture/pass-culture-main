import React, { useState } from 'react'

import { UserPhoneBodyModel } from 'apiClient/v1'
import { BannerRGS } from 'components/Banner'
import { IUserIdentityFormValues } from 'components/UserIdentityForm/types'

import { Forms } from './constants'
import UserEmail, { IUserEmailInitialValues } from './UserEmail/UserEmail'
import { UserIdentity } from './UserIdentity'
import { UserPassword } from './UserPassword'
import { UserPhone } from './UserPhone'
import styles from './UserProfile.module.scss'

interface IUserProfileProps {
  userIdentityInitialValues: IUserIdentityFormValues
  userPhoneInitialValues: UserPhoneBodyModel
  userEmailInitialValues: IUserEmailInitialValues
}

const UserProfile = ({
  userIdentityInitialValues,
  userPhoneInitialValues,
  userEmailInitialValues,
}: IUserProfileProps): JSX.Element => {
  const [currentForm, setCurrentForm] = useState<Forms | null>(null)
  return (
    <>
      <h1 className={styles['profil-title']}>Profil</h1>
      <BannerRGS />
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
    </>
  )
}

export default UserProfile
