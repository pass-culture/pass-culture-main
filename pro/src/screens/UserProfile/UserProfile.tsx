import React, { useState } from 'react'

import { UserPhoneBodyModel } from 'apiClient/v1'
import { IUserIdentityFormValues } from 'new_components/UserIdentityForm/types'

import { Forms } from './constants'
import { UserIdentity } from './UserIdentity'
import { UserPhone } from './UserPhone'

interface IUserProfileProps {
  userIdentityInitialValues: IUserIdentityFormValues
  userPhoneInitialValues: UserPhoneBodyModel
}

const UserProfile = ({
  userIdentityInitialValues,
  userPhoneInitialValues,
}: IUserProfileProps): JSX.Element => {
  const [currentForm, setCurrentForm] = useState<Forms | null>(null)
  return (
    <>
      <h1>Profil</h1>
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
    </>
  )
}

export default UserProfile
