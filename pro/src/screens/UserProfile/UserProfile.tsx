import React, { useState } from 'react'

import { IUserIdentityFormValues } from 'new_components/UserIdentityForm/types'

import { Forms } from './constants'
import { UserIdentity } from './UserIdentity'

interface IUserProfileProps {
  userIdentityInitialValues: IUserIdentityFormValues
}

const UserProfile = ({
  userIdentityInitialValues,
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
    </>
  )
}

export default UserProfile
